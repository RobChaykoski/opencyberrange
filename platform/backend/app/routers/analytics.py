"""Learning analytics for students, instructors, and administrators.

V2 Phase 1 keeps analytics descriptive and explanatory. It never ranks
learners, predicts grades, or exposes small groups. Course access is limited to
the course instructor or an administrator.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from statistics import median
from typing import Optional
import io
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_active_user, get_current_instructor_user
from app.database import get_db
from app.export_reason import require_export_reason
from app.services.activity import EventTypes, log_activity
from app.services.audit import log_admin_action, AuditActions
from app.services.learning_time import (
    learning_minutes_by_pair,
    learning_minutes_by_user,
)
from app.services.skill_dna import (
    SKILL_BRANCH_LABELS,
    SKILL_BRANCH_ORDER,
    skill_branch_mix,
)
from app.models import (
    Course,
    CourseCompletionReset,
    CourseEnrollment,
    CourseLabAssignment,
    ExercisePulseSurvey,
    ExerciseReaction,
    FlagAttempt,
    Lab,
    LabCompletion,
    LabSession,
    Level,
    Survey,
    SurveyAttachment,
    SurveyResponse,
    User,
)

router = APIRouter()

GROWTH_WINDOW = 3
MIN_GROWTH_EVIDENCE = GROWTH_WINDOW * 2


def _median(values):
    cleaned = [value for value in values if value is not None]
    return round(float(median(cleaned)), 1) if cleaned else None


def _rate(part: int, total: int) -> float:
    return round(part / total * 100, 1) if total else 0.0


def _status(delta: float, *, lower_is_better: bool, has_evidence: bool) -> str:
    if not has_evidence:
        return "insufficient_evidence"
    if lower_is_better:
        if delta <= -0.5:
            return "improving"
        if delta >= 0.5:
            return "needs_attention"
    else:
        if delta >= 0.05:
            return "improving"
        if delta <= -0.05:
            return "needs_attention"
    return "steady"


def _growth_indicator(label, first, latest, status, explanation, unit=None):
    return {
        "label": label,
        "first": first,
        "latest": latest,
        "change": (
            round(latest - first, 2)
            if first is not None and latest is not None else None
        ),
        "status": status,
        "explanation": explanation,
        "unit": unit,
    }


def _confidence_gain(growth: list[dict]) -> Optional[float]:
    """A transparent proxy from hint, attempt, and time growth.

    This is *not* a validated psychological confidence measure. It is a
    performance-growth score shown alongside the underlying indicators.
    """
    score_map = {"improving": 1, "steady": 0, "needs_attention": -1}
    values = [
        score_map[item["status"]]
        for item in growth
        if item["label"] in {"Hint usage", "First-attempt success", "Time efficiency"}
        and item["status"] in score_map
    ]
    if not values:
        return None
    return round(sum(values) / len(values) * 100, 1)


def _rag_status(
    *,
    completion_rate: float,
    abandonment_rate: float,
    median_attempts: Optional[float],
    learning_reported: Optional[float],
    difficulty_reported: Optional[float],
) -> tuple[str, list[str]]:
    """Classify an exercise or course as red, amber, or green.

    Red: learners are not succeeding, or self-reported learning is low.
    Amber: learners are succeeding but the experience is frustrating.
    Green: completion and learning are both strong.
    """
    reasons = []
    if abandonment_rate >= 50:
        reasons.append("High abandonment")
    if completion_rate < 50:
        reasons.append("Low completion")
    if median_attempts is not None and median_attempts >= 5:
        reasons.append("High attempt burden")
    if learning_reported is not None and learning_reported <= 2:
        reasons.append("Low learning reported")
    if reasons:
        return "red", reasons

    if (
        completion_rate >= 80
        and (learning_reported is None or learning_reported >= 4)
        and (difficulty_reported is None or 2 <= difficulty_reported <= 4)
    ):
        return "green", ["Strong completion and learning"]

    if completion_rate >= 70:
        reasons.append("Succeeding but strained")
    else:
        reasons.append("Mixed evidence")
    if difficulty_reported is not None and difficulty_reported >= 4:
        reasons.append("Reported as difficult")
    if learning_reported is not None and learning_reported < 3:
        reasons.append("Learning reported is low")
    return "amber", reasons


def _completion_rows(db: Session, user_ids: set, lab_ids: set):
    if not user_ids or not lab_ids:
        return []
    return db.query(LabCompletion).options(
        joinedload(LabCompletion.lab).joinedload(Lab.level).joinedload(Level.track)
    ).filter(
        LabCompletion.user_id.in_(user_ids),
        LabCompletion.lab_id.in_(lab_ids),
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).all()


def _session_rows(db: Session, user_ids: set, lab_ids: set):
    if not user_ids or not lab_ids:
        return []
    return db.query(LabSession).options(
        joinedload(LabSession.lab).joinedload(Lab.level).joinedload(Level.track)
    ).filter(
        LabSession.user_id.in_(user_ids),
        LabSession.lab_id.in_(lab_ids),
        LabSession.is_diagnostic == False,
    ).all()


def _reaction_rows(db: Session, lab_ids: set, course_id: Optional[int] = None):
    if not lab_ids:
        return []
    query = db.query(ExerciseReaction).filter(
        ExerciseReaction.lab_id.in_(lab_ids)
    )
    if course_id is not None:
        query = query.filter(ExerciseReaction.course_id == course_id)
    return query.all()


def _reaction_fields(rows) -> dict:
    likes = sum(1 for row in rows if row.reaction == "like")
    dislikes = sum(1 for row in rows if row.reaction == "dislike")
    total = likes + dislikes
    return {
        "likes": likes,
        "dislikes": dislikes,
        "reaction_count": total,
        "positive_rate": _rate(likes, total),
    }


def _require_started_lab(db: Session, current_user: User, lab_id: int):
    if current_user.role in {"admin", "instructor"}:
        return
    started = db.query(LabSession.id).filter(
        LabSession.user_id == current_user.id,
        LabSession.lab_id == lab_id,
        LabSession.is_diagnostic == False,
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


class PulseSurveyRequest(BaseModel):
    difficulty: int = Field(..., ge=1, le=5)
    learning: int = Field(..., ge=1, le=5)
    unclear: Optional[str] = Field(None, max_length=2000)
    topic_interest: Optional[str] = Field(None, max_length=50)
    course_id: Optional[int] = None


class ExerciseReactionRequest(BaseModel):
    reaction: Optional[str] = Field(None, pattern="^(like|dislike)$")
    course_id: Optional[int] = None


class WorkbookOpenRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    url: Optional[str] = Field(None, max_length=500)


class SurveyQuestionInput(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500)
    type: str = Field(..., pattern="^(scale|choice|text)$")
    options: list[str] = Field(default_factory=list, max_length=12)

    def normalized(self):
        options = [item.strip() for item in self.options if item.strip()]
        if self.type == "choice" and len(options) < 2:
            raise ValueError("Choice questions need at least two options")
        return {
            "prompt": self.prompt.strip(),
            "type": self.type,
            "options": options if self.type == "choice" else [],
        }


class SurveyCreateInput(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    questions: list[SurveyQuestionInput] = Field(..., min_length=1, max_length=20)
    course_ids: list[int] = Field(..., min_length=1)


class SurveyResponseInput(BaseModel):
    answers: dict = Field(default_factory=dict)


def _pulse_rows(
    db: Session,
    lab_ids: set,
    *,
    course_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    if not lab_ids:
        return []
    query = db.query(ExercisePulseSurvey).filter(
        ExercisePulseSurvey.lab_id.in_(lab_ids)
    )
    if course_id is not None:
        query = query.filter(ExercisePulseSurvey.course_id == course_id)
    if user_id is not None:
        query = query.filter(ExercisePulseSurvey.user_id == user_id)
    return query.all()


def _average(values):
    cleaned = [value for value in values if value is not None]
    return round(sum(cleaned) / len(cleaned), 2) if cleaned else None


DOMAIN_DEFINITIONS = (
    {
        "key": "web",
        "label": "Web Security",
        "track_slugs": ("web", "software-security"),
    },
    {"key": "osint", "label": "OSINT", "track_slugs": ("osint",)},
    {"key": "forensics", "label": "Forensics", "track_slugs": ("forensics",)},
    {"key": "malware", "label": "Malware", "track_slugs": ("malware",)},
    {"key": "ot", "label": "OT / ICS", "track_slugs": ("ot",)},
    {"key": "ai", "label": "AI Security", "track_slugs": ("ai",)},
)

DOMAIN_BY_TRACK = {
    slug: definition["key"]
    for definition in DOMAIN_DEFINITIONS
    for slug in definition["track_slugs"]
}

TOPIC_INTERESTS = {
    "web": "Web Security",
    "osint": "OSINT",
    "forensics": "Forensics",
    "malware": "Malware Analysis",
    "ot": "OT / ICS",
    "ai": "AI Security",
    "cloud": "Cloud Security",
    "network": "Network Security",
    "linux": "Linux",
    "windows": "Windows",
    "software-security": "Software Security",
    "career": "Career skills",
    "other": "Something else",
}


def _trending_topics(pulse_rows) -> list[dict]:
    counts = Counter(
        row.topic_interest for row in pulse_rows
        if row.topic_interest and row.topic_interest in TOPIC_INTERESTS
    )
    return [
        {"key": key, "label": TOPIC_INTERESTS[key], "count": count}
        for key, count in counts.most_common()
    ]


def _track_slug(row) -> Optional[str]:
    lab = getattr(row, "lab", None)
    level = getattr(lab, "level", None) if lab else None
    track = getattr(level, "track", None) if level else None
    return track.slug if track else None


def _domain_performance(
    completions: list[LabCompletion],
    sessions: list[LabSession],
) -> list[dict]:
    """Competency evidence for the six research/teaching domains."""
    rows = []
    for definition in DOMAIN_DEFINITIONS:
        slugs = set(definition["track_slugs"])
        domain_completions = [
            row for row in completions if _track_slug(row) in slugs
        ]
        domain_sessions = [
            row for row in sessions if _track_slug(row) in slugs
        ]
        completed_labs = {row.lab_id for row in domain_completions}
        started_labs = {row.lab_id for row in domain_sessions}
        growth = _growth(domain_completions)
        growth_statuses = [
            item["status"] for item in growth
            if item["status"] != "insufficient_evidence"
        ]
        if len(domain_completions) < MIN_GROWTH_EVIDENCE:
            domain_status = "insufficient_evidence"
        elif growth_statuses.count("improving") > growth_statuses.count("needs_attention"):
            domain_status = "improving"
        elif growth_statuses.count("needs_attention") > growth_statuses.count("improving"):
            domain_status = "needs_attention"
        else:
            domain_status = "steady"

        count = len(completed_labs)
        if count == 0:
            evidence = "no_evidence"
        elif count < 3:
            evidence = "early"
        elif count < 6:
            evidence = "growing"
        else:
            evidence = "strong"

        rows.append({
            "key": definition["key"],
            "label": definition["label"],
            "track_slugs": list(definition["track_slugs"]),
            "started_exercises": len(started_labs),
            "completed_exercises": count,
            "completion_rate": _rate(count, len(started_labs)),
            "median_time_minutes": _median(
                [row.time_spent_minutes for row in domain_completions]
            ),
            "hint_free_rate": _rate(
                sum(1 for row in domain_completions if (row.hints_used or 0) == 0),
                len(domain_completions),
            ),
            "first_attempt_rate": _rate(
                sum(1 for row in domain_completions if (row.attempts or 0) == 1),
                len(domain_completions),
            ),
            "growth_status": domain_status,
            "evidence_level": evidence,
        })
    return rows


def _growth(completions: list[LabCompletion]) -> list[dict]:
    ordered = sorted(
        [row for row in completions if row.completed_at],
        key=lambda row: row.completed_at,
    )
    has_evidence = len(ordered) >= MIN_GROWTH_EVIDENCE
    first = ordered[:GROWTH_WINDOW]
    latest = ordered[-GROWTH_WINDOW:] if ordered else []

    def window_median(rows, getter):
        return _median([getter(row) for row in rows])

    hint_first = window_median(first, lambda row: row.hints_used or 0)
    hint_latest = window_median(latest, lambda row: row.hints_used or 0)
    hint_status = _status(
        (hint_latest or 0) - (hint_first or 0),
        lower_is_better=True,
        has_evidence=has_evidence,
    )

    attempt_first = _rate(
        sum(1 for row in first if (row.attempts or 0) == 1), len(first)
    )
    attempt_latest = _rate(
        sum(1 for row in latest if (row.attempts or 0) == 1), len(latest)
    )
    attempt_status = _status(
        (attempt_latest - attempt_first) / 100,
        lower_is_better=False,
        has_evidence=has_evidence,
    )

    def time_ratio(row):
        duration = row.lab.duration_minutes if row.lab else None
        if not duration or row.time_spent_minutes is None:
            return None
        return row.time_spent_minutes / duration

    time_first = window_median(first, time_ratio)
    time_latest = window_median(latest, time_ratio)
    time_status = _status(
        (time_latest or 0) - (time_first or 0),
        lower_is_better=True,
        has_evidence=has_evidence,
    )

    tracks = {
        row.lab.level.track.name
        for row in ordered
        if row.lab and row.lab.level and row.lab.level.track
    }
    persistent = sum(1 for row in ordered if (row.attempts or 0) >= 2)

    return [
        _growth_indicator(
            "Hint usage",
            hint_first,
            hint_latest,
            hint_status,
            "Median hints per exercise across your earliest and latest exercises.",
            "hints",
        ),
        _growth_indicator(
            "First-attempt success",
            attempt_first,
            attempt_latest,
            attempt_status,
            "Share of exercises solved on the first flag attempt.",
            "%",
        ),
        _growth_indicator(
            "Time efficiency",
            round(time_first, 2) if time_first is not None else None,
            round(time_latest, 2) if time_latest is not None else None,
            time_status,
            "Median time as a fraction of the exercise estimate. Lower is more efficient.",
            "× estimate",
        ),
        {
            "label": "Persistence",
            "value": persistent,
            "status": "steady" if persistent else "insufficient_evidence",
            "explanation": (
                "Exercises completed after more than one flag attempt."
                if persistent else "No multi-attempt completions yet."
            ),
            "unit": "exercises",
        },
        {
            "label": "Breadth",
            "value": len(tracks),
            "status": "steady" if tracks else "insufficient_evidence",
            "explanation": "Tracks with at least one completed exercise.",
            "unit": "tracks",
        },
    ]


def _student_summary(completions: list[LabCompletion], sessions: list[LabSession]):
    started_labs = {row.lab_id for row in sessions}
    completed_labs = {row.lab_id for row in completions}
    total_time = sum(row.time_spent_minutes or 0 for row in completions)
    learning_pairs = learning_minutes_by_pair(completions, sessions)
    total_learning_minutes = int(sum(learning_minutes_by_user(learning_pairs).values()))
    total_hints = sum(row.hints_used or 0 for row in completions)
    first_attempt = sum(1 for row in completions if (row.attempts or 0) == 1)
    return {
        "started_exercises": len(started_labs),
        "completed_exercises": len(completed_labs),
        "completion_rate": _rate(len(completed_labs), len(started_labs)),
        "total_time_minutes": total_time,
        "total_learning_minutes": total_learning_minutes,
        "total_learning_hours": round(total_learning_minutes / 60, 1),
        "median_time_minutes": _median(
            [row.time_spent_minutes for row in completions]
        ),
        "hints_used": total_hints,
        "hints_per_completion": (
            round(total_hints / len(completions), 2) if completions else 0
        ),
        "hint_free_rate": _rate(
            sum(1 for row in completions if (row.hints_used or 0) == 0),
            len(completions),
        ),
        "first_attempt_rate": _rate(first_attempt, len(completions)),
        "reattempt_rate": _rate(
            sum(1 for row in completions if (row.attempts or 0) > 1),
            len(completions),
        ),
    }


def _course_or_403(db: Session, course_id: int, current_user: User) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the course instructor or an administrator can view analytics",
        )
    return course


def _course_context(db: Session, course: Course):
    enrollments = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course.id
    ).all()
    user_ids = {row.user_id for row in enrollments}
    enrolled_at = {row.user_id: row.enrolled_at for row in enrollments}

    assignments = db.query(CourseLabAssignment).options(
        joinedload(CourseLabAssignment.lab).joinedload(Lab.level).joinedload(Level.track)
    ).filter(
        CourseLabAssignment.course_id == course.id
    ).order_by(CourseLabAssignment.sort_order, CourseLabAssignment.id).all()
    labs = [
        row.lab for row in assignments
        if row.lab and row.lab.is_active
    ]
    lab_ids = {lab.id for lab in labs}

    resets = db.query(CourseCompletionReset).filter(
        CourseCompletionReset.course_id == course.id
    ).all()
    reset_map = {}
    for row in resets:
        key = (row.user_id, row.lab_id)
        if key not in reset_map or row.reset_at > reset_map[key]:
            reset_map[key] = row.reset_at

    completions = []
    for row in _completion_rows(db, user_ids, lab_ids):
        enrolled = enrolled_at.get(row.user_id)
        if enrolled and row.completed_at and row.completed_at < enrolled:
            continue
        reset = reset_map.get((row.user_id, row.lab_id))
        if reset and row.completed_at and row.completed_at <= reset:
            continue
        completions.append(row)

    sessions = [
        row for row in _session_rows(db, user_ids, lab_ids)
        if not enrolled_at.get(row.user_id)
        or not row.started_at
        or row.started_at >= enrolled_at[row.user_id]
    ]
    return labs, user_ids, completions, sessions


@router.get("/metrics")
async def metric_dictionary(
    current_user: User = Depends(get_current_active_user),
):
    """One definition set shared by the UI, exports, and documentation."""
    return {
        "metrics": [
            {"key": "completion_rate", "label": "Completion rate", "unit": "%",
             "definition": "Completed exercises divided by assigned exercises."},
            {"key": "started_completion_rate", "label": "Started-to-complete", "unit": "%",
             "definition": "Completed exercises divided by exercises that were started."},
            {"key": "median_time", "label": "Median time", "unit": "minutes",
             "definition": "Median reported time spent on completed exercises."},
            {"key": "learning_hours", "label": "Learning hours", "unit": "hours",
             "definition": "Tracked time on completed exercises, plus bounded session time for started exercises without a completion."},
            {"key": "exercise_reaction", "label": "Exercise reaction", "unit": "likes / dislikes",
             "definition": "Optional thumbs-up or thumbs-down feedback on an exercise. Reports show totals, not learner names."},
            {"key": "hints_per_completion", "label": "Hints per completion", "unit": "hints",
             "definition": "Total hints used divided by completed exercises."},
            {"key": "hint_free_rate", "label": "Hint-free rate", "unit": "%",
             "definition": "Completions with zero hints divided by all completions."},
            {"key": "first_attempt_rate", "label": "First-attempt rate", "unit": "%",
             "definition": "Completions with one flag attempt divided by all completions."},
            {"key": "reattempt_rate", "label": "Reattempt rate", "unit": "%",
             "definition": "Completions needing more than one flag attempt."},
            {"key": "persistence", "label": "Persistence", "unit": "exercises",
             "definition": "Exercises completed after more than one flag attempt."},
            {"key": "breadth", "label": "Breadth", "unit": "tracks",
             "definition": "Distinct tracks with at least one completed exercise."},
            {"key": "abandonment_rate", "label": "Abandonment rate", "unit": "%",
             "definition": "Started learner-exercise pairs without a completion."},
            {"key": "learning_reported", "label": "Learning reported", "unit": "1-5",
             "definition": "Average self-reported learning from the quick pulse survey."},
            {"key": "difficulty_reported", "label": "Difficulty reported", "unit": "1-5",
             "definition": "Average self-reported difficulty from the quick pulse survey."},
            {"key": "confidence_gain", "label": "Confidence gain", "unit": "index",
             "definition": "Performance-growth proxy from hint, attempt, and time trends. Not a validated psychological score."},
            {"key": "workbook_opens", "label": "Workbook opens", "unit": "events",
             "definition": "Authenticated workbook open events."},
            {"key": "time_to_first_attempt", "label": "Time to first attempt", "unit": "minutes",
             "definition": "Median time from lab start to the first flag attempt."},
        ],
        "note": "Analytics are descriptive. They are not grades, predictions, or rankings.",
    }


def _ai_prompts(
    summary: dict,
    growth: list[dict],
    recent: list[dict],
) -> list[dict]:
    """Ready-to-copy prompts for a learner's own AI assistant.

    The prompts deliberately ask for coaching rather than answers. They never
    include account details, flags, or another learner's data.
    """
    exercise = recent[0] if recent else {}
    lab_name = exercise.get("lab_name") or "a cybersecurity exercise"
    track_name = exercise.get("track_name") or "the current track"
    prompts = []

    if summary.get("hints_per_completion", 0) >= 1 or summary.get("hint_free_rate", 100) < 60:
        prompts.append({
            "id": "hint-coaching",
            "title": "Turn hints into understanding",
            "reason": "You are using hints on a meaningful share of exercises.",
            "prompt": (
                f"I am working on \"{lab_name}\" in {track_name} on SWOCTS Cyber Range. "
                "I have used several hints and want to understand the concept rather "
                "than skip it. Act as a Socratic coach: ask me one question at a time, "
                "help me form a hypothesis, and do not give me the flag or the final answer. "
                "Start by asking what I have already tried and what I noticed."
            ),
        })

    if summary.get("reattempt_rate", 0) >= 40:
        prompts.append({
            "id": "debug-coach",
            "title": "Debug your approach",
            "reason": "Several exercises needed more than one flag attempt.",
            "prompt": (
                f"I am stuck on \"{lab_name}\" in {track_name} on SWOCTS Cyber Range after "
                "more than one flag attempt. Act as a debugging coach, not an answer key. "
                "Ask for my observations and evidence, suggest one check at a time, and "
                "do not reveal the flag or final answer. Begin by asking me to summarize "
                "what I have tested and what changed."
            ),
        })

    time_growth = next(
        (item for item in growth if item.get("label") == "Time efficiency"),
        None,
    )
    if time_growth and time_growth.get("status") == "needs_attention":
        prompts.append({
            "id": "scope-coach",
            "title": "Break the exercise into phases",
            "reason": "Recent exercises are taking longer than their estimate.",
            "prompt": (
                f"Help me plan \"{lab_name}\" in {track_name} without solving it for me. "
                "Break the work into three short phases: observe, hypothesize, and verify. "
                "Ask what evidence I already have before suggesting the next phase. "
                "Do not give me the flag or final answer."
            ),
        })

    if summary.get("completion_rate", 100) < 50 or summary.get("started_exercises", 0) > summary.get("completed_exercises", 0):
        prompts.append({
            "id": "restart-coach",
            "title": "Restart with a plan",
            "reason": "You have started more exercises than you have completed.",
            "prompt": (
                f"I have started \"{lab_name}\" in {track_name} on SWOCTS Cyber Range but "
                "have not completed it. Help me decide the next small step. Ask me what "
                "I have already confirmed, what is still uncertain, and what one check "
                "I can run next. Do not provide the flag or final answer."
            ),
        })

    if not prompts or summary.get("first_attempt_rate", 0) >= 70:
        prompts.append({
            "id": "teach-back",
            "title": "Lock in what you learned",
            "reason": "A teach-back prompt helps turn a completed exercise into durable understanding.",
            "prompt": (
                f"I have completed \"{lab_name}\" in {track_name} on SWOCTS Cyber Range. "
                "Act as a study partner: ask me to explain the vulnerability or technique, "
                "the evidence I used, and one defensive control in my own words. Then give "
                "me one follow-up question. Do not give me another flag or final answer."
            ),
        })

    return prompts[:4]


@router.get("/student/me")
async def student_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    completions = db.query(LabCompletion).options(
        joinedload(LabCompletion.lab).joinedload(Lab.level).joinedload(Level.track)
    ).filter(
        LabCompletion.user_id == current_user.id,
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).order_by(LabCompletion.completed_at.asc()).all()
    sessions = _session_rows(db, {current_user.id}, {
        row.lab_id for row in completions
    })
    recent = []
    for row in sorted(
        completions, key=lambda item: item.completed_at or datetime.min, reverse=True
    )[:8]:
        lab = row.lab
        recent.append({
            "lab_id": row.lab_id,
            "lab_name": lab.name if lab else None,
            "track_name": (
                lab.level.track.name
                if lab and lab.level and lab.level.track else None
            ),
            "completed_at": row.completed_at.isoformat() if row.completed_at else None,
            "time_spent_minutes": row.time_spent_minutes,
            "hints_used": row.hints_used or 0,
            "attempts": row.attempts or 0,
        })
    summary = _student_summary(completions, sessions)
    growth = _growth(completions)
    pulse_rows = _pulse_rows(
        db, {row.lab_id for row in completions}, user_id=current_user.id
    )
    learning_reported = _average([row.learning for row in pulse_rows])
    difficulty_reported = _average([row.difficulty for row in pulse_rows])
    confidence_gain = _confidence_gain(growth)
    summary.update({
        "pulse_responses": len(pulse_rows),
        "learning_reported": learning_reported,
        "difficulty_reported": difficulty_reported,
        "confidence_gain": confidence_gain,
    })
    return {
        "summary": summary,
        "growth": growth,
        "domains": _domain_performance(completions, sessions),
        "ai_prompts": _ai_prompts(summary, growth, recent),
        "learning_impact": {
            "learning_reported": learning_reported,
            "completion_rate": summary["completion_rate"],
            "confidence_gain": confidence_gain,
        },
        "recent_exercises": recent,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/courses/{course_id}/overview")
async def course_overview(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    course = _course_or_403(db, course_id, current_user)
    labs, user_ids, completions, sessions = _course_context(db, course)

    started_users = {row.user_id for row in sessions}
    completed_users = {row.user_id for row in completions}
    learning_pairs = learning_minutes_by_pair(completions, sessions)
    learning_by_user = learning_minutes_by_user(learning_pairs)
    total_learning_minutes = int(sum(learning_by_user.values()))
    active_learning_minutes = [
        value for value in learning_by_user.values() if value > 0
    ]
    reaction_rows = _reaction_rows(db, {lab.id for lab in labs}, course.id)
    reaction_summary = _reaction_fields(reaction_rows)
    total_possible = len(user_ids) * len(labs)
    time_over = sum(
        1 for row in completions
        if row.lab and row.lab.duration_minutes
        and row.time_spent_minutes is not None
        and row.time_spent_minutes > row.lab.duration_minutes
    )
    timed = sum(1 for row in completions if row.time_spent_minutes is not None)
    median_attempts = _median([row.attempts or 0 for row in completions])
    started_pairs = {(row.user_id, row.lab_id) for row in sessions}
    abandonment_rate = _rate(
        max(0, len(started_pairs) - len(completions)), len(started_pairs)
    )
    pulse_rows = _pulse_rows(
        db, {lab.id for lab in labs}, course_id=course.id
    )
    learning_reported = _average([row.learning for row in pulse_rows])
    difficulty_reported = _average([row.difficulty for row in pulse_rows])
    completion_rate = _rate(len(completions), total_possible)
    confidence_gain = _confidence_gain(_growth(completions))
    rag, rag_reasons = _rag_status(
        completion_rate=completion_rate,
        abandonment_rate=abandonment_rate,
        median_attempts=median_attempts,
        learning_reported=learning_reported,
        difficulty_reported=difficulty_reported,
    )

    return {
        "course": {
            "id": course.id,
            "code": course.code,
            "name": course.name,
            "semester": course.semester,
        },
        "summary": {
            "enrolled_learners": len(user_ids),
            "assigned_exercises": len(labs),
            "started_learners": len(started_users),
            "completed_learners": len(completed_users),
            "completion_rate": completion_rate,
            "started_rate": _rate(
                len(started_pairs),
                total_possible,
            ),
            "abandonment_rate": abandonment_rate,
            "median_time_minutes": _median(
                [row.time_spent_minutes for row in completions]
            ),
            "total_learning_minutes": total_learning_minutes,
            "total_learning_hours": round(total_learning_minutes / 60, 1),
            "learning_learners": len(active_learning_minutes),
            "median_learning_minutes_per_learner": _median(active_learning_minutes),
            "time_over_estimate_rate": _rate(time_over, timed),
            **reaction_summary,
            "hints_per_completion": (
                round(
                    sum(row.hints_used or 0 for row in completions)
                    / len(completions), 2
                ) if completions else 0
            ),
            "hint_free_rate": _rate(
                sum(1 for row in completions if (row.hints_used or 0) == 0),
                len(completions),
            ),
            "first_attempt_rate": _rate(
                sum(1 for row in completions if (row.attempts or 0) == 1),
                len(completions),
            ),
            "reattempt_rate": _rate(
                sum(1 for row in completions if (row.attempts or 0) > 1),
                len(completions),
            ),
            "median_attempts": median_attempts,
            "pulse_responses": len(pulse_rows),
            "learning_reported": learning_reported,
            "difficulty_reported": difficulty_reported,
            "confidence_gain": confidence_gain,
            "rag": rag,
            "rag_reasons": rag_reasons,
        },
        "learning_impact": {
            "learning_reported": learning_reported,
            "completion_rate": completion_rate,
            "confidence_gain": confidence_gain,
        },
        "trending_topics": _trending_topics(pulse_rows),
        "domains": _domain_performance(completions, sessions),
        "skill_tree": skill_branch_mix(labs, completions),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _total_skill_tree(rows: list[dict]) -> dict:
    """Aggregate per-course skill-tree mixes for the all-courses radar."""
    assigned = {key: 0 for key in SKILL_BRANCH_ORDER}
    completed = {key: 0 for key in SKILL_BRANCH_ORDER}
    for row in rows:
        tree = row.get("skill_tree") or {}
        for dimension in tree.get("dimensions", []):
            key = dimension.get("key")
            if key in assigned:
                assigned[key] += int(dimension.get("assigned") or 0)
                completed[key] += int(dimension.get("completed") or 0)
    assigned_total = sum(assigned.values())
    completed_total = sum(completed.values())
    return {
        "dimensions": [
            {
                "key": key,
                "label": SKILL_BRANCH_LABELS[key],
                "assigned": assigned[key],
                "completed": completed[key],
                "assigned_pct": _rate(assigned[key], assigned_total),
                "completed_pct": _rate(completed[key], completed_total),
            }
            for key in SKILL_BRANCH_ORDER
        ],
        "assigned_total": assigned_total,
        "completed_total": completed_total,
        "completion_pct": _rate(completed_total, assigned_total),
    }


@router.get("/reports/overview")
async def reports_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Cross-course reporting landing data for instructors and admins."""
    query = db.query(Course).filter(Course.is_active == True)
    if current_user.role != "admin":
        query = query.filter(Course.instructor_id == current_user.id)
    courses = query.order_by(Course.name).all()

    rows = []
    for course in courses:
        detail = await course_overview(course.id, db, current_user)
        rows.append({
            "course": detail["course"],
            "summary": detail["summary"],
            "trending_topics": detail.get("trending_topics", []),
            "skill_tree": detail.get("skill_tree"),
        })

    rag_counts = {"red": 0, "amber": 0, "green": 0}
    topic_counts = Counter()
    for row in rows:
        rag = row["summary"].get("rag")
        if rag in rag_counts:
            rag_counts[rag] += 1
        for topic in row.get("trending_topics", []):
            topic_counts[topic["key"]] += topic["count"]

    trending_topics = [
        {"key": key, "label": TOPIC_INTERESTS.get(key, key), "count": count}
        for key, count in topic_counts.most_common()
    ]

    return {
        "courses": rows,
        "trending_topics": trending_topics,
        "totals": {
            "courses": len(rows),
            "enrolled_learners": sum(
                row["summary"]["enrolled_learners"] for row in rows
            ),
            "assigned_exercises": sum(
                row["summary"]["assigned_exercises"] for row in rows
            ),
            "pulse_responses": sum(
                row["summary"]["pulse_responses"] for row in rows
            ),
            "total_learning_hours": round(
                sum(
                    row["summary"]["total_learning_minutes"]
                    for row in rows
                ) / 60,
                1,
            ),
            "likes": sum(row["summary"]["likes"] for row in rows),
            "dislikes": sum(row["summary"]["dislikes"] for row in rows),
            "reaction_count": sum(
                row["summary"]["reaction_count"] for row in rows
            ),
            "positive_rate": _rate(
                sum(row["summary"]["likes"] for row in rows),
                sum(row["summary"]["reaction_count"] for row in rows),
            ),
            "rag_counts": rag_counts,
            "skill_tree": _total_skill_tree(rows),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


class ReportExportAuditRequest(BaseModel):
    format: str = Field(..., pattern="^(csv|pdf)$")
    reason: str = Field(..., min_length=5, max_length=500)


@router.post("/reports/export-audit")
async def audit_report_export(
    payload: ReportExportAuditRequest,
    request: Request,
    current_user: User = Depends(get_current_instructor_user),
):
    """Record why a report was exported.

    The CSV is assembled in the browser from data the instructor can already
    see, so this endpoint exists to keep the compliance trail complete. The PDF
    path records the same fields directly in ``reports_export_pdf``.
    """
    reason = payload.reason.strip()
    if len(reason) < 5:
        raise HTTPException(
            status_code=400, detail="A reason of at least 5 characters is required."
        )
    log_admin_action(
        action=AuditActions.REPORT_EXPORTED,
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        target_type="report",
        details={
            "format": payload.format,
            "reason": reason,
            "scope": (
                "all_active_courses"
                if current_user.role == "admin"
                else "owned_courses"
            ),
        },
        ip_address=request.client.host if request.client else None,
    )
    return {"ok": True}


@router.get("/reports/export.pdf")
async def reports_export_pdf(
    request: Request,
    reason: str = Depends(require_export_reason),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Download the cross-course report as a PDF."""
    from app.services.analytics_report import generate_reports_pdf

    payload = await reports_overview(db, current_user)
    pdf_bytes = generate_reports_pdf(payload)
    log_admin_action(
        action=AuditActions.REPORT_EXPORTED,
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        target_type="report",
        details={
            "format": "pdf",
            "reason": reason,
            "scope": (
                "all_active_courses"
                if current_user.role == "admin"
                else "owned_courses"
            ),
            "course_count": len(payload.get("courses", [])),
        },
        ip_address=request.client.host if request.client else None,
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="learning-reports.pdf"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/courses/{course_id}/exercises")
async def course_exercises(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    course = _course_or_403(db, course_id, current_user)
    labs, user_ids, completions, sessions = _course_context(db, course)
    enrolled = len(user_ids)

    by_lab_completions = {}
    for row in completions:
        by_lab_completions.setdefault(row.lab_id, []).append(row)
    by_lab_sessions = {}
    for row in sessions:
        by_lab_sessions.setdefault(row.lab_id, set()).add(row.user_id)
    session_start_map = {}
    for row in sessions:
        if row.started_at is None:
            continue
        key = (row.user_id, row.lab_id)
        if key not in session_start_map or row.started_at < session_start_map[key]:
            session_start_map[key] = row.started_at
    attempt_rows = db.query(
        FlagAttempt.user_id,
        FlagAttempt.lab_id,
        func.min(FlagAttempt.attempted_at),
    ).filter(
        FlagAttempt.user_id.in_(user_ids),
        FlagAttempt.lab_id.in_({lab.id for lab in labs}),
    ).group_by(FlagAttempt.user_id, FlagAttempt.lab_id).all()
    first_attempt_map = {
        (user_id, lab_id): attempted_at
        for user_id, lab_id, attempted_at in attempt_rows
    }
    by_lab_pulse = {}
    for row in _pulse_rows(db, {lab.id for lab in labs}, course_id=course.id):
        by_lab_pulse.setdefault(row.lab_id, []).append(row)
    learning_pairs = learning_minutes_by_pair(completions, sessions)
    by_lab_reactions = {}
    for row in _reaction_rows(db, {lab.id for lab in labs}, course.id):
        by_lab_reactions.setdefault(row.lab_id, []).append(row)

    rows = []
    for lab in labs:
        lab_completions = by_lab_completions.get(lab.id, [])
        lab_pulse = by_lab_pulse.get(lab.id, [])
        lab_learning_minutes = sum(
            value for (_user_id, lab_id), value in learning_pairs.items()
            if lab_id == lab.id
        )
        lab_reaction_summary = _reaction_fields(
            by_lab_reactions.get(lab.id, [])
        )
        completed_users = {row.user_id for row in lab_completions}
        started_users = by_lab_sessions.get(lab.id, set())
        attempts = [row.attempts or 0 for row in lab_completions]
        hint_pressure = _rate(
            sum(1 for row in lab_completions if (row.hints_used or 0) > 0),
            len(lab_completions),
        )
        completion_rate = _rate(len(completed_users), enrolled)
        started_completion = _rate(len(completed_users), len(started_users))
        abandonment_rate = _rate(
            max(0, len(started_users) - len(completed_users)),
            len(started_users),
        )
        median_attempts = _median(attempts)
        learning_reported = _average([row.learning for row in lab_pulse])
        difficulty_reported = _average([row.difficulty for row in lab_pulse])
        first_attempt_gaps = []
        for (uid, lid), attempted_at in first_attempt_map.items():
            if lid != lab.id or attempted_at is None:
                continue
            started = session_start_map.get((uid, lid))
            if started is not None and attempted_at >= started:
                first_attempt_gaps.append(
                    (attempted_at - started).total_seconds() / 60
                )
        completion_gaps = []
        for row in lab_completions:
            started = session_start_map.get((row.user_id, row.lab_id))
            if started is not None and row.completed_at and row.completed_at >= started:
                completion_gaps.append(
                    (row.completed_at - started).total_seconds() / 60
                )
        rag, rag_reasons = _rag_status(
            completion_rate=completion_rate,
            abandonment_rate=abandonment_rate,
            median_attempts=median_attempts,
            learning_reported=learning_reported,
            difficulty_reported=difficulty_reported,
        )
        flags = []
        if hint_pressure >= 50 and lab_completions:
            flags.append("high_hint_pressure")
        if median_attempts is not None and median_attempts >= 3:
            flags.append("high_attempt_burden")
        if started_users and completion_rate < 50:
            flags.append("low_completion")
        rows.append({
            "lab_id": lab.id,
            "lab_name": lab.name,
            "slug": lab.slug,
            "difficulty": lab.difficulty,
            "duration_minutes": lab.duration_minutes,
            "track_name": (
                lab.level.track.name
                if lab.level and lab.level.track else "Uncategorized"
            ),
            "level_name": lab.level.name if lab.level else None,
            "started_learners": len(started_users),
            "completed_learners": len(completed_users),
            "completion_rate": completion_rate,
            "started_completion_rate": started_completion,
            "abandonment_rate": abandonment_rate,
            "median_time_minutes": _median(
                [row.time_spent_minutes for row in lab_completions]
            ),
            "total_learning_minutes": int(lab_learning_minutes),
            "total_learning_hours": round(lab_learning_minutes / 60, 1),
            **lab_reaction_summary,
            "median_attempts": median_attempts,
            "hint_pressure_rate": hint_pressure,
            "first_attempt_rate": _rate(
                sum(1 for row in lab_completions if (row.attempts or 0) == 1),
                len(lab_completions),
            ),
            "reattempt_recovery_rate": _rate(
                sum(1 for row in lab_completions if (row.attempts or 0) > 1),
                len(lab_completions),
            ),
            "pulse_responses": len(lab_pulse),
            "pulse_response_rate": _rate(len(lab_pulse), len(lab_completions)),
            "learning_reported": learning_reported,
            "difficulty_reported": difficulty_reported,
            "unclear_comments": sum(1 for row in lab_pulse if row.unclear),
            "median_time_to_first_attempt_minutes": _median(first_attempt_gaps),
            "median_time_to_completion_minutes": _median(completion_gaps),
            "rag": rag,
            "rag_reasons": rag_reasons,
            "flags": flags,
        })

    rows.sort(key=lambda row: (-row["started_learners"], row["lab_name"].lower()))
    return {
        "course": {"id": course.id, "code": course.code, "name": course.name},
        "exercises": rows,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/courses/{course_id}/pulse-comments")
async def course_pulse_comments(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    course = _course_or_403(db, course_id, current_user)
    lab_ids = [
        row[0] for row in db.query(CourseLabAssignment.lab_id).filter(
            CourseLabAssignment.course_id == course.id
        ).all()
    ]
    rows = db.query(ExercisePulseSurvey).options(
        joinedload(ExercisePulseSurvey.lab),
        joinedload(ExercisePulseSurvey.user),
    ).filter(
        ExercisePulseSurvey.course_id == course.id,
        ExercisePulseSurvey.lab_id.in_(lab_ids),
        ExercisePulseSurvey.unclear.isnot(None),
        ExercisePulseSurvey.unclear != "",
    ).order_by(ExercisePulseSurvey.updated_at.desc()).limit(100).all()
    return {
        "course": {"id": course.id, "code": course.code, "name": course.name},
        "comments": [
            {
                "lab_id": row.lab_id,
                "lab_name": row.lab.name if row.lab else None,
                "display_name": row.user.display_name if row.user else "Unknown learner",
                "difficulty": row.difficulty,
                "learning": row.learning,
                "unclear": row.unclear,
                "submitted_at": (
                    row.updated_at.isoformat() if row.updated_at else None
                ),
            }
            for row in rows
        ],
    }


@router.post("/events/workbook-open")
async def workbook_opened(
    payload: WorkbookOpenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    log_activity(
        db,
        EventTypes.WORKBOOK_OPENED,
        actor_id=current_user.id,
        target_type="workbook",
        target_label=(payload.title or payload.url or "Workbook")[:200],
        detail={"url": payload.url} if payload.url else None,
        commit=True,
    )
    return {"message": "Workbook activity recorded"}


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
        "updated_at": (
            row.updated_at.isoformat()
            if row and row.updated_at else None
        ),
    }


@router.post("/reaction/{lab_id}")
async def set_exercise_reaction(
    lab_id: int,
    payload: ExerciseReactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create, change, or clear a learner's reaction to an exercise.

    One reaction is kept per learner and exercise. Passing ``null`` clears it.
    Reports only aggregate likes and dislikes; they never show who reacted.
    """
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


@router.get("/pulse/{lab_id}")
async def get_pulse(
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = _pulse_rows(db, {lab_id}, user_id=current_user.id)
    row = rows[0] if rows else None
    return {
        "submitted": row is not None,
        "pulse": (
            {
                "difficulty": row.difficulty,
                "learning": row.learning,
                "unclear": row.unclear,
                "topic_interest": row.topic_interest,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            } if row else None
        ),
    }


@router.post("/pulse/{lab_id}")
async def submit_pulse(
    lab_id: int,
    payload: PulseSurveyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if not getattr(current_user, "survey_opt_in", False):
        raise HTTPException(
            status_code=403,
            detail="Survey participation requires opting in under Privacy and data",
        )

    completion = db.query(LabCompletion).filter(
        LabCompletion.user_id == current_user.id,
        LabCompletion.lab_id == lab_id,
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).first()
    if not completion:
        raise HTTPException(
            status_code=400,
            detail="Complete the exercise before submitting pulse feedback",
        )

    if payload.course_id is not None:
        enrolled = db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == payload.course_id,
            CourseEnrollment.user_id == current_user.id,
        ).first()
        if not enrolled:
            raise HTTPException(status_code=403, detail="Not enrolled in that course")

    if payload.topic_interest and payload.topic_interest not in TOPIC_INTERESTS:
        raise HTTPException(status_code=400, detail="Unknown topic interest")

    row = db.query(ExercisePulseSurvey).filter(
        ExercisePulseSurvey.user_id == current_user.id,
        ExercisePulseSurvey.lab_id == lab_id,
    ).first()
    if row is None:
        row = ExercisePulseSurvey(
            user_id=current_user.id,
            lab_id=lab_id,
        )
        db.add(row)
    row.course_id = payload.course_id
    row.difficulty = payload.difficulty
    row.learning = payload.learning
    row.unclear = (payload.unclear or "").strip() or None
    row.topic_interest = payload.topic_interest
    db.commit()
    return {"message": "Pulse feedback saved"}


def _survey_questions(survey: Survey) -> list:
    try:
        return json.loads(survey.questions or "[]")
    except (TypeError, ValueError):
        return []


def _survey_owner_or_403(db: Session, survey_id: int, current_user: User) -> Survey:
    survey = db.query(Survey).options(
        joinedload(Survey.attachments).joinedload(SurveyAttachment.course),
    ).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if current_user.role != "admin" and survey.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to manage this survey")
    return survey


def _survey_payload(db: Session, survey: Survey, response_count: int) -> dict:
    return {
        "id": survey.id,
        "title": survey.title,
        "description": survey.description,
        "questions": _survey_questions(survey),
        "is_active": bool(survey.is_active),
        "created_at": survey.created_at.isoformat() if survey.created_at else None,
        "response_count": response_count,
        "courses": [
            {
                "id": attachment.course.id,
                "code": attachment.course.code,
                "name": attachment.course.name,
            }
            for attachment in survey.attachments
            if attachment.course
        ],
    }


@router.get("/surveys")
async def list_surveys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    query = db.query(Survey).options(
        joinedload(Survey.attachments).joinedload(SurveyAttachment.course),
    )
    if current_user.role != "admin":
        query = query.filter(Survey.created_by == current_user.id)
    surveys = query.order_by(Survey.created_at.desc()).all()
    counts = dict(
        db.query(SurveyResponse.survey_id, func.count(SurveyResponse.id))
        .group_by(SurveyResponse.survey_id)
        .all()
    )
    return {
        "surveys": [
            _survey_payload(db, survey, counts.get(survey.id, 0))
            for survey in surveys
        ]
    }


@router.post("/surveys")
async def create_survey(
    payload: SurveyCreateInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    course_ids = list(dict.fromkeys(payload.course_ids))
    query = db.query(Course).filter(Course.id.in_(course_ids))
    if current_user.role != "admin":
        query = query.filter(Course.instructor_id == current_user.id)
    courses = query.all()
    if len(courses) != len(course_ids):
        raise HTTPException(status_code=403, detail="One or more courses are not yours")

    try:
        questions = [question.normalized() for question in payload.questions]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    survey = Survey(
        title=payload.title.strip(),
        description=(payload.description or "").strip() or None,
        questions=json.dumps(questions),
        created_by=current_user.id,
        is_active=True,
    )
    db.add(survey)
    db.flush()
    for course in courses:
        db.add(SurveyAttachment(survey_id=survey.id, course_id=course.id))
    db.commit()
    return {"message": "Survey created", "id": survey.id}


@router.get("/surveys/available")
async def available_surveys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course_ids = {
        row[0] for row in db.query(CourseEnrollment.course_id).filter(
            CourseEnrollment.user_id == current_user.id
        ).all()
    }
    if not course_ids:
        return {"surveys": []}
    if not getattr(current_user, "survey_opt_in", False):
        return {"surveys": [], "reason": "opt_in_required"}
    attachments = db.query(SurveyAttachment).options(
        joinedload(SurveyAttachment.survey),
        joinedload(SurveyAttachment.course),
    ).filter(
        SurveyAttachment.course_id.in_(course_ids)
    ).all()
    responded = {
        row[0] for row in db.query(SurveyResponse.survey_id).filter(
            SurveyResponse.user_id == current_user.id
        ).all()
    }
    surveys = []
    for attachment in attachments:
        survey = attachment.survey
        if not survey or not survey.is_active or survey.id in responded:
            continue
        surveys.append({
            **_survey_payload(db, survey, 0),
            "attachment_id": attachment.id,
            "course": {
                "id": attachment.course.id,
                "code": attachment.course.code,
                "name": attachment.course.name,
            },
        })
    return {"surveys": surveys}


@router.post("/surveys/{survey_id}/responses")
async def submit_survey_response(
    survey_id: int,
    payload: SurveyResponseInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey or not survey.is_active:
        raise HTTPException(status_code=404, detail="Survey not available")
    if not getattr(current_user, "survey_opt_in", False):
        raise HTTPException(
            status_code=403,
            detail="Survey participation requires opting in under Privacy and data",
        )
    course_ids = {
        row[0] for row in db.query(SurveyAttachment.course_id).filter(
            SurveyAttachment.survey_id == survey_id
        ).all()
    }
    enrolled = db.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == current_user.id,
        CourseEnrollment.course_id.in_(course_ids),
    ).first()
    if not enrolled:
        raise HTTPException(status_code=403, detail="You are not enrolled in this survey's course")

    questions = _survey_questions(survey)
    answers = {}
    for index, question in enumerate(questions):
        key = str(index)
        value = payload.answers.get(key)
        if value is None or value == "":
            raise HTTPException(
                status_code=400,
                detail=f"Question {index + 1} requires an answer",
            )
        if question["type"] == "scale":
            try:
                number = int(value)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail=f"Question {index + 1} must be a number")
            if number < 1 or number > 5:
                raise HTTPException(status_code=400, detail=f"Question {index + 1} must be 1-5")
            answers[key] = number
        elif question["type"] == "choice":
            if str(value) not in question["options"]:
                raise HTTPException(status_code=400, detail=f"Question {index + 1} has an invalid option")
            answers[key] = str(value)
        else:
            text = str(value).strip()
            if not text or len(text) > 2000:
                raise HTTPException(status_code=400, detail=f"Question {index + 1} text is invalid")
            answers[key] = text

    row = db.query(SurveyResponse).filter(
        SurveyResponse.survey_id == survey_id,
        SurveyResponse.user_id == current_user.id,
    ).first()
    if row is None:
        row = SurveyResponse(
            survey_id=survey_id,
            user_id=current_user.id,
            course_id=enrolled.course_id,
        )
        db.add(row)
    else:
        row.course_id = enrolled.course_id
        row.submitted_at = datetime.now(timezone.utc)
    row.answers = json.dumps(answers)
    db.commit()
    return {"message": "Survey response saved"}


@router.get("/surveys/{survey_id}/responses")
async def survey_responses(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    survey = _survey_owner_or_403(db, survey_id, current_user)
    questions = _survey_questions(survey)
    rows = db.query(SurveyResponse).options(
        joinedload(SurveyResponse.user),
        joinedload(SurveyResponse.course),
    ).filter(SurveyResponse.survey_id == survey.id).order_by(
        SurveyResponse.submitted_at.desc()
    ).all()

    responses = []
    summary = {}
    for row in rows:
        try:
            answers = json.loads(row.answers or "{}")
        except (TypeError, ValueError):
            answers = {}
        responses.append({
            "user_id": row.user_id,
            "display_name": row.user.display_name if row.user else "Unknown learner",
            "course_code": row.course.code if row.course else None,
            "answers": answers,
            "submitted_at": row.submitted_at.isoformat() if row.submitted_at else None,
        })
        for index, question in enumerate(questions):
            key = str(index)
            entry = summary.setdefault(key, {
                "prompt": question["prompt"],
                "type": question["type"],
                "counts": {},
                "texts": [],
            })
            value = answers.get(key)
            if value is None:
                continue
            if question["type"] == "text":
                if len(entry["texts"]) < 20:
                    entry["texts"].append(str(value))
            else:
                entry["counts"][str(value)] = entry["counts"].get(str(value), 0) + 1

    return {
        "survey": _survey_payload(db, survey, len(rows)),
        "summary": summary,
        "responses": responses,
    }


@router.delete("/surveys/{survey_id}")
async def delete_survey(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    survey = _survey_owner_or_403(db, survey_id, current_user)
    db.delete(survey)
    db.commit()
    return {"message": "Survey deleted"}
