"""Centralized Authorization Service.

Every new or high-risk surface calls this service instead of comparing role
strings. The decision joins four inputs:

1. **RBAC** - the server-resolved role and its permissions from the RBAC tables.
2. **Resource scope** - owner, course, explicit share, and tenant boundary.
3. **Consent** - a revoked learner consent blocks derived-data access even for
   an administrator.
4. **Break-glass** - a time-bound, reasoned emergency grant for one permission,
   never a role change and never a consent override.

Denials and break-glass use are written to the append-only security event store.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import BreakGlassGrant, Course, User
from app.security.permissions import (
    BREAK_GLASS_PERMISSIONS,
    PERMISSION_CATALOG,
    PERMISSION_META,
    READ_ONLY_PERMISSIONS,
    SCOPED_PERMISSIONS,
    SELF_PERMISSIONS,
    SENSITIVE_PRIVATE_PERMISSIONS,
    SHARED_PERMISSIONS,
    PolicyDecision,
)
from app.services import rbac, security_events, settings_service

logger = logging.getLogger(__name__)

TRUTHY = {"true", "1", "yes", "on", "enabled"}
DEFAULT_INSTITUTION = "default"


@dataclass(frozen=True)
class BreakGlassInfo:
    id: int
    permission: str
    expires_at: datetime | None
    reason: str
    reference: str | None


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _setting(db: Session | None, key: str, default: str) -> str:
    if db is None:
        return default
    return (
        settings_service.get_setting_fresh(db, key, default) or default
    ).strip()


def _truthy(value: str, default: bool = False) -> bool:
    text = (value or "").strip().lower()
    return text in TRUTHY if text else default


def _int_setting(db: Session, key: str, default: int) -> int:
    try:
        return int(_setting(db, key, str(default)))
    except (TypeError, ValueError):
        return default


def tenant_of(user: User | None) -> str:
    return (
        (getattr(user, "institution_id", None) or DEFAULT_INSTITUTION)
        .strip()
        .lower()
    )


def consent_type_for_permission(permission: str) -> str | None:
    """Return the learner consent type that gates a permission, if any."""
    if permission.startswith(("dna.", "career_affinity.", "recommendation.")):
        return "cyber_dna"
    if permission.startswith("gps."):
        return "cyber_gps"
    if permission.startswith("coach."):
        return "ai_coach"
    if permission in {"competency.view", "competency.view.self"}:
        return "cyber_dna"
    if permission.startswith("portfolio."):
        return "portfolio"
    return None


def _consent_status(db: Session, user_id: int, consent_type: str) -> str | None:
    try:
        from app.consent import service as consent_service

        return consent_service.blocked_status(db, user_id, consent_type)
    except Exception:
        # A consent registry failure must not turn a deny into an allow. Treat
        # the missing check as a block on derived-data permissions.
        logger.exception("Consent check failed for user %s type %s", user_id, consent_type)
        return "unavailable"


def _decision(
    user: User,
    permission: str,
    allowed: bool,
    reason: str,
    *,
    source: str = "role",
    scope: dict | None = None,
    break_glass_id: int | None = None,
) -> PolicyDecision:
    return PolicyDecision(
        allowed=allowed,
        permission=permission,
        reason=reason,
        role=(getattr(user, "role", "") or "student"),
        scope=scope or {},
        source=source,
        break_glass_id=break_glass_id,
        tenant_id=tenant_of(user),
    )


def _record_denial(
    user: User,
    permission: str,
    reason: str,
    *,
    resource_user_id: int | None,
    course_id: int | None,
) -> None:
    if permission not in PERMISSION_CATALOG:
        return
    meta = PERMISSION_META.get(permission, {})
    if meta.get("sensitivity") not in {"high", "critical", "restricted"}:
        return
    security_events.record(
        "authz.denied",
        outcome="denied",
        actor=user,
        target_type="user" if resource_user_id else ("course" if course_id else None),
        target_id=resource_user_id or course_id,
        detail={
            "permission": permission,
            "reason": reason,
            "resource_user_id": resource_user_id,
            "course_id": course_id,
        },
    )


def _active_grant(
    db: Session,
    user_id: int,
    permission: str,
    *,
    resource_user_id: int | None,
    course_id: int | None,
) -> BreakGlassGrant | None:
    if not _truthy(_setting(db, "break_glass_enabled", "false"), False):
        return None
    now = _now()
    rows = (
        db.query(BreakGlassGrant)
        .filter(
            BreakGlassGrant.user_id == user_id,
            BreakGlassGrant.permission == permission,
            BreakGlassGrant.status == "active",
            BreakGlassGrant.expires_at > now,
        )
        .order_by(BreakGlassGrant.expires_at.asc())
        .all()
    )
    for row in rows:
        if row.scope_user_id is not None and row.scope_user_id != resource_user_id:
            continue
        if row.scope_course_id is not None and row.scope_course_id != course_id:
            continue
        return row
    return None


def _consume_grant(grant_id: int, actor: User, reason: str) -> None:
    """Record use without committing the caller's transaction."""
    from app.database import SessionLocal

    own = SessionLocal()
    try:
        row = own.get(BreakGlassGrant, grant_id)
        if row is None:
            return
        row.use_count = (row.use_count or 0) + 1
        row.last_used_at = _now()
        own.commit()
        security_events.record(
            "break_glass.used",
            severity="critical",
            actor=actor,
            target_type="break_glass",
            target_id=grant_id,
            detail={
                "permission": row.permission,
                "reason": row.reason,
                "reference": row.reference,
                "access_reason": reason,
                "use_count": row.use_count,
            },
        )
    finally:
        own.close()


