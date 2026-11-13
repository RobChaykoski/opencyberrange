"""
Dashboard API routes for instructor and student dashboard views.
"""

import csv
import io
import json
import logging
from datetime import datetime, timezone, timedelta
from app.timezones import resolve_timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, literal_column

from app.database import get_db
from app.models import (
    User, Lab, LabSession, LabCompletion, FlagAttempt, WireGuardConfig,
    Course, CourseEnrollment, CourseLabAssignment, ActivityEvent,
    Track, Level, Achievement, CustomAchievement, Competition,
    AchievementCelebration, CourseCompletionReset,
)
from app.auth import get_current_active_user, get_current_instructor_user
from app.export_reason import require_export_reason
from app.services.activity import EVENT_LABELS
from app.services.audit import log_admin_action, AuditActions
from app.services.achievements import (
    ACHIEVEMENT_DESCRIPTIONS,
    ACHIEVEMENT_LABELS,
    BUILTIN_ACHIEVEMENT_ICONS,
    CLEAN_SWEEP,
    FIRST_BLOOD,
    competition_achievement_display,
    competition_achievement_parts,
    custom_achievement_id,
    resolve_achievement_label,
)
from app.services.pdf_report import generate_dashboard_report
from app.services.curriculum_manifest import chapter_label
from app.services.spreadsheet_safety import neutralize_row
from app.routers.courses import get_course_completed_lab_ids
from app.routers.curriculum import (
    _is_lab_visible,
    get_accessible_exclusive_lab_ids,
    get_user_completions,
)

# Report timestamps render in the requesting instructor's timezone, falling
# back to UTC for legacy accounts.

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== Helpers ====================

def _admin_user_ids(db: Session) -> set:
    """Return the set of user IDs with admin role (diagnostic actors)."""
    rows = db.query(User.id).filter(User.role == 'admin').all()
    return {r[0] for r in rows}


def _exclude_diagnostic(q, actor_col, db: Session):
    """Exclude admin-actor rows from a query."""
    admin_ids = _admin_user_ids(db)
    if admin_ids:
        q = q.filter(~actor_col.in_(admin_ids))
    return q


def _resolve_student_scope(db: Session, current_user: User,
                           course_id: Optional[int] = None,
                           user_id: Optional[int] = None):
    """Return a set of student IDs the current user is allowed to see,
    optionally narrowed by course_id and/or user_id.

    Under-18 accounts are excluded from instructor reporting by privacy rule,
    even when an administrator asks for them explicitly. Returns an empty set
    when the scope matches nobody.
    """
    is_admin = current_user.role == 'admin'

    if user_id:
        target = db.query(User).filter(User.id == user_id).first()
        if target is not None and getattr(target, "is_minor", False):
            raise HTTPException(
                status_code=403,
                detail=(
                    "This learner is excluded from reporting by an under-18 "
                    "privacy setting."
                ),
            )

    # Build base query for visible student IDs
    if is_admin and not course_id and not user_id:
        rows = db.query(User.id).filter(
            User.role == "student",
            User.is_minor == False,
        ).all()
        return {r[0] for r in rows}

    if course_id:
        # Validate instructor owns this course (skip for admin)
        if not is_admin:
            course = db.query(Course).filter(
                Course.id == course_id,
                Course.instructor_id == current_user.id,
            ).first()
            if not course:
                raise HTTPException(status_code=403, detail="Not your course")
        enrolled = db.query(CourseEnrollment.user_id).filter(
            CourseEnrollment.course_id == course_id,
        ).distinct().all()
        student_ids = {r[0] for r in enrolled}
    elif is_admin:
        rows = db.query(User.id).filter(
            User.role == "student",
            User.is_minor == False,
        ).all()
        student_ids = {r[0] for r in rows}
    else:
        # Instructor without course filter: all their students
        rows = db.query(CourseEnrollment.user_id).join(
            Course, Course.id == CourseEnrollment.course_id,
        ).filter(
            Course.instructor_id == current_user.id,
            Course.is_active == True,
        ).distinct().all()
        student_ids = {r[0] for r in rows}

    if student_ids:
        minor_ids = {
            row[0]
            for row in db.query(User.id).filter(
                User.id.in_(student_ids),
                User.is_minor == True,
            ).all()
        }
        student_ids -= minor_ids

    # Narrow to specific user
    if user_id:
        if student_ids is None:
            # Admin: trust the user_id directly
            student_ids = {user_id}
        elif user_id in student_ids:
            student_ids = {user_id}
        else:
            raise HTTPException(status_code=403, detail="User not in scope")

    return student_ids


