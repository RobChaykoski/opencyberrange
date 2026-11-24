"""Release 6 evidence ledger service.

The service owns three rules:

* an evidence record is created only from a known rubric and known taxonomy
  competencies, with an optional artifact hash;
* creation is idempotent for the same learner, source, rubric, competencies,
  and artifact;
* content is append-only. Review outcomes add rows and move the workflow
  fields; they never edit the evidence itself.

Access is scoped in the service, not only in the router: a learner sees their
own records, a reviewer sees learners in courses they own or staff, and a
platform administrator sees the system. PostgreSQL RLS is the backstop.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone

from sqlalchemy import false, text
from sqlalchemy.orm import Session, selectinload

from app.models import Course, CourseEnrollment, CourseStaff, User
from app.models.evidence import (
    EVIDENCE_CONFIDENCES,
    EVIDENCE_DECISIONS,
    EVIDENCE_SOURCE_TYPES,
    EVIDENCE_VISIBILITIES,
    EvidenceAppeal,
    EvidenceCompetency,
    EvidenceRecord,
    EvidenceReview,
)
from app.services.competency_contract import taxonomy_ids
from app.services.rubrics import get_rubric

READ_ROLES = frozenset(
    {
        "admin",
        "institution_admin",
        "instructor",
        "mentor",
        "teaching_assistant",
        "auditor",
        "privacy_officer",
    }
)
REVIEW_ROLES = frozenset(
    {
        "admin",
        "institution_admin",
        "instructor",
        "mentor",
        "teaching_assistant",
    }
)
TENANT_WIDE_READ_ROLES = frozenset(
    {"admin", "institution_admin", "auditor", "privacy_officer"}
)
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


class EvidenceError(Exception):
    """A validation or access failure with a stable API code."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _naive_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _as_naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=None) if value.tzinfo is not None else value


def _tenant_of(user: User) -> str:
    return getattr(user, "institution_id", None) or "default"


def _covered_course_ids(db: Session, viewer: User) -> set[int]:
    owned = {
        row[0]
        for row in db.query(Course.id)
        .filter(Course.instructor_id == viewer.id)
        .all()
    }
    staff = {
        row[0]
        for row in db.query(CourseStaff.course_id)
        .filter(CourseStaff.user_id == viewer.id)
        .all()
    }
    return owned | staff


def _covered_learner_ids(db: Session, viewer: User) -> set[int]:
    course_ids = _covered_course_ids(db, viewer)
    if not course_ids:
        return set()
    return {
        row[0]
        for row in db.query(CourseEnrollment.user_id)
        .filter(CourseEnrollment.course_id.in_(course_ids))
        .distinct()
        .all()
    }


def _can_access(db: Session, viewer: User, record: EvidenceRecord) -> bool:
    if viewer.role == "admin":
        return True
    if record.learner_id == viewer.id:
        return True
    if viewer.role not in READ_ROLES:
        return False
    if record.institution_id != _tenant_of(viewer):
        return False
    if record.visibility == "learner":
        return False
    if viewer.role in TENANT_WIDE_READ_ROLES:
        return True
    return record.learner_id in _covered_learner_ids(db, viewer)


def apply_scope(query, db: Session, viewer: User):
    """Apply the caller's learner, course, or tenant scope to a query."""
    return _apply_scope(query, db, viewer)


def _apply_scope(query, db: Session, viewer: User):
    if viewer.role == "admin":
        return query
    query = query.filter(EvidenceRecord.institution_id == _tenant_of(viewer))
    if viewer.role == "student":
        return query.filter(EvidenceRecord.learner_id == viewer.id)
    if viewer.role not in READ_ROLES:
        return query.filter(false())
    query = query.filter(EvidenceRecord.visibility != "learner")
    if viewer.role in TENANT_WIDE_READ_ROLES:
        return query
    covered = _covered_learner_ids(db, viewer)
    if not covered:
        return query.filter(false())
    return query.filter(EvidenceRecord.learner_id.in_(covered))


