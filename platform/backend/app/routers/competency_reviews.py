"""Competency contract review-cycle endpoints.

A review is a signed instructor decision with a period and a next-review date.
The endpoints do not edit the generated contract file. An administrator exports
approved reviews separately.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api_errors import api_error
from app.auth import get_current_active_user
from app.database import get_db
from app.models import User
from app.services import competency_reviews

router = APIRouter()


class ReviewIn(BaseModel):
    competency_ids: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    assessment_reliability: dict[str, Any] = Field(default_factory=dict)
    assessment_criteria: list[str] = Field(default_factory=list)
    review_cycle_months: int = 12
    rationale: str = Field(..., min_length=20, max_length=4000)
    decision: str | None = None
    attestation: bool = False


def _raise(exc: competency_reviews.ReviewError):
    raise api_error(exc.status_code, exc.code, exc.message) from exc


@router.get("/queue")
async def review_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return competency_reviews.queue(db, current_user)
    except competency_reviews.ReviewError as exc:
        _raise(exc)


@router.get("/export-ready")
async def export_ready(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return competency_reviews.export_ready(db, current_user)
    except competency_reviews.ReviewError as exc:
        _raise(exc)


@router.get("/{lab_slug}")
async def review_detail(
    lab_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return competency_reviews.detail(db, current_user, lab_slug)
    except competency_reviews.ReviewError as exc:
        _raise(exc)


@router.post("/{lab_slug}/draft")
async def save_review_draft(
    lab_slug: str,
    payload: ReviewIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return competency_reviews.save_draft(
            db, current_user, lab_slug, payload.model_dump()
        )
    except competency_reviews.ReviewError as exc:
        _raise(exc)


@router.post("/{lab_slug}/sign")
async def sign_review(
    lab_slug: str,
    payload: ReviewIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return competency_reviews.sign(
            db, current_user, lab_slug, payload.model_dump()
        )
    except competency_reviews.ReviewError as exc:
        _raise(exc)


@router.post("/{review_id}/exported")
async def mark_review_exported(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return competency_reviews.mark_exported(db, current_user, review_id)
    except competency_reviews.ReviewError as exc:
        _raise(exc)
