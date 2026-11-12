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
    # Cyber DNA never reaches 100: there is always another branch to develop.
    return max(0, min(99, round(value)))


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
        .filter(LabCompletion.user_id == user_id)
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

    for row in completions:
        lab: Lab | None = getattr(row, "lab", None)
        level = getattr(lab, "level", None) if lab else None
        track = getattr(level, "track", None) if level else None
        track_slug = _track_slug(track)
        category = (getattr(lab, "category", None) or "general").strip().lower()
        branches = {"explorer", "builder"}

        if track_slug or track is not None:
            tracks.add(track_slug or (track.name or "").strip().lower())
        categories.add(category)

        if category in DEFENDER_CATEGORIES or track_slug in DEFENDER_TRACKS:
            defender_labs += 1
            branches.add("defender")
            if track_slug:
                defender_tracks.add(track_slug)
        if category in INVESTIGATOR_CATEGORIES or track_slug in INVESTIGATOR_TRACKS:
            investigator_labs += 1
            branches.add("investigator")
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
            if (row.hints_used or 0) == 0:
                offensive_no_hint_labs += 1
        if category == "assessment":
            assessment_labs += 1
            branches.add("tester")

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
        strength = 1.0
        if (row.hints_used or 0) == 0:
            strength += 0.5
        if (row.attempts or 1) <= 1:
            strength += 0.25
        if is_advanced:
            strength += 0.75
        if category == "assessment":
            strength += 0.5
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
        quiz_strength = 0.75 + (best / 100) * 0.75
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
    evidence_weight["explorer"] += 0.5 * len(session_lab_ids - completed_lab_ids)
    evidence_weight["explorer"] += 0.25 * len(tracks) + 0.25 * len(categories)
    evidence_weight["leader"] += (
        1.5 * int(courses)
        + 0.5 * int(achievements)
        + 3.0 * int(instructed)
        + 0.25 * int(likes_given)
    )

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
        "branch_last_activity": branch_last_at,
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
    tester = _clamp(
        9 * min(signals["offensive_core_labs"], 12)
        + 2 * min(signals["offensive_labs"], 20)
        + 3 * min(len(signals["offensive_categories"]), 4)
        + 1 * min(signals["offensive_no_hint_labs"], 10)
        + 3 * min(signals["assessment_labs"], 4)
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
        6 * min(signals["courses"], 5)
        + 2 * min(signals["achievements"], 20)
        + 4 * min(signals["advanced_labs"], 10)
        + 8 * min(signals["instructed_courses"], 3)
        + 1 * min(signals["likes_given"], 10)
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
    return {
        "offensive": signals["offensive_core_labs"] + signals["assessment_labs"],
        "defensive": signals["defender_labs"],
        "investigative": signals["investigator_labs"],
        "leadership": (
            signals["event_achievements"]
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
        if signals["assessment_labs"]:
            parts.append(f"{signals['assessment_labs']} assessments")
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
        f"{signals['event_achievements']} event awards · "
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


def _recency_factor(days: int | None) -> float:
    """Keep practice current: a long break slowly lowers the training signal.

    A new completion resets the factor to 1.0, so the effect is repair by
    practice, not a permanent penalty. The floor is 0.90 (10% at most).
    """
    if days is None or days <= 14:
        return 1.0
    if days <= 30:
        return 0.99
    if days <= 60:
        return 0.97
    if days <= 90:
        return 0.94
    return 0.90


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
