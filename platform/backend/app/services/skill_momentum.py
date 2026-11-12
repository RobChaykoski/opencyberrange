"""Momentum and friction: a derived layer on top of Cyber DNA.

The six Cyber DNA scores are deliberately unchanged. This module answers a
different question from the same records:

* Where is practice gaining? (recent work compared with earlier work)
* Where is practice under friction? (hints, reattempts, time over estimate,
  and exercises that were started but never finished)

The output is descriptive and private to the learner. It is not a grade, a
ranking, a prediction, or a claim about ability. A missing signal is reported
as "no evidence yet", never as a zero.

Formula version ``2026.1``. The friction score is a transparent weighted mix of
four observable rates. It is not part of the Cyber DNA formula and does not
change the learner's trait scores.
"""

from __future__ import annotations

from statistics import median
from typing import Iterable, Optional

from sqlalchemy.orm import Session, joinedload

from app.models import Lab, LabCompletion, LabSession, Level, User
from app.services.skill_dna import DIMENSIONS, DIMENSION_BY_KEY, skill_branch_for_lab

MOMENTUM_VERSION = "2026.1"

FRICTION_WEIGHTS = {
    "hint": 0.35,
    "reattempt": 0.35,
    "unfinished": 0.20,
    "time": 0.10,
}

STATUS_LABELS = {
    "gaining": "Gaining",
    "steady": "Steady",
    "friction": "Friction",
    "no_evidence": "No evidence yet",
}


def _percent(part: int, total: int) -> float:
    return round(part / total * 100, 1) if total else 0.0


def _median(values: Iterable[float]) -> Optional[float]:
    items = [value for value in values if value is not None]
    if not items:
        return None
    return round(float(median(items)), 1)


def _clean(row: LabCompletion) -> bool:
    return (row.hints_used or 0) == 0 and (row.attempts or 1) <= 1


def _time_ratio(row: LabCompletion, lab: Optional[Lab]) -> Optional[float]:
    minutes = row.time_spent_minutes or 0
    estimate = getattr(lab, "duration_minutes", None) or 0
    if minutes <= 0 or estimate <= 0:
        return None
    return round(minutes / estimate, 2)


def _movement(items: list[dict]) -> dict:
    """Compare the recent half of completions with the earlier half."""
    if len(items) < 2:
        return {
            "delta": None,
            "earlier_clean_rate": None,
            "recent_clean_rate": None,
            "label": "Not enough evidence yet",
        }
    split = len(items) // 2
    earlier = items[:split] or items[:1]
    recent = items[split:] or items[-1:]
    earlier_rate = _percent(sum(1 for item in earlier if item["clean"]), len(earlier))
    recent_rate = _percent(sum(1 for item in recent if item["clean"]), len(recent))
    delta = round(recent_rate - earlier_rate, 1)
    if delta >= 8:
        label = f"Up {delta:g} points"
    elif delta <= -8:
        label = f"Down {abs(delta):g} points"
    else:
        label = "Steady"
    return {
        "delta": delta,
        "earlier_clean_rate": earlier_rate,
        "recent_clean_rate": recent_rate,
        "label": label,
    }


def _friction_score(
    *,
    hint_rate: float,
    first_attempt_rate: float,
    unfinished_rate: float,
    time_ratio: Optional[float],
) -> int:
    time_pressure = 0.0
    if time_ratio is not None:
        time_pressure = min(max(time_ratio - 1.0, 0.0) / 1.5, 1.0)
    score = (
        FRICTION_WEIGHTS["hint"] * (hint_rate / 100)
        + FRICTION_WEIGHTS["reattempt"] * (1 - first_attempt_rate / 100)
        + FRICTION_WEIGHTS["unfinished"] * (unfinished_rate / 100)
        + FRICTION_WEIGHTS["time"] * time_pressure
    )
    return max(0, min(100, round(score * 100)))


