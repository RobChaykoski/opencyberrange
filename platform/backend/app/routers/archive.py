"""The Living Archive endpoint.

The archive describes an observed tradition. It is not a self-assessment and it
never returns a percentage, a ranking, or a public label.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import User
from app.services import archive as archive_service

router = APIRouter()


@router.get("/me")
async def my_archive(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    response.headers["Cache-Control"] = "no-store"
    return archive_service.observe(db, current_user)
