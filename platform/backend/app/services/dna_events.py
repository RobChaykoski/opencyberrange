"""Exercise-side adapter that emits Cyber DNA activity events.

This is the only place that maps a lab completion to competency IDs and reads
course/attempt context. The Cyber DNA package consumes the resulting event and
never sees the exercise tables.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.cyber_dna.events import ActivityCompleted
from app.cyber_dna.service import ingest_activity
from app.models import (
    Course,
    CourseEnrollment,
    CourseLabAssignment,
    FlagAttempt,
    Lab,
    LabCompletion,
)
from app.services.competency_taxonomy import evidence_competencies_for_lab

ADAPTER_VERSION = "exercise-2026.1"


def _is_voluntary(db: Session, user_id: int, lab_id: int) -> bool:
    course_ids = [
        row[0]
        for row in db.query(CourseEnrollment.course_id)
        .join(Course, Course.id == CourseEnrollment.course_id)
        .filter(
            CourseEnrollment.user_id == user_id,
            Course.is_active.is_(True),
        )
        .all()
    ]
    if not course_ids:
        return True
    assigned = (
        db.query(CourseLabAssignment.id)
        .filter(
            CourseLabAssignment.course_id.in_(course_ids),
            CourseLabAssignment.lab_id == lab_id,
        )
        .first()
    )
    return assigned is None


def _prior_failed_attempts(db: Session, user_id: int, lab_id: int) -> int:
    return int(
        db.query(func.count(FlagAttempt.id))
        .filter(
            FlagAttempt.user_id == user_id,
            FlagAttempt.lab_id == lab_id,
            FlagAttempt.is_correct.is_(False),
            ~FlagAttempt.flag_submitted.like("HINT%"),
        )
        .scalar()
        or 0
    )


def build_completion_event(
    db: Session,
    user_id: int,
    completion: LabCompletion,
    lab: Lab | None,
) -> ActivityCompleted | None:
    """Build the event for one completion, or None when nothing maps."""
    if completion is None or lab is None:
        return None
    competencies = evidence_competencies_for_lab(lab)
    if not competencies:
        return None
    weight = 1.0 / len(competencies)
    occurred = completion.completed_at or datetime.now(timezone.utc).replace(
        tzinfo=None
    )
    if occurred.tzinfo is not None:
        occurred = occurred.replace(tzinfo=None)
    return ActivityCompleted(
        event_id=f"completion:{completion.id}",
        learner_id=user_id,
        activity_id=lab.slug,
        activity_category=(lab.category or "general"),
        competency_weights={competency_id: weight for competency_id in competencies},
        difficulty=(lab.difficulty or "beginner"),
        attempts=int(completion.attempts or 1),
        hints_used=int(completion.hints_used or 0),
        duration_minutes=completion.time_spent_minutes,
        prior_failed_attempts=_prior_failed_attempts(db, user_id, lab.id),
        voluntary=_is_voluntary(db, user_id, lab.id),
        occurred_at=occurred,
        source_version=ADAPTER_VERSION,
    )


def emit_completion_event(
    db: Session,
    user_id: int,
    completion: LabCompletion,
    lab: Lab | None,
) -> int:
    """Build and ingest one completion event. Returns the rows written."""
    event = build_completion_event(db, user_id, completion, lab)
    if event is None:
        return 0
    return ingest_activity(db, event)
