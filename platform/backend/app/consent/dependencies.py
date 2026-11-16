"""FastAPI dependencies for consent-gated surfaces."""

from __future__ import annotations

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.consent import service
from app.database import get_db
from app.models import User


def consent_detail(consent_type: str, status: str) -> str:
    if status == "revocation_in_progress":
        return (
            f"{consent_type.replace('_', ' ').title()} data is being removed after "
            "consent was revoked. This surface is temporarily unavailable."
        )
    return (
        f"{consent_type.replace('_', ' ').title()} consent is not granted. "
        "Re-enable it from Privacy and consent to use this surface."
    )


def require_consent(consent_type: str):
    """Return a dependency that blocks a revoked or purging feature."""

    def dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> bool:
        status = service.blocked_status(db, current_user.id, consent_type)
        if status:
            raise HTTPException(
                status_code=403,
                detail=consent_detail(consent_type, status),
                headers={"X-Consent-Status": status},
            )
        return True

    return dependency
