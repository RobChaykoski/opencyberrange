"""OIDC SSO flow, shared state, provisioning, and title-safe failures."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest

from app.auth import get_password_hash
from app.models import (
    ExternalIdentity,
    IdentityProvider,
    SsoLoginState,
    SsoLoginTicket,
    SsoSession,
    User,
)
from app.services import oidc

pytestmark = pytest.mark.db

PASSWORD = uuid.uuid4().hex + "Aa1!"

DISCOVERY = {
    "issuer": "https://idp.example.edu",
    "authorization_endpoint": "https://idp.example.edu/authorize",
    "token_endpoint": "https://idp.example.edu/token",
    "jwks_uri": "https://idp.example.edu/jwks",
    "end_session_endpoint": "https://idp.example.edu/logout",
}


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


@pytest.fixture(autouse=True)
def _cleanup_sso(db_session):
    yield
    provider_ids = [
        row.id
        for row in db_session.query(IdentityProvider)
        .filter(IdentityProvider.name.like("SSO Test %"))
        .all()
    ]
    user_ids = [
        row.id
        for row in db_session.query(User)
        .filter(User.username.like("sso_test_%"))
        .all()
    ]
    if provider_ids or user_ids:
        db_session.query(SsoLoginTicket).filter(
            (SsoLoginTicket.provider_id.in_(provider_ids))
            | (SsoLoginTicket.user_id.in_(user_ids))
        ).delete(synchronize_session=False)
        db_session.query(SsoLoginState).filter(
            SsoLoginState.provider_id.in_(provider_ids)
        ).delete(synchronize_session=False)
        db_session.query(SsoSession).filter(
            (SsoSession.provider_id.in_(provider_ids))
            | (SsoSession.user_id.in_(user_ids))
        ).delete(synchronize_session=False)
        db_session.query(ExternalIdentity).filter(
            (ExternalIdentity.provider_id.in_(provider_ids))
            | (ExternalIdentity.user_id.in_(user_ids))
        ).delete(synchronize_session=False)
        db_session.query(User).filter(User.id.in_(user_ids)).delete(
            synchronize_session=False
        )
        db_session.query(IdentityProvider).filter(
            IdentityProvider.id.in_(provider_ids)
        ).delete(synchronize_session=False)
        db_session.commit()


def _admin(client, db_session) -> dict:
    suffix = _suffix()
    user = User(
        username=f"sso_test_admin_{suffix}",
        email=f"sso_test_admin_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=True,
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _provider(
    client,
    headers,
    *,
    name: str | None = None,
    config: dict | None = None,
    is_default: bool = True,
):
    suffix = _suffix()
    payload = {
        "name": name or f"SSO Test OIDC {suffix}",
        "kind": "oidc",
        "enabled": True,
        "is_default": is_default,
        "config": {
            "issuer": "https://idp.example.edu",
            "client_id": "ocr-client",
            "scopes": "openid email profile",
            **(config or {}),
        },
        "secrets": {"client_secret": "client-secret"},
    }
    resp = client.post("/api/identity/providers", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _mock_oidc(monkeypatch, claims: dict):
    monkeypatch.setattr(oidc, "discover", lambda provider: dict(DISCOVERY))
    monkeypatch.setattr(
        oidc,
        "exchange_code",
        lambda provider, **kwargs: {"id_token": "fake-id-token"},
    )
    monkeypatch.setattr(
        oidc,
        "validate_id_token",
        lambda provider, token, nonce: dict(claims),
    )


def _claims(*, sub: str | None = None, email: str | None = None, verified: bool = True):
    suffix = _suffix()
    return {
        "sub": sub or f"subject-{suffix}",
        "email": email or f"sso_test_user_{suffix}@example.org",
        "email_verified": verified,
        "preferred_username": f"sso_test_user_{suffix}",
        "given_name": "Sam",
        "family_name": "Student",
        "name": "Sam Student",
    }


def _start(client, provider_id: int) -> dict:
    resp = client.get(
        f"/api/auth/sso/oidc/{provider_id}/login?return_to=/profile",
        follow_redirects=False,
    )
    assert resp.status_code == 302, resp.text
    location = resp.headers["location"]
    query = parse_qs(urlparse(location).query)
    assert query["response_type"] == ["code"]
    assert query["code_challenge_method"] == ["S256"]
    return {
        "location": location,
        "state": query["state"][0],
        "nonce": query["nonce"][0],
        "challenge": query["code_challenge"][0],
    }


def _callback(client, provider_id: int, state: str, code: str = "auth-code"):
    return client.get(
        f"/api/auth/sso/oidc/{provider_id}/callback?code={code}&state={state}",
        follow_redirects=False,
    )


def _ticket_or_error(response) -> tuple[str | None, str | None]:
    assert response.status_code == 302, response.text
    query = parse_qs(urlparse(response.headers["location"]).query)
    return (query.get("ticket", [None])[0], query.get("error", [None])[0])


def test_provider_list_and_redirect_uri(client, db_session):
    headers = _admin(client, db_session)
    provider = _provider(client, headers)

    assert provider["resolved_redirect_uri"].endswith(
        f"/api/auth/sso/oidc/{provider['id']}/callback"
    )
    listed = client.get("/api/auth/sso/providers")
    assert listed.status_code == 200
    body = listed.json()
    assert len(body["providers"]) == 1
    assert body["providers"][0]["login_path"].endswith(
        f"/oidc/{provider['id']}/login"
    )
    assert "client-secret" not in listed.text
    assert "client_id" not in listed.text


def test_oidc_login_provisions_user_and_exchanges_ticket(
    client, db_session, monkeypatch
):
    headers = _admin(client, db_session)
    provider = _provider(client, headers)
    claims = _claims()
    _mock_oidc(monkeypatch, claims)

    started = _start(client, provider["id"])
    assert claims["sub"] not in started["location"]

    callback = _callback(client, provider["id"], started["state"])
    ticket, error = _ticket_or_error(callback)
    assert error is None
    assert ticket

    exchanged = client.post("/api/auth/sso/exchange", json={"ticket": ticket})
    assert exchanged.status_code == 200, exchanged.text
    body = exchanged.json()
    assert body["user"]["email"] == claims["email"]
    assert body["user"]["role"] == "student"
    assert body["return_to"] == "/profile"

    user = (
        db_session.query(User)
        .filter(User.email == claims["email"])
        .first()
    )
    assert user is not None
    assert user.password_login_disabled is True
    assert user.is_approved is True
    link = (
        db_session.query(ExternalIdentity)
        .filter(
            ExternalIdentity.provider_id == provider["id"],
            ExternalIdentity.subject == claims["sub"],
        )
        .first()
    )
    assert link is not None
    assert link.user_id == user.id

    replay = client.post("/api/auth/sso/exchange", json={"ticket": ticket})
    assert replay.status_code == 400


def test_sso_logout_returns_idp_end_session_url(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _provider(client, headers)
    claims = _claims()
    _mock_oidc(monkeypatch, claims)

    started = _start(client, provider["id"])
    ticket, error = _ticket_or_error(
        _callback(client, provider["id"], started["state"])
    )
    assert error is None and ticket
    exchanged = client.post("/api/auth/sso/exchange", json={"ticket": ticket})
    assert exchanged.status_code == 200, exchanged.text
    token = exchanged.json()["access_token"]

    logout = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout.status_code == 200, logout.text
    body = logout.json()
    assert body["post_logout_url"].startswith("https://idp.example.edu/logout?")
    assert "id_token_hint=fake-id-token" in body["post_logout_url"]
    assert "post_logout_redirect_uri=" in body["post_logout_url"]

    revoked = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert revoked.status_code == 401


def test_local_logout_has_no_sso_redirect(client, db_session):
    suffix = _suffix()
    user = User(
        username=f"sso_test_local_{suffix}",
        email=f"sso_test_local_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add(user)
    db_session.commit()
    login = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    logout = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout.status_code == 200, logout.text
    assert logout.json()["post_logout_url"] is None


def test_callback_can_run_on_a_second_replica(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _provider(client, headers)
    claims = _claims()
    _mock_oidc(monkeypatch, claims)

    started = _start(client, provider["id"])

    from app.main import app
    from fastapi.testclient import TestClient

    second = TestClient(app)
    callback = _callback(second, provider["id"], started["state"])
    ticket, error = _ticket_or_error(callback)
    assert error is None and ticket

    exchanged = second.post("/api/auth/sso/exchange", json={"ticket": ticket})
    assert exchanged.status_code == 200, exchanged.text


def test_verified_email_links_existing_student(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _provider(client, headers)
    suffix = _suffix()
    existing = User(
        username=f"sso_test_existing_{suffix}",
        email=f"sso_test_existing_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)
    claims = _claims(email=existing.email, verified=True)
    _mock_oidc(monkeypatch, claims)

    started = _start(client, provider["id"])
    ticket, error = _ticket_or_error(
        _callback(client, provider["id"], started["state"])
    )
    assert error is None and ticket

    link = (
        db_session.query(ExternalIdentity)
        .filter(
            ExternalIdentity.provider_id == provider["id"],
            ExternalIdentity.subject == claims["sub"],
        )
        .first()
    )
    assert link is not None
    assert link.user_id == existing.id
    assert db_session.query(User).filter(User.email == existing.email).count() == 1


def test_unverified_email_does_not_link_existing_account(
    client, db_session, monkeypatch
):
    headers = _admin(client, db_session)
    provider = _provider(client, headers)
    suffix = _suffix()
    existing = User(
        username=f"sso_test_unverified_{suffix}",
        email=f"sso_test_unverified_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add(existing)
    db_session.commit()
    claims = _claims(email=existing.email, verified=False)
    _mock_oidc(monkeypatch, claims)

    started = _start(client, provider["id"])
    _ticket, error = _ticket_or_error(
        _callback(client, provider["id"], started["state"])
    )
    assert error == "sso_failed"
    assert (
        db_session.query(ExternalIdentity)
        .filter(ExternalIdentity.subject == claims["sub"])
        .first()
        is None
    )


def test_admin_email_is_never_auto_linked(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _provider(client, headers)
    suffix = _suffix()
    admin = User(
        username=f"sso_test_other_admin_{suffix}",
        email=f"sso_test_other_admin_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="admin",
        is_admin=True,
    )
    db_session.add(admin)
    db_session.commit()
    claims = _claims(email=admin.email, verified=True)
    _mock_oidc(monkeypatch, claims)

    started = _start(client, provider["id"])
    _ticket, error = _ticket_or_error(
        _callback(client, provider["id"], started["state"])
    )
    assert error == "sso_failed"
    assert (
        db_session.query(ExternalIdentity)
        .filter(ExternalIdentity.subject == claims["sub"])
        .first()
        is None
    )


def test_pending_approval_redirects_without_ticket(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _provider(client, headers, config={"auto_approve": False})
    claims = _claims()
    _mock_oidc(monkeypatch, claims)

    started = _start(client, provider["id"])
    _ticket, error = _ticket_or_error(
        _callback(client, provider["id"], started["state"])
    )
    assert error == "pending_approval"
    user = db_session.query(User).filter(User.email == claims["email"]).first()
    assert user is not None
    assert user.is_approved is False


def test_expired_state_and_replay_fail(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _provider(client, headers)
    claims = _claims()
    _mock_oidc(monkeypatch, claims)

    started = _start(client, provider["id"])
    state_row = (
        db_session.query(SsoLoginState)
        .filter(SsoLoginState.state == started["state"])
        .first()
    )
    state_row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()

    _ticket, error = _ticket_or_error(
        _callback(client, provider["id"], started["state"])
    )
    assert error == "sso_failed"

    # A valid state cannot be consumed twice.
    started2 = _start(client, provider["id"])
    first = _callback(client, provider["id"], started2["state"])
    _ticket, error = _ticket_or_error(first)
    assert error is None
    second = _callback(client, provider["id"], started2["state"])
    _ticket, error = _ticket_or_error(second)
    assert error == "sso_failed"


def test_disabled_or_non_oidc_provider_is_not_public(
    client, db_session, monkeypatch
):
    headers = _admin(client, db_session)
    provider = _provider(client, headers, is_default=False)
    disabled = client.patch(
        f"/api/identity/providers/{provider['id']}",
        json={"enabled": False},
        headers=headers,
    )
    assert disabled.status_code == 200, disabled.text

    assert client.get("/api/auth/sso/providers").json()["providers"] == []
    missing = client.get(
        f"/api/auth/sso/oidc/{provider['id']}/login",
        follow_redirects=False,
    )
    assert missing.status_code == 404


def test_password_login_is_blocked_for_sso_only_account(client, db_session):
    suffix = _suffix()
    user = User(
        username=f"sso_test_only_{suffix}",
        email=f"sso_test_only_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
        password_login_disabled=True,
    )
    db_session.add(user)
    db_session.commit()

    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert resp.status_code == 401


def test_oidc_provider_test_endpoint(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _provider(client, headers)
    monkeypatch.setattr(
        oidc,
        "test_provider",
        lambda row: {
            "issuer": DISCOVERY["issuer"],
            "authorization_endpoint": DISCOVERY["authorization_endpoint"],
            "token_endpoint": DISCOVERY["token_endpoint"],
            "jwks_uri": DISCOVERY["jwks_uri"],
            "signing_keys": 2,
        },
    )
    resp = client.post(
        f"/api/identity/providers/{provider['id']}/test",
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["ok"] is True
    assert resp.json()["signing_keys"] == 2
