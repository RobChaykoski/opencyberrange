"""Capstone planning endpoints.

The planner returns a proposal. It does not publish a capstone, grade a learner,
or bypass instructor review.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api_errors import api_error
from app.auth import get_current_active_user
from app.models import User
from app.services import capstone_builder
from app.services.evidence import REVIEW_ROLES

router = APIRouter()


class PlanIn(BaseModel):
    profile_id: str = Field(..., min_length=1, max_length=64)
    duration_hours: float = Field(default=40, ge=4, le=200)
    max_labs: int = Field(default=10, ge=1, le=20)
    waived_competencies: list[str] = Field(default_factory=list)
    waiver_reason: str | None = Field(default=None, max_length=2000)
    assume_entry_level: bool = True


def _require_reviewer(user: User) -> None:
    if user.role not in REVIEW_ROLES:
        raise api_error(
            403,
            "capstone_forbidden",
            "Capstone planning is available to instructors and administrators.",
        )


@router.get("/profiles")
async def capstone_profiles(
    current_user: User = Depends(get_current_active_user),
):
    _require_reviewer(current_user)
    return {"profiles": capstone_builder.profiles()}


@router.post("/plan")
async def capstone_plan(
    payload: PlanIn,
    current_user: User = Depends(get_current_active_user),
):
    _require_reviewer(current_user)
    try:
        return capstone_builder.build_plan(payload.model_dump())
    except capstone_builder.CapstoneError as exc:
        raise api_error(exc.status_code, exc.code, exc.message) from exc
