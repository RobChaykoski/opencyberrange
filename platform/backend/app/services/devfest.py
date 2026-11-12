"""Cyber Discovery experience for an existing Competition event.

The event engine already owns participants, labs, sponsors, leaderboards, and
certificates. This service adds the discovery layer on top: the morning
investigation blocks, the Cyber DNA snapshot, the afternoon pathway readiness,
and the instructor aggregate.

Nothing here stores new personal data. It reads the learner's existing
completions and competency evidence for the event's labs.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Competition,
    CompetitionLab,
    CompetitionParticipant,
    Lab,
    LabCompletion,
    Level,
    User,
)
from app.services import settings_service
from app.services.achievements import (
    ACHIEVEMENT_DESCRIPTIONS,
    ACHIEVEMENT_LABELS,
)
from app.services.competency_assessment import build_competency_assessment_profile
from app.services.event_certificates import (
    event_award_keys_for_user,
    event_certificate_serial,
    event_ended,
)
from app.services.role_readiness import build_role_readiness
from app.services.skill_dna import build_skill_dna

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PLAN_FILE = DATA_DIR / "devfest-2027.yaml"
EXPERIENCE_KEY = "devfest-2027"
DEFAULT_MIN_COHORT = 5

_plan_cache: dict | None = None


def load_plan() -> dict:
    global _plan_cache
    if _plan_cache is None:
        with PLAN_FILE.open("r", encoding="utf-8") as handle:
            _plan_cache = yaml.safe_load(handle) or {}
    return _plan_cache


def plan_for_experience(experience_key: str | None) -> dict | None:
    if experience_key != EXPERIENCE_KEY:
        return None
    return load_plan()


def _minimum_cohort_size(db: Session) -> int:
    raw = settings_service.get_setting_fresh(
        db, "analytics_min_cohort_size", str(DEFAULT_MIN_COHORT)
    )
    try:
        value = int(raw)
    except (TypeError, ValueError):
        value = DEFAULT_MIN_COHORT
    return max(0, min(value, 1000))


def _event_labs(db: Session, competition_id: int) -> dict[str, Lab]:
    rows = (
        db.query(CompetitionLab)
        .options(joinedload(CompetitionLab.lab).joinedload(Lab.level).joinedload(Level.track))
        .filter(CompetitionLab.competition_id == competition_id)
        .all()
    )
    return {
        row.lab.slug: row.lab
        for row in rows
        if row.lab and row.lab.is_active and row.lab.slug
    }


def _completed_slugs(db: Session, user_id: int, lab_ids: set[int]) -> set[str]:
    if not lab_ids:
        return set()
    rows = (
        db.query(Lab.slug)
        .join(LabCompletion, LabCompletion.lab_id == Lab.id)
        .filter(
            LabCompletion.user_id == user_id,
            LabCompletion.lab_id.in_(lab_ids),
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        )
        .distinct()
        .all()
    )
    return {row[0] for row in rows}


def _lab_payload(lab: Lab, completed: bool) -> dict:
    level = getattr(lab, "level", None)
    track = getattr(level, "track", None) if level else None
    return {
        "id": getattr(lab, "id", None),
        "slug": getattr(lab, "slug", None),
        "name": getattr(lab, "name", ""),
        "track_slug": getattr(track, "slug", None),
        "completed": completed,
    }


def _block_progress(
    block: dict,
    event_labs: dict[str, Lab],
    completed: set[str],
) -> dict:
    slugs = [slug for slug in block.get("lab_slugs", []) if slug in event_labs]
    done = [slug for slug in slugs if slug in completed]
    return {
        "id": block["id"],
        "title": block["title"],
        "scenario": block.get("scenario"),
        "inspiration": block.get("inspiration"),
        "competencies": block.get("competencies", []),
        "measures": block.get("measures", []),
        "career_paths": block.get("career_paths", []),
        "labs": [
            _lab_payload(event_labs[slug], slug in completed)
            for slug in slugs
        ],
        "completed": bool(done),
        "completed_labs": len(done),
        "total_labs": len(slugs),
    }


def _dna_snapshot(db: Session, user: User) -> dict:
    dna = build_skill_dna(db, user)
    return {
        "overall": dna.get("overall"),
        "tier": dna.get("tier"),
        "class": dna.get("class"),
        "dimensions": dna.get("dimensions", []),
        "affinities": dna.get("affinities", []),
    }


def learner_discovery(
    db: Session,
    user: User,
    competition: Competition,
    plan: dict,
    *,
    joined: bool,
) -> dict:
    event_labs = _event_labs(db, competition.id)
    lab_ids = {lab.id for lab in event_labs.values()}
    completed = _completed_slugs(db, user.id, lab_ids)
    assessment = build_competency_assessment_profile(db, user)

    morning = []
    for session in plan.get("sessions", []):
        if session.get("id") != "morning":
            continue
        for block in session.get("exercises", []):
            morning.append(_block_progress(block, event_labs, completed))

    completed_blocks = sum(1 for block in morning if block["completed"])
    afternoon = []
    for session in plan.get("sessions", []):
        if session.get("id") != "afternoon":
            continue
        for pathway in session.get("pathways", []):
            readiness = build_role_readiness(
                db,
                user,
                pathway["id"],
                assessment=assessment,
            )
            pathway_slugs = [
                slug for slug in pathway.get("lab_slugs", []) if slug in event_labs
            ]
            pathway_done = [
                slug for slug in pathway_slugs if slug in completed
            ]
            afternoon.append(
                {
                    "id": pathway["id"],
                    "title": pathway["title"],
                    "scenario": pathway.get("scenario"),
                    "activities": pathway.get("activities", []),
                    "competencies": pathway.get("competencies", []),
                    "readiness_score": readiness["readiness"]["score"],
                    "rating": readiness["readiness"]["rating"],
                    "next_workbooks": readiness.get("next_workbooks", [])[:2],
                    "certifications": readiness.get("certifications", {}),
                    "labs": [
                        _lab_payload(event_labs[slug], slug in completed)
                        for slug in pathway_slugs
                    ],
                    "completed_labs": len(pathway_done),
                    "total_labs": len(pathway_slugs),
                }
            )

    keys = event_award_keys_for_user(
        db, user.id, competition.id, competition.experience_key
    )
    ended = event_ended(competition)
    certificate = {
        "joined": joined,
        "event_ended": ended,
        "available": joined and ended and "discovery" in keys,
        "award": "discovery",
        "serial": event_certificate_serial(competition.id, user.id, "discovery"),
        "url": f"/certificate/event/{competition.id}/discovery",
        "label": "Cyber Discovery Experience Certificate",
    }

    next_block = next((block for block in morning if not block["completed"]), None)
    if next_block and next_block["labs"]:
        next_action = {
            "label": f"Open {next_block['labs'][0]['name']}",
            "lab": next_block["labs"][0],
            "kind": "exercise",
        }
    elif certificate["available"]:
        next_action = {
            "label": "Open your Cyber Discovery certificate",
            "url": certificate["url"],
            "kind": "certificate",
        }
    else:
        next_action = {
            "label": "Join the event to unlock the certificate",
            "kind": "join",
        }

    return {
        "experience_key": competition.experience_key,
        "event": {
            "id": competition.id,
            "name": competition.name,
            "description": competition.description,
            "start_at": competition.start_at.isoformat() if competition.start_at else None,
            "end_at": competition.end_at.isoformat() if competition.end_at else None,
            "ended": ended,
        },
        "plan": {
            "tagline": plan.get("event", {}).get("tagline"),
            "promise": plan.get("event", {}).get("promise", []),
            "audience": plan.get("event", {}).get("audience", []),
            "career_stories": plan.get("career_stories", {}),
        },
        "progress": {
            "completed_blocks": completed_blocks,
            "total_blocks": len(morning),
            "morning": morning,
        },
        "dna": _dna_snapshot(db, user),
        "pathways": afternoon,
        "certificate": certificate,
        "next_action": next_action,
        "disclaimer": (
            "The Cyber DNA snapshot and Cyber GPS are descriptive practice "
            "signals. They are not a grade, a ranking, or a prediction of "
            "employment. The event certificate records participation in this "
            "event, not a certification."
        ),
    }


def instructor_overview(
    db: Session,
    competition: Competition,
    plan: dict,
) -> dict:
    minimum = _minimum_cohort_size(db)
    participants = (
        db.query(CompetitionParticipant)
        .options(joinedload(CompetitionParticipant.user))
        .filter(CompetitionParticipant.competition_id == competition.id)
        .all()
    )
    participants = [
        row
        for row in participants
        if row.user and row.user.is_active and row.user.is_approved
    ]
    participant_count = len(participants)
    if participant_count < max(1, minimum):
        return {
            "state": "suppressed",
            "participants": participant_count,
            "minimum_cohort_size": minimum,
            "reason": (
                "Event aggregates are hidden until the participant count reaches "
                f"{minimum}."
            ),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    user_ids = [row.user_id for row in participants]
    event_labs = _event_labs(db, competition.id)
    lab_ids = {lab.id for lab in event_labs.values()}
    completions = (
        db.query(LabCompletion)
        .filter(
            LabCompletion.user_id.in_(user_ids),
            LabCompletion.lab_id.in_(lab_ids),
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        )
        .all()
    )
    completed_by_user: dict[int, set[str]] = {}
    lab_slug_by_id = {lab.id: slug for slug, lab in event_labs.items()}
    for row in completions:
        slug = lab_slug_by_id.get(row.lab_id)
        if slug:
            completed_by_user.setdefault(row.user_id, set()).add(slug)

    def count_block(block: dict) -> dict:
        slugs = set(block.get("lab_slugs", []))
        count = sum(
            1 for slugs_done in completed_by_user.values() if slugs & slugs_done
        )
        return {
            "id": block["id"],
            "title": block["title"],
            "participants": count,
            "rate": round(count / participant_count * 100, 1),
        }

    morning = []
    afternoon = []
    for session in plan.get("sessions", []):
        if session.get("id") == "morning":
            morning = [count_block(block) for block in session.get("exercises", [])]
        elif session.get("id") == "afternoon":
            afternoon = [
                count_block(pathway) for pathway in session.get("pathways", [])
            ]

    return {
        "state": "available",
        "participants": participant_count,
        "minimum_cohort_size": minimum,
        "morning": morning,
        "pathways": afternoon,
        "certificates_available": participant_count if event_ended(competition) else 0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "Aggregate event participation only. Small cohorts are suppressed. "
            "This is not an evaluation of teaching or learners."
        ),
    }


def plan_summary(plan: dict) -> dict:
    return {
        "event": plan.get("event", {}),
        "career_stories": plan.get("career_stories", {}),
        "top_concepts": plan.get("top_concepts", []),
        "outputs": plan.get("outputs", {}),
        "privacy": plan.get("privacy", []),
        "achievement": {
            "type": "devfest_2027_discovery",
            "label": ACHIEVEMENT_LABELS.get("devfest_2027_discovery"),
            "description": ACHIEVEMENT_DESCRIPTIONS.get("devfest_2027_discovery"),
        },
    }
