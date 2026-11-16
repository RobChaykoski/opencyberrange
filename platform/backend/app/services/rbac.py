"""Database-backed RBAC: seeding, effective grants, and role administration.

``permissions.yaml`` is the reviewed baseline. On first boot the catalog and
role grants are copied into the RBAC tables. Later boots add newly introduced
permissions and their default grants without overwriting an administrator's
reviewed changes.

The Authorization Service reads these tables. If the tables are absent (a unit
test before schema creation) the static YAML grants remain the fallback, so a
deny-by-default policy never becomes an accidental allow.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import RbacPermission, RbacRole, RbacRolePermission, RbacUserRole, User
from app.security.permissions import (
    PERMISSION_CATALOG,
    PERMISSION_META,
    ROLE_META,
    ROLE_PERMISSIONS,
    SENSITIVE_PRIVATE_PERMISSIONS,
    permissions_for_role,
)
from app.services import security_events

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def seed(db: Session) -> dict[str, int]:
    """Idempotently copy the YAML catalog into the RBAC tables."""
    added_permissions = 0
    added_roles = 0
    added_grants = 0

    permission_rows: dict[str, RbacPermission] = {
        row.key: row for row in db.query(RbacPermission).all()
    }
    new_permission_keys: set[str] = set()
    for key, description in PERMISSION_CATALOG.items():
        meta = PERMISSION_META.get(key, {})
        row = permission_rows.get(key)
        if row is None:
            row = RbacPermission(
                key=key,
                description=description,
                category=meta.get("category"),
                sensitivity=meta.get("sensitivity") or "medium",
            )
            db.add(row)
            permission_rows[key] = row
            new_permission_keys.add(key)
            added_permissions += 1
        else:
            # Description and sensitivity are release metadata; refresh them so
            # a catalog review is visible in the admin view immediately.
            row.description = description
            row.category = meta.get("category")
            row.sensitivity = meta.get("sensitivity") or "medium"
    db.flush()

    role_rows: dict[str, RbacRole] = {
        row.key: row for row in db.query(RbacRole).all()
    }
    new_role_keys: set[str] = set()
    for key in ROLE_PERMISSIONS:
        meta = ROLE_META.get(key, {})
        role = role_rows.get(key)
        if role is None:
            role = RbacRole(
                key=key,
                label=str(meta.get("label") or key.replace("_", " ").title()),
                description=meta.get("description"),
                rank=int(meta.get("rank") or 100),
                is_system=True,
            )
            db.add(role)
            role_rows[key] = role
            new_role_keys.add(key)
            added_roles += 1
    db.flush()

    existing = {
        (row.role_id, row.permission_id)
        for row in db.query(RbacRolePermission).all()
    }
    for role_key, grants in ROLE_PERMISSIONS.items():
        role = role_rows[role_key]
        if role_key not in new_role_keys:
            # A newly introduced permission receives its default grant, but an
            # existing permission grant is not restored after an admin review.
            grants = {key for key in grants if key in new_permission_keys}
        for permission_key in grants:
            permission = permission_rows.get(permission_key)
            if permission is None or permission.id is None:
                continue
            pair = (role.id, permission.id)
            if pair in existing:
                continue
            db.add(
                RbacRolePermission(
                    role_id=role.id, permission_id=permission.id
                )
            )
            existing.add(pair)
            added_grants += 1
    db.commit()
    result = {
        "permissions": added_permissions,
        "roles": added_roles,
        "grants": added_grants,
    }
    if any(result.values()):
        logger.info("RBAC catalog seeded: %s", result)
    return result


def _role_permissions_from_db(db: Session, role_key: str) -> frozenset[str] | None:
    role = db.query(RbacRole).filter(RbacRole.key == role_key).first()
    if role is None:
        return None
    return frozenset(row.key for row in role.permissions)


def role_permissions(db: Session | None, role_key: str) -> frozenset[str]:
    """Return a role's grants, falling back to the reviewed YAML baseline."""
    if db is None:
        return permissions_for_role(role_key)
    try:
        stored = _role_permissions_from_db(db, role_key)
    except SQLAlchemyError:
        db.rollback()
        return permissions_for_role(role_key)
    return stored if stored is not None else permissions_for_role(role_key)


