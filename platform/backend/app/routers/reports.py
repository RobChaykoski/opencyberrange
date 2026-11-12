"""Decision-led instructor reports with verifiable manifests."""

from __future__ import annotations

import csv
import io
import re
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import mean, median

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth import get_current_instructor_user
from app.database import get_db
from app.export_reason import require_export_reason
from app.models import Course, CourseFeedback, ExerciseQuizAttempt, User
from app.ratelimit import create_limiter
from app.routers.analytics import (
    _course_context,
    _course_or_403,
    course_exercises,
    course_overview,
)
from app.services.audit import AuditActions, log_admin_action
from app.services.report_integrity import record_report, verify_report
from app.services.report_pdf import (
    generate_coaching_queue_pdf,
    generate_course_health_pdf,
    generate_exercise_diagnostics_pdf,
)
from app.services.spreadsheet_safety import neutralize_row

router = APIRouter()
limiter = create_limiter()

MAX_VERIFY_BYTES = 25 * 1024 * 1024


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", value)[:80] or "course"


def _report_catalog(course: Course) -> list[dict]:
    base = f"/courses/{course.id}/reports"
    return [
        {
            "id": "course-health",
            "group": "Understand the class",
            "title": "Course health brief",
            "description": "A one-to-two page brief with cohort completion, hint and attempt pressure, time, RAG reasons, an exercise watchlist, and one next step.",
            "use_when": "You need to decide what the teaching team should address next.",
            "privacy": "Aggregated; small cohorts are suppressed. No learner names. Learners who identify as under 18 are excluded.",
            "formats": [
                {"id": "pdf", "label": "PDF", "path": f"{base}/course-health.pdf"}
            ],
        },
        {
            "id": "exercise-diagnostics",
            "group": "Understand the class",
            "title": "Exercise diagnostics",
            "description": "Per-exercise completion, abandonment, hint pressure, attempt burden, time, RAG, and flags for content and scaffolding review, with cohort time and hint baselines.",
            "use_when": "A course or exercise is underperforming and you need the likely cause, or you need to spot completions that are far outside the cohort baseline.",
            "privacy": "Aggregated by exercise; small cells are suppressed. No learner names. Learners who identify as under 18 are excluded.",
            "formats": [
                {"id": "pdf", "label": "PDF", "path": f"{base}/exercise-diagnostics.pdf"},
                {"id": "csv", "label": "CSV", "path": f"{base}/exercise-diagnostics.csv"},
            ],
        },
        {
            "id": "coaching-queue",
            "group": "Act this week",
            "title": "Coaching queue",
            "description": "A private queue with one suggested next step and review date per learner: no activity, hint pressure, silent struggle, unusually fast hint-free completion, completion without quiz accuracy, or no coaching note.",
            "use_when": "You have limited time and need the next teaching actions for individual learners.",
            "privacy": "Individual learner identifiers; instructor-only. Not a ranking or a misconduct finding. Learners who identify as under 18 are excluded.",
            "formats": [
                {"id": "csv", "label": "CSV", "path": f"{base}/coaching-queue.csv"},
                {"id": "pdf", "label": "PDF", "path": f"{base}/coaching-queue.pdf"},
            ],
        },
        {
            "id": "student-record-pack",
            "group": "Individual records",
            "title": "Full student record pack",
            "description": "One page per learner with scores, attempt counts, hints, time, and achievements.",
            "use_when": "You need an individual record for a meeting, file, or appeal. Use the course health brief for class decisions.",
            "privacy": "Contains learner identity; instructor-only. Learners who identify as under 18 are excluded.",
            "formats": [
                {
                    "id": "pdf",
                    "label": "PDF",
                    "path": f"/courses/{course.id}/report",
                }
            ],
        },
    ]


def _audit_export(
    request: Request,
    current_user: User,
    course: Course,
    report_type: str,
    file_format: str,
    reason: str,
) -> None:
    log_admin_action(
        action=AuditActions.REPORT_EXPORTED,
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        target_type="course_report",
        target_id=course.id,
        target_identifier=course.code,
        details={
            "report": report_type,
            "format": file_format,
            "reason": reason,
        },
        ip_address=request.client.host if request.client else None,
    )


