"""Self-service password reset: token scope and the end-to-end API path."""
import jwt
import pytest

import app.routers.auth as auth_router
from app.config import settings
from app.services import password_reset

pytestmark = pytest.mark.db

NEW_PASSWORD = "Fresh#Cedar9Harbor"


def _request_reset(client, monkeypatch, email):
    captured = {}

    def fake_send(**kwargs):
        captured.update(kwargs)
        return True

    monkeypatch.setattr(auth_router.mail, "send_password_reset_email", fake_send)
    resp = client.post("/api/auth/forgot-password", json={"email": email})
    assert resp.status_code == 200, resp.text
    return resp, captured


def test_forgot_password_is_generic_for_unknown_address(client, db_schema):
    resp = client.post(
        "/api/auth/forgot-password", json={"email": "nobody-here@example.edu"}
    )
    assert resp.status_code == 200
    assert "if that email is registered" in resp.json()["message"].lower()


def test_forgot_password_sends_one_link_for_a_local_account(
    client, db_session, test_user, monkeypatch
):
    resp, captured = _request_reset(client, monkeypatch, test_user.email)

    assert "if that email is registered" in resp.json()["message"].lower()
    assert captured["to_email"] == test_user.email
    assert captured["username"] == test_user.username
    assert captured["token"]

    claims = password_reset.decode_reset_token(captured["token"])
    assert claims["sub"] == str(test_user.id)
    assert claims["purpose"] == "password_reset"
    assert claims["pwd"] != test_user.hashed_password


def test_reset_token_is_not_accepted_as_an_access_token(test_user):
    token = password_reset.create_reset_token(test_user)

    with pytest.raises(jwt.PyJWTError):
        jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            options={"require": ["sub", "exp", "iat"]},
        )


def test_reset_link_changes_the_password_and_cannot_be_reused(
    client, db_session, test_user, test_password, monkeypatch
):
    _, captured = _request_reset(client, monkeypatch, test_user.email)
    token = captured["token"]

    resp = client.post(
        "/api/auth/reset-password",
        json={
            "token": token,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["reauth_required"] is True

    db_session.refresh(test_user)
    old_login = client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": test_password},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": NEW_PASSWORD},
    )
    assert new_login.status_code == 200, new_login.text

    reuse = client.post(
        "/api/auth/reset-password",
        json={
            "token": token,
            "new_password": "Another#Willow2Orbit",
            "confirm_password": "Another#Willow2Orbit",
        },
    )
    assert reuse.status_code == 400
    assert "invalid or has expired" in reuse.json()["detail"].lower()


def test_reset_rejects_a_weak_password(client, test_user, monkeypatch):
    _, captured = _request_reset(client, monkeypatch, test_user.email)

    resp = client.post(
        "/api/auth/reset-password",
        json={
            "token": captured["token"],
            "new_password": "password",
            "confirm_password": "password",
        },
    )
    assert resp.status_code == 400


def test_reset_rejects_a_tampered_token(client, test_user):
    token = password_reset.create_reset_token(test_user)
    tampered = f"{token[:-2]}xy"

    resp = client.post(
        "/api/auth/reset-password",
        json={
            "token": tampered,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )
    assert resp.status_code == 400


def test_forgot_password_skips_sso_only_account(
    client, db_session, test_user, monkeypatch
):
    test_user.password_login_disabled = True
    db_session.commit()

    _, captured = _request_reset(client, monkeypatch, test_user.email)

    assert captured == {}
