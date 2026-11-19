"""NICE Framework reference data and lab mapping API."""

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_admin_user, get_current_instructor_user
from app.database import get_db
from app.models import Lab, User
from app.services import nice_framework

router = APIRouter()


class NiceSelection(BaseModel):
    work_role: list[str] = Field(default_factory=list, max_length=100)
    task: list[str] = Field(default_factory=list, max_length=250)
    knowledge: list[str] = Field(default_factory=list, max_length=250)
    skill: list[str] = Field(default_factory=list, max_length=250)


class NiceRefreshRequest(BaseModel):
    source: Literal["official", "snapshot"] = "official"


@router.get("/status")
def nice_status(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_instructor_user),
):
    """Return the installed NICE Framework version and component counts."""
    return nice_framework.status(db)


@router.get("/components")
def nice_components(
    component_type: Literal["work_role", "task", "knowledge", "skill"] = "work_role",
    q: str = "",
    work_role: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_instructor_user),
):
    """Search NICE components for the authoring dropdown."""
    try:
        return nice_framework.list_components(
            db,
            component_type=component_type,
            query=q,
            work_role_code=work_role,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/labs/{lab_id}")
def get_lab_nice_mappings(
    lab_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_instructor_user),
):
    """Return the selected NICE components for one lab."""
    if db.query(Lab.id).filter(Lab.id == lab_id).first() is None:
        raise HTTPException(status_code=404, detail="Lab not found")
    return {
        "lab_id": lab_id,
        "version": nice_framework.status(db).get("version"),
        **nice_framework.lab_mappings(db, lab_id),
    }


@router.put("/labs/{lab_id}")
def set_lab_nice_mappings(
    lab_id: int,
    payload: NiceSelection,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Replace the NICE components selected for one lab."""
    if db.query(Lab.id).filter(Lab.id == lab_id).first() is None:
        raise HTTPException(status_code=404, detail="Lab not found")
    try:
        mappings = nice_framework.set_lab_mappings(
            db,
            lab_id=lab_id,
            selections=payload.model_dump(),
            created_by_id=admin.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"lab_id": lab_id, **mappings}


@router.post("/refresh")
def refresh_nice_framework(
    payload: NiceRefreshRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    """Refresh NICE components from NIST or the bundled snapshot."""
    try:
        result = nice_framework.refresh(db, source=payload.source)
    except Exception as exc:  # noqa: BLE001 - surface a useful admin error
        raise HTTPException(
            status_code=502,
            detail=f"NICE Framework refresh failed: {exc}",
        ) from exc
    return {**result, "status": nice_framework.status(db)}
