"""Administrator API for security events, RBAC review, and break-glass.

Every route uses the Authorization Service through ``require_permission``. The
endpoints are intentionally read/administrative only: there is no update or
delete endpoint for security events, and private permissions cannot be granted
through the RBAC editor.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import BreakGlassGrant, NetworkAccessRule, RbacRole, User
from app.security.dependencies import require_permission
from app.security.permissions import PolicyDecision
from app.services import (
    authorization,
    network_access,
    rbac,
    security_events,
    service_identities,
)
from app.services import reauth as reauth_service
from app.services.audit import AuditActions, log_admin_action

router = APIRouter()


class RolePermissionsUpdate(BaseModel):
    permissions: list[str] = Field(default_factory=list)
    reason: Optional[str] = Field(None, min_length=5, max_length=500)


class UserRoleGrant(BaseModel):
    role_key: str
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None


class AuthorizationCheck(BaseModel):
    user_id: int
    permission: str
    resource_user_id: Optional[int] = None
    course_id: Optional[int] = None
    shared: bool = False


class BreakGlassRequest(BaseModel):
    permission: str
    reason: str
    minutes: int = Field(60, ge=1, le=1440)
    reference: Optional[str] = None
    user_id: Optional[int] = None
    course_id: Optional[int] = None


class BreakGlassRevoke(BaseModel):
    reason: Optional[str] = None


class BreakGlassReview(BaseModel):
    note: str


class ServiceIdentityCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    scopes: list[str] = Field(default_factory=list)
    days: int = Field(90, ge=1, le=365)
    institution_id: Optional[str] = Field(None, max_length=64)


class AccessRuleCreate(BaseModel):
    scope: str = Field(..., max_length=16)
    kind: str = Field(..., max_length=16)
    value: str = Field(..., min_length=1, max_length=255)
    action: str = Field(..., max_length=8)
    note: Optional[str] = Field(None, max_length=255)
    expires_at: Optional[datetime] = None


class AccessRuleTest(BaseModel):
    scope: str = Field(..., max_length=16)
    ip_address: Optional[str] = Field(None, max_length=64)
    email: Optional[str] = Field(None, max_length=320)


def _event_payload(row) -> dict:
    return {
        "id": row.id,
        "occurred_at": row.occurred_at.isoformat() if row.occurred_at else None,
        "category": row.category,
        "event_type": row.event_type,
        "severity": row.severity,
        "outcome": row.outcome,
        "action": row.action,
        "actor_id": row.actor_id,
        "actor_username": row.actor_username,
        "actor_role": row.actor_role,
        "institution_id": row.institution_id,
        "target_type": row.target_type,
        "target_id": row.target_id,
        "target_label": row.target_label,
        "resource": row.resource,
        "method": row.method,
        "path": row.path,
        "status_code": row.status_code,
        "ip_address": row.ip_address,
        "user_agent": row.user_agent,
        "request_id": row.request_id,
        "detail": row.detail,
    }


def _grant_payload(db: Session, row: BreakGlassGrant) -> dict:
    user = db.query(User).filter(User.id == row.user_id).first()
    return {
        "id": row.id,
        "user_id": row.user_id,
        "username": getattr(user, "username", None),
        "permission": row.permission,
        "scope_user_id": row.scope_user_id,
        "scope_course_id": row.scope_course_id,
        "reason": row.reason,
        "reference": row.reference,
        "status": row.status,
        "requested_by_id": row.requested_by_id,
        "approved_by_id": row.approved_by_id,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "approved_at": row.approved_at.isoformat() if row.approved_at else None,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        "revoked_at": row.revoked_at.isoformat() if row.revoked_at else None,
        "last_used_at": row.last_used_at.isoformat() if row.last_used_at else None,
        "use_count": row.use_count,
        "review_status": row.review_status,
        "reviewed_at": row.reviewed_at.isoformat() if row.reviewed_at else None,
        "review_note": row.review_note,
    }


def _access_rule_payload(row: NetworkAccessRule) -> dict:
    return {
        "id": row.id,
        "scope": row.scope,
        "kind": row.kind,
        "value": row.value,
        "action": row.action,
        "note": row.note,
        "created_by_id": row.created_by_id,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
    }


@router.get("/events", summary="Query security, audit, and privacy events")
async def list_events(
    category: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    outcome: Optional[str] = Query(None),
    actor_id: Optional[int] = Query(None),
    institution_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    until: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    viewer: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("security.events.view")),
):
    if category and category not in security_events.CATEGORIES:
        raise HTTPException(status_code=422, detail="Unknown event category.")
    if severity and severity not in security_events.SEVERITIES:
        raise HTTPException(status_code=422, detail="Unknown severity.")
    rows = security_events.query_events(
        db,
        viewer=viewer,
        category=category,
        event_type=event_type,
        severity=severity,
        outcome=outcome,
        actor_id=actor_id,
        institution_id=institution_id,
        search=search,
        since=since,
        until=until,
        limit=limit,
        offset=offset,
    )
    security_events.record(
        "security.events_read",
        actor=viewer,
        detail={"count": len(rows), "category": category, "event_type": event_type},
    )
    security_events.mark_request_recorded()
    return {"events": [_event_payload(row) for row in rows], "limit": limit, "offset": offset}


@router.get("/events/summary", summary="Security event counts and top event types")
async def event_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    viewer: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("security.events.view")),
):
    return security_events.summary(db, viewer=viewer, days=days)


@router.get("/events/{event_id}", summary="One security event")
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    viewer: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("security.events.view")),
):
    security_events.set_rls_context(
        db,
        institution_id=getattr(viewer, "institution_id", None),
        system_admin=(getattr(viewer, "role", "") or "") == "admin",
    )
    from app.models import SecurityEvent

    row = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    return _event_payload(row)


# --- RBAC review and administration ---------------------------------------


def _ensure_seeded(db: Session) -> None:
    if db.query(RbacRole).count() == 0:
        rbac.seed(db)


@router.get("/rbac/roles", summary="Roles, grants, and effective permission counts")
async def list_roles(
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(require_permission("security.events.view")),
):
    _ensure_seeded(db)
    return {"roles": rbac.role_catalog(db)}


@router.get("/rbac/permissions", summary="Reviewed permission catalog")
async def list_permissions(
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(require_permission("security.events.view")),
):
    _ensure_seeded(db)
    return {"permissions": rbac.permission_catalog(db)}


@router.get("/rbac/matrix", summary="Role and policy access matrix")
async def rbac_matrix(
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(require_permission("security.events.view")),
):
    """Return the effective role grants and the PBAC attributes together.

    This is a read-only review surface: it never returns learner data, secrets,
    or request-scoped decisions. Role grants come from the RBAC tables so an
    administrator's reviewed edits are what the matrix shows.
    """
    _ensure_seeded(db)
    from app.services import access_matrix

    return access_matrix.build_matrix(db)


@router.put(
    "/rbac/roles/{role_key}/permissions",
    summary="Replace one role's permission grants",
)
async def update_role_permissions(
    role_key: str,
    payload: RolePermissionsUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("rbac.manage")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("role permission change")
    ),
):
    _ensure_seeded(db)
    try:
        result = rbac.set_role_permissions(
            db, actor, role_key, payload.permissions, reason=payload.reason
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result


@router.get("/rbac/users/{user_id}", summary="Effective roles and permissions")
async def user_authorization(
    user_id: int,
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(require_permission("security.events.view")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    service = authorization.AuthorizationService(db, user)
    return {
        "user_id": user.id,
        "username": user.username,
        "institution_id": getattr(user, "institution_id", None),
        "roles": service.roles(),
        "permissions": sorted(service.permissions()),
    }


@router.post("/rbac/users/{user_id}/roles", summary="Grant an expiring extra role")
async def grant_user_role(
    user_id: int,
    payload: UserRoleGrant,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("rbac.manage")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("role assignment")
    ),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    expires_at = payload.expires_at
    if expires_at is not None and expires_at.tzinfo is not None:
        expires_at = expires_at.astimezone(timezone.utc).replace(tzinfo=None)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if expires_at is not None and expires_at <= now:
        raise HTTPException(status_code=422, detail="expires_at must be in the future.")
    try:
        row = rbac.grant_user_role(
            db,
            actor,
            user,
            payload.role_key,
            reason=payload.reason,
            expires_at=expires_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "user_id": user.id,
        "role_key": row.role_key,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
    }


@router.delete(
    "/rbac/users/{user_id}/roles/{role_key}",
    summary="Revoke an extra role",
)
async def revoke_user_role(
    user_id: int,
    role_key: str,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("rbac.manage")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("role assignment")
    ),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if not rbac.revoke_user_role(db, actor, user, role_key):
        raise HTTPException(status_code=404, detail="Role grant not found.")
    return {"revoked": True, "user_id": user.id, "role_key": role_key}


@router.post("/rbac/check", summary="Explain one authorization decision")
async def check_authorization(
    payload: AuthorizationCheck,
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(require_permission("security.events.view")),
):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return authorization.explain(
        db,
        user,
        payload.permission,
        resource_user_id=payload.resource_user_id,
        course_id=payload.course_id,
        shared=payload.shared,
    )


# --- Service identities ----------------------------------------------------


@router.get("/service-identities", summary="List non-human service credentials")
async def list_service_identities(
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("service.identity.manage")),
):
    institution = None if actor.role == "admin" else actor.institution_id
    return {"credentials": service_identities.list_credentials(db, institution_id=institution)}


@router.post("/service-identities", summary="Create a scoped service credential")
async def create_service_identity(
    payload: ServiceIdentityCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("service.identity.manage")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("service identity creation")
    ),
):
    institution = payload.institution_id or actor.institution_id
    if actor.role != "admin":
        institution = actor.institution_id
    row, token = service_identities.create_credential(
        db,
        actor,
        name=payload.name,
        scopes=payload.scopes,
        days=payload.days,
        institution_id=institution,
    )
    credentials = service_identities.list_credentials(db, institution_id=institution)
    credential = next((item for item in credentials if item["id"] == row.id), None)
    return {
        "credential": credential,
        # Returned exactly once. Only the SHA-256 hash is stored.
        "token": token,
    }


@router.delete(
    "/service-identities/{credential_id}",
    summary="Revoke a service credential",
)
async def revoke_service_identity(
    credential_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("service.identity.manage")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("service identity revocation")
    ),
):
    if not service_identities.revoke_credential(db, actor, credential_id):
        raise HTTPException(status_code=404, detail="Service credential not found.")
    return {"revoked": True, "credential_id": credential_id}


# --- Network and registration access rules ---------------------------------


@router.get(
    "/access-rules",
    summary="List sign-in and registration allow/deny rules",
)
async def list_access_rules(
    scope: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(require_permission("rbac.manage")),
):
    query = db.query(NetworkAccessRule)
    if scope:
        try:
            scope = network_access.normalize_scope(scope)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        query = query.filter(NetworkAccessRule.scope == scope)
    rows = (
        query.order_by(
            NetworkAccessRule.scope,
            NetworkAccessRule.action,
            NetworkAccessRule.kind,
            NetworkAccessRule.value,
        )
        .limit(1000)
        .all()
    )
    return {
        "rules": [_access_rule_payload(row) for row in rows],
        "scopes": list(network_access.SCOPES),
        "kinds": list(network_access.KINDS),
        "actions": list(network_access.ACTIONS),
    }


@router.post(
    "/access-rules",
    status_code=201,
    summary="Add a sign-in or registration allow/deny rule",
)
async def create_access_rule(
    payload: AccessRuleCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("rbac.manage")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("network access rule change")
    ),
):
    try:
        scope = network_access.normalize_scope(payload.scope)
        kind = network_access.normalize_kind(payload.kind)
        action = network_access.normalize_action(payload.action)
        value = network_access.normalize_value(kind, payload.value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    expires_at = payload.expires_at
    if expires_at is not None:
        if expires_at.tzinfo is not None:
            expires_at = expires_at.astimezone(timezone.utc).replace(tzinfo=None)
        if expires_at <= datetime.now(timezone.utc).replace(tzinfo=None):
            raise HTTPException(
                status_code=422, detail="expires_at must be in the future."
            )

    duplicate = (
        db.query(NetworkAccessRule)
        .filter(
            NetworkAccessRule.scope == scope,
            NetworkAccessRule.kind == kind,
            NetworkAccessRule.value == value,
            NetworkAccessRule.action == action,
        )
        .first()
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=409,
            detail="An identical rule already exists for this scope.",
        )

    row = NetworkAccessRule(
        scope=scope,
        kind=kind,
        value=value,
        action=action,
        note=(payload.note or "").strip()[:255] or None,
        created_by_id=actor.id,
        expires_at=expires_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    log_admin_action(
        action=AuditActions.ACCESS_RULE_CREATED,
        admin_user_id=actor.id,
        admin_username=actor.username,
        target_type="network_access_rule",
        target_id=row.id,
        target_identifier=f"{scope}:{action}:{value}",
        details={
            "scope": scope,
            "kind": kind,
            "value": value,
            "action": action,
            "note": row.note,
            "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        },
        ip_address=request.client.host if request.client else None,
    )
    return _access_rule_payload(row)


@router.delete(
    "/access-rules/{rule_id}",
    summary="Remove a sign-in or registration allow/deny rule",
)
async def delete_access_rule(
    rule_id: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("rbac.manage")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("network access rule change")
    ),
):
    row = db.query(NetworkAccessRule).filter(NetworkAccessRule.id == rule_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Access rule not found.")
    details = {
        "scope": row.scope,
        "kind": row.kind,
        "value": row.value,
        "action": row.action,
    }
    identifier = f"{row.scope}:{row.action}:{row.value}"
    db.delete(row)
    db.commit()
    log_admin_action(
        action=AuditActions.ACCESS_RULE_DELETED,
        admin_user_id=actor.id,
        admin_username=actor.username,
        target_type="network_access_rule",
        target_id=rule_id,
        target_identifier=identifier,
        details=details,
        ip_address=request.client.host if request.client else None,
    )
    return {"deleted": True, "rule_id": rule_id}


@router.post(
    "/access-rules/test",
    summary="Explain how the current rules evaluate one request",
)
async def test_access_rule(
    payload: AccessRuleTest,
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(require_permission("rbac.manage")),
):
    try:
        scope = network_access.normalize_scope(payload.scope)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    decision = network_access.check(
        db,
        scope,
        ip_address=payload.ip_address,
        email=payload.email,
    )
    return {
        "scope": scope,
        "allowed": decision.allowed,
        "reason": decision.reason or "allowed",
        "rule_id": decision.rule_id,
        "rule_value": decision.rule_value,
    }


# --- Break-glass -----------------------------------------------------------


@router.get("/break-glass", summary="Break-glass grants and review state")
async def list_break_glass(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(require_permission("security.events.view")),
):
    authorization.expire_stale_grants(db)
    query = db.query(BreakGlassGrant)
    if status:
        query = query.filter(BreakGlassGrant.status == status)
    rows = query.order_by(BreakGlassGrant.id.desc()).limit(200).all()
    return {"grants": [_grant_payload(db, row) for row in rows]}


@router.post("/break-glass", summary="Request time-bound emergency access")
async def request_break_glass(
    payload: BreakGlassRequest,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("break_glass.request")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("break-glass request")
    ),
):
    target = None
    if payload.user_id is not None:
        target = db.query(User).filter(User.id == payload.user_id).first()
        if target is None:
            raise HTTPException(status_code=404, detail="Target user not found.")
    row = authorization.create_break_glass(
        db,
        actor,
        permission=payload.permission,
        reason=payload.reason,
        minutes=payload.minutes,
        reference=payload.reference,
        scope_user_id=payload.user_id,
        scope_course_id=payload.course_id,
        target_user=target,
    )
    return _grant_payload(db, row)


@router.post("/break-glass/{grant_id}/approve", summary="Approve a pending grant")
async def approve_break_glass(
    grant_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("break_glass.approve")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("break-glass approval")
    ),
):
    row = authorization.approve_break_glass(db, actor, grant_id)
    return _grant_payload(db, row)


@router.post("/break-glass/{grant_id}/revoke", summary="Revoke a grant")
async def revoke_break_glass(
    grant_id: int,
    payload: BreakGlassRevoke | None = None,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("break_glass.revoke")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("break-glass revocation")
    ),
):
    row = authorization.revoke_break_glass(
        db, actor, grant_id, reason=(payload.reason if payload else None)
    )
    return _grant_payload(db, row)


@router.post("/break-glass/{grant_id}/review", summary="Close the post-use review")
async def review_break_glass(
    grant_id: int,
    payload: BreakGlassReview,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("break_glass.approve")),
    _reauth: object = Depends(
        reauth_service.require_recent_reauth("break-glass review")
    ),
):
    row = authorization.review_break_glass(db, actor, grant_id, note=payload.note)
    return _grant_payload(db, row)
