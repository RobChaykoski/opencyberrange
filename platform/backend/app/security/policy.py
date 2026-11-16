"""FastAPI-facing policy helpers.

The decision logic now lives in :mod:`app.services.authorization` so every
surface - route dependency, export middleware, service call - uses the same
RBAC + tenant + consent + break-glass evaluation. This module keeps the
historical import path used by existing routers and tests.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import User
from app.security.permissions import PolicyDecision
from app.services.authorization import authorize as _authorize


def authorize(
    db: Session,
    user: User,
    permission: str,
    *,
    resource_user_id: int | None = None,
    course_id: int | None = None,
    shared: bool = False,
) -> PolicyDecision:
    return _authorize(
        db,
        user,
        permission,
        resource_user_id=resource_user_id,
        course_id=course_id,
        shared=shared,
    )


def require_allowed(
    db: Session,
    user: User,
    permission: str,
    *,
    resource_user_id: int | None = None,
    course_id: int | None = None,
    shared: bool = False,
) -> PolicyDecision:
    decision = authorize(
        db,
        user,
        permission,
        resource_user_id=resource_user_id,
        course_id=course_id,
        shared=shared,
    )
    if not decision.allowed:
        from fastapi import HTTPException

        headers = {"X-Policy-Permission": permission}
        consent_status = decision.scope.get("consent_status")
        if consent_status:
            headers["X-Consent-Status"] = str(consent_status)
        if decision.source == "break_glass":
            headers["X-Break-Glass"] = "true"
        raise HTTPException(
            status_code=403,
            detail=decision.reason,
            headers=headers,
        )
    return decision
