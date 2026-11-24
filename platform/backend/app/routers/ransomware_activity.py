"""Aggregated ransomware activity API.

Only totals and per-group post counts are returned. Victim names, post links,
crypto addresses, and peer addresses are never stored or exposed. See ADR 0009.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api_errors import api_error
from app.auth import get_current_active_user
from app.models import User
from app.services import ransomware_activity

router = APIRouter()


@router.get("")
def get_ransomware_activity(
    _user: User = Depends(get_current_active_user),
):
    """Return the current aggregated ransomware snapshot."""

    try:
        return ransomware_activity.snapshot()
    except ransomware_activity.RansomwareActivityError as exc:
        raise api_error(exc.status_code, exc.code, exc.message) from exc
