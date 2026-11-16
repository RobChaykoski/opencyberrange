"""Portfolio share-link API and public token reader."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import User
from app.security.dependencies import require_permission
from app.security.permissions import PolicyDecision
from app.services import portfolio_shares, security_events
from app.services import reauth as reauth_service
from app.services.feature_flags import advanced_dna_insights_enabled

router = APIRouter()


class ShareCreate(BaseModel):
    label: Optional[str] = Field(None, max_length=120)
    audience: Optional[str] = Field(None, max_length=120)
    days: Optional[int] = Field(None, ge=1, le=365)
    single_use: bool = False
    max_uses: Optional[int] = Field(None, ge=1, le=1000)


def _consent_required(db: Session, user: User, consent_type: str) -> None:
    from app.consent import service as consent_service

    status = consent_service.blocked_status(db, user.id, consent_type)
    if status:
        raise HTTPException(
            status_code=403,
            detail=f"Consent for {consent_type} is {status}.",
            headers={"X-Consent-Status": status},
        )


@router.get("/api/profile/shares", summary="List portfolio share links")
async def list_shares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("portfolio.share")),
):
    return {
        "shares": [
            portfolio_shares.share_payload(row)
            for row in portfolio_shares.list_shares(db, current_user)
        ]
    }


@router.post("/api/profile/shares", summary="Create a portfolio share link")
async def create_share(
    payload: ShareCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("portfolio.share")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("portfolio sharing")
    ),
):
    if not advanced_dna_insights_enabled(db):
        raise HTTPException(status_code=404, detail="The portfolio is not enabled.")
    _consent_required(db, current_user, "portfolio")
    row, token = portfolio_shares.create_share(
        db,
        current_user,
        label=payload.label,
        audience=payload.audience,
        days=payload.days,
        single_use=payload.single_use,
        max_uses=payload.max_uses,
        actor=current_user,
    )
    return {
        "share": portfolio_shares.share_payload(row),
        # Returned exactly once. Only the SHA-256 hash is stored.
        "token": token,
        "url": f"/api/public/portfolio/{token}",
    }


@router.delete("/api/profile/shares/{share_id}", summary="Revoke a portfolio share link")
async def revoke_share(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("portfolio.share")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("portfolio sharing")
    ),
):
    if not portfolio_shares.revoke_share(db, current_user, share_id):
        raise HTTPException(status_code=404, detail="Share link not found.")
    return {"revoked": True, "share_id": share_id}


@router.get("/api/public/portfolio/{token}", summary="Read a shared portfolio")
async def read_shared_portfolio(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    if not advanced_dna_insights_enabled(db):
        raise HTTPException(status_code=404, detail="The portfolio is not enabled.")
    ip_address = request.client.host if request.client else None
    row = portfolio_shares.resolve_share(db, token, ip_address=ip_address)
    if row is None:
        raise HTTPException(status_code=404, detail="Share link not found or expired.")
    user = db.query(User).filter(User.id == row.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Share link not found or expired.")
    _consent_required(db, user, "portfolio")

    # Import lazily: the profile router owns the single profile-summary builder
    # so the public portfolio and the authenticated view cannot drift.
    from app.routers.profile import _build_profile_summary
    from app.services.portfolio import build_portfolio

    summary = _build_profile_summary(db, user)
    portfolio = build_portfolio(db, user, summary)
    security_events.mark_request_recorded()
    return JSONResponse(
        content={
            "portfolio": portfolio,
            "share": {
                "label": row.label,
                "audience": row.audience,
                "expires_at": row.expires_at.isoformat() if row.expires_at else None,
            },
        },
        headers={
            "Cache-Control": "no-store",
            "X-Robots-Tag": "noindex, nofollow",
        },
    )
