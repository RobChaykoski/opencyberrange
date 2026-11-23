"""Public QR landing for conference and campaign links.

A scan is recorded before the browser is redirected to registration, so the
dashboard can report scan-to-registration conversion even when the visitor does
not finish signing up.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.ratelimit import create_limiter
from app.services import attribution

router = APIRouter()
limiter = create_limiter()


@router.get("/qr/{source}")
@limiter.limit("120/minute")
def qr_landing(
    source: str,
    request: Request,
    campaign: str | None = None,
    db: Session = Depends(get_db),
):
    normalized_source = attribution.normalize_source(source)
    normalized_campaign = attribution.normalize_campaign(campaign)
    attribution.record_qr_scan(
        db,
        source=normalized_source,
        campaign=normalized_campaign,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        path=request.url.path,
    )
    response = RedirectResponse(
        attribution.registration_path(normalized_source, normalized_campaign),
        status_code=302,
    )
    response.headers["Cache-Control"] = "no-store"
    return response