def _next_action(
    *,
    label: str,
    completed: int,
    started: int,
    unfinished: int,
    hint_rate: float,
    first_attempt_rate: float,
    time_ratio: Optional[float],
    status: str,
) -> str:
    if completed == 0 and started > 0:
        return (
            f"You opened {started} {label} exercise{'s' if started != 1 else ''} "
            "but have not finished one. Complete the shortest open exercise before "
            "starting a new branch."
        )
    if hint_rate >= 50:
        return (
            f"Hints carried {hint_rate:g}% of your {label} work. Retry one exercise "
            "with hints closed, then write down the step that unlocked it."
        )
    if first_attempt_rate < 50:
        return (
            f"{first_attempt_rate:g}% of your {label} completions landed on the "
            "first attempt. Plan the next attempt in three checkpoints before "
            "submitting."
        )
    if time_ratio is not None and time_ratio > 1.5:
        return (
            f"Your median {label} exercise took {time_ratio:g}x its estimate. "
            "Time-box the next one to the estimate and stop at the first blocker."
        )
    if unfinished:
        return (
            f"{unfinished} {label} exercise{'s are' if unfinished != 1 else ' is'} "
            "open. Finish one before adding a new branch."
        )
    if status == "gaining":
        return f"Keep the current pace and add one stretch exercise in {label}."
    return f"Complete one more {label} exercise to give the signal more evidence."


_DIFFICULTY_ORDER = {
    "beginner": 0,
    "intermediate": 1,
    "advanced": 2,
    "expert": 3,
}


def next_labs_for_user(db: Session, user: User) -> dict[str, dict]:
    """Return one open public exercise per Skill DNA branch.

    The suggestion is the easiest uncompleted public exercise in the branch,
    ordered by difficulty and then curriculum order. It is a practice prompt,
    not a requirement or a prediction. Course-only labs are deliberately
    excluded so the link never bypasses course enrolment.
    """
    completed_ids = {
        row[0]
        for row in db.query(LabCompletion.lab_id)
        .filter(LabCompletion.user_id == user.id)
        .distinct()
        .all()
    }
    labs = (
        db.query(Lab)
        .options(joinedload(Lab.level).joinedload(Level.track))
        .filter(Lab.is_active == True, Lab.visibility == "public")
        .all()
    )
    best: dict[str, tuple] = {}
    for lab in labs:
        if lab.id in completed_ids:
            continue
        level = getattr(lab, "level", None)
        track = getattr(level, "track", None) if level else None
        if track is None:
            continue
        branch = skill_branch_for_lab(lab)
        key = (
            _DIFFICULTY_ORDER.get((lab.difficulty or "").strip().lower(), 9),
            lab.sort_order or 0,
            lab.id,
        )
        if branch not in best or key < best[branch][0]:
            best[branch] = (key, lab, track)
    return {
        branch: {
            "name": lab.name,
            "slug": lab.slug,
            "track_slug": track.slug,
            "track_name": track.name,
            "level_id": lab.level_id,
            "difficulty": lab.difficulty,
            "duration_minutes": lab.duration_minutes,
        }
        for branch, (_key, lab, track) in best.items()
    }


def _stuck_points(
    *,
    branch_items: dict[str, list[dict]],
    unfinished_by_branch: dict[str, list[dict]],
) -> list[dict]:
    points: dict[int, dict] = {}

    for branch, labs in unfinished_by_branch.items():
        for entry in labs:
            lab: Lab = entry["lab"]
            points[lab.id] = {
                "lab": lab.name,
                "branch": DIMENSION_BY_KEY[branch].label,
                "reason": "Started but not finished",
                "evidence": (
                    f"{entry['starts']} start{'s' if entry['starts'] != 1 else ''}, "
                    "no completion"
                ),
                "_severity": 20 + entry["starts"] * 4,
            }

    for branch, items in branch_items.items():
        for item in items:
            row = item["row"]
            lab = item["lab"]
            if lab is None:
                continue
            severity = 0
            reason = ""
            evidence = ""
            if (row.hints_used or 0) >= 2:
                severity = 30 + (row.hints_used or 0) * 3
                reason = "High hint use"
                evidence = f"{row.hints_used} hints on {lab.name}"
            elif (row.attempts or 1) >= 3:
                severity = 30 + (row.attempts or 1) * 3
                reason = "Needed repeated attempts"
                evidence = f"{row.attempts} attempts on {lab.name}"
            elif item["time_ratio"] is not None and item["time_ratio"] >= 2:
                severity = 30 + round(item["time_ratio"] * 4)
                reason = "Took much longer than estimated"
                evidence = (
                    f"{row.time_spent_minutes} min against a "
                    f"{getattr(lab, 'duration_minutes', 0)} min estimate"
                )
            if not severity:
                continue
            existing = points.get(lab.id)
            if existing and existing["_severity"] >= severity:
                continue
            points[lab.id] = {
                "lab": lab.name,
                "branch": DIMENSION_BY_KEY[branch].label,
                "reason": reason,
                "evidence": evidence,
                "_severity": severity,
            }

    ordered = sorted(points.values(), key=lambda row: -row["_severity"])[:3]
    for row in ordered:
        row.pop("_severity", None)
    return ordered


