"""Persistence and approval for capstone plans.

Planning is deterministic and stateless; this module adds a saved proposal, a
version, and an explicit approval. Approval requires the validation gate to pass.
Publication to a course is not implemented here.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import CapstonePlan, User
from app.services import capstone_builder
from app.services.audit import log_admin_action
from app.services.evidence import REVIEW_ROLES, _tenant_of

REQUEST_FIELDS = (
    "profile_id",
    "duration_hours",
    "max_labs",
    "waived_competencies",
    "waiver_reason",
    "assume_entry_level",
)


class PlanError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _require_reviewer(user: User) -> None:
    if user.role not in REVIEW_ROLES:
        raise PlanError(
            "capstone_forbidden",
            "Capstone planning is available to instructors and administrators.",
            403,
        )


def _request_payload(payload: dict) -> dict:
    return {key: payload.get(key) for key in REQUEST_FIELDS if key in payload}


def _default_title(plan: dict) -> str:
    capstone = plan.get("profile", {}).get("capstone") or {}
    return str(
        capstone.get("title")
        or f"{plan.get('profile', {}).get('title') or 'Capstone'} capstone"
    )[:200]


def serialize(row: CapstonePlan) -> dict:
    return {
        "id": row.id,
        "profile_id": row.profile_id,
        "title": row.title,
        "status": row.status,
        "version": row.version,
        "request": row.request,
        "plan": row.plan,
        "validation": row.validation,
        "notes": row.notes,
        "created_at": row.created_at.isoformat() + "Z" if row.created_at else None,
        "updated_at": row.updated_at.isoformat() + "Z" if row.updated_at else None,
        "approved_at": row.approved_at.isoformat() + "Z" if row.approved_at else None,
        "approved_by_id": row.approved_by_id,
    }


def _scope(query, user: User):
    if user.role == "admin":
        return query
    if user.role == "institution_admin":
        return query.filter(CapstonePlan.institution_id == _tenant_of(user))
    return query.filter(CapstonePlan.owner_id == user.id)


def _owned(db: Session, user: User, plan_id: int) -> CapstonePlan:
    row = _scope(db.query(CapstonePlan), user).filter(
        CapstonePlan.id == plan_id
    ).first()
    if row is None:
        raise PlanError("capstone_not_found", "Capstone plan not found.", 404)
    return row


def save_plan(db: Session, user: User, payload: dict) -> dict:
    _require_reviewer(user)
    plan = capstone_builder.build_plan(payload)
    row = CapstonePlan(
        institution_id=_tenant_of(user),
        owner_id=user.id,
        profile_id=str(payload.get("profile_id")),
        title=str(payload.get("title") or _default_title(plan))[:200],
        status="draft",
        version=1,
        request=_request_payload(payload),
        plan=plan,
        validation=plan["validation"],
        notes=(str(payload.get("notes") or "").strip() or None),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


def list_plans(db: Session, user: User) -> list[dict]:
    _require_reviewer(user)
    rows = (
        _scope(db.query(CapstonePlan), user)
        .order_by(CapstonePlan.updated_at.desc(), CapstonePlan.id.desc())
        .all()
    )
    return [
        {
            "id": row.id,
            "profile_id": row.profile_id,
            "title": row.title,
            "status": row.status,
            "version": row.version,
            "publishable": bool((row.validation or {}).get("publishable")),
            "updated_at": row.updated_at.isoformat() + "Z" if row.updated_at else None,
        }
        for row in rows
    ]


def get_plan(db: Session, user: User, plan_id: int) -> dict:
    _require_reviewer(user)
    return serialize(_owned(db, user, plan_id))


def update_plan(db: Session, user: User, plan_id: int, payload: dict) -> dict:
    _require_reviewer(user)
    row = _owned(db, user, plan_id)
    if row.status == "archived":
        raise PlanError(
            "capstone_status_invalid",
            "An archived plan cannot be edited.",
            409,
        )
    plan = capstone_builder.build_plan(payload)
    row.profile_id = str(payload.get("profile_id"))
    row.title = str(payload.get("title") or row.title or _default_title(plan))[:200]
    row.request = _request_payload(payload)
    row.plan = plan
    row.validation = plan["validation"]
    row.version += 1
    row.status = "draft"
    row.approved_at = None
    row.approved_by_id = None
    if payload.get("notes") is not None:
        row.notes = str(payload.get("notes") or "").strip() or None
    db.commit()
    db.refresh(row)
    return serialize(row)


def approve_plan(db: Session, user: User, plan_id: int) -> dict:
    _require_reviewer(user)
    row = _owned(db, user, plan_id)
    if row.status == "archived":
        raise PlanError(
            "capstone_status_invalid",
            "An archived plan cannot be approved.",
            409,
        )
    if row.status == "approved":
        return serialize(row)
    if not (row.validation or {}).get("publishable"):
        raise PlanError(
            "capstone_not_publishable",
            "The validation gate has not passed. Fix the gaps or record explicit waivers.",
            409,
        )
    row.status = "approved"
    row.approved_at = _now()
    row.approved_by_id = user.id
    db.commit()
    db.refresh(row)
    log_admin_action(
        action="CAPSTONE_APPROVED",
        admin_user_id=user.id,
        admin_username=user.username,
        target_type="capstone_plan",
        target_id=row.id,
        target_identifier=row.title,
        details={"profile_id": row.profile_id, "version": row.version},
    )
    return serialize(row)


def archive_plan(db: Session, user: User, plan_id: int) -> dict:
    _require_reviewer(user)
    row = _owned(db, user, plan_id)
    row.status = "archived"
    db.commit()
    db.refresh(row)
    return serialize(row)
