"""LMS-ready gradebook rows for a course.

The scoreboard route is optimised for the browser. This module is the export
path: it produces the same scores, then reshapes them into the column layouts
that Canvas, Brightspace, Moodle, and a generic CSV importer expect.

Under-18 accounts are excluded, matching every other individual report. The
library card names that behaviour so an instructor is not surprised by a short
roster.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models import (
    Achievement,
    Course,
    CourseCompletionReset,
    CourseEnrollment,
    CourseLabAssignment,
    Lab,
    LabCompletion,
    LabSession,
    User,
)
from app.routers.courses import calculate_lab_score

ADAPTERS = ("generic", "canvas", "brightspace", "moodle")


def max_lab_score(lab: Lab) -> int:
    """Highest score ``calculate_lab_score`` can return for this lab.

    The bonuses are fixed: 100 base, 25 hint-free, 25 first attempt, up to 50
    speed, and 50 first blood. Speed is only reachable when the lab declares a
    duration.
    """
    return 150 + (50 if lab.duration_minutes else 0) + 50


def _column_name(value: str, used: set[str]) -> str:
    name = re.sub(r"[\r\n,]+", " ", str(value or "").strip())
    name = re.sub(r"\s+", " ", name).strip()[:80] or "Lab"
    candidate = name
    suffix = 2
    while candidate.lower() in used:
        candidate = f"{name} ({suffix})"
        suffix += 1
    used.add(candidate.lower())
    return candidate


def _name_parts(user: User) -> tuple[str, str]:
    first = (user.first_name or "").strip()
    last = (user.last_name or "").strip()
    if not first and not last:
        # Keep the username intact when no profile name exists; splitting on a
        # dot would guess at a person's name and can be wrong.
        first = user.username
    return first, last


def _display_name(user: User) -> str:
    first, last = _name_parts(user)
    if last:
        return f"{last}, {first}"
    return first


def build_gradebook(
    db: Session,
    course: Course,
    adapter: str = "generic",
) -> dict:
    """Return ``{labs, students, rows, max_scores, max_total}`` for an export."""
    adapter = str(adapter or "generic").strip().lower()
    if adapter not in ADAPTERS:
        raise ValueError(f"Unknown gradebook adapter: {adapter}")

    enrollments = (
        db.query(CourseEnrollment)
        .options(joinedload(CourseEnrollment.user))
        .filter(CourseEnrollment.course_id == course.id)
        .all()
    )
    enrollment_map = {row.user_id: row.enrolled_at for row in enrollments}
    students = [
        row.user
        for row in enrollments
        if row.user is not None and not getattr(row.user, "is_minor", False)
    ]
    students.sort(key=lambda user: (user.last_name or "", user.first_name or "", user.username))
    user_ids = [user.id for user in students]

    assignments = (
        db.query(CourseLabAssignment)
        .options(joinedload(CourseLabAssignment.lab))
        .filter(CourseLabAssignment.course_id == course.id)
        .order_by(CourseLabAssignment.sort_order, CourseLabAssignment.id)
        .all()
    )
    labs: list[Lab] = []
    display_names: dict[int, str] = {}
    for row in assignments:
        lab = row.lab
        if lab is None or not lab.is_active:
            continue
        labs.append(lab)
        display_names[lab.id] = row.display_name or lab.name
    lab_ids = [lab.id for lab in labs]

    used_columns: set[str] = set()
    lab_columns = [_column_name(display_names[lab.id], used_columns) for lab in labs]
    max_scores = [max_lab_score(lab) for lab in labs]
    max_total = sum(max_scores)

    if not user_ids or not lab_ids:
        return {
            "adapter": adapter,
            "labs": labs,
            "lab_columns": lab_columns,
            "max_scores": max_scores,
            "max_total": max_total,
            "students": students,
            "rows": [],
        }

    reset_map: dict[tuple[int, int], datetime] = {}
    for row in (
        db.query(CourseCompletionReset)
        .filter(
            CourseCompletionReset.course_id == course.id,
            CourseCompletionReset.user_id.in_(user_ids),
        )
        .all()
    ):
        key = (row.user_id, row.lab_id)
        if key not in reset_map or row.reset_at > reset_map[key]:
            reset_map[key] = row.reset_at

    completions: dict[tuple[int, int], LabCompletion] = {}
    for row in (
        db.query(LabCompletion)
        .filter(
            LabCompletion.user_id.in_(user_ids),
            LabCompletion.lab_id.in_(lab_ids),
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        )
        .all()
    ):
        enrolled_at = enrollment_map.get(row.user_id)
        if enrolled_at and row.completed_at and row.completed_at < enrolled_at:
            continue
        reset = reset_map.get((row.user_id, row.lab_id))
        if reset and row.completed_at and row.completed_at <= reset:
            continue
        current = completions.get((row.user_id, row.lab_id))
        if current is None or (row.completed_at or datetime.min) > (
            current.completed_at or datetime.min
        ):
            completions[(row.user_id, row.lab_id)] = row

    first_blood: dict[int, int] = {}
    for (user_id, lab_id), row in completions.items():
        current_id = first_blood.get(lab_id)
        if current_id is None:
            first_blood[lab_id] = user_id
            continue
        current = completions.get((current_id, lab_id))
        if current and (row.completed_at or datetime.min) < (
            current.completed_at or datetime.min
        ):
            first_blood[lab_id] = user_id

    achievements: dict[tuple[int, int], list[str]] = defaultdict(list)
    for row in (
        db.query(Achievement)
        .filter(
            Achievement.course_id == course.id,
            Achievement.user_id.in_(user_ids),
        )
        .all()
    ):
        if row.lab_id is not None:
            achievements[(row.user_id, row.lab_id)].append(row.achievement_type)

    last_activity: dict[int, datetime] = {}
    for row in (
        db.query(LabSession)
        .filter(
            LabSession.user_id.in_(user_ids),
            LabSession.lab_id.in_(lab_ids),
        )
        .all()
    ):
        mark = row.started_at or row.stopped_at
        if mark is not None and (
            row.user_id not in last_activity or mark > last_activity[row.user_id]
        ):
            last_activity[row.user_id] = mark
    for (user_id, _lab_id), row in completions.items():
        mark = row.completed_at
        if mark is not None and (
            user_id not in last_activity or mark > last_activity[user_id]
        ):
            last_activity[user_id] = mark

    rows = []
    for user in students:
        scores = []
        completed = 0
        for lab in labs:
            completion = completions.get((user.id, lab.id))
            scores.append(
                calculate_lab_score(
                    completion,
                    lab,
                    course.id,
                    db,
                    first_blood_user_id=first_blood.get(lab.id),
                )
            )
            if completion is not None:
                completed += 1
        total = sum(scores)
        first, last = _name_parts(user)
        rows.append(
            {
                "user": user,
                "first_name": first,
                "last_name": last,
                "display_name": _display_name(user),
                "username": user.username,
                "student_id": user.student_id or "",
                "email": user.email or "",
                "scores": scores,
                "total_score": total,
                "max_score": max_total,
                "percentage": round(total / max_total * 100, 1) if max_total else 0.0,
                "labs_completed": completed,
                "labs_assigned": len(labs),
                "last_activity": (
                    last_activity[user.id].date().isoformat()
                    if user.id in last_activity
                    else ""
                ),
                "achievements": sorted(
                    {
                        item
                        for lab in labs
                        for item in achievements.get((user.id, lab.id), [])
                    }
                ),
            }
        )

    return {
        "adapter": adapter,
        "labs": labs,
        "lab_columns": lab_columns,
        "max_scores": max_scores,
        "max_total": max_total,
        "students": students,
        "rows": rows,
    }


def csv_table(
    report_id: str,
    course: Course,
    gradebook: dict,
) -> tuple[list[str], list[list]]:
    """Return the header and data rows for the chosen LMS adapter."""
    adapter = gradebook["adapter"]
    lab_columns = gradebook["lab_columns"]
    max_scores = gradebook["max_scores"]
    rows = gradebook["rows"]

    if adapter == "canvas":
        headers = [
            "Student",
            "ID",
            "SIS User ID",
            "SIS Login ID",
            "Section",
            *lab_columns,
            "Total",
        ]
        points = ["    Points Possible", "", "", "", "", *max_scores, gradebook["max_total"]]
        data = [
            [
                row["display_name"],
                row["user"].id,
                row["student_id"],
                row["username"],
                course.code or "",
                *row["scores"],
                row["total_score"],
            ]
            for row in rows
        ]
        return headers, [points, *data]

    if adapter == "brightspace":
        headers = [
            "OrgDefinedId",
            "Username",
            "FirstName",
            "LastName",
            "Email",
            *[f"{name} Points Grade" for name in lab_columns],
            "Total Points Grade",
            "End-of-Line Indicator",
        ]
        data = [
            [
                row["student_id"] or row["username"],
                row["username"],
                row["first_name"],
                row["last_name"],
                row["email"],
                *row["scores"],
                row["total_score"],
                "#",
            ]
            for row in rows
        ]
        return headers, data

    if adapter == "moodle":
        headers = [
            "username",
            "email",
            "firstname",
            "lastname",
            "idnumber",
            *lab_columns,
            "total",
            "max_total",
            "percentage",
        ]
        data = [
            [
                row["username"],
                row["email"],
                row["first_name"],
                row["last_name"],
                row["student_id"],
                *row["scores"],
                row["total_score"],
                row["max_score"],
                row["percentage"],
            ]
            for row in rows
        ]
        return headers, data

    headers = [
        "report_id",
        "username",
        "student_id",
        "email",
        "first_name",
        "last_name",
        "labs_assigned",
        "labs_completed",
        *lab_columns,
        "total_score",
        "max_score",
        "percentage",
        "last_activity",
        "achievements",
    ]
    data = [
        [
            report_id,
            row["username"],
            row["student_id"],
            row["email"],
            row["first_name"],
            row["last_name"],
            row["labs_assigned"],
            row["labs_completed"],
            *row["scores"],
            row["total_score"],
            row["max_score"],
            row["percentage"],
            row["last_activity"],
            "; ".join(row["achievements"]),
        ]
        for row in rows
    ]
    return headers, data
