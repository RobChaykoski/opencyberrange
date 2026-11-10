"""Achievement titles for the learner character sheet.

Titles are cosmetic. They do not grant lab access, change scores, or rank
learners against each other. A title is unlocked by an existing achievement;
the learner may equip one unlocked title. With no equipped title, the profile
shows the current Skill DNA class instead.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Achievement, User
from app.services.achievements import (
    ACHIEVEMENT_DESCRIPTIONS,
    competition_achievement_parts,
)

RARITIES = ("common", "uncommon", "rare", "epic", "legendary")


@dataclass(frozen=True)
class TitleDef:
    key: str
    label: str
    description: str
    rarity: str
    achievement_types: tuple[str, ...] = ()
    competition_codes: tuple[str, ...] = ()
    hidden: bool = False


# Built-in titles. The label is deliberately the achievement language the
# learner already sees, so the title collection reinforces the badge collection
# instead of inventing a second vocabulary.
TITLE_CATALOG: tuple[TitleDef, ...] = (
    TitleDef("recruit", "Recruit", "The first step into the range.", "common"),
    TitleDef(
        "first_blood",
        "First Blood",
        ACHIEVEMENT_DESCRIPTIONS["first_blood"],
        "rare",
        ("first_blood",),
    ),
    TitleDef(
        "self_reliant",
        "Self-Reliant",
        ACHIEVEMENT_DESCRIPTIONS["no_hints"],
        "common",
        ("no_hints",),
    ),
    TitleDef(
        "perfectionist",
        "Perfectionist",
        ACHIEVEMENT_DESCRIPTIONS["perfectionist"],
        "rare",
        ("perfectionist",),
    ),
    TitleDef(
        "speed_demon",
        "Speed Demon",
        ACHIEVEMENT_DESCRIPTIONS["speed_demon"],
        "rare",
        ("speed_demon",),
    ),
    TitleDef(
        "clean_sweep",
        "Clean Sweep",
        ACHIEVEMENT_DESCRIPTIONS["clean_sweep"],
        "epic",
        ("clean_sweep",),
    ),
    TitleDef(
        "on_a_roll",
        "On a Roll",
        ACHIEVEMENT_DESCRIPTIONS["streak"],
        "uncommon",
        ("streak",),
    ),
    TitleDef(
        "curious_mind",
        "Curious Mind",
        ACHIEVEMENT_DESCRIPTIONS["learning_hours_1"],
        "common",
        ("learning_hours_1",),
    ),
    TitleDef(
        "deep_dive",
        "Deep Dive",
        ACHIEVEMENT_DESCRIPTIONS["learning_hours_5"],
        "uncommon",
        ("learning_hours_5",),
    ),
    TitleDef(
        "dedicated_learner",
        "Dedicated Learner",
        ACHIEVEMENT_DESCRIPTIONS["learning_hours_15"],
        "rare",
        ("learning_hours_15",),
    ),
    TitleDef(
        "scholar",
        "Scholar",
        ACHIEVEMENT_DESCRIPTIONS["learning_hours_30"],
        "epic",
        ("learning_hours_30",),
    ),
    TitleDef(
        "checking_in",
        "Checking In",
        ACHIEVEMENT_DESCRIPTIONS["login_streak_3"],
        "common",
        ("login_streak_3",),
    ),
    TitleDef(
        "week_strong",
        "Week Strong",
        ACHIEVEMENT_DESCRIPTIONS["login_streak_7"],
        "uncommon",
        ("login_streak_7",),
    ),
    TitleDef(
        "month_of_momentum",
        "Month of Momentum",
        ACHIEVEMENT_DESCRIPTIONS["login_streak_30"],
        "epic",
        ("login_streak_30",),
    ),
    TitleDef(
        "rangebox_rookie",
        "RangeBox Rookie",
        ACHIEVEMENT_DESCRIPTIONS["rangebox_rookie"],
        "common",
        ("rangebox_rookie",),
        hidden=True,
    ),
    TitleDef(
        "file_hunter",
        "File Hunter",
        ACHIEVEMENT_DESCRIPTIONS["file_hunter"],
        "common",
        ("file_hunter",),
        hidden=True,
    ),
    TitleDef(
        "header_hunter",
        "Header Hunter",
        ACHIEVEMENT_DESCRIPTIONS["header_hunter"],
        "common",
        ("header_hunter",),
        hidden=True,
    ),
    TitleDef(
        "source_sleuth",
        "Source Sleuth",
        ACHIEVEMENT_DESCRIPTIONS["source_sleuth"],
        "common",
        ("source_sleuth",),
        hidden=True,
    ),
    TitleDef(
        "log_detective",
        "Log Detective",
        ACHIEVEMENT_DESCRIPTIONS["log_detective"],
        "rare",
        ("log_detective",),
        hidden=True,
    ),
    TitleDef(
        "rangebox_ranger",
        "RangeBox Ranger",
        ACHIEVEMENT_DESCRIPTIONS["rangebox_ranger"],
        "rare",
        ("rangebox_ranger",),
        hidden=True,
    ),
    TitleDef(
        "forensics_pathfinder",
        "Forensics Pathfinder",
        ACHIEVEMENT_DESCRIPTIONS["forensics_pathfinder"],
        "rare",
        ("forensics_pathfinder",),
        hidden=True,
    ),
    TitleDef(
        "mfa_recovery_ace",
        "Recovery Architect",
        ACHIEVEMENT_DESCRIPTIONS["mfa_recovery_ace"],
        "rare",
        ("mfa_recovery_ace",),
        hidden=True,
    ),
    TitleDef(
        "provenance_analyst",
        "Provenance Analyst",
        ACHIEVEMENT_DESCRIPTIONS["provenance_analyst"],
        "rare",
        ("provenance_analyst",),
        hidden=True,
    ),
    TitleDef(
        "liquidity_tracker",
        "Liquidity Tracker",
        ACHIEVEMENT_DESCRIPTIONS["liquidity_tracker"],
        "rare",
        ("liquidity_tracker",),
        hidden=True,
    ),
    TitleDef(
        "digital_frontier",
        "Digital Frontier",
        ACHIEVEMENT_DESCRIPTIONS["digital_frontier"],
        "epic",
        ("digital_frontier",),
        hidden=True,
    ),
    TitleDef(
        "quiz_ace",
        "Quiz Ace",
        ACHIEVEMENT_DESCRIPTIONS["quiz_ace"],
        "rare",
        ("quiz_ace",),
    ),
    TitleDef(
        "quiz_explorer",
        "Quiz Explorer",
        ACHIEVEMENT_DESCRIPTIONS["quiz_explorer"],
        "uncommon",
        ("quiz_explorer",),
    ),
    TitleDef(
        "quiz_scholar",
        "Quiz Scholar",
        ACHIEVEMENT_DESCRIPTIONS["quiz_scholar"],
        "epic",
        ("quiz_scholar",),
    ),
    TitleDef(
        "quiz_comeback",
        "Quiz Comeback",
        ACHIEVEMENT_DESCRIPTIONS["quiz_comeback"],
        "rare",
        ("quiz_comeback",),
    ),
    TitleDef(
        "shell_shocked",
        "Shell Shocked",
        ACHIEVEMENT_DESCRIPTIONS["shell_shocked"],
        "epic",
        ("shell_shocked",),
        hidden=True,
    ),
    TitleDef(
        "source_whisperer",
        "Source Whisperer",
        ACHIEVEMENT_DESCRIPTIONS["source_whisperer"],
        "rare",
        ("source_whisperer",),
        hidden=True,
    ),
    TitleDef(
        "memory_miner",
        "Memory Miner",
        ACHIEVEMENT_DESCRIPTIONS["memory_miner"],
        "rare",
        ("memory_miner",),
        hidden=True,
    ),
    TitleDef(
        "ghost_in_the_ram",
        "Ghost in the RAM",
        ACHIEVEMENT_DESCRIPTIONS["ghost_in_the_ram"],
        "epic",
        ("ghost_in_the_ram",),
        hidden=True,
    ),
    TitleDef(
        "voice_from_the_wire",
        "Voice from the Wire",
        ACHIEVEMENT_DESCRIPTIONS["voice_from_the_wire"],
        "rare",
        ("voice_from_the_wire",),
        hidden=True,
    ),
    TitleDef(
        "sip_whisperer",
        "SIP Whisperer",
        ACHIEVEMENT_DESCRIPTIONS["sip_whisperer"],
        "epic",
        ("sip_whisperer",),
        hidden=True,
    ),
    TitleDef(
        "competitor",
        "Event Participant",
        "Joined a time-boxed event leaderboard.",
        "common",
        competition_codes=("c",),
    ),
    TitleDef(
        "event_first_blood",
        "Event First Blood",
        "First participant to solve an exercise in an event.",
        "rare",
        competition_codes=("fb",),
    ),
    TitleDef(
        "event_clean_sweep",
        "Event Clean Sweep",
        "Solved every exercise in an event.",
        "epic",
        competition_codes=("cs",),
    ),
    TitleDef(
        "perfect_event",
        "Perfect Event",
        "Solved every event exercise without hints and on the first attempt.",
        "legendary",
        competition_codes=("pr",),
    ),
    TitleDef(
        "champion",
        "Champion",
        "Finished first in an event.",
        "legendary",
        competition_codes=("ch",),
    ),
    TitleDef(
        "runner_up",
        "Runner-up",
        "Finished second in an event.",
        "epic",
        competition_codes=("ru",),
    ),
    TitleDef(
        "third_place",
        "Third Place",
        "Finished third in an event.",
        "rare",
        competition_codes=("tp",),
    ),
)

TITLE_BY_KEY = {title.key: title for title in TITLE_CATALOG}


def title_catalog() -> tuple[TitleDef, ...]:
    return TITLE_CATALOG


def _achievement_dates(db: Session, user_id: int) -> tuple[dict[str, object], set[str]]:
    """Return earliest award date per type and the competition badge codes."""
    dates: dict[str, object] = {}
    competition_codes: set[str] = set()
    rows = db.query(Achievement).filter(Achievement.user_id == user_id).all()
    for row in rows:
        awarded = getattr(row, "awarded_at", None)
        current = dates.get(row.achievement_type)
        if current is None or (awarded is not None and awarded < current):
            dates[row.achievement_type] = awarded
        parts = competition_achievement_parts(row.achievement_type)
        if parts is not None:
            competition_codes.add(parts[1])
    return dates, competition_codes


def _awarded_for_title(
    title: TitleDef,
    dates: dict[str, object],
    competition_codes: set[str],
) -> object | None:
    matches = [dates[type_] for type_ in title.achievement_types if type_ in dates]
    if title.competition_codes and any(code in competition_codes for code in title.competition_codes):
        matches.extend(
            value
            for type_, value in dates.items()
            if (parts := competition_achievement_parts(type_)) is not None
            and parts[1] in title.competition_codes
        )
    matches = [value for value in matches if value is not None]
    return min(matches) if matches else None


def resolve_titles(
    db: Session,
    user: User,
    *,
    class_title: str | None = None,
    class_key: str | None = None,
) -> dict:
    """Return the full title collection plus the currently displayed title.

    Locked hidden titles do not reveal their label. The class title is a
    synthetic title used when the learner has not equipped an achievement
    title; it is not part of the collectible catalog.
    """
    dates, competition_codes = _achievement_dates(db, user.id)
    rows = []
    for title in TITLE_CATALOG:
        awarded = _awarded_for_title(title, dates, competition_codes)
        unlocked = title.key == "recruit" or awarded is not None
        label = title.label
        description = title.description
        if title.hidden and not unlocked:
            label = "Secret title"
            description = "Complete a hidden challenge to reveal this title."
        rows.append(
            {
                "key": title.key,
                "label": label,
                "description": description,
                "rarity": title.rarity,
                "hidden": title.hidden,
                "unlocked": unlocked,
                "equipped": user.equipped_title == title.key,
                "awarded_at": awarded.isoformat() if hasattr(awarded, "isoformat") else None,
            }
        )

    equipped_key = user.equipped_title if user.equipped_title in TITLE_BY_KEY else None
    equipped_row = next((row for row in rows if row["key"] == equipped_key), None)
    if equipped_row is None or not equipped_row["unlocked"]:
        equipped_row = {
            "key": "class",
            "class_key": class_key or "recruit",
            "label": class_title or "Recruit",
            "description": "Your current Skill DNA class.",
            "rarity": "class",
            "hidden": False,
            "unlocked": True,
            "equipped": True,
            "awarded_at": None,
        }

    unlocked_count = sum(1 for row in rows if row["unlocked"])
    return {
        "equipped": equipped_row,
        "class_title": class_title or "Recruit",
        "unlocked_count": unlocked_count,
        "rare_count": sum(
            1 for row in rows if row["unlocked"] and row["rarity"] in {"rare", "epic", "legendary"}
        ),
        "titles": rows,
    }


def equip_title(db: Session, user: User, key: str | None) -> dict:
    """Equip an unlocked title, or clear it to return to the class title."""
    if key in (None, "", "class"):
        user.equipped_title = None
        db.commit()
        return {"equipped_title": None}

    title = TITLE_BY_KEY.get(key)
    if title is None:
        raise ValueError("Unknown title")
    dates, competition_codes = _achievement_dates(db, user.id)
    awarded = _awarded_for_title(title, dates, competition_codes)
    if title.key != "recruit" and awarded is None:
        raise ValueError("Title is not unlocked")
    user.equipped_title = title.key
    db.commit()
    return {"equipped_title": title.key}
