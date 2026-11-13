"""Public, unauthenticated runtime configuration.

Only values that are safe for every visitor belong here. The wiki origin is a
public URL the browser needs before login; it contains no secret.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.settings_service import get_setting_fresh

router = APIRouter()


@router.get("/config/public")
def public_config(db: Session = Depends(get_db)):
    """Return runtime values needed by the SPA before authentication."""
    wiki_origin = (get_setting_fresh(db, "wiki_origin", "") or "").strip()
    return JSONResponse(
        {"wiki_origin": wiki_origin},
        headers={"Cache-Control": "no-store"},
    )
