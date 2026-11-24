"""Aggregate evidence operations for instructors and administrators.

This is an operational view, not a learner ranking. It answers "how much
evidence is waiting, what is it made of, and which competencies have accepted
evidence?" Small cohorts are suppressed so the view cannot become a proxy for an
individual learner.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

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
        "strongest_competencies": [],
        "weakest_competencies": [],
        "documentation": {
            "total": 0,
            "accepted": 0,
            "acceptance_rate": 0.0,
            "learners": 0,
        },
        "confidence_trend": {
            "recent_average": None,
            "prior_average": None,
            "delta": None,
            "recent_window_days": 30,
        },
        "program_effectiveness": {
            "accepted_rate": 0.0,
            "evidence_per_learner": 0.0,
            "review_backlog": 0,
        },
        "recent_reviews": [],
    }
    accepted_total = statuses.get("accepted", 0)
    result["program_effectiveness"] = {
        "accepted_rate": round(accepted_total / total * 100, 1) if total else 0.0,
        "evidence_per_learner": (
            round(total / learner_count, 1) if learner_count else 0.0
        ),
        "review_backlog": backlog_count,
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

    competency_status_rows = (
        base.join(
            EvidenceCompetency,
            EvidenceCompetency.evidence_id == EvidenceRecord.id,
        )
        .with_entities(
            EvidenceCompetency.competency_id,
            EvidenceRecord.status,
            func.count(EvidenceRecord.id),
        )
        .group_by(EvidenceCompetency.competency_id, EvidenceRecord.status)
        .all()
    )
    competency_learner_rows = (
        base.join(
            EvidenceCompetency,
            EvidenceCompetency.evidence_id == EvidenceRecord.id,
        )
        .with_entities(
            EvidenceCompetency.competency_id,
            func.count(distinct(EvidenceRecord.learner_id)),
        )
        .group_by(EvidenceCompetency.competency_id)
        .all()
    )
    learners_by_competency = {
        str(competency_id): int(count)
        for competency_id, count in competency_learner_rows
    }
    competency_data: dict[str, dict] = {}
    for competency_id, status, count in competency_status_rows:
        row = competency_data.setdefault(
            str(competency_id),
            {
                "competency_id": str(competency_id),
                "total": 0,
                "accepted": 0,
                "rejected": 0,
                "collected": 0,
                "in_review": 0,
                "learners": learners_by_competency.get(str(competency_id), 0),
            },
        )
        key = str(status)
        if key in row:
            row[key] = int(count)
        row["total"] += int(count)
    for row in competency_data.values():
        row["acceptance_rate"] = (
            round(row["accepted"] / row["total"] * 100, 1) if row["total"] else 0.0
        )
    competencies = list(competency_data.values())
    competencies.sort(
        key=lambda row: (-row["accepted"], -row["learners"], row["competency_id"])
    )
    result["competencies"] = [
        {"competency_id": row["competency_id"], "accepted": row["accepted"]}
        for row in competencies[:12]
    ]
    result["strongest_competencies"] = competencies[:12]
    weakest = [row for row in competencies if row["total"] >= 2]
    weakest.sort(
        key=lambda row: (
            row["acceptance_rate"],
            -row["rejected"],
            -row["total"],
            row["competency_id"],
        )
    )
    result["weakest_competencies"] = weakest[:12]

    workbook_base = base.filter(EvidenceRecord.source_type == "workbook")
    workbook_total = workbook_base.count()
    workbook_accepted = workbook_base.filter(
        EvidenceRecord.status == "accepted"
    ).count()
    workbook_learners = (
        workbook_base.with_entities(
            func.count(distinct(EvidenceRecord.learner_id))
        ).scalar()
        or 0
    )
    result["documentation"] = {
        "total": workbook_total,
        "accepted": workbook_accepted,
        "acceptance_rate": (
            round(workbook_accepted / workbook_total * 100, 1)
            if workbook_total
            else 0.0
        ),
        "learners": workbook_learners,
    }

    confidence_values = {"low": 1, "medium": 2, "high": 3}
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent_cutoff = now - timedelta(days=30)
    prior_cutoff = now - timedelta(days=60)

    def _average_confidence(start, end=None):
        query = base.with_entities(
            EvidenceRecord.confidence, func.count(EvidenceRecord.id)
        ).filter(EvidenceRecord.collected_at >= start)
        if end is not None:
            query = query.filter(EvidenceRecord.collected_at < end)
        counts = query.group_by(EvidenceRecord.confidence).all()
        weighted = sum(
            confidence_values.get(str(confidence), 0) * int(count)
            for confidence, count in counts
        )
        total_count = sum(int(count) for _confidence, count in counts)
        return round(weighted / total_count, 2) if total_count else None

    recent_average = _average_confidence(recent_cutoff)
    prior_average = _average_confidence(prior_cutoff, recent_cutoff)
    result["confidence_trend"] = {
        "recent_average": recent_average,
        "prior_average": prior_average,
        "delta": (
            round(recent_average - prior_average, 2)
            if recent_average is not None and prior_average is not None
            else None
        ),
        "recent_window_days": 30,
    }

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
