"""Optional exercise knowledge-check endpoints.

These are benchmark-style practice quizzes attached to one exercise. They are
separate from the level quiz: unlimited re-attempts, a small random sample per
attempt, and explanations/references after submission.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Lab, User
from app.routers.curriculum import (
    _is_lab_visible,
    get_accessible_exclusive_lab_ids,
)
from app.schemas import ExerciseQuizSubmitRequest, ExerciseQuizFeedbackInput
from app.services import exercise_quiz

logger = logging.getLogger(__name__)
router = APIRouter()


def _lab_or_404(db: Session, lab_slug: str) -> Lab:
    lab = db.query(Lab).filter(
        Lab.slug == lab_slug,
        Lab.is_active == True,
    ).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return lab


def _visible_lab_or_403(db: Session, user: User, lab_slug: str) -> Lab:
    lab = _lab_or_404(db, lab_slug)
    accessible = get_accessible_exclusive_lab_ids(db, user.id)
    if not _is_lab_visible(lab, user, accessible):
        raise HTTPException(status_code=403, detail="You do not have access to this exercise")
    return lab


@router.get("/labs/{lab_slug}/quiz")
async def get_exercise_quiz(
    lab_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lab = _visible_lab_or_403(db, current_user, lab_slug)
    return exercise_quiz.summary(db, current_user, lab)


@router.post("/labs/{lab_slug}/quiz/attempts")
async def start_exercise_quiz(
    lab_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lab = _visible_lab_or_403(db, current_user, lab_slug)
    try:
        return exercise_quiz.start_attempt(db, current_user, lab)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/labs/{lab_slug}/quiz/attempts/{attempt_id}/submit")
async def submit_exercise_quiz(
    lab_slug: str,
    attempt_id: int,
    payload: ExerciseQuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lab = _visible_lab_or_403(db, current_user, lab_slug)
    try:
        return exercise_quiz.submit_attempt(
            db,
            current_user,
            lab,
            attempt_id,
            payload.answers,
            payload.feedback.model_dump() if payload.feedback else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/labs/{lab_slug}/quiz/attempts")
async def list_exercise_quiz_attempts(
    lab_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lab = _visible_lab_or_403(db, current_user, lab_slug)
    return exercise_quiz.list_attempts(db, current_user, lab)


@router.post("/labs/{lab_slug}/quiz/feedback")
async def submit_exercise_quiz_feedback(
    lab_slug: str,
    payload: ExerciseQuizFeedbackInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lab = _visible_lab_or_403(db, current_user, lab_slug)
    exercise_quiz.record_feedback(
        db, current_user, lab, payload.model_dump()
    )
    return {"status": "ok"}
