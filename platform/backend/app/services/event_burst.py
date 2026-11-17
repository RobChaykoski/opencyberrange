"""Event-aware per-IP limits for shared-NAT classrooms.

A competition row is the platform's scheduled event. Its window is widened by
``EVENT_BURST_BUFFER_MINUTES`` before the start and after the end, so a class
can register and sign in as it gathers and leaves. Outside that window the
strict limits apply.

The check is read at request time and cached per worker for a few seconds, so a
competition created or moved from the admin UI takes effect without a restart.
A database failure falls back to the strict limits.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger(__name__)

LOGIN_STRICT = os.environ.get("LOGIN_RATE_LIMIT", "10/minute")
LOGIN_BURST = os.environ.get("LOGIN_BURST_RATE_LIMIT", "40/minute")
REGISTRATION_STRICT = "5/minute;30/hour;100/day"
REGISTRATION_BURST = "20/minute;120/hour;400/day"

try:
    EVENT_BURST_BUFFER_MINUTES = max(
        0, int(os.environ.get("EVENT_BURST_BUFFER_MINUTES", "30"))
    )
except ValueError:
    EVENT_BURST_BUFFER_MINUTES = 30

_CACHE_TTL_SECONDS = 20.0
_cache_active: Optional[bool] = None
_cache_at = 0.0


def _utcnow() -> datetime:
    """Competition timestamps are stored as naive UTC."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def within_event_window(
    now: datetime,
    start_at: datetime,
    end_at: datetime,
    buffer_minutes: int = EVENT_BURST_BUFFER_MINUTES,
) -> bool:
    """Return True when ``now`` is inside the event window plus its buffer."""
    buffer = timedelta(minutes=buffer_minutes)
    return (start_at - buffer) <= now <= (end_at + buffer)


def _competition_is_live(now: datetime) -> bool:
    """Return True when an active, non-archived competition covers ``now``."""
    from app.database import SessionLocal
    from app.models import Competition

    db = SessionLocal()
    try:
        buffer = timedelta(minutes=EVENT_BURST_BUFFER_MINUTES)
        row = (
            db.query(Competition.id)
            .filter(
                Competition.is_active.is_(True),
                Competition.is_archived.is_(False),
                Competition.start_at <= now + buffer,
                Competition.end_at >= now - buffer,
            )
            .first()
        )
        return row is not None
    finally:
        db.close()


def event_window_active(now: Optional[datetime] = None) -> bool:
    """Return True when a scheduled event burst window is active.

    Passing ``now`` bypasses and does not fill the per-worker cache, which keeps
    unit tests deterministic.
    """
    global _cache_active, _cache_at

    use_cache = now is None
    if use_cache:
        if (
            _cache_active is not None
            and (time.monotonic() - _cache_at) < _CACHE_TTL_SECONDS
        ):
            return _cache_active
        now = _utcnow()

    try:
        active = _competition_is_live(now)
    except Exception:
        logger.warning("Event burst check failed; using strict limits", exc_info=True)
        active = False

    if use_cache:
        _cache_active = active
        _cache_at = time.monotonic()

    return active


def login_rate_limit() -> str:
    """Per-IP login allowance, relaxed inside an event window."""
    return LOGIN_BURST if event_window_active() else LOGIN_STRICT


def registration_rate_limit() -> str:
    """Per-IP registration allowance, relaxed inside an event window."""
    return REGISTRATION_BURST if event_window_active() else REGISTRATION_STRICT
