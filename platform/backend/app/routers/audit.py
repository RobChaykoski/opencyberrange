"""Audit history for a learner or instructor, plus impersonation sessions.

Admins can read any user's history. Instructors can read the history of a
student enrolled in a course they own. Every read is itself recorded in the
activity log.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.auth import get_current_active_user, get_current_admin_user
from app.database import get_db
from app.models import (
    ActivityEvent,
    Course,
    CourseEnrollment,
    ImpersonationSession,
    User,
)
from app.services.activity import EVENT_LABELS, EventTypes, log_activity

router = APIRouter()

MAX_EVENTS = 500
MAX_SESSIONS = 100


def _naive_utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _session_status(row: ImpersonationSession, now: datetime) -> str:
    if row.ended_at is not None:
        return "ended"
    if row.expires_at and row.expires_at <= now:
        return "expired"
    return "live"


def _session_payload(row: ImpersonationSession, now: datetime) -> dict:
    return {
        "id": row.id,
        "session_id": row.session_id,
        "actor_id": row.actor_id,
        "actor_username": row.actor_username,
        "target_user_id": row.target_user_id,
        "target_username": row.target_username,
        "mode": row.mode,
        "course_id": row.course_id,
        "read_only": bool(row.read_only),
        "ip_address": row.ip_address,
        "started_at": row.started_at.isoformat() if row.started_at else None,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        "ended_at": row.ended_at.isoformat() if row.ended_at else None,
        "end_reason": row.end_reason,
        "status": _session_status(row, now),
    }


def _event_payload(row: ActivityEvent, actor_name: str | None) -> dict:
    detail = row.detail
    if detail:
        try:
            detail = json.loads(detail)
        except (TypeError, ValueError):
            pass
    return {
        "id": row.id,
        "event_type": row.event_type,
        "label": EVENT_LABELS.get(row.event_type, row.event_type),
        "actor_id": row.actor_id,
        "actor_name": actor_name,
        "target_type": row.target_type,
        "target_id": row.target_id,
        "target_label": row.target_label,
        "detail": detail,
        "ip_address": row.ip_address,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def user_history(db: Session, user: User, limit: int = MAX_EVENTS) -> dict:
    events = (
        db.query(ActivityEvent)
        .filter(
            or_(
                ActivityEvent.actor_id == user.id,
                and_(
                    ActivityEvent.target_type == "user",
                    ActivityEvent.target_id == user.id,
                ),
            )
        )
        .order_by(ActivityEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    actor_ids = {row.actor_id for row in events if row.actor_id}
    names = {
        row.id: row.username
        for row in db.query(User.id, User.username).filter(User.id.in_(actor_ids)).all()
    } if actor_ids else {}

    now = _naive_utcnow()
    sessions = (
        db.query(ImpersonationSession)
        .filter(
            or_(
                ImpersonationSession.actor_id == user.id,
                ImpersonationSession.target_user_id == user.id,
            )
        )
        .order_by(ImpersonationSession.started_at.desc())
        .limit(MAX_SESSIONS)
        .all()
    )
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "is_active": bool(user.is_active),
        },
        "events": [_event_payload(row, names.get(row.actor_id)) for row in events],
        "impersonations": [_session_payload(row, now) for row in sessions],
        "event_count": len(events),
        "impersonation_count": len(sessions),
    }


def _record_view(db: Session, viewer: User, target: User, request: Request, scope: str, course_id: int | None = None) -> None:
    log_activity(
        db,
        EventTypes.AUDIT_REPORT_VIEWED,
        actor_id=viewer.id,
        target_type="user",
        target_id=target.id,
        target_label=target.username,
        detail={"scope": scope, "course_id": course_id},
        ip_address=request.client.host if request.client else None,
    )


@router.get("/admin/audit/users/by-username/{username}/history")
async def admin_user_history_by_username(
    username: str,
    request: Request,
    limit: int = MAX_EVENTS,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    user = (
        db.query(User)
        .filter(func.lower(User.username) == username.strip().lower())
        .first()
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    payload = user_history(db, user, min(max(limit, 1), MAX_EVENTS))
    _record_view(db, admin, user, request, "admin")
    return payload


@router.get("/admin/audit/users/{user_id}/history")
async def admin_user_history(
    user_id: int,
    request: Request,
    limit: int = MAX_EVENTS,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    payload = user_history(db, user, min(max(limit, 1), MAX_EVENTS))
    _record_view(db, admin, user, request, "admin")
    return payload


@router.get("/admin/audit/impersonations")
async def admin_impersonation_sessions(
    live_only: bool = False,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    now = _naive_utcnow()
    query = db.query(ImpersonationSession).order_by(
        ImpersonationSession.started_at.desc()
    )
    if live_only:
        query = query.filter(
            ImpersonationSession.ended_at.is_(None),
            ImpersonationSession.expires_at > now,
        )
    rows = query.limit(min(max(limit, 1), 200)).all()
    return {
        "sessions": [_session_payload(row, now) for row in rows],
        "server_time": now.isoformat() + "Z",
    }


@router.get("/courses/{course_id}/students/{user_id}/history")
async def course_student_history(
    course_id: int,
    user_id: int,
    request: Request,
    limit: int = MAX_EVENTS,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to audit this course")

    student = db.query(User).filter(User.id == user_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    enrolled = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id == student.id,
        )
        .first()
    )
    if enrolled is None:
        raise HTTPException(status_code=404, detail="Student is not enrolled in this course")

    payload = user_history(db, student, min(max(limit, 1), MAX_EVENTS))
    _record_view(db, current_user, student, request, "course", course_id)
    return payload
