"""Policy-based authorization for scoped resources.

Role checks answer "may this kind of user do this at all?". Policies answer
"may this user do it to this record?". The function is deny-by-default and
keeps the existing ``User.role`` values working while adding auditor,
privacy-officer, employer, and institution roles for new surfaces.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Course, User
from app.security.permissions import (
    PERMISSION_CATALOG,
    READ_ONLY_PERMISSIONS,
    SCOPED_PERMISSIONS,
    SELF_PERMISSIONS,
    SENSITIVE_PRIVATE_PERMISSIONS,
    SHARED_PERMISSIONS,
    permissions_for_role,
    PolicyDecision,
)


def _deny(user: User, permission: str, reason: str, scope: dict | None = None):
    return PolicyDecision(
        allowed=False,
        permission=permission,
        reason=reason,
        role=(getattr(user, "role", "") or "student"),
        scope=scope or {},
    )


def _allow(user: User, permission: str, reason: str, scope: dict | None = None):
    return PolicyDecision(
        allowed=True,
        permission=permission,
        reason=reason,
        role=(getattr(user, "role", "") or "student"),
        scope=scope or {},
    )


def authorize(
    db: Session,
    user: User,
    permission: str,
    *,
    resource_user_id: int | None = None,
    course_id: int | None = None,
    shared: bool = False,
) -> PolicyDecision:
    """Return a decision for one permission and one resource scope.

    ``resource_user_id`` is the owner of the record. ``course_id`` is the
    teaching scope for staff-only permissions. ``shared`` is only true when a
    live learner share token (or an equivalent explicit grant) was verified by
    the caller; the caller must never infer it from a query parameter alone.
    """
    role = (getattr(user, "role", "") or "student").strip().lower()
    if permission not in PERMISSION_CATALOG:
        return _deny(user, permission, "Unknown permission", {"role": role})

    granted = permissions_for_role(role)
    if role == "auditor" and permission not in READ_ONLY_PERMISSIONS:
        return _deny(user, permission, "Auditor access is read-only", {"role": role})
    if permission not in granted:
        return _deny(user, permission, "Role does not grant this permission", {"role": role})

    if permission in SENSITIVE_PRIVATE_PERMISSIONS:
        # Even administrators need a self or explicit-share basis. No role
        # receives these by default; this branch documents the requirement.
        if resource_user_id != user.id and not shared:
            return _deny(
                user,
                permission,
                "Private data requires the owner or an explicit share",
                {"role": role},
            )

    if permission in SELF_PERMISSIONS:
        if resource_user_id is not None and resource_user_id != user.id:
            return _deny(
                user,
                permission,
                "Self-scoped permission cannot target another learner",
                {"role": role, "resource_user_id": resource_user_id},
            )
        return _allow(user, permission, "Self-scoped access", {"role": role})

    if permission in SHARED_PERMISSIONS:
        if not shared:
            return _deny(
                user,
                permission,
                "No active learner share grants this access",
                {"role": role},
            )
        return _allow(user, permission, "Explicit learner share", {"role": role})

    if permission in SCOPED_PERMISSIONS:
        if role in {"admin", "institution_admin", "privacy_officer"}:
            return _allow(user, permission, "Administrative scope", {"role": role})
        if course_id is None:
            return _deny(
                user,
                permission,
                "A course scope is required for this permission",
                {"role": role},
            )
        course = db.query(Course).filter(Course.id == course_id).first()
        if course is None:
            return _deny(user, permission, "Course not found", {"role": role})
        if course.instructor_id != user.id:
            return _deny(
                user,
                permission,
                "Course is not assigned to this user",
                {"role": role, "course_id": course_id},
            )
        return _allow(
            user,
            permission,
            "Assigned course scope",
            {"role": role, "course_id": course_id},
        )

    if role == "admin":
        return _allow(user, permission, "Platform administration", {"role": role})

    return _allow(user, permission, "Role permission", {"role": role})


def require_allowed(
    db: Session,
    user: User,
    permission: str,
    *,
    resource_user_id: int | None = None,
    course_id: int | None = None,
    shared: bool = False,
) -> PolicyDecision:
    decision = authorize(
        db,
        user,
        permission,
        resource_user_id=resource_user_id,
        course_id=course_id,
        shared=shared,
    )
    if not decision.allowed:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403,
            detail=decision.reason,
            headers={"X-Policy-Permission": permission},
        )
    return decision
