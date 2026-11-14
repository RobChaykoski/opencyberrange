"""Pause/resume payload helpers for lab sessions."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.routers.labs import _session_pause_payload


def test_running_session_reports_remaining_time():
    now = datetime.now(timezone.utc)
    session = SimpleNamespace(
        id=1,
        status="running",
        expires_at=now + timedelta(hours=1),
        paused_at=None,
        paused_seconds=0,
        pause_reason=None,
    )
    payload = _session_pause_payload(session)
    assert payload["is_paused"] is False
    assert 3500 < payload["time_remaining_seconds"] <= 3600


def test_paused_session_freezes_remaining_time():
    now = datetime.now(timezone.utc)
    paused_at = now - timedelta(minutes=10)
    session = SimpleNamespace(
        id=2,
        status="running",
        expires_at=paused_at + timedelta(minutes=30),
        paused_at=paused_at,
        paused_seconds=0,
        pause_reason="medical appointment",
    )
    payload = _session_pause_payload(session)
    assert payload["is_paused"] is True
    assert payload["pause_reason"] == "medical appointment"
    assert payload["time_remaining_seconds"] == 1800