def extra_roles(db: Session | None, user_id: int) -> list[str]:
    if db is None:
        return []
    now = _now()
    try:
        rows = (
            db.query(RbacUserRole)
            .filter(RbacUserRole.user_id == user_id)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        return []
    return [
        row.role_key
        for row in rows
        if row.expires_at is None or row.expires_at > now
    ]


def effective_roles(db: Session | None, user: User) -> list[str]:
    base = (getattr(user, "role", "") or "student").strip().lower()
    if db is None:
        return [base]
    roles = [base]
    for role in extra_roles(db, user.id):
        if role not in roles:
            roles.append(role)
    return roles


def effective_permissions(db: Session | None, user: User) -> frozenset[str]:
    if db is None:
        return permissions_for_role(getattr(user, "role", "student"))
    permissions: set[str] = set()
    for role in effective_roles(db, user):
        permissions.update(role_permissions(db, role))
    # A service credential carries an explicit, narrower scope list. It is
    # additive to the (empty) service_account role and never widens a human.
    permissions.update(getattr(user, "_service_scopes", frozenset()))
    return frozenset(permissions)


def role_catalog(db: Session) -> list[dict]:
    rows = []
    for role in db.query(RbacRole).order_by(RbacRole.rank, RbacRole.key).all():
        rows.append(
            {
                "key": role.key,
                "label": role.label,
                "description": role.description,
                "rank": role.rank,
                "is_system": role.is_system,
                "permissions": sorted(row.key for row in role.permissions),
            }
        )
    return rows


def permission_catalog(db: Session) -> list[dict]:
    return [
        {
            "key": row.key,
            "description": row.description,
            "category": row.category,
            "sensitivity": row.sensitivity,
            "scope": PERMISSION_META.get(row.key, {}).get("scope", "global"),
            "read_only": bool(PERMISSION_META.get(row.key, {}).get("read_only")),
            "break_glass": bool(PERMISSION_META.get(row.key, {}).get("break_glass")),
        }
        for row in db.query(RbacPermission).order_by(RbacPermission.key).all()
    ]


def set_role_permissions(
    db: Session,
    actor: User | None,
    role_key: str,
    permissions: list[str],
) -> dict:
    """Replace one role's grants. Sensitive private data stays ungrantable."""
    role = db.query(RbacRole).filter(RbacRole.key == role_key).first()
    if role is None:
        raise ValueError(f"unknown role: {role_key}")
    wanted = {str(item).strip() for item in permissions if str(item).strip()}
    unknown = wanted - set(PERMISSION_CATALOG)
    if unknown:
        raise ValueError(f"unknown permissions: {sorted(unknown)}")
    private = wanted & SENSITIVE_PRIVATE_PERMISSIONS
    if private:
        raise ValueError(
            "private permissions require the owner, an explicit share, or a "
            f"break-glass grant: {sorted(private)}"
        )
    if role_key == "admin" and "rbac.manage" not in wanted:
        raise ValueError("the admin role must keep rbac.manage to avoid lockout")

    rows = db.query(RbacPermission).filter(RbacPermission.key.in_(wanted)).all()
    role.permissions = rows
    db.commit()
    security_events.record(
        "rbac.permissions_changed",
        actor=actor,
        target_type="role",
        target_id=role_key,
        detail={"permissions": sorted(wanted), "count": len(wanted)},
    )
    return {
        "role": role_key,
        "permissions": sorted(row.key for row in rows),
    }


def grant_user_role(
    db: Session,
    actor: User | None,
    user: User,
    role_key: str,
    *,
    reason: str | None = None,
    expires_at: datetime | None = None,
) -> RbacUserRole:
    role = db.query(RbacRole).filter(RbacRole.key == role_key).first()
    if role is None:
        raise ValueError(f"unknown role: {role_key}")
    row = (
        db.query(RbacUserRole)
        .filter(
            RbacUserRole.user_id == user.id,
            RbacUserRole.role_key == role_key,
        )
        .first()
    )
    if row is None:
        row = RbacUserRole(
            user_id=user.id,
            role_key=role_key,
            institution_id=getattr(user, "institution_id", None),
            granted_by_id=getattr(actor, "id", None),
            reason=(reason or "")[:500] or None,
            expires_at=expires_at,
        )
        db.add(row)
    else:
        row.expires_at = expires_at
        row.reason = (reason or "")[:500] or None
    db.commit()
    security_events.record(
        "rbac.role_granted",
        actor=actor,
        target_type="user",
        target_id=user.id,
        target_label=user.username,
        detail={"role": role_key, "expires_at": expires_at, "reason": reason},
    )
    return row


def revoke_user_role(
    db: Session,
    actor: User | None,
    user: User,
    role_key: str,
) -> bool:
    row = (
        db.query(RbacUserRole)
        .filter(
            RbacUserRole.user_id == user.id,
            RbacUserRole.role_key == role_key,
        )
        .first()
    )
    if row is None:
        return False
    db.delete(row)
    db.commit()
    security_events.record(
        "rbac.role_revoked",
        actor=actor,
        target_type="user",
        target_id=user.id,
        target_label=user.username,
        detail={"role": role_key},
    )
    return True