class AuthorizationService:
    """One place to answer "may this actor do this to this resource?"."""

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.role = (getattr(user, "role", "") or "student").strip().lower()

    def permissions(self) -> frozenset[str]:
        return rbac.effective_permissions(self.db, self.user)

    def roles(self) -> list[str]:
        return rbac.effective_roles(self.db, self.user)

    def _tenant_enforced(self) -> bool:
        return _truthy(_setting(self.db, "tenant_isolation_enabled", "true"), True)

    def _same_tenant(self, owner: User | None) -> bool:
        if owner is None:
            return False
        if self.role == "admin" or not self._tenant_enforced():
            return True
        return tenant_of(owner) == tenant_of(self.user)

    def _course_tenant_allows(self, course: Course) -> bool:
        if self.role == "admin" or not self._tenant_enforced():
            return True
        instructor = (
            self.db.query(User).filter(User.id == course.instructor_id).first()
        )
        if instructor is None:
            return False
        return tenant_of(instructor) == tenant_of(self.user)

    def check(
        self,
        permission: str,
        *,
        resource_user_id: int | None = None,
        course_id: int | None = None,
        shared: bool = False,
        reason: str | None = None,
    ) -> PolicyDecision:
        if permission not in PERMISSION_CATALOG:
            return _decision(self.user, permission, False, "Unknown permission")

        granted = self.permissions()
        scope: dict = {"role": self.role, "roles": self.roles()}
        if self.role == "auditor" and permission not in READ_ONLY_PERMISSIONS:
            self._deny(permission, "Auditor access is read-only", resource_user_id, course_id)
            return _decision(
                self.user,
                permission,
                False,
                "Auditor access is read-only",
                scope={**scope, "read_only": True},
            )
        if permission not in granted:
            return self._maybe_break_glass(
                permission,
                "Role does not grant this permission",
                resource_user_id=resource_user_id,
                course_id=course_id,
                scope=scope,
                shared=shared,
                access_reason=reason,
            )

        owner = None
        if resource_user_id is not None and self.db is not None:
            owner = self.db.query(User).filter(User.id == resource_user_id).first()
            if owner is None:
                return _decision(
                    self.user,
                    permission,
                    False,
                    "Resource owner not found",
                    scope=scope,
                )
            if not self._same_tenant(owner):
                self._deny(
                    permission,
                    "Cross-institution access is not allowed",
                    resource_user_id,
                    course_id,
                )
                return _decision(
                    self.user,
                    permission,
                    False,
                    "Cross-institution access is not allowed",
                    scope={**scope, "tenant": tenant_of(self.user)},
                )

        consent_type = consent_type_for_permission(permission)
        subject_id = resource_user_id
        if subject_id is None and permission in SELF_PERMISSIONS:
            subject_id = self.user.id
        if consent_type and subject_id is not None and self.db is not None:
            status = _consent_status(self.db, subject_id, consent_type)
            if status:
                self._deny(
                    permission,
                    f"Consent for {consent_type} is {status}",
                    resource_user_id,
                    course_id,
                )
                return _decision(
                    self.user,
                    permission,
                    False,
                    f"Consent for {consent_type} is {status}; emergency access "
                    "does not override a learner's consent decision.",
                    scope={**scope, "consent_type": consent_type, "consent_status": status},
                )

        if permission in SENSITIVE_PRIVATE_PERMISSIONS:
            if resource_user_id != self.user.id and not shared:
                return self._maybe_break_glass(
                    permission,
                    "Private data requires the owner or an explicit share",
                    resource_user_id=resource_user_id,
                    course_id=course_id,
                    scope=scope,
                    shared=shared,
                    access_reason=reason,
                )

        if permission in SELF_PERMISSIONS:
            if resource_user_id is not None and resource_user_id != self.user.id:
                self._deny(
                    permission,
                    "Self-scoped permission cannot target another learner",
                    resource_user_id,
                    course_id,
                )
                return _decision(
                    self.user,
                    permission,
                    False,
                    "Self-scoped permission cannot target another learner",
                    scope=scope,
                )
            return _decision(
                self.user, permission, True, "Self-scoped access", scope=scope
            )

        if permission in SHARED_PERMISSIONS:
            if not shared:
                return _decision(
                    self.user,
                    permission,
                    False,
                    "No active learner share grants this access",
                    scope=scope,
                )
            return _decision(
                self.user, permission, True, "Explicit learner share", scope=scope
            )

        if permission in SCOPED_PERMISSIONS:
            if self.role == "admin":
                return _decision(
                    self.user, permission, True, "Platform administration", scope=scope
                )
            if course_id is None:
                return _decision(
                    self.user,
                    permission,
                    False,
                    "A course scope is required for this permission",
                    scope=scope,
                )
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if course is None:
                return _decision(
                    self.user, permission, False, "Course not found", scope=scope
                )
            if not self._course_tenant_allows(course):
                self._deny(
                    permission,
                    "Course belongs to another institution",
                    resource_user_id,
                    course_id,
                )
                return _decision(
                    self.user,
                    permission,
                    False,
                    "Course belongs to another institution",
                    scope={**scope, "course_id": course_id},
                )
            if self.role in {"institution_admin", "privacy_officer"}:
                return _decision(
                    self.user,
                    permission,
                    True,
                    "Institution administrative scope",
                    scope={**scope, "course_id": course_id},
                )
            if course.instructor_id != self.user.id:
                self._deny(
                    permission,
                    "Course is not assigned to this user",
                    resource_user_id,
                    course_id,
                )
                return _decision(
                    self.user,
                    permission,
                    False,
                    "Course is not assigned to this user",
                    scope={**scope, "course_id": course_id},
                )
            return _decision(
                self.user,
                permission,
                True,
                "Assigned course scope",
                scope={**scope, "course_id": course_id},
            )

        if self.role == "admin":
            return _decision(
                self.user, permission, True, "Platform administration", scope=scope
            )
        return _decision(self.user, permission, True, "Role permission", scope=scope)

    def _deny(
        self,
        permission: str,
        reason: str,
        resource_user_id: int | None,
        course_id: int | None,
    ) -> None:
        if self.db is None:
            return
        _record_denial(
            self.user,
            permission,
            reason,
            resource_user_id=resource_user_id,
            course_id=course_id,
        )

    def _maybe_break_glass(
        self,
        permission: str,
        reason: str,
        *,
        resource_user_id: int | None,
        course_id: int | None,
        scope: dict,
        shared: bool,
        access_reason: str | None,
    ) -> PolicyDecision:
        # Consent is a legal gate, not a role gate. Check it before any
        # break-glass path so emergency access cannot override a learner's
        # revocation.
        consent_type = consent_type_for_permission(permission)
        subject_id = resource_user_id
        if subject_id is None and permission in SELF_PERMISSIONS:
            subject_id = self.user.id
        if consent_type and subject_id is not None and self.db is not None:
            status = _consent_status(self.db, subject_id, consent_type)
            if status:
                denial = (
                    f"Consent for {consent_type} is {status}; emergency access "
                    "does not override a learner's consent decision."
                )
                self._deny(permission, denial, resource_user_id, course_id)
                return _decision(
                    self.user,
                    permission,
                    False,
                    denial,
                    scope={
                        **scope,
                        "consent_type": consent_type,
                        "consent_status": status,
                    },
                )
        if permission not in BREAK_GLASS_PERMISSIONS:
            self._deny(permission, reason, resource_user_id, course_id)
            return _decision(self.user, permission, False, reason, scope=scope)
        if not _truthy(_setting(self.db, "break_glass_enabled", "false"), False):
            self._deny(permission, reason, resource_user_id, course_id)
            return _decision(self.user, permission, False, reason, scope=scope)
        if _truthy(_setting(self.db, "break_glass_require_mfa", "true"), True):
            if not getattr(self.user, "mfa_enabled", False):
                denial = (
                    "Break-glass access requires MFA on this account; normal "
                    f"policy also denied: {reason}"
                )
                self._deny(permission, denial, resource_user_id, course_id)
                return _decision(self.user, permission, False, denial, scope=scope)

        grant = _active_grant(
            self.db,
            self.user.id,
            permission,
            resource_user_id=resource_user_id,
            course_id=course_id,
        )
        if grant is None:
            self._deny(permission, reason, resource_user_id, course_id)
            return _decision(
                self.user,
                permission,
                False,
                f"{reason}. No active break-glass grant covers this request.",
                scope=scope,
            )

        _consume_grant(grant.id, self.user, access_reason or "authorization check")
        return _decision(
            self.user,
            permission,
            True,
            "Break-glass grant: " + (grant.reason or "emergency access"),
            source="break_glass",
            scope={**scope, "break_glass_reference": grant.reference},
            break_glass_id=grant.id,
        )


