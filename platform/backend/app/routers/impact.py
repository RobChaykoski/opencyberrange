"""Impact and legacy endpoints.

A learner sees only their own impact. A reviewer sees pending contributions for
learners they own or staff. Cohort aggregates suppress below five learners.
There is deliberately no learner ranking endpoint.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api_errors import api_error
from app.auth import get_current_active_user
from app.database import get_db
from app.models import User
from app.services import impact as impact_service
from app.services.impact import BASE_POINTS

router = APIRouter()


class ContributionIn(BaseModel):
    dimension: str
    kind: str
    title: str = Field(..., min_length=5, max_length=200)
    summary: str | None = Field(default=None, max_length=4000)
    reach_count: int = Field(default=0, ge=0)
    originality: str = "original"
    notes: str | None = Field(default=None, max_length=2000)
    occurred_at: datetime | None = None


class VerificationIn(BaseModel):
    validation_level: str = "instructor"
    quality_rating: float = Field(..., ge=3.0, le=5.0)
    reach_count: int | None = Field(default=None, ge=0)
    originality: str | None = None
    review_notes: str | None = Field(default=None, max_length=2000)


class RejectionIn(BaseModel):
    notes: str = Field(..., min_length=6, max_length=2000)


class StewardshipIn(BaseModel):
    points_delta: int
    category: str = "positive"
    reason: str = Field(..., min_length=10, max_length=300)
    evidence_ref: str | None = Field(default=None, max_length=300)
    visibility: str = "private"


def _raise(exc: impact_service.ImpactError):
    raise api_error(exc.status_code, exc.code, exc.message) from exc


@router.get("/me")
async def my_impact(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return impact_service.rollup(db, current_user)


@router.get("/catalogue")
async def impact_catalogue(
    current_user: User = Depends(get_current_active_user),
):
    """The contribution types and their base values."""
    return {
        "dimensions": BASE_POINTS,
        "validation_levels": list(impact_service.VALIDATION_MULTIPLIERS),
        "originalities": list(impact_service.ORIGINALITY_MULTIPLIERS),
    }


@router.post("/contributions", status_code=201)
async def submit_contribution(
    payload: ContributionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        row = impact_service.create_contribution(
            db, current_user, payload.model_dump()
        )
    except impact_service.ImpactError as exc:
        _raise(exc)
    return {
        "id": row.id,
        "status": row.status,
        "preview_points": impact_service.score_contribution(row)["preview_points"],
        "message": (
            "Submitted for verification. Self-reported work stays pending until "
            "another person verifies it."
        ),
    }


@router.get("/pending")
async def pending_contributions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return {"pending": impact_service.pending_queue(db, current_user)}


@router.post("/contributions/{contribution_id}/verify")
async def verify_contribution(
    contribution_id: int,
    payload: VerificationIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        row = impact_service.verify_contribution(
            db, current_user, contribution_id, payload.model_dump()
        )
    except impact_service.ImpactError as exc:
        _raise(exc)
    return {
        "id": row.id,
        "status": row.status,
        "points": impact_service.score_contribution(row)["points"],
    }


@router.post("/contributions/{contribution_id}/reject")
async def reject_contribution(
    contribution_id: int,
    payload: RejectionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        row = impact_service.reject_contribution(
            db, current_user, contribution_id, payload.notes
        )
    except impact_service.ImpactError as exc:
        _raise(exc)
    return {"id": row.id, "status": row.status}


@router.post("/stewardship/{learner_id}", status_code=201)
async def record_stewardship(
    learner_id: int,
    payload: StewardshipIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    learner = db.get(User, learner_id)
    if learner is None:
        raise api_error(404, "user_not_found", "Learner not found.")
    try:
        row = impact_service.record_stewardship(
            db, current_user, learner, payload.model_dump()
        )
    except impact_service.ImpactError as exc:
        _raise(exc)
    return {
        "id": row.id,
        "user_id": row.user_id,
        "points_delta": row.points_delta,
        "category": row.category,
    }


@router.get("/cohort")
async def cohort_impact(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role not in impact_service.READ_ROLES:
        raise api_error(
            403,
            "impact_forbidden",
            "Cohort impact is available to reviewers and administrators.",
        )
    summary = impact_service.cohort_summary(db, current_user)
    response.headers["Cache-Control"] = "no-store"
    return summary
