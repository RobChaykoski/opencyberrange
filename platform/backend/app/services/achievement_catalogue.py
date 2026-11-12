"""Achievement catalogue: one friendly, grouped view for administrators.

Built-in achievements are code paths, not database rows. This service gives them
the same presentation metadata as admin-defined achievements so the studio can
group, filter, and explain every badge in one place.

Value model: a badge's points come from its tier and difficulty. That keeps the
number meaningful without a second scoring table, and it lets a platinum badge on
an expert exercise be worth more than a bronze badge on a starter exercise.
"""

from __future__ import annotations

from collections import Counter

from sqlalchemy.orm import Session

from app.models import CustomAchievement
from app.services.achievements import (
    ACHIEVEMENT_DESCRIPTIONS,
    ACHIEVEMENT_LABELS,
    BUILTIN_ACHIEVEMENT_ICONS,
    CUSTOM_ACHIEVEMENT_TRIGGERS,
    HIDDEN_ACHIEVEMENT_TYPES,
    QUIZ_ACE,
    QUIZ_COMEBACK,
    QUIZ_EXPLORER,
    QUIZ_FIVE_STREAK,
    QUIZ_HAT_TRICK,
    QUIZ_PLATINUM,
    QUIZ_POLYMATH,
    QUIZ_RELEVANCE_ACE,
    QUIZ_SCHOLAR,
    QUIZ_TIER_CLIMB,
)

TIERS = [
    {
        "key": "bronze",
        "label": "Bronze",
        "base_points": 10,
        "description": "A first step or a small habit.",
    },
    {
        "key": "silver",
        "label": "Silver",
        "base_points": 25,
        "description": "A solid piece of practice.",
    },
    {
        "key": "gold",
        "label": "Gold",
        "base_points": 50,
        "description": "Sustained or higher-difficulty evidence.",
    },
    {
        "key": "platinum",
        "label": "Platinum",
        "base_points": 100,
        "description": "A standout, SWOCTS-specific achievement.",
    },
]

DIFFICULTIES = [
    {"key": "starter", "label": "Starter", "multiplier": 0.75, "description": "Entry-level work."},
    {"key": "standard", "label": "Standard", "multiplier": 1.0, "description": "Normal exercise difficulty."},
    {"key": "advanced", "label": "Advanced", "multiplier": 1.5, "description": "Advanced or multi-step work."},
    {"key": "expert", "label": "Expert", "multiplier": 2.0, "description": "Expert, hidden, or collection-level work."},
]

GROUPS = [
    {
        "key": "foundations",
        "label": "Foundations",
        "description": "First completions and clean-practice habits.",
    },
    {
        "key": "consistency",
        "label": "Consistency",
        "description": "Time invested and returning to practice.",
    },
    {
        "key": "quiz",
        "label": "Knowledge checks",
        "description": "Short sampled checks, including the platinum sampled-quiz ladder.",
    },
    {
        "key": "tracks",
        "label": "Tracks and collections",
        "description": "Whole-track and themed collection badges.",
    },
    {
        "key": "hidden",
        "label": "Hidden discoveries",
        "description": "Specific exercise discoveries. Hidden until earned.",
    },
    {
        "key": "custom",
        "label": "Custom",
        "description": "Admin-defined goals for a course or programme.",
    },
]

GROUP_BY_KEY = {group["key"]: group for group in GROUPS}
TIER_BY_KEY = {tier["key"]: tier for tier in TIERS}
DIFFICULTY_BY_KEY = {difficulty["key"]: difficulty for difficulty in DIFFICULTIES}

