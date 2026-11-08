"""RangeBox capacity policy.

The host's computed maximum is the number of RangeBoxes the memory and CPU
maths can hold. Running that many at once leaves no headroom for the backend,
database, SIEM, or interactive VNC, so the live cap is a configurable
percentage of the ceiling.

The ceiling is the measured Level 4 stress-test maximum when one has been
recorded, otherwise the computed maximum. Both the percentage and the measured
ceiling are stored in ``platform_settings`` so an administrator can change the
policy without restarting the backend. Values are cached briefly because the
capacity property is read on every launch and by the RangeBox meter.
"""

from __future__ import annotations

import math
import time
from typing import Optional

from datetime import datetime, timezone

DEFAULT_PERCENT = 75
MIN_PERCENT = 10
MAX_PERCENT = 100
DEFAULT_STRESS_MAX = 0
_CACHE_TTL_SECONDS = 10.0

_cached_policy: Optional[tuple[float, int, int]] = None


def clamp_percent(value) -> int:
    """Return a usable percentage, falling back to the documented default."""
    try:
        percent = int(float(value))
    except (TypeError, ValueError):
        return DEFAULT_PERCENT
    return max(MIN_PERCENT, min(MAX_PERCENT, percent))


def clamp_stress_max(value) -> int:
    """Return a recorded stress ceiling, or 0 when none has been recorded."""
    try:
        stress_max = int(float(value))
    except (TypeError, ValueError):
        return DEFAULT_STRESS_MAX
    return max(0, stress_max)


def effective_max(computed_max: int, percent: int, stress_max: int = 0) -> int:
    """Apply the headroom percentage to the measured or computed ceiling.

    A recorded stress ceiling lowers the ceiling when a host cannot actually
    fill its memory-derived maximum. It never raises it above the computed
    maximum, so a stale value from a larger host cannot over-authorise.
    Small hosts still get one box: a 1-box host at 75% would otherwise round
    down to zero and make the platform unusable.
    """
    try:
        computed = max(0, int(computed_max))
    except (TypeError, ValueError):
        computed = 0
    if computed <= 0:
        return 0
    measured = clamp_stress_max(stress_max)
    ceiling = min(computed, measured) if measured > 0 else computed
    pct = clamp_percent(percent)
    return max(1, int(math.floor(ceiling * pct / 100)))


def _read_policy(db) -> tuple[int, int]:
    from app.services.settings_service import get_setting

    percent = clamp_percent(
        get_setting(db, "rangebox_capacity_percent", str(DEFAULT_PERCENT))
    )
    stress_max = clamp_stress_max(
        get_setting(db, "rangebox_stress_max", str(DEFAULT_STRESS_MAX))
    )
    return percent, stress_max


def get_capacity_policy(db=None) -> tuple[int, int]:
    """Read ``(percent, measured_ceiling)`` with a short-lived cache.

    ``db`` is optional so callers in a request can pass their session. When it
    is omitted (for example from the Docker manager) a short-lived session is
    opened. Any failure falls back to the default rather than blocking all
    launches on a settings read.
    """
    global _cached_policy

    now = time.monotonic()
    if _cached_policy is not None and now - _cached_policy[0] < _CACHE_TTL_SECONDS:
        return _cached_policy[1], _cached_policy[2]

    close_db = False
    percent = DEFAULT_PERCENT
    stress_max = DEFAULT_STRESS_MAX
    try:
        if db is None:
            from app.database import SessionLocal

            db = SessionLocal()
            close_db = True
        percent, stress_max = _read_policy(db)
    except Exception:
        percent = DEFAULT_PERCENT
        stress_max = DEFAULT_STRESS_MAX
    finally:
        if close_db and db is not None:
            db.close()

    _cached_policy = (now, percent, stress_max)
    return percent, stress_max


def get_capacity_percent(db=None) -> int:
    """Backwards-compatible accessor for the percentage alone."""
    return get_capacity_policy(db)[0]


def record_stress_ceiling(stress_max: int, computed_max: int, db=None) -> int:
    """Persist a measured Level 4 ceiling, clamped to the computed maximum.

    Returns the value that was stored. A zero or invalid measurement leaves the
    existing value alone.
    """
    global _cached_policy

    measured = clamp_stress_max(stress_max)
    if measured <= 0:
        return 0
    computed = clamp_stress_max(computed_max)
    if computed > 0:
        measured = min(measured, computed)

    close_db = False
    try:
        if db is None:
            from app.database import SessionLocal

            db = SessionLocal()
            close_db = True
        from app.services.settings_service import set_setting

        set_setting(db, "rangebox_stress_max", str(measured))
        set_setting(
            db,
            "rangebox_stress_tested_at",
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
    finally:
        if close_db and db is not None:
            db.close()

    _cached_policy = None
    return measured


def invalidate_cache() -> None:
    """Drop the local cache after an administrator changes the setting."""
    global _cached_policy
    _cached_policy = None