def build_momentum(db: Session, user: User) -> dict:
    """Return the learner's Momentum and friction snapshot."""
    completions = (
        db.query(LabCompletion)
        .options(
            joinedload(LabCompletion.lab)
            .joinedload(Lab.level)
            .joinedload(Level.track)
        )
        .filter(
            LabCompletion.user_id == user.id,
            LabCompletion.completed_at.isnot(None),
        )
        .order_by(LabCompletion.completed_at.asc(), LabCompletion.id.asc())
        .all()
    )
    sessions = (
        db.query(LabSession)
        .options(joinedload(LabSession.lab).joinedload(Lab.level).joinedload(Level.track))
        .filter(LabSession.user_id == user.id)
        .all()
    )
    next_labs = next_labs_for_user(db, user)

    branch_items: dict[str, list[dict]] = {spec.key: [] for spec in DIMENSIONS}
    branch_completed_ids: dict[str, set[int]] = {spec.key: set() for spec in DIMENSIONS}
    branch_session_labs: dict[str, dict[int, Lab]] = {spec.key: {} for spec in DIMENSIONS}
    branch_session_starts: dict[str, dict[int, int]] = {spec.key: {} for spec in DIMENSIONS}

    for row in completions:
        lab: Optional[Lab] = getattr(row, "lab", None)
        branch = skill_branch_for_lab(lab)
        ratio = _time_ratio(row, lab)
        branch_items[branch].append(
            {
                "row": row,
                "lab": lab,
                "clean": _clean(row),
                "time_ratio": ratio,
            }
        )
        if lab is not None:
            branch_completed_ids[branch].add(lab.id)

    for session in sessions:
        lab: Optional[Lab] = getattr(session, "lab", None)
        if lab is None:
            continue
        branch = skill_branch_for_lab(lab)
        branch_session_labs[branch][lab.id] = lab
        branch_session_starts[branch][lab.id] = (
            branch_session_starts[branch].get(lab.id, 0) + 1
        )

    branches: list[dict] = []
    unfinished_by_branch: dict[str, list[dict]] = {}
    for spec in DIMENSIONS:
        branch = spec.key
        items = branch_items[branch]
        completed_ids = branch_completed_ids[branch]
        session_labs = branch_session_labs[branch]
        started_ids = set(session_labs) | completed_ids
        unfinished_ids = set(session_labs) - completed_ids
        unfinished_labs = [
            {
                "lab": session_labs[lab_id],
                "starts": branch_session_starts[branch].get(lab_id, 1),
            }
            for lab_id in sorted(unfinished_ids)
        ]
        unfinished_by_branch[branch] = unfinished_labs

        completed = len(items)
        started = len(started_ids)
        unfinished = len(unfinished_ids)
        hint_labs = sum(1 for item in items if (item["row"].hints_used or 0) > 0)
        first_attempt_labs = sum(
            1 for item in items if (item["row"].attempts or 1) <= 1
        )
        clean_labs = sum(1 for item in items if item["clean"])
        hint_rate = _percent(hint_labs, completed)
        first_attempt_rate = _percent(first_attempt_labs, completed)
        unfinished_rate = _percent(unfinished, started)
        time_ratio = _median(
            item["time_ratio"] for item in items if item["time_ratio"] is not None
        )
        friction = _friction_score(
            hint_rate=hint_rate,
            first_attempt_rate=first_attempt_rate,
            unfinished_rate=unfinished_rate,
            time_ratio=time_ratio,
        )
        movement = _movement(items)

        if completed == 0 and started == 0:
            status = "no_evidence"
        elif movement["delta"] is not None and movement["delta"] >= 8 and friction < 55:
            status = "gaining"
        elif friction >= 55 or (movement["delta"] is not None and movement["delta"] <= -8):
            status = "friction"
        else:
            status = "steady"

        branches.append(
            {
                "key": branch,
                "label": spec.label,
                "class_name": spec.class_name,
                "status": status,
                "status_label": STATUS_LABELS[status],
                "score": None,  # filled from the DNA dimensions by the caller
                "completed": completed,
                "started": started,
                "unfinished": unfinished,
                "clean_labs": clean_labs,
                "clean_rate": _percent(clean_labs, completed),
                "hint_rate": hint_rate,
                "first_attempt_rate": first_attempt_rate,
                "unfinished_rate": unfinished_rate,
                "median_time_ratio": time_ratio,
                "friction_score": friction,
                "movement": movement,
                "next_action": _next_action(
                    label=spec.label,
                    completed=completed,
                    started=started,
                    unfinished=unfinished,
                    hint_rate=hint_rate,
                    first_attempt_rate=first_attempt_rate,
                    time_ratio=time_ratio,
                    status=status,
                ),
                "next_lab": next_labs.get(branch),
            }
        )

    stuck_points = _stuck_points(
        branch_items=branch_items,
        unfinished_by_branch=unfinished_by_branch,
    )
    gaining = [
        {
            "branch": row["label"],
            "delta": row["movement"]["delta"],
            "evidence": (
                f"Clean-solve rate moved from "
                f"{row['movement']['earlier_clean_rate']:g}% to "
                f"{row['movement']['recent_clean_rate']:g}%."
            ),
        }
        for row in branches
        if row["status"] == "gaining"
    ]
    friction_rows = [
        {
            "branch": row["label"],
            "friction_score": row["friction_score"],
            "evidence": (
                f"{row['hint_rate']:g}% hint use, "
                f"{row['first_attempt_rate']:g}% first-attempt, "
                f"{row['unfinished']} unfinished."
            ),
        }
        for row in branches
        if row["status"] == "friction"
    ]

    total_completed = len(completions)
    total_started = len(
        {lab_id for labs in branch_session_labs.values() for lab_id in labs}
        | {lab_id for ids in branch_completed_ids.values() for lab_id in ids}
    )
    total_clean = sum(1 for row in completions if _clean(row))
    active_branches = sum(1 for row in branches if row["completed"] > 0)

    if friction_rows:
        next_move = next(
            row["next_action"] for row in branches if row["status"] == "friction"
        )
    elif gaining:
        next_move = next(
            row["next_action"] for row in branches if row["status"] == "gaining"
        )
    elif total_started:
        next_move = "Finish one open exercise before opening a new branch."
    else:
        next_move = (
            "Complete one beginner exercise to give Momentum its first evidence."
        )

    return {
        "version": MOMENTUM_VERSION,
        "window": (
            "Recent half of completed exercises compared with the earlier half. "
            "Friction uses hints, reattempts, time over estimate, and unfinished "
            "exercises."
        ),
        "summary": {
            "completed": total_completed,
            "started": total_started,
            "clean_solves": total_clean,
            "clean_rate": _percent(total_clean, total_completed),
            "active_branches": active_branches,
            "gaining_branches": len(gaining),
            "friction_branches": len(friction_rows),
        },
        "branches": branches,
        "gaining": gaining,
        "friction": friction_rows,
        "stuck_points": stuck_points,
        "next_move": next_move,
        "disclaimer": (
            "Momentum and friction are descriptive signals from your own records. "
            "They are not grades, a ranking, or a prediction. A missing signal is "
            "shown as no evidence yet, not as a zero."
        ),
    }
