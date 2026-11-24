"""Release 6 evidence ledger API.

The router is deliberately thin: the service owns the rubric, competency,
tenant, and review rules. Stable ``X-Error-Code`` headers identify validation
and access failures without changing the human-readable ``detail``.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api_errors import api_error
from app.auth import (
    get_current_active_user,
    get_current_instructor_user,
    get_current_reporting_user,
)
from app.database import get_db
from app.models import User
from app.services import evidence as evidence_service
from app.services import evidence_analytics
from app.services.evidence import EvidenceError
from app.services.rubrics import load_rubrics

router = APIRouter()
competency_router = APIRouter()


class CompetencyLinkIn(BaseModel):
    competency_id: str = Field(..., min_length=1, max_length=32)
    criteria: list[str] = Field(default_factory=list, max_length=20)
    weight: float = Field(1.0, gt=0, le=10)


class ArtifactIn(BaseModel):
    uri: str | None = Field(None, max_length=500)
    mime: str | None = Field(None, max_length=120)
    size: int | None = Field(None, ge=0)
    sha256: str | None = Field(None, pattern=r"^[0-9a-fA-F]{64}$")


class EvidenceCreate(BaseModel):
    learner_id: int
    source_type: str = Field(..., max_length=32)
    source_id: str = Field(..., min_length=1, max_length=160)
    competencies: list[CompetencyLinkIn] = Field(..., min_length=1, max_length=50)
    rubric_id: str = Field(..., min_length=1, max_length=64)
    rubric_version: str = Field(..., min_length=1, max_length=16)
    confidence: str = Field("medium", max_length=16)
    confidence_reason: str | None = Field(None, max_length=500)
    collected_at: datetime | None = None
    provenance: str = Field("api", min_length=1, max_length=255)
    provenance_version: str | None = Field(None, max_length=32)
    visibility: str = Field("both", max_length=16)
    formula_version: str = Field("competency-v1", min_length=1, max_length=32)
    artifact: ArtifactIn | None = None


class EvidenceReviewIn(BaseModel):
    decision: str = Field(..., pattern="^(accepted|rejected|more_evidence)$")
    criterion_scores: dict[str, int] = Field(default_factory=dict)
    notes: str | None = Field(None, max_length=1000)
    next_step: str | None = Field(None, max_length=500)


class EvidenceAppealIn(BaseModel):
    reason: str = Field(..., min_length=10, max_length=2000)


class EvidenceAppealDecisionIn(BaseModel):
    decision: str = Field(..., pattern="^(accepted|rejected)$")
    notes: str = Field(..., min_length=1, max_length=2000)


def _raise(exc: EvidenceError):
    raise api_error(exc.status_code, exc.code, exc.message) from exc


@router.post("", status_code=201)
async def create_evidence(
    payload: EvidenceCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Record evidence from a reviewed rubric and competency contract.

    Replaying the same learner, source, rubric, competencies, and artifact hash
    returns the existing record instead of creating a duplicate.
    """
    artifact = payload.artifact
    try:
        record, created = evidence_service.create_record(
            db,
            learner_id=payload.learner_id,
            source_type=payload.source_type,
            source_id=payload.source_id,
            competencies=[link.model_dump() for link in payload.competencies],
            rubric_id=payload.rubric_id,
            rubric_version=payload.rubric_version,
            confidence=payload.confidence,
            confidence_reason=payload.confidence_reason,
            collected_at=payload.collected_at,
            provenance=payload.provenance,
            provenance_version=payload.provenance_version,
            visibility=payload.visibility,
            formula_version=payload.formula_version,
            artifact_uri=artifact.uri if artifact else None,
            artifact_mime=artifact.mime if artifact else None,
            artifact_size=artifact.size if artifact else None,
            artifact_sha256=artifact.sha256 if artifact else None,
        )
    except EvidenceError as exc:
        _raise(exc)
    response.status_code = 201 if created else 200
    return {
        "created": created,
        "evidence": evidence_service.record_payload(record),
    }


