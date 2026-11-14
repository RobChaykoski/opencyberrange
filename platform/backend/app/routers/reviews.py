"""Human review requests for deterministic results."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import (
    Course,
    CourseEnrollment,
    CourseLabAssignment,
    Lab,
    LabCompletion,
    ReviewRequest,
    FlagAttempt,
    User,
)
from app.services.activity import EventTypes, log_activity

router = APIRouter()


class ReviewRequestCreate(BaseModel):
    lab_id: int
    course_id: int | None = None
    source: str = Field("flag", max_length=30)
    reason: str = Field(..., min_length=5, max_length=1000)


class ReviewDecision(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    note: str = Field("", max_length=1000)


def _review_payload(
    row: ReviewRequest,
    student: User | None = None,
    lab_name: str | None = None,
) -> dict:
    return {
        "id": row.id,
        "user_id": row.user_id,
        "username": student.username if student else None,
        "lab_name": lab_name,
        "course_id": row.course_id,
        "lab_id": row.lab_id,
        "source": row.source,
        "reason": row.reason,
        "status": row.status,
        "rule_version": row.rule_version,
        "primary_factors": json.loads(row.primary_factors) if row.primary_factors else {},
        "decision_note": row.decision_note,
        "requested_at": row.requested_at.isoformat() if row.requested_at else None,
        "decided_at": row.decided_at.isoformat() if row.decided_at else None,
    }


def _course_for_lab(db: Session, user_id: int, lab_id: int) -> int | None:
    rows = (
        db.query(CourseLabAssignment.course_id)
        .join(
            CourseEnrollment,
            CourseEnrollment.course_id == CourseLabAssignment.course_id,
        )
        .filter(
            CourseLabAssignment.lab_id == lab_id,
            CourseEnrollment.user_id == user_id,
        )
        .distinct()
        .all()
    )
    return rows[0][0] if len(rows) == 1 else None


def _require_course_manager(db: Session, course_id: int, user: User) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if user.role != "admin" and course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to manage this course")
    return course


@router.post("/reviews", status_code=201)
async def request_review(
    payload: ReviewRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lab = db.query(Lab).filter(Lab.id == payload.lab_id).first()
    if lab is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    existing = (
        db.query(ReviewRequest)
        .filter(
            ReviewRequest.user_id == current_user.id,
            ReviewRequest.lab_id == payload.lab_id,
            ReviewRequest.status == "pending",
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="A human review request is already pending for this exercise.",
        )
    course_id = payload.course_id
    if course_id is not None:
        enrolled = (
            db.query(CourseEnrollment)
            .filter(
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.user_id == current_user.id,
            )
            .first()
        )
        if enrolled is None:
            raise HTTPException(status_code=403, detail="Not enrolled in this course")
    else:
        course_id = _course_for_lab(db, current_user.id, payload.lab_id)

    attempts = (
        db.query(FlagAttempt)
        .filter(
            FlagAttempt.user_id == current_user.id,
            FlagAttempt.lab_id == payload.lab_id,
        )
        .count()
    )
    completed = (
        db.query(LabCompletion)
        .filter(
            LabCompletion.user_id == current_user.id,
            LabCompletion.lab_id == payload.lab_id,
        )
        .first()
        is not None
    )
    row = ReviewRequest(
        user_id=current_user.id,
        course_id=course_id,
        lab_id=payload.lab_id,
        source=payload.source,
        reason=payload.reason.strip(),
        primary_factors=json.dumps(
            {
                "source": payload.source,
                "attempts": attempts,
                "completed": completed,
                "rule_version": "deterministic-v1",
            }
        ),
    )
    db.add(row)
    log_activity(
        db,
        EventTypes.REVIEW_REQUESTED,
        actor_id=current_user.id,
        target_type="lab",
        target_id=payload.lab_id,
        target_label=lab.name,
        detail={"course_id": course_id, "source": payload.source},
        commit=False,
    )
    db.commit()
    db.refresh(row)
    return _review_payload(row, current_user)


@router.get("/reviews/mine")
async def list_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = (
        db.query(ReviewRequest)
        .filter(ReviewRequest.user_id == current_user.id)
        .order_by(ReviewRequest.id.desc())
        .limit(50)
        .all()
    )
    return {"reviews": [_review_payload(row, current_user) for row in rows]}


@router.get("/courses/{course_id}/reviews")
async def list_course_reviews(
    course_id: int,
    status: str = "pending",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_course_manager(db, course_id, current_user)
    query = db.query(ReviewRequest, User).join(
        User, User.id == ReviewRequest.user_id
    ).filter(ReviewRequest.course_id == course_id)
    if status in ("pending", "approved", "rejected"):
        query = query.filter(ReviewRequest.status == status)
    rows = query.order_by(ReviewRequest.id.desc()).limit(200).all()
    lab_ids = {row.lab_id for row, _student in rows if row.lab_id}
    lab_names = {
        lab.id: lab.name
        for lab in db.query(Lab).filter(Lab.id.in_(lab_ids)).all()
    } if lab_ids else {}
    return {
        "reviews": [
            _review_payload(row, student, lab_names.get(row.lab_id))
            for row, student in rows
        ]
    }


@router.put("/reviews/{review_id}/decision")
async def decide_review(
    review_id: int,
    payload: ReviewDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    row = db.query(ReviewRequest).filter(ReviewRequest.id == review_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Review request not found")
    if row.course_id is None:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
    else:
        _require_course_manager(db, row.course_id, current_user)
    if row.status != "pending":
        raise HTTPException(status_code=409, detail="Review request is already decided")
    row.status = payload.status
    row.decision_note = (payload.note or "").strip()[:1000] or None
    row.decided_by_id = current_user.id
    row.decided_at = datetime.now(timezone.utc)
    log_activity(
        db,
        EventTypes.REVIEW_DECIDED,
        actor_id=current_user.id,
        target_type="user",
        target_id=row.user_id,
        detail={"review_id": row.id, "status": row.status},
        commit=False,
    )
    db.commit()
    db.refresh(row)
    student = db.query(User).filter(User.id == row.user_id).first()
    return _review_payload(row, student)
