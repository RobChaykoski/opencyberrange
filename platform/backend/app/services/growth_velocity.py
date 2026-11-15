"""Growth velocity: how a learner's practice is changing over time.

The Cyber DNA report answers "what am I like"; growth velocity answers "am I
getting better". It is a personal, within-learner view. It never compares one
learner with another and it never feeds a ranking.

Signals (last 30 days versus the 30 days before that):

- improvement: completions in the current window versus the prior window;
- hint discipline: hints per completion (lower is better);
- challenge stretch: average difficulty of the labs completed;
- consistency: distinct active days and weeks with at least one completion.

The same measures are also exposed as 30/60/90-day windows for trend charts.

Privacy and anti-gaming rules:

- One completion per learner and lab (enforced by the database), so counts
  cannot be inflated by replaying the same lab.
- Difficulty comes from the snapshot stored on the completion, so a later
  catalog edit cannot rewrite history in the learner's favour.
- Hints and attempts are recorded by the lab lifecycle, not by the learner.
- Percentages are only produced with a denominator of at least three; below
  that the caller receives counts and an explicit confidence label.
- The response is scoped to the requesting learner. There is no cohort
  comparison here.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from sqlalchemy.orm import Session, joinedload

from app.models import LabCompletion

WINDOW_DAYS = 30
TREND_WINDOWS = (30, 60, 90)
GROWTH_VERSION = "2026.1"
DIFFICULTY_WEIGHT = {
    "beginner": 1.0,
    "intermediate": 2.0,
    "advanced": 3.0,
    "expert": 4.0,
}
DIFFICULTY_LABEL = {
    1: "Beginner",
    2: "Intermediate",
    3: "Advanced",
    4: "Expert",
}

# Minimum number of distinct solved labs before a learner sees a percentage or
# a named career direction. Below this the UI shows counts and a next step.
MIN_PERCENT_EVIDENCE = 3
MIN_CAREER_EVIDENCE = 8


def _naive_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _difficulty(row) -> float:
    snapshot = (getattr(row, "lab_difficulty_snapshot", None) or "").strip().lower()
    if snapshot in DIFFICULTY_WEIGHT:
        return DIFFICULTY_WEIGHT[snapshot]
    lab = getattr(row, "lab", None)
    value = (getattr(lab, "difficulty", None) or "").strip().lower()
    return DIFFICULTY_WEIGHT.get(value, 1.0)


def _completed_at(row) -> datetime | None:
    return getattr(row, "completed_at", None)


def summarise_completions(
    rows: Iterable,
    start: datetime,
    end: datetime,
) -> dict:
    """Summarise one window. Rows are duck-typed for easy unit testing."""
    window = []
    for row in rows:
        completed = _completed_at(row)
        if completed is None:
            continue
        if start <= completed < end:
            window.append(row)

    completions = len(window)
    hints = sum(max(int(getattr(row, "hints_used", 0) or 0), 0) for row in window)
    difficulty = sum(_difficulty(row) for row in window)
    days = {
        _completed_at(row).date()
        for row in window
        if _completed_at(row) is not None
    }
    weeks = {day.isocalendar()[:2] for day in days}
    unique_labs = {getattr(row, "lab_id", id(row)) for row in window}

    return {
        "completions": completions,
        "unique_labs": len(unique_labs),
        "hints_per_completion": round(hints / completions, 2) if completions else 0.0,
        "avg_difficulty": round(difficulty / completions, 2) if completions else 0.0,
        "active_days": len(days),
        "active_weeks": len(weeks),
        "hint_free": sum(
            1
            for row in window
            if int(getattr(row, "hints_used", 0) or 0) == 0
        ),
    }


def _direction(delta: float, *, lower_is_better: bool = False) -> str:
    if abs(delta) < 1e-9:
        return "flat"
    improved = delta < 0 if lower_is_better else delta > 0
    return "up" if improved else "down"


def _difficulty_label(value: float) -> str:
    if value <= 0:
        return "No evidence yet"
    nearest = min(DIFFICULTY_LABEL, key=lambda key: abs(key - value))
    return DIFFICULTY_LABEL[nearest]


def confidence_for(evidence_labs: int) -> dict:
    """Label how much evidence sits behind a recommendation."""
    if evidence_labs < MIN_PERCENT_EVIDENCE:
        level, label = "starting", "Not enough evidence yet"
    elif evidence_labs < MIN_CAREER_EVIDENCE:
        level, label = "early", "Early signal"
    elif evidence_labs < 15:
        level, label = "building", "Building evidence"
    else:
        level, label = "established", "Established pattern"
    return {
        "level": level,
        "label": label,
        "evidence_labs": evidence_labs,
        "career_ready": evidence_labs >= MIN_CAREER_EVIDENCE,
        "percent_ready": evidence_labs >= MIN_PERCENT_EVIDENCE,
    }


def _trend_series(rows: Iterable, now: datetime) -> list[dict]:
    series = []
    for days in TREND_WINDOWS:
        start = now - timedelta(days=days)
        summary = summarise_completions(rows, start, now)
        series.append(
            {
                "days": days,
                "completions": summary["completions"],
                "hints_per_completion": summary["hints_per_completion"],
                "avg_difficulty": summary["avg_difficulty"],
                "active_days": summary["active_days"],
            }
        )
    return series


def _opportunities(
    current: dict,
    prior: dict,
    evidence_labs: int,
    hint_delta: float,
    difficulty_delta: float,
) -> list[dict]:
    opportunities = []

    if evidence_labs < MIN_PERCENT_EVIDENCE:
        opportunities.append(
            {
                "key": "start",
                "label": "Start with three short exercises",
                "detail": "Finish the starter set before reading trends; one lab is not a pattern.",
                "action": "Open your starter path",
                "route": "/discover",
                "priority": 1,
            }
        )
        return opportunities

    if current["hints_per_completion"] >= 1 or hint_delta > 0:
        opportunities.append(
            {
                "key": "hints",
                "label": "Try one hint-free solve",
                "detail": "Hints are useful, but they also cap what the exercise teaches you.",
                "action": "Find a beginner exercise",
                "route": "/exercises",
                "priority": 2,
            }
        )

    if current["avg_difficulty"] < 2 and current["completions"] >= 3:
        opportunities.append(
            {
                "key": "stretch",
                "label": "Step up to an intermediate exercise",
                "detail": "Your recent work is all beginner level. A small stretch builds new evidence.",
                "action": "Browse intermediate labs",
                "route": "/exercises",
                "priority": 2,
            }
        )

    if current["active_weeks"] < 2:
        opportunities.append(
            {
                "key": "consistency",
                "label": "Book two short sessions this week",
                "detail": "Consistency moves the DNA more than one long session.",
                "action": "Pick a 30-minute exercise",
                "route": "/exercises",
                "priority": 3,
            }
        )

    if current["completions"] == 0 and prior["completions"] > 0:
        opportunities.append(
            {
                "key": "return",
                "label": "Restart with a familiar track",
                "detail": "You have prior evidence; one completed lab restores the recent signal.",
                "action": "Resume your strongest track",
                "route": "/dashboard",
                "priority": 1,
            }
        )

    if not opportunities:
        opportunities.append(
            {
                "key": "keep-going",
                "label": "Keep the current cadence",
                "detail": "Difficulty and consistency are both moving in the right direction.",
                "action": "Browse the next level",
                "route": "/exercises",
                "priority": 4,
            }
        )

    return sorted(opportunities, key=lambda item: item["priority"])


def build_growth_velocity(db: Session, user) -> dict:
    """Return the four growth signals, 30/60/90 trends, and next opportunities."""
    now = _naive_utc_now()
    current_start = now - timedelta(days=WINDOW_DAYS)
    prior_start = current_start - timedelta(days=WINDOW_DAYS)
    trend_start = now - timedelta(days=max(TREND_WINDOWS))

    rows = (
        db.query(LabCompletion)
        .options(joinedload(LabCompletion.lab))
        .filter(
            LabCompletion.user_id == user.id,
            LabCompletion.completed_at >= trend_start,
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        )
        .all()
    )

    current = summarise_completions(rows, current_start, now)
    prior = summarise_completions(rows, prior_start, current_start)
    lifetime_rows = (
        db.query(LabCompletion.lab_id)
        .filter(
            LabCompletion.user_id == user.id,
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        )
        .distinct()
        .count()
    )
    confidence = confidence_for(lifetime_rows)

    completion_delta = current["completions"] - prior["completions"]
    completion_pct = (
        round(completion_delta / prior["completions"] * 100)
        if prior["completions"] >= MIN_PERCENT_EVIDENCE
        else None
    )
    hint_delta = round(
        current["hints_per_completion"] - prior["hints_per_completion"], 2
    )
    difficulty_delta = round(
        current["avg_difficulty"] - prior["avg_difficulty"], 2
    )

    signals = [
        {
            "key": "improvement",
            "label": "Improvement over time",
            "value": (
                f"{completion_delta:+d} labs vs prior 30 days"
                if prior["completions"] and completion_delta
                else (
                    "Same pace as the prior 30 days"
                    if prior["completions"]
                    else f"{current['completions']} labs in the last 30 days"
                )
            ),
            "direction": _direction(completion_delta),
            "detail": (
                f"{completion_pct:+d}% change"
                if completion_pct is not None
                else "Not enough prior evidence for a percentage"
            ),
        },
        {
            "key": "hints",
            "label": "Hint discipline",
            "value": (
                f"{current['hints_per_completion']:.2f} hints per lab"
                if current["completions"]
                else "No completions yet"
            ),
            "direction": _direction(hint_delta, lower_is_better=True),
            "detail": (
                f"{current['hint_free']} of {current['completions']} solved without hints"
                if current["completions"]
                else "Solve a lab to start the signal"
            ),
        },
        {
            "key": "difficulty",
            "label": "Challenge stretch",
            "value": _difficulty_label(current["avg_difficulty"]),
            "direction": _direction(difficulty_delta),
            "detail": (
                f"From {_difficulty_label(prior['avg_difficulty'])} in the prior window"
                if prior["completions"]
                else "Baseline window"
            ),
        },
        {
            "key": "consistency",
            "label": "Consistency",
            "value": f"{current['active_days']} active days",
            "direction": "up" if current["active_weeks"] >= 3 else "flat",
            "detail": f"{current['active_weeks']} active weeks in the last 30 days",
        },
    ]

    if current["completions"] < 2:
        state = "starting"
    elif completion_delta > 0 or difficulty_delta > 0 or hint_delta < 0:
        state = "improving"
    elif completion_delta < 0:
        state = "slowing"
    else:
        state = "steady"

    return {
        "version": GROWTH_VERSION,
        "factor_weights": {
            "window_days": WINDOW_DAYS,
            "trend_windows": list(TREND_WINDOWS),
            "difficulty": DIFFICULTY_WEIGHT,
            "min_percent_evidence": MIN_PERCENT_EVIDENCE,
            "min_career_evidence": MIN_CAREER_EVIDENCE,
        },
        "window_days": WINDOW_DAYS,
        "state": state,
        "confidence": confidence,
        "current": current,
        "prior": prior,
        "trend": _trend_series(rows, now),
        "deltas": {
            "completions": completion_delta,
            "completions_pct": completion_pct,
            "hints_per_completion": hint_delta,
            "avg_difficulty": difficulty_delta,
        },
        "signals": signals,
        "opportunities": _opportunities(
            current,
            prior,
            lifetime_rows,
            hint_delta,
            difficulty_delta,
        ),
    }
