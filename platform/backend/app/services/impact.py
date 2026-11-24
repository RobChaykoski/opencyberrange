"""Impact and legacy scoring.

The scoring math is pure and deterministic so it can be reviewed, tested, and
replayed. The ledger functions add access scope and persistence.

Design rules enforced here:

* self-reported work is pending and earns no credit;
* reach grows logarithmically and is capped;
* repeats of one kind diminish within a rolling year;
* a quality rating below 3.0 excludes a contribution;
* unused work decays after two years;
* stewardship is a separate trust record, never inferred from activity.
"""

from __future__ import annotations

import hashlib
import math
from datetime import datetime, timezone

from sqlalchemy import false
from sqlalchemy.orm import Session

from app.models import User
from app.models.impact import (
    IMPACT_DIMENSIONS,
    IMPACT_ORIGINALITIES,
    IMPACT_VALIDATION_LEVELS,
    ImpactContribution,
    StewardshipEvent,
)
from app.services.evidence import (
    READ_ROLES,
    REVIEW_ROLES,
    TENANT_WIDE_READ_ROLES,
    _covered_learner_ids,
    _tenant_of,
)

BASE_POINTS: dict[str, dict[str, int]] = {
    "build": {
        "lab": 50,
        "detection_rule": 40,
        "tool": 60,
        "workbook": 40,
        "playbook": 30,
        "research": 50,
        "integration": 40,
    },
    "protect": {
        "assessment": 40,
        "remediation": 50,
        "policy": 30,
        "exercise": 30,
        "mfa_rollout": 50,
        "monitoring": 40,
    },
    "teach": {
        "workshop": 40,
        "mentoring": 20,
        "course_material": 40,
        "presentation": 30,
        "publication": 50,
        "teach_back": 20,
    },
    "serve": {
        "nonprofit_support": 40,
        "small_business_support": 40,
        "community_event": 30,
        "student_support": 20,
        "service_hours": 10,
        "judging": 25,
    },
}

VALIDATION_MULTIPLIERS = {
    "self": 0.5,
    "peer": 1.0,
    "instructor": 1.2,
    "industry": 1.5,
    "adoption": 2.0,
}
ORIGINALITY_MULTIPLIERS = {
    "copied": 0.25,
    "modified": 0.75,
    "original": 1.0,
    "innovative": 1.5,
}
LONGEVITY_TIERS = (
    (30, 0.5),
    (91, 1.0),
    (183, 1.2),
    (365, 1.5),
    (730, 1.75),
    (None, 2.0),
)
QUALITY_FLOOR = 3.0
REPEAT_WINDOW_DAYS = 365
DECAY_START_YEARS = 2.0
DECAY_RATE = 0.8
DECAY_FLOOR = 0.25
STEWARDSHIP_BASE = 100
STEWARDSHIP_MAX = 150

LONG_RUNNING_DIMENSIONS = frozenset({"build", "protect"})
TEACHING_KINDS = frozenset(
    {"workshop", "course_material", "presentation", "publication", "teach_back"}
)
OPEN_SOURCE_KINDS = frozenset({"tool", "integration", "detection_rule"})
CLASS_BY_DIMENSION = {
    "build": "Builder",
    "protect": "Guardian",
    "teach": "Teacher",
    "serve": "Community Champion",
}


