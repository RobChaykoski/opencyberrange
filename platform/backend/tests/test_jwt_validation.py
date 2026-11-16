"""Platform JWT validation contract.

The platform token is not a generic bearer JWT. It must carry issuer, audience,
purpose, all security-critical claims, a security version, and a jti that is
checked against the fail-closed revocation store.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.auth import RevocationUnavailable
from app.config import settings
from app.models import AuthSession, User

PASSWORD = "Correct#Horse7Battery"  # conftest TEST_PASSWORD; security-delta: allow
pytestmark = pytest.mark.db


def _login(client, user, password=PASSWORD):
    response = client.post(
        "/api/auth/login", data={"username": user.username, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()


def _claims(token):
    return jwt.decode(token, options={"verify_signature": False})


def _mint(claims: dict) -> str:
    return jwt.encode(claims, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def _mutate(token: str, **changes) -> str:
    claims = _claims(token)
    for key, value in changes.items():
        if value is None:
            claims.pop(key, None)
        else:
            claims[key] = value
    return _mint(claims)


def _get(client, token, path="/api/auth/me"):
    return client.get(path, headers={"Authorization": f"Bearer {token}"})


def test_valid_access_token_is_accepted(client, test_user):
    body = _login(client, test_user)
    claims = _claims(body["access_token"])
    assert claims["iss"] == settings.JWT_ISSUER
    assert claims["aud"] == settings.JWT_AUDIENCE
    assert claims["type"] == "access"
    assert claims["jti"]
    assert claims["nbf"]
    assert _get(client, body["access_token"]).status_code == 200


@pytest.mark.parametrize("claim", ["sub", "exp", "iat", "nbf", "jti", "iss", "aud", "type", "sec"])
def test_missing_required_claim_is_rejected(client, test_user, claim):
    token = _login(client, test_user)["access_token"]
    assert _get(client, _mutate(token, **{claim: None})).status_code == 401


def test_wrong_issuer_and_audience_are_rejected(client, test_user):
    token = _login(client, test_user)["access_token"]
    assert _get(client, _mutate(token, iss="another-environment")).status_code == 401
    assert _get(client, _mutate(token, aud="ocr-other")).status_code == 401


def test_wrong_purpose_is_rejected(client, test_user):
    token = _login(client, test_user)["access_token"]
    assert _get(client, _mutate(token, type="refresh")).status_code == 401
    assert _get(client, _mutate(token, type="password_reset")).status_code == 401
    assert _get(client, _mutate(token, type="portfolio")).status_code == 401


def test_wrong_algorithm_and_unsigned_token_are_rejected(client, test_user):
    claims = _claims(_login(client, test_user)["access_token"])
    none_token = jwt.encode(claims, "", algorithm="none")
    assert _get(client, none_token).status_code == 401


def test_external_key_headers_are_rejected(client, test_user):
    token = _login(client, test_user)["access_token"]
    claims = _claims(token)
    external = jwt.encode(
        claims,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        headers={"jku": "https://attacker.example/jwks.json"},
    )
    assert _get(client, external).status_code == 401


def test_expired_and_future_nbf_tokens_are_rejected(client, test_user):
    token = _login(client, test_user)["access_token"]
    now = datetime.now(timezone.utc)
    expired = _mutate(token, exp=now - timedelta(minutes=5))
    assert _get(client, expired).status_code == 401
    future = _mutate(token, nbf=now + timedelta(minutes=5))
    assert _get(client, future).status_code == 401


def test_refresh_token_cannot_be_used_as_access_token(client, test_user):
    body = _login(client, test_user)
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {body['refresh_token']}"},
    )
    assert response.status_code == 401


def test_access_token_cannot_be_used_as_refresh_token(client, test_user):
    body = _login(client, test_user)
    response = client.post(
        "/api/auth/refresh", json={"refresh_token": body["access_token"]}
    )
    assert response.status_code == 401


def test_revoked_jti_and_session_are_rejected(client, test_user):
    body = _login(client, test_user)
    token = body["access_token"]
    assert client.post(
        "/api/auth/logout", headers={"Authorization": f"Bearer {token}"}
    ).status_code == 200
    assert _get(client, token).status_code == 401


def test_disabled_deleted_and_revoked_session_are_rejected(
    client, db_session, test_user
):
    body = _login(client, test_user)
    token = body["access_token"]

    test_user.is_active = False
    db_session.commit()
    assert _get(client, token).status_code in {400, 401}
    test_user.is_active = True
    db_session.commit()

    session = db_session.get(AuthSession, body["session_id"])
    session.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db_session.commit()
    assert _get(client, token).status_code == 401

    # A fresh login has a new session; deleting the account invalidates it.
    body = _login(client, test_user)
    db_session.delete(db_session.get(User, test_user.id))
    db_session.commit()
    assert _get(client, body["access_token"]).status_code == 401


def test_role_change_invalidates_a_stale_token(client, db_session, test_user):
    body = _login(client, test_user)
    token = body["access_token"]
    test_user.role = "instructor"
    test_user.security_version = int(test_user.security_version or 1) + 1
    db_session.commit()
    response = _get(client, token)
    assert response.status_code == 401
    assert response.headers.get("x-security-version") == "stale"


def test_revocation_store_outage_fails_closed(client, test_user, monkeypatch):
    token = _login(client, test_user)["access_token"]

    def unavailable(*args, **kwargs):
        raise RevocationUnavailable("database down")

    monkeypatch.setattr("app.auth._check_token_revocation", unavailable)
    response = _get(client, token)
    assert response.status_code == 503
