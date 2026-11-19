"""Instructor readiness dashboard: pilot CWRS queue and lab health.

This is a descriptive support view, not a grade, prediction, or automated
decision. It uses the evidence the course already records and labels every
component as provisional until the rubric is calibrated.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import median
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import ExerciseQuizAttempt, LabCompletion, LabSession, User
from app.services.competency_radar import build_individual_radar

CWRS_FORMULA_VERSION = "cwrs-pilot-2026.1"
CWRS_WEIGHTS = {
    "performance": 0.35,
    "engagement": 0.20,
    "progression": 0.15,
    "competency": 0.15,
    "behavioural": 0.10,
    "infrastructure": 0.05,
}
BANDS = (
    (85, "critical_intervention", "Critical intervention"),
    (70, "high_risk", "High risk"),
    (50, "elevated", "Elevated"),
    (30, "monitor", "Monitor"),
    (0, "healthy", "Healthy"),
)


def _as_aware(value) -> Optional[datetime]:
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def _rate(part: int, total: int) -> float:
    return round(part / total * 100, 1) if total else 0.0


def _median(values) -> Optional[float]:
    cleaned = [value for value in values if value is not None]
    if not cleaned:
        return None
    return round(float(median(cleaned)), 1)


def _band(score: int) -> tuple[str, str]:
    for minimum, key, label in BANDS:
        if score >= minimum:
            return key, label
    return "healthy", "Healthy"


def _weighted_available(values: dict[str, Optional[float]], weights: dict[str, float]) -> Optional[float]:
    available = {
        key: value for key, value in values.items()
        if value is not None and key in weights
    }
    total_weight = sum(weights[key] for key in available)
    if total_weight <= 0:
        return None
    return round(sum(value * weights[key] for key, value in available.items()) / total_weight, 1)


def _confidence(components: dict[str, Optional[float]], sample: int) -> str:
    substantive = ("performance", "engagement", "progression", "competency")
    available = sum(1 for key in substantive if components.get(key) is not None)
    if available >= 4 and sample >= 5:
        return "high"
    if available >= 3:
        return "medium"
    return "low"


def _login_risk(days: Optional[int]) -> int:
    if days is None:
        return 100
    if days <= 3:
        return 0
    if days <= 7:
        return 25
    if days <= 14:
        return 60
    return 100


def _performance_risk(
    *,
    completed: int,
    started: int,
    assigned: int,
    reattempt_rate: float,
    quiz_average: Optional[float],
) -> tuple[Optional[float], bool]:
    success = _rate(completed, started) if started else None
    evidence = _rate(completed, assigned) if assigned else None
    retake = max(0.0, min(100.0, 100.0 - reattempt_rate)) if completed else None
    success_risk = None if success is None else 100.0 - success
    evidence_risk = None if evidence is None else 100.0 - evidence
    assessment_risk = None if quiz_average is None else 100.0 - quiz_average
    retake_risk = None if retake is None else 100.0 - retake
    risk = _weighted_available(
        {
            "success": success_risk,
            "assessment": assessment_risk,
            "evidence": evidence_risk,
            "retake": retake_risk,
        },
        {"success": 0.30, "assessment": 0.30, "evidence": 0.25, "retake": 0.15},
    )
    provisional = any(
        value is None
        for value in (success_risk, assessment_risk, evidence_risk, retake_risk)
    )
    return risk, provisional


def _engagement_risk(
    *,
    days_since: Optional[int],
    active_days: int,
    learning_minutes: int,
    cohort_median_minutes: Optional[float],
) -> Optional[float]:
    login = _login_risk(days_since)
    weekly = 100.0 - min(100.0, active_days / 7.0 * 100.0)
    if cohort_median_minutes and cohort_median_minutes > 0:
        time_risk = 100.0 - min(100.0, learning_minutes / cohort_median_minutes * 100.0)
    else:
        time_risk = None
    return _weighted_available(
        {"login": float(login), "weekly": weekly, "time": time_risk},
        {"login": 0.45, "weekly": 0.30, "time": 0.25},
    )


def _caption(components: dict[str, Optional[float]]) -> dict[str, Optional[float]]:
    return {key: (round(value, 1) if value is not None else None) for key, value in components.items()}


def build_course_readiness(
    db: Session,
    *,
    labs: list,
    user_ids: set[int],
    completions: list[LabCompletion],
    sessions: list[LabSession],
) -> dict:
    now = datetime.now(timezone.utc)
    users = {
        row.id: row
        for row in db.query(User).filter(User.id.in_(user_ids)).all()
    }
    quiz_query = (
        db.query(
            ExerciseQuizAttempt.user_id,
            ExerciseQuizAttempt.lab_id,
            func.max(ExerciseQuizAttempt.score),
        )
        .filter(
            ExerciseQuizAttempt.user_id.in_(user_ids),
            ExerciseQuizAttempt.completed_at.isnot(None),
        )
    )
    if labs:
        quiz_query = quiz_query.filter(
            ExerciseQuizAttempt.lab_id.in_([lab.id for lab in labs])
        )
    quiz_rows = (
        quiz_query
        .group_by(ExerciseQuizAttempt.user_id, ExerciseQuizAttempt.lab_id)
        .all()
    )
    quiz_by_user: dict[int, list[int]] = defaultdict(list)
    for user_id, _lab_id, score in quiz_rows:
        if score is not None:
            quiz_by_user[user_id].append(score)

    completions_by_user: dict[int, list[LabCompletion]] = defaultdict(list)
    for row in completions:
        completions_by_user[row.user_id].append(row)
    sessions_by_user: dict[int, list[LabSession]] = defaultdict(list)
    for row in sessions:
        sessions_by_user[row.user_id].append(row)

    learning_minutes = {
        user_id: int(sum((row.time_spent_minutes or 0) for row in rows))
        for user_id, rows in completions_by_user.items()
    }
    cohort_median_minutes = _median(list(learning_minutes.values()))
    completed_counts = {
        user_id: len(completions_by_user.get(user_id, []))
        for user_id in user_ids
    }
    expected_completed = _median(list(completed_counts.values())) or 0

    students = []
    for user_id in user_ids:
        user = users.get(user_id)
        if user is None:
            continue
        completion_rows = completions_by_user.get(user_id, [])
        session_rows = sessions_by_user.get(user_id, [])
        started_pairs = {(row.lab_id) for row in session_rows}
        completed_pairs = {row.lab_id for row in completion_rows}
        started = len(started_pairs)
        completed = len(completed_pairs)
        reattempt_rate = _rate(
            sum(1 for row in completion_rows if (row.attempts or 0) > 1),
            len(completion_rows),
        )
        quiz_scores = quiz_by_user.get(user_id, [])
        quiz_average = round(sum(quiz_scores) / len(quiz_scores), 1) if quiz_scores else None

        activity = [
            value for value in (
                user.last_login_at,
                *(row.started_at for row in session_rows),
                *(row.completed_at for row in completion_rows),
            )
            if value is not None
        ]
        last_activity = max((_as_aware(value) for value in activity), default=None)
        days_since = max(0, (now - last_activity).days) if last_activity else None

        active_days = {
            _as_aware(value).date()
            for value in (
                *(row.started_at for row in session_rows),
                *(row.completed_at for row in completion_rows),
            )
            if value is not None and _as_aware(value) >= now - timedelta(days=14)
        }
        active_day_count = len(active_days)

        performance, performance_provisional = _performance_risk(
            completed=completed,
            started=started,
            assigned=len(labs),
            reattempt_rate=reattempt_rate,
            quiz_average=quiz_average,
        )
        engagement = _engagement_risk(
            days_since=days_since,
            active_days=active_day_count,
            learning_minutes=learning_minutes.get(user_id, 0),
            cohort_median_minutes=cohort_median_minutes,
        )
        if expected_completed > 0:
            gap = max(0.0, expected_completed - completed)
            progression = round(min(100.0, gap / expected_completed * 100.0), 1)
        else:
            progression = 0.0
        competency_proxy = _weighted_available(
            {
                "quiz": quiz_average,
                "completion": _rate(completed, len(labs)) if labs else None,
            },
            {"quiz": 0.60, "completion": 0.40},
        )
        competency = None if competency_proxy is None else 100.0 - competency_proxy
        abandonment = _rate(max(0, started - completed), started) if started else 0.0
        behavioural = abandonment

        components = {
            "performance": performance,
            "engagement": engagement,
            "progression": progression,
            "competency": competency,
            "behavioural": behavioural,
            "infrastructure": 0.0,
        }
        score = _weighted_available(components, CWRS_WEIGHTS)
        if score is None:
            continue
        cwrs = max(0, min(100, round(score)))
        band_key, band_label = _band(cwrs)
        flags = []
        if performance is not None and performance >= 70:
            flags.append("performance")
        if engagement is not None and engagement >= 70:
            flags.append("engagement")
        if progression >= 70:
            flags.append("progression")
        if competency is not None and competency >= 70:
            flags.append("competency")
        if behavioural >= 50:
            flags.append("abandonment")
        if days_since is None or days_since >= 14:
            flags.append("inactive")
        if completed == 0 and started > 0:
            flags.append("no_completions")

        students.append(
            {
                "user_id": user_id,
                "username": user.username,
                "display_name": user.display_name,
                "cwrs": cwrs,
                "band": band_key,
                "band_label": band_label,
                "confidence": _confidence(components, len(session_rows)),
                "components": _caption(components),
                "flags": flags,
                "started_exercises": started,
                "completed_exercises": completed,
                "assigned_exercises": len(labs),
                "last_activity": last_activity.isoformat() if last_activity else None,
                "days_since_activity": days_since,
                "provisional": bool(performance_provisional or quiz_average is None),
            }
        )

    students.sort(key=lambda row: (-row["cwrs"], row["display_name"]))

    lab_health = _build_lab_health(labs, completions, sessions)
    band_counts = {key: 0 for _minimum, key, _label in BANDS}
    for row in students:
        band_counts[row["band"]] += 1

    return {
        "formula_version": CWRS_FORMULA_VERSION,
        "provisional": True,
        "note": (
            "Pilot readiness view. CWRS is a support prompt, not a grade or a "
            "hiring prediction. Components marked provisional need more evidence."
        ),
        "cohort": {
            "students": len(students),
            "assigned_exercises": len(labs),
            "median_completed": expected_completed,
            "band_counts": band_counts,
        },
        "students": students,
        "lab_health": lab_health,
        "generated_at": now.isoformat(),
    }


def _build_lab_health(labs: list, completions: list[LabCompletion], sessions: list[LabSession]) -> dict:
    completions_by_lab: dict[int, list[LabCompletion]] = defaultdict(list)
    for row in completions:
        completions_by_lab[row.lab_id].append(row)
    sessions_by_lab: dict[int, list[LabSession]] = defaultdict(list)
    for row in sessions:
        sessions_by_lab[row.lab_id].append(row)

    rows = []
    for lab in labs:
        lab_sessions = sessions_by_lab.get(lab.id, [])
        lab_completions = completions_by_lab.get(lab.id, [])
        started_users = {row.user_id for row in lab_sessions}
        completed_users = {row.user_id for row in lab_completions}
        if started_users:
            success = _rate(len(completed_users), len(started_users))
            abandonment = _rate(len(started_users - completed_users), len(started_users))
        else:
            success = None
            abandonment = None
        sample = len(started_users)
        if sample < 3:
            status = "no_data"
        elif (
            (success is not None and success < 50)
            or (abandonment is not None and abandonment > 35)
        ):
            status = "degraded"
        elif (
            (success is not None and success < 75)
            or (abandonment is not None and abandonment > 20)
        ):
            status = "warning"
        else:
            status = "healthy"
        rows.append(
            {
                "lab_id": lab.id,
                "name": lab.name,
                "slug": lab.slug,
                "track": getattr(getattr(getattr(lab, "level", None), "track", None), "name", None),
                "level": getattr(getattr(lab, "level", None), "name", None),
                "difficulty": lab.difficulty,
                "started": len(started_users),
                "completed": len(completed_users),
                "success_rate": success,
                "abandonment_rate": abandonment,
                "median_hints": _median([row.hints_used for row in lab_completions]),
                "median_minutes": _median([row.time_spent_minutes for row in lab_completions]),
                "sample_size": sample,
                "status": status,
            }
        )
    order = {"degraded": 0, "warning": 1, "no_data": 2, "healthy": 3}
    rows.sort(key=lambda row: (order[row["status"]], row["success_rate"] if row["success_rate"] is not None else 101, row["name"]))
    counts = {key: 0 for key in order}
    for row in rows:
        counts[row["status"]] += 1
    return {"counts": counts, "labs": rows}


def build_student_capabilities(db: Session, user_id: int) -> dict:
    radar = build_individual_radar(db, user_id)
    return {
        "model_version": radar.get("model_version"),
        "axes": [
            {
                "key": axis.get("key"),
                "label": axis.get("label"),
                "score": axis.get("current"),
                "target": axis.get("target"),
                "evidence_count": axis.get("evidence_count"),
                "evidence_quality": axis.get("evidence_quality"),
                "description": axis.get("description"),
            }
            for axis in radar.get("axes", [])
        ],
        "disclaimer": (
            "A low score with no evidence is unmeasured, not weak. Use the "
            "evidence links before deciding on support."
        ),
    }
