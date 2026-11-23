"""The deployment-wide SSO switch must fail closed and leave local login alone."""

import uuid

import pytest

from app.models import IdentityProvider, SsoLoginTicket
from app.routers import sso as sso_module
from app.services import sso_flow

pytestmark = pytest.mark.db


def test_sso_disabled_hides_providers(client, monkeypatch):
    monkeypatch.setattr(
        sso_module, "get_setting_fresh", lambda db, key, default=None: "false"
    )
    response = client.get("/api/auth/sso/providers")
    assert response.status_code == 200
    assert response.json() == {"providers": [], "sso_enabled": False}


def test_sso_disabled_rejects_unknown_ticket(client, monkeypatch):
    monkeypatch.setattr(
        sso_module, "get_setting_fresh", lambda db, key, default=None: "false"
    )
    response = client.post(
        "/api/auth/sso/exchange", json={"ticket": "one-time-ticket-value"}
    )
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


def test_sso_disabled_exchanges_an_already_issued_ticket(
    client, db_session, test_user, monkeypatch
):
    """LTI launches exchange tickets even when institution SSO is switched off."""
    suffix = uuid.uuid4().hex[:10]
    provider = IdentityProvider(
        name=f"Pytest LTI {suffix}",
        kind="oidc",
        enabled=True,
        config="{}",
    )
    db_session.add(provider)
    db_session.commit()
    db_session.refresh(provider)
    ticket = sso_flow.create_login_ticket(
        db_session, user=test_user, provider=provider, return_to="/dashboard"
    )
    try:
        monkeypatch.setattr(
            sso_module, "get_setting_fresh", lambda db, key, default=None: "false"
        )
        response = client.post("/api/auth/sso/exchange", json={"ticket": ticket})

        assert response.status_code == 200, response.text
        assert response.json()["user"]["email"] == test_user.email
    finally:
        db_session.query(SsoLoginTicket).filter(
            SsoLoginTicket.ticket == ticket
        ).delete(synchronize_session=False)
        db_session.query(IdentityProvider).filter(
            IdentityProvider.id == provider.id
        ).delete(synchronize_session=False)
        db_session.commit()


def test_sso_enabled_accepts_truthy_values(monkeypatch):
    for value in ("true", "1", "yes", "on"):
        monkeypatch.setattr(
            sso_module, "get_setting_fresh", lambda db, key, default=None, v=value: v
        )
        assert sso_module.sso_enabled(None) is True


def test_sso_enabled_defaults_to_on_when_unset(monkeypatch):
    monkeypatch.setattr(
        sso_module, "get_setting_fresh", lambda db, key, default=None: default
    )
    assert sso_module.sso_enabled(None) is True
