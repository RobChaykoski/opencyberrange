"""Threat-awareness snapshots are aggregated and validated before they ship."""

from __future__ import annotations

import json
import re
import uuid

import pytest

from app.auth import get_password_hash
from app.models import User
from app.services import threat_awareness

PASSWORD = "Threat#Pass123"  # test-only credential; security-delta: allow
pytestmark = pytest.mark.db

IPV4 = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")


def _user(db_session) -> User:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"threat_{suffix}",
        email=f"threat_{suffix}@example.org",
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
        "window_hours": 24,
        "source": {
            "name": "Test feed",
            "url": "https://example.org/feeds",
            "attribution": "Aggregated test counts.",
        },
        "method": {
            "aggregation": "country",
            "minimum_bucket_size": 25,
            "individual_addresses": False,
        },
        "totals": {
            "entries_observed": 200,
            "entries_reported": 180,
            "buckets_suppressed": 2,
        },
        "categories": [
            {"id": "level1", "label": "High risk", "count": 100},
            {"id": "level2", "label": "Moderate risk", "count": 80},
        ],
        "countries": [
            {"code": "US", "label": "United States", "count": 120},
            {"code": "DE", "label": "Germany", "count": 60},
        ],
        "notes": ["Test snapshot."],
    }
    document.update(overrides)
    return document


def _install(tmp_path, monkeypatch, document: dict):
    path = tmp_path / "threat-awareness.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    monkeypatch.setenv(threat_awareness.ENV_PATH, str(path))
    threat_awareness.reset_cache()
    return path


@pytest.fixture(autouse=True)
def _clear_cache():
    threat_awareness.reset_cache()
    yield
    threat_awareness.reset_cache()


def test_snapshot_endpoint_returns_aggregated_counts(client, db_session):
    response = client.get(
        "/api/threat-awareness", headers=_headers(client, _user(db_session))
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["mode"] == "sample"
    assert data["sample"] is True
    assert data["method"]["individual_addresses"] is False
    assert data["totals"]["entries_reported"] <= data["totals"]["entries_observed"]
    assert data["categories"][0]["count"] >= data["categories"][-1]["count"]
    assert data["countries"][0]["share"] == round(
        data["countries"][0]["count"] / data["totals"]["entries_reported"], 4
    )
    assert IPV4.search(json.dumps(data)) is None


def test_snapshot_endpoint_requires_authentication(client):
    response = client.get("/api/threat-awareness")

    assert response.status_code == 401


def test_snapshot_validation_computes_shares_and_sorts(tmp_path, monkeypatch):
    _install(tmp_path, monkeypatch, _document())
    data = threat_awareness.snapshot()

    assert data["mode"] == "snapshot"
    assert data["sample"] is False
    assert data["totals"]["coverage"] == 0.9
    assert [row["id"] for row in data["categories"]] == ["level1", "level2"]
    assert [row["code"] for row in data["countries"]] == ["US", "DE"]
    assert data["categories"][0]["share"] == round(100 / 180, 4)


def test_snapshot_rejects_an_unsuppressed_bucket(tmp_path, monkeypatch):
    document = _document(
        countries=[
            {"code": "US", "label": "United States", "count": 170},
            {"code": "DE", "label": "Germany", "count": 10},
        ]
    )
    _install(tmp_path, monkeypatch, document)

    with pytest.raises(threat_awareness.ThreatAwarenessError, match="minimum size"):
        threat_awareness.snapshot()


def test_snapshot_rejects_individual_addresses(tmp_path, monkeypatch):
    document = _document(notes=["Observed 203.0.113.9 repeatedly."])
    _install(tmp_path, monkeypatch, document)

    with pytest.raises(threat_awareness.ThreatAwarenessError, match="address-like"):
        threat_awareness.snapshot()


def test_snapshot_rejects_unknown_schema(tmp_path, monkeypatch):
    _install(tmp_path, monkeypatch, _document(schema_version=99))

    with pytest.raises(threat_awareness.ThreatAwarenessError, match="schema"):
        threat_awareness.snapshot()


def test_endpoint_reports_a_missing_snapshot(client, db_session, tmp_path, monkeypatch):
    monkeypatch.setenv(
        threat_awareness.ENV_PATH, str(tmp_path / "does-not-exist.json")
    )
    threat_awareness.reset_cache()

    response = client.get(
        "/api/threat-awareness", headers=_headers(client, _user(db_session))
    )

    assert response.status_code == 503
    assert response.headers["X-Error-Code"] == "threat_awareness_unavailable"
