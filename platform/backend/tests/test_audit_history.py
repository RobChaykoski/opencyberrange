"""Regression tests for audit history and impersonation status."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.routers.audit import _event_payload, _session_status


def _naive(value: datetime) -> datetime:
    return value.replace(tzinfo=None)


def _row(**kwargs):
    base = {
        "ended_at": None,
        "expires_at": _naive(datetime.now(timezone.utc) + timedelta(hours=1)),
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_live_impersonation_status():
    assert _session_status(_row(), _naive(datetime.now(timezone.utc))) == "live"


def test_expired_impersonation_status():
    now = _naive(datetime.now(timezone.utc))
    assert _session_status(_row(expires_at=now - timedelta(minutes=1)), now) == "expired"


def test_ended_impersonation_status():
    now = _naive(datetime.now(timezone.utc))
    assert _session_status(_row(ended_at=now), now) == "ended"


def test_event_payload_parses_json_detail():
    event = SimpleNamespace(
        id=1,
        event_type="impersonation_start",
        actor_id=7,
        target_type="user",
        target_id=9,
        target_label="student",
        detail=json.dumps({"mode": "user"}),
        ip_address="127.0.0.1",
        created_at=datetime(2026, 11, 14, 6, 0, 0),
    )
    payload = _event_payload(event, "instructor")
    assert payload["detail"] == {"mode": "user"}
    assert payload["actor_name"] == "instructor"
    assert payload["label"] == "Started Impersonation"