class ImpactError(Exception):
    """A validation or access failure with a stable API code."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def reach_multiplier(reach_count: int | None) -> float:
    """Sublinear reach: 1 person = 1.0, 1,000 = 4.0, 10,000+ = 5.0."""
    reach = max(int(reach_count or 0), 1)
    return round(_clamp(math.log10(reach) + 1, 1.0, 5.0), 4)


def quality_multiplier(rating: float | None) -> float | None:
    """A rating below 3/5 excludes the contribution. None means unreviewed."""
    if rating is None:
        return None
    rating = float(rating)
    if rating < QUALITY_FLOOR:
        return None
    return round(_clamp(rating / 4.0, 0.5, 1.5), 4)


def longevity_multiplier(
    dimension: str,
    last_used_at: datetime | None,
    occurred_at: datetime | None = None,
    now: datetime | None = None,
) -> float:
    """How long the contribution has kept mattering.

    One-off teaching and service events do not decay with age; their value is
    the people reached at the time. Build and protect artifacts are measured
    from their last verified use.
    """
    if dimension not in LONG_RUNNING_DIMENSIONS:
        return 1.0
    reference = last_used_at or occurred_at
    if reference is None:
        return 0.5
    current = now or _now()
    days = max((current - reference).days, 0)
    for cutoff, multiplier in LONGEVITY_TIERS:
        if cutoff is None or days < cutoff:
            return multiplier
    return 0.5


def validation_multiplier(level: str) -> float:
    return VALIDATION_MULTIPLIERS.get(str(level or "self"), 0.5)


def originality_multiplier(originality: str) -> float:
    return ORIGINALITY_MULTIPLIERS.get(str(originality or "original"), 1.0)


def repeat_weight(ordinal: int) -> float:
    """The nth contribution of one kind in a year. 1.0, 0.67, 0.5, ..."""
    ordinal = max(int(ordinal or 1), 1)
    return round(max(0.1, 1.0 / (1.0 + 0.5 * (ordinal - 1))), 4)


def decay_multiplier(
    dimension: str,
    last_used_at: datetime | None,
    now: datetime | None = None,
) -> float:
    """Unused build and protect work loses weight after two years."""
    if dimension not in LONG_RUNNING_DIMENSIONS or last_used_at is None:
        return 1.0
    current = now or _now()
    years = (current - last_used_at).days / 365.0
    if years <= DECAY_START_YEARS:
        return 1.0
    full_years = int(years - DECAY_START_YEARS)
    return round(max(DECAY_FLOOR, DECAY_RATE**full_years), 4)


def score_contribution(
    contribution: ImpactContribution,
    ordinal: int = 1,
    now: datetime | None = None,
) -> dict:
    """Score one contribution. Only verified work is credited."""
    dimension = str(contribution.dimension)
    quality = quality_multiplier(contribution.quality_rating)
    provisional = False
    if quality is None and contribution.quality_rating is None:
        if str(contribution.status) != "verified":
            # Before review, show a neutral estimate rather than a zero.
            quality = 1.0
            provisional = True
    if quality is None:
        return {
            "points": 0,
            "preview_points": 0,
            "counted": False,
            "excluded": "quality_threshold",
            "provisional": False,
            "factors": {},
        }
    factors = {
        "base": int(contribution.base_points or 0),
        "reach": reach_multiplier(contribution.reach_count),
        "quality": quality,
        "longevity": longevity_multiplier(
            dimension,
            contribution.last_used_at,
            contribution.occurred_at,
            now,
        ),
        "validation": validation_multiplier(contribution.validation_level),
        "originality": originality_multiplier(contribution.originality),
        "repeat": repeat_weight(ordinal),
        "decay": decay_multiplier(dimension, contribution.last_used_at, now),
    }
    raw = 1.0
    for value in factors.values():
        raw *= value
    preview = int(round(raw))
    verified = str(contribution.status) == "verified"
    return {
        "points": preview if verified else 0,
        "preview_points": preview,
        "counted": verified,
        "excluded": None if verified else "not_verified",
        "provisional": provisional,
        "factors": factors,
    }


def stewardship_points(events: list[StewardshipEvent]) -> int:
    total = STEWARDSHIP_BASE + sum(int(event.points_delta or 0) for event in events)
    return max(0, min(STEWARDSHIP_MAX, total))


def stewardship_band(points: int) -> str:
    if points >= 90:
        return "Trusted"
    if points >= 70:
        return "Established"
    if points >= 40:
        return "Watch"
    return "Restricted"


def meaning_index(
    contributions: list[ImpactContribution],
    now: datetime | None = None,
) -> dict:
    """A human count beside the weighted score.

    Derived only from verified contributions, so it cannot be inflated by
    self-reported activity.
    """
    verified = [row for row in contributions if str(row.status) == "verified"]
    organizations = sum(1 for row in verified if row.dimension == "protect")
    communities = sum(1 for row in verified if row.dimension == "serve")
    mentored = sum(
        int(row.reach_count or 0)
        for row in verified
        if row.dimension == "teach" and row.kind == "mentoring"
    )
    taught = sum(
        int(row.reach_count or 0)
        for row in verified
        if row.dimension == "teach" and row.kind in TEACHING_KINDS
    )
    open_source_users = sum(
        int(row.reach_count or 0)
        for row in verified
        if row.dimension == "build" and row.kind in OPEN_SOURCE_KINDS
    )
    current = now or _now()
    dates = [row.occurred_at for row in verified if row.occurred_at is not None]
    years = 0
    if dates:
        span = (current - min(dates)).days / 365.0
        years = int(span)
    total = (
        organizations * 5
        + mentored * 2
        + taught
        + open_source_users * 0.1
        + communities * 10
        + years * 25
    )
    return {
        "organizations_protected": organizations,
        "learners_mentored": mentored,
        "people_taught": taught,
        "open_source_users": open_source_users,
        "communities_supported": communities,
        "years_contributing": years,
        "total": int(round(total)),
    }


def legacy_class(
    totals: dict[str, int],
    band: str,
    has_contributions: bool,
    innovative_build: int = 0,
) -> str:
    if not has_contributions:
        return "Unclassified"
    build_points = int(totals.get("build", 0))
    if build_points and innovative_build / build_points > 0.5:
        return "Pathfinder"
    highest_dimension = max(totals, key=lambda key: totals[key]) if totals else None
    highest = totals.get(highest_dimension, 0) if highest_dimension else 0
    total = sum(totals.values()) or 1
    if highest / total > 0.5:
        return CLASS_BY_DIMENSION.get(highest_dimension or "", "Unclassified")
    if band in {"Trusted", "Established"}:
        return "Steward"
    return "Contributor"


def _verify_ordinals(
    contributions: list[ImpactContribution],
) -> dict[int, int]:
    """Ordinal of each verified contribution within its kind and year."""
    ordinals: dict[int, int] = {}
    counters: dict[tuple[int, str, str], list[datetime]] = {}
    ordered = sorted(
        contributions,
        key=lambda row: (row.occurred_at or _now(), row.id or 0),
    )
    for row in ordered:
        if str(row.status) != "verified":
            continue
        key = (row.user_id, str(row.dimension), str(row.kind))
        occurred = row.occurred_at or _now()
        history = counters.setdefault(key, [])
        history = [
            moment
            for moment in history
            if (occurred - moment).days <= REPEAT_WINDOW_DAYS
        ]
        history.append(occurred)
        counters[key] = history
        ordinals[row.id] = len(history)
    return ordinals


def contribution_row(row: ImpactContribution, score: dict) -> dict:
    return {
        "id": row.id,
        "dimension": row.dimension,
        "kind": row.kind,
        "title": row.title,
        "summary": row.summary,
        "status": row.status,
        "base_points": int(row.base_points or 0),
        "reach_count": int(row.reach_count or 0),
        "quality_rating": row.quality_rating,
        "validation_level": row.validation_level,
        "originality": row.originality,
        "occurred_at": row.occurred_at.isoformat() + "Z" if row.occurred_at else None,
        "last_used_at": (
            row.last_used_at.isoformat() + "Z" if row.last_used_at else None
        ),
        "verified_at": (
            row.verified_at.isoformat() + "Z" if row.verified_at else None
        ),
        "points": score["points"],
        "preview_points": score["preview_points"],
        "provisional": score.get("provisional", False),
        "factors": score["factors"],
        "excluded": score["excluded"],
        "review_notes": row.review_notes,
    }


def rollup(db: Session, learner: User, now: datetime | None = None) -> dict:
    """The learner's own impact story. Never another learner's ranking."""
    rows = (
        db.query(ImpactContribution)
        .filter(ImpactContribution.user_id == learner.id)
        .order_by(ImpactContribution.occurred_at.asc(), ImpactContribution.id.asc())
        .all()
    )
    ordinals = _verify_ordinals(rows)
    totals = {dimension: 0 for dimension in IMPACT_DIMENSIONS}
    scored: list[dict] = []
    pending = 0
    innovative_build = 0
    for row in rows:
        score = score_contribution(row, ordinals.get(row.id, 1), now)
        if row.status == "submitted" or row.status == "draft":
            pending += 1
        if row.status == "verified":
            totals[str(row.dimension)] = totals.get(str(row.dimension), 0) + score[
                "points"
            ]
            if row.dimension == "build" and row.originality == "innovative":
                innovative_build += score["points"]
        scored.append(contribution_row(row, score))

    events = (
        db.query(StewardshipEvent)
        .filter(StewardshipEvent.user_id == learner.id)
        .order_by(StewardshipEvent.occurred_at.desc())
        .all()
    )
    trust = stewardship_points(events)
    band = stewardship_band(trust)
    total = sum(totals.values())
    return {
        "learner_id": learner.id,
        "legacy_score": total,
        "dimensions": totals,
        "legacy_class": legacy_class(
            totals, band, total > 0, innovative_build
        ),
        "meaning_index": meaning_index(rows, now),
        "stewardship": {
            "points": trust,
            "band": band,
            "events": [
                {
                    "id": event.id,
                    "points_delta": event.points_delta,
                    "category": event.category,
                    "reason": event.reason,
                    "occurred_at": (
                        event.occurred_at.isoformat() + "Z"
                        if event.occurred_at
                        else None
                    ),
                    "visibility": event.visibility,
                }
                for event in events
            ],
        },
        "pending_impact": pending,
        "contributions": sorted(
            scored,
            key=lambda item: (-item["points"], -item["preview_points"], item["id"]),
        ),
        "scoring": {
            "version": "legacy-v1",
            "quality_floor": QUALITY_FLOOR,
            "repeat_window_days": REPEAT_WINDOW_DAYS,
            "decay_start_years": DECAY_START_YEARS,
            "stewardship_base": STEWARDSHIP_BASE,
        },
    }


def _normalized_hash(
    user_id: int,
    dimension: str,
    kind: str,
    title: str,
    occurred_at: datetime | None,
) -> str:
    stamp = occurred_at.date().isoformat() if occurred_at else ""
    payload = f"{user_id}|{dimension}|{kind}|{title.strip().lower()}|{stamp}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def create_contribution(db: Session, learner: User, payload: dict) -> ImpactContribution:
    dimension = str(payload.get("dimension") or "").strip()
    if dimension not in IMPACT_DIMENSIONS:
        raise ImpactError(
            "impact_dimension_invalid",
            "Dimension must be build, protect, teach, or serve.",
        )
    kind = str(payload.get("kind") or "").strip()
    if kind not in BASE_POINTS[dimension]:
        raise ImpactError(
            "impact_kind_invalid",
            f"Kind is not valid for {dimension}.",
        )
    title = str(payload.get("title") or "").strip()
    if len(title) < 5 or len(title) > 200:
        raise ImpactError(
            "impact_title_invalid",
            "Title must be between 5 and 200 characters.",
        )
    originality = str(payload.get("originality") or "original")
    if originality not in IMPACT_ORIGINALITIES:
        raise ImpactError(
            "impact_originality_invalid",
            "Originality must be copied, modified, original, or innovative.",
        )
    occurred_at = payload.get("occurred_at")
    if isinstance(occurred_at, datetime):
        occurred_at = occurred_at.replace(tzinfo=None)
    content_hash = _normalized_hash(
        learner.id, dimension, kind, title, occurred_at
    )
    existing = (
        db.query(ImpactContribution)
        .filter(
            ImpactContribution.user_id == learner.id,
            ImpactContribution.content_hash == content_hash,
        )
        .first()
    )
    if existing is not None:
        raise ImpactError(
            "impact_duplicate",
            "This contribution has already been submitted.",
            409,
        )
    row = ImpactContribution(
        institution_id=_tenant_of(learner),
        user_id=learner.id,
        dimension=dimension,
        kind=kind,
        title=title,
        summary=(str(payload.get("summary") or "").strip() or None),
        base_points=BASE_POINTS[dimension][kind],
        reach_count=max(0, int(payload.get("reach_count") or 0)),
        quality_rating=None,
        validation_level="self",
        originality=originality,
        status="submitted",
        occurred_at=occurred_at or _now(),
        content_hash=content_hash,
        notes=(str(payload.get("notes") or "").strip() or None),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def contribution_scope(query, db: Session, viewer: User):
    if viewer.role == "admin":
        return query
    query = query.filter(
        ImpactContribution.institution_id == _tenant_of(viewer)
    )
    if viewer.role == "student":
        return query.filter(ImpactContribution.user_id == viewer.id)
    if viewer.role not in READ_ROLES:
        return query.filter(false())
    if viewer.role in TENANT_WIDE_READ_ROLES:
        return query
    covered = _covered_learner_ids(db, viewer)
    if not covered:
        return query.filter(false())
    return query.filter(ImpactContribution.user_id.in_(covered))


def _reviewer_can_touch(db: Session, reviewer: User, learner_id: int) -> bool:
    if reviewer.role == "admin":
        return True
    if reviewer.role not in REVIEW_ROLES:
        return False
    return learner_id in _covered_learner_ids(db, reviewer)


def verify_contribution(
    db: Session,
    reviewer: User,
    contribution_id: int,
    payload: dict,
) -> ImpactContribution:
    row = db.get(ImpactContribution, contribution_id)
    if row is None:
        raise ImpactError("impact_not_found", "Contribution not found.", 404)
    if not _reviewer_can_touch(db, reviewer, row.user_id):
        raise ImpactError(
            "impact_forbidden",
            "You cannot verify this contribution.",
            403,
        )
    if row.status == "verified":
        raise ImpactError(
            "impact_already_verified",
            "This contribution is already verified.",
            409,
        )
    validation = str(payload.get("validation_level") or "instructor")
    if validation not in IMPACT_VALIDATION_LEVELS or validation == "self":
        raise ImpactError(
            "impact_validation_invalid",
            "Validation must be peer, instructor, industry, or adoption.",
        )
    if validation in {"industry", "adoption"} and reviewer.role != "admin":
        raise ImpactError(
            "impact_validation_forbidden",
            "Only an administrator can record external validation.",
            403,
        )
    rating = payload.get("quality_rating")
    if rating is None:
        raise ImpactError(
            "impact_rating_required",
            "A quality rating is required to verify a contribution.",
        )
    rating = float(rating)
    if rating < QUALITY_FLOOR or rating > 5:
        raise ImpactError(
            "impact_rating_invalid",
            "Quality rating must be at least 3.0 and at most 5.0.",
        )
    reach = payload.get("reach_count")
    if reach is not None:
        reach = int(reach)
        if reach < 0:
            raise ImpactError(
                "impact_reach_invalid",
                "Reach cannot be negative.",
            )
        row.reach_count = reach
    originality = payload.get("originality")
    if originality is not None:
        if originality not in IMPACT_ORIGINALITIES:
            raise ImpactError(
                "impact_originality_invalid",
                "Originality must be copied, modified, original, or innovative.",
            )
        row.originality = originality
    row.quality_rating = rating if rating is not None else row.quality_rating
    row.validation_level = validation
    row.status = "verified"
    row.verified_at = _now()
    row.verified_by_id = reviewer.id
    row.last_used_at = row.last_used_at or _now()
    row.review_notes = (
        str(payload.get("review_notes") or "").strip() or None
    )
    db.commit()
    db.refresh(row)
    return row


def reject_contribution(
    db: Session,
    reviewer: User,
    contribution_id: int,
    notes: str,
) -> ImpactContribution:
    row = db.get(ImpactContribution, contribution_id)
    if row is None:
        raise ImpactError("impact_not_found", "Contribution not found.", 404)
    if not _reviewer_can_touch(db, reviewer, row.user_id):
        raise ImpactError(
            "impact_forbidden",
            "You cannot review this contribution.",
            403,
        )
    if row.status == "verified":
        raise ImpactError(
            "impact_already_verified",
            "This contribution is already verified.",
            409,
        )
    notes = str(notes or "").strip()
    if len(notes) < 6:
        raise ImpactError(
            "impact_notes_required",
            "Explain the rejection in at least 6 characters.",
        )
    row.status = "rejected"
    row.review_notes = notes
    row.verified_by_id = reviewer.id
    row.verified_at = _now()
    db.commit()
    db.refresh(row)
    return row


def record_stewardship(
    db: Session,
    admin: User,
    learner: User,
    payload: dict,
) -> StewardshipEvent:
    if admin.role != "admin":
        raise ImpactError(
            "impact_forbidden",
            "Only an administrator can record a stewardship event.",
            403,
        )
    delta = int(payload.get("points_delta") or 0)
    category = str(payload.get("category") or "positive")
    reason = str(payload.get("reason") or "").strip()
    evidence_ref = str(payload.get("evidence_ref") or "").strip()
    if len(reason) < 10:
        raise ImpactError(
            "impact_reason_invalid",
            "A stewardship reason of at least 10 characters is required.",
        )
    if category not in {"positive", "negative", "restoration"}:
        raise ImpactError(
            "impact_category_invalid",
            "Category must be positive, negative, or restoration.",
        )
    if delta == 0:
        raise ImpactError(
            "impact_delta_invalid",
            "Points change cannot be zero.",
        )
    if category == "negative":
        if delta > 0:
            raise ImpactError(
                "impact_delta_invalid",
                "A negative event must reduce the trust score.",
            )
        if not evidence_ref:
            raise ImpactError(
                "impact_evidence_required",
                "A negative event requires an evidence reference.",
            )
    if category in {"positive", "restoration"} and delta < 0:
        raise ImpactError(
            "impact_delta_invalid",
            "A positive or restoration event cannot reduce the score.",
        )
    row = StewardshipEvent(
        institution_id=_tenant_of(learner),
        user_id=learner.id,
        points_delta=delta,
        category=category,
        reason=reason,
        occurred_at=_now(),
        recorded_by_id=admin.id,
        evidence_ref=evidence_ref or None,
        visibility=str(payload.get("visibility") or "private"),
    )
    if row.visibility not in {"private", "instructor"}:
        raise ImpactError(
            "impact_visibility_invalid",
            "Visibility must be private or instructor.",
        )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def pending_queue(db: Session, reviewer: User) -> list[dict]:
    query = (
        db.query(ImpactContribution)
        .filter(ImpactContribution.status == "submitted")
        .order_by(ImpactContribution.occurred_at.asc())
    )
    rows = contribution_scope(query, db, reviewer).all()
    if reviewer.role not in REVIEW_ROLES:
        return []
    now = _now()
    return [
        {
            "id": row.id,
            "learner_id": row.user_id,
            "dimension": row.dimension,
            "kind": row.kind,
            "title": row.title,
            "summary": row.summary,
            "base_points": row.base_points,
            "reach_count": row.reach_count,
            "originality": row.originality,
            "occurred_at": (
                row.occurred_at.isoformat() + "Z" if row.occurred_at else None
            ),
            "preview_points": score_contribution(row, 1, now)["preview_points"],
        }
        for row in rows
    ]


def cohort_summary(db: Session, viewer: User) -> dict:
    """Aggregate impact for a reviewer. No learner rows, no ranking."""
    query = contribution_scope(
        db.query(ImpactContribution),
        db,
        viewer,
    ).filter(ImpactContribution.status == "verified")
    rows = query.all()
    learner_ids = {row.user_id for row in rows}
    totals = {dimension: 0 for dimension in IMPACT_DIMENSIONS}
    ordinals = _verify_ordinals(rows)
    for row in rows:
        totals[str(row.dimension)] = totals.get(str(row.dimension), 0) + (
            score_contribution(row, ordinals.get(row.id, 1))["points"]
        )
    suppressed = viewer.role != "admin" and len(learner_ids) < 5
    return {
        "learners": 0 if suppressed else len(learner_ids),
        "contributions": 0 if suppressed else len(rows),
        "dimensions": (
            {dimension: 0 for dimension in IMPACT_DIMENSIONS}
            if suppressed
            else totals
        ),
        "suppressed": suppressed,
        "suppression_note": (
            "Aggregates are hidden below five learners." if suppressed else None
        ),
    }
