"""
Course management routes: CRUD, enrollment, lab assignment, scoreboard,
achievements, and PDF reports.
"""

import io
import json
import os
import re
import secrets
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.database import get_db
from app.models import (
    User, Lab, LabCompletion, Course, CourseEnrollment,
    CourseLabAssignment, Achievement, CourseCompletionReset,
    Assignment, AssignmentLab, FlagAttempt, CustomAchievement,
    CourseFeedback, ExercisePulseSurvey, ExerciseReaction,
    Survey, SurveyAttachment, SurveyResponse, Level, Track,
    UserAccommodation,
)
from app.auth import get_current_active_user, get_current_instructor_user, get_current_admin_user
from app import entitlement
from app.schemas import (
    CourseCreate, CourseUpdate, CourseJoinRequest,
    CourseLabAssignRequest, CourseLabBulkRemoveRequest, CourseLabReorderRequest, CourseLabUpdateRequest, AssignmentReorderRequest,
    BulkEnrollRequest,
    MinorConsentRequest,
    AssignmentCreate, AssignmentUpdate, AssignmentLabsRequest,
    CourseFeedbackRequest,
)
from app.services.achievements import resolve_achievement_label
from app.services.curriculum_manifest import chapter_label
from app.services.learning_metadata import (
    aggregate_difficulty,
    level_label_for_numbers,
    percent_complete,
)
from app.services import exercise_quiz, settings_service, accommodations
from app.export_reason import require_export_reason
from app.services.audit import log_admin_action, AuditActions
from app.services.report_integrity import record_report
from app.services.activity import log_activity, EventTypes
from app.services.course_wiki import rebuild_course_wiki

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== Helpers ====================

def _generate_invite_code() -> str:
    return secrets.token_urlsafe(6)[:8]


WIKI_THEME_PALETTE = [
    "red", "pink", "purple", "deep-purple", "indigo", "blue",
    "light-blue", "cyan", "teal", "green", "light-green", "lime",
    "yellow", "amber", "orange", "deep-orange",
]


def _reserved_track_slugs() -> set:
    """Track slugs from the generated wiki registry (app/wiki_registry.json,
    emitted from wikis.yaml and shipped with the backend). A course wiki_slug
    must never collide with a track slug, or the /wiki/range/ and /wiki/course/
    namespaces clash (root cause of the original adpt collision). Fails open
    (empty set) if the registry is missing, so course creation is never blocked."""
    registry = os.path.join(os.path.dirname(__file__), "..", "wiki_registry.json")
    try:
        with open(os.path.abspath(registry)) as f:
            return set(json.load(f).get("tracks", {}).keys())
    except Exception:
        return set()


def _generate_wiki_slug(code: str, db: Session) -> str:
    """Generate a unique wiki slug from a course code (never colliding with a
    track slug or another course)."""
    base = re.sub(r'[^a-z0-9]', '', code.lower())
    if not base:
        base = "course"
    reserved = _reserved_track_slugs()
    slug = base
    suffix = 2
    while (slug in reserved
           or db.query(Course.id).filter(Course.wiki_slug == slug).first()):
        slug = f"{base}{suffix}"
        suffix += 1
    return slug


def _auto_assign_theme_color(db: Session) -> str:
    """Pick the next color from the palette, cycling through."""
    count = db.query(func.count(Course.id)).scalar() or 0
    return WIKI_THEME_PALETTE[count % len(WIKI_THEME_PALETTE)]


def _course_response(
    course: Course,
    db: Session,
    user_id: Optional[int] = None,
) -> dict:
    """Build a CourseResponse dict from a Course model.

    ``user_id`` is supplied when the caller is the learner viewing their own
    courses, so the card can show their course-aware completion progress.
    Staff responses leave ``completed_labs``/``progress_percent`` as ``None``
    because there is no single learner whose progress they represent.
    """
    student_count = db.query(func.count(CourseEnrollment.id)).filter(
        CourseEnrollment.course_id == course.id
    ).scalar()
    assignment_rows = (
        db.query(
            CourseLabAssignment.lab_id,
            Lab.difficulty,
            Level.level_number,
            Track.name,
        )
        .join(Lab, Lab.id == CourseLabAssignment.lab_id)
        .outerjoin(Level, Level.id == Lab.level_id)
        .outerjoin(Track, Track.id == Level.track_id)
        .filter(CourseLabAssignment.course_id == course.id)
        .all()
    )
    lab_count = len(assignment_rows)
    assigned_lab_ids = {row[0] for row in assignment_rows}
    difficulty, difficulty_rank = aggregate_difficulty(row[1] for row in assignment_rows)
    track_names = sorted({row[3] for row in assignment_rows if row[3]})
    level_numbers = sorted({
        row[2] for row in assignment_rows if row[2] is not None
    })
    course_level_label = level_label_for_numbers(level_numbers)
    completed_labs = None
    progress_percent = None
    if user_id is not None:
        completed_labs = len(get_course_completed_lab_ids(
            db, user_id, course.id, assigned_lab_ids,
        ))
        progress_percent = percent_complete(completed_labs, lab_count)
    return {
        "id": course.id,
        "name": course.name,
        "code": course.code,
        "semester": course.semester,
        "description": course.description,
        "invite_code": course.invite_code,
        "instructor_id": course.instructor_id,
        "instructor_name": course.instructor.username if course.instructor else None,
        "start_date": course.start_date,
        "end_date": course.end_date,
        "is_active": course.is_active,
        "is_archived": getattr(course, 'is_archived', False),
        "wiki_slug": getattr(course, 'wiki_slug', None),
        "wiki_theme_color": getattr(course, 'wiki_theme_color', 'blue'),
        "created_at": course.created_at,
        "student_count": student_count,
        "lab_count": lab_count,
        "completed_labs": completed_labs,
        "progress_percent": progress_percent,
        "difficulty": difficulty,
        "difficulty_rank": difficulty_rank,
        "track_names": track_names,
        "track_count": len(track_names),
        "level_numbers": level_numbers,
        "level_count": len(level_numbers),
        "level_label": course_level_label,
    }


def _require_instructor(course: Course, user: User):
    if user.role == 'admin':
        return  # Admins can manage any course
    if course.instructor_id == user.id:
        return  # Course owner can manage their own course
    raise HTTPException(status_code=403, detail="Not authorized to manage this course")


def _get_course_or_404(db: Session, course_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


def _ensure_scope_token(db: Session, enrollment: CourseEnrollment) -> str:
    """
    Assign a unique 4-char scope token to an enrollment if it doesn't already
    have one. Tokens are namespaced by course; tokens never collide with any
    OTHER active enrollment in the same course. Used by per-token-scoped
    tracks like ADPT (svc_kerb_<token>, etc.).

    Returns the token (existing or newly assigned).
    """
    if enrollment.scope_token:
        return enrollment.scope_token

    from sqlalchemy import text

    existing = {
        row[0] for row in db.execute(
            text("SELECT scope_token FROM course_enrollments "
                 "WHERE course_id = :cid AND scope_token IS NOT NULL"),
            {"cid": enrollment.course_id},
        ).fetchall()
        if row[0]
    }
    # 4-char lowercase alphanumeric, ~1.7M values; collision probability per
    # course negligible at any realistic class size.
    alphabet = "abcdefghijkmnpqrstuvwxyz23456789"  # avoid 0/o/1/l/i ambiguity
    for _ in range(100):
        candidate = "".join(secrets.choice(alphabet) for _ in range(4))
        if candidate not in existing:
            enrollment.scope_token = candidate
            return candidate
    raise HTTPException(status_code=500, detail="Could not allocate unique scope token after 100 attempts")


def get_course_completed_lab_ids(
    db: Session,
    user_id: int,
    course_id: int,
    assigned_lab_ids: set[int],
) -> set[int]:
    """Return lab IDs that count as completed within a course context.

    A lab is completed-in-course only if:
    - completed_at >= enrolled_at  AND
    - completed_at > latest reset_at (if any reset exists)
    """
    if not assigned_lab_ids:
        return set()

    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == user_id,
    ).first()
    if not enrollment:
        return set()

    enrolled_at = enrollment.enrolled_at

    completions = db.query(LabCompletion).filter(
        LabCompletion.user_id == user_id,
        LabCompletion.lab_id.in_(assigned_lab_ids),
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).all()

    if not completions:
        return set()

    resets = db.query(CourseCompletionReset).filter(
        CourseCompletionReset.course_id == course_id,
        CourseCompletionReset.user_id == user_id,
    ).all()
    reset_map = {}
    for r in resets:
        if r.lab_id not in reset_map or r.reset_at > reset_map[r.lab_id]:
            reset_map[r.lab_id] = r.reset_at

    result = set()
    for c in completions:
        if c.completed_at is None:
            continue
        if c.completed_at < enrolled_at:
            continue
        latest_reset = reset_map.get(c.lab_id)
        if latest_reset and c.completed_at <= latest_reset:
            continue
        result.add(c.lab_id)

    return result


def is_completed_in_course(
    db: Session,
    user_id: int,
    course_id: int,
    lab_id: int,
) -> bool:
    """Check if a single lab counts as completed in course context."""
    return lab_id in get_course_completed_lab_ids(db, user_id, course_id, {lab_id})


