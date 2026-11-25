"""Ransomware snapshots expose group aggregates only, never victim details."""

from __future__ import annotations

import json
import uuid

import pytest

from app.auth import get_password_hash
from app.models import User
from app.services import ransomware_activity

PASSWORD = "Ransom#Pass123"  # test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db_session) -> User:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"ransom_{suffix}",
        email=f"ransom_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _headers(client, user: User) -> dict:
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _document(**overrides) -> dict:
    document = {
        "schema_version": 1,
        "mode": "snapshot",
        "generated_at": "2026-11-24T00:00:00Z",
        "window_days": 7,
        "source": {
            "name": "RansomLook",
            "url": "https://www.ransomlook.io/",
            "licence": "CC BY 4.0",
            "attribution": "Aggregated counts.",
        },
        "method": {
            "aggregation": "group",
            "victim_details": False,
            "links": False,
            "crypto_addresses": False,
        },
        "totals": {
            "posts_24h": 40,
            "posts_month": 300,
            "posts_90d": 900,
            "posts_year": 3000,
            "posts_total": 10000,
            "groups": 600,
            "groups_online": 700,
            "markets": 150,
            "window_posts": 200,
        },
        "groups": [
            {"name": "alpha", "count": 120},
            {"name": "beta", "count": 50},
        ],
        "notes": ["Aggregated per group."],
    }
    document.update(overrides)
    return document


def _install(tmp_path, monkeypatch, document: dict):
    path = tmp_path / "ransomware-activity.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    monkeypatch.setenv(ransomware_activity.ENV_PATH, str(path))
    ransomware_activity.reset_cache()
    return path


@pytest.fixture(autouse=True)
def _clear_cache():
    ransomware_activity.reset_cache()
    yield
    ransomware_activity.reset_cache()


def test_endpoint_returns_aggregated_snapshot(client, db_session):
    response = client.get(
        "/api/ransomware-activity", headers=_headers(client, _user(db_session))
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["mode"] in {"sample", "snapshot"}
    assert data["method"]["victim_details"] is False
    assert data["method"]["links"] is False
    assert data["groups"][0]["count"] >= data["groups"][-1]["count"]
    assert data["groups"][0]["share"] == round(
        data["groups"][0]["count"] / data["totals"]["window_posts"], 4
    )
    body = json.dumps(data).lower()
    for forbidden in ("post_title", "magnet:", "onion", "crypto_addresses\": true"):
        assert forbidden not in body


def test_endpoint_requires_authentication(client):
    response = client.get("/api/ransomware-activity")

    assert response.status_code == 401


def test_validation_sorts_and_computes_shares(tmp_path, monkeypatch):
    _install(tmp_path, monkeypatch, _document())
    data = ransomware_activity.snapshot()

    assert data["sample"] is False
    assert [row["name"] for row in data["groups"]] == ["alpha", "beta"]
    assert data["groups"][0]["share"] == 0.6


def test_validation_rejects_victim_details(tmp_path, monkeypatch):
    document = _document()
    document["method"]["victim_details"] = True
    _install(tmp_path, monkeypatch, document)

    with pytest.raises(ransomware_activity.RansomwareActivityError, match="victim_details"):
        ransomware_activity.snapshot()


def test_validation_rejects_a_url_or_contact_group_name(tmp_path, monkeypatch):
    for name in ("http://example.org", "victim@example.org", "x.onion"):
        _install(
            tmp_path,
            monkeypatch,
            _document(groups=[{"name": name, "count": 10}]),
        )
        with pytest.raises(ransomware_activity.RansomwareActivityError):
            ransomware_activity.snapshot()


def test_validation_rejects_counts_above_the_window_total(tmp_path, monkeypatch):
    _install(
        tmp_path,
        monkeypatch,
        _document(groups=[{"name": "alpha", "count": 250}]),
    )

    with pytest.raises(ransomware_activity.RansomwareActivityError, match="window total"):
        ransomware_activity.snapshot()


def test_endpoint_reports_a_missing_snapshot(client, db_session, tmp_path, monkeypatch):
    monkeypatch.setenv(
        ransomware_activity.ENV_PATH, str(tmp_path / "does-not-exist.json")
    )
    ransomware_activity.reset_cache()

    response = client.get(
        "/api/ransomware-activity", headers=_headers(client, _user(db_session))
    )

    assert response.status_code == 503
    assert response.headers["X-Error-Code"] == "ransomware_activity_unavailable"
