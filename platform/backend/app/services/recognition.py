"""Recognition catalogue, rules, and awards.

Recognition is the values-based layer: integrity, mentorship, service,
curiosity, and durable contribution. It is separate from the course
micro-credentials in ``achievements.py`` and never changes the Legacy Score.

The catalogue lives on the server. An unearned award is returned as a tier and
a clue, never as a trigger. Secret awards do not expose progress.
"""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app.models import User
from app.models.impact import ImpactContribution
from app.models.recognition import RecognitionAward
from app.services.audit import log_admin_action
from app.services.evidence import _tenant_of

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "achievements.yaml"

INSTRUCTOR_ROLES = frozenset(
    {"admin", "institution_admin", "instructor", "mentor", "teaching_assistant"}
)


class RecognitionError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@lru_cache(maxsize=1)
def load_catalogue() -> dict:
    with DATA_FILE.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def awards() -> list[dict]:
    return list(load_catalogue().get("achievements") or [])


def _by_key() -> dict[str, dict]:
    return {str(row["key"]): row for row in awards()}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _verified(db: Session, user: User) -> list[ImpactContribution]:
    return (
        db.query(ImpactContribution)
        .filter(
            ImpactContribution.user_id == user.id,
            ImpactContribution.status == "verified",
        )
        .order_by(ImpactContribution.occurred_at.asc())
        .all()
    )


def _teach(rows):
    return [row for row in rows if row.dimension == "teach"]


def _mentoring(rows):
    return [
        row for row in rows if row.dimension == "teach" and row.kind == "mentoring"
    ]


def _reach(rows) -> int:
    return sum(int(row.reach_count or 0) for row in rows)


def _distinct_years(rows) -> int:
    return len({row.occurred_at.year for row in rows if row.occurred_at})


def _span_years(rows, now: datetime) -> float:
    dates = [row.occurred_at for row in rows if row.occurred_at]
    if not dates:
        return 0.0
    return (now - min(dates)).days / 365.0


def _rule_build_reach_100(ctx) -> bool:
    return any(
        row.dimension == "build" and int(row.reach_count or 0) >= 100
        for row in ctx["rows"]
    )


def _rule_tool_reach_10(ctx) -> bool:
    return any(
        row.dimension == "build"
        and row.kind in {"tool", "integration"}
        and int(row.reach_count or 0) >= 10
        for row in ctx["rows"]
    )


def _rule_architect_365(ctx) -> bool:
    for row in ctx["rows"]:
        if row.dimension not in {"build", "protect"}:
            continue
        if row.last_used_at and row.verified_at:
            if (row.last_used_at - row.verified_at).days >= 365:
                return True
    return False


def _rule_nonprofit_first(ctx) -> bool:
    return any(
        row.dimension == "serve" and row.kind == "nonprofit_support"
        for row in ctx["rows"]
    )


def _rule_small_business_five(ctx) -> bool:
    return (
        sum(
            1
            for row in ctx["rows"]
            if row.dimension == "serve"
            and row.kind in {"nonprofit_support", "small_business_support"}
        )
        >= 5
    )


def _rule_lighthouse(ctx) -> bool:
    if ctx["user"].role in INSTRUCTOR_ROLES:
        return False
    return _reach(_mentoring(ctx["rows"])) >= 100


def _rule_steward_3_years(ctx) -> bool:
    return _distinct_years(ctx["rows"]) >= 3


def _rule_myth_scale(ctx) -> bool:
    rows = ctx["rows"]
    taught = _reach(_teach(rows))
    organizations = sum(1 for row in rows if row.dimension == "protect")
    return (
        taught >= 10_000
        or organizations >= 100
        or _span_years(rows, ctx["now"]) >= 5
    )


def _rule_legacy_hidden(ctx) -> bool:
    rows = ctx["rows"]
    protected = any(row.dimension == "protect" for row in rows)
    taught = any(row.dimension == "teach" for row in rows)
    mentored = bool(_mentoring(rows))
    built_used = any(
        row.dimension == "build" and int(row.reach_count or 0) >= 1
        for row in rows
    )
    return (
        protected
        and taught
        and mentored
        and built_used
        and _distinct_years(rows) >= 3
    )


def _rule_helping_first(ctx) -> bool:
    return any(row.dimension in {"teach", "serve"} for row in ctx["rows"])


def _rule_helping_five(ctx) -> bool:
    return (
        sum(1 for row in ctx["rows"] if row.dimension in {"teach", "serve"}) >= 5
    )


def _rule_helping_25(ctx) -> bool:
    return _reach(_teach(ctx["rows"])) >= 25


RULES = {
    "build_reach_100": _rule_build_reach_100,
    "tool_reach_10": _rule_tool_reach_10,
    "architect_365": _rule_architect_365,
    "nonprofit_first": _rule_nonprofit_first,
    "small_business_five": _rule_small_business_five,
    "lighthouse": _rule_lighthouse,
    "steward_3_years": _rule_steward_3_years,
    "myth_scale": _rule_myth_scale,
    "legacy_hidden": _rule_legacy_hidden,
    "helping_first": _rule_helping_first,
    "helping_five": _rule_helping_five,
    "helping_25": _rule_helping_25,
}


def _earned_keys(db: Session, user: User) -> set[str]:
    return {
        row.achievement_key
        for row in db.query(RecognitionAward)
        .filter(RecognitionAward.user_id == user.id)
        .all()
    }


def _requirements_met(row: dict, earned: set[str]) -> bool:
    return all(str(key) in earned for key in (row.get("requires") or []))


