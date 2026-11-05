"""Learner feedback endpoints.

Community / Academic 1.1 keeps the lightweight like/dislike control that is
also available in Professional. It is deliberately small: the control is not
gated by survey consent, collects no free text, and reports only aggregate
totals to instructors.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import (
    Course,
    CourseEnrollment,
    CourseLabAssignment,
    ExerciseReaction,
    Lab,
    LabCompletion,
    LabSession,
    User,
)

router = APIRouter()


class ExerciseReactionRequest(BaseModel):
    reaction: Optional[str] = Field(None, pattern="^(like|dislike)$")
    course_id: Optional[int] = None


def _require_started_lab(db: Session, current_user: User, lab_id: int):
    if current_user.role in {"admin", "instructor"}:
        return
    started = db.query(LabSession.id).filter(
        LabSession.user_id == current_user.id,
        LabSession.lab_id == lab_id,
        LabSession.is_diagnostic == False,  # noqa: E712 - SQL boolean comparison
    ).first()
    completed = db.query(LabCompletion.id).filter(
        LabCompletion.user_id == current_user.id,
        LabCompletion.lab_id == lab_id,
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).first()
    if not started and not completed:
        raise HTTPException(
            status_code=403,
            detail="Start the exercise before rating it",
        )


@router.get("/reaction/{lab_id}")
async def get_exercise_reaction(
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the signed-in learner's own reaction to an exercise."""
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Exercise not found")
    row = db.query(ExerciseReaction).filter(
        ExerciseReaction.user_id == current_user.id,
        ExerciseReaction.lab_id == lab_id,
    ).first()
    return {
        "lab_id": lab_id,
        "reaction": row.reaction if row else None,
        "course_id": row.course_id if row else None,
        "updated_at": row.updated_at.isoformat() if row and row.updated_at else None,
    }


@router.post("/reaction/{lab_id}")
async def set_exercise_reaction(
    lab_id: int,
    payload: ExerciseReactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create, change, or clear a learner's reaction to an exercise."""
    lab = db.query(Lab).filter(
        Lab.id == lab_id, Lab.is_active == True
    ).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Exercise not found")

    course_id = payload.course_id
    if course_id is not None:
        course = db.query(Course).filter(
            Course.id == course_id, Course.is_active == True
        ).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        assigned = db.query(CourseLabAssignment.id).filter(
            CourseLabAssignment.course_id == course_id,
            CourseLabAssignment.lab_id == lab_id,
        ).first()
        if not assigned:
            raise HTTPException(
                status_code=400,
                detail="Exercise is not assigned to this course",
            )
        if current_user.role == "student":
            enrolled = db.query(CourseEnrollment.id).filter(
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.user_id == current_user.id,
            ).first()
            if not enrolled:
                raise HTTPException(
                    status_code=403,
                    detail="Join the course before rating its exercises",
                )

    _require_started_lab(db, current_user, lab_id)

    row = db.query(ExerciseReaction).filter(
        ExerciseReaction.user_id == current_user.id,
        ExerciseReaction.lab_id == lab_id,
    ).first()

    if payload.reaction is None:
        if row is not None:
            db.delete(row)
            db.commit()
        return {"reaction": None, "course_id": course_id, "updated_at": None}

    now = datetime.now(timezone.utc)
    if row is None:
        row = ExerciseReaction(
            user_id=current_user.id,
            lab_id=lab_id,
            course_id=course_id,
            reaction=payload.reaction,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
    else:
        row.reaction = payload.reaction
        row.course_id = course_id
        row.updated_at = now
    db.commit()
    return {
        "reaction": row.reaction,
        "course_id": row.course_id,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }
