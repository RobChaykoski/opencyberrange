"""Decision-led instructor reports with verifiable manifests."""

from __future__ import annotations

import csv
import io
import re
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import mean, median

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.export_reason import require_export_reason
from app.models import (
    Course,
    CourseCompletionReset,
    CourseEnrollment,
    CourseFeedback,
    ExerciseQuizAttempt,
    FlagAttempt,
    User,
)
from app.ratelimit import create_limiter
from app.routers.analytics import (
    _course_context,
    _minimum_cohort_size,
    course_exercises,
    course_overview,
)
from app.services import gradebook, report_access
from app.services.audit import AuditActions
from app.services.export_labels import csv_with_labels
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


def _report_catalog(db: Session, course: Course, user: User) -> list[dict]:
    base = f"/courses/{course.id}/reports"
    reports = [
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
            "id": "lab-friction",
            "group": "Improve the labs",
            "title": "Lab friction report",
            "description": "Ranks assigned labs by completion from start, wrong-flag attempts per solve, hint use per solve, and median time. Flags labs where learners start but stall.",
            "use_when": "You need to decide which lab to fix, rescope, or add scaffolding to before the next cohort.",
            "privacy": "Aggregated by lab; small cells are suppressed. No learner names. Learners who identify as under 18 are excluded.",
            "formats": [
                {"id": "csv", "label": "CSV", "path": f"{base}/lab-friction.csv"}
            ],
        },
        {
            "id": "lms-gradebook",
            "group": "Individual records",
            "title": "LMS gradebook export",
            "description": "Per-learner scores and per-lab columns in Canvas, Brightspace, Moodle, or a plain CSV layout.",
            "use_when": "You need to move course scores into the institutional gradebook without retyping them.",
            "privacy": "Contains learner identity and scores; instructor-only. Learners who identify as under 18 are excluded, so import those records separately if your institution requires them.",
            "formats": [
                {
                    "id": "csv",
                    "label": "Generic CSV",
                    "path": f"{base}/lms-gradebook.csv?adapter=generic",
                },
                {
                    "id": "canvas-csv",
                    "label": "Canvas CSV",
                    "path": f"{base}/lms-gradebook.csv?adapter=canvas",
                },
                {
                    "id": "brightspace-csv",
                    "label": "Brightspace CSV",
                    "path": f"{base}/lms-gradebook.csv?adapter=brightspace",
                },
                {
                    "id": "moodle-csv",
                    "label": "Moodle CSV",
                    "path": f"{base}/lms-gradebook.csv?adapter=moodle",
                },
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
    visible = []
    for item in reports:
        if not report_access.can_view(db, course, user, item["id"]):
            continue
        policy = report_access.policy_for(item["id"])
        visible.append(
            {
                **item,
                "purpose": policy.purpose,
                "owner": policy.owner,
                "audience": policy.audience,
                "retention_days": policy.retention_days,
            }
        )
    return visible


def _analytics_actor(db: Session, course: Course, current_user: User) -> User:
    """Use an aggregate-safe actor for auditor and privacy report views.

    The report policy already authorised the caller. The analytics helpers have
    their own course-owner check, so an auditor or privacy officer borrows the
    course instructor's aggregate context rather than gaining learner-level
    analytics access elsewhere.
    """
    if current_user.role in {"auditor", "privacy_officer"}:
        instructor = (
            db.query(User).filter(User.id == course.instructor_id).first()
        )
        return instructor or current_user
    return current_user


def _report_course_or_403(
    db: Session,
    request: Request,
    course_id: int,
    current_user: User,
    report_id: str,
    *,
    export: bool,
) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    report_access.require_report_access(
        db,
        request,
        current_user,
        course,
        report_id,
        export=export,
    )
    return course


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
    policy = report_access.policy_for(report_type)
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
        expires_at=report_access.expiration(policy),
    )
    report_access.audit_access(
        db,
        request,
        current_user,
        course,
        policy,
        AuditActions.REPORT_VIEWED,
        reason=reason,
        format=file_format,
        report_id=report_id,
    )
    report_access.audit_access(
        db,
        request,
        current_user,
        course,
        policy,
        AuditActions.REPORT_EXPORTED,
        reason=reason,
        format=file_format,
        report_id=report_id,
        sha256=row.sha256,
    )
    media = (
        "application/pdf"
        if file_format == "pdf"
        else "text/csv; charset=utf-8"
    )
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store",
        "X-Report-Id": report_id,
        "X-Report-Sha256": row.sha256,
        "X-Report-Filename": filename,
        "Access-Control-Expose-Headers": (
            "Content-Disposition, X-Report-Id, X-Report-Sha256, "
            "X-Report-Filename, X-Report-Purpose, X-Report-Owner, "
            "X-Report-Audience, X-Report-Retention-Days, X-Report-Expires-At"
        ),
    }
    headers.update(report_access.export_headers(policy))
    return Response(
        content=data,
        media_type=media,
        headers=headers,
    )


def _csv_bytes(
    headers: list[str],
    rows: list[list],
    labels: list[str] | None = None,
    *,
    annotate: bool = True,
) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(neutralize_row(row))
    data = buffer.getvalue().encode("utf-8-sig")
    if labels:
        prefix = "".join(f"# {line}\n" for line in labels)
        data = ("\ufeff" + prefix + data.decode("utf-8-sig")).encode("utf-8")
    if not annotate:
        # LMS importers read the header row first. The response headers and
        # the signed manifest still carry the classification and purpose.
        return data
    return csv_with_labels(data)


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


def _friction_rows(
    db: Session,
    course: Course,
    *,
    min_starts: int = 0,
) -> list[dict]:
    """Per-lab friction metrics for a course.

    A start is a learner who opened a session. Wrong-flag attempts exclude hint
    requests, which are stored in the same table so the attempt counter can see
    them. Suppression runs after the shape is built so a small lab is visible
    as suppressed rather than silently dropped.
    """
    labs, user_ids, completions, sessions = _course_context(db, course)
    cohort_size = len(user_ids)
    lab_ids = {lab.id for lab in labs}
    if not lab_ids or not user_ids:
        return []

    enrollment_map = {
        row.user_id: row.enrolled_at
        for row in db.query(CourseEnrollment)
        .filter(CourseEnrollment.course_id == course.id)
        .all()
    }
    reset_map: dict[tuple[int, int], datetime] = {}
    for row in (
        db.query(CourseCompletionReset)
        .filter(CourseCompletionReset.course_id == course.id)
        .all()
    ):
        key = (row.user_id, row.lab_id)
        if key not in reset_map or row.reset_at > reset_map[key]:
            reset_map[key] = row.reset_at

    started: dict[int, set[int]] = defaultdict(set)
    for row in sessions:
        started[row.lab_id].add(row.user_id)

    completed: dict[int, list] = defaultdict(list)
    for row in completions:
        completed[row.lab_id].append(row)

    attempts: dict[int, list] = defaultdict(list)
    for row in (
        db.query(FlagAttempt)
        .filter(
            FlagAttempt.user_id.in_(user_ids),
            FlagAttempt.lab_id.in_(lab_ids),
        )
        .all()
    ):
        enrolled_at = enrollment_map.get(row.user_id)
        if enrolled_at and row.attempted_at and row.attempted_at < enrolled_at:
            continue
        reset = reset_map.get((row.user_id, row.lab_id))
        if reset and row.attempted_at and row.attempted_at <= reset:
            continue
        attempts[row.lab_id].append(row)

    rows: list[dict] = []
    for lab in labs:
        starter_ids = started.get(lab.id, set())
        lab_completions = completed.get(lab.id, [])
        lab_attempts = attempts.get(lab.id, [])
        # A completion or an attempt proves the learner opened the lab, even
        # when the session row was cleaned up or predates session logging.
        learners = (
            starter_ids
            | {row.user_id for row in lab_completions}
            | {row.user_id for row in lab_attempts}
        )
        hint_rows = [
            row
            for row in lab_attempts
            if (row.flag_submitted or "").upper().startswith("HINT")
        ]
        wrong_rows = [
            row
            for row in lab_attempts
            if not row.is_correct
            and not (row.flag_submitted or "").upper().startswith("HINT")
        ]
        hint_uses = len(hint_rows)
        failed_attempts = len(wrong_rows)
        starts = len(learners)
        completer_ids = {row.user_id for row in lab_completions}
        completion_count = len(completer_ids)
        completion_rate = (
            round(completion_count / starts * 100, 1) if starts else None
        )
        start_rate = (
            round(starts / cohort_size * 100, 1) if cohort_size else None
        )
        failed_per_completion = (
            round(failed_attempts / completion_count, 2)
            if completion_count
            else None
        )
        hints_per_completion = (
            round(hint_uses / completion_count, 2)
            if completion_count
            else None
        )
        times = [
            row.time_spent_minutes
            for row in lab_completions
            if row.time_spent_minutes is not None
        ]
        attempt_counts = [
            row.attempts
            for row in lab_completions
            if row.attempts is not None
        ]
        median_minutes = round(float(median(times)), 1) if times else None
        median_attempts = (
            round(float(median(attempt_counts)), 1) if attempt_counts else None
        )
        sample_size = len(learners)

        flags: list[str] = []
        if starts == 0:
            flags.append("No starts")
        elif completion_rate is not None and completion_rate < 50:
            flags.append("Low completion from start")
        if completion_count and failed_per_completion is not None and failed_per_completion >= 2:
            flags.append("Repeated wrong flags")
        if completion_count and hints_per_completion is not None and hints_per_completion >= 1.5:
            flags.append("High hint use")
        if (
            median_minutes is not None
            and lab.duration_minutes
            and median_minutes > lab.duration_minutes * 1.5
        ):
            flags.append("Slow for its estimate")

        level = getattr(lab, "level", None)
        track = getattr(level, "track", None)
        rows.append(
            {
                "lab_id": lab.id,
                "lab_name": lab.name,
                "slug": lab.slug,
                "track_name": getattr(track, "name", "") or "",
                "level_name": getattr(level, "name", "") or "",
                "difficulty": lab.difficulty or "",
                "duration_minutes": lab.duration_minutes,
                "cohort_size": cohort_size,
                "sample_size": sample_size,
                "starts": starts,
                "start_rate": start_rate,
                "completed_learners": completion_count,
                "completion_rate": completion_rate,
                "stalled_learners": max(starts - completion_count, 0),
                "failed_attempts": failed_attempts,
                "failed_per_completion": failed_per_completion,
                "hint_uses": hint_uses,
                "hints_per_completion": hints_per_completion,
                "median_minutes": median_minutes,
                "median_attempts": median_attempts,
                "friction_flags": flags,
            }
        )

    rows = [
        row
        for row in rows
        if row["starts"] >= max(0, min_starts)
    ]
    rows.sort(
        key=lambda row: (
            row["starts"] == 0,
            row["completion_rate"] if row["completion_rate"] is not None else 101,
            -(row["failed_per_completion"] or 0),
            row["lab_name"].lower(),
        )
    )
    return report_access.suppress_small_cells(
        rows,
        _minimum_cohort_size(db),
        sample_key="sample_size",
        metric_keys=(
            "start_rate",
            "completion_rate",
            "stalled_learners",
            "failed_attempts",
            "failed_per_completion",
            "hint_uses",
            "hints_per_completion",
            "median_minutes",
            "median_attempts",
        ),
    )