# type -> (group, tier, difficulty)
BUILTIN_METADATA: dict[str, tuple[str, str, str]] = {
    "first_blood": ("foundations", "silver", "standard"),
    "no_hints": ("foundations", "bronze", "standard"),
    "perfectionist": ("foundations", "silver", "standard"),
    "speed_demon": ("foundations", "silver", "advanced"),
    "clean_sweep": ("tracks", "gold", "advanced"),
    "streak": ("foundations", "silver", "standard"),
    "shell_shocked": ("hidden", "platinum", "expert"),
    "source_whisperer": ("hidden", "gold", "advanced"),
    "memory_miner": ("hidden", "silver", "advanced"),
    "ghost_in_the_ram": ("hidden", "gold", "advanced"),
    "voice_from_the_wire": ("hidden", "silver", "advanced"),
    "sip_whisperer": ("hidden", "gold", "advanced"),
    "rangebox_rookie": ("hidden", "bronze", "starter"),
    "file_hunter": ("hidden", "bronze", "starter"),
    "header_hunter": ("hidden", "bronze", "starter"),
    "source_sleuth": ("hidden", "bronze", "starter"),
    "log_detective": ("hidden", "silver", "standard"),
    "log_reviewer": ("hidden", "bronze", "starter"),
    "evidence_explorer": ("hidden", "silver", "standard"),
    "stage2_explorer": ("tracks", "gold", "advanced"),
    "rangebox_ranger": ("tracks", "gold", "advanced"),
    "forensics_pathfinder": ("tracks", "gold", "advanced"),
    "mfa_recovery_ace": ("hidden", "silver", "standard"),
    "provenance_analyst": ("hidden", "silver", "standard"),
    "liquidity_tracker": ("hidden", "silver", "standard"),
    "digital_frontier": ("tracks", "platinum", "advanced"),
    "learning_hours_1": ("consistency", "bronze", "starter"),
    "learning_hours_5": ("consistency", "silver", "standard"),
    "learning_hours_15": ("consistency", "gold", "advanced"),
    "learning_hours_30": ("consistency", "platinum", "expert"),
    "login_streak_3": ("consistency", "bronze", "starter"),
    "login_streak_7": ("consistency", "silver", "standard"),
    "login_streak_30": ("consistency", "gold", "advanced"),
    "quiz_ace": ("quiz", "silver", "standard"),
    "quiz_explorer": ("quiz", "silver", "standard"),
    "quiz_scholar": ("quiz", "gold", "advanced"),
    "quiz_comeback": ("quiz", "bronze", "standard"),
    "quiz_platinum": ("quiz", "platinum", "standard"),
    "quiz_relevance_ace": ("quiz", "platinum", "advanced"),
    "quiz_hat_trick": ("quiz", "gold", "standard"),
    "quiz_five_streak": ("quiz", "silver", "standard"),
    "quiz_tier_climb": ("quiz", "gold", "advanced"),
    "quiz_polymath": ("quiz", "platinum", "expert"),
}

QUIZ_TYPES = {
    QUIZ_ACE,
    QUIZ_COMEBACK,
    QUIZ_EXPLORER,
    QUIZ_FIVE_STREAK,
    QUIZ_HAT_TRICK,
    QUIZ_PLATINUM,
    QUIZ_POLYMATH,
    QUIZ_RELEVANCE_ACE,
    QUIZ_SCHOLAR,
    QUIZ_TIER_CLIMB,
}

DEFAULT_GROUP = "custom"
DEFAULT_TIER = "bronze"
DEFAULT_DIFFICULTY = "standard"


def points_for(tier: str, difficulty: str) -> int:
    """Return a friendly point value for a tier and difficulty.

    Tier sets the base and difficulty scales it, so a platinum expert badge is
    worth far more than a bronze starter badge. Values are rounded to whole
    points rather than a coarse band so the difficulty difference stays visible.
    """
    tier_row = TIER_BY_KEY.get(tier) or TIER_BY_KEY[DEFAULT_TIER]
    difficulty_row = DIFFICULTY_BY_KEY.get(difficulty) or DIFFICULTY_BY_KEY[DEFAULT_DIFFICULTY]
    raw = tier_row["base_points"] * difficulty_row["multiplier"]
    return max(5, int(round(raw)))


def _public_tiers() -> list[dict]:
    return [
        {
            **tier,
            "points": tier["base_points"],
        }
        for tier in TIERS
    ]