def calculate_lab_score(
    completion: Optional[LabCompletion],
    lab: Lab,
    course_id: int,
    db: Session,
    first_blood_user_id: Optional[int] = None,
) -> int:
    """Calculate score for a single lab completion within a course.

    If first_blood_user_id is provided, it's used directly instead of querying.
    """
    if not completion or not completion.flag_submitted:
        return 0

    score = 100  # Base

    # Hint scoring: per-hint deduction if hints define point_cost, else flat bonus
    hint_deduction = 0
    if completion.hints_used > 0:
        try:
            hints = json.loads(lab.hints) if lab.hints else []
            costs = [h.get("point_cost", 0) for h in hints if isinstance(h, dict)]
            if any(c > 0 for c in costs):
                # Deduct point_cost for each hint used (in order)
                for i in range(min(completion.hints_used, len(costs))):
                    hint_deduction += costs[i]
        except Exception:
            pass

    if hint_deduction > 0:
        score -= hint_deduction
    elif completion.hints_used == 0:
        score += 25

    # First attempt bonus
    if completion.attempts == 1:
        score += 25

    # Speed bonus
    if completion.time_spent_minutes and lab.duration_minutes:
        ratio = completion.time_spent_minutes / lab.duration_minutes
        if ratio <= 0.25:
            score += 50
        elif ratio <= 0.50:
            score += 30
        elif ratio <= 0.75:
            score += 10

    # First blood bonus
    if first_blood_user_id is not None:
        if first_blood_user_id == completion.user_id:
            score += 50
    else:
        # Fallback: query DB (used when called outside scoreboard context)
        first = db.query(LabCompletion.user_id).join(
            CourseEnrollment,
            CourseEnrollment.user_id == LabCompletion.user_id,
        ).filter(
            CourseEnrollment.course_id == course_id,
            LabCompletion.lab_id == lab.id,
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        ).order_by(LabCompletion.completed_at.asc()).first()
        if first and first[0] == completion.user_id:
            score += 50

    return score


# ==================== Course CRUD ====================

@router.post("/", status_code=201)
async def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Create a new course. Admin only."""
    if data.end_date <= data.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    # Entitlement cap: non-archived courses count against the edition limit
    course_limit = entitlement.active_course_limit()
    if course_limit is not None:
        active_count = db.query(Course).filter(Course.is_archived.isnot(True)).count()
        if active_count >= course_limit:
            edition = f"OCR-{entitlement.edition_name().capitalize()}"
            raise HTTPException(
                status_code=403,
                detail=(
                    f"{edition} includes {course_limit} active courses and this "
                    f"install has {active_count}. Archive a finished course to "
                    f"free a slot, or upgrade for unlimited courses (see LICENSING.md)."
                ),
            )

    owner_id = current_user.id
    if current_user.role == 'admin' and data.instructor_id is not None:
        target = db.query(User).filter(User.id == data.instructor_id).first()
        if not target or target.role not in ('instructor', 'admin'):
            raise HTTPException(status_code=400, detail="Selected instructor not found or does not have instructor/admin role")
        owner_id = target.id

    course = Course(
        name=data.name,
        code=data.code,
        semester=data.semester,
        description=data.description,
        invite_code=_generate_invite_code(),
        instructor_id=owner_id,
        start_date=data.start_date,
        end_date=data.end_date,
        is_active=False,
        wiki_slug=_generate_wiki_slug(data.code, db),
        wiki_theme_color=data.wiki_theme_color or _auto_assign_theme_color(db),
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    logger.info(f"Course created: {course.code} by {current_user.username}")
    return _course_response(course, db)


@router.get("/")
async def list_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List courses. Admins see all; instructors see own courses; students see enrolled only."""
    if current_user.role == 'admin':
        courses = db.query(Course).order_by(Course.created_at.desc()).all()
    elif current_user.role == 'instructor':
        courses = db.query(Course).filter(
            Course.instructor_id == current_user.id,
        ).order_by(Course.created_at.desc()).all()
    else:
        courses = db.query(Course).join(
            CourseEnrollment,
            CourseEnrollment.course_id == Course.id,
        ).filter(
            CourseEnrollment.user_id == current_user.id,
            Course.is_active == True,
        ).order_by(Course.created_at.desc()).all()

    viewer_id = current_user.id if current_user.role not in ('admin', 'instructor') else None
    responses = [_course_response(c, db, viewer_id) for c in courses]
    # Beginner-first so a learner meets the easiest course before a capstone.
    # Code/name break ties deterministically.
    responses.sort(key=lambda course: (
        course["difficulty_rank"],
        (course["code"] or "").lower(),
        (course["name"] or "").lower(),
    ))
    return {"courses": responses}


@router.get("/{course_id}")
async def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get course detail with assigned labs."""
    course = _get_course_or_404(db, course_id)

    # Must be admin, course owner, or enrolled
    is_instructor = (current_user.role == 'admin') or (course.instructor_id == current_user.id)
    is_enrolled = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == current_user.id,
    ).first() is not None

    if not is_instructor and not is_enrolled:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    # Get assigned labs with completion status
    assignments = db.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course_id,
    ).order_by(CourseLabAssignment.sort_order).all()

    assigned_lab_ids = {a.lab_id for a in assignments}
    if is_enrolled:
        from app.services.course_planning import cohort_lab_ids

        assigned_lab_ids |= cohort_lab_ids(db, current_user.id, course_id)

    # Course-aware: only count completions after enrollment (+ respecting resets)
    if is_enrolled:
        completed_ids = get_course_completed_lab_ids(
            db, current_user.id, course_id, assigned_lab_ids,
        )
    else:
        # Admin viewing without enrollment — show global completions
        completed_ids = {
            r[0] for r in db.query(LabCompletion.lab_id).filter(
                LabCompletion.user_id == current_user.id,
                LabCompletion.flag_submitted.isnot(None),
                LabCompletion.flag_submitted != "",
            ).all()
        }

    # Find lab IDs that belong to locked or not-yet-open assignments (for students)
    locked_lab_ids: set[int] = set()
    if not is_instructor:
        now_utc = datetime.now(timezone.utc)
        all_asns = db.query(Assignment).filter(
            Assignment.course_id == course_id,
        ).all()
        for asn in all_asns:
            # Manually locked
            if asn.locked:
                for al in asn.assignment_labs:
                    locked_lab_ids.add(al.lab_id)
                continue
            # Not yet open (future start_date)
            if asn.start_date:
                sd = asn.start_date
                if sd.tzinfo is None:
                    sd = sd.replace(tzinfo=timezone.utc)
                if sd > now_utc:
                    for al in asn.assignment_labs:
                        locked_lab_ids.add(al.lab_id)

    labs = []
    for a in assignments:
        lab = a.lab
        if not lab:
            continue
        is_lab_locked = lab.id in locked_lab_ids
        track_name = lab.level.track.name if lab.level and lab.level.track else "Course Assessments"
        track_slug = lab.level.track.slug if lab.level and lab.level.track else None
        level_name = lab.level.name if lab.level else "Assessments"
        labs.append({
            "id": lab.id,
            "name": a.display_name or lab.name,
            "slug": lab.slug,
            "description": lab.description,
            "difficulty": lab.difficulty,
            "category": lab.category,
            "duration_minutes": lab.duration_minutes,
            "sort_order": a.sort_order,
            "is_completed": lab.id in completed_ids,
            "is_active": lab.is_active,
            "is_course_exclusive": lab.is_course_exclusive,
            "track_name": track_name,
            "track_slug": track_slug,
            "level_name": level_name,
            "chapter_id": lab.chapter_id,
            "chapter_name": lab.chapter_name,
            "chapter_label": chapter_label(lab.chapter_id),
            "primary_competency": lab.primary_competency,
            "framework_refs": lab.framework_refs_list,
            "measurable_outcome": lab.measurable_outcome,
            "display_name": a.display_name,
            "locked": is_lab_locked,
            "workbook": lab.workbook,
        })

    now = datetime.now(timezone.utc)
    course_end = course.end_date
    if course_end.tzinfo is None:
        course_end = course_end.replace(tzinfo=timezone.utc)
    is_ended = now > course_end

    return {
        "course": _course_response(course, db),
        "labs": labs,
        "is_instructor": is_instructor,
        "is_enrolled": is_enrolled,
        "is_ended": is_ended,
    }


# ==================== Two-way course feedback ====================

def _feedback_avg(values):
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None
    return round(sum(clean) / len(clean), 2)


def _feedback_pct(part, whole):
    if not whole:
        return 0.0
    return round((part / whole) * 100, 1)


def _feedback_payload(row: CourseFeedback) -> dict:
    return {
        "id": row.id,
        "direction": row.direction,
        "clarity": row.clarity,
        "challenge": row.challenge,
        "engagement": row.engagement,
        "confidence": row.confidence,
        "comment": row.comment,
        "subject_user_id": row.subject_user_id,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


def _feedback_access(db: Session, course: Course, user: User) -> tuple[bool, bool]:
    is_instructor = user.role == "admin" or course.instructor_id == user.id
    is_enrolled = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course.id,
        CourseEnrollment.user_id == user.id,
    ).first() is not None
    return is_instructor, is_enrolled


CHECKIN_TITLE_PREFIX = "Course check-in - "
CHECKIN_QUESTIONS = [
    {
        "prompt": "How clear were the instructions and expectations?",
        "type": "scale",
        "options": [],
        "required": True,
    },
    {
        "prompt": "How well did the challenge level fit you?",
        "type": "scale",
        "options": [],
        "required": True,
    },
    {
        "prompt": "How engaging was the course so far?",
        "type": "scale",
        "options": [],
        "required": True,
    },
    {
        "prompt": "How confident do you feel applying the skills?",
        "type": "scale",
        "options": [],
        "required": True,
    },
    {
        "prompt": "What would make this course clearer?",
        "type": "text",
        "options": [],
        "required": False,
    },
]


def _course_checkin_survey(db: Session, course: Course) -> Optional[Survey]:
    """Find the auto-created course check-in survey for this course."""
    return (
        db.query(Survey)
        .join(SurveyAttachment, SurveyAttachment.survey_id == Survey.id)
        .filter(
            SurveyAttachment.course_id == course.id,
            Survey.title == f"{CHECKIN_TITLE_PREFIX}{course.code}",
        )
        .first()
    )


def _ensure_course_checkin_survey(db: Session, course: Course) -> Survey:
    """Create the default one-minute check-in through the survey engine.

    The survey is a normal ``Survey`` attached to the course, so instructors
    can reuse the existing survey builder, response view, and consent rules.
    """
    survey = _course_checkin_survey(db, course)
    if survey:
        return survey
    survey = Survey(
        title=f"{CHECKIN_TITLE_PREFIX}{course.code}",
        description=(
            "A one-minute course check-in. Responses feed the private feedback "
            "analysis and are not shown as a public ranking."
        ),
        questions=json.dumps(CHECKIN_QUESTIONS),
        created_by=course.instructor_id,
        is_active=True,
    )
    db.add(survey)
    db.flush()
    db.add(SurveyAttachment(survey_id=survey.id, course_id=course.id))
    db.commit()
    db.refresh(survey)
    return survey


def _survey_answer_int(row: SurveyResponse, index: int) -> Optional[int]:
    try:
        answers = json.loads(row.answers or "{}")
        value = answers.get(str(index))
        return int(value) if value is not None else None
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


def _survey_answer_text(row: SurveyResponse, index: int) -> Optional[str]:
    try:
        answers = json.loads(row.answers or "{}")
        value = answers.get(str(index))
        return str(value).strip() if value else None
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


@router.post("/{course_id}/feedback", status_code=201)
async def submit_course_feedback(
    course_id: int,
    body: CourseFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit a student course check-in or an instructor coaching note.

    Students update their own single check-in. Instructors address one enrolled
    student per note and may update it. Student rows keep the author internally
    for duplicate prevention but are aggregated anonymously for instructors.
    """
    course = _get_course_or_404(db, course_id)
    is_instructor, is_enrolled = _feedback_access(db, course, current_user)
    if not is_instructor and not is_enrolled:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    if not any((body.clarity, body.challenge, body.engagement, body.confidence, body.comment)):
        raise HTTPException(status_code=400, detail="Add a rating or a comment")

    if is_instructor:
        if not body.subject_user_id:
            raise HTTPException(status_code=400, detail="Choose a student to coach")
        enrollment = db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id == body.subject_user_id,
        ).first()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Student is not enrolled")
        direction = "instructor_student"
        subject_user_id = body.subject_user_id
    else:
        direction = "student_course"
        subject_user_id = None

    query = db.query(CourseFeedback).filter(
        CourseFeedback.course_id == course_id,
        CourseFeedback.author_id == current_user.id,
        CourseFeedback.direction == direction,
    )
    if subject_user_id is not None:
        query = query.filter(CourseFeedback.subject_user_id == subject_user_id)
    else:
        query = query.filter(CourseFeedback.subject_user_id.is_(None))

    row = query.first()
    if row is None:
        row = CourseFeedback(
            course_id=course_id,
            author_id=current_user.id,
            subject_user_id=subject_user_id,
            direction=direction,
        )
        db.add(row)
    row.clarity = body.clarity
    row.challenge = body.challenge
    row.engagement = body.engagement
    row.confidence = body.confidence
    row.comment = (body.comment or "").strip() or None
    db.commit()
    db.refresh(row)
    return {"status": "ok", "feedback": _feedback_payload(row)}