def _aware(value):
    """Compare database timestamps safely when some are naive."""
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def _instructor_teaching_focus(
    db: Session,
    current_user: User,
    now: datetime,
    admin_ids: set[int],
) -> dict:
    """Small, actionable aggregates for the teaching dashboard.

    Deliberately scoped to active courses the instructor owns (all active
    courses for an admin). The certificate signal is per track/level, matching
    how certificates are actually issued; it is a prompt, not an award.
    """
    empty = {
        "near_certificate": [],
        "near_certificate_count": 0,
        "inactive_students": [],
        "inactive_students_count": 0,
        "recent_completions": [],
        "recent_completions_count": 0,
        "recent_certificates": [],
        "recent_certificates_count": 0,
    }

    course_query = db.query(Course).filter(Course.is_active == True)
    if current_user.role != 'admin':
        course_query = course_query.filter(Course.instructor_id == current_user.id)
    courses = course_query.all()
    course_ids = [course.id for course in courses]
    if not course_ids:
        return empty

    courses_by_id = {course.id: course for course in courses}
    enrollments = db.query(
        CourseEnrollment.course_id,
        CourseEnrollment.user_id,
        CourseEnrollment.enrolled_at,
    ).join(
        User, User.id == CourseEnrollment.user_id,
    ).filter(
        CourseEnrollment.course_id.in_(course_ids),
        User.is_minor == False,
    ).all()
    course_students = {}
    enrolled_at = {}
    student_ids = set()
    for course_id, user_id, joined_at in enrollments:
        if user_id in admin_ids:
            continue
        course_students.setdefault(course_id, set()).add(user_id)
        enrolled_at[(course_id, user_id)] = joined_at
        student_ids.add(user_id)
    if not student_ids:
        return empty

    assignment_rows = db.query(
        CourseLabAssignment.course_id,
        Lab.id,
        Level.id,
        Level.level_number,
        Level.name,
        Track.id,
        Track.name,
        Track.slug,
    ).join(
        Lab, Lab.id == CourseLabAssignment.lab_id,
    ).join(
        Level, Level.id == Lab.level_id,
    ).join(
        Track, Track.id == Level.track_id,
    ).filter(CourseLabAssignment.course_id.in_(course_ids)).all()

    groups = {}
    for course_id, lab_id, level_id, level_number, level_name, track_id, track_name, track_slug in assignment_rows:
        key = (course_id, level_id)
        group = groups.setdefault(key, {
            "course": courses_by_id[course_id],
            "level_id": level_id,
            "level_number": level_number,
            "level_name": level_name,
            "track_id": track_id,
            "track_name": track_name,
            "track_slug": track_slug,
            "lab_ids": set(),
        })
        group["lab_ids"].add(lab_id)

    all_lab_ids = set()
    for group in groups.values():
        all_lab_ids.update(group["lab_ids"])
    if not all_lab_ids:
        return empty

    completion_rows = db.query(
        LabCompletion.user_id,
        LabCompletion.lab_id,
        LabCompletion.completed_at,
    ).filter(
        LabCompletion.user_id.in_(student_ids),
        LabCompletion.lab_id.in_(all_lab_ids),
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).all()
    completion_times = {}
    for user_id, lab_id, when in completion_rows:
        when_aware = _aware(when)
        if when_aware is None:
            continue
        completion_times.setdefault((user_id, lab_id), []).append(when_aware)

    reset_rows = db.query(
        CourseCompletionReset.course_id,
        CourseCompletionReset.user_id,
        CourseCompletionReset.lab_id,
        CourseCompletionReset.reset_at,
    ).filter(
        CourseCompletionReset.course_id.in_(course_ids),
        CourseCompletionReset.user_id.in_(student_ids),
    ).all()
    reset_at = {}
    for course_id, user_id, lab_id, when in reset_rows:
        when_aware = _aware(when)
        if when_aware is None:
            continue
        key = (course_id, user_id, lab_id)
        previous = reset_at.get(key)
        if previous is None or when_aware > previous:
            reset_at[key] = when_aware

    def _completed_in_course(course_id, user_id, lab_id):
        """A lab counts only if earned after enrollment and after any reset."""
        joined = _aware(enrolled_at.get((course_id, user_id)))
        if joined is None:
            return False
        latest_reset = reset_at.get((course_id, user_id, lab_id))
        for when in completion_times.get((user_id, lab_id), ()):
            if when < joined:
                continue
            if latest_reset and when <= latest_reset:
                continue
            return True
        return False

    users = db.query(User).filter(User.id.in_(student_ids)).all()
    users_by_id = {user.id: user for user in users}
    course_codes = {}
    for course_id, members in course_students.items():
        for user_id in members:
            course_codes.setdefault(user_id, []).append(courses_by_id[course_id].code)

    near = {}
    recent_certificates = {}
    valid_completion_pairs = set()
    cutoff = now - timedelta(days=7)
    for (course_id, level_id), group in groups.items():
        total = len(group["lab_ids"])
        if total < 2:
            continue
        for user_id in course_students.get(course_id, set()):
            completed = [
                lab_id for lab_id in group["lab_ids"]
                if _completed_in_course(course_id, user_id, lab_id)
            ]
            for lab_id in completed:
                valid_completion_pairs.add((user_id, lab_id))
            remaining = total - len(completed)
            if remaining == 1:
                key = (user_id, group["track_id"], level_id)
                near.setdefault(key, {
                    "user_id": user_id,
                    "username": users_by_id[user_id].username if user_id in users_by_id else "Deleted user",
                    "course_code": group["course"].code,
                    "track_name": group["track_name"],
                    "level_name": group["level_name"],
                    "level_number": group["level_number"],
                    "completed": len(completed),
                    "total": total,
                })
            elif remaining == 0:
                latest = max(
                    (
                        max(completion_times.get((user_id, lab_id), [None]))
                        for lab_id in completed
                    ),
                    default=None,
                )
                if latest is not None and latest >= cutoff:
                    key = (user_id, group["track_id"], level_id)
                    recent_certificates.setdefault(key, {
                        "user_id": user_id,
                        "username": users_by_id[user_id].username if user_id in users_by_id else "Deleted user",
                        "course_code": group["course"].code,
                        "track_name": group["track_name"],
                        "level_name": group["level_name"],
                        "level_number": group["level_number"],
                        "awarded_at": latest.isoformat(),
                    })

    inactive = []
    for user in users:
        last_login = _aware(user.last_login_at)
        if last_login is None or last_login < cutoff:
            inactive.append({
                "user_id": user.id,
                "username": user.username,
                "last_login_at": last_login.isoformat() if last_login else None,
                "course_codes": sorted(set(course_codes.get(user.id, []))),
            })
    inactive.sort(key=lambda item: item["last_login_at"] or "")

    recent_completion_rows = db.query(
        LabCompletion, User.username, Lab.name,
    ).join(
        User, User.id == LabCompletion.user_id,
    ).join(
        Lab, Lab.id == LabCompletion.lab_id,
    ).filter(
        LabCompletion.user_id.in_(student_ids),
        LabCompletion.lab_id.in_(all_lab_ids),
        LabCompletion.completed_at >= cutoff,
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).order_by(LabCompletion.completed_at.desc()).all()
    recent_completion_items = [
        {
            "user_id": completion.user_id,
            "username": username,
            "lab_name": lab_name,
            "completed_at": completion.completed_at.isoformat() if completion.completed_at else None,
        }
        for completion, username, lab_name in recent_completion_rows
        if (completion.user_id, completion.lab_id) in valid_completion_pairs
    ]
    recent_completions = recent_completion_items[:8]
    recent_completion_count = len(recent_completion_items)

    near_items = sorted(near.values(), key=lambda item: (item["course_code"], item["username"]))
    certificate_items = sorted(
        recent_certificates.values(), key=lambda item: item["awarded_at"], reverse=True,
    )
    return {
        "near_certificate": near_items[:6],
        "near_certificate_count": len(near_items),
        "inactive_students": inactive[:6],
        "inactive_students_count": len(inactive),
        "recent_completions": recent_completions,
        "recent_completions_count": recent_completion_count,
        "recent_certificates": certificate_items[:6],
        "recent_certificates_count": len(certificate_items),
    }


def _instructor_learning_metrics(
    db: Session,
    now: datetime,
    admin_ids: set[int],
    student_ids: Optional[set[int]],
) -> dict:
    """Basic learning metrics for the last 7 days.

    Uses the same cohort scope as the rest of the ops dashboard. The score is a
    transparent 0-100 participation score, not the course scoreboard total:
    start at 100, subtract 10 per retry and 5 per hint, then clamp at zero.
    """
    cutoff = now - timedelta(days=7)

    def scoped(query, column):
        if student_ids is not None:
            query = query.filter(column.in_(student_ids)) if student_ids else query.filter(False)
        if admin_ids:
            query = query.filter(~column.in_(admin_ids))
        return query

    active_users: set[int] = set()
    session_rows = scoped(
        db.query(LabSession.user_id, LabSession.lab_id).filter(
            (LabSession.started_at >= cutoff) | (LabSession.stopped_at >= cutoff),
        ),
        LabSession.user_id,
    ).all()
    active_users.update(row[0] for row in session_rows)

    completion_rows = scoped(
        db.query(
            LabCompletion.user_id,
            LabCompletion.lab_id,
            LabCompletion.attempts,
            LabCompletion.hints_used,
        ).filter(LabCompletion.completed_at >= cutoff),
        LabCompletion.user_id,
    ).all()
    active_users.update(row[0] for row in completion_rows)

    attempt_users = scoped(
        db.query(FlagAttempt.user_id).filter(FlagAttempt.attempted_at >= cutoff),
        FlagAttempt.user_id,
    ).distinct().all()
    active_users.update(row[0] for row in attempt_users)

    scores = []
    struggling: set[int] = set()
    completed_pairs = set()
    for user_id, lab_id, attempts, hints in completion_rows:
        completed_pairs.add((user_id, lab_id))
        retries = max(0, (attempts or 1) - 1)
        score = 100 - retries * 10 - min(25, (hints or 0) * 5)
        score = max(0, min(100, score))
        scores.append(score)
        if score < 70 or (attempts or 1) >= 3:
            struggling.add(user_id)

    # Started but not finished during the window.
    for user_id, lab_id in session_rows:
        if (user_id, lab_id) not in completed_pairs:
            struggling.add(user_id)

    # Repeated incorrect submissions without a completion in the window.
    incorrect_rows = scoped(
        db.query(
            FlagAttempt.user_id,
            func.count(FlagAttempt.id).label("attempts"),
        ).filter(
            FlagAttempt.is_correct == False,
            FlagAttempt.attempted_at >= cutoff,
        ),
        FlagAttempt.user_id,
    ).group_by(FlagAttempt.user_id).having(
        func.count(FlagAttempt.id) >= 5
    ).all()
    completed_users = {user_id for user_id, _lab_id, _attempts, _hints in completion_rows}
    for user_id, _attempts in incorrect_rows:
        if user_id not in completed_users:
            struggling.add(user_id)

    return {
        "students_active": len(active_users),
        "labs_completed": len(completion_rows),
        "average_score": round(sum(scores) / len(scores), 1) if scores else None,
        "struggling_students": len(struggling),
        "metrics_window_days": 7,
    }


# ==================== Instructor Endpoints ====================

