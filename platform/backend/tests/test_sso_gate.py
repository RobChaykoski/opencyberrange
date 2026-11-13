"""The deployment-wide SSO switch must fail closed and leave local login alone."""

from app.routers import sso as sso_module


def test_sso_disabled_hides_providers(client, monkeypatch):
    monkeypatch.setattr(
        sso_module, "get_setting_fresh", lambda db, key, default=None: "false"
    )
    response = client.get("/api/auth/sso/providers")
    assert response.status_code == 200
    assert response.json() == {"providers": [], "sso_enabled": False}


def test_sso_disabled_rejects_ticket_exchange(client, monkeypatch):
    monkeypatch.setattr(
        sso_module, "get_setting_fresh", lambda db, key, default=None: "false"
    )
    response = client.post(
        "/api/auth/sso/exchange", json={"ticket": "one-time-ticket-value"}
    )
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()


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