@router.get("/{course_id}/feedback/summary")
async def course_feedback_summary(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the private two-way feedback analysis for a course.

    Existing exercise pulse surveys and reactions are included immediately, so
    the dashboard is useful before anyone submits a new course check-in.
    """
    course = _get_course_or_404(db, course_id)
    is_instructor, is_enrolled = _feedback_access(db, course, current_user)
    if not is_instructor and not is_enrolled:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    enrolled = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id
    ).count()

    student_rows = db.query(CourseFeedback).filter(
        CourseFeedback.course_id == course_id,
        CourseFeedback.direction == "student_course",
    ).all()
    instructor_rows = db.query(CourseFeedback).filter(
        CourseFeedback.course_id == course_id,
        CourseFeedback.direction == "instructor_student",
        CourseFeedback.subject_user_id.isnot(None),
    ).all()
    pulse_rows = db.query(ExercisePulseSurvey).filter(
        ExercisePulseSurvey.course_id == course_id
    ).all()
    reaction_rows = db.query(ExerciseReaction).filter(
        ExerciseReaction.course_id == course_id
    ).all()
    quiz_metrics = exercise_quiz.course_quiz_metrics(db, course_id)

    # Reuse the existing survey engine for the student check-in. Instructors
    # get the default survey created automatically; students only see it once
    # it exists and they have opted in to surveys.
    checkin_survey = _course_checkin_survey(db, course)
    if is_instructor and checkin_survey is None:
        checkin_survey = _ensure_course_checkin_survey(db, course)
    survey_opt_in = bool(getattr(current_user, "survey_opt_in", False))
    can_submit_checkin = bool(
        is_enrolled and survey_opt_in and checkin_survey and checkin_survey.is_active
    )

    minimum = int(settings_service.get_setting(db, "analytics_min_cohort_size", "5") or 5)
    if enrolled <= 0:
        cohort_state = "no_evidence"
    elif enrolled < minimum:
        cohort_state = "suppressed"
    else:
        cohort_state = "available"
    if cohort_state != "available":
        suppression = {
            "state": cohort_state,
            "suppressed": cohort_state == "suppressed",
            "minimum_cohort_size": minimum,
            "sample_size": enrolled,
            "reason": (
                "No enrolled learners yet."
                if cohort_state == "no_evidence"
                else f"Cohort is smaller than the minimum cell size ({enrolled} of {minimum} learners)."
            ),
        }
        return {
            "course_id": course_id,
            "is_instructor": is_instructor,
            "enrolled": enrolled,
            "cohort_state": cohort_state,
            "suppression": suppression,
            "aggregate": {
                "enrolled": enrolled,
                "respondents": None,
                "response_rate": None,
                "clarity": None,
                "challenge": None,
                "engagement": None,
                "confidence": None,
                "overall_score": None,
                "quiz_experience": None,
                "data_sources": [],
            },
            "pulse": {"responses": None, "difficulty": None, "learning": None, "unclear": None},
            "reactions": {"likes": None, "dislikes": None, "like_ratio": None},
            "course_checkin": {
                "responses": None,
                "clarity": None,
                "challenge": None,
                "engagement": None,
                "confidence": None,
                "survey_id": checkin_survey.id if checkin_survey else None,
                "survey_title": checkin_survey.title if checkin_survey else None,
            },
            "instructor_coaching": {"notes": None, "students_coached": None},
            "quizzes": {},
            "has_data": False,
            "survey_opt_in": survey_opt_in,
            "can_submit_checkin": can_submit_checkin,
            "survey": (
                {
                    "id": checkin_survey.id,
                    "title": checkin_survey.title,
                    "is_active": bool(checkin_survey.is_active),
                    "questions": json.loads(checkin_survey.questions or "[]"),
                }
                if checkin_survey else None
            ),
            "prompt": suppression["reason"],
        }

    survey_responses = []
    if checkin_survey:
        survey_responses = db.query(SurveyResponse).filter(
            SurveyResponse.survey_id == checkin_survey.id,
            SurveyResponse.course_id == course_id,
        ).all()

    survey_clarity = _feedback_avg([_survey_answer_int(row, 0) for row in survey_responses])
    survey_challenge = _feedback_avg([_survey_answer_int(row, 1) for row in survey_responses])
    survey_engagement = _feedback_avg([_survey_answer_int(row, 2) for row in survey_responses])
    survey_confidence = _feedback_avg([_survey_answer_int(row, 3) for row in survey_responses])

    clarity = survey_clarity if survey_clarity is not None else _feedback_avg([row.clarity for row in student_rows])
    challenge = survey_challenge if survey_challenge is not None else _feedback_avg([row.challenge for row in student_rows])
    engagement = survey_engagement if survey_engagement is not None else _feedback_avg([row.engagement for row in student_rows])
    confidence = survey_confidence if survey_confidence is not None else _feedback_avg([row.confidence for row in student_rows])
    pulse_difficulty = _feedback_avg([row.difficulty for row in pulse_rows])
    pulse_learning = _feedback_avg([row.learning for row in pulse_rows])
    likes = sum(1 for row in reaction_rows if row.reaction == "like")
    dislikes = sum(1 for row in reaction_rows if row.reaction == "dislike")
    like_ratio = round(likes / (likes + dislikes), 3) if (likes + dislikes) else None

    checkin_respondents = (
        {row.user_id for row in survey_responses}
        | {row.author_id for row in student_rows}
    )
    respondents = (
        checkin_respondents
        | {row.user_id for row in pulse_rows}
        | {row.user_id for row in reaction_rows}
    )
    response_rate = _feedback_pct(len(respondents), enrolled)

    # A weighted 0-100 summary. Components with no evidence are omitted and the
    # remaining weights are renormalised, so a new course is not punished for
    # data it has not collected yet.
    components = []
    if clarity is not None:
        components.append(((clarity / 5) * 100, 0.4))
    elif pulse_learning is not None:
        components.append(((pulse_learning / 5) * 100, 0.4))
    if pulse_difficulty is not None:
        components.append((max(0.0, 100 - abs(pulse_difficulty - 3) * 25), 0.2))
    if like_ratio is not None:
        components.append((like_ratio * 100, 0.2))
    elif response_rate:
        components.append((response_rate, 0.2))
    if instructor_rows:
        coached = len({row.subject_user_id for row in instructor_rows})
        components.append((_feedback_pct(coached, enrolled), 0.2))
    quiz_ratings = [
        quiz_metrics[key]
        for key in ("satisfaction", "relevance", "usefulness", "ease_of_use")
        if quiz_metrics.get(key) is not None
    ]
    if quiz_ratings:
        quiz_experience = round(sum(quiz_ratings) / len(quiz_ratings), 2)
        components.append(((quiz_experience / 5) * 100, 0.1))
    else:
        quiz_experience = None
    overall_score = None
    if components:
        weight = sum(item[1] for item in components)
        overall_score = round(sum(value * w for value, w in components) / weight, 1)

    data_sources = []
    if survey_responses or student_rows:
        data_sources.append("course_checkin")
    if pulse_rows:
        data_sources.append("exercise_pulse")
    if reaction_rows:
        data_sources.append("exercise_reactions")
    if instructor_rows:
        data_sources.append("instructor_coaching")
    if quiz_metrics["attempts"] or quiz_metrics["feedback_responses"]:
        data_sources.append("knowledge_checks")

    aggregate = {
        "enrolled": enrolled,
        "respondents": len(respondents),
        "response_rate": response_rate,
        "clarity": clarity,
        "challenge": challenge,
        "engagement": engagement,
        "confidence": confidence,
        "overall_score": overall_score,
        "quiz_experience": quiz_experience,
        "data_sources": data_sources,
    }

    payload = {
        "course_id": course_id,
        "is_instructor": is_instructor,
        "enrolled": enrolled,
        "cohort_state": "available",
        "suppression": {
            "state": "available",
            "suppressed": False,
            "minimum_cohort_size": minimum,
            "sample_size": enrolled,
            "reason": None,
        },
        "aggregate": aggregate,
        "pulse": {
            "responses": len(pulse_rows),
            "difficulty": pulse_difficulty,
            "learning": pulse_learning,
            "unclear": sum(1 for row in pulse_rows if (row.unclear or "").strip()),
        },
        "reactions": {
            "likes": likes,
            "dislikes": dislikes,
            "like_ratio": like_ratio,
        },
        "course_checkin": {
            "responses": len(checkin_respondents),
            "clarity": clarity,
            "challenge": challenge,
            "engagement": engagement,
            "confidence": confidence,
            "survey_id": checkin_survey.id if checkin_survey else None,
            "survey_title": checkin_survey.title if checkin_survey else None,
        },
        "instructor_coaching": {
            "notes": len(instructor_rows),
            "students_coached": len({row.subject_user_id for row in instructor_rows}),
        },
        "quizzes": quiz_metrics,
        "has_data": bool(data_sources),
        "survey_opt_in": survey_opt_in,
        "can_submit_checkin": can_submit_checkin,
        "survey": (
            {
                "id": checkin_survey.id,
                "title": checkin_survey.title,
                "is_active": bool(checkin_survey.is_active),
                "questions": json.loads(checkin_survey.questions or "[]"),
            }
            if checkin_survey else None
        ),
        "prompt": (
            None if data_sources else
            "No feedback yet. A one-minute check-in starts the loop and feeds "
            "the course metrics immediately."
        ),
    }

    if is_instructor:
        pulse_by_user = {}
        for row in pulse_rows:
            pulse_by_user.setdefault(row.user_id, []).append(row)
        reactions_by_user = {row.user_id: row for row in reaction_rows}
        checkin_by_user = {row.author_id: row for row in student_rows}
        coaching_by_user = {}
        for row in instructor_rows:
            coaching_by_user.setdefault(row.subject_user_id, []).append(row)

        lab_ids = {
            row.lab_id for row in db.query(CourseLabAssignment.lab_id).filter(
                CourseLabAssignment.course_id == course_id
            ).all()
        }
        students = []
        for enrollment in db.query(CourseEnrollment).options(
            joinedload(CourseEnrollment.user)
        ).filter(
            CourseEnrollment.course_id == course_id
        ).all():
            student = enrollment.user
            if not student:
                continue
            completed = get_course_completed_lab_ids(
                db, student.id, course_id, lab_ids
            )
            latest_coaching = sorted(
                coaching_by_user.get(student.id, []),
                key=lambda row: row.updated_at or row.created_at or datetime.min,
                reverse=True,
            )
            students.append({
                "user_id": student.id,
                "name": student.display_name,
                "username": student.username,
                "enrolled_at": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
                "completed_labs": len(completed),
                "total_labs": len(lab_ids),
                "pulse_responses": len(pulse_by_user.get(student.id, [])),
                "reaction": reactions_by_user.get(student.id).reaction if reactions_by_user.get(student.id) else None,
                "survey_responded": any(row.user_id == student.id for row in survey_responses),
                "checkin": _feedback_payload(checkin_by_user[student.id]) if student.id in checkin_by_user else None,
                "coaching": _feedback_payload(latest_coaching[0]) if latest_coaching else None,
            })
        payload["students"] = students
        payload["survey_opt_in_count"] = db.query(CourseEnrollment).join(
            User, User.id == CourseEnrollment.user_id
        ).filter(
            CourseEnrollment.course_id == course_id,
            User.survey_opt_in == True,
        ).count()

        comments = []
        for row in survey_responses:
            text = _survey_answer_text(row, 4)
            if text:
                comments.append({
                    "source": "course_checkin",
                    "anonymous_label": "Anonymous student",
                    "comment": text,
                    "created_at": row.submitted_at.isoformat() if row.submitted_at else None,
                })
        for row in student_rows:
            if (row.comment or "").strip():
                comments.append({
                    "source": "course_checkin",
                    "anonymous_label": "Anonymous student",
                    "comment": row.comment.strip(),
                    "created_at": row.updated_at.isoformat() if row.updated_at else None,
                })
        for row in pulse_rows:
            if (row.unclear or "").strip():
                comments.append({
                    "source": "exercise_pulse",
                    "anonymous_label": "Anonymous student",
                    "comment": row.unclear.strip(),
                    "created_at": row.updated_at.isoformat() if row.updated_at else None,
                })
        comments.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        payload["recent_comments"] = comments[:12]
    else:
        own = db.query(CourseFeedback).filter(
            CourseFeedback.course_id == course_id,
            CourseFeedback.author_id == current_user.id,
            CourseFeedback.direction == "student_course",
        ).first()
        own_coaching = db.query(CourseFeedback).filter(
            CourseFeedback.course_id == course_id,
            CourseFeedback.subject_user_id == current_user.id,
            CourseFeedback.direction == "instructor_student",
        ).order_by(CourseFeedback.updated_at.desc()).all()
        payload["my_feedback"] = _feedback_payload(own) if own else None
        own_survey = next(
            (row for row in survey_responses if row.user_id == current_user.id),
            None,
        )
        payload["my_survey_response"] = (
            {
                "answers": json.loads(own_survey.answers or "{}"),
                "submitted_at": own_survey.submitted_at.isoformat() if own_survey.submitted_at else None,
            }
            if own_survey else None
        )
        payload["instructor_feedback_for_me"] = [
            {
                **_feedback_payload(row),
                "instructor": row.author.display_name if row.author else "Instructor",
            }
            for row in own_coaching
        ]

    return payload


@router.get("/{course_id}/feedback/me")
async def my_course_feedback(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the current user's own check-in and coaching notes."""
    course = _get_course_or_404(db, course_id)
    _, is_enrolled = _feedback_access(db, course, current_user)
    if not is_enrolled and current_user.role != "admin" and course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    own = db.query(CourseFeedback).filter(
        CourseFeedback.course_id == course_id,
        CourseFeedback.author_id == current_user.id,
        CourseFeedback.direction == "student_course",
    ).first()
    coaching = db.query(CourseFeedback).filter(
        CourseFeedback.course_id == course_id,
        CourseFeedback.subject_user_id == current_user.id,
        CourseFeedback.direction == "instructor_student",
    ).order_by(CourseFeedback.updated_at.desc()).all()
    return {
        "my_feedback": _feedback_payload(own) if own else None,
        "instructor_feedback_for_me": [
            {
                **_feedback_payload(row),
                "instructor": row.author.display_name if row.author else "Instructor",
            }
            for row in coaching
        ],
    }


@router.put("/{course_id}")
async def update_course(
    course_id: int,
    data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Update a course. Must be the instructor."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    update_data = data.model_dump(exclude_unset=True)

    if 'instructor_id' in update_data:
        if current_user.role != 'admin':
            update_data.pop('instructor_id')
        else:
            new_instructor = db.query(User).filter(User.id == update_data['instructor_id']).first()
            if not new_instructor or new_instructor.role not in ('instructor', 'admin'):
                raise HTTPException(status_code=400, detail="Selected instructor not found or does not have instructor/admin role")

    for key, value in update_data.items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course)
    return _course_response(course, db)


@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Delete a course. Must be the instructor."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)
    db.delete(course)
    db.commit()
    return {"message": "Course deleted"}


@router.post("/{course_id}/regenerate-invite")
async def regenerate_invite(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Regenerate the invite code for a course."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)
    course.invite_code = _generate_invite_code()
    db.commit()
    return {"invite_code": course.invite_code}


@router.post("/{course_id}/toggle-active")
async def toggle_course_active(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Toggle course active/inactive status."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)
    if getattr(course, 'is_archived', False):
        raise HTTPException(status_code=400, detail="Cannot toggle active status of an archived course. Unarchive first.")
    course.is_active = not course.is_active
    db.commit()
    db.refresh(course)
    return _course_response(course, db)


@router.post("/{course_id}/archive")
async def archive_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Archive a course. Sets is_archived=True and is_active=False."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)
    course.is_archived = True
    course.is_active = False
    db.commit()
    db.refresh(course)
    logger.info(f"Course {course.code} archived by {current_user.username}")
    return _course_response(course, db)


@router.post("/{course_id}/unarchive")
async def unarchive_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Unarchive a course. Sets is_archived=False but keeps is_active=False."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)
    course.is_archived = False
    db.commit()
    db.refresh(course)
    logger.info(f"Course {course.code} unarchived by {current_user.username}")
    return _course_response(course, db)


# ==================== Enrollment ====================

@router.post("/join")
async def join_course(
    data: CourseJoinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Join a course via invite code."""
    # Match case-insensitively: invite codes are generated with mixed case, and
    # users often retype or paste them in the wrong case.
    course = db.query(Course).filter(
        func.upper(Course.invite_code) == data.invite_code.upper(),
        Course.is_active == True,
        Course.is_archived == False,
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Invalid invite code or course is not active")

    now = datetime.now(timezone.utc)
    end = course.end_date
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    if now > end:
        raise HTTPException(status_code=403, detail="This course has ended")

    existing = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course.id,
        CourseEnrollment.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")

    enrollment = CourseEnrollment(
        course_id=course.id,
        user_id=current_user.id,
    )
    db.add(enrollment)
    db.flush()  # so _ensure_scope_token can see the row
    _ensure_scope_token(db, enrollment)
    db.commit()
    logger.info(f"User {current_user.username} enrolled in {course.code}")

    log_activity(db, EventTypes.COURSE_ENROLLED,
                  actor_id=current_user.id, target_type="course",
                  target_id=course.id, target_label=course.code)

    return {"message": f"Enrolled in {course.code}", "course_id": course.id}


@router.post("/{course_id}/enroll-bulk")
async def enroll_students_bulk(
    course_id: int,
    data: BulkEnrollRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Admin bulk-enrolls multiple students in a course."""
    course = _get_course_or_404(db, course_id)

    if not data.user_ids:
        raise HTTPException(status_code=400, detail="No user IDs provided")

    already_enrolled = {
        e.user_id for e in db.query(CourseEnrollment.user_id).filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id.in_(data.user_ids),
        ).all()
    }

    students = db.query(User).filter(
        User.id.in_(data.user_ids),
        User.role == "student",
        User.is_active == True,
    ).all()
    valid_ids = {s.id for s in students}

    enrolled = []
    skipped = []
    new_enrollments = []
    for uid in data.user_ids:
        if uid not in valid_ids:
            skipped.append({"user_id": uid, "reason": "not found or not an active student"})
        elif uid in already_enrolled:
            skipped.append({"user_id": uid, "reason": "already enrolled"})
        else:
            ce = CourseEnrollment(course_id=course_id, user_id=uid)
            db.add(ce)
            new_enrollments.append(ce)
            enrolled.append(uid)

    if enrolled:
        db.flush()
        for ce in new_enrollments:
            _ensure_scope_token(db, ce)
        db.commit()
        for uid in enrolled:
            log_activity(db, EventTypes.COURSE_ENROLLED,
                         actor_id=uid, target_type="course",
                         target_id=course_id, target_label=course.code)

    return {
        "enrolled_count": len(enrolled),
        "skipped_count": len(skipped),
        "skipped": skipped,
        "consent_required": [s.id for s in students if s.id in enrolled and getattr(s, "is_minor", False)],
    }


@router.delete("/{course_id}/enroll/{user_id}")
async def remove_student(
    course_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Remove a student from a course."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == user_id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not enrolled")

    db.delete(enrollment)
    db.commit()
    return {"message": "Student removed from course"}


@router.get("/{course_id}/students")
async def list_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """List enrolled students."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    enrollments = db.query(CourseEnrollment).options(
        joinedload(CourseEnrollment.user)
    ).filter(
        CourseEnrollment.course_id == course_id,
    ).all()

    students = []
    user_ids = [e.user_id for e in enrollments if e.user]
    records = {
        row.user_id: row
        for row in db.query(UserAccommodation)
        .filter(UserAccommodation.user_id.in_(user_ids))
        .all()
    } if user_ids else {}
    for e in enrollments:
        u = e.user
        record = records.get(u.id)
        students.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "student_id": u.student_id,
            "enrolled_at": e.enrolled_at,
            "is_minor": bool(getattr(u, "is_minor", False)),
            "consent_recorded": bool(e.consent_recorded_at),
            "consent_recorded_at": e.consent_recorded_at,
            "consent_reference": e.consent_reference,
            "time_multiplier": float(record.time_multiplier) if record else 1.0,
            "due_date_extension_days": int(record.due_date_extension_days or 0) if record else 0,
        })
    return {"students": students}


@router.put("/{course_id}/students/{user_id}/consent")
async def record_minor_consent(
    course_id: int,
    user_id: int,
    data: MinorConsentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Record the institution's parental/guardian consent reference for a minor."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    student = db.query(User).filter(User.id == user_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    if not getattr(student, "is_minor", False):
        raise HTTPException(
            status_code=400,
            detail="Consent references are only recorded for minor accounts.",
        )
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == user_id,
    ).first()
    if enrollment is None:
        raise HTTPException(
            status_code=404, detail="Learner is not enrolled in this course"
        )

    reference = data.reference.strip()
    if len(reference) < 3:
        raise HTTPException(status_code=400, detail="A consent reference is required.")
    enrollment.consent_reference = reference
    enrollment.consent_recorded_at = datetime.now(timezone.utc)
    enrollment.consent_recorded_by_id = current_user.id
    log_activity(
        db,
        EventTypes.MINOR_CONSENT_RECORDED,
        actor_id=current_user.id,
        target_type="user",
        target_id=student.id,
        target_label=student.username,
        detail={"course_id": course_id, "consent": "recorded"},
        commit=False,
    )
    db.commit()
    return {
        "user_id": student.id,
        "consent_recorded": True,
        "consent_recorded_at": enrollment.consent_recorded_at,
        "consent_reference": enrollment.consent_reference,
    }


# ==================== Lab Assignment ====================

@router.post("/{course_id}/labs")
async def assign_labs(
    course_id: int,
    data: CourseLabAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Assign labs to a course."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    # Get existing assignments
    existing_lab_ids = {
        a.lab_id for a in db.query(CourseLabAssignment).filter(
            CourseLabAssignment.course_id == course_id
        ).all()
    }

    # Get max sort_order
    max_order = db.query(func.max(CourseLabAssignment.sort_order)).filter(
        CourseLabAssignment.course_id == course_id
    ).scalar() or 0

    added = 0
    for lab_id in data.lab_ids:
        if lab_id in existing_lab_ids:
            continue
        lab = db.query(Lab).filter(Lab.id == lab_id).first()
        if not lab:
            continue
        max_order += 1
        db.add(CourseLabAssignment(
            course_id=course_id,
            lab_id=lab_id,
            sort_order=max_order,
        ))
        added += 1

    db.commit()
    rebuild_course_wiki(db, course)
    return {"message": f"{added} lab(s) assigned"}


@router.post(
    "/{course_id}/labs/bulk-remove",
    summary="Remove several exercises from a course",
    response_description="Number of assignments removed",
)
async def bulk_remove_labs(
    course_id: int,
    data: CourseLabBulkRemoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Remove multiple exercises from a course in one request.

    Used by the instructor panel's multi-select action. Labs that are not
    assigned to the course are ignored so a stale selection cannot fail the
    whole batch.
    """
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    assignments = db.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course_id,
        CourseLabAssignment.lab_id.in_(data.lab_ids),
    ).all()
    removed = 0
    for assignment in assignments:
        db.delete(assignment)
        removed += 1

    db.commit()
    rebuild_course_wiki(db, course)
    return {
        "message": f"{removed} lab(s) removed",
        "removed": removed,
        "requested": len(data.lab_ids),
    }


@router.delete("/{course_id}/labs/{lab_id}")
async def remove_lab(
    course_id: int,
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Remove a lab from a course."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    assignment = db.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course_id,
        CourseLabAssignment.lab_id == lab_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Lab not assigned to this course")

    db.delete(assignment)
    db.commit()
    rebuild_course_wiki(db, course)
    return {"message": "Lab removed from course"}


@router.put("/{course_id}/labs/reorder")
async def reorder_labs(
    course_id: int,
    data: CourseLabReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Reorder labs in a course."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    for item in data.lab_order:
        assignment = db.query(CourseLabAssignment).filter(
            CourseLabAssignment.course_id == course_id,
            CourseLabAssignment.lab_id == item["lab_id"],
        ).first()
        if assignment:
            assignment.sort_order = item["sort_order"]

    db.commit()
    rebuild_course_wiki(db, course)
    return {"message": "Lab order updated"}


@router.put("/{course_id}/labs/{lab_id}")
async def update_course_lab(
    course_id: int,
    lab_id: int,
    data: CourseLabUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Update a course lab assignment (e.g. display_name). Instructor only."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    assignment = db.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course_id,
        CourseLabAssignment.lab_id == lab_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Lab not assigned to this course")

    if data.display_name is not None:
        # Empty string means reset to original lab name
        assignment.display_name = data.display_name if data.display_name.strip() else None

    db.commit()
    return {
        "message": "Course lab updated",
        "display_name": assignment.display_name,
        "lab_name": assignment.lab.name if assignment.lab else None,
    }


# ==================== Scoreboard ====================

@router.get("/{course_id}/scoreboard")
async def get_scoreboard(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get course scoreboard. Must be enrolled or instructor."""
    course = _get_course_or_404(db, course_id)

    # Check access: enrolled, admin, or course owner
    is_enrolled = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == current_user.id,
    ).first() is not None
    is_instructor = (current_user.role == 'admin') or (course.instructor_id == current_user.id)

    if not is_enrolled and not is_instructor:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    # Get assigned labs
    assignments = db.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course_id,
    ).order_by(CourseLabAssignment.sort_order).all()

    labs = []
    lab_map = {}
    for a in assignments:
        lab = a.lab
        if lab:
            labs.append({"id": lab.id, "name": a.display_name or lab.name, "slug": lab.slug})
            lab_map[lab.id] = lab

    # Get enrolled students
    enrollments = db.query(CourseEnrollment).options(
        joinedload(CourseEnrollment.user)
    ).filter(
        CourseEnrollment.course_id == course_id,
    ).all()

    # Get all completions for enrolled users + assigned labs
    enrolled_user_ids = [e.user_id for e in enrollments]
    assigned_lab_ids_set = set(lab_map.keys())

    completions_raw = {}
    if enrolled_user_ids and assigned_lab_ids_set:
        rows = db.query(LabCompletion).filter(
            LabCompletion.user_id.in_(enrolled_user_ids),
            LabCompletion.lab_id.in_(assigned_lab_ids_set),
        ).all()
        for c in rows:
            completions_raw[(c.user_id, c.lab_id)] = c

    # Build enrollment map and reset map for course-aware filtering
    enrollment_map = {e.user_id: e.enrolled_at for e in enrollments}
    reset_map = {}  # (user_id, lab_id) -> latest reset_at
    if enrolled_user_ids:
        resets = db.query(CourseCompletionReset).filter(
            CourseCompletionReset.course_id == course_id,
            CourseCompletionReset.user_id.in_(enrolled_user_ids),
        ).all()
        for r in resets:
            key = (r.user_id, r.lab_id)
            if key not in reset_map or r.reset_at > reset_map[key]:
                reset_map[key] = r.reset_at

    def _is_valid_in_course(c: LabCompletion, uid: int) -> bool:
        """Check if a completion counts within this course."""
        if not c or not c.flag_submitted or not c.completed_at:
            return False
        enrolled_at = enrollment_map.get(uid)
        if not enrolled_at or c.completed_at < enrolled_at:
            return False
        latest_reset = reset_map.get((uid, c.lab_id))
        if latest_reset and c.completed_at <= latest_reset:
            return False
        return True

    # Filter completions to only course-valid ones
    completions = {}
    for key, c in completions_raw.items():
        if _is_valid_in_course(c, key[0]):
            completions[key] = c

    # Compute per-lab first blood from course-valid completions
    first_blood_map = {}  # lab_id -> user_id (earliest valid completer)
    for (uid, lid), c in completions.items():
        if lid not in first_blood_map or c.completed_at < completions[(first_blood_map[lid], lid)].completed_at:
            first_blood_map[lid] = uid

    # Get achievements for this course (both aggregate and per-lab)
    user_achievements = {}       # user_id -> [achievement_type, ...]
    user_lab_achievements = {}   # (user_id, lab_id) -> [achievement_type, ...]
    if enrolled_user_ids:
        ach_rows = db.query(Achievement).filter(
            Achievement.course_id == course_id,
            Achievement.user_id.in_(enrolled_user_ids),
        ).all()
        for a in ach_rows:
            user_achievements.setdefault(a.user_id, []).append(a.achievement_type)
            if a.lab_id is not None:
                user_lab_achievements.setdefault((a.user_id, a.lab_id), []).append(a.achievement_type)

    # Build scoreboard entries
    entries = []
    for enrollment in enrollments:
        user = enrollment.user
        total_score = 0
        labs_completed = 0
        lab_scores = {}

        for lab_id, lab in lab_map.items():
            completion = completions.get((user.id, lab_id))
            score = calculate_lab_score(
                completion, lab, course_id, db,
                first_blood_user_id=first_blood_map.get(lab_id),
            )
            total_score += score

            completed = completion is not None
            if completed:
                labs_completed += 1

            lab_scores[str(lab_id)] = {
                "score": score,
                "completed": completed,
                "time_minutes": completion.time_spent_minutes if completion else None,
                "attempts": completion.attempts if completion else 0,
                "hints_used": completion.hints_used if completion else 0,
                "achievements": user_lab_achievements.get((user.id, lab_id), []),
            }

        entries.append({
            "user_id": user.id,
            "username": user.username,
            "student_id": user.student_id,
            "total_score": total_score,
            "labs_completed": labs_completed,
            "achievements": list(set(user_achievements.get(user.id, []))),
            "lab_scores": lab_scores,
        })

    # Sort by total_score descending, then by labs_completed
    entries.sort(key=lambda e: (-e["total_score"], -e["labs_completed"]))

    # Add ranks
    for i, entry in enumerate(entries):
        entry["rank"] = i + 1

    return {
        "course": {"id": course.id, "name": course.name, "code": course.code},
        "labs": labs,
        "scoreboard": entries,
    }


# ==================== Achievements ====================

@router.get("/{course_id}/achievements")
async def list_achievements(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all achievements in a course."""
    course = _get_course_or_404(db, course_id)

    is_enrolled = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == current_user.id,
    ).first() is not None
    is_instructor = (current_user.role == 'admin') or (course.instructor_id == current_user.id)

    if not is_enrolled and not is_instructor:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    achievements = db.query(Achievement).options(
        joinedload(Achievement.user),
        joinedload(Achievement.lab),
    ).filter(
        Achievement.course_id == course_id,
    ).order_by(Achievement.awarded_at.desc()).all()

    # Build display_name map for course labs
    cla_rows = db.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course_id
    ).all()
    dn_map = {r.lab_id: r.display_name for r in cla_rows}

    result = []
    for a in achievements:
        lab_name = None
        if a.lab:
            lab_name = dn_map.get(a.lab_id) or a.lab.name
        result.append({
            "id": a.id,
            "user_id": a.user_id,
            "username": a.user.username if a.user else None,
            "achievement_type": a.achievement_type,
            "label": resolve_achievement_label(db, a.achievement_type),
            "lab_id": a.lab_id,
            "lab_name": lab_name,
            "awarded_at": a.awarded_at,
        })

    custom_rows = db.query(CustomAchievement).order_by(CustomAchievement.id).all()
    custom_definitions = {
        f"custom_{row.id}": {
            "label": row.name,
            "icon": row.icon or "\U0001F3C5",
            "description": row.description or "",
            "trigger": row.trigger,
            "threshold": row.threshold,
            "is_active": row.is_active,
        }
        for row in custom_rows
    }

    return {
        "achievements": result,
        "custom_achievements": custom_definitions,
    }


# ==================== Completion Reset ====================

@router.post("/{course_id}/labs/{lab_id}/reset/{user_id}")
async def reset_student_lab(
    course_id: int,
    lab_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Reset a student's lab completion within this course (admin only)."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    # Verify student is enrolled
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == user_id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course")

    # Verify lab is assigned
    assignment = db.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course_id,
        CourseLabAssignment.lab_id == lab_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Lab not assigned in this course")

    # Insert reset record
    db.add(CourseCompletionReset(
        course_id=course_id,
        user_id=user_id,
        lab_id=lab_id,
        reset_by=current_user.id,
    ))

    # Delete lab-specific achievements for this student+course+lab
    db.query(Achievement).filter(
        Achievement.course_id == course_id,
        Achievement.user_id == user_id,
        Achievement.lab_id == lab_id,
    ).delete()

    # Delete course-wide achievements (clean_sweep, streak) that may be invalidated
    db.query(Achievement).filter(
        Achievement.course_id == course_id,
        Achievement.user_id == user_id,
        Achievement.lab_id.is_(None),
    ).delete()

    db.commit()

    student = db.query(User).filter(User.id == user_id).first()
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    log_activity(db, EventTypes.ACHIEVEMENT_AWARDED,
                 actor_id=current_user.id, target_type="reset",
                 target_id=lab_id,
                 target_label=f"Reset {student.username if student else user_id} on {lab.name if lab else lab_id}",
                 commit=True)

    logger.info(f"Reset lab {lab_id} for user {user_id} in course {course_id} by {current_user.username}")
    return {"detail": "Lab completion reset for this course"}


# ==================== PDF Reports ====================

@router.get("/{course_id}/report")
async def class_report(
    course_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Generate PDF report for entire class."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    from app.services.pdf_report import generate_class_report

    course_dict = _build_course_dict(course)
    students_data = _build_all_students_data(db, course)

    report_id = str(uuid.uuid4())
    pdf_bytes = generate_class_report(
        course_dict,
        students_data,
        current_user.timezone,
        report_id=report_id,
    )
    safe_code = re.sub(r"[^A-Za-z0-9_.-]", "_", course.code or "course")[:80]
    filename = f"report_{safe_code}_student-record-pack_{report_id}.pdf"
    manifest = record_report(
        db,
        report_id=report_id,
        course_id=course_id,
        report_type="student-record-pack",
        file_format="pdf",
        filename=filename,
        data=bytes(pdf_bytes),
        generated_by=current_user.id,
    )
    log_admin_action(
        action=AuditActions.REPORT_EXPORTED,
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        target_type="course_report",
        target_id=course_id,
        details={
            "format": "pdf",
            "scope": "class",
            "report": "student-record-pack",
            "report_id": report_id,
            "sha256": manifest.sha256,
            "reason": reason,
        },
        ip_address=request.client.host if request.client else None,
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
            "X-Report-Id": report_id,
            "X-Report-Sha256": manifest.sha256,
            "X-Report-Filename": filename,
            "Access-Control-Expose-Headers": (
                "Content-Disposition, X-Report-Id, X-Report-Sha256, X-Report-Filename"
            ),
        },
    )


@router.get("/{course_id}/report/{user_id}")
async def student_report(
    course_id: int,
    user_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Generate PDF report for a single student."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    # Verify student is enrolled
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == user_id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course")

    student = db.query(User).filter(User.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="User not found")
    if getattr(student, "is_minor", False):
        raise HTTPException(
            status_code=403,
            detail=(
                "This learner is excluded from reporting by an under-18 "
                "privacy setting."
            ),
        )

    from app.services.pdf_report import generate_student_report

    course_dict = _build_course_dict(course)
    lab_scores, achievements = _build_student_scores(db, course, student)
    student_dict = {
        "username": student.username,
        "student_id": student.student_id,
        "email": student.email,
    }

    pdf_bytes = generate_student_report(student_dict, course_dict, lab_scores, achievements, current_user.timezone)
    log_admin_action(
        action=AuditActions.REPORT_EXPORTED,
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        target_type="student_report",
        target_id=user_id,
        details={
            "format": "pdf",
            "course_id": course_id,
            "reason": reason,
        },
        ip_address=request.client.host if request.client else None,
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{course.code}_{student.username}.pdf"
        },
    )


# ==================== Report Helpers ====================

def _build_course_dict(course: Course) -> dict:
    return {
        "name": course.name,
        "code": course.code,
        "semester": course.semester,
        "instructor_name": course.instructor.username if course.instructor else "N/A",
        "start_date": course.start_date,
        "end_date": course.end_date,
    }


def _build_student_scores(
    db: Session, course: Course, student: User
) -> tuple:
    """Build lab scores and achievements for a student in a course."""
    assignments = db.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course.id,
    ).order_by(CourseLabAssignment.sort_order).all()

    # Build display_name map for course labs
    dn_map = {a.lab_id: a.display_name for a in assignments}
    # Pre-compute course-valid completions for this student
    assigned_lab_ids = {a.lab_id for a in assignments}
    valid_completed_ids = get_course_completed_lab_ids(
        db, student.id, course.id, assigned_lab_ids,
    )

    lab_scores = []
    for a in assignments:
        lab = a.lab
        if not lab:
            continue

        completion = db.query(LabCompletion).filter(
            LabCompletion.user_id == student.id,
            LabCompletion.lab_id == lab.id,
        ).first()

        has_flag = (completion and completion.flag_submitted
                    and completion.flag_submitted != ""
                    and lab.id in valid_completed_ids)

        score = calculate_lab_score(completion if has_flag else None, lab, course.id, db) if has_flag else 0

        lab_scores.append({
            "lab_id": lab.id,
            "lab_name": a.display_name or lab.name,
            "chapter_id": lab.chapter_id,
            "chapter_name": lab.chapter_name,
            "chapter_label": chapter_label(lab.chapter_id),
            "primary_competency": lab.primary_competency,
            "framework_refs": lab.framework_refs_list,
            "measurable_outcome": lab.measurable_outcome,
            "score": score,
            "max_score": 250,
            "attempts": completion.attempts if has_flag else 0,
            "hints_used": completion.hints_used if has_flag else 0,
            "time_minutes": completion.time_spent_minutes if has_flag else None,
            "completed_at": completion.completed_at if has_flag else None,
        })

    # Achievements
    ach_rows = db.query(Achievement).options(
        joinedload(Achievement.lab)
    ).filter(
        Achievement.course_id == course.id,
        Achievement.user_id == student.id,
    ).all()

    achievements = []
    for a in ach_rows:
        achievements.append({
            "type": a.achievement_type,
            "label": resolve_achievement_label(db, a.achievement_type),
            "lab_name": (dn_map.get(a.lab_id) or a.lab.name) if a.lab else None,
        })

    return lab_scores, achievements


def _build_all_students_data(db: Session, course: Course) -> list:
    """Build report data for all enrolled students."""
    enrollments = db.query(CourseEnrollment).options(
        joinedload(CourseEnrollment.user)
    ).filter(
        CourseEnrollment.course_id == course.id,
    ).all()

    students_data = []
    for e in enrollments:
        student = e.user
        if student is None or getattr(student, "is_minor", False):
            continue
        lab_scores, achievements = _build_student_scores(db, course, student)
        students_data.append({
            "student": {
                "username": student.username,
                "student_id": student.student_id,
                "email": student.email,
            },
            "lab_scores": lab_scores,
            "achievements": achievements,
        })

    # Sort by username
    students_data.sort(key=lambda s: s["student"]["username"])
    return students_data


# ==================== Assignment CRUD ====================

@router.get("/{course_id}/assignments")
async def list_assignments(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List assignments for a course with labs and completion stats."""
    course = _get_course_or_404(db, course_id)

    is_instructor = (current_user.role == 'admin') or (course.instructor_id == current_user.id)
    is_enrolled = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == current_user.id,
    ).first() is not None

    if not is_instructor and not is_enrolled:
        raise HTTPException(status_code=403, detail="Not authorized")

    assignments = db.query(Assignment).filter(
        Assignment.course_id == course_id,
    ).order_by(Assignment.sort_order, Assignment.created_at).all()

    course_lab_rows = db.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course_id
    ).all()
    assigned_lab_ids = {a.lab_id for a in course_lab_rows}
    display_name_map = {a.lab_id: a.display_name for a in course_lab_rows}

    completed_ids = set()
    if not is_instructor:
        completed_ids = get_course_completed_lab_ids(
            db, current_user.id, course_id, assigned_lab_ids
        )

    extension_days = 0
    if not is_instructor:
        extension_days = accommodations.extension_days(db, current_user.id)

    result = []
    for asn in assignments:
        effective_due = asn.due_date
        if effective_due is not None and extension_days:
            effective_due = effective_due + timedelta(days=extension_days)
        labs = []
        for al in asn.assignment_labs:
            lab = al.lab
            if not lab:
                continue
            lab_display = display_name_map.get(lab.id)
            labs.append({
                "id": lab.id,
                "name": lab_display or lab.name,
                "slug": lab.slug,
                "difficulty": lab.difficulty,
                "category": lab.category,
                "duration_minutes": lab.duration_minutes,
                "is_completed": lab.id in completed_ids,
                "sort_order": al.sort_order,
                "track_slug": lab.level.track.slug if lab.level and lab.level.track else None,
                "track_name": lab.level.track.name if lab.level and lab.level.track else "Course Assessments",
                "level_name": lab.level.name if lab.level else "Assessments",
                "chapter_id": lab.chapter_id,
                "chapter_name": lab.chapter_name,
                "chapter_label": chapter_label(lab.chapter_id),
                "primary_competency": lab.primary_competency,
                "framework_refs": lab.framework_refs_list,
                "measurable_outcome": lab.measurable_outcome,
            })
        # Determine if assignment is locked:
        #   1. Manually locked by instructor (asn.locked field), OR
        #   2. start_date is in the future (not yet open)
        is_locked = bool(asn.locked)
        not_yet_open = False
        if asn.start_date:
            start_dt = asn.start_date
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=timezone.utc)
            if start_dt > datetime.now(timezone.utc):
                not_yet_open = True

        # Determine due date status
        is_ended = False
        if effective_due:
            due_dt = effective_due
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=timezone.utc)
            if due_dt < datetime.now(timezone.utc):
                is_ended = True

        # Students can see assignment info but not exercise details when locked/not open
        hide_content = (is_locked or not_yet_open) and not is_instructor

        result.append({
            "id": asn.id,
            "name": asn.name,
            "description": asn.description,
            "due_date": asn.due_date,
            "effective_due_date": effective_due,
            "accommodation_extension_days": extension_days,
            "start_date": asn.start_date,
            "sort_order": asn.sort_order,
            "created_at": asn.created_at,
            "locked": is_locked,
            "not_yet_open": not_yet_open,
            "is_ended": is_ended,
            "lab_count": len(labs),
            "completed_count": 0 if hide_content else sum(1 for l in labs if l["is_completed"]),
            "labs": [] if hide_content else labs,
        })

    return {"assignments": result}


@router.post("/{course_id}/assignments", status_code=201)
async def create_assignment(
    course_id: int,
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Create a new assignment within a course."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    if data.start_date and data.due_date and data.due_date < data.start_date:
        raise HTTPException(status_code=400, detail="Due date cannot be before the availability date")

    max_order = db.query(func.max(Assignment.sort_order)).filter(
        Assignment.course_id == course_id
    ).scalar() or 0

    assignment = Assignment(
        course_id=course_id,
        name=data.name,
        description=data.description,
        due_date=data.due_date,
        start_date=data.start_date,
        locked=data.locked or False,
        sort_order=max_order + 1,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "id": assignment.id,
        "name": assignment.name,
        "description": assignment.description,
        "due_date": assignment.due_date,
        "start_date": assignment.start_date,
        "sort_order": assignment.sort_order,
        "created_at": assignment.created_at,
        "lab_count": 0,
        "completed_count": 0,
        "labs": [],
        "locked": assignment.locked,
        "not_yet_open": False,
        "is_ended": False,
    }


@router.put("/{course_id}/assignments/reorder")
async def reorder_assignments(
    course_id: int,
    data: AssignmentReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Reorder assignments in a course."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    for item in data.assignment_order:
        asn = db.query(Assignment).filter(
            Assignment.course_id == course_id,
            Assignment.id == item["id"],
        ).first()
        if asn:
            asn.sort_order = item["sort_order"]

    db.commit()
    return {"message": "Assignment order updated"}


@router.put("/{course_id}/assignments/{assignment_id}")
async def update_assignment(
    course_id: int,
    assignment_id: int,
    data: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Update an assignment's name, description, or due date."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.course_id == course_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if data.name is not None:
        assignment.name = data.name
    if data.description is not None:
        assignment.description = data.description
    if data.due_date is not None:
        assignment.due_date = data.due_date
    if data.start_date is not None:
        assignment.start_date = data.start_date
    if data.locked is not None:
        assignment.locked = data.locked

    # Validate: due date must not be before start date
    effective_start = assignment.start_date
    effective_due = assignment.due_date
    if effective_start and effective_due and effective_due < effective_start:
        db.rollback()
        raise HTTPException(status_code=400, detail="Due date cannot be before the availability date")

    db.commit()
    return {"message": "Assignment updated", "locked": assignment.locked}


@router.delete("/{course_id}/assignments/{assignment_id}")
async def delete_assignment(
    course_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Delete an assignment (labs remain assigned to the course)."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.course_id == course_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted"}


# ==================== Assignment Lab Management ====================

@router.post("/{course_id}/assignments/{assignment_id}/labs")
async def add_labs_to_assignment(
    course_id: int,
    assignment_id: int,
    data: AssignmentLabsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Add labs to an assignment. Auto-assigns labs to the course if needed."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.course_id == course_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course_lab_ids = {a.lab_id for a in db.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course_id
    ).all()}

    existing = {al.lab_id for al in db.query(AssignmentLab).filter(
        AssignmentLab.assignment_id == assignment_id
    ).all()}

    max_order = db.query(func.max(AssignmentLab.sort_order)).filter(
        AssignmentLab.assignment_id == assignment_id
    ).scalar() or 0

    # Max sort_order for course lab assignments (for auto-assign)
    max_cla_order = db.query(func.coalesce(func.max(CourseLabAssignment.sort_order), 0)).filter(
        CourseLabAssignment.course_id == course_id
    ).scalar()

    added = 0
    for lab_id in data.lab_ids:
        # Auto-assign lab to course if not already there
        if lab_id not in course_lab_ids:
            max_cla_order += 1
            db.add(CourseLabAssignment(
                course_id=course_id,
                lab_id=lab_id,
                sort_order=max_cla_order,
            ))
            course_lab_ids.add(lab_id)
        if lab_id in existing:
            continue
        max_order += 1
        db.add(AssignmentLab(
            assignment_id=assignment_id,
            lab_id=lab_id,
            sort_order=max_order,
        ))
        added += 1

    db.commit()
    return {"message": f"{added} lab(s) added to assignment"}


@router.delete("/{course_id}/assignments/{assignment_id}/labs/{lab_id}")
async def remove_lab_from_assignment(
    course_id: int,
    assignment_id: int,
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Remove a lab from an assignment (lab stays assigned to the course)."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    # Scope the assignment to THIS course. Without this, an instructor who owns
    # any course could pass a foreign assignment_id and delete a lab from
    # another instructor's assignment.
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.course_id == course_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found in this course")

    al = db.query(AssignmentLab).filter(
        AssignmentLab.assignment_id == assignment_id,
        AssignmentLab.lab_id == lab_id,
    ).first()
    if not al:
        raise HTTPException(status_code=404, detail="Lab not in this assignment")

    db.delete(al)
    db.commit()
    return {"message": "Lab removed from assignment"}



# ==================== Assignment Reports ====================

@router.get("/{course_id}/assignments/{assignment_id}/report")
async def assignment_class_report(
    course_id: int,
    assignment_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Generate PDF class report scoped to a specific assignment."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.course_id == course_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment_lab_ids = {al.lab_id for al in db.query(AssignmentLab).filter(
        AssignmentLab.assignment_id == assignment_id
    ).all()}

    from app.services.pdf_report import generate_class_report

    course_dict = _build_course_dict(course)
    course_dict["name"] = f"{course.name} - {assignment.name}"

    all_data = _build_all_students_data(db, course)
    for entry in all_data:
        entry["lab_scores"] = [
            s for s in entry["lab_scores"] if s.get("lab_id") in assignment_lab_ids
        ]

    pdf_bytes = generate_class_report(course_dict, all_data, current_user.timezone)
    safe_name = assignment.name.replace(" ", "_")[:30]
    log_admin_action(
        action=AuditActions.REPORT_EXPORTED,
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        target_type="assignment_report",
        target_id=assignment_id,
        details={
            "format": "pdf",
            "course_id": course_id,
            "scope": "class",
            "reason": reason,
        },
        ip_address=request.client.host if request.client else None,
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{course.code}_{safe_name}.pdf"
        },
    )


@router.get("/{course_id}/assignments/{assignment_id}/report/{user_id}")
async def assignment_student_report(
    course_id: int,
    assignment_id: int,
    user_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Generate PDF student report scoped to a specific assignment."""
    course = _get_course_or_404(db, course_id)
    _require_instructor(course, current_user)

    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.course_id == course_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == user_id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course")

    student = db.query(User).filter(User.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="User not found")
    if getattr(student, "is_minor", False):
        raise HTTPException(
            status_code=403,
            detail=(
                "This learner is excluded from reporting by an under-18 "
                "privacy setting."
            ),
        )

    assignment_lab_ids = {al.lab_id for al in db.query(AssignmentLab).filter(
        AssignmentLab.assignment_id == assignment_id
    ).all()}

    from app.services.pdf_report import generate_student_report

    course_dict = _build_course_dict(course)
    course_dict["name"] = f"{course.name} - {assignment.name}"

    lab_scores, achievements = _build_student_scores(db, course, student)
    lab_scores = [s for s in lab_scores if s.get("lab_id") in assignment_lab_ids]

    student_dict = {
        "username": student.username,
        "student_id": student.student_id,
        "email": student.email,
    }
    pdf_bytes = generate_student_report(student_dict, course_dict, lab_scores, achievements, current_user.timezone)
    safe_name = assignment.name.replace(" ", "_")[:30]
    log_admin_action(
        action=AuditActions.REPORT_EXPORTED,
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        target_type="assignment_report",
        target_id=assignment_id,
        details={
            "format": "pdf",
            "course_id": course_id,
            "user_id": user_id,
            "reason": reason,
        },
        ip_address=request.client.host if request.client else None,
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{course.code}_{safe_name}_{student.username}.pdf"
        },
    )


@router.get("/{course_id}/students/{user_id}/labs/{lab_id}/attempts")
async def get_student_lab_attempts(
    course_id: int,
    user_id: int,
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Every flag attempt one student made on one exercise, oldest first.

    The scoreboard shows an attempt count. A count cannot answer the questions
    that actually come up: was the first try right, how far apart were the
    tries, and what did they type. Auditing a suspicious-looking solve without
    that meant reading the database by hand.

    Restricted to the course's instructor and to admins. A student cannot read
    another student's attempts, and cannot read their own here either: the
    submitted strings for an exercise they may not have finished are in this
    payload, so enrolment is not enough.
    """
    course = _get_course_or_404(db, course_id)

    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only this course's instructor can view a student's attempts",
        )

    # The lab has to belong to this course, otherwise the course id is just a
    # doorway to any exercise in the platform.
    assigned = db.query(CourseLabAssignment.id).filter(
        CourseLabAssignment.course_id == course_id,
        CourseLabAssignment.lab_id == lab_id,
    ).first()
    if not assigned:
        raise HTTPException(status_code=404, detail="Exercise is not assigned to this course")

    enrolled = db.query(CourseEnrollment.id).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == user_id,
    ).first()
    if not enrolled:
        raise HTTPException(status_code=404, detail="Student is not enrolled in this course")

    rows = db.query(FlagAttempt).filter(
        FlagAttempt.user_id == user_id,
        FlagAttempt.lab_id == lab_id,
    ).order_by(FlagAttempt.attempted_at.asc()).all()

    attempts = []
    previous = None
    for row in rows:
        # Gap since the previous attempt. Reading timestamps and subtracting
        # them in your head is exactly the work this endpoint exists to remove.
        gap = None
        if previous is not None and row.attempted_at and previous.attempted_at:
            gap = int((row.attempted_at - previous.attempted_at).total_seconds())
        attempts.append({
            "attempted_at": row.attempted_at,
            "is_correct": bool(row.is_correct),
            "submitted": row.flag_submitted or "",
            "seconds_since_previous": gap,
        })
        previous = row

    return {
        "user_id": user_id,
        "lab_id": lab_id,
        "total": len(attempts),
        "correct": sum(1 for a in attempts if a["is_correct"]),
        "attempts": attempts,
    }