@router.get("/instructor/stats")
async def instructor_stats(
    tz_offset: int = Query(0, description="Client UTC offset in minutes (e.g. -300 for CDT)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Rich stat card data for the instructor Ops Center.

    Admins see platform-wide stats.  Instructors see only students
    enrolled in courses they own.  *tz_offset* (minutes) adjusts
    "today" to the client's local midnight.
    """
    now = datetime.now(timezone.utc)
    # Compute local midnight in UTC terms
    local_now = now + timedelta(minutes=tz_offset)
    today_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(minutes=tz_offset)
    yesterday_start = today_start - timedelta(days=1)

    # ── Scope: which student IDs does this user see? ─────────
    # Admins see all non-minor students; instructors see their enrolled
    # non-minor students. Under-18 accounts are excluded from reporting.
    if current_user.role != 'admin':
        rows = db.query(CourseEnrollment.user_id).join(
            Course, Course.id == CourseEnrollment.course_id,
        ).join(
            User, User.id == CourseEnrollment.user_id,
        ).filter(
            Course.instructor_id == current_user.id,
            Course.is_active == True,
            User.is_minor == False,
        ).distinct().all()
        student_ids = {r[0] for r in rows}
    else:
        rows = db.query(User.id).filter(
            User.role == "student",
            User.is_minor == False,
        ).all()
        student_ids = {r[0] for r in rows}

    admin_ids = _admin_user_ids(db)

    def _scoped(q, user_col):
        """Apply student scope filter and exclude admin/diagnostic actors."""
        if student_ids is not None:
            q = q.filter(user_col.in_(student_ids)) if student_ids else q.filter(False)
        if admin_ids:
            q = q.filter(~user_col.in_(admin_ids))
        return q

    # ── Flags Today ──────────────────────────────────────────
    q = db.query(func.count(FlagAttempt.id)).filter(
        FlagAttempt.is_correct == True,
        FlagAttempt.attempted_at >= today_start,
    )
    flags_today = _scoped(q, FlagAttempt.user_id).scalar() or 0

    q = db.query(func.count(FlagAttempt.id)).filter(
        FlagAttempt.is_correct == True,
        FlagAttempt.attempted_at >= yesterday_start,
        FlagAttempt.attempted_at < today_start,
    )
    flags_yesterday = _scoped(q, FlagAttempt.user_id).scalar() or 0

    q = db.query(func.count(func.distinct(FlagAttempt.user_id))).filter(
        FlagAttempt.is_correct == True,
        FlagAttempt.attempted_at >= today_start,
    )
    flag_students_today = _scoped(q, FlagAttempt.user_id).scalar() or 0

    # Last 7 days sparkline
    week_start = today_start - timedelta(days=6)
    q = db.query(
        func.date_trunc('day', FlagAttempt.attempted_at).label('day'),
        func.count(FlagAttempt.id),
    ).filter(
        FlagAttempt.is_correct == True,
        FlagAttempt.attempted_at >= week_start,
    )
    spark_rows = _scoped(q, FlagAttempt.user_id).group_by('day').order_by('day').all()
    spark_map = {r[0].date(): r[1] for r in spark_rows}
    flags_sparkline = []
    for i in range(7):
        d = (week_start + timedelta(days=i)).date()
        flags_sparkline.append(spark_map.get(d, 0))

    # ── Active Exercises ─────────────────────────────────────
    q = db.query(LabSession, User.username).join(
        User, User.id == LabSession.user_id
    ).filter(LabSession.status == "running")
    if student_ids is not None:
        q = q.filter(LabSession.user_id.in_(student_ids)) if student_ids else q.filter(False)
    if admin_ids:
        q = q.filter(~LabSession.user_id.in_(admin_ids))
    active_sessions = q.all()

    active_users = [
        {"username": username, "lab_id": s.lab_id}
        for s, username in active_sessions
    ]

    # ── Avg Completion ───────────────────────────────────────
    q = db.query(func.avg(LabCompletion.time_spent_minutes)).filter(
        LabCompletion.completed_at >= today_start,
        LabCompletion.time_spent_minutes.isnot(None),
        LabCompletion.time_spent_minutes > 0,
    )
    avg_time_today = _scoped(q, LabCompletion.user_id).scalar()

    month_start = today_start - timedelta(days=30)
    q = db.query(func.avg(LabCompletion.time_spent_minutes)).filter(
        LabCompletion.completed_at >= month_start,
        LabCompletion.time_spent_minutes.isnot(None),
        LabCompletion.time_spent_minutes > 0,
    )
    avg_time_typical = _scoped(q, LabCompletion.user_id).scalar()

    focus = _instructor_teaching_focus(db, current_user, now, admin_ids)
    learning = _instructor_learning_metrics(db, now, admin_ids, student_ids)
    return {
        "flags_today": flags_today,
        "flags_yesterday": flags_yesterday,
        "flag_students_today": flag_students_today,
        "flags_sparkline": flags_sparkline,
        "active_count": len(active_users),
        "active_users": active_users,
        "avg_completion_min": round(avg_time_today) if avg_time_today else None,
        "avg_completion_typical": round(avg_time_typical) if avg_time_typical else None,
        **learning,
        **focus,
    }


@router.get("/instructor/pulse")
async def instructor_pulse(
    start: Optional[str] = Query(None, description="ISO 8601 start datetime"),
    end: Optional[str] = Query(None, description="ISO 8601 end datetime"),
    course_id: Optional[int] = Query(None, description="Filter to a specific course"),
    user_id: Optional[int] = Query(None, description="Filter to a specific user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Hourly or daily data points for The Pulse chart."""
    now = datetime.now(timezone.utc)

    # Parse start/end or default to last 24 hours
    if start:
        try:
            range_start = datetime.fromisoformat(start.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start datetime format")
    else:
        range_start = now - timedelta(hours=24)

    if end:
        try:
            range_end = datetime.fromisoformat(end.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end datetime format")
    else:
        range_end = now

    # Determine bucket granularity: hours if range <= 48h, else days
    total_hours = (range_end - range_start).total_seconds() / 3600
    use_days = total_hours > 48
    trunc_unit = 'day' if use_days else 'hour'

    # Scope to visible students (respects course_id / user_id filters)
    student_ids = _resolve_student_scope(db, current_user, course_id, user_id)

    # Query activity_events grouped by bucket.
    # The truncation unit is rendered as a SQL literal so the SELECT and
    # GROUP BY expressions match exactly on PostgreSQL; separate bind
    # parameters make PostgreSQL reject the grouped query.
    bucket_expr = func.date_trunc(
        literal_column(f"'{trunc_unit}'"),
        ActivityEvent.created_at,
    ).label('bucket')
    q = db.query(
        bucket_expr,
        ActivityEvent.event_type,
        func.count(ActivityEvent.id).label('cnt'),
    ).filter(
        ActivityEvent.created_at >= range_start,
        ActivityEvent.created_at <= range_end,
    )
    q = _exclude_diagnostic(q, ActivityEvent.actor_id, db)
    if student_ids is not None:
        q = q.filter(ActivityEvent.actor_id.in_(student_ids)) if student_ids else q.filter(False)
    rows = q.group_by(bucket_expr, ActivityEvent.event_type).all()

    # Build bucket keys
    bucket_data = {}
    if use_days:
        num_days = int(total_hours // 24) + 1
        for i in range(num_days):
            d = (range_start + timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            key = d.strftime("%Y-%m-%dT00:00:00Z")
            bucket_data[key] = {"concurrent_labs": 0, "flags_submitted": 0}
    else:
        num_hours = int(total_hours) + 1
        for i in range(num_hours):
            h = (range_start + timedelta(hours=i)).replace(
                minute=0, second=0, microsecond=0
            )
            key = h.strftime("%Y-%m-%dT%H:00:00Z")
            bucket_data[key] = {"concurrent_labs": 0, "flags_submitted": 0}

    for row in rows:
        if use_days:
            bucket_key = row.bucket.strftime("%Y-%m-%dT00:00:00Z") if row.bucket else None
        else:
            bucket_key = row.bucket.strftime("%Y-%m-%dT%H:00:00Z") if row.bucket else None
        if bucket_key and bucket_key in bucket_data:
            if row.event_type == "lab_started":
                bucket_data[bucket_key]["concurrent_labs"] += row.cnt
            elif row.event_type in ("flag_correct", "flag_incorrect"):
                bucket_data[bucket_key]["flags_submitted"] += row.cnt

    data = [
        {"hour": k, "concurrent_labs": v["concurrent_labs"], "flags_submitted": v["flags_submitted"]}
        for k, v in bucket_data.items()
    ]

    return {"data": data, "granularity": trunc_unit}


@router.get("/instructor/feed")
async def instructor_feed(
    limit: int = 50,
    offset: int = 0,
    start: Optional[str] = Query(None, description="ISO 8601 start datetime"),
    end: Optional[str] = Query(None, description="ISO 8601 end datetime"),
    course_id: Optional[int] = Query(None, description="Filter to a specific course"),
    user_id: Optional[int] = Query(None, description="Filter to a specific user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Paginated activity event feed for the instructor dashboard."""
    query = db.query(ActivityEvent).options(
        joinedload(ActivityEvent.actor)
    )

    # Scope to visible students (respects course_id / user_id filters)
    student_ids = _resolve_student_scope(db, current_user, course_id, user_id)
    if student_ids is not None:
        if student_ids:
            query = query.filter(ActivityEvent.actor_id.in_(student_ids))
        else:
            query = query.filter(False)

    if start:
        try:
            range_start = datetime.fromisoformat(start.replace('Z', '+00:00'))
            query = query.filter(ActivityEvent.created_at >= range_start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start datetime format")

    if end:
        try:
            range_end = datetime.fromisoformat(end.replace('Z', '+00:00'))
            query = query.filter(ActivityEvent.created_at <= range_end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end datetime format")

    events = query.order_by(
        ActivityEvent.created_at.desc()
    ).offset(offset).limit(limit).all()

    result = []
    for e in events:
        result.append({
            "id": e.id,
            "event_type": e.event_type,
            "event_label": EVENT_LABELS.get(e.event_type, e.event_type),
            "actor_id": e.actor_id,
            "actor_username": e.actor.username if e.actor else None,
            "actor_role": e.actor.role if e.actor else None,
            "target_type": e.target_type,
            "target_id": e.target_id,
            "target_label": (resolve_achievement_label(db, e.target_label) if e.target_type == "achievement" and e.target_label else e.target_label),
            "detail": e.detail,
            "created_at": (e.created_at.isoformat() + "Z") if e.created_at else None,
        })

    return {"events": result, "limit": limit, "offset": offset}


@router.get("/instructor/filter-options")
async def instructor_filter_options(
    course_id: Optional[int] = Query(None, description="Get students for a specific course"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Return courses and students available to the current user for filtering."""
    is_admin = current_user.role == 'admin'

    # Courses
    if is_admin:
        courses = db.query(Course).filter(Course.is_active == True).order_by(Course.code).all()
    else:
        courses = db.query(Course).filter(
            Course.instructor_id == current_user.id,
            Course.is_active == True,
        ).order_by(Course.code).all()

    # Students (all visible, or filtered by course)
    if course_id:
        if not is_admin:
            owns = db.query(Course).filter(
                Course.id == course_id, Course.instructor_id == current_user.id
            ).first()
            if not owns:
                raise HTTPException(status_code=403, detail="Not your course")
        students_q = db.query(User).join(
            CourseEnrollment, CourseEnrollment.user_id == User.id
        ).filter(
            CourseEnrollment.course_id == course_id,
            User.role == 'student',
            User.is_minor == False,
        ).order_by(User.username)
    elif is_admin:
        students_q = db.query(User).filter(
            User.role == 'student',
            User.is_minor == False,
        ).order_by(User.username)
    else:
        students_q = db.query(User).join(
            CourseEnrollment, CourseEnrollment.user_id == User.id
        ).join(
            Course, Course.id == CourseEnrollment.course_id
        ).filter(
            Course.instructor_id == current_user.id,
            Course.is_active == True,
            User.role == 'student',
            User.is_minor == False,
        ).distinct().order_by(User.username)

    students = students_q.all()

    return {
        "courses": [{"id": c.id, "code": c.code, "name": c.name} for c in courses],
        "students": [{"id": s.id, "username": s.username} for s in students],
    }


@router.get("/instructor/report")
async def instructor_report(
    request: Request,
    reason: str = Depends(require_export_reason),
    format: str = Query("pdf", description="Report format: 'pdf' or 'csv'"),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    course_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    range_label: Optional[str] = Query(None, description="Human label for window e.g. 'Last 7 days'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Download a report of the currently filtered dashboard view.

    Includes: student details (or per-student summary), an activity graphic,
    and the filtered activity log.
    """
    fmt = (format or "pdf").lower()
    if fmt not in ("pdf", "csv"):
        raise HTTPException(status_code=400, detail="format must be 'pdf' or 'csv'")

    local_tz = resolve_timezone(getattr(current_user, "timezone", None))

    # Parse range (default last 24 h)
    now = datetime.now(timezone.utc)
    try:
        range_start = datetime.fromisoformat(start.replace('Z', '+00:00')) if start else now - timedelta(hours=24)
        range_end = datetime.fromisoformat(end.replace('Z', '+00:00')) if end else now
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    student_ids = _resolve_student_scope(db, current_user, course_id, user_id)

    admin_ids = _admin_user_ids(db)

    def _scope(q, col):
        if student_ids is not None:
            q = q.filter(col.in_(student_ids)) if student_ids else q.filter(False)
        if admin_ids:
            q = q.filter(~col.in_(admin_ids))
        return q

    # ── Fetch events ─────────────────────────────────────────
    ev_q = db.query(ActivityEvent).options(joinedload(ActivityEvent.actor)).filter(
        ActivityEvent.created_at >= range_start,
        ActivityEvent.created_at <= range_end,
    )
    ev_q = _scope(ev_q, ActivityEvent.actor_id)
    events_rows = ev_q.order_by(ActivityEvent.created_at.desc()).limit(5000).all()

    events = []
    for e in events_rows:
        events.append({
            "id": e.id,
            "event_type": e.event_type,
            "event_label": EVENT_LABELS.get(e.event_type, e.event_type),
            "actor_username": e.actor.username if e.actor else None,
            "actor_role": e.actor.role if e.actor else None,
            "target_label": (resolve_achievement_label(db, e.target_label) if e.target_type == "achievement" and e.target_label else e.target_label),
            "detail": e.detail,
            "created_at": e.created_at,
        })

    # ── Scope / labels ───────────────────────────────────────
    course = db.query(Course).filter(Course.id == course_id).first() if course_id else None
    target_user = db.query(User).filter(User.id == user_id).first() if user_id else None

    scope_parts = []
    if course:
        scope_parts.append(f"{course.code} - {course.name}")
    if target_user:
        scope_parts.append(f"Student: {target_user.username}")
    if not scope_parts:
        scope_parts.append("All visible activity")
    scope_label = " / ".join(scope_parts)

    filters = {
        "range_label": range_label or f"{range_start.isoformat()} to {range_end.isoformat()}",
        "start_local": range_start.astimezone(local_tz).strftime("%Y-%m-%d %H:%M"),
        "end_local": range_end.astimezone(local_tz).strftime("%Y-%m-%d %H:%M"),
        "scope_label": scope_label,
        "course_code": course.code if course else None,
    }

    # ── Per-student summary (always computed; used for both single + list) ──
    def _summary_for(uid: int) -> dict:
        flags_c = db.query(func.count(FlagAttempt.id)).filter(
            FlagAttempt.user_id == uid,
            FlagAttempt.is_correct == True,
            FlagAttempt.attempted_at >= range_start,
            FlagAttempt.attempted_at <= range_end,
        ).scalar() or 0
        flags_w = db.query(func.count(FlagAttempt.id)).filter(
            FlagAttempt.user_id == uid,
            FlagAttempt.is_correct == False,
            FlagAttempt.attempted_at >= range_start,
            FlagAttempt.attempted_at <= range_end,
        ).scalar() or 0
        labs_done = db.query(func.count(LabCompletion.id)).filter(
            LabCompletion.user_id == uid,
            LabCompletion.completed_at >= range_start,
            LabCompletion.completed_at <= range_end,
        ).scalar() or 0
        sess = db.query(func.count(LabSession.id)).filter(
            LabSession.user_id == uid,
            LabSession.started_at >= range_start,
            LabSession.started_at <= range_end,
        ).scalar() or 0
        return {
            "flags_correct": flags_c,
            "flags_wrong": flags_w,
            "labs_completed": labs_done,
            "sessions_started": sess,
        }

    student_detail = None
    students_summary = []
    if target_user:
        s = _summary_for(target_user.id)
        student_detail = {
            "username": target_user.username,
            "email": target_user.email,
            "role": target_user.role,
            **s,
        }
    else:
        # Find students active in the window within scope
        active_q = db.query(User).join(
            ActivityEvent, ActivityEvent.actor_id == User.id
        ).filter(
            ActivityEvent.created_at >= range_start,
            ActivityEvent.created_at <= range_end,
        )
        if student_ids is not None:
            active_q = active_q.filter(User.id.in_(student_ids)) if student_ids else active_q.filter(False)
        active_users = active_q.distinct().order_by(User.username).all()
        for u in active_users:
            row = {"username": u.username, **_summary_for(u.id)}
            students_summary.append(row)

    # ── Pulse buckets (reuse logic from instructor_pulse) ────
    total_hours = (range_end - range_start).total_seconds() / 3600
    use_days = total_hours > 48
    trunc_unit = 'day' if use_days else 'hour'

    bucket_expr = func.date_trunc(
        literal_column(f"'{trunc_unit}'"),
        ActivityEvent.created_at,
    ).label('bucket')
    pq = db.query(
        bucket_expr,
        ActivityEvent.event_type,
        func.count(ActivityEvent.id).label('cnt'),
    ).filter(
        ActivityEvent.created_at >= range_start,
        ActivityEvent.created_at <= range_end,
    )
    pq = _scope(pq, ActivityEvent.actor_id)
    pulse_rows = pq.group_by(bucket_expr, ActivityEvent.event_type).all()

    bucket_data = {}
    if use_days:
        num_days = int(total_hours // 24) + 1
        for i in range(num_days):
            d = (range_start + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            key = d.strftime("%Y-%m-%dT00:00:00Z")
            bucket_data[key] = {"hour": key, "concurrent_labs": 0, "flags_submitted": 0}
    else:
        num_hours = int(total_hours) + 1
        for i in range(num_hours):
            h = (range_start + timedelta(hours=i)).replace(minute=0, second=0, microsecond=0)
            key = h.strftime("%Y-%m-%dT%H:00:00Z")
            bucket_data[key] = {"hour": key, "concurrent_labs": 0, "flags_submitted": 0}

    for row in pulse_rows:
        if use_days:
            bkey = row.bucket.strftime("%Y-%m-%dT00:00:00Z") if row.bucket else None
        else:
            bkey = row.bucket.strftime("%Y-%m-%dT%H:00:00Z") if row.bucket else None
        if bkey and bkey in bucket_data:
            if row.event_type == "lab_started":
                bucket_data[bkey]["concurrent_labs"] += row.cnt
            elif row.event_type in ("flag_correct", "flag_incorrect"):
                bucket_data[bkey]["flags_submitted"] += row.cnt

    pulse = list(bucket_data.values())

    # ── Build filename ───────────────────────────────────────
    stamp = datetime.now(local_tz).strftime("%Y%m%d_%H%M")
    name_parts = ["ops_report", stamp]
    if course:
        name_parts.append(course.code.replace(" ", "_"))
    if target_user:
        name_parts.append(target_user.username)
    base_name = "_".join(name_parts)

    if fmt == "pdf":
        pdf_bytes = generate_dashboard_report(
            filters=filters,
            student=student_detail,
            students=students_summary,
            pulse=pulse,
            pulse_granularity=trunc_unit,
            events=events,
            timezone_name=getattr(current_user, "timezone", None),
        )
        log_admin_action(
            action=AuditActions.REPORT_EXPORTED,
            admin_user_id=current_user.id,
            admin_username=current_user.username,
            target_type="dashboard_report",
            details={
                "format": "pdf",
                "course_id": course_id,
                "user_id": user_id,
                "reason": reason,
            },
            ip_address=request.client.host if request.client else None,
        )
        return Response(
            content=bytes(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{base_name}.pdf"'},
        )

    # CSV
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["# SWOCTS Cyber Range Ops Center Report"])
    writer.writerow(neutralize_row(["# Scope", scope_label]))
    writer.writerow(neutralize_row(["# Range", filters["range_label"]]))
    writer.writerow(neutralize_row(["# Window (local)", f"{filters['start_local']} to {filters['end_local']}"]))
    writer.writerow([])

    if student_detail:
        writer.writerow(["# Student Details"])
        writer.writerow(["username", "email", "role", "flags_correct", "flags_wrong", "labs_completed", "sessions_started"])
        writer.writerow(neutralize_row([
            student_detail["username"], student_detail.get("email") or "",
            student_detail.get("role") or "", student_detail["flags_correct"],
            student_detail["flags_wrong"], student_detail["labs_completed"],
            student_detail["sessions_started"],
        ]))
        writer.writerow([])
    elif students_summary:
        writer.writerow(["# Students in Window"])
        writer.writerow(["username", "flags_correct", "flags_wrong", "labs_completed", "sessions_started"])
        for s in students_summary:
            writer.writerow(neutralize_row([s["username"], s["flags_correct"], s["flags_wrong"],
                             s["labs_completed"], s["sessions_started"]]))
        writer.writerow([])

    writer.writerow(["# Activity Pulse"])
    writer.writerow(["bucket", "concurrent_labs", "flags_submitted"])
    for p in pulse:
        writer.writerow(neutralize_row([p["hour"], p["concurrent_labs"], p["flags_submitted"]]))
    writer.writerow([])

    writer.writerow(["# Activity Log"])
    writer.writerow(["time_local", "user", "role", "event", "target", "detail"])
    for e in events:
        ts = e["created_at"]
        if isinstance(ts, datetime):
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            ts_str = ts.astimezone(local_tz).strftime("%Y-%m-%d %H:%M:%S")
        else:
            ts_str = str(ts or "")
        writer.writerow(neutralize_row([
            ts_str,
            e.get("actor_username") or "System",
            e.get("actor_role") or "",
            e.get("event_label") or e.get("event_type") or "",
            e.get("target_label") or "",
            (e.get("detail") or "").replace("\n", " ") if isinstance(e.get("detail"), str) else (e.get("detail") or ""),
        ]))

    csv_bytes = buf.getvalue().encode("utf-8")
    log_admin_action(
        action=AuditActions.REPORT_EXPORTED,
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        target_type="dashboard_report",
        details={
            "format": "csv",
            "course_id": course_id,
            "user_id": user_id,
            "reason": reason,
        },
        ip_address=request.client.host if request.client else None,
    )
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{base_name}.csv"'},
    )


# ==================== ICS Attack Coverage ====================

import os as _os
import yaml as _yaml

# Canonical taxonomy lives alongside the backend (app/data) so this endpoint and
# tools/ics-coverage/coverage_matrix.py read a single source.
_ICS_TAXONOMY_PATH = _os.path.join(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
    "data", "ics_attack_taxonomy.yaml",
)


def _load_ics_taxonomy():
    """Return (tactic_order, tactic_names, id_to_meta) from the canonical taxonomy.

    tactic_order preserves kill-chain order; id_to_meta maps a technique id to
    {tactic, name, aliases}.
    """
    with open(_ICS_TAXONOMY_PATH) as fh:
        data = _yaml.safe_load(fh) or {}
    tactics = data.get("tactics", {})
    tactic_order = list(tactics.keys())
    tactic_names = {k: v.get("name", k) for k, v in tactics.items()}
    id_to_meta = {}
    for tkey, tval in tactics.items():
        for tech in tval.get("techniques", []):
            id_to_meta[tech["id"]] = {
                "tactic": tkey,
                "name": tech["name"],
                "aliases": tech.get("aliases", []),
            }
    return tactic_order, tactic_names, id_to_meta


@router.get("/instructor/ics-coverage")
async def ics_attack_coverage(
    track: Optional[str] = Query(None, description="Track slug to scope to; default all tracks with tags"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """ICS ATT&CK coverage matrix per track, computed from lab ics_techniques tags.

    For each track: labs tagged vs total, techniques covered vs taxonomy total,
    a per-tactic heatmap (covered/total + lab count), the covered techniques with
    the labs that teach them, the gaps (taxonomy techniques no lab covers), and
    the untagged labs. Drives the instructor coverage view.
    """
    tactic_order, tactic_names, id_to_meta = _load_ics_taxonomy()

    tactic_techs = {t: [] for t in tactic_order}
    for tid, meta in id_to_meta.items():
        tactic_techs[meta["tactic"]].append(tid)
    total_tech = len(id_to_meta)

    q = (
        db.query(Lab.slug, Lab.name, Lab.ics_techniques, Track.slug, Track.name)
        .join(Level, Lab.level_id == Level.id)
        .join(Track, Level.track_id == Track.id)
    )
    if track:
        q = q.filter(Track.slug == track)

    tracks = {}
    for lab_slug, lab_name, ics_json, tslug, tname in q.all():
        tr = tracks.setdefault(tslug, {"slug": tslug, "name": tname, "labs": []})
        tr["labs"].append({"slug": lab_slug, "name": lab_name, "ics": ics_json})

    results = []
    for tslug, tr in tracks.items():
        tech_to_labs = {}
        tagged, untagged = [], []
        for lab in tr["labs"]:
            try:
                tags = json.loads(lab["ics"]) if lab["ics"] else []
            except (ValueError, TypeError):
                tags = []
            if not tags:
                untagged.append({"slug": lab["slug"], "name": lab["name"]})
                continue
            tagged.append(lab["slug"])
            for entry in tags:
                tid = entry.get("technique_id")
                if not tid:
                    continue
                tech_to_labs.setdefault(tid, []).append(
                    {"slug": lab["slug"], "name": lab["name"], "note": entry.get("note", "")}
                )

        # A track with no tagged labs is noise unless the caller asked for it.
        if not tagged and not track:
            continue

        tactics_out, gaps = [], []
        for t in tactic_order:
            techs = tactic_techs[t]
            covered_ids = [tid for tid in techs if tid in tech_to_labs]
            missing_ids = [tid for tid in techs if tid not in tech_to_labs]
            lab_set = {l["slug"] for tid in covered_ids for l in tech_to_labs[tid]}
            tactics_out.append({
                "key": t,
                "name": tactic_names[t],
                "covered": len(covered_ids),
                "total": len(techs),
                "lab_count": len(lab_set),
                "techniques": [
                    {
                        "id": tid,
                        "name": id_to_meta[tid]["name"],
                        "aliases": id_to_meta[tid]["aliases"],
                        "labs": tech_to_labs[tid],
                    }
                    for tid in covered_ids
                ],
            })
            if missing_ids:
                gaps.append({
                    "tactic": tactic_names[t],
                    "techniques": [{"id": tid, "name": id_to_meta[tid]["name"]} for tid in missing_ids],
                })

        results.append({
            "slug": tslug,
            "name": tr["name"],
            "labs_total": len(tr["labs"]),
            "labs_tagged": len(tagged),
            "techniques_covered": sum(1 for tid in id_to_meta if tid in tech_to_labs),
            "techniques_total": total_tech,
            "tactics_total": len(tactic_order),
            "tactics_touched": sum(1 for to in tactics_out if to["covered"] > 0),
            "tactics": tactics_out,
            "gaps": gaps,
            "untagged_labs": untagged,
        })

    results.sort(key=lambda r: r["slug"])
    return {"tracks": results}


# ==================== Student Endpoint ====================

@router.get("/student")
async def student_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Student dashboard: next objective, progress, VPN, rank."""

    # --- Progress ---
    tracks = db.query(Track).options(
        joinedload(Track.levels).joinedload(Level.labs)
    ).filter(Track.is_active == True).all()

    # Use the same visibility and completion helpers as the profile and
    # exercise catalogue. A dashboard total that counts course-only or draft
    # labs is not comparable with the catalogue count.
    accessible_exclusive_ids = get_accessible_exclusive_lab_ids(db, current_user.id)
    completed_ids = get_user_completions(db, current_user.id)

    total_labs = 0
    completed_labs = 0
    next_objective = None

    for track in tracks:
        for level in sorted(track.levels, key=lambda l: l.level_number):
            for lab in sorted(level.labs, key=lambda l: l.sort_order):
                if not _is_lab_visible(lab, current_user, accessible_exclusive_ids):
                    continue
                total_labs += 1
                if lab.id in completed_ids:
                    completed_labs += 1
                elif next_objective is None:
                    next_objective = {
                        "lab_id": lab.id,
                        "lab_name": lab.name,
                        "lab_slug": lab.slug,
                        "track_name": track.name,
                        "track_slug": track.slug,
                        "level_name": level.name,
                    }

    progress_percent = round(completed_labs / total_labs * 100) if total_labs > 0 else 0

    # --- VPN status ---
    wg_config = db.query(WireGuardConfig).filter(
        WireGuardConfig.user_id == current_user.id
    ).first()

    vpn_status = {
        "has_config": wg_config is not None,
        "vpn_registered": current_user.vpn_registered if wg_config else False,
        "client_ip": wg_config.client_ip if wg_config else None,
    }

    # --- Scoreboard rank (first enrolled active course) ---
    scoreboard_rank = None
    course_name = None

    enrollment = db.query(CourseEnrollment).join(
        Course
    ).filter(
        CourseEnrollment.user_id == current_user.id,
        Course.is_active == True,
    ).first()

    if enrollment:
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        if course:
            course_name = f"{course.code}"

            # Get assigned lab IDs
            assigned_lab_ids = [
                r[0] for r in db.query(CourseLabAssignment.lab_id).filter(
                    CourseLabAssignment.course_id == course.id,
                ).all()
            ]

            if assigned_lab_ids:
                # Single aggregated query: compute scores for all enrolled
                # students in one pass instead of N separate queries.
                from sqlalchemy import case
                score_expr = (
                    func.count(LabCompletion.id) * 100
                    + func.sum(case((LabCompletion.hints_used == 0, 25), else_=0))
                    + func.sum(case((LabCompletion.attempts == 1, 25), else_=0))
                )
                score_rows = (
                    db.query(CourseEnrollment.user_id, func.coalesce(score_expr, 0).label("total_score"))
                    .outerjoin(
                        LabCompletion,
                        (LabCompletion.user_id == CourseEnrollment.user_id)
                        & LabCompletion.lab_id.in_(assigned_lab_ids)
                        & LabCompletion.flag_submitted.isnot(None)
                        & (LabCompletion.flag_submitted != ""),
                    )
                    .filter(CourseEnrollment.course_id == course.id)
                    .group_by(CourseEnrollment.user_id)
                    .order_by(func.coalesce(score_expr, 0).desc())
                    .all()
                )
                for rank, (uid, _score) in enumerate(score_rows, 1):
                    if uid == current_user.id:
                        scoreboard_rank = rank
                        break

    # --- Completion matrix: courses (rows) x levels (columns) ---
    # A student may be enrolled in several courses whose exercises come from
    # different tracks and levels, so the columns are the union of every level
    # that has at least one exercise assigned to one of their courses. Each
    # cell counts only the exercises assigned to that course.
    matrix_columns = {}
    matrix_rows = []
    matrix_totals = {}
    now_utc = datetime.now(timezone.utc)

    enrollment_rows = db.query(Course, CourseEnrollment).join(
        CourseEnrollment,
        CourseEnrollment.course_id == Course.id,
    ).filter(
        CourseEnrollment.user_id == current_user.id,
        Course.is_active == True,
        Course.end_date >= now_utc,
    ).order_by(Course.code).all()

    for course, _enrollment in enrollment_rows:
        assigned_lab_ids = [
            r[0] for r in db.query(CourseLabAssignment.lab_id).filter(
                CourseLabAssignment.course_id == course.id,
            ).all()
        ]
        course_completed_ids = get_course_completed_lab_ids(
            db, current_user.id, course.id, set(assigned_lab_ids),
        )
        course_labs = []
        if assigned_lab_ids:
            course_labs = db.query(Lab).options(
                joinedload(Lab.level).joinedload(Level.track)
            ).filter(
                Lab.id.in_(assigned_lab_ids),
                Lab.is_active == True,
            ).all()

        cells = {}
        for lab in course_labs:
            level = lab.level
            if not level:
                continue
            chapter_id = lab.chapter_id
            key = chapter_id or f"L{level.id}"
            track_name = level.track.name if level.track else "Uncategorized"
            matrix_columns.setdefault(key, {
                "key": key,
                "track_name": track_name,
                "track_slug": level.track.slug if level.track else None,
                "level_number": level.level_number,
                "level_name": level.name,
                "chapter_id": chapter_id,
                "chapter_name": lab.chapter_name,
                "chapter_label": chapter_label(chapter_id),
            })
            cell = cells.setdefault(key, {"completed": 0, "total": 0})
            cell["total"] += 1
            if lab.id in course_completed_ids:
                cell["completed"] += 1

        row_completed = sum(c["completed"] for c in cells.values())
        row_total = sum(c["total"] for c in cells.values())
        matrix_rows.append({
            "course_id": course.id,
            "course_code": course.code,
            "course_name": course.name,
            "cells": cells,
            "completed": row_completed,
            "total": row_total,
        })
        for key, cell in cells.items():
            total = matrix_totals.setdefault(key, {"completed": 0, "total": 0})
            total["completed"] += cell["completed"]
            total["total"] += cell["total"]

    ordered_columns = sorted(
        matrix_columns.values(),
        key=lambda c: (
            c["track_name"].lower(),
            c["level_number"],
            (c.get("chapter_label") or "").lower(),
        ),
    )
    completion_matrix = {
        "columns": ordered_columns,
        "rows": matrix_rows,
        "totals": {
            "cells": matrix_totals,
            "completed": sum(r["completed"] for r in matrix_rows),
            "total": sum(r["total"] for r in matrix_rows),
        },
    }

    return {
        "next_objective": next_objective,
        "progress_percent": progress_percent,
        "total_labs": total_labs,
        "completed_labs": completed_labs,
        "vpn_status": vpn_status,
        "scoreboard_rank": scoreboard_rank,
        "course_name": course_name,
        "completion_matrix": completion_matrix,
    }


# ==================== Celebration Wall ====================

def _iso_utc(value: Optional[datetime]) -> Optional[str]:
    """Serialize a datetime as ISO 8601 with an explicit timezone."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _achievement_display(
    achievement_type: str, custom_defs: dict, competition_defs: dict | None = None
) -> tuple:
    """Return (label, icon, description) for a built-in or custom award.

    ``custom_defs`` is the pre-fetched CustomAchievement map, so a feed of
    awards only hits the database once for all of its labels. ``competition_defs``
    is the matching Competition map for event badges.
    """
    if achievement_type in ACHIEVEMENT_LABELS:
        return (
            ACHIEVEMENT_LABELS[achievement_type],
            BUILTIN_ACHIEVEMENT_ICONS.get(achievement_type, "\U0001F3C5"),
            ACHIEVEMENT_DESCRIPTIONS.get(achievement_type),
        )

    competition_parts = competition_achievement_parts(achievement_type)
    if competition_parts:
        competition = (competition_defs or {}).get(competition_parts[0])
        display = competition_achievement_display(
            achievement_type, competition.name if competition else None
        )
        if display:
            return display

    custom_id = custom_achievement_id(achievement_type)
    definition = custom_defs.get(custom_id) if custom_id is not None else None
    if definition:
        return (
            definition.name,
            definition.icon or "\U0001F3C5",
            definition.description,
        )
    return (achievement_type, "\U0001F3C5", None)


def _celebration_counts(db: Session, achievement_ids: list[int]) -> dict[int, int]:
    """Return achievement_id -> celebration count for a small feed."""
    if not achievement_ids:
        return {}
    rows = (
        db.query(
            AchievementCelebration.achievement_id,
            func.count(AchievementCelebration.id),
        )
        .filter(AchievementCelebration.achievement_id.in_(achievement_ids))
        .group_by(AchievementCelebration.achievement_id)
        .all()
    )
    return {achievement_id: count for achievement_id, count in rows}


def _public_achievement_or_404(db: Session, achievement_id: int) -> Achievement:
    """Return a wall-eligible achievement, or raise 404.

    The same visibility rules as the wall apply: an active, listed, non-admin
    owner. An unlisted learner can still see their own corner, but their wins
    are not public and cannot be celebrated.
    """
    achievement = (
        db.query(Achievement)
        .options(joinedload(Achievement.user))
        .filter(Achievement.id == achievement_id)
        .first()
    )
    if achievement is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    owner = achievement.user
    if (
        owner is None
        or not owner.is_active
        or not getattr(owner, "show_on_scoreboard", False)
        or getattr(owner, "is_minor", False)
        or owner.role == "admin"
    ):
        raise HTTPException(status_code=404, detail="Achievement is not on the wall")
    return achievement


@router.post("/celebrations/{achievement_id}/celebrate")
async def toggle_celebration(
    achievement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Toggle one anonymous celebration on a public achievement.

    The celebration is voluntary and anonymous: the wall returns only the
    count. The actor is stored so one person can celebrate a win once, but the
    actor's identity is never exposed. This endpoint does not touch analytics,
    progress, grading, or course-health data.
    """
    achievement = _public_achievement_or_404(db, achievement_id)
    if achievement.user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot celebrate your own win.",
        )

    existing = (
        db.query(AchievementCelebration)
        .filter(
            AchievementCelebration.achievement_id == achievement_id,
            AchievementCelebration.user_id == current_user.id,
        )
        .first()
    )
    if existing is not None:
        db.delete(existing)
        db.commit()
        celebrated = False
    else:
        db.add(
            AchievementCelebration(
                achievement_id=achievement_id,
                user_id=current_user.id,
            )
        )
        db.commit()
        celebrated = True

    count = (
        db.query(func.count(AchievementCelebration.id))
        .filter(AchievementCelebration.achievement_id == achievement_id)
        .scalar()
        or 0
    )
    return {"celebrated": celebrated, "count": count}


@router.get("/celebrations")
async def celebration_wall(
    limit: int = Query(15, ge=1, le=50, description="Recent wins to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """A cross-course wall of achievement wins, visible to every signed-in user.

    Only active users who have not opted out of scoreboards are counted in the
    public stats, feed, and leaderboard. Admin accounts are left off the public
    wall because they are the diagnostic actors in the instructor views. The
    current user's own awards are still returned in ``me`` so someone in
    privacy mode can see their personal corner.
    """
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=7)
    admin_ids = _admin_user_ids(db)

    def public_awards():
        """Awards eligible for the shared wall."""
        q = db.query(Achievement).join(
            User, User.id == Achievement.user_id
        ).filter(
            User.is_active == True,
            User.show_on_scoreboard == True,
            User.is_minor == False,
        )
        if admin_ids:
            q = q.filter(~Achievement.user_id.in_(admin_ids))
        return q

    custom_defs = {
        row.id: row for row in db.query(CustomAchievement).all()
    }
    competition_defs = {
        row.id: row for row in db.query(Competition).all()
    }

    total_awards = public_awards().count()
    unique_earners = public_awards().with_entities(
        func.count(func.distinct(Achievement.user_id))
    ).scalar() or 0
    awards_this_week = public_awards().filter(
        Achievement.awarded_at >= week_start
    ).count()
    first_bloods = public_awards().filter(
        Achievement.achievement_type == FIRST_BLOOD
    ).count()
    clean_sweeps = public_awards().filter(
        Achievement.achievement_type == CLEAN_SWEEP
    ).count()

    # Recent wins, newest first. Eager-load the people and places so a feed
    # of fifteen rows stays one query plus the joins.
    recent_rows = (
        public_awards()
        .options(
            joinedload(Achievement.user),
            joinedload(Achievement.course),
            joinedload(Achievement.lab),
        )
        .order_by(Achievement.awarded_at.desc().nullslast(), Achievement.id.desc())
        .limit(limit)
        .all()
    )

    recent = []
    recent_ids = [row.id for row in recent_rows]
    celebration_counts = _celebration_counts(db, recent_ids)
    my_celebrated = set()
    if recent_ids:
        my_celebrated = {
            achievement_id
            for (achievement_id,) in db.query(AchievementCelebration.achievement_id)
            .filter(
                AchievementCelebration.user_id == current_user.id,
                AchievementCelebration.achievement_id.in_(recent_ids),
            )
            .all()
        }
    for row in recent_rows:
        label, icon, description = _achievement_display(
            row.achievement_type, custom_defs, competition_defs
        )
        user = row.user
        name_mode = (getattr(user, "scoreboard_name_mode", None) or "real_name") if user else "real_name"
        # Anonymous users keep their border cosmetics but never publish a photo
        # that could identify them.
        show_avatar = bool(user and name_mode != "anonymous")
        recent.append({
            "id": row.id,
            "user_id": row.user_id,
            "username": user.username if user and name_mode != "anonymous" else None,
            "display_name": user.scoreboard_name if user else None,
            "name_mode": name_mode,
            "avatar_data": user.avatar_data if show_avatar else None,
            "avatar_border_style": (
                getattr(user, "avatar_border_style", None) or "solid"
            ) if user else "solid",
            "avatar_border_color": (
                getattr(user, "avatar_border_color", None) or "blue"
            ) if user else "blue",
            "achievement_type": row.achievement_type,
            "label": label,
            "icon": icon,
            "description": description,
            "lab_name": row.lab.name if row.lab else None,
            "course_code": row.course.code if row.course else None,
            "course_name": row.course.name if row.course else None,
            "awarded_at": _iso_utc(row.awarded_at),
            "is_mine": row.user_id == current_user.id,
            "celebration_count": celebration_counts.get(row.id, 0),
            "celebrated_by_me": row.id in my_celebrated,
        })

    # Celebration spotlight: the most recently celebrated people, one row per
    # person. Deliberately not a leaderboard. A public badge ranking turns a
    # learning record into a competition and conflicts with the platform's
    # learning-impact guidance; the wall celebrates moments instead.
    spotlight = []
    seen_user_ids = set()
    for row in recent_rows:
        if row.user_id in seen_user_ids:
            continue
        seen_user_ids.add(row.user_id)
        label, icon, _description = _achievement_display(
            row.achievement_type, custom_defs, competition_defs
        )
        user = row.user
        if user is None:
            continue
        name_mode = getattr(user, "scoreboard_name_mode", None) or "real_name"
        show_avatar = name_mode != "anonymous"
        spotlight.append({
            "user_id": user.id,
            "username": user.username if name_mode != "anonymous" else None,
            "display_name": user.scoreboard_name,
            "name_mode": name_mode,
            "avatar_data": user.avatar_data if show_avatar else None,
            "avatar_border_style": getattr(user, "avatar_border_style", None) or "solid",
            "avatar_border_color": getattr(user, "avatar_border_color", None) or "blue",
            "latest_label": label,
            "latest_icon": icon,
            "awarded_at": _iso_utc(row.awarded_at),
            "is_mine": user.id == current_user.id,
        })
        if len(spotlight) >= 6:
            break

    # Badge gallery: how often each badge has been awarded, and to how many
    # different people. Counts are public-only, matching the rest of the wall.
    badge_rows = (
        public_awards()
        .with_entities(
            Achievement.achievement_type.label("achievement_type"),
            func.count(Achievement.id).label("award_count"),
            func.count(func.distinct(Achievement.user_id)).label("earners"),
            func.max(Achievement.awarded_at).label("latest_at"),
        )
        .group_by(Achievement.achievement_type)
        .order_by(func.count(Achievement.id).desc())
        .all()
    )

    badges = []
    for row in badge_rows:
        label, icon, description = _achievement_display(
            row.achievement_type, custom_defs, competition_defs
        )
        badges.append({
            "type": row.achievement_type,
            "label": label,
            "icon": icon,
            "description": description,
            "count": row.award_count,
            "earners": row.earners,
            "latest_at": _iso_utc(row.latest_at),
        })

    # Anonymous celebration totals, grouped by badge type. This is about which
    # achievements resonate, not which people are most popular.
    celebration_query = (
        db.query(
            Achievement.achievement_type.label("achievement_type"),
            func.count(AchievementCelebration.id).label("celebrations"),
            func.count(func.distinct(AchievementCelebration.user_id)).label("celebrants"),
        )
        .join(AchievementCelebration, AchievementCelebration.achievement_id == Achievement.id)
        .join(User, User.id == Achievement.user_id)
        .filter(
            User.is_active == True,
            User.show_on_scoreboard == True,
            User.is_minor == False,
        )
    )
    if admin_ids:
        celebration_query = celebration_query.filter(~Achievement.user_id.in_(admin_ids))
    celebration_rows = (
        celebration_query
        .group_by(Achievement.achievement_type)
        .order_by(func.count(AchievementCelebration.id).desc())
        .all()
    )
    celebration_type_map = {
        row.achievement_type: {
            "celebrations": row.celebrations,
            "celebrants": row.celebrants,
        }
        for row in celebration_rows
    }
    for badge in badges:
        stats = celebration_type_map.get(badge["type"], {})
        badge["celebrations"] = stats.get("celebrations", 0)
        badge["celebrants"] = stats.get("celebrants", 0)

    celebrated_badges = []
    for row in celebration_rows[:5]:
        label, icon, description = _achievement_display(
            row.achievement_type, custom_defs, competition_defs
        )
        celebrated_badges.append({
            "type": row.achievement_type,
            "label": label,
            "icon": icon,
            "description": description,
            "celebrations": row.celebrations,
            "celebrants": row.celebrants,
        })

    # The current user's own corner. Their awards are returned even when they
    # opted out of the public wall; ``listed`` tells the page whether they are
    # part of the shared feed and ranking.
    my_badge_count = db.query(func.count(Achievement.id)).filter(
        Achievement.user_id == current_user.id
    ).scalar() or 0
    my_unique_badges = db.query(
        func.count(func.distinct(Achievement.achievement_type))
    ).filter(
        Achievement.user_id == current_user.id
    ).scalar() or 0

    my_recent_rows = (
        db.query(Achievement)
        .options(
            joinedload(Achievement.course),
            joinedload(Achievement.lab),
        )
        .filter(Achievement.user_id == current_user.id)
        .order_by(Achievement.awarded_at.desc().nullslast(), Achievement.id.desc())
        .limit(3)
        .all()
    )

    my_recent = []
    my_recent_ids = [row.id for row in my_recent_rows]
    my_recent_celebrations = _celebration_counts(db, my_recent_ids)
    for row in my_recent_rows:
        label, icon, description = _achievement_display(
            row.achievement_type, custom_defs, competition_defs
        )
        my_recent.append({
            "id": row.id,
            "achievement_type": row.achievement_type,
            "label": label,
            "icon": icon,
            "description": description,
            "lab_name": row.lab.name if row.lab else None,
            "course_code": row.course.code if row.course else None,
            "awarded_at": _iso_utc(row.awarded_at),
            "celebration_count": my_recent_celebrations.get(row.id, 0),
        })

    can_list = bool(
        current_user.is_active
        and current_user.id not in admin_ids
        and not getattr(current_user, "is_minor", False)
    )
    listed = bool(
        can_list
        and getattr(current_user, "show_on_scoreboard", True)
    )
    my_celebrations_received = (
        db.query(func.count(AchievementCelebration.id))
        .join(Achievement, Achievement.id == AchievementCelebration.achievement_id)
        .filter(Achievement.user_id == current_user.id)
        .scalar()
        or 0
    )
    my_celebrations_given = (
        db.query(func.count(AchievementCelebration.id))
        .filter(AchievementCelebration.user_id == current_user.id)
        .scalar()
        or 0
    )

    return {
        "generated_at": _iso_utc(now),
        "stats": {
            "total_awards": total_awards,
            "unique_earners": unique_earners,
            "awards_this_week": awards_this_week,
            "first_bloods": first_bloods,
            "clean_sweeps": clean_sweeps,
        },
        "recent": recent,
        "spotlight": spotlight,
        "celebrated_badges": celebrated_badges,
        "badges": badges,
        "me": {
            "badge_count": my_badge_count,
            "unique_badges": my_unique_badges,
            "celebrations_received": my_celebrations_received,
            "celebrations_given": my_celebrations_given,
            "listed": listed,
            "can_list": can_list,
            "username": current_user.username,
            "display_name": current_user.display_name,
            "scoreboard_name": current_user.scoreboard_name,
            "name_mode": getattr(current_user, "scoreboard_name_mode", None) or "real_name",
            "avatar_data": getattr(current_user, "avatar_data", None),
            "avatar_border_style": getattr(current_user, "avatar_border_style", None) or "solid",
            "avatar_border_color": getattr(current_user, "avatar_border_color", None) or "blue",
            "recent": my_recent,
        },
    }