def _award(
    db: Session,
    user: User,
    row: dict,
    source: str,
    awarded_by: User | None = None,
    evidence_ref: str | None = None,
    note: str | None = None,
) -> RecognitionAward:
    existing = (
        db.query(RecognitionAward)
        .filter(
            RecognitionAward.user_id == user.id,
            RecognitionAward.achievement_key == row["key"],
        )
        .first()
    )
    if existing is not None:
        return existing
    award = RecognitionAward(
        institution_id=_tenant_of(user),
        user_id=user.id,
        achievement_key=row["key"],
        source=source,
        awarded_at=_now(),
        awarded_by_id=awarded_by.id if awarded_by else None,
        evidence_ref=evidence_ref,
        note=note,
    )
    db.add(award)
    db.commit()
    db.refresh(award)
    return award


def _award_payload(
    award: RecognitionAward, row: dict, unseen: bool
) -> dict:
    return {
        "key": award.achievement_key,
        "title": row.get("title"),
        "marker": row.get("marker"),
        "tradition": row.get("tradition"),
        "category": row.get("category"),
        "tier": row.get("tier"),
        "clue": row.get("clue"),
        "earned_message": row.get("earned_message"),
        "earned": True,
        "source": award.source,
        "awarded_at": (
            award.awarded_at.isoformat() + "Z" if award.awarded_at else None
        ),
        "unseen": unseen,
    }


def evaluate(db: Session, user: User, now: datetime | None = None) -> list[dict]:
    """Award every active rule that now holds. Idempotent."""
    current = now or _now()
    rows = _verified(db, user)
    earned = _earned_keys(db, user)
    ctx = {"rows": rows, "user": user, "now": current}
    newly: list[dict] = []
    for row in awards():
        key = str(row["key"])
        if key in earned:
            continue
        if not _requirements_met(row, earned):
            continue
        if row.get("status") != "active":
            continue
        rule = RULES.get(str(row.get("rule")))
        if rule is None or not rule(ctx):
            continue
        award = _award(db, user, row, "auto")
        earned.add(key)
        newly.append(_award_payload(award, row, True))
    return newly


def board(db: Session, user: User, now: datetime | None = None) -> dict:
    """The learner's board: earned awards, clues, and a sealed count."""
    current = now or _now()
    awards_by_key = {
        row.achievement_key: row
        for row in db.query(RecognitionAward)
        .filter(RecognitionAward.user_id == user.id)
        .all()
    }
    earned = set(awards_by_key)
    earned_rows: list[dict] = []
    visible: list[dict] = []
    sealed = 0
    for row in awards():
        key = str(row["key"])
        if key in awards_by_key:
            award = awards_by_key[key]
            earned_rows.append(
                _award_payload(award, row, award.seen_at is None)
            )
            continue
        if row.get("tier") == "mythic":
            sealed += 1
            continue
        if not _requirements_met(row, earned):
            continue
        visible.append(
            {
                "key": None,
                "title": (
                    row.get("title")
                    if row.get("tier") == "public"
                    else ("????" if row.get("tier") == "legendary" else "Unknown")
                ),
                "category": row.get("category"),
                "tradition": row.get("tradition"),
                "tier": row.get("tier"),
                "clue": row.get("clue"),
                "earned": False,
                "sealed": False,
            }
        )
    whispers = list(load_catalogue().get("whispers") or [])
    whisper = whispers[current.toordinal() % len(whispers)] if whispers else None
    return {
        "earned": sorted(
            earned_rows,
            key=lambda item: (item["awarded_at"] or "", item["key"]),
        ),
        "visible": visible,
        "sealed": sealed,
        "whisper": whisper,
        "rules": "Recognition only. Achievements never change your Legacy Score.",
    }


def manual_award(
    db: Session,
    admin: User,
    learner: User,
    key: str,
    evidence_ref: str,
    note: str,
) -> dict:
    if admin.role not in {"admin", "institution_admin"}:
        raise RecognitionError(
            "achievement_forbidden",
            "Only an administrator can award an achievement manually.",
            403,
        )
    row = _by_key().get(str(key))
    if row is None:
        raise RecognitionError(
            "achievement_unknown",
            "Unknown achievement.",
            404,
        )
    if row.get("status") != "manual":
        raise RecognitionError(
            "achievement_not_manual",
            "This achievement is not awarded manually.",
        )
    evidence_ref = str(evidence_ref or "").strip()
    note = str(note or "").strip()
    if len(evidence_ref) < 3:
        raise RecognitionError(
            "achievement_evidence_required",
            "A manual award needs an evidence reference.",
        )
    if len(note) < 10:
        raise RecognitionError(
            "achievement_note_required",
            "A manual award needs a note of at least 10 characters.",
        )
    earned = _earned_keys(db, learner)
    if not _requirements_met(row, earned):
        raise RecognitionError(
            "achievement_locked",
            "This achievement is not yet available.",
        )
    award = _award(
        db,
        learner,
        row,
        "manual",
        awarded_by=admin,
        evidence_ref=evidence_ref,
        note=note,
    )
    log_admin_action(
        action="ACHIEVEMENT_AWARDED",
        admin_user_id=admin.id,
        admin_username=admin.username,
        target_type="user",
        target_id=learner.id,
        target_identifier=learner.username,
        details={
            "achievement": row["key"],
            "evidence_ref": evidence_ref,
            "note": note,
        },
    )
    return _award_payload(award, row, True)


def mark_seen(db: Session, user: User) -> int:
    updated = (
        db.query(RecognitionAward)
        .filter(
            RecognitionAward.user_id == user.id,
            RecognitionAward.seen_at.is_(None),
        )
        .update({"seen_at": _now()}, synchronize_session=False)
    )
    db.commit()
    return int(updated or 0)
