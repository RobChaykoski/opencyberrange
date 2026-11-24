"""The Living Archive.

Traditions are **observed, not declared**. A learner never selects an archetype.
The archive reads verified contribution and describes a pattern in plain
language. Until there is enough evidence it says so.

The service deliberately returns no percentage and no ranking. It returns a
status, at most one emerging tradition, narrative notes, and the observation
counts that produced them.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import User
from app.models.impact import ImpactContribution
from app.services import journeys as journey_service

MIN_CONTRIBUTIONS = 3
MIN_DISTINCT_KINDS = 2
RECOGNIZED_CONTRIBUTIONS = 6
RECOGNIZED_DISTINCT_KINDS = 3
RECOGNIZED_SPAN_DAYS = 180

# Each contribution has one primary tradition. A contribution is never counted
# in two traditions, so the observation is stable and explainable.
TRADITION_BY_KIND: dict[tuple[str, str], str] = {
    ("protect", "assessment"): "Protection",
    ("protect", "remediation"): "Protection",
    ("protect", "mfa_rollout"): "Protection",
    ("protect", "exercise"): "Protection",
    ("protect", "monitoring"): "Stewardship",
    ("protect", "policy"): "Judgment",
    ("build", "lab"): "Creation",
    ("build", "tool"): "Creation",
    ("build", "integration"): "Creation",
    ("build", "workbook"): "Creation",
    ("build", "detection_rule"): "Protection",
    ("build", "playbook"): "Stewardship",
    ("build", "documentation"): "Stewardship",
    ("build", "research"): "Discovery",
    ("teach", "workshop"): "Illumination",
    ("teach", "mentoring"): "Illumination",
    ("teach", "course_material"): "Illumination",
    ("teach", "presentation"): "Illumination",
    ("teach", "teach_back"): "Illumination",
    ("teach", "publication"): "Discovery",
    ("serve", "nonprofit_support"): "Service",
    ("serve", "small_business_support"): "Service",
    ("serve", "student_support"): "Service",
    ("serve", "service_hours"): "Service",
    ("serve", "community_event"): "Connection",
    ("serve", "judging"): "Connection",
}


class ArchiveError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _tradition_for(row: ImpactContribution) -> str | None:
    return TRADITION_BY_KIND.get((str(row.dimension), str(row.kind)))


def _tradition_payload(title: str) -> dict | None:
    for tradition in journey_service.traditions():
        if tradition.get("title") == title:
            return {
                "id": tradition.get("id"),
                "title": tradition.get("title"),
                "archetype": tradition.get("archetype"),
                "future_view": tradition.get("future_view"),
            }
    return None


def _notes(rows: list[ImpactContribution], tradition: str) -> list[str]:
    notes: list[str] = []
    reach = sum(int(row.reach_count or 0) for row in rows)
    kinds = {row.kind for row in rows}
    if reach:
        notes.append(f"Your verified work in this path reached {reach} people.")
    if "mentoring" in kinds:
        mentored = sum(
            int(row.reach_count or 0)
            for row in rows
            if row.kind == "mentoring"
        )
        notes.append(f"You helped {mentored} learners directly.")
    if tradition == "Stewardship":
        notes.append("You returned to maintain work after the first version.")
    if tradition == "Judgment":
        notes.append("You made a decision that affected other people's risk.")
    if tradition == "Connection":
        notes.append("You brought people together around a shared activity.")
    if tradition == "Service":
        notes.append("You gave time to a community that could not repay it.")
    if tradition == "Protection":
        notes.append("You reduced risk for someone who depended on it.")
    if tradition == "Creation":
        notes.append("You built something another person could use.")
    if tradition == "Discovery":
        notes.append("You followed a question further than the instructions.")
    if tradition == "Illumination":
        notes.append("You helped someone understand something they did not before.")
    notes.append("This is an observation from verified contribution, not a label.")
    return notes[:4]


def observe(db: Session, learner: User, now: datetime | None = None) -> dict:
    """Describe the pattern in verified contribution. Never a self-assessment."""
    current = now or _now()
    rows = (
        db.query(ImpactContribution)
        .filter(
            ImpactContribution.user_id == learner.id,
            ImpactContribution.status == "verified",
        )
        .order_by(ImpactContribution.occurred_at.asc())
        .all()
    )
    if not rows:
        return {
            "status": "undetermined",
            "tradition": None,
            "alternative": None,
            "notes": [
                "The archive is still observing. It records verified contribution, not self-description."
            ],
            "observed": {"contributions": 0, "kinds": 0, "days": 0},
            "disclaimer": "Traditions are inferred; they are not selected or scored.",
        }

    counts: dict[str, int] = {}
    kinds: dict[str, set[str]] = {}
    members: dict[str, list[ImpactContribution]] = {}
    for row in rows:
        tradition = _tradition_for(row)
        if tradition is None:
            continue
        counts[tradition] = counts.get(tradition, 0) + 1
        kinds.setdefault(tradition, set()).add(str(row.kind))
        members.setdefault(tradition, []).append(row)

    dates = [row.occurred_at for row in rows if row.occurred_at]
    span_days = (current - min(dates)).days if dates else 0
    ordered = sorted(
        counts.items(),
        key=lambda item: (-item[1], -len(kinds[item[0]]), item[0]),
    )
    leader = ordered[0] if ordered else None
    runner_up = ordered[1] if len(ordered) > 1 else None

    enough = (
        leader is not None
        and leader[1] >= MIN_CONTRIBUTIONS
        and len(kinds[leader[0]]) >= MIN_DISTINCT_KINDS
    )
    recognized = (
        enough
        and leader[1] >= RECOGNIZED_CONTRIBUTIONS
        and len(kinds[leader[0]]) >= RECOGNIZED_DISTINCT_KINDS
        and span_days >= RECOGNIZED_SPAN_DAYS
    )
    tied = (
        leader is not None
        and runner_up is not None
        and leader[1] == runner_up[1]
        and len(kinds[leader[0]]) == len(kinds[runner_up[0]])
    )

    observed = {
        "contributions": len(rows),
        "kinds": len({row.kind for row in rows}),
        "days": span_days,
    }
    if not enough or tied:
        return {
            "status": "undetermined",
            "tradition": None,
            "alternative": None,
            "notes": [
                "The archive has not seen enough of a pattern yet.",
                "It records verified contribution, not what you say you enjoy.",
            ],
            "observed": observed,
            "disclaimer": "Traditions are inferred; they are not selected or scored.",
        }

    return {
        "status": "recognized" if recognized else "emerging",
        "tradition": _tradition_payload(leader[0]),
        "alternative": (
            _tradition_payload(runner_up[0]) if runner_up else None
        ),
        "notes": _notes(members[leader[0]], leader[0]),
        "observed": observed,
        "disclaimer": "Traditions are inferred; they are not selected or scored.",
    }
