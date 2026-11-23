"""Shared reporting-window parsing for instructor and analytics endpoints.

One parser keeps the frontend presets, the API validation, and the exported
labels on the same definition. Windows are half-open at the start and closed at
the end: ``start <= timestamp <= end``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

MAX_WINDOW_DAYS = 366


@dataclass(frozen=True)
class Window:
    start: datetime
    end: datetime
    days: float


def _parse(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Invalid ISO 8601 datetime: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_window(
    start: str | None,
    end: str | None,
    *,
    default_days: int = 7,
    max_days: int = MAX_WINDOW_DAYS,
    now: datetime | None = None,
) -> Window:
    """Parse an explicit window or fall back to a rolling default.

    A missing ``end`` means "now". A missing ``start`` means
    ``end - default_days``. The caller decides whether a short window is
    appropriate for the metric; this parser only validates the bounds.
    """
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    window_end = _parse(end) if end else current
    window_start = _parse(start) if start else window_end - timedelta(days=default_days)

    if window_start >= window_end:
        raise ValueError("Period start must be before period end")

    span_days = (window_end - window_start).total_seconds() / 86400
    if span_days > max_days:
        raise ValueError(f"Period cannot exceed {max_days} days")

    return Window(start=window_start, end=window_end, days=round(span_days, 2))
