"""Learner workbook answer capture.

The workbook is a static site. This API stores the learner's current answer and
snapshots each distinct version into the evidence ledger for instructor review.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.api_errors import api_error
from app.auth import get_current_active_user
from app.database import get_db
from app.models import Lab, Level, User
from app.routers.curriculum import (
    _is_lab_visible,
    get_accessible_exclusive_lab_ids,
)
from app.services import workbook_answers as workbook_answer_service
from app.services.evidence import record_payload

router = APIRouter()


class WorkbookAnswerIn(BaseModel):
    answer: str = Field(..., min_length=10, max_length=20000)
    prompt_key: str = Field(
        "reflection",
        min_length=1,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )


def _visible_lab(db: Session, user: User, lab_slug: str) -> Lab:
    lab = (
        db.query(Lab)
        .options(joinedload(Lab.level).joinedload(Level.track))
        .filter(Lab.slug == lab_slug, Lab.is_active == True)
        .first()
    )
    if lab is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    accessible = get_accessible_exclusive_lab_ids(db, user.id)
    if not _is_lab_visible(lab, user, accessible):
        raise HTTPException(status_code=403, detail="Exercise is not available")
    return lab


@router.get("/options")
async def answer_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Visible exercises that have a workbook page, for the answer selector."""
    accessible = get_accessible_exclusive_lab_ids(db, current_user.id)
    labs = (
        db.query(Lab)
        .options(joinedload(Lab.level).joinedload(Level.track))
        .filter(
            Lab.is_active == True,
            Lab.workbook.isnot(None),
            Lab.workbook != "",
        )
        .order_by(Lab.name)
        .all()
    )
    options = []
    for lab in labs:
        if not _is_lab_visible(lab, current_user, accessible):
            continue
        level = getattr(lab, "level", None)
        track = getattr(level, "track", None) if level else None
        options.append(
            {
                "id": lab.id,
                "slug": lab.slug,
                "name": lab.name,
                "track": track.name if track else None,
                "track_slug": track.slug if track else None,
                "workbook": lab.workbook,
            }
        )
    return {"exercises": options}


@router.get("")
async def list_my_answers(
    lab_id: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = workbook_answer_service.list_answers(db, current_user, lab_id=lab_id)
    return {"answers": [workbook_answer_service.answer_payload(row) for row in rows]}


@router.get("/{lab_slug}")
async def get_my_answer(
    lab_slug: str,
    prompt_key: str = Query("reflection", min_length=1, max_length=64),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lab = _visible_lab(db, current_user, lab_slug)
    row = workbook_answer_service.get_answer(db, current_user, lab.id, prompt_key)
    return {
        "lab": {"id": lab.id, "slug": lab.slug, "name": lab.name},
        "answer": workbook_answer_service.answer_payload(row) if row else None,
    }


@router.put("/{lab_slug}")
async def save_my_answer(
    lab_slug: str,
    payload: WorkbookAnswerIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lab = _visible_lab(db, current_user, lab_slug)
    try:
        result = workbook_answer_service.save_answer(
            db,
            current_user,
            lab,
            prompt_key=payload.prompt_key,
            answer_text=payload.answer,
        )
    except ValueError as exc:
        raise api_error(400, "workbook_answer_invalid", str(exc)) from exc
    evidence = result["evidence"]
    return {
        "answer": workbook_answer_service.answer_payload(result["answer"]),
        "created": result["created"],
        "evidence": record_payload(evidence) if evidence is not None else None,
    }