def _validate_links(links: list[dict], rubric: dict) -> list[dict]:
    known_competencies = taxonomy_ids()
    known_criteria = {
        str(criterion.get("id"))
        for criterion in rubric.get("criteria") or []
        if isinstance(criterion, dict) and criterion.get("id")
    }
    normalized: list[dict] = []
    seen: set[str] = set()
    for raw in links:
        if not isinstance(raw, dict):
            raise EvidenceError("evidence_competency_invalid", "Each competency link must be an object.")
        competency_id = str(raw.get("competency_id") or "").strip()
        if not competency_id:
            raise EvidenceError("evidence_competency_invalid", "A competency id is required.")
        if competency_id in seen:
            raise EvidenceError(
                "evidence_competency_invalid",
                f"Competency {competency_id} is listed more than once.",
            )
        if competency_id not in known_competencies:
            raise EvidenceError(
                "evidence_competency_unknown",
                f"Competency {competency_id} is not in the taxonomy.",
            )
        criteria = [
            str(item).strip()
            for item in (raw.get("criteria") or [])
            if str(item).strip()
        ]
        if not criteria:
            raise EvidenceError(
                "evidence_competency_invalid",
                f"Competency {competency_id} must name at least one rubric criterion.",
            )
        unknown_criteria = set(criteria) - known_criteria
        if unknown_criteria:
            raise EvidenceError(
                "evidence_competency_invalid",
                f"Competency {competency_id} cites unknown criteria: "
                f"{', '.join(sorted(unknown_criteria))}.",
            )
        try:
            weight = float(raw.get("weight", 1.0))
        except (TypeError, ValueError):
            raise EvidenceError(
                "evidence_competency_invalid",
                f"Competency {competency_id} has a non-numeric weight.",
            ) from None
        if weight <= 0 or weight > 10:
            raise EvidenceError(
                "evidence_competency_invalid",
                f"Competency {competency_id} weight must be between 0 and 10.",
            )
        seen.add(competency_id)
        normalized.append(
            {"competency_id": competency_id, "criteria": criteria, "weight": weight}
        )
    if not normalized:
        raise EvidenceError(
            "evidence_competency_invalid",
            "At least one competency link is required.",
        )
    return normalized


def _validate_artifact(
    artifact_uri: str | None,
    artifact_mime: str | None,
    artifact_size: int | None,
    artifact_sha256: str | None,
) -> tuple[str | None, str | None, int | None, str | None]:
    if not any(
        value is not None
        for value in (artifact_uri, artifact_mime, artifact_size, artifact_sha256)
    ):
        return None, None, None, None
    if not artifact_sha256 or not SHA256_PATTERN.match(artifact_sha256):
        raise EvidenceError(
            "evidence_artifact_invalid",
            "An artifact requires a 64-character SHA-256 hash.",
        )
    if artifact_size is None or int(artifact_size) < 0:
        raise EvidenceError(
            "evidence_artifact_invalid",
            "An artifact requires a non-negative size.",
        )
    return (
        (artifact_uri or "").strip() or None,
        (artifact_mime or "").strip() or None,
        int(artifact_size),
        artifact_sha256.lower(),
    )


