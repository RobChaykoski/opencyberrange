"""Authentication lifecycle: sessions, refresh rotation, MFA, reauth, hashes."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pyotp
import pytest
from pwdlib.hashers.bcrypt import BcryptHasher

from app.auth import get_password_hash
from app.config import settings
from app.models import AuthSession, PlatformSetting, SecurityEvent, User

PASSWORD = "Lifecycle#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role="student", mfa=False, password=PASSWORD, tenant="default"):
    suffix = uuid.uuid4().hex[:8]
    row = User(
        username=f"life_{role}_{suffix}",
        email=f"life_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(password),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id=tenant,
        mfa_enabled=mfa,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _set(db, key, value):
    row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if row is None:
        row = PlatformSetting(
            key=key,
            value=str(value),
            category="security",
            description="test",
            is_secret=False,
        )
        db.add(row)
    else:
        row.value = str(value)
    db.commit()


def _login(client, user, password=PASSWORD, **extra):
    data = {"username": user.username, "password": password}
    data.update(extra)
    return client.post("/api/auth/login", data=data)


def _enable_mfa(client, headers):
    enroll = client.post("/api/auth/mfa/enroll", headers=headers)
    assert enroll.status_code == 200, enroll.text
    secret = enroll.json()["secret"]
    verify = client.post(
        "/api/auth/mfa/verify",
        json={"code": pyotp.TOTP(secret).now()},
        headers=headers,
    )
    assert verify.status_code == 200, verify.text
    return secret


def test_refresh_rotation_and_reuse_revokes_family(client, db_session):
    user = _user(db_session)
    login = _login(client, user)
    assert login.status_code == 200, login.text
    first = login.json()
    assert first["refresh_token"]
    assert first["session_id"]

    rotated = client.post(
        "/api/auth/refresh", json={"refresh_token": first["refresh_token"]}
    )
    assert rotated.status_code == 200, rotated.text
    second = rotated.json()
    assert second["refresh_token"] != first["refresh_token"]
    assert second["session_id"] == first["session_id"]

    reused = client.post(
        "/api/auth/refresh", json={"refresh_token": first["refresh_token"]}
    )
    assert reused.status_code == 401
    assert reused.headers.get("x-refresh-reuse") == "true"

    # The family and session are revoked, so the newest token is dead too.
    dead = client.post(
        "/api/auth/refresh", json={"refresh_token": second["refresh_token"]}
    )
    assert dead.status_code == 401
    me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {second['access_token']}"},
    )
    assert me.status_code == 401

    event = (
        db_session.query(SecurityEvent)
        .filter(SecurityEvent.event_type == "auth.refresh_reuse")
        .order_by(SecurityEvent.id.desc())
        .first()
    )
    assert event is not None


def test_session_is_bound_to_the_tenant_at_login(client, db_session):
    user = _user(db_session, tenant="tenant-a")
    login = _login(client, user)
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    assert client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    ).status_code == 200

    user.institution_id = "tenant-b"
    db_session.commit()
    denied = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert denied.status_code == 401
    assert denied.headers.get("x-session-invalid") == "true"


def test_reauth_is_required_before_export(client, db_session, test_user, auth_headers):
    first = client.get("/api/auth/export", headers=auth_headers)
    assert first.status_code == 200, first.text

    session = (
        db_session.query(AuthSession)
        .filter(AuthSession.user_id == test_user.id)
        .order_by(AuthSession.created_at.desc())
        .first()
    )
    session.reauth_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
    db_session.commit()

    denied = client.get("/api/auth/export", headers=auth_headers)
    assert denied.status_code == 403
    assert denied.headers.get("x-reauth-required") == "true"

    reauth = client.post(
        "/api/auth/reauth",
        json={"password": "Correct#Horse7Battery"},
        headers=auth_headers,
    )
    assert reauth.status_code == 200, reauth.text
    again = client.get("/api/auth/export", headers=auth_headers)
    assert again.status_code == 200, again.text


def test_recovery_codes_are_single_use_and_expire(client, db_session):
    user = _user(db_session)
    headers = _login(client, user).json()
    auth_headers = {"Authorization": f"Bearer {headers['access_token']}"}
    _enable_mfa(client, auth_headers)

    generated = client.post("/api/auth/mfa/recovery-codes", headers=auth_headers)
    assert generated.status_code == 200, generated.text
    body = generated.json()
    assert len(body["codes"]) == 10
    assert body["expires_at"]
    code = body["codes"][0]

    used = client.post(
        "/api/auth/mfa/recovery-codes/verify",
        json={"code": code},
        headers=auth_headers,
    )
    assert used.status_code == 200, used.text
    assert used.json()["remaining"] == 9

    reused = client.post(
        "/api/auth/mfa/recovery-codes/verify",
        json={"code": code},
        headers=auth_headers,
    )
    assert reused.status_code == 401

    user = db_session.get(User, user.id)
    user.mfa_recovery_generated_at = datetime.now(timezone.utc).replace(
        tzinfo=None
    ) - timedelta(days=400)
    db_session.commit()
    expired = client.post(
        "/api/auth/mfa/recovery-codes/verify",
        json={"code": body["codes"][1]},
        headers=auth_headers,
    )
    assert expired.status_code in {400, 401}


def test_mfa_brute_force_locks_the_challenge(client, db_session):
    _set(db_session, "mfa_max_failed_attempts", "2")
    _set(db_session, "mfa_lockout_minutes", "15")
    user = _user(db_session)
    login = _login(client, user)
    auth_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    secret = _enable_mfa(client, auth_headers)

    bad1 = _login(client, user, totp_code="000000")
    assert bad1.status_code == 401
    bad2 = _login(client, user, totp_code="111111")
    assert bad2.status_code == 401
    locked = _login(client, user, totp_code=pyotp.TOTP(secret).now())
    assert locked.status_code == 429
    assert locked.headers.get("x-mfa-locked") == "true"

    db_session.refresh(user)
    user.mfa_locked_until = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        seconds=1
    )
    db_session.commit()
    ok = _login(client, user, totp_code=pyotp.TOTP(secret).now())
    assert ok.status_code == 200, ok.text


def test_admin_mfa_reset_requires_reason_and_reauth(client, db_session):
    admin = _user(db_session, "admin")
    target = _user(db_session, "student", mfa=True)
    headers = {
        "Authorization": f"Bearer {_login(client, admin).json()['access_token']}"
    }

    short = client.post(
        f"/api/admin/users/{target.id}/mfa/reset",
        json={"reason": "short", "admin_password": PASSWORD},
        headers=headers,
    )
    assert short.status_code == 422

    wrong = client.post(
        f"/api/admin/users/{target.id}/mfa/reset",
        json={"reason": "lost authenticator device", "admin_password": "wrong"},
        headers=headers,
    )
    assert wrong.status_code == 401

    reset = client.post(
        f"/api/admin/users/{target.id}/mfa/reset",
        json={"reason": "lost authenticator device", "admin_password": PASSWORD},
        headers=headers,
    )
    assert reset.status_code == 200, reset.text
    db_session.refresh(target)
    assert target.mfa_enabled is False
    assert target.totp_secret is None
    event = (
        db_session.query(SecurityEvent)
        .filter(SecurityEvent.event_type == "auth.mfa_reset")
        .order_by(SecurityEvent.id.desc())
        .first()
    )
    assert event is not None
    assert event.severity == "critical"


def test_argon2_parameters_and_recurring_rehash(client, db_session):
    bcrypt_hash = BcryptHasher().hash(PASSWORD)
    user = _user(db_session, password=PASSWORD)
    user.hashed_password = bcrypt_hash
    user.password_rehashed_at = None
    db_session.commit()

    login = _login(client, user)
    assert login.status_code == 200, login.text
    db_session.refresh(user)
    assert user.hashed_password.startswith("$argon2id$")
    assert (
        f"m={settings.ARGON2_MEMORY_COST},t={settings.ARGON2_TIME_COST},"
        f"p={settings.ARGON2_PARALLELISM}"
    ) in user.hashed_password
    first_hash = user.hashed_password
    assert user.password_rehashed_at is not None

    user.password_rehashed_at = datetime.now(timezone.utc).replace(
        tzinfo=None
    ) - timedelta(days=settings.PASSWORD_REHASH_DAYS + 1)
    db_session.commit()
    again = _login(client, user)
    assert again.status_code == 200, again.text
    db_session.refresh(user)
    assert user.hashed_password != first_hash
    assert user.hashed_password.startswith("$argon2id$")
