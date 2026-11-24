"""Learner journey catalogue and selection.

A journey is a learner-chosen direction. It is not a competency score and it is
not permanent: the learner can choose another journey, and the evidence history
stays intact.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app.models import LearnerJourney, User

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "journeys.yaml"
TRADITIONS_FILE = Path(__file__).resolve().parent.parent / "data" / "traditions.yaml"


@lru_cache(maxsize=1)
def load_catalogue() -> dict:
    with DATA_FILE.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


@lru_cache(maxsize=1)
def load_traditions() -> list[dict]:
    with TRADITIONS_FILE.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return list(payload.get("traditions") or [])


def traditions() -> list[dict]:
    return load_traditions()


def journeys() -> list[dict]:
    return list(load_catalogue().get("journeys") or [])


def get_journey(journey_id: str) -> dict | None:
    journey_id = str(journey_id or "").strip()
    for journey in journeys():
        if str(journey.get("id")) == journey_id:
            return journey
    return None


def payload(row: LearnerJourney, journey: dict | None = None) -> dict:
    definition = journey or get_journey(row.journey_id) or {}
    return {
        "id": row.id,
        "journey_id": row.journey_id,
        "is_primary": row.is_primary,
        "status": row.status,
        "chosen_at": row.chosen_at.isoformat() + "Z" if row.chosen_at else None,
        "journey": definition,
    }


def mine(db: Session, learner: User) -> LearnerJourney | None:
    return (
        db.query(LearnerJourney)
        .filter(
            LearnerJourney.user_id == learner.id,
            LearnerJourney.is_primary == True,
        )
        .first()
    )


def choose(db: Session, learner: User, journey_id: str) -> LearnerJourney:
    journey = get_journey(journey_id)
    if journey is None:
        raise ValueError(f"unknown journey: {journey_id}")
    db.query(LearnerJourney).filter(
        LearnerJourney.user_id == learner.id
    ).update({"is_primary": False}, synchronize_session=False)
    row = (
        db.query(LearnerJourney)
        .filter(
            LearnerJourney.user_id == learner.id,
            LearnerJourney.journey_id == journey["id"],
        )
        .first()
    )
    if row is None:
        row = LearnerJourney(
            institution_id=getattr(learner, "institution_id", None) or "default",
            user_id=learner.id,
            journey_id=journey["id"],
            is_primary=True,
            status="active",
        )
        db.add(row)
    else:
        row.is_primary = True
        row.status = "active"
    db.commit()
    db.refresh(row)
    return row
