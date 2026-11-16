"""Public runtime configuration for unauthenticated visitors."""

from app.routers import public_config as public_config_router


def _patch_settings(monkeypatch, values):
    def fake_setting(db, key, default=None):
        return values.get(key, default)

    monkeypatch.setattr(public_config_router, "get_setting_fresh", fake_setting)


def test_public_config_is_unauthenticated_and_no_store(client, monkeypatch):
    _patch_settings(
        monkeypatch,
        {"wiki_origin": " https://wiki.example.edu ", "require_approval": " FALSE "},
    )

    response = client.get("/api/config/public")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == {
        "wiki_origin": "https://wiki.example.edu",
        "require_approval": False,
    }


def test_public_config_defaults_require_approval(client, monkeypatch):
    _patch_settings(monkeypatch, {})

    response = client.get("/api/config/public")

    assert response.status_code == 200
    assert response.json() == {
        "wiki_origin": "",
        "require_approval": True,
    }


def test_public_config_only_literal_false_disables_approval(client, monkeypatch):
    _patch_settings(
        monkeypatch,
        {"wiki_origin": "https://wiki.example.edu", "require_approval": "0"},
    )

    response = client.get("/api/config/public")

    assert response.status_code == 200
    assert response.json()["require_approval"] is True
