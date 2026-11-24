"""Aggregate evidence operations for instructors and administrators.

This is an operational view, not a learner ranking. It answers "how much
evidence is waiting, what is it made of, and which competencies have accepted
evidence?" Small cohorts are suppressed so the view cannot become a proxy for an
individual learner.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.models import EvidenceCompetency, EvidenceRecord, EvidenceReview, User
from app.services.evidence import apply_scope

SMALL_COHORT = 5


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() + "Z" if value else None


def overview(db: Session, viewer: User) -> dict:
    base = apply_scope(db.query(EvidenceRecord), db, viewer)
    total = base.count()
    learner_count = (
        base.with_entities(func.count(distinct(EvidenceRecord.learner_id))).scalar()
        or 0
    )
    accepted_learners = (
        base.filter(EvidenceRecord.status == "accepted")
        .with_entities(func.count(distinct(EvidenceRecord.learner_id)))
        .scalar()
        or 0
    )
    status_rows = (
        base.with_entities(EvidenceRecord.status, func.count(EvidenceRecord.id))
        .group_by(EvidenceRecord.status)
        .all()
    )
    statuses = {str(status): int(count) for status, count in status_rows}

    backlog = base.filter(
        EvidenceRecord.status.in_(("collected", "in_review"))
    )
    backlog_count = backlog.count()
    oldest = backlog.with_entities(func.min(EvidenceRecord.collected_at)).scalar()
    oldest_age_days = None
    if oldest:
        oldest_aware = oldest.replace(tzinfo=timezone.utc) if oldest.tzinfo is None else oldest
        oldest_age_days = max(
            0, (datetime.now(timezone.utc) - oldest_aware).days
        )

    suppressed = viewer.role != "admin" and learner_count < SMALL_COHORT
    result = {
        "totals": {
            "evidence": total,
            "learners": learner_count,
            "accepted_learners": accepted_learners,
            "accepted": statuses.get("accepted", 0),
            "awaiting_review": statuses.get("collected", 0)
            + statuses.get("in_review", 0),
            "rejected": statuses.get("rejected", 0),
        },
        "backlog": {
            "awaiting_review": backlog_count,
            "oldest_collected_at": _iso(oldest),
            "oldest_age_days": oldest_age_days,
        },
        "statuses": statuses,
        "suppressed": suppressed,
        "small_cohort": SMALL_COHORT,
        "suppression_note": (
            f"Aggregate breakdowns are hidden because this scope has fewer than "
            f"{SMALL_COHORT} learners with evidence."
            if suppressed
            else None
        ),
        "sources": [],
        "rubrics": [],
        "competencies": [],
        "recent_reviews": [],
    }
    if suppressed:
        return result

    source_rows = (
        base.with_entities(EvidenceRecord.source_type, func.count(EvidenceRecord.id))
        .group_by(EvidenceRecord.source_type)
        .order_by(func.count(EvidenceRecord.id).desc(), EvidenceRecord.source_type)
        .all()
    )
    result["sources"] = [
        {"source_type": str(source), "count": int(count)}
        for source, count in source_rows
    ]

    rubric_rows = (
        base.with_entities(
            EvidenceRecord.rubric_id,
            EvidenceRecord.rubric_version,
            func.count(EvidenceRecord.id),
        )
        .group_by(EvidenceRecord.rubric_id, EvidenceRecord.rubric_version)
        .order_by(func.count(EvidenceRecord.id).desc(), EvidenceRecord.rubric_id)
        .all()
    )
    result["rubrics"] = [
        {
            "rubric_id": str(rubric_id),
            "rubric_version": str(version),
            "count": int(count),
        }
        for rubric_id, version, count in rubric_rows
    ]

    competency_rows = (
        base.join(
            EvidenceCompetency,
            EvidenceCompetency.evidence_id == EvidenceRecord.id,
        )
        .filter(EvidenceRecord.status == "accepted")
        .with_entities(
            EvidenceCompetency.competency_id,
            func.count(distinct(EvidenceCompetency.evidence_id)),
        )
        .group_by(EvidenceCompetency.competency_id)
        .order_by(
            func.count(distinct(EvidenceCompetency.evidence_id)).desc(),
            EvidenceCompetency.competency_id,
        )
        .limit(12)
        .all()
    )
    result["competencies"] = [
        {"competency_id": str(competency_id), "accepted": int(count)}
        for competency_id, count in competency_rows
    ]

    review_query = apply_scope(
        db.query(EvidenceReview).join(
            EvidenceRecord, EvidenceReview.evidence_id == EvidenceRecord.id
        ),
        db,
        viewer,
    )
    review_rows = (
        review_query.order_by(EvidenceReview.reviewed_at.desc())
        .limit(8)
        .all()
    )
    result["recent_reviews"] = [
        {
            "evidence_id": review.evidence_id,
            "decision": review.decision,
            "weighted_score": review.weighted_score,
            "reviewed_at": _iso(review.reviewed_at),
            "reviewer_id": review.reviewer_id,
        }
        for review in review_rows
    ]
    return result
