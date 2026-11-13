"""First-run setup must never be claimable without the operator token."""

from app import config

VALID_PAYLOAD = {
    "admin_username": "firstadmin",
    "admin_email": "admin@university.edu",
    "admin_password": "Correct#Horse7Battery",
    "require_approval": True,
}


def test_complete_setup_refuses_when_token_not_configured(client, monkeypatch):
    monkeypatch.setattr(config.settings, "SETUP_TOKEN", "")
    resp = client.post("/api/setup/complete", json=VALID_PAYLOAD)
    assert resp.status_code == 503
    assert "SETUP_TOKEN" in resp.json()["detail"]


def test_complete_setup_rejects_wrong_token(client, monkeypatch):
    monkeypatch.setattr(config.settings, "SETUP_TOKEN", "install-token-value")
    resp = client.post(
        "/api/setup/complete",
        json={**VALID_PAYLOAD, "setup_token": "wrong-token"},
    )
    assert resp.status_code == 403
