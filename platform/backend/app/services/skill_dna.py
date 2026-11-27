"""Skill DNA: a transparent, activity-based learner character sheet.

The six traits are deliberately descriptive, not predictive. They summarise
what a learner has practised in the range and give a next step. They are not a
rank, a grade, or a claim about employability.

Formula version 2026.12:

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
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Achievement,
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

FORMULA_VERSION = "2026.14"

# Published factor weights. They live in the payload and in every persisted
# report snapshot so a later formula change cannot silently rewrite an old
# report. The scoring functions below read these values; keep the two in step.
FACTOR_WEIGHTS = {
    "cap": 99,
    "recency": [
        {"max_days": 14, "factor": 1.0},
        {"max_days": 30, "factor": 0.99},
        {"max_days": 60, "factor": 0.97},
        {"max_days": 90, "factor": 0.94},
        {"max_days": None, "factor": 0.90},
    ],
    "evidence_strength": {
        "base": 1.0,
        "clean_solve": 0.5,
        "first_attempt": 0.25,
        "advanced": 0.75,
        "assessment": 0.5,
        "quiz_base": 0.75,
        "quiz_scale": 0.75,
        "explorer_open_lab": 0.5,
        "explorer_track": 0.25,
        "explorer_category": 0.25,
        "leader_course": 1.5,
        "leader_achievement": 0.5,
        "leader_instructed": 3.0,
        "leader_like": 0.25,
    },
    "dimensions": {
        "explorer": {
            "track": 7,
            "category": 2,
            "started_lab": 1.2,
            "track_bonus": 2,
            "quiz_lab": 1.0,
        },
        "builder": {
            "completed_lab": 2.0,
            "minute": 0.04,
            "no_hint_lab": 1.0,
            "perfect_lab": 0.5,
            "builder_lab": 1.0,
            "quiz_lab": 1.5,
            "quiz_accuracy_point": 0.15,
        },
        "tester": {
            "offensive_core_lab": 9,
            "offensive_lab": 2,
            "offensive_category": 3,
            "offensive_no_hint_lab": 1,
            "assessment_lab": 3,
        },
        "defender": {
            "defender_lab": 9,
            "defender_track": 3,
            "category": 2,
        },
        "investigator": {
            "investigator_lab": 9,
            "investigator_track": 3,
            "category": 2,
        },
        "leader": {
            "course": 6,
            "achievement": 2,
            "advanced_lab": 4,
            "instructed_course": 8,
            "like": 1,
        },
    },
}

DIMENSION_ORDER = ("explorer", "builder", "tester", "defender", "investigator", "leader")

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
    "assessment",
}
OFFENSIVE_CATEGORIES = OFFENSIVE_CORE_CATEGORIES | OFFENSIVE_SUPPORT_CATEGORIES
TESTER_CATEGORIES = OFFENSIVE_CORE_CATEGORIES | {"assessment"}


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
        "tester",
        "Tester",
        "Assessor",
        "web",
        "Authorised offensive testing, exploitation, and reporting",
        "Complete an assessment or capstone lab and write a short finding.",
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
# from the same activity records as the six traits but are deliberately not
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
        "Events, teaching, and programme practice.",
        ("Security lead", "Security educator", "Programme coordinator"),
        "Add a communication, risk-register, or mentoring exercise to the technical work.",
    ),
)

AFFINITY_BY_KEY = {spec.key: spec for spec in AFFINITIES}
AFFINITY_LEVELS = ("no_evidence", "early", "growing", "strong")
AFFINITY_LEVEL_RANK = {level: index for index, level in enumerate(AFFINITY_LEVELS)}
# Affinities look at the last year first so a learner who changes direction is
# not pinned to early practice. Older work still counts at half weight.
AFFINITY_RECENT_DAYS = 365
AFFINITY_OLDER_WEIGHT = 0.5


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
    # Cyber DNA never reaches 100: there is always another branch to develop.
    return max(0, min(FACTOR_WEIGHTS["cap"], round(value)))


def _completion_rows(
    db: Session, user_id: int, before: datetime | None = None
) -> list[LabCompletion]:
    query = (
        db.query(LabCompletion)
        .options(
            joinedload(LabCompletion.lab)
            .joinedload(Lab.level)
            .joinedload(Level.track)
        )
        .filter(
            LabCompletion.user_id == user_id,
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        )
    )
    if before is not None:
        query = query.filter(LabCompletion.completed_at < before)
    return query.all()


def _signals(db: Session, user_id: int, before: datetime | None = None) -> dict:
    now = before or datetime.now(timezone.utc).replace(tzinfo=None)
    completions = _completion_rows(db, user_id, before=before)
    tracks: set[str] = set()
    categories: set[str] = set()
    defender_labs = 0
    investigator_labs = 0
    builder_labs = 0
    offensive_labs = 0
    offensive_core_labs = 0
    offensive_no_hint_labs = 0
    assessment_labs = 0
    defender_tracks: set[str] = set()
    investigator_tracks: set[str] = set()
    offensive_categories: set[str] = set()
    total_minutes = 0
    no_hint = 0
    perfect = 0
    advanced = 0
    # Which branches each completed lab feeds. Quiz attempts are attributed to
    # the same branches so the chart can size a point by the work behind it.
    lab_branches: dict[int, set[str]] = {}
    branch_last_at: dict[str, datetime] = {}
    evidence_weight: Counter[str] = Counter()
    affinity_totals: Counter[str] = Counter()
    affinity_recent: Counter[str] = Counter()
    recent_cutoff = now - timedelta(days=AFFINITY_RECENT_DAYS)

    for row in completions:
        lab: Lab | None = getattr(row, "lab", None)
        level = getattr(lab, "level", None) if lab else None
        track = getattr(level, "track", None) if level else None
        track_slug = _track_slug(track)
        category = (getattr(lab, "category", None) or "general").strip().lower()
        branches = {"explorer", "builder"}
        completed_at = getattr(row, "completed_at", None)
        is_recent = bool(completed_at and completed_at >= recent_cutoff)

        if track_slug or track is not None:
            tracks.add(track_slug or (track.name or "").strip().lower())
        categories.add(category)

        if category in DEFENDER_CATEGORIES or track_slug in DEFENDER_TRACKS:
            defender_labs += 1
            branches.add("defender")
            affinity_totals["defensive"] += 1
            if is_recent:
                affinity_recent["defensive"] += 1
            if track_slug:
                defender_tracks.add(track_slug)
        if category in INVESTIGATOR_CATEGORIES or track_slug in INVESTIGATOR_TRACKS:
            investigator_labs += 1
            branches.add("investigator")
            affinity_totals["investigative"] += 1
            if is_recent:
                affinity_recent["investigative"] += 1
            if track_slug:
                investigator_tracks.add(track_slug)
        if category in BUILDER_CATEGORIES:
            builder_labs += 1

        if category in OFFENSIVE_CATEGORIES:
            offensive_labs += 1
            branches.add("tester")
            offensive_categories.add(category)
            if category in OFFENSIVE_CORE_CATEGORIES:
                offensive_core_labs += 1
                affinity_totals["offensive"] += 1
                if is_recent:
                    affinity_recent["offensive"] += 1
            if (row.hints_used or 0) == 0:
                offensive_no_hint_labs += 1
        if category == "assessment":
            assessment_labs += 1
            branches.add("tester")
            affinity_totals["offensive"] += 1
            if is_recent:
                affinity_recent["offensive"] += 1

        total_minutes += row.time_spent_minutes or 0
        if (row.hints_used or 0) == 0:
            no_hint += 1
        if (row.attempts or 1) <= 1:
            perfect += 1
        is_advanced = (
            (getattr(lab, "difficulty", None) or "").strip().lower()
            in {"advanced", "expert"}
        )
        if is_advanced:
            advanced += 1
            branches.add("leader")
        if lab is not None:
            lab_branches[lab.id] = branches

        # Stronger work leaves a heavier mark. A clean, unaided solve of an
        # advanced or assessment lab counts for more than a hinted walkthrough.
        strength_weights = FACTOR_WEIGHTS["evidence_strength"]
        strength = strength_weights["base"]
        if (row.hints_used or 0) == 0:
            strength += strength_weights["clean_solve"]
        if (row.attempts or 1) <= 1:
            strength += strength_weights["first_attempt"]
        if is_advanced:
            strength += strength_weights["advanced"]
        if category == "assessment":
            strength += strength_weights["assessment"]
        for branch in branches:
            evidence_weight[branch] += strength
            completed_at = getattr(row, "completed_at", None)
            if completed_at and (
                branch not in branch_last_at or completed_at > branch_last_at[branch]
            ):
                branch_last_at[branch] = completed_at

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
    # Event participation is context, not a trait score. Event success is
    # captured by the comp_* achievement badges (first blood, clean sweep,
    # perfect event, placement), and the event exercises count as normal labs.
    event_achievements = (
        db.query(func.count(Achievement.id))
        .filter(
            Achievement.user_id == user_id,
            Achievement.achievement_type.like("comp_%"),
        )
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
    event_recent = (
        db.query(func.count(Achievement.id))
        .filter(
            Achievement.user_id == user_id,
            Achievement.achievement_type.like("comp_%"),
            Achievement.awarded_at >= recent_cutoff,
        )
        .scalar()
        or 0
    )
    instructed_recent = (
        db.query(func.count(Course.id))
        .filter(
            Course.instructor_id == user_id,
            Course.created_at >= recent_cutoff,
        )
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
    # Leadership evidence is timestamped too, so an inactive leader branch
    # decays even when the learner is not completing labs.
    for stamp in (
        db.query(func.max(Achievement.awarded_at))
        .filter(Achievement.user_id == user_id)
        .scalar(),
        db.query(func.max(CourseEnrollment.enrolled_at))
        .filter(CourseEnrollment.user_id == user_id)
        .scalar(),
        db.query(func.max(Course.created_at))
        .filter(Course.instructor_id == user_id)
        .scalar(),
    ):
        if stamp and (
            "leader" not in branch_last_at or stamp > branch_last_at["leader"]
        ):
            branch_last_at["leader"] = stamp

    quiz_query = db.query(ExerciseQuizAttempt).filter(
        ExerciseQuizAttempt.user_id == user_id,
        ExerciseQuizAttempt.completed_at.isnot(None),
    )
    if before is not None:
        quiz_query = quiz_query.filter(ExerciseQuizAttempt.completed_at < before)
    quiz_rows = quiz_query.all()
    quiz_best: dict[int, int] = {}
    quiz_last_at: dict[int, datetime] = {}
    for row in quiz_rows:
        quiz_best[row.lab_id] = max(quiz_best.get(row.lab_id, 0), row.score or 0)
        if row.completed_at and (
            row.lab_id not in quiz_last_at or row.completed_at > quiz_last_at[row.lab_id]
        ):
            quiz_last_at[row.lab_id] = row.completed_at
    quiz_labs = len(quiz_best)
    quiz_accuracy = round(sum(quiz_best.values()) / quiz_labs) if quiz_labs else None
    quiz_area: Counter[str] = Counter()
    for lab_id, best in quiz_best.items():
        # A quiz counts toward volume and adds strength in proportion to the
        # learner's best score on that lab's knowledge check.
        quiz_strength = (
            FACTOR_WEIGHTS["evidence_strength"]["quiz_base"]
            + (best / 100) * FACTOR_WEIGHTS["evidence_strength"]["quiz_scale"]
        )
        for branch in lab_branches.get(lab_id, {"explorer", "builder"}):
            quiz_area[branch] += 1
            evidence_weight[branch] += quiz_strength
            completed_at = quiz_last_at.get(lab_id)
            if completed_at and (
                branch not in branch_last_at or completed_at > branch_last_at[branch]
            ):
                branch_last_at[branch] = completed_at

    # How much work sits behind each branch. The score says how far a branch
    # has grown; this says how much practice supports it. Used to size the
    # spider-chart points so a point backed by many labs and quizzes reads
    # heavier than one backed by a single completion.
    evidence_volume = {
        "explorer": (
            started_labs
            + len(tracks)
            + len(categories)
            + quiz_area["explorer"]
        ),
        "builder": (
            len(completions)
            + builder_labs
            + no_hint
            + quiz_area["builder"]
        ),
        "tester": (
            offensive_labs
            + assessment_labs
            + quiz_area["tester"]
        ),
        "defender": defender_labs + quiz_area["defender"],
        "investigator": investigator_labs + quiz_area["investigator"],
        "leader": (
            int(courses)
            + int(achievements)
            + int(instructed)
            + advanced
            + int(likes_given)
            + quiz_area["leader"]
        ),
    }
    # Breadth and leadership work also strengthen a branch's point.
    strength_weights = FACTOR_WEIGHTS["evidence_strength"]
    evidence_weight["explorer"] += strength_weights["explorer_open_lab"] * len(
        session_lab_ids - completed_lab_ids
    )
    evidence_weight["explorer"] += strength_weights["explorer_track"] * len(tracks)
    evidence_weight["explorer"] += strength_weights["explorer_category"] * len(
        categories
    )
    evidence_weight["leader"] += (
        strength_weights["leader_course"] * int(courses)
        + strength_weights["leader_achievement"] * int(achievements)
        + strength_weights["leader_instructed"] * int(instructed)
        + strength_weights["leader_like"] * int(likes_given)
    )

    # Leadership affinity is teaching and event practice, not course enrolment
    # or advanced technical work. Those already count in other branches; removing
    # the overlap stops an active learner from looking like a leader by accident.
    affinity_totals["leadership"] = int(instructed) * 2 + int(event_achievements)
    affinity_recent["leadership"] = int(instructed_recent) * 2 + int(event_recent)

    last_at = max(
        (row.completed_at for row in completions if row.completed_at),
        default=None,
    )
    days_since_last = (now - last_at).days if last_at else None
    minutes_12m = sum(
        row.time_spent_minutes or 0
        for row in completions
        if row.completed_at and row.completed_at >= now - timedelta(days=365)
    )

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
        "assessment_labs": assessment_labs,
        "total_minutes": total_minutes,
        "no_hint_labs": no_hint,
        "perfect_labs": perfect,
        "advanced_labs": advanced,
        "achievements": int(achievements),
        "event_achievements": int(event_achievements),
        "courses": int(courses),
        "instructed_courses": int(instructed),
        "likes_given": int(likes_given),
        "quiz_attempts": len(quiz_rows),
        "quiz_labs": quiz_labs,
        "quiz_accuracy": quiz_accuracy,
        "last_completion_at": last_at,
        "days_since_last_activity": days_since_last,
        "minutes_12m": minutes_12m,
        "evidence_volume": evidence_volume,
        "evidence_weight": {
            key: round(value, 2) for key, value in evidence_weight.items()
        },
        "affinity_totals": dict(affinity_totals),
        "affinity_recent": dict(affinity_recent),
        "branch_last_activity": branch_last_at,
    }


def _scores(signals: dict) -> dict[str, int]:
    w = FACTOR_WEIGHTS["dimensions"]
    explorer_w = w["explorer"]
    builder_w = w["builder"]
    tester_w = w["tester"]
    defender_w = w["defender"]
    investigator_w = w["investigator"]
    leader_w = w["leader"]
    explorer = _clamp(
        explorer_w["track"] * len(signals["tracks"])
        + explorer_w["category"] * len(signals["categories"])
        + explorer_w["started_lab"] * min(signals["started_labs"], 20)
        + explorer_w["track_bonus"] * min(len(signals["tracks"]), 3)
        + explorer_w["quiz_lab"] * min(signals["quiz_labs"], 10)
    )
    builder = _clamp(
        builder_w["completed_lab"] * min(signals["completed_labs"], 25)
        + builder_w["minute"] * min(signals["total_minutes"], 1200)
        + builder_w["no_hint_lab"] * min(signals["no_hint_labs"], 10)
        + builder_w["perfect_lab"] * min(signals["perfect_labs"], 10)
        + builder_w["builder_lab"] * min(signals["builder_labs"], 10)
        + builder_w["quiz_lab"] * min(signals["quiz_labs"], 10)
        + builder_w["quiz_accuracy_point"] * (signals["quiz_accuracy"] or 0)
    )
    tester = _clamp(
        tester_w["offensive_core_lab"] * min(signals["offensive_core_labs"], 12)
        + tester_w["offensive_lab"] * min(signals["offensive_labs"], 20)
        + tester_w["offensive_category"] * min(len(signals["offensive_categories"]), 4)
        + tester_w["offensive_no_hint_lab"] * min(signals["offensive_no_hint_labs"], 10)
        + tester_w["assessment_lab"] * min(signals["assessment_labs"], 4)
    )
    defender = _clamp(
        defender_w["defender_lab"] * min(signals["defender_labs"], 12)
        + defender_w["defender_track"] * min(len(signals["defender_tracks"]), 4)
        + defender_w["category"] * min(len(signals["categories"]), 5)
    )
    investigator = _clamp(
        investigator_w["investigator_lab"] * min(signals["investigator_labs"], 12)
        + investigator_w["investigator_track"]
        * min(len(signals["investigator_tracks"]), 4)
        + investigator_w["category"] * min(len(signals["categories"]), 5)
    )
    leader = _clamp(
        leader_w["course"] * min(signals["courses"], 5)
        + leader_w["achievement"] * min(signals["achievements"], 20)
        + leader_w["advanced_lab"] * min(signals["advanced_labs"], 10)
        + leader_w["instructed_course"] * min(signals["instructed_courses"], 3)
        + leader_w["like"] * min(signals["likes_given"], 10)
    )
    return {
        "explorer": explorer,
        "builder": builder,
        "tester": tester,
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
    if spec.key == "tester":
        return (
            f"{signals['offensive_core_labs']} offensive labs · "
            f"{len(signals['offensive_categories'])} offensive categories · "
            f"{signals['assessment_labs']} assessments"
        )
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
        f"{signals['event_achievements']} event awards · "
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
    totals = signals.get("affinity_totals")
    if totals:
        return {
            key: int(totals.get(key, 0))
            for key in ("offensive", "defensive", "investigative", "leadership")
        }
    # Fallback for callers that build a partial signal dict in a test or a
    # one-off script. Production signals always carry the explicit counters.
    return {
        "offensive": signals["offensive_core_labs"] + signals["assessment_labs"],
        "defensive": signals["defender_labs"],
        "investigative": signals["investigator_labs"],
        "leadership": (
            signals["event_achievements"] + signals["instructed_courses"]
        ),
    }


def _affinity_recent_counts(signals: dict) -> dict[str, int]:
    recent = signals.get("affinity_recent")
    if recent:
        return {
            key: int(recent.get(key, 0))
            for key in ("offensive", "defensive", "investigative", "leadership")
        }
    return _affinity_counts(signals)


def _affinity_recent_note(total: int, recent: int) -> str:
    if total <= 0:
        return ""
    if recent <= 0:
        return " · no practice in the last year"
    return f" · {recent} in the last year"


def _affinity_evidence(
    spec: AffinitySpec, signals: dict, recent: int = 0
) -> str:
    if spec.key == "offensive":
        total = int(signals.get("affinity_totals", {}).get("offensive", 0)) or (
            signals["offensive_core_labs"] + signals["assessment_labs"]
        )
        parts = [
            f"{signals['offensive_core_labs']} core offensive labs",
            f"{signals['offensive_labs']} offensive labs total",
        ]
        if signals["assessment_labs"]:
            parts.append(f"{signals['assessment_labs']} assessments")
        if signals["offensive_no_hint_labs"]:
            parts.append(f"{signals['offensive_no_hint_labs']} clean solves")
        if signals["offensive_categories"]:
            parts.append(
                f"{len(signals['offensive_categories'])} offensive categories"
            )
        return " · ".join(parts) + _affinity_recent_note(total, recent)
    if spec.key == "defensive":
        total = signals["defender_labs"]
        return (
            f"{total} defensive labs · "
            f"{len(signals['defender_tracks'])} tracks"
            + _affinity_recent_note(total, recent)
        )
    if spec.key == "investigative":
        total = signals["investigator_labs"]
        return (
            f"{total} analysis labs · "
            f"{len(signals['investigator_tracks'])} tracks"
            + _affinity_recent_note(total, recent)
        )
    total = int(signals.get("affinity_totals", {}).get("leadership", 0))
    return (
        f"{signals['instructed_courses']} courses taught · "
        f"{signals['event_achievements']} event awards"
        + _affinity_recent_note(total, recent)
    )


def _affinities(signals: dict) -> list[dict]:
    counts = _affinity_counts(signals)
    recent_counts = _affinity_recent_counts(signals)
    rows = []
    for spec in AFFINITIES:
        count = counts[spec.key]
        recent = min(count, recent_counts.get(spec.key, count))
        older = max(0, count - recent)
        rank_count = recent + older * AFFINITY_OLDER_WEIGHT
        level = _affinity_level(rank_count)
        rows.append({
            "key": spec.key,
            "label": spec.label,
            "summary": spec.summary,
            "roles": list(spec.roles),
            "evidence_level": level,
            "evidence": _affinity_evidence(spec, signals, recent),
            "next_step": spec.next_step,
            "recommended": False,
            "primary": False,
            "evidence_count": count,
            "recent_count": recent,
            "rank_count": round(rank_count, 2),
            "_rank": rank_count,
        })

    rows.sort(
        key=lambda row: (
            -AFFINITY_LEVEL_RANK[row["evidence_level"]],
            -row["_rank"],
            -row["evidence_count"],
            row["key"],
        )
    )
    # A learner can have more than one strong direction. Mark every branch with
    # growing or strong recent evidence, not only the single highest count. If
    # every branch is still early, keep one next step so a beginner is not left
    # without a prompt.
    recommended_keys = {
        row["key"]
        for row in rows
        if row["evidence_count"] > 0
        and row["evidence_level"] in ("growing", "strong")
    }
    if not recommended_keys and rows and rows[0]["evidence_count"] > 0:
        recommended_keys = {rows[0]["key"]}
    for row in rows:
        row["recommended"] = row["key"] in recommended_keys
    for row in rows:
        if row["recommended"]:
            row["primary"] = True
            break
    for row in rows:
        row.pop("_rank", None)
    return rows


def _recency_factor(days: int | None) -> float:
    """Keep practice current: a long break slowly lowers the training signal.

    A new completion resets the factor to 1.0, so the effect is repair by
    practice, not a permanent penalty. The floor is 0.90 (10% at most).
    """
    if days is None:
        return FACTOR_WEIGHTS["recency"][0]["factor"]
    for step in FACTOR_WEIGHTS["recency"]:
        max_days = step["max_days"]
        if max_days is None or days <= max_days:
            return step["factor"]
    return FACTOR_WEIGHTS["recency"][-1]["factor"]


def build_skill_dna(db: Session, user: User) -> dict:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    signals = _signals(db, user.id)
    scores = _scores(signals)
    evidence_volume = signals.get("evidence_volume") or {}
    evidence_weight = signals.get("evidence_weight") or {}
    branch_last = signals.get("branch_last_activity") or {}

    # Directional trend: rebuild the branch scores as they stood 30 days ago
    # from the same timestamps. This needs no snapshot table and stays honest
    # when old data is imported or removed.
    trend_days = 30
    prior_cutoff = now - timedelta(days=trend_days)
    if signals["completed_labs"] or signals["quiz_labs"]:
        prior_signals = _signals(db, user.id, before=prior_cutoff)
        prior_scores = _scores(prior_signals)
        prior_last = prior_signals.get("branch_last_activity") or {}
    else:
        prior_scores = scores
        prior_last = branch_last

    dimensions = []
    for spec in DIMENSIONS:
        last = branch_last.get(spec.key)
        branch_days = (now - last).days if last else None
        branch_factor = _recency_factor(branch_days)
        score = min(99, round(scores[spec.key] * branch_factor))

        prior_branch_last = prior_last.get(spec.key)
        prior_days = (
            (prior_cutoff - prior_branch_last).days if prior_branch_last else None
        )
        prior_score = min(
            99, round(prior_scores[spec.key] * _recency_factor(prior_days))
        )
        delta = score - prior_score
        dimensions.append(
            {
                "key": spec.key,
                "label": spec.label,
                "class_name": spec.class_name,
                "tier": tier_for(score),
                "score": score,
                "evidence_count": int(evidence_volume.get(spec.key, 0)),
                "evidence_weight": round(float(evidence_weight.get(spec.key, 0)), 2),
                "recency": {
                    "days_since_last_activity": branch_days,
                    "factor_percent": round(branch_factor * 100),
                    "decay_percent": round((1 - branch_factor) * 100),
                },
                "trend": {
                    "window_days": trend_days,
                    "previous_score": prior_score,
                    "delta": delta,
                    "direction": "up" if delta > 0 else "down" if delta < 0 else "flat",
                },
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
    overall = min(99, round(sum(row["score"] for row in dimensions) / len(dimensions)))
    hours_12m = round((signals.get("minutes_12m") or 0) / 60, 1)
    ce_percent = min(100, round(hours_12m / 40 * 100)) if hours_12m else 0
    days = signals.get("days_since_last_activity")
    if days is None:
        recency_note = "No completed exercise yet. One completion starts the clock."
    elif all(row["recency"]["decay_percent"] == 0 for row in dimensions):
        recency_note = "Current: every branch has practice within the last two weeks."
    else:
        stale = [
            row["label"]
            for row in dimensions
            if row["recency"]["decay_percent"] > 0 and row["score"] > 0
        ]
        recency_note = (
            "Each branch decays on its own if it is left alone. "
            + (
                f"Practice {', '.join(stale)} to restore the reduced branches."
                if stale
                else "A completion in a branch restores it."
            )
        )

    weakest = min(dimensions, key=lambda row: row["recency"]["factor_percent"])
    return {
        "formula_version": FORMULA_VERSION,
        "factor_weights": FACTOR_WEIGHTS,
        "overall": overall,
        "tier": tier_for(overall),
        "class": top_class,
        "dimensions": dimensions,
        "affinities": _affinities(signals),
        "titles": titles,
        "trend_window_days": trend_days,
        "ceiling_note": "No branch reaches 100: there is always a next skill to develop.",
        "recency": {
            "days_since_last_activity": weakest["recency"]["days_since_last_activity"],
            "factor_percent": weakest["recency"]["factor_percent"],
            "decay_percent": weakest["recency"]["decay_percent"],
            "branch": weakest["label"],
            "note": recency_note,
        },
        "continuing_education": {
            "hours_12m": hours_12m,
            "target_hours": 40,
            "percent": ce_percent,
            "met": hours_12m >= 40,
            "status": "met" if hours_12m >= 40 else "building",
            "note": (
                "Aim for 40 hours of hands-on practice a year, like a continuing-"
                "education requirement. This is a practice target, not a "
                "certification claim."
            ),
        },
        "quiz": {
            "attempts": signals["quiz_attempts"],
            "labs": signals["quiz_labs"],
            "accuracy": signals["quiz_accuracy"],
        },
        "signals": {
            key: value.isoformat() if isinstance(value, datetime) else value
            for key, value in signals.items()
            if key != "branch_last_activity"
        },
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

    * offensive core and assessment exercises count as Tester;
    * advanced/expert exercises count as Leader (capstone/advanced work);
    * OSINT, forensics, and malware analysis count as Investigator;
    * network analysis and OT count as Defender;
    * builder categories count as Builder;
    * reconnaissance, enumeration, and the remaining foundations count as
      Explorer.
    """
    if lab is None:
        return "explorer"
    category = (getattr(lab, "category", None) or "general").strip().lower()
    difficulty = (getattr(lab, "difficulty", None) or "").strip().lower()
    level = getattr(lab, "level", None)
    track = getattr(level, "track", None) if level else None
    track_slug = _track_slug(track)

    if category in TESTER_CATEGORIES:
        return "tester"
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