def authorize(
    db: Session,
    user: User,
    permission: str,
    *,
    resource_user_id: int | None = None,
    course_id: int | None = None,
    shared: bool = False,
    reason: str | None = None,
) -> PolicyDecision:
    return AuthorizationService(db, user).check(
        permission,
        resource_user_id=resource_user_id,
        course_id=course_id,
        shared=shared,
        reason=reason,
    )


def explain(
    db: Session,
    user: User,
    permission: str,
    *,
    resource_user_id: int | None = None,
    course_id: int | None = None,
    shared: bool = False,
) -> dict:
    service = AuthorizationService(db, user)
    decision = service.check(
        permission,
        resource_user_id=resource_user_id,
        course_id=course_id,
        shared=shared,
    )
    return {
        "allowed": decision.allowed,
        "permission": decision.permission,
        "reason": decision.reason,
        "role": decision.role,
        "roles": service.roles(),
        "source": decision.source,
        "break_glass_id": decision.break_glass_id,
        "tenant_id": decision.tenant_id,
        "scope": decision.scope,
    }


# --- Object-level helpers ---------------------------------------------------


def require_owner(
    db: Session,
    actor: User,
    owner_id: int,
    *,
    resource: str = "record",
    allow_system_admin: bool = False,
) -> None:
    """Enforce ``actor.id == resource.ownerId`` after RBAC.

    Returns 404, not 403, so a guessed identifier cannot reveal whether another
    learner's record exists. System administrators must opt in explicitly and
    still cannot read private data through a self/owner-only endpoint.
    """
    is_admin = allow_system_admin and (getattr(actor, "role", "") or "") == "admin"
    if actor.id == owner_id or is_admin:
        return
    security_events.record(
        "authz.denied",
        outcome="denied",
        actor=actor,
        target_type=resource,
        target_id=owner_id,
        detail={"owner_id": owner_id, "reason": "owner mismatch"},
    )
    raise HTTPException(status_code=404, detail=f"{resource.title()} not found.")


