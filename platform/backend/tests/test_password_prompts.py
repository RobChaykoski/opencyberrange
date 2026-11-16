"""Every password prompt accepts the correct password and rejects bad input.

Covers login, re-authentication, password change, account deletion, an
administrator password reset, and MFA disable. The tests also bound the input
and verify that a password is never echoed back and that injection-shaped input
does not produce a server error.
"""

from __future__ import annotations

import uuid

import pyotp
import pytest
from sqlalchemy import text

from app.auth import get_password_hash
from app.models import User

PASSWORD = "Prompt#Valid9Pass"  # Test-only credential; security-delta: allow
NEW_PASSWORD = "Rotated#Pass9Word"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role="student", mfa=False, password=PASSWORD):
    suffix = uuid.uuid4().hex[:8]
    row = User(
        username=f"prompt_{role}_{suffix}",
        email=f"prompt_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(password),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id="default",
        mfa_enabled=mfa,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _login(client, user, password=PASSWORD, **extra):
    data = {"username": user.username, "password": password}
    data.update(extra)
    return client.post("/api/auth/login", data=data)


def _headers(client, user, password=PASSWORD):
    response = _login(client, user, password)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_login_prompt_accepts_correct_password_and_rejects_bad_input(
    client, db_session
):
    user = _user(db_session)

    accepted = _login(client, user)
    assert accepted.status_code == 200, accepted.text
    assert PASSWORD not in accepted.text

    rejected = _login(client, user, "Wrong#Password9")
    assert rejected.status_code == 401
    assert rejected.json()["detail"] == "Incorrect username or password"

    oversized = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": "A1" + "a" * 127},
    )
    assert oversized.status_code == 401
    assert oversized.json()["detail"] == "Incorrect username or password"

    newline_username = client.post(
        "/api/auth/login",
        data={"username": "user\nforged-log-line", "password": PASSWORD},
    )
    assert newline_username.status_code == 401

    injection = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": "' OR 1=1 --"},
    )
    assert injection.status_code == 401
    assert "' OR 1=1 --" not in injection.text


def test_reauth_prompt_accepts_correct_password(client, db_session):
    user = _user(db_session)
    headers = _headers(client, user)

    accepted = client.post(
        "/api/auth/reauth", json={"password": PASSWORD}, headers=headers
    )
    assert accepted.status_code == 200, accepted.text
    assert PASSWORD not in accepted.text

    rejected = client.post(
        "/api/auth/reauth",
        json={"password": "Wrong#Password9"},
        headers=headers,
    )
    assert rejected.status_code == 401
    assert rejected.json()["detail"] == "Current password is incorrect."

    oversized = client.post(
        "/api/auth/reauth",
        json={"password": "A1" + "a" * 127},
        headers=headers,
    )
    assert oversized.status_code == 422


def test_change_password_prompt_accepts_correct_current_password(
    client, db_session
):
    user = _user(db_session)
    headers = _headers(client, user)

    rejected = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "Wrong#Password9",
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
        headers=headers,
    )
    assert rejected.status_code == 401

    weak = client.post(
        "/api/auth/change-password",
        json={
            "current_password": PASSWORD,
            "new_password": "abcdefgh",
            "confirm_password": "abcdefgh",
        },
        headers=headers,
    )
    assert weak.status_code == 422

    control_character = client.post(
        "/api/auth/change-password",
        json={
            "current_password": PASSWORD,
            "new_password": "Strong#1\nPass",
            "confirm_password": "Strong#1\nPass",
        },
        headers=headers,
    )
    assert control_character.status_code == 422

    accepted = client.post(
        "/api/auth/change-password",
        json={
            "current_password": PASSWORD,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
        headers=headers,
    )
    assert accepted.status_code == 200, accepted.text
    assert _login(client, user, NEW_PASSWORD).status_code == 200
    assert _login(client, user, PASSWORD).status_code == 401


def test_delete_account_prompt_accepts_correct_password(client, db_session):
    user = _user(db_session)
    headers = _headers(client, user)

    rejected = client.post(
        "/api/auth/delete-account",
        json={"password": "Wrong#Password9", "confirm": "DELETE"},
        headers=headers,
    )
    assert rejected.status_code == 401

    wrong_confirmation = client.post(
        "/api/auth/delete-account",
        json={"password": PASSWORD, "confirm": "delete"},
        headers=headers,
    )
    assert wrong_confirmation.status_code == 400

    accepted = client.post(
        "/api/auth/delete-account",
        json={"password": PASSWORD, "confirm": "DELETE"},
        headers=headers,
    )
    assert accepted.status_code == 200, accepted.text
    remaining = db_session.execute(
        text("SELECT count(*) FROM users WHERE id = :id"), {"id": user.id}
    ).scalar()
    assert remaining == 0


def test_admin_reset_prompt_accepts_correct_admin_password(client, db_session):
    admin = _user(db_session, role="admin")
    target = _user(db_session)
    headers = _headers(client, admin)
    url = f"/api/admin/users/{target.id}/reset-password"

    rejected = client.post(
        url,
        json={
            "admin_password": "Wrong#Password9",
            "new_password": NEW_PASSWORD,
            "must_change_password": False,
        },
        headers=headers,
    )
    assert rejected.status_code in {401, 403}

    accepted = client.post(
        url,
        json={
            "admin_password": PASSWORD,
            "new_password": NEW_PASSWORD,
            "must_change_password": False,
        },
        headers=headers,
    )
    assert accepted.status_code == 200, accepted.text
    assert _login(client, target, NEW_PASSWORD).status_code == 200


def test_mfa_disable_prompt_accepts_correct_password(client, db_session):
    user = _user(db_session)
    headers = _headers(client, user)

    enroll = client.post("/api/auth/mfa/enroll", headers=headers)
    assert enroll.status_code == 200, enroll.text
    secret = enroll.json()["secret"]
    verify = client.post(
        "/api/auth/mfa/verify",
        json={"code": pyotp.TOTP(secret).now()},
        headers=headers,
    )
    assert verify.status_code == 200, verify.text

    rejected = client.post(
        "/api/auth/mfa/disable",
        json={"password": "Wrong#Password9", "code": pyotp.TOTP(secret).now()},
        headers=headers,
    )
    assert rejected.status_code == 401

    accepted = client.post(
        "/api/auth/mfa/disable",
        json={"password": PASSWORD, "code": pyotp.TOTP(secret).now()},
        headers=headers,
    )
    assert accepted.status_code == 200, accepted.text
    db_session.expire_all()
    assert db_session.query(User).filter(User.id == user.id).first().mfa_enabled is False
