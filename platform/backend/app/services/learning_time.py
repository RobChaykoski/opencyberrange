"""Shared learning-time calculations for analytics and achievements.

The platform has two time sources:

* ``LabCompletion.time_spent_minutes`` is recorded when a learner captures the
  flag. The submission path derives it from the session windows up to the
  completion, so it is the best per-exercise figure for completed work.
* ``LabSession`` rows cover work that has not produced a completion yet. They
  are bounded by ``stopped_at``, ``expires_at``, and "now" so an abandoned tab
  cannot inflate a learner's hours forever.

A single learner/exercise pair is counted once. When a timed completion exists
we use it; otherwise we fall back to the merged session windows. This keeps the
number honest without inventing a second tracking system.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Iterable

# One exercise cannot credibly consume more than eight hours in this model.
# The cap only bites when an old session has no usable stop/expiry value.
LEARNING_MINUTES_PER_EXERCISE_CAP = 8 * 60


def _as_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def bounded_session_minutes(sessions: Iterable) -> float:
    """Merged session time for one learner/exercise, capped for sanity."""
    now = datetime.now(timezone.utc)
    intervals = []
    for row in sessions:
        start = _as_utc(getattr(row, "started_at", None))
        if start is None:
            continue
        ends = [now]
        stopped = _as_utc(getattr(row, "stopped_at", None))
        expires = _as_utc(getattr(row, "expires_at", None))
        if stopped is not None:
            ends.append(stopped)
        if expires is not None:
            ends.append(expires)
        end = min(ends)
        if end > start:
            intervals.append((start, end))

    if not intervals:
        return 0.0

    intervals.sort(key=lambda item: item[0])
    total = 0.0
    current_start, current_end = intervals[0]
    for start, end in intervals[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            total += (current_end - current_start).total_seconds()
            current_start, current_end = start, end
    total += (current_end - current_start).total_seconds()
    return min(total / 60, LEARNING_MINUTES_PER_EXERCISE_CAP)


def learning_minutes_by_pair(completions: Iterable, sessions: Iterable) -> dict:
    """Return ``{(user_id, lab_id): minutes}`` without double-counting."""
    minutes: dict[tuple[int, int], int] = {}
    timed_pairs = set()

    for row in completions:
        value = getattr(row, "time_spent_minutes", None)
        if not value or value <= 0:
            continue
        key = (row.user_id, row.lab_id)
        minutes[key] = minutes.get(key, 0) + int(value)
        timed_pairs.add(key)

    by_pair: dict[tuple[int, int], list] = {}
    for row in sessions:
        key = (row.user_id, row.lab_id)
        if key in timed_pairs:
            continue
        by_pair.setdefault(key, []).append(row)

    for key, rows in by_pair.items():
        value = int(round(bounded_session_minutes(rows)))
        if value > 0:
            minutes[key] = minutes.get(key, 0) + value

    return minutes


def learning_minutes_by_user(pair_minutes: dict) -> Counter:
    """Collapse ``{(user_id, lab_id): minutes}`` into per-user totals."""
    totals = Counter()
    for (user_id, _lab_id), value in pair_minutes.items():
        totals[user_id] += value
    return totals


def total_learning_minutes(db, user_id: int) -> int:
    """Total tracked learning minutes for one account."""
    from app.models import LabCompletion, LabSession

    completions = db.query(LabCompletion).filter(
        LabCompletion.user_id == user_id,
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).all()
    sessions = db.query(LabSession).filter(
        LabSession.user_id == user_id,
        LabSession.is_diagnostic == False,  # noqa: E712 - SQL boolean comparison
    ).all()
    pairs = learning_minutes_by_pair(completions, sessions)
    return int(sum(learning_minutes_by_user(pairs).values()))
