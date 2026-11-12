"""Security gates must honour a setting change immediately.

The docs and module gates are described as hot toggles. A stale per-worker
cache would keep /docs (or a disabled module API) reachable after an
administrator turns it off.
"""

from __future__ import annotations

from app.services import settings_service


def test_docs_gate_uses_fresh_setting(client, monkeypatch):
    monkeypatch.setattr(
        settings_service,
        "get_setting",
        lambda db, key, default=None: "true",
    )
    monkeypatch.setattr(
        settings_service,
        "get_setting_fresh",
        lambda db, key, default=None: "false",
    )

    response = client.get("/docs")
    assert response.status_code == 404


def test_docs_gate_allows_when_fresh_setting_is_on(client, monkeypatch):
    monkeypatch.setattr(
        settings_service,
        "get_setting",
        lambda db, key, default=None: "false",
    )
    monkeypatch.setattr(
        settings_service,
        "get_setting_fresh",
        lambda db, key, default=None: "true",
    )

    response = client.get("/docs")
    assert response.status_code == 200