@router.get("/courses/{course_id}/reports")
async def list_reports(
    course_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the report library for a course the caller can manage."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    reports = _report_catalog(db, course, current_user)
    if not reports:
        report_access.audit_library(db, request, current_user, course, [])
        raise HTTPException(
            status_code=403,
            detail="Your role is not permitted to view reports for this course.",
        )
    report_access.audit_library(
        db, request, current_user, course, [item["id"] for item in reports]
    )
    return {"course_id": course.id, "reports": reports}


@router.get("/courses/{course_id}/reports/course-health.pdf")
async def course_health_report(
    course_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = _report_course_or_403(
        db, request, course_id, current_user, "course-health", export=True
    )
    overview = await course_overview(
        course_id, db, _analytics_actor(db, course, current_user)
    )
    exercises = await course_exercises(
        course_id, db, _analytics_actor(db, course, current_user)
    )
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
    current_user: User = Depends(get_current_active_user),
):
    course = _report_course_or_403(
        db, request, course_id, current_user, "exercise-diagnostics", export=True
    )
    _labs, _user_ids, completions, _sessions = _course_context(db, course)
    payload = await course_exercises(
        course_id, db, _analytics_actor(db, course, current_user)
    )
    payload = _with_exercise_baselines(payload, completions)
    payload["exercises"] = report_access.suppress_small_cells(
        payload.get("exercises") or [],
        _minimum_cohort_size(db),
    )
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
    current_user: User = Depends(get_current_active_user),
):
    course = _report_course_or_403(
        db, request, course_id, current_user, "exercise-diagnostics", export=True
    )
    _labs, _user_ids, completions, _sessions = _course_context(db, course)
    payload = await course_exercises(
        course_id, db, _analytics_actor(db, course, current_user)
    )
    payload = _with_exercise_baselines(payload, completions)
    payload["exercises"] = report_access.suppress_small_cells(
        payload.get("exercises") or [],
        _minimum_cohort_size(db),
    )
    exercises = payload.get("exercises") or []
    report_id = str(uuid.uuid4())
    headers = [
        "report_id",
        "exercise",
        "track",
        "level",
        "difficulty",
        "sample_size",
        "suppressed",
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
            row.get("suppressed"),
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
    data = _csv_bytes(
        headers,
        rows,
        labels=report_access.csv_label_lines(
            report_access.policy_for("exercise-diagnostics")
        ),
    )
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


@router.get("/courses/{course_id}/reports/lab-friction.csv")
async def lab_friction_csv(
    course_id: int,
    request: Request,
    min_starts: int = Query(0, ge=0, le=100000),
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Per-lab completion, wrong-flag, hint, and time friction."""
    course = _report_course_or_403(
        db, request, course_id, current_user, "lab-friction", export=True
    )
    rows = _friction_rows(db, course, min_starts=min_starts)
    report_id = str(uuid.uuid4())
    headers = [
        "report_id",
        "lab_id",
        "lab",
        "slug",
        "track",
        "level",
        "difficulty",
        "duration_minutes",
        "cohort_size",
        "sample_size",
        "suppressed",
        "starts",
        "start_rate",
        "completed_learners",
        "completion_rate",
        "stalled_learners",
        "failed_attempts",
        "failed_per_completion",
        "hint_uses",
        "hints_per_completion",
        "median_minutes",
        "median_attempts",
        "friction_flags",
    ]
    data = _csv_bytes(
        headers,
        [
            [
                report_id,
                row.get("lab_id"),
                row.get("lab_name"),
                row.get("slug"),
                row.get("track_name"),
                row.get("level_name"),
                row.get("difficulty"),
                row.get("duration_minutes"),
                row.get("cohort_size"),
                row.get("sample_size"),
                row.get("suppressed"),
                row.get("starts"),
                row.get("start_rate"),
                row.get("completed_learners"),
                row.get("completion_rate"),
                row.get("stalled_learners"),
                row.get("failed_attempts"),
                row.get("failed_per_completion"),
                row.get("hint_uses"),
                row.get("hints_per_completion"),
                row.get("median_minutes"),
                row.get("median_attempts"),
                ", ".join(row.get("friction_flags") or []),
            ]
            for row in rows
        ],
        labels=report_access.csv_label_lines(
            report_access.policy_for("lab-friction")
        ),
    )
    return _serve(
        db,
        request=request,
        current_user=current_user,
        course=course,
        report_id=report_id,
        report_type="lab-friction",
        file_format="csv",
        data=data,
        reason=reason,
    )


@router.get("/courses/{course_id}/reports/lms-gradebook.csv")
async def lms_gradebook_csv(
    course_id: int,
    request: Request,
    adapter: str = Query("generic"),
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Per-learner gradebook in the selected LMS layout."""
    course = _report_course_or_403(
        db, request, course_id, current_user, "lms-gradebook", export=True
    )
    try:
        book = gradebook.build_gradebook(db, course, adapter)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    report_id = str(uuid.uuid4())
    headers, rows = gradebook.csv_table(report_id, course, book)
    data = _csv_bytes(headers, rows, annotate=False)
    response = _serve(
        db,
        request=request,
        current_user=current_user,
        course=course,
        report_id=report_id,
        report_type="lms-gradebook",
        file_format="csv",
        data=data,
        reason=reason,
    )
    response.headers["X-Gradebook-Adapter"] = book["adapter"]
    response.headers["Access-Control-Expose-Headers"] += ", X-Gradebook-Adapter"
    return response


@router.get("/courses/{course_id}/reports/coaching-queue.csv")
async def coaching_queue_csv(
    course_id: int,
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = _report_course_or_403(
        db, request, course_id, current_user, "coaching-queue", export=True
    )
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
        labels=report_access.csv_label_lines(
            report_access.policy_for("coaching-queue")
        ),
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
    current_user: User = Depends(get_current_active_user),
):
    course = _report_course_or_403(
        db, request, course_id, current_user, "coaching-queue", export=True
    )
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