@router.get("")
async def list_evidence(
    learner_id: int | None = Query(None, ge=1),
    status: str | None = Query(None, max_length=16),
    source_type: str | None = Query(None, max_length=32),
    competency_id: str | None = Query(None, max_length=32),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List evidence visible to the caller.

    Learners see their own records. Reviewers see learners in courses they
    own or staff. Tenant-wide roles see their institution, and a platform
    administrator sees the system.
    """
    records = evidence_service.list_records(
        db,
        current_user,
        learner_id=learner_id,
        status=status,
        source_type=source_type,
        competency_id=competency_id,
        limit=limit,
        offset=offset,
    )
    return {"evidence": [evidence_service.record_payload(row) for row in records]}


@router.get("/rubrics")
async def list_evidence_rubrics(
    current_user: User = Depends(get_current_reporting_user),
):
    """Return the versioned rubric registry used by the review form."""
    return {
        "rubrics": sorted(
            load_rubrics().values(),
            key=lambda item: (str(item.get("rubric")), str(item.get("version"))),
        )
    }


@router.get("/analytics")
async def evidence_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_reporting_user),
):
    """Aggregate evidence operations for the caller's scope."""
    return evidence_analytics.overview(db, current_user)


@router.get("/appeals/queue")
async def appeal_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_reporting_user),
):
    """Pending learner appeals for the caller's scope."""
    appeals = evidence_service.list_appeals(db, current_user, status="pending")
    return {"appeals": [evidence_service.appeal_payload(row) for row in appeals]}


@router.post("/appeals/{appeal_id}/decision")
async def decide_appeal(
    appeal_id: int,
    payload: EvidenceAppealDecisionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_reporting_user),
):
    """Accept or reject an appeal. Acceptance returns evidence to review."""
    appeal = evidence_service.get_appeal(db, current_user, appeal_id)
    if appeal is None:
        raise api_error(404, "evidence_appeal_not_found", "Appeal not found.")
    try:
        evidence_service.review_appeal(
            db,
            appeal,
            current_user,
            decision=payload.decision,
            notes=payload.notes,
        )
    except EvidenceError as exc:
        _raise(exc)
    return {
        "appeal": evidence_service.appeal_payload(appeal),
        "evidence": evidence_service.record_payload(appeal.evidence),
    }


@router.get("/queue")
async def review_queue(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_reporting_user),
):
    """Evidence awaiting a first review or more evidence."""
    records = evidence_service.list_records(
        db,
        current_user,
        statuses=("collected", "in_review"),
        limit=limit,
    )
    return {"evidence": [evidence_service.record_payload(row) for row in records]}


@router.get("/{evidence_id}")
async def get_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Read one record with its competencies, reviews, and artifact hash."""
    record = evidence_service.get_record(db, current_user, evidence_id)
    if record is None:
        raise api_error(404, "evidence_not_found", "Evidence record not found.")
    return {"evidence": evidence_service.record_payload(record)}


@router.post("/{evidence_id}/review")
async def review_evidence(
    evidence_id: int,
    payload: EvidenceReviewIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_reporting_user),
):
    """Score, accept, reject, or request more evidence.

    The decision is appended; the record's content is never edited.
    """
    record = evidence_service.get_record(db, current_user, evidence_id)
    if record is None:
        raise api_error(404, "evidence_not_found", "Evidence record not found.")
    try:
        review = evidence_service.review_record(
            db,
            record,
            current_user,
            decision=payload.decision,
            criterion_scores=payload.criterion_scores,
            notes=payload.notes,
            next_step=payload.next_step,
        )
    except EvidenceError as exc:
        _raise(exc)
    return {
        "evidence": evidence_service.record_payload(record),
        "review": evidence_service.review_payload(review),
    }


@router.post("/{evidence_id}/appeal", status_code=201)
async def appeal_evidence(
    evidence_id: int,
    payload: EvidenceAppealIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Request a second review of a rejected evidence record."""
    record = evidence_service.get_record(db, current_user, evidence_id)
    if record is None:
        raise api_error(404, "evidence_not_found", "Evidence record not found.")
    try:
        appeal = evidence_service.create_appeal(
            db,
            record,
            current_user,
            reason=payload.reason,
        )
    except EvidenceError as exc:
        _raise(exc)
    return {"appeal": evidence_service.appeal_payload(appeal)}


@competency_router.get("/{competency_id}/evidence")
async def competency_evidence(
    competency_id: str,
    learner_id: int | None = Query(None, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Evidence linked to one competency, scoped to the caller."""
    return evidence_service.competency_summary(
        db,
        current_user,
        competency_id,
        learner_id=learner_id,
        limit=limit,
    )
