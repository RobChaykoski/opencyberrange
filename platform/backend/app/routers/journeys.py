"""Learner journey endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api_errors import api_error
from app.auth import get_current_active_user
from app.database import get_db
from app.models import User
from app.services import journeys as journey_service

router = APIRouter()


class JourneyChoiceIn(BaseModel):
    journey_id: str = Field(..., min_length=1, max_length=64)


@router.get("")
async def list_journeys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """The journey catalogue plus the learner's current primary journey."""
    row = journey_service.mine(db, current_user)
    return {
        "journeys": journey_service.journeys(),
        "traditions": journey_service.traditions(),
        "selected": journey_service.payload(row) if row else None,
    }


@router.get("/mine")
async def my_journey(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    row = journey_service.mine(db, current_user)
    return {"journey": journey_service.payload(row) if row else None}


@router.put("/mine")
async def choose_journey(
    payload: JourneyChoiceIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        row = journey_service.choose(db, current_user, payload.journey_id)
    except ValueError as exc:
        raise api_error(400, "journey_invalid", str(exc)) from exc
    return {"journey": journey_service.payload(row)}
