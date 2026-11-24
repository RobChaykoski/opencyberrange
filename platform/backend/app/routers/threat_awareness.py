"""Threat-awareness snapshot API.

The response is aggregated: country and category counts only. No individual
address, hostname, or simulated attack path is ever returned. See ADR 0008.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api_errors import api_error
from app.auth import get_current_active_user
from app.models import User
from app.services import threat_awareness

router = APIRouter()


@router.get("")
def get_threat_awareness(
    _user: User = Depends(get_current_active_user),
):
    """Return the current aggregated snapshot with derived shares."""

    try:
        return threat_awareness.snapshot()
    except threat_awareness.ThreatAwarenessError as exc:
        raise api_error(exc.status_code, exc.code, exc.message) from exc