def _group_label(group_key: str) -> str:
    return GROUP_BY_KEY.get(group_key, GROUP_BY_KEY[DEFAULT_GROUP])["label"]


def _builtin_rows() -> list[dict]:
    rows = []
    for achievement_type, label in ACHIEVEMENT_LABELS.items():
        group_key, tier, difficulty = BUILTIN_METADATA.get(
            achievement_type, (DEFAULT_GROUP, DEFAULT_TIER, DEFAULT_DIFFICULTY)
        )
        rows.append(
            {
                "id": f"builtin:{achievement_type}",
                "type": achievement_type,
                "name": label,
                "description": ACHIEVEMENT_DESCRIPTIONS.get(achievement_type, ""),
                "icon": BUILTIN_ACHIEVEMENT_ICONS.get(achievement_type, "\U0001F3C5"),
                "source": "builtin",
                "group_key": group_key,
                "group_label": _group_label(group_key),
                "tier": tier,
                "difficulty": difficulty,
                "points": points_for(tier, difficulty),
                "is_active": True,
                "hidden": achievement_type in HIDDEN_ACHIEVEMENT_TYPES,
                "trigger": None,
                "threshold": None,
                "editable": False,
                "quiz": achievement_type in QUIZ_TYPES,
            }
        )
    rows.sort(key=lambda row: (row["group_key"], row["tier"], row["name"]))
    return rows


def serialize_custom_achievement(row: CustomAchievement) -> dict:
    group_key = row.group_key or DEFAULT_GROUP
    tier = row.tier or DEFAULT_TIER
    difficulty = row.difficulty or DEFAULT_DIFFICULTY
    return {
        "id": f"custom:{row.id}",
        "custom_id": row.id,
        "type": f"custom_{row.id}",
        "name": row.name,
        "description": row.description or "",
        "icon": row.icon or "\U0001F3C5",
        "source": "custom",
        "group_key": group_key,
        "group_label": _group_label(group_key),
        "tier": tier,
        "difficulty": difficulty,
        "points": row.points or points_for(tier, difficulty),
        "is_active": row.is_active,
        "hidden": False,
        "trigger": row.trigger,
        "threshold": row.threshold,
        "editable": True,
        "quiz": False,
        "created_at": row.created_at,
    }


def _custom_rows(db: Session) -> list[dict]:
    rows = db.query(CustomAchievement).order_by(
        CustomAchievement.created_at.asc(), CustomAchievement.id.asc()
    ).all()
    return [serialize_custom_achievement(row) for row in rows]


def build_catalogue(db: Session) -> dict:
    """Return every achievement, grouped and filterable, plus summary counts."""
    achievements = _builtin_rows() + _custom_rows(db)
    tier_counts = Counter(row["tier"] for row in achievements)
    group_counts = Counter(row["group_key"] for row in achievements)
    return {
        "groups": GROUPS,
        "tiers": _public_tiers(),
        "difficulties": DIFFICULTIES,
        "triggers": [
            {"value": key, "label": label}
            for key, label in CUSTOM_ACHIEVEMENT_TRIGGERS.items()
        ],
        "achievements": achievements,
        "summary": {
            "total": len(achievements),
            "builtin": sum(1 for row in achievements if row["source"] == "builtin"),
            "custom": sum(1 for row in achievements if row["source"] == "custom"),
            "active": sum(1 for row in achievements if row["is_active"]),
            "inactive": sum(1 for row in achievements if not row["is_active"]),
            "hidden": sum(1 for row in achievements if row["hidden"]),
            "total_points": sum(row["points"] for row in achievements),
            "by_tier": {tier["key"]: tier_counts.get(tier["key"], 0) for tier in TIERS},
            "by_group": {
                group["key"]: group_counts.get(group["key"], 0) for group in GROUPS
            },
        },
        "note": (
            "Points come from tier and difficulty. Built-in achievements run in "
            "code and are read-only here; custom achievements are evaluated after "
            "the built-in checks."
        ),
    }
