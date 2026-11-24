"""Certification practice endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api_errors import api_error
from app.auth import get_current_active_user
from app.database import get_db
from app.models import User
from app.services import practice as practice_service

router = APIRouter()


class SessionIn(BaseModel):
    pathway_id: str = Field(..., min_length=1, max_length=64)
    mode: str = "mock"
    domain_id: str | None = Field(default=None, max_length=32)
    question_count: int | None = Field(default=None, ge=1, le=40)
    duration_minutes: int | None = Field(default=None, ge=5, le=240)
    pass_mark: int | None = Field(default=None, ge=1, le=100)


class AnswerIn(BaseModel):
    position: int = Field(..., ge=1)
    selected_index: int = Field(..., ge=0)


class SubmitIn(BaseModel):
    answers: list[AnswerIn] = Field(default_factory=list)


def _raise(exc: practice_service.PracticeError):
    raise api_error(exc.status_code, exc.code, exc.message) from exc


@router.get("/pathways")
async def practice_pathways(
    current_user: User = Depends(get_current_active_user),
):
    return practice_service.pathways_payload()


@router.post("/sessions", status_code=201)
async def start_session(
    payload: SessionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return practice_service.create_session(
            db, current_user, payload.model_dump()
        )
    except practice_service.PracticeError as exc:
        _raise(exc)


@router.get("/sessions")
async def practice_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return practice_service.history(db, current_user, limit)


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        payload = practice_service.session_payload(db, current_user, session_id)
    except practice_service.PracticeError as exc:
        _raise(exc)
    response.headers["Cache-Control"] = "no-store"
    return payload


@router.post("/sessions/{session_id}/submit")
async def submit_session(
    session_id: int,
    payload: SubmitIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return practice_service.submit_session(
            db,
            current_user,
            session_id,
            [answer.model_dump() for answer in payload.answers],
        )
    except practice_service.PracticeError as exc:
        _raise(exc)


@router.get("/progress")
async def practice_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return practice_service.progress(db, current_user)