def require_tenant(actor: User, resource_tenant: str | None) -> None:
    """Enforce ``resource.tenantId == actor.tenantId`` for non-system admins."""
    if (getattr(actor, "role", "") or "") == "admin":
        return
    if tenant_of(actor) == (resource_tenant or DEFAULT_INSTITUTION).lower():
        return
    security_events.record(
        "authz.denied",
        outcome="denied",
        actor=actor,
        target_type="tenant",
        target_label=resource_tenant,
        detail={
            "resource_tenant": resource_tenant,
            "actor_tenant": tenant_of(actor),
        },
    )
    raise HTTPException(status_code=404, detail="Resource not found.")


# --- Break-glass workflow ---------------------------------------------------


def create_break_glass(
    db: Session,
    actor: User,
    *,
    permission: str,
    reason: str,
    minutes: int | None = None,
    reference: str | None = None,
    scope_user_id: int | None = None,
    scope_course_id: int | None = None,
    target_user: User | None = None,
    allow_approval: bool = False,
) -> BreakGlassGrant:
    if not _truthy(_setting(db, "break_glass_enabled", "false"), False):
        raise HTTPException(status_code=403, detail="Break-glass access is disabled.")
    if permission not in BREAK_GLASS_PERMISSIONS:
        raise HTTPException(
            status_code=400,
            detail="That permission is not eligible for break-glass access.",
        )
    reason = (reason or "").strip()
    if len(reason) < 10:
        raise HTTPException(
            status_code=422,
            detail="A break-glass reason of at least 10 characters is required.",
        )
    require_mfa = _truthy(
        _setting(db, "break_glass_require_mfa", "true"), True
    )
    if require_mfa and not getattr(actor, "mfa_enabled", False):
        raise HTTPException(
            status_code=403,
            detail="Enable MFA before requesting break-glass access.",
        )
    grantee = target_user or actor
    if require_mfa and grantee.id != actor.id and not getattr(grantee, "mfa_enabled", False):
        raise HTTPException(
            status_code=403,
            detail="The target account must enable MFA before break-glass access.",
        )
    max_minutes = max(5, min(_int_setting(db, "break_glass_max_minutes", 60), 1440))
    minutes = max(1, min(int(minutes or max_minutes), max_minutes))
    now = _now()
    expires_at = now + timedelta(minutes=minutes)

    existing = (
        db.query(BreakGlassGrant)
        .filter(
            BreakGlassGrant.user_id == grantee.id,
            BreakGlassGrant.permission == permission,
            BreakGlassGrant.status.in_(("pending", "active")),
            BreakGlassGrant.expires_at > now,
        )
        .first()
    )
    if existing is not None:
        return existing

    require_approval = _truthy(
        _setting(db, "break_glass_require_approval", "false"), False
    )
    auto_active = not require_approval and (allow_approval or actor.id == grantee.id)
    row = BreakGlassGrant(
        user_id=grantee.id,
        permission=permission,
        scope_user_id=scope_user_id,
        scope_course_id=scope_course_id,
        reason=reason[:2000],
        reference=(reference or "")[:120] or None,
        status="active" if auto_active else "pending",
        requested_by_id=actor.id,
        approved_by_id=actor.id if auto_active else None,
        approved_at=now if auto_active else None,
        expires_at=expires_at,
        review_status="pending",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    security_events.record(
        "break_glass.requested",
        actor=actor,
        target_type="user",
        target_id=grantee.id,
        target_label=grantee.username,
        detail={
            "grant_id": row.id,
            "permission": permission,
            "status": row.status,
            "reason": reason,
            "reference": reference,
            "expires_at": expires_at.isoformat(),
        },
    )
    return row


def approve_break_glass(
    db: Session, actor: User, grant_id: int, *, note: str | None = None
) -> BreakGlassGrant:
    row = db.get(BreakGlassGrant, grant_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Break-glass grant not found.")
    if row.status != "pending":
        raise HTTPException(status_code=409, detail="Grant is not pending approval.")
    if row.requested_by_id == actor.id and not getattr(actor, "is_admin", False):
        raise HTTPException(
            status_code=403, detail="A second operator must approve this request."
        )
    row.status = "active"
    row.approved_by_id = actor.id
    row.approved_at = _now()
    db.commit()
    security_events.record(
        "break_glass.approved",
        actor=actor,
        target_type="break_glass",
        target_id=row.id,
        detail={"permission": row.permission, "note": note},
    )
    return row


def revoke_break_glass(
    db: Session, actor: User, grant_id: int, *, reason: str | None = None
) -> BreakGlassGrant:
    row = db.get(BreakGlassGrant, grant_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Break-glass grant not found.")
    row.status = "revoked"
    row.revoked_at = _now()
    row.revoked_by_id = actor.id
    db.commit()
    security_events.record(
        "break_glass.revoked",
        actor=actor,
        target_type="break_glass",
        target_id=row.id,
        detail={"permission": row.permission, "reason": reason},
    )
    return row


def review_break_glass(
    db: Session, actor: User, grant_id: int, *, note: str
) -> BreakGlassGrant:
    row = db.get(BreakGlassGrant, grant_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Break-glass grant not found.")
    if not (note or "").strip():
        raise HTTPException(status_code=422, detail="A review note is required.")
    row.review_status = "reviewed"
    row.reviewed_by_id = actor.id
    row.reviewed_at = _now()
    row.review_note = note.strip()[:2000]
    db.commit()
    security_events.record(
        "break_glass.reviewed",
        actor=actor,
        target_type="break_glass",
        target_id=row.id,
        detail={"permission": row.permission, "note": note, "use_count": row.use_count},
    )
    return row


def expire_stale_grants(db: Session) -> int:
    now = _now()
    rows = (
        db.query(BreakGlassGrant)
        .filter(
            BreakGlassGrant.status.in_(("pending", "active")),
            BreakGlassGrant.expires_at <= now,
        )
        .all()
    )
    for row in rows:
        row.status = "expired"
    if rows:
        db.commit()
        security_events.record(
            "break_glass.expired",
            severity="notice",
            detail={
                "count": len(rows),
                "grant_ids": [row.id for row in rows],
                "permissions": sorted({row.permission for row in rows}),
            },
        )
    return len(rows)