def _fingerprint(
    *,
    learner_id: int,
    source_type: str,
    source_id: str,
    rubric_id: str,
    rubric_version: str,
    links: list[dict],
    artifact_sha256: str | None,
    content_text: str | None = None,
) -> str:
    payload = {
        "learner_id": learner_id,
        "source_type": source_type,
        "source_id": source_id,
        "rubric_id": rubric_id,
        "rubric_version": rubric_version,
        "competencies": sorted(link["competency_id"] for link in links),
        "artifact_sha256": artifact_sha256 or "",
        "content_sha256": (
            hashlib.sha256(content_text.encode("utf-8")).hexdigest()
            if content_text
            else ""
        ),
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def create_record(
    db: Session,
    *,
    learner_id: int,
    source_type: str,
    source_id: str,
    competencies: list[dict],
    rubric_id: str,
    rubric_version: str,
    confidence: str = "medium",
    confidence_reason: str | None = None,
    collected_at: datetime | None = None,
    provenance: str = "api",
    provenance_version: str | None = None,
    visibility: str = "both",
    formula_version: str = "competency-v1",
    artifact_uri: str | None = None,
    artifact_mime: str | None = None,
    artifact_size: int | None = None,
    artifact_sha256: str | None = None,
    content_text: str | None = None,
) -> tuple[EvidenceRecord, bool]:
    learner = db.query(User).filter(User.id == learner_id).first()
    if learner is None:
        raise EvidenceError("evidence_learner_not_found", "Learner not found.", 404)

    source_type = str(source_type or "").strip()
    if source_type not in EVIDENCE_SOURCE_TYPES:
        raise EvidenceError(
            "evidence_source_type_invalid",
            f"Unknown evidence source type: {source_type or '(empty)'}.",
        )
    source_id = str(source_id or "").strip()
    if not source_id:
        raise EvidenceError("evidence_source_invalid", "A source id is required.")

    rubric = get_rubric(rubric_id, rubric_version)
    if rubric is None:
        raise EvidenceError(
            "evidence_rubric_unknown",
            f"Unknown rubric {rubric_id} version {rubric_version}.",
        )
    allowed_types = {str(item) for item in rubric.get("evidence_types") or []}
    if allowed_types and source_type not in allowed_types:
        raise EvidenceError(
            "evidence_source_not_allowed",
            f"Rubric {rubric_id} does not accept {source_type} evidence.",
        )

    confidence = str(confidence or "medium").strip()
    if confidence not in EVIDENCE_CONFIDENCES:
        raise EvidenceError(
            "evidence_confidence_invalid",
            f"Confidence must be one of {', '.join(EVIDENCE_CONFIDENCES)}.",
        )
    visibility = str(visibility or "both").strip()
    if visibility not in EVIDENCE_VISIBILITIES:
        raise EvidenceError(
            "evidence_visibility_invalid",
            f"Visibility must be one of {', '.join(EVIDENCE_VISIBILITIES)}.",
        )

    links = _validate_links(competencies, rubric)
    (
        artifact_uri,
        artifact_mime,
        artifact_size,
        artifact_sha256,
    ) = _validate_artifact(
        artifact_uri, artifact_mime, artifact_size, artifact_sha256
    )

    content_text = (content_text or "").strip()[:20000] or None

    rubric_version = str(rubric.get("version"))
    fingerprint = _fingerprint(
        learner_id=learner.id,
        source_type=source_type,
        source_id=source_id,
        rubric_id=str(rubric.get("rubric")),
        rubric_version=rubric_version,
        links=links,
        artifact_sha256=artifact_sha256,
        content_text=content_text,
    )
    existing = (
        db.query(EvidenceRecord)
        .filter(EvidenceRecord.source_fingerprint == fingerprint)
        .first()
    )
    if existing is not None:
        return existing, False

    record = EvidenceRecord(
        institution_id=_tenant_of(learner),
        learner_id=learner.id,
        source_type=source_type,
        source_id=source_id,
        rubric_id=str(rubric.get("rubric")),
        rubric_version=rubric_version,
        confidence=confidence,
        confidence_reason=(confidence_reason or "").strip()[:500] or None,
        collected_at=_as_naive(collected_at) or _naive_utc_now(),
        provenance=(provenance or "api").strip()[:255] or "api",
        provenance_version=(provenance_version or "").strip()[:32] or None,
        visibility=visibility,
        status="collected",
        formula_version=(formula_version or "competency-v1").strip()[:32],
        source_fingerprint=fingerprint,
        artifact_uri=artifact_uri,
        artifact_mime=artifact_mime,
        artifact_size=artifact_size,
        artifact_sha256=artifact_sha256,
        content_text=content_text,
    )
    db.add(record)
    db.flush()
    for link in links:
        db.add(
            EvidenceCompetency(
                institution_id=record.institution_id,
                evidence_id=record.id,
                competency_id=link["competency_id"],
                criteria=json.dumps(link["criteria"], separators=(",", ":")),
                weight=link["weight"],
            )
        )
    db.commit()
    db.refresh(record)
    return record, True


def list_records(
    db: Session,
    viewer: User,
    *,
    learner_id: int | None = None,
    status: str | None = None,
    statuses: tuple[str, ...] | None = None,
    source_type: str | None = None,
    competency_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[EvidenceRecord]:
    query = db.query(EvidenceRecord).options(
        selectinload(EvidenceRecord.competencies),
        selectinload(EvidenceRecord.reviews),
        selectinload(EvidenceRecord.appeals),
        selectinload(EvidenceRecord.learner),
    )
    query = _apply_scope(query, db, viewer)
    if learner_id is not None:
        query = query.filter(EvidenceRecord.learner_id == int(learner_id))
    if statuses:
        query = query.filter(EvidenceRecord.status.in_(statuses))
    elif status:
        query = query.filter(EvidenceRecord.status == status)
    if source_type:
        query = query.filter(EvidenceRecord.source_type == source_type)
    if competency_id:
        query = query.join(
            EvidenceCompetency,
            EvidenceCompetency.evidence_id == EvidenceRecord.id,
        ).filter(EvidenceCompetency.competency_id == competency_id)
    limit = max(1, min(int(limit), 200))
    offset = max(0, int(offset))
    return (
        query.order_by(
            EvidenceRecord.collected_at.desc(),
            EvidenceRecord.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_record(db: Session, viewer: User, record_id: int) -> EvidenceRecord | None:
    record = (
        db.query(EvidenceRecord)
        .options(
            selectinload(EvidenceRecord.competencies),
            selectinload(EvidenceRecord.reviews),
            selectinload(EvidenceRecord.appeals),
            selectinload(EvidenceRecord.learner),
        )
        .filter(EvidenceRecord.id == int(record_id))
        .first()
    )
    if record is None or not _can_access(db, viewer, record):
        return None
    return record


def review_record(
    db: Session,
    record: EvidenceRecord,
    reviewer: User,
    *,
    decision: str,
    criterion_scores: dict,
    notes: str | None = None,
    next_step: str | None = None,
) -> EvidenceReview:
    if reviewer.role not in REVIEW_ROLES:
        raise EvidenceError(
            "evidence_forbidden",
            "This role cannot review evidence.",
            403,
        )
    if record.learner_id == reviewer.id:
        raise EvidenceError(
            "evidence_forbidden",
            "A learner cannot review their own evidence.",
            403,
        )
    if not _can_access(db, reviewer, record):
        raise EvidenceError(
            "evidence_forbidden",
            "You do not have access to this evidence record.",
            403,
        )
    if record.status not in ("collected", "in_review"):
        raise EvidenceError(
            "evidence_review_conflict",
            "This evidence record already has a final decision.",
            409,
        )

    decision = str(decision or "").strip()
    if decision not in EVIDENCE_DECISIONS:
        raise EvidenceError(
            "evidence_review_invalid",
            f"Decision must be one of {', '.join(EVIDENCE_DECISIONS)}.",
        )

    rubric = get_rubric(record.rubric_id, record.rubric_version)
    if rubric is None:
        raise EvidenceError(
            "evidence_rubric_unknown",
            f"The recorded rubric {record.rubric_id} version "
            f"{record.rubric_version} is not available.",
        )
    weights = {
        str(criterion.get("id")): float(criterion.get("weight") or 0)
        for criterion in rubric.get("criteria") or []
        if isinstance(criterion, dict) and criterion.get("id")
    }
    scores: dict[str, int] = {}
    for criterion_id, raw_score in (criterion_scores or {}).items():
        criterion_id = str(criterion_id)
        if criterion_id not in weights:
            raise EvidenceError(
                "evidence_review_invalid",
                f"Unknown rubric criterion: {criterion_id}.",
            )
        try:
            score = int(raw_score)
        except (TypeError, ValueError):
            raise EvidenceError(
                "evidence_review_invalid",
                f"Criterion {criterion_id} must be scored 0, 1, 2, or 3.",
            ) from None
        if score not in (0, 1, 2, 3):
            raise EvidenceError(
                "evidence_review_invalid",
                f"Criterion {criterion_id} must be scored 0, 1, 2, or 3.",
            )
        scores[criterion_id] = score

    notes = (notes or "").strip()[:1000] or None
    next_step = (next_step or "").strip()[:500] or None
    if decision == "accepted":
        missing = set(weights) - set(scores)
        if missing:
            raise EvidenceError(
                "evidence_review_invalid",
                "An accepted decision must score every rubric criterion: "
                f"{', '.join(sorted(missing))}.",
            )
    else:
        if not notes:
            raise EvidenceError(
                "evidence_review_invalid",
                "A rejection or more-evidence decision requires notes.",
            )
        if decision == "rejected" and not next_step:
            raise EvidenceError(
                "evidence_review_invalid",
                "A rejection requires a next step for the learner.",
            )

    weighted_score = (
        round(sum(weights[key] * (value / 3) for key, value in scores.items()), 4)
        if scores
        else None
    )
    review = EvidenceReview(
        institution_id=record.institution_id,
        evidence_id=record.id,
        reviewer_id=reviewer.id,
        rubric_id=record.rubric_id,
        rubric_version=record.rubric_version,
        decision=decision,
        criterion_scores=json.dumps(scores, sort_keys=True, separators=(",", ":")),
        weighted_score=weighted_score,
        notes=notes,
        next_step=next_step,
        reviewed_at=_naive_utc_now(),
    )
    db.add(review)

    record.status = "in_review" if decision == "more_evidence" else decision
    record.reviewer_id = reviewer.id
    record.review_notes = notes
    db.commit()
    db.refresh(review)
    db.refresh(record)
    return review


def appeal_payload(appeal: EvidenceAppeal) -> dict:
    learner = appeal.learner
    evidence = appeal.evidence
    return {
        "id": appeal.id,
        "evidence_id": appeal.evidence_id,
        "learner_id": appeal.learner_id,
        "learner": (
            {
                "id": learner.id,
                "username": learner.username,
                "display_name": learner.display_name,
            }
            if learner is not None
            else None
        ),
        "reason": appeal.reason,
        "status": appeal.status,
        "reviewer_id": appeal.reviewer_id,
        "decision_notes": appeal.decision_notes,
        "created_at": _iso(appeal.created_at),
        "reviewed_at": _iso(appeal.reviewed_at),
        "evidence": (
            {
                "source_type": evidence.source_type,
                "source_id": evidence.source_id,
                "status": evidence.status,
                "rubric_id": evidence.rubric_id,
                "rubric_version": evidence.rubric_version,
            }
            if evidence is not None
            else None
        ),
    }


def create_appeal(
    db: Session,
    record: EvidenceRecord,
    learner: User,
    *,
    reason: str,
) -> EvidenceAppeal:
    if record.learner_id != learner.id:
        raise EvidenceError(
            "evidence_appeal_forbidden",
            "You can only appeal your own evidence.",
            403,
        )
    if record.status != "rejected":
        raise EvidenceError(
            "evidence_appeal_invalid",
            "Only a rejected evidence record can be appealed.",
        )
    reason = (reason or "").strip()[:2000]
    if len(reason) < 10:
        raise EvidenceError(
            "evidence_appeal_invalid",
            "An appeal needs a reason of at least 10 characters.",
        )
    pending = (
        db.query(EvidenceAppeal)
        .filter(
            EvidenceAppeal.evidence_id == record.id,
            EvidenceAppeal.status == "pending",
        )
        .first()
    )
    if pending is not None:
        raise EvidenceError(
            "evidence_appeal_conflict",
            "An appeal is already pending for this evidence record.",
            409,
        )
    appeal = EvidenceAppeal(
        institution_id=record.institution_id,
        evidence_id=record.id,
        learner_id=learner.id,
        reason=reason,
        status="pending",
    )
    db.add(appeal)
    db.commit()
    db.refresh(appeal)
    return appeal


def list_appeals(
    db: Session,
    viewer: User,
    *,
    status: str | None = None,
) -> list[EvidenceAppeal]:
    query = (
        db.query(EvidenceAppeal)
        .options(
            selectinload(EvidenceAppeal.learner),
            selectinload(EvidenceAppeal.evidence),
        )
        .join(EvidenceRecord, EvidenceAppeal.evidence_id == EvidenceRecord.id)
    )
    query = apply_scope(query, db, viewer)
    if status:
        query = query.filter(EvidenceAppeal.status == status)
    return query.order_by(EvidenceAppeal.created_at.desc(), EvidenceAppeal.id.desc()).limit(200).all()


def get_appeal(db: Session, viewer: User, appeal_id: int) -> EvidenceAppeal | None:
    query = (
        db.query(EvidenceAppeal)
        .options(
            selectinload(EvidenceAppeal.learner),
            selectinload(EvidenceAppeal.evidence),
        )
        .join(EvidenceRecord, EvidenceAppeal.evidence_id == EvidenceRecord.id)
    )
    query = apply_scope(query, db, viewer)
    return query.filter(EvidenceAppeal.id == int(appeal_id)).first()


def review_appeal(
    db: Session,
    appeal: EvidenceAppeal,
    reviewer: User,
    *,
    decision: str,
    notes: str,
) -> EvidenceAppeal:
    if reviewer.role not in REVIEW_ROLES:
        raise EvidenceError(
            "evidence_forbidden",
            "This role cannot review an appeal.",
            403,
        )
    if appeal.evidence is None or not _can_access(db, reviewer, appeal.evidence):
        raise EvidenceError(
            "evidence_forbidden",
            "You do not have access to this appeal.",
            403,
        )
    if appeal.status != "pending":
        raise EvidenceError(
            "evidence_appeal_conflict",
            "This appeal has already been decided.",
            409,
        )
    decision = str(decision or "").strip()
    if decision not in ("accepted", "rejected"):
        raise EvidenceError(
            "evidence_appeal_invalid",
            "Appeal decision must be accepted or rejected.",
        )
    notes = (notes or "").strip()[:2000]
    if not notes:
        raise EvidenceError(
            "evidence_appeal_invalid",
            "An appeal decision requires notes.",
        )
    appeal.status = decision
    appeal.reviewer_id = reviewer.id
    appeal.decision_notes = notes
    appeal.reviewed_at = _naive_utc_now()
    if decision == "accepted":
        appeal.evidence.status = "in_review"
        appeal.evidence.reviewer_id = reviewer.id
        appeal.evidence.review_notes = f"Appeal accepted: {notes}"[:1000]
    db.commit()
    db.refresh(appeal)
    return appeal


def auto_accept_record(
    db: Session,
    record: EvidenceRecord,
    *,
    note: str,
) -> EvidenceReview | None:
    """Accept a deterministically verified record without a human reviewer.

    This is the system-review path for flags and quizzes. It appends a normal
    review row so the audit trail is complete, and it uses the recorded rubric
    version rather than the current one.
    """

    if record.status == "accepted":
        return None
    rubric = get_rubric(record.rubric_id, record.rubric_version)
    if rubric is None:
        raise EvidenceError(
            "evidence_rubric_unknown",
            f"The recorded rubric {record.rubric_id} version "
            f"{record.rubric_version} is not available.",
        )
    weights = {
        str(criterion.get("id")): float(criterion.get("weight") or 0)
        for criterion in rubric.get("criteria") or []
        if isinstance(criterion, dict) and criterion.get("id")
    }
    scores = {criterion_id: 3 for criterion_id in weights}
    weighted_score = round(sum(weights.values()), 4) if weights else None
    review = EvidenceReview(
        institution_id=record.institution_id,
        evidence_id=record.id,
        reviewer_id=None,
        rubric_id=record.rubric_id,
        rubric_version=record.rubric_version,
        decision="accepted",
        criterion_scores=json.dumps(scores, sort_keys=True, separators=(",", ":")),
        weighted_score=weighted_score,
        notes=note[:1000],
        next_step=None,
        reviewed_at=_naive_utc_now(),
    )
    db.add(review)
    record.status = "accepted"
    record.review_notes = note[:1000]
    db.commit()
    db.refresh(review)
    db.refresh(record)
    return review


def competency_summary(
    db: Session,
    viewer: User,
    competency_id: str,
    *,
    learner_id: int | None = None,
    limit: int = 50,
) -> dict:
    records = list_records(
        db,
        viewer,
        learner_id=learner_id,
        competency_id=competency_id,
        limit=limit,
    )
    counts = Counter(record.status for record in records)
    return {
        "competency_id": competency_id,
        "total": len(records),
        "accepted": counts.get("accepted", 0),
        "collected": counts.get("collected", 0),
        "in_review": counts.get("in_review", 0),
        "rejected": counts.get("rejected", 0),
        "superseded": counts.get("superseded", 0),
        "validated": counts.get("accepted", 0) > 0,
        "evidence": [record_payload(record) for record in records],
    }


def _loads(value: str | None, fallback):
    if not value:
        return fallback
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return fallback


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() + "Z" if value else None


def review_payload(review: EvidenceReview | None) -> dict | None:
    if review is None:
        return None
    return {
        "id": review.id,
        "evidence_id": review.evidence_id,
        "reviewer_id": review.reviewer_id,
        "rubric_id": review.rubric_id,
        "rubric_version": review.rubric_version,
        "decision": review.decision,
        "criterion_scores": _loads(review.criterion_scores, {}),
        "weighted_score": review.weighted_score,
        "notes": review.notes,
        "next_step": review.next_step,
        "reviewed_at": _iso(review.reviewed_at),
    }


def record_payload(record: EvidenceRecord) -> dict:
    reviews = sorted(record.reviews, key=lambda row: row.id or 0)
    latest_review = reviews[-1] if reviews else None
    artifact = None
    if record.artifact_sha256:
        artifact = {
            "uri": record.artifact_uri,
            "mime": record.artifact_mime,
            "size": record.artifact_size,
            "sha256": record.artifact_sha256,
        }
    learner = record.learner
    return {
        "id": record.id,
        "learner_id": record.learner_id,
        "learner": (
            {
                "id": learner.id,
                "username": learner.username,
                "display_name": learner.display_name,
            }
            if learner is not None
            else None
        ),
        "source_type": record.source_type,
        "source_id": record.source_id,
        "rubric": {
            "id": record.rubric_id,
            "version": record.rubric_version,
        },
        "confidence": record.confidence,
        "confidence_reason": record.confidence_reason,
        "collected_at": _iso(record.collected_at),
        "provenance": record.provenance,
        "provenance_version": record.provenance_version,
        "visibility": record.visibility,
        "status": record.status,
        "reviewer_id": record.reviewer_id,
        "review_notes": record.review_notes,
        "formula_version": record.formula_version,
        "supersedes_id": record.supersedes_id,
        "artifact": artifact,
        "content_text": record.content_text,
        "competencies": [
            {
                "competency_id": link.competency_id,
                "criteria": _loads(link.criteria, []),
                "weight": link.weight,
            }
            for link in sorted(record.competencies, key=lambda row: row.id or 0)
        ],
        "latest_review": review_payload(latest_review),
        "reviews": [review_payload(review) for review in reviews],
        "appeals": [appeal_payload(appeal) for appeal in record.appeals],
        "created_at": _iso(record.created_at),
    }


def ensure_append_only(connection) -> None:
    """Install the PostgreSQL guard that keeps evidence content immutable.

    The guard allows the workflow columns (``status``, ``reviewer_id``, and
    ``review_notes``) to change when a review is recorded. Deletion remains
    possible so the account-erasure flow can remove learner data.
    """

    if connection.dialect.name != "postgresql":
        return
    connection.execute(
        text(
            """
            CREATE OR REPLACE FUNCTION ocr_evidence_record_guard()
            RETURNS trigger AS $$
            BEGIN
                IF TG_OP = 'UPDATE' THEN
                    IF NEW.institution_id IS DISTINCT FROM OLD.institution_id
                       OR NEW.learner_id IS DISTINCT FROM OLD.learner_id
                       OR NEW.source_type IS DISTINCT FROM OLD.source_type
                       OR NEW.source_id IS DISTINCT FROM OLD.source_id
                       OR NEW.rubric_id IS DISTINCT FROM OLD.rubric_id
                       OR NEW.rubric_version IS DISTINCT FROM OLD.rubric_version
                       OR NEW.confidence IS DISTINCT FROM OLD.confidence
                       OR NEW.confidence_reason IS DISTINCT FROM OLD.confidence_reason
                       OR NEW.collected_at IS DISTINCT FROM OLD.collected_at
                       OR NEW.provenance IS DISTINCT FROM OLD.provenance
                       OR NEW.provenance_version IS DISTINCT FROM OLD.provenance_version
                       OR NEW.visibility IS DISTINCT FROM OLD.visibility
                       OR NEW.formula_version IS DISTINCT FROM OLD.formula_version
                       OR NEW.supersedes_id IS DISTINCT FROM OLD.supersedes_id
                       OR NEW.source_fingerprint IS DISTINCT FROM OLD.source_fingerprint
                       OR NEW.artifact_uri IS DISTINCT FROM OLD.artifact_uri
                       OR NEW.artifact_mime IS DISTINCT FROM OLD.artifact_mime
                       OR NEW.artifact_size IS DISTINCT FROM OLD.artifact_size
                       OR NEW.artifact_sha256 IS DISTINCT FROM OLD.artifact_sha256
                       OR NEW.content_text IS DISTINCT FROM OLD.content_text
                    THEN
                        RAISE EXCEPTION
                            'evidence content is append-only; create a new record';
                    END IF;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
        )
    )
    connection.execute(
        text("DROP TRIGGER IF EXISTS ocr_evidence_record_guard ON evidence_records")
    )
    connection.execute(
        text(
            "CREATE TRIGGER ocr_evidence_record_guard "
            "BEFORE UPDATE ON evidence_records "
            "FOR EACH ROW EXECUTE FUNCTION ocr_evidence_record_guard()"
        )
    )
