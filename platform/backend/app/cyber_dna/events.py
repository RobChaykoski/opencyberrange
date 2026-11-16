"""Versioned activity events accepted by the Cyber DNA bounded context.

The exercise platform owns labs, workbooks, completions, courses, and their
database tables. Cyber DNA never reads those tables. It consumes this event,
which carries only the facts the DNA model needs and the competency weights the
exercise-side adapter resolved.

The event is deliberately free of exercise prose, flags, answers, and learner
PII. ``learner_id`` is the platform's stable user id; it is the only identity
the DNA store keeps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

EVENT_VERSION = "2026.1"


def _naive_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@dataclass(frozen=True)
class ActivityCompleted:
    """One completed activity, already mapped to competencies."""

    event_id: str
    learner_id: int
    activity_id: str
    activity_category: str
    competency_weights: dict[str, float]
    difficulty: str = "beginner"
    attempts: int = 1
    hints_used: int = 0
    duration_minutes: int | None = None
    prior_failed_attempts: int = 0
    voluntary: bool = True
    occurred_at: datetime = field(default_factory=_naive_utc_now)
    source_version: str = EVENT_VERSION

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id is required")
        if not self.learner_id:
            raise ValueError("learner_id is required")
        if not self.activity_id:
            raise ValueError("activity_id is required")
        if not self.competency_weights:
            raise ValueError("competency_weights is required")
        total = sum(float(value) for value in self.competency_weights.values())
        if total <= 0:
            raise ValueError("competency_weights must sum to a positive value")
        # Normalise at the boundary so the ledger always stores a share.
        object.__setattr__(
            self,
            "competency_weights",
            {
                competency_id: float(weight) / total
                for competency_id, weight in self.competency_weights.items()
                if weight > 0
            },
        )
