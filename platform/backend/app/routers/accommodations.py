"""Instructor and administrator accommodation management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_active_user, get_current_instructor_user
from app.database import get_db
from app.models import Course, CourseEnrollment, User
from app.services import accommodations
from app.services.activity import EventTypes, log_activity

router = APIRouter()


class AccommodationUpdate(BaseModel):
    time_multiplier: float = Field(..., ge=1.0, le=3.0)
    due_date_extension_days: int = Field(..., ge=0, le=365)
    notes: str = Field("", max_length=500)


def _managed_student(db: Session, course_id: int, student_id: int, actor: User):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if actor.role != "admin" and course.instructor_id != actor.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to manage this course"
        )
    student = db.query(User).filter(User.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    enrolled = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id == student_id,
        )
        .first()
    )
    if enrolled is None:
        raise HTTPException(
            status_code=404, detail="Learner is not enrolled in this course"
        )
    return course, student


def _response(student: User, record) -> dict:
    data = accommodations.serialize(record)
    data.update(
        {
            "user_id": student.id,
            "username": student.username,
            "effective_percent": round(data["time_multiplier"] * 100),
        }
    )
    return data


@router.get("/courses/{course_id}/students/{student_id}/accommodation")
async def get_student_accommodation(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    _, student = _managed_student(db, course_id, student_id, current_user)
    return _response(student, accommodations.get_record(db, student_id))


@router.put("/courses/{course_id}/students/{student_id}/accommodation")
async def set_student_accommodation(
    course_id: int,
    student_id: int,
    payload: AccommodationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    _, student = _managed_student(db, course_id, student_id, current_user)
    try:
        record = accommodations.set_accommodation(
            db,
            user_id=student_id,
            actor_id=current_user.id,
            time_multiplier=payload.time_multiplier,
            due_date_extension_days=payload.due_date_extension_days,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    log_activity(
        db,
        EventTypes.ACCOMMODATION_CHANGED,
        actor_id=current_user.id,
        target_type="user",
        target_id=student_id,
        target_label=student.username,
        detail={
            "accommodation": "updated",
            "time_multiplier": payload.time_multiplier,
            "due_date_extension_days": payload.due_date_extension_days,
        },
        commit=False,
    )
    db.commit()
    return _response(student, record)


@router.delete("/courses/{course_id}/students/{student_id}/accommodation")
async def clear_student_accommodation(
    course_id: int,
    student_id: int,
    reason: str = Query("", max_length=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    _, student = _managed_student(db, course_id, student_id, current_user)
    accommodations.clear_accommodation(
        db, user_id=student_id, actor_id=current_user.id, reason=reason
    )
    log_activity(
        db,
        EventTypes.ACCOMMODATION_CHANGED,
        actor_id=current_user.id,
        target_type="user",
        target_id=student_id,
        target_label=student.username,
        detail={"accommodation": "cleared"},
        commit=False,
    )
    db.commit()
    return _response(student, None)


@router.get("/accommodations/me")
async def get_my_accommodation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    record = accommodations.get_record(db, current_user.id)
    data = accommodations.serialize(record)
    data["effective_percent"] = round(data["time_multiplier"] * 100)
    return data

