"""Recognition board and manual award endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api_errors import api_error
from app.auth import get_current_active_user
from app.database import get_db
from app.models import User
from app.services import recognition as recognition_service

router = APIRouter()


class ManualAwardIn(BaseModel):
    key: str = Field(..., min_length=1, max_length=64)
    evidence_ref: str = Field(..., min_length=3, max_length=300)
    note: str = Field(..., min_length=10, max_length=2000)


def _raise(exc: recognition_service.RecognitionError):
    raise api_error(exc.status_code, exc.code, exc.message) from exc


@router.get("/me")
async def my_recognition(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return recognition_service.board(db, current_user)


@router.post("/evaluate")
async def evaluate_recognition(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    newly = recognition_service.evaluate(db, current_user)
    return {"newly_earned": newly}


@router.post("/seen")
async def mark_seen(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return {"marked": recognition_service.mark_seen(db, current_user)}


@router.post("/{learner_id}/award", status_code=201)
async def manual_award(
    learner_id: int,
    payload: ManualAwardIn,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    learner = db.get(User, learner_id)
    if learner is None:
        raise api_error(404, "user_not_found", "Learner not found.")
    try:
        award = recognition_service.manual_award(
            db,
            current_user,
            learner,
            payload.key,
            payload.evidence_ref,
            payload.note,
        )
    except recognition_service.RecognitionError as exc:
        _raise(exc)
    response.headers["Cache-Control"] = "no-store"
    return award