def _serve(
    db: Session,
    *,
    request: Request,
    current_user: User,
    course: Course,
    report_id: str,
    report_type: str,
    file_format: str,
    data: bytes,
    reason: str,
) -> Response:
    extension = "pdf" if file_format == "pdf" else "csv"
    filename = f"report_{_safe_name(course.code)}_{report_type}_{report_id}.{extension}"
    row = record_report(
        db,
        report_id=report_id,
        course_id=course.id,
        report_type=report_type,
        file_format=file_format,
        filename=filename,
        data=data,
        generated_by=current_user.id,
    )
    _audit_export(request, current_user, course, report_type, file_format, reason)
    media = (
        "application/pdf"
        if file_format == "pdf"
        else "text/csv; charset=utf-8"
    )
    return Response(
        content=data,
        media_type=media,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
            "X-Report-Id": report_id,
            "X-Report-Sha256": row.sha256,
            "X-Report-Filename": filename,
            "Access-Control-Expose-Headers": (
                "Content-Disposition, X-Report-Id, X-Report-Sha256, X-Report-Filename"
            ),
        },
    )


def _csv_bytes(headers: list[str], rows: list[list]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(neutralize_row(row))
    return buffer.getvalue().encode("utf-8-sig")


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _lab_baselines(completions) -> dict[int, dict]:
    """Per-exercise cohort baselines for solve time and hint usage.

    Median values are the default comparison because a single outlier should
    not move the baseline. Means are included so instructors can see skew.
    """
    grouped: dict[int, list] = defaultdict(list)
    for row in completions:
        grouped[row.lab_id].append(row)

    baselines: dict[int, dict] = {}
    for lab_id, rows in grouped.items():
        times = [row.time_spent_minutes for row in rows if row.time_spent_minutes]
        hints = [row.hints_used for row in rows if row.hints_used is not None]
        baselines[lab_id] = {
            "baseline_completions": len(rows),
            "baseline_median_time_minutes": (
                round(float(median(times)), 1) if times else None
            ),
            "baseline_mean_time_minutes": round(mean(times), 1) if times else None,
            "baseline_median_hints": (
                round(float(median(hints)), 1) if hints else None
            ),
            "baseline_mean_hints": round(mean(hints), 2) if hints else None,
            "baseline_hint_free_rate": (
                round(
                    sum(1 for row in rows if (row.hints_used or 0) == 0)
                    / len(rows)
                    * 100,
                    1,
                )
                if rows
                else None
            ),
        }
    return baselines


def _with_exercise_baselines(payload: dict, completions) -> dict:
    baselines = _lab_baselines(completions)
    for row in payload.get("exercises") or []:
        stats = baselines.get(row.get("lab_id")) or {}
        row.update(
            {
                "baseline_completions": stats.get("baseline_completions", 0),
                "baseline_median_time_minutes": stats.get(
                    "baseline_median_time_minutes"
                ),
                "baseline_mean_time_minutes": stats.get(
                    "baseline_mean_time_minutes"
                ),
                "baseline_median_hints": stats.get("baseline_median_hints"),
                "baseline_mean_hints": stats.get("baseline_mean_hints"),
                "baseline_hint_free_rate": stats.get("baseline_hint_free_rate"),
            }
        )
    return payload


def _coaching_rows(db: Session, course: Course) -> list[dict]:
    labs, user_ids, completions, sessions = _course_context(db, course)
    if not user_ids:
        return []

    users = {
        user.id: user
        for user in db.query(User).filter(User.id.in_(user_ids)).all()
    }
    by_user_completions: dict[int, list] = defaultdict(list)
    for row in completions:
        by_user_completions[row.user_id].append(row)
    by_user_sessions: dict[int, list] = defaultdict(list)
    for row in sessions:
        by_user_sessions[row.user_id].append(row)
    baselines = _lab_baselines(completions)

    quiz_rows = db.query(ExerciseQuizAttempt).filter(
        ExerciseQuizAttempt.course_id == course.id,
        ExerciseQuizAttempt.user_id.in_(user_ids),
    ).all()
    quiz_by_user: dict[int, list] = defaultdict(list)
    for row in quiz_rows:
        quiz_by_user[row.user_id].append(row)

    notes = db.query(CourseFeedback).filter(
        CourseFeedback.course_id == course.id,
        CourseFeedback.direction == "instructor_student",
        CourseFeedback.subject_user_id.in_(list(user_ids)),
    ).all()
    note_users = {
        row.subject_user_id
        for row in notes
        if _aware(row.created_at) is not None
        and _aware(row.created_at) >= datetime.now(timezone.utc) - timedelta(days=14)
    }

    now = datetime.now(timezone.utc)
    no_activity_cutoff = now - timedelta(days=7)
    assigned = len(labs)
    rows: list[dict] = []

    for user_id in user_ids:
        user = users.get(user_id)
        if user is None:
            continue
        user_completions = by_user_completions.get(user_id, [])
        user_sessions = by_user_sessions.get(user_id, [])
        if not user_completions and not user_sessions:
            last_activity = None
        else:
            marks = [
                _aware(row.completed_at) for row in user_completions
            ] + [_aware(row.started_at) for row in user_sessions]
            marks = [mark for mark in marks if mark is not None]
            last_activity = max(marks) if marks else None

        completion_rate = (
            len(user_completions) / assigned * 100 if assigned else 0
        )
        hint_free = (
            sum(1 for row in user_completions if (row.hints_used or 0) == 0)
            / len(user_completions) * 100
            if user_completions else None
        )
        first_attempt = (
            sum(1 for row in user_completions if (row.attempts or 0) == 1)
            / len(user_completions) * 100
            if user_completions else None
        )
        time_ratios = [
            row.time_spent_minutes / row.lab.duration_minutes
            for row in user_completions
            if row.time_spent_minutes and row.lab and row.lab.duration_minutes
        ]
        time_ratio = median(time_ratios) if time_ratios else None
        user_quiz = quiz_by_user.get(user_id, [])
        quiz_total = sum(row.total or 0 for row in user_quiz)
        quiz_correct = sum(row.correct or 0 for row in user_quiz)
        quiz_accuracy = (
            quiz_correct / quiz_total * 100 if quiz_total else None
        )

        signals: list[tuple[int, str, str, str]] = []
        if last_activity is None or last_activity < no_activity_cutoff:
            signals.append((
                0,
                "No activity in 7 days",
                "No course activity recorded in the last 7 days."
                if last_activity is None
                else f"Last activity {last_activity.date().isoformat()}.",
                "Check access and schedule; agree on one small next exercise.",
            ))
        if (
            len(user_completions) >= 2
            and hint_free is not None and hint_free < 50
            and first_attempt is not None and first_attempt < 50
        ):
            signals.append((
                1,
                "High hint use with low first-attempt success",
                f"{len(user_completions)} completions; hint-free {hint_free:.0f}%; first-attempt {first_attempt:.0f}%.",
                "Review the concept and add a worked example; check understanding.",
            ))
        if (
            len(user_completions) >= 2
            and time_ratio is not None and time_ratio > 1.5
            and hint_free is not None and hint_free >= 80
        ):
            signals.append((
                2,
                "Long time with few hints",
                f"Median time {time_ratio:.1f}x the estimate; hint-free {hint_free:.0f}%.",
                "Check for a silent blocker; offer a targeted hint or pair session.",
            ))
        if (
            completion_rate >= 70
            and quiz_total >= 10
            and quiz_accuracy is not None and quiz_accuracy < 60
        ):
            signals.append((
                3,
                "Completion without quiz accuracy",
                f"{len(user_completions)}/{assigned} completed; quiz accuracy {quiz_accuracy:.0f}% (n={quiz_total} questions).",
                "Ask for a short teach-back or pair review before more completion.",
            ))

        fast_completions = []
        for row in user_completions:
            stats = baselines.get(row.lab_id) or {}
            baseline_time = stats.get("baseline_median_time_minutes")
            if (
                stats.get("baseline_completions", 0) >= 3
                and baseline_time
                and row.time_spent_minutes is not None
                and row.time_spent_minutes <= baseline_time * 0.5
                and (row.hints_used or 0) == 0
            ):
                fast_completions.append((row, baseline_time))
        if len(fast_completions) >= 2:
            example, baseline_time = fast_completions[0]
            lab_name = example.lab.name if example.lab else "an exercise"
            signals.append((
                3,
                "Unusually fast, hint-free completion",
                f"{len(fast_completions)} completions at or below half the cohort "
                f"median time with no hints (e.g. {example.time_spent_minutes} min "
                f"vs {baseline_time} min on {lab_name}).",
                "Check interest and goals: ask what they want from the course and "
                "whether the material feels relevant, and offer a stretch exercise "
                "or an alternative path. This is a support conversation, not a "
                "disciplinary finding or proof of AI use.",
            ))

        if user_completions and user_id not in note_users:
            signals.append((
                4,
                "No coaching note in 14 days",
                "No instructor coaching note recorded in the last 14 days.",
                "Send a short coaching note and set a review date.",
            ))

        if not signals:
            continue
        signals.sort(key=lambda item: item[0])
        _, signal, evidence, action = signals[0]
        other = [item[1] for item in signals[1:]]
        if other:
            evidence = f"{evidence} Also: {', '.join(other)}."
        rows.append({
            "priority": signals[0][0],
            "learner": user.username,
            "student_id": user.student_id or "",
            "signal": signal,
            "evidence": evidence,
            "suggested_action": action,
            "review_date": (now + timedelta(days=7)).date().isoformat(),
            "completions": len(user_completions),
            "assigned": assigned,
            "completion_rate": round(completion_rate, 1),
            "hint_free_rate": round(hint_free, 1) if hint_free is not None else "",
            "first_attempt_rate": round(first_attempt, 1) if first_attempt is not None else "",
            "median_time_ratio": round(time_ratio, 2) if time_ratio is not None else "",
            "quiz_accuracy": round(quiz_accuracy, 1) if quiz_accuracy is not None else "",
            "quiz_questions": quiz_total,
            "fast_hint_free_completions": len(fast_completions),
        })

    rows.sort(key=lambda row: (row["priority"], row["learner"].lower()))
    return rows


@router.get("/courses/{course_id}/reports")
async def list_reports(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Return the report library for a course the caller can manage."""
    course = _course_or_403(db, course_id, current_user)
    return {"course_id": course.id, "reports": _report_catalog(course)}


@router.get("/courses/{course_id}/reports/course-health.pdf")
async def course_health_report(
    course_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    course = _course_or_403(db, course_id, current_user)
    overview = await course_overview(course_id, db, current_user)
    exercises = await course_exercises(course_id, db, current_user)
    report_id = str(uuid.uuid4())
    data = await run_in_threadpool(
        generate_course_health_pdf,
        overview,
        exercises,
        datetime.now(timezone.utc),
        report_id=report_id,
    )
    return _serve(
        db,
        request=request,
        current_user=current_user,
        course=course,
        report_id=report_id,
        report_type="course-health",
        file_format="pdf",
        data=data,
        reason=reason,
    )


@router.get("/courses/{course_id}/reports/exercise-diagnostics.pdf")
async def exercise_diagnostics_report(
    course_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    course = _course_or_403(db, course_id, current_user)
    _labs, _user_ids, completions, _sessions = _course_context(db, course)
    payload = await course_exercises(course_id, db, current_user)
    payload = _with_exercise_baselines(payload, completions)
    report_id = str(uuid.uuid4())
    data = await run_in_threadpool(
        generate_exercise_diagnostics_pdf,
        payload,
        datetime.now(timezone.utc),
        report_id=report_id,
    )
    return _serve(
        db,
        request=request,
        current_user=current_user,
        course=course,
        report_id=report_id,
        report_type="exercise-diagnostics",
        file_format="pdf",
        data=data,
        reason=reason,
    )


@router.get("/courses/{course_id}/reports/exercise-diagnostics.csv")
async def exercise_diagnostics_csv(
    course_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    course = _course_or_403(db, course_id, current_user)
    _labs, _user_ids, completions, _sessions = _course_context(db, course)
    payload = await course_exercises(course_id, db, current_user)
    payload = _with_exercise_baselines(payload, completions)
    exercises = payload.get("exercises") or []
    report_id = str(uuid.uuid4())
    headers = [
        "report_id",
        "exercise",
        "track",
        "level",
        "difficulty",
        "sample_size",
        "started_learners",
        "completed_learners",
        "completion_rate",
        "started_completion_rate",
        "abandonment_rate",
        "median_time_minutes",
        "median_attempts",
        "hint_pressure_rate",
        "first_attempt_rate",
        "rag",
        "health_status",
        "flags",
        "health_reasons",
        "baseline_completions",
        "baseline_median_time_minutes",
        "baseline_mean_time_minutes",
        "baseline_median_hints",
        "baseline_mean_hints",
        "baseline_hint_free_rate",
    ]
    rows = [
        [
            report_id,
            row.get("lab_name"),
            row.get("track_name"),
            row.get("level_name"),
            row.get("difficulty"),
            row.get("sample_size"),
            row.get("started_learners"),
            row.get("completed_learners"),
            row.get("completion_rate"),
            row.get("started_completion_rate"),
            row.get("abandonment_rate"),
            row.get("median_time_minutes"),
            row.get("median_attempts"),
            row.get("hint_pressure_rate"),
            row.get("first_attempt_rate"),
            row.get("rag"),
            row.get("health_status"),
            ", ".join(row.get("flags") or []),
            "; ".join(row.get("health_reasons") or []),
            row.get("baseline_completions"),
            row.get("baseline_median_time_minutes"),
            row.get("baseline_mean_time_minutes"),
            row.get("baseline_median_hints"),
            row.get("baseline_mean_hints"),
            row.get("baseline_hint_free_rate"),
        ]
        for row in exercises
    ]
    data = _csv_bytes(headers, rows)
    return _serve(
        db,
        request=request,
        current_user=current_user,
        course=course,
        report_id=report_id,
        report_type="exercise-diagnostics",
        file_format="csv",
        data=data,
        reason=reason,
    )


@router.get("/courses/{course_id}/reports/coaching-queue.csv")
async def coaching_queue_csv(
    course_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    course = _course_or_403(db, course_id, current_user)
    rows = _coaching_rows(db, course)
    report_id = str(uuid.uuid4())
    headers = [
        "report_id",
        "learner",
        "student_id",
        "signal",
        "evidence",
        "suggested_action",
        "review_date",
        "completions",
        "assigned",
        "completion_rate",
        "hint_free_rate",
        "first_attempt_rate",
        "median_time_ratio",
        "quiz_accuracy",
        "quiz_questions",
        "fast_hint_free_completions",
    ]
    data = _csv_bytes(
        headers,
        [[report_id] + [row.get(header) for header in headers[1:]] for row in rows],
    )
    return _serve(
        db,
        request=request,
        current_user=current_user,
        course=course,
        report_id=report_id,
        report_type="coaching-queue",
        file_format="csv",
        data=data,
        reason=reason,
    )


@router.get("/courses/{course_id}/reports/coaching-queue.pdf")
async def coaching_queue_pdf(
    course_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    course = _course_or_403(db, course_id, current_user)
    rows = _coaching_rows(db, course)
    report_id = str(uuid.uuid4())
    data = await run_in_threadpool(
        generate_coaching_queue_pdf,
        {"code": course.code, "name": course.name},
        rows[:50],
        datetime.now(timezone.utc),
        report_id=report_id,
    )
    return _serve(
        db,
        request=request,
        current_user=current_user,
        course=course,
        report_id=report_id,
        report_type="coaching-queue",
        file_format="pdf",
        data=data,
        reason=reason,
    )


@router.post("/reports/verify")
@limiter.limit("10/minute")
async def verify_report_file(
    request: Request,
    report_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Verify that a report file matches the platform manifest.

    This endpoint is intentionally public but requires both the unguessable
    report id and the file. It does not return learner data beyond the report
    metadata.
    """
    data = await file.read(MAX_VERIFY_BYTES + 1)
    if len(data) > MAX_VERIFY_BYTES:
        raise HTTPException(status_code=413, detail="Report file is too large")
    return verify_report(db, report_id.strip(), data)
