"""Skill DNA: a transparent, activity-based learner character sheet.

The five traits are deliberately descriptive, not predictive. They summarise
what a learner has practised in the range and give a next step. They are not a
rank, a grade, or a claim about employability.

Formula version 2026.11:

- Explorer   breadth of tracks, categories, and labs opened.
- Builder    hands-on completion, time, and clean solves.
- Defender   defensive, forensics, network-analysis, and OT practice.
- Investigator analysis, reconnaissance, OSINT, and forensics practice.
- Leader     competitions, courses, badges, advanced labs, and teaching.

Every raw score is capped at 100. The formulas live here, not in the database,
so a future review can change them without a migration.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Achievement,
    CompetitionParticipant,
    Course,
    CourseEnrollment,
    ExerciseQuizAttempt,
    ExerciseReaction,
    Lab,
    LabCompletion,
    LabSession,
    Level,
    Track,
    User,
)
from app.services.titles import resolve_titles

FORMULA_VERSION = "2026.11"

DIMENSION_ORDER = ("explorer", "builder", "defender", "investigator", "leader")

BUILDER_CATEGORIES = {
    "web",
    "network",
    "authentication",
    "general",
    "ai",
    "exploitation",
    "privilege-escalation",
    "post-exploitation",
}
DEFENDER_CATEGORIES = {"forensics", "network-analysis", "ot"}
DEFENDER_TRACKS = {"forensics", "malware", "ot", "network"}
INVESTIGATOR_CATEGORIES = {"osint", "reconnaissance", "network-analysis", "forensics"}
INVESTIGATOR_TRACKS = {"osint", "forensics", "malware", "network"}

# Offensive practice is counted separately from the five trait scores. A
# learner can be a strong Builder without ever touching exploitation content;
# the affinity model only reports offensive evidence when the learner has
# actually completed offensive labs.
OFFENSIVE_CORE_CATEGORIES = {
    "web",
    "exploitation",
    "privilege-escalation",
    "post-exploitation",
    "credential-attacks",
}
OFFENSIVE_SUPPORT_CATEGORIES = {
    "network",
    "authentication",
    "enumeration",
    "reconnaissance",
}
OFFENSIVE_CATEGORIES = OFFENSIVE_CORE_CATEGORIES | OFFENSIVE_SUPPORT_CATEGORIES


@dataclass(frozen=True)
class DimensionSpec:
    key: str
    label: str
    class_name: str
    certification_key: str
    certification_focus: str
    next_step: str


@dataclass(frozen=True)
class AffinitySpec:
    key: str
    label: str
    summary: str
    roles: tuple[str, ...]
    next_step: str


DIMENSIONS: tuple[DimensionSpec, ...] = (
    DimensionSpec(
        "explorer",
        "Explorer",
        "Pathfinder",
        "osint",
        "OSINT, threat intelligence, and reconnaissance",
        "Open a track you have not tried yet.",
    ),
    DimensionSpec(
        "builder",
        "Builder",
        "Artificer",
        "web",
        "AppSec, secure development, and web testing",
        "Complete a multi-step lab without hints.",
    ),
    DimensionSpec(
        "defender",
        "Defender",
        "Warden",
        "network",
        "SOC, network defence, and incident response",
        "Try a forensics or network-analysis lab.",
    ),
    DimensionSpec(
        "investigator",
        "Investigator",
        "Seeker",
        "forensics",
        "DFIR, malware analysis, and forensics",
        "Try an OSINT or traffic-analysis lab.",
    ),
    DimensionSpec(
        "leader",
        "Leader",
        "Commander",
        "general",
        "Security leadership, governance, and programme delivery",
        "Join an event or take part in a course cohort.",
    ),
)

DIMENSION_BY_KEY = {spec.key: spec for spec in DIMENSIONS}

# Practice affinities are positive, evidence-based role families. They update
# from the same activity records as the five traits but are deliberately not
# another rank: they answer "what kind of work have I practised most?" and
# "what should I try next?".
AFFINITIES: tuple[AffinitySpec, ...] = (
    AffinitySpec(
        "offensive",
        "Offensive Security / Penetration Testing",
        "Exploitation, web testing, credential work, and post-exploitation practice.",
        ("Penetration tester", "Red team operator", "Security consultant"),
        "Pair the technical work with a scoping, rules-of-engagement, and reporting exercise.",
    ),
    AffinitySpec(
        "defensive",
        "Defensive Security / SOC",
        "Detection, network analysis, forensics, and OT defence practice.",
        ("SOC analyst", "Detection engineer", "Network security analyst"),
        "Add a detection-engineering or incident-response lab to turn alerts into a repeatable process.",
    ),
    AffinitySpec(
        "investigative",
        "DFIR / Investigation",
        "OSINT, forensics, malware, and evidence-handling practice.",
        ("DFIR analyst", "Forensic examiner", "Threat intelligence analyst"),
        "Practise a timeline or evidence-handling exercise and write a short finding for a non-specialist.",
    ),
    AffinitySpec(
        "leadership",
        "Security Leadership / Education",
        "Events, courses, advanced work, and teaching practice.",
        ("Security lead", "Security educator", "Programme coordinator"),
        "Add a communication, risk-register, or mentoring exercise to the technical work.",
    ),
)

AFFINITY_BY_KEY = {spec.key: spec for spec in AFFINITIES}
AFFINITY_LEVELS = ("no_evidence", "early", "growing", "strong")
AFFINITY_LEVEL_RANK = {level: index for index, level in enumerate(AFFINITY_LEVELS)}


def _track_slug(track: Track | None) -> str:
    if track is None:
        return ""
    return (track.slug or track.name or "").strip().lower()


def tier_for(score: int) -> str:
    if score >= 90:
        return "Master"
    if score >= 75:
        return "Specialist"
    if score >= 50:
        return "Practitioner"
    if score >= 25:
        return "Apprentice"
    if score > 0:
        return "Initiate"
    return "Unranked"


def _clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def _completion_rows(db: Session, user_id: int) -> list[LabCompletion]:
    return (
        db.query(LabCompletion)
        .options(
            joinedload(LabCompletion.lab)
            .joinedload(Lab.level)
            .joinedload(Level.track)
        )
        .filter(LabCompletion.user_id == user_id)
        .all()
    )


def _signals(db: Session, user_id: int) -> dict:
    completions = _completion_rows(db, user_id)
    tracks: set[str] = set()
    categories: set[str] = set()
    defender_labs = 0
    investigator_labs = 0
    builder_labs = 0
    offensive_labs = 0
    offensive_core_labs = 0
    offensive_no_hint_labs = 0
    defender_tracks: set[str] = set()
    investigator_tracks: set[str] = set()
    offensive_categories: set[str] = set()
    total_minutes = 0
    no_hint = 0
    perfect = 0
    advanced = 0

    for row in completions:
        lab: Lab | None = getattr(row, "lab", None)
        level = getattr(lab, "level", None) if lab else None
        track = getattr(level, "track", None) if level else None
        track_slug = _track_slug(track)
        category = (getattr(lab, "category", None) or "general").strip().lower()

        if track_slug or track is not None:
            tracks.add(track_slug or (track.name or "").strip().lower())
        categories.add(category)

        if category in DEFENDER_CATEGORIES or track_slug in DEFENDER_TRACKS:
            defender_labs += 1
            if track_slug:
                defender_tracks.add(track_slug)
        if category in INVESTIGATOR_CATEGORIES or track_slug in INVESTIGATOR_TRACKS:
            investigator_labs += 1
            if track_slug:
                investigator_tracks.add(track_slug)
        if category in BUILDER_CATEGORIES:
            builder_labs += 1

        if category in OFFENSIVE_CATEGORIES:
            offensive_labs += 1
            offensive_categories.add(category)
            if category in OFFENSIVE_CORE_CATEGORIES:
                offensive_core_labs += 1
            if (row.hints_used or 0) == 0:
                offensive_no_hint_labs += 1

        total_minutes += row.time_spent_minutes or 0
        if (row.hints_used or 0) == 0:
            no_hint += 1
        if (row.attempts or 1) <= 1:
            perfect += 1
        if (getattr(lab, "difficulty", None) or "").strip().lower() in {"advanced", "expert"}:
            advanced += 1

    # A completed lab may have no surviving session row (for example after a
    # cleanup or a historical import), so count the union of opened sessions and
    # completed labs as "explored".
    session_lab_ids = {
        row[0]
        for row in db.query(LabSession.lab_id)
        .filter(LabSession.user_id == user_id)
        .distinct()
        .all()
    }
    completed_lab_ids = {row.lab_id for row in completions}
    started_labs = len(session_lab_ids | completed_lab_ids)
    achievements = (
        db.query(func.count(Achievement.id))
        .filter(Achievement.user_id == user_id)
        .scalar()
        or 0
    )
    competitions = (
        db.query(func.count(CompetitionParticipant.id))
        .filter(CompetitionParticipant.user_id == user_id)
        .scalar()
        or 0
    )
    courses = (
        db.query(func.count(CourseEnrollment.id))
        .filter(CourseEnrollment.user_id == user_id)
        .scalar()
        or 0
    )
    instructed = (
        db.query(func.count(Course.id))
        .filter(Course.instructor_id == user_id)
        .scalar()
        or 0
    )
    likes_given = (
        db.query(func.count(ExerciseReaction.id))
        .filter(
            ExerciseReaction.user_id == user_id,
            ExerciseReaction.reaction == "like",
        )
        .scalar()
        or 0
    )

    quiz_rows = (
        db.query(ExerciseQuizAttempt)
        .filter(
            ExerciseQuizAttempt.user_id == user_id,
            ExerciseQuizAttempt.completed_at.isnot(None),
        )
        .all()
    )
    quiz_best: dict[int, int] = {}
    for row in quiz_rows:
        quiz_best[row.lab_id] = max(quiz_best.get(row.lab_id, 0), row.score or 0)
    quiz_labs = len(quiz_best)
    quiz_accuracy = round(sum(quiz_best.values()) / quiz_labs) if quiz_labs else None

    return {
        "completed_labs": len(completions),
        "started_labs": int(started_labs),
        "tracks": sorted(tracks),
        "categories": sorted(categories),
        "defender_labs": defender_labs,
        "defender_tracks": sorted(defender_tracks),
        "investigator_labs": investigator_labs,
        "investigator_tracks": sorted(investigator_tracks),
        "builder_labs": builder_labs,
        "offensive_labs": offensive_labs,
        "offensive_core_labs": offensive_core_labs,
        "offensive_no_hint_labs": offensive_no_hint_labs,
        "offensive_categories": sorted(offensive_categories),
        "total_minutes": total_minutes,
        "no_hint_labs": no_hint,
        "perfect_labs": perfect,
        "advanced_labs": advanced,
        "achievements": int(achievements),
        "competitions": int(competitions),
        "courses": int(courses),
        "instructed_courses": int(instructed),
        "likes_given": int(likes_given),
        "quiz_attempts": len(quiz_rows),
        "quiz_labs": quiz_labs,
        "quiz_accuracy": quiz_accuracy,
    }


def _scores(signals: dict) -> dict[str, int]:
    explorer = _clamp(
        7 * len(signals["tracks"])
        + 2 * len(signals["categories"])
        + 1.2 * min(signals["started_labs"], 20)
        + 2 * min(len(signals["tracks"]), 3)
        + 1.0 * min(signals["quiz_labs"], 10)
    )
    builder = _clamp(
        2.0 * min(signals["completed_labs"], 25)
        + 0.04 * min(signals["total_minutes"], 1200)
        + 1.0 * min(signals["no_hint_labs"], 10)
        + 0.5 * min(signals["perfect_labs"], 10)
        + 1.0 * min(signals["builder_labs"], 10)
        + 1.5 * min(signals["quiz_labs"], 10)
        + 0.15 * (signals["quiz_accuracy"] or 0)
    )
    defender = _clamp(
        9 * min(signals["defender_labs"], 12)
        + 3 * min(len(signals["defender_tracks"]), 4)
        + 2 * min(len(signals["categories"]), 5)
    )
    investigator = _clamp(
        9 * min(signals["investigator_labs"], 12)
        + 3 * min(len(signals["investigator_tracks"]), 4)
        + 2 * min(len(signals["categories"]), 5)
    )
    leader = _clamp(
        12 * min(signals["competitions"], 5)
        + 6 * min(signals["courses"], 5)
        + 2 * min(signals["achievements"], 20)
        + 4 * min(signals["advanced_labs"], 10)
        + 8 * min(signals["instructed_courses"], 3)
        + 1 * min(signals["likes_given"], 10)
    )
    return {
        "explorer": explorer,
        "builder": builder,
        "defender": defender,
        "investigator": investigator,
        "leader": leader,
    }


def _evidence(spec: DimensionSpec, signals: dict, score: int) -> str:
    if score == 0:
        return "No signal yet."
    if spec.key == "explorer":
        return (
            f"{len(signals['tracks'])} tracks · "
            f"{len(signals['categories'])} categories · "
            f"{signals['started_labs']} labs explored"
        )
    if spec.key == "builder":
        parts = [
            f"{signals['completed_labs']} labs completed",
            f"{signals['total_minutes']} min hands-on",
            f"{signals['no_hint_labs']} no-hint",
        ]
        if signals["quiz_labs"]:
            parts.append(
                f"{signals['quiz_labs']} knowledge checks"
                + (f" ({signals['quiz_accuracy']}% avg)" if signals["quiz_accuracy"] is not None else "")
            )
        return " · ".join(parts)
    if spec.key == "defender":
        return (
            f"{signals['defender_labs']} defensive labs · "
            f"{len(signals['defender_tracks'])} tracks"
        )
    if spec.key == "investigator":
        return (
            f"{signals['investigator_labs']} analysis labs · "
            f"{len(signals['investigator_tracks'])} tracks"
        )
    return (
        f"{signals['competitions']} events · "
        f"{signals['courses']} courses · "
        f"{signals['achievements']} badges"
    )


def _affinity_level(count: int) -> str:
    if count <= 0:
        return "no_evidence"
    if count < 3:
        return "early"
    if count < 6:
        return "growing"
    return "strong"


def _affinity_counts(signals: dict) -> dict[str, int]:
    return {
        "offensive": signals["offensive_core_labs"],
        "defensive": signals["defender_labs"],
        "investigative": signals["investigator_labs"],
        "leadership": (
            signals["competitions"]
            + signals["courses"]
            + signals["instructed_courses"]
            + signals["advanced_labs"]
        ),
    }


def _affinity_evidence(spec: AffinitySpec, signals: dict) -> str:
    if spec.key == "offensive":
        parts = [
            f"{signals['offensive_core_labs']} core offensive labs",
            f"{signals['offensive_labs']} offensive labs total",
        ]
        if signals["offensive_no_hint_labs"]:
            parts.append(f"{signals['offensive_no_hint_labs']} clean solves")
        if signals["offensive_categories"]:
            parts.append(
                f"{len(signals['offensive_categories'])} offensive categories"
            )
        return " · ".join(parts)
    if spec.key == "defensive":
        return (
            f"{signals['defender_labs']} defensive labs · "
            f"{len(signals['defender_tracks'])} tracks"
        )
    if spec.key == "investigative":
        return (
            f"{signals['investigator_labs']} analysis labs · "
            f"{len(signals['investigator_tracks'])} tracks"
        )
    return (
        f"{signals['competitions']} events · "
        f"{signals['courses']} courses · "
        f"{signals['instructed_courses']} courses taught · "
        f"{signals['advanced_labs']} advanced labs"
    )


def _affinities(signals: dict) -> list[dict]:
    counts = _affinity_counts(signals)
    rows = []
    for spec in AFFINITIES:
        count = counts[spec.key]
        level = _affinity_level(count)
        rows.append({
            "key": spec.key,
            "label": spec.label,
            "summary": spec.summary,
            "roles": list(spec.roles),
            "evidence_level": level,
            "evidence": _affinity_evidence(spec, signals),
            "next_step": spec.next_step,
            "recommended": False,
            "_count": count,
            "evidence_count": count,
        })

    rows.sort(
        key=lambda row: (
            -AFFINITY_LEVEL_RANK[row["evidence_level"]],
            -row["_count"],
            row["key"],
        )
    )
    if rows and rows[0]["_count"] > 0:
        rows[0]["recommended"] = True
    for row in rows:
        row.pop("_count", None)
    return rows


def build_skill_dna(db: Session, user: User) -> dict:
    signals = _signals(db, user.id)
    scores = _scores(signals)

    dimensions = []
    for spec in DIMENSIONS:
        score = scores[spec.key]
        dimensions.append(
            {
                "key": spec.key,
                "label": spec.label,
                "class_name": spec.class_name,
                "tier": tier_for(score),
                "score": score,
                "certification_key": spec.certification_key,
                "certification_focus": spec.certification_focus,
                "evidence": _evidence(spec, signals, score),
                "next_step": spec.next_step,
            }
        )

    top = sorted(
        dimensions,
        key=lambda row: (-row["score"], DIMENSION_ORDER.index(row["key"])),
    )[0]
    if top["score"] == 0:
        top_class = {
            "key": "recruit",
            "label": "Recruit",
            "class_name": "Recruit",
            "certification_key": "general",
            "certification_focus": "General cybersecurity foundations",
        }
    else:
        top_class = {
            "key": top["key"],
            "label": top["label"],
            "class_name": top["class_name"],
            "certification_key": top["certification_key"],
            "certification_focus": top["certification_focus"],
        }

    titles = resolve_titles(
        db,
        user,
        class_title=top_class["class_name"],
        class_key=top_class["key"],
    )
    overall = round(sum(row["score"] for row in dimensions) / len(dimensions))

    return {
        "formula_version": FORMULA_VERSION,
        "overall": overall,
        "tier": tier_for(overall),
        "class": top_class,
        "dimensions": dimensions,
        "affinities": _affinities(signals),
        "titles": titles,
        "quiz": {
            "attempts": signals["quiz_attempts"],
            "labs": signals["quiz_labs"],
            "accuracy": signals["quiz_accuracy"],
        },
        "signals": signals,
    }


# ---------------------------------------------------------------------------
# Skill-tree coverage
# ---------------------------------------------------------------------------

SKILL_BRANCH_ORDER = DIMENSION_ORDER
SKILL_BRANCH_LABELS = {spec.key: spec.label for spec in DIMENSIONS}


def skill_branch_for_lab(lab: Lab | None) -> str:
    """Assign one curriculum exercise to one Skill DNA branch.

    The report needs a single branch per exercise so the radar is a true mix
    that sums to 100%. The rules follow the Skill DNA categories, with the
    following tie-breaks:

    * advanced/expert exercises count as Leader (capstone/advanced work);
    * OSINT, forensics, and malware analysis count as Investigator;
    * network analysis and OT count as Defender;
    * builder categories count as Builder;
    * reconnaissance, enumeration, assessment, and the remaining foundations
      count as Explorer.
    """
    if lab is None:
        return "explorer"
    category = (getattr(lab, "category", None) or "general").strip().lower()
    difficulty = (getattr(lab, "difficulty", None) or "").strip().lower()
    level = getattr(lab, "level", None)
    track = getattr(level, "track", None) if level else None
    track_slug = _track_slug(track)

    if difficulty in {"advanced", "expert"}:
        return "leader"
    if category in {"osint", "forensics"} or track_slug in {
        "osint",
        "forensics",
        "malware",
    }:
        return "investigator"
    if category in {"network-analysis", "ot"} or track_slug in {"network", "ot"}:
        return "defender"
    if category in BUILDER_CATEGORIES:
        return "builder"
    return "explorer"


def _skill_pct(count: int, total: int) -> float:
    return round(count / total * 100, 1) if total else 0.0


def skill_branch_mix(labs: list[Lab], completions: list[LabCompletion]) -> dict:
    """Summarise assigned and completed exercises by Skill DNA branch.

    ``completions`` may contain several learners for the same exercise. The
    completed side counts distinct exercises, matching the assigned side.
    """
    assigned_counts = Counter(skill_branch_for_lab(lab) for lab in labs if lab)
    completed_labs: dict[int, Lab] = {}
    for row in completions:
        lab = getattr(row, "lab", None)
        if lab is not None:
            completed_labs[lab.id] = lab
    completed_counts = Counter(
        skill_branch_for_lab(lab) for lab in completed_labs.values()
    )
    assigned_total = sum(assigned_counts.values())
    completed_total = sum(completed_counts.values())

    return {
        "dimensions": [
            {
                "key": key,
                "label": SKILL_BRANCH_LABELS[key],
                "assigned": assigned_counts.get(key, 0),
                "completed": completed_counts.get(key, 0),
                "assigned_pct": _skill_pct(assigned_counts.get(key, 0), assigned_total),
                "completed_pct": _skill_pct(completed_counts.get(key, 0), completed_total),
            }
            for key in SKILL_BRANCH_ORDER
        ],
        "assigned_total": assigned_total,
        "completed_total": completed_total,
        "completion_pct": _skill_pct(completed_total, assigned_total),
    }
