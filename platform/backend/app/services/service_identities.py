"""Scoped, hashed credentials for non-human service identities.

A service identity is not a shared administrator key. It is a normal account
with role ``service_account``, password login disabled, and an explicit scope
list. The raw bearer token is shown once; only its SHA-256 hash is stored.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.models import ServiceCredential, User
from app.security.permissions import (
    PERMISSION_CATALOG,
    SENSITIVE_PRIVATE_PERMISSIONS,
)
from app.services import security_events

TOKEN_PREFIX = "ocr_svc"
MAX_SCOPE_COUNT = 200


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def _normalize_scopes(scopes: list[str]) -> list[str]:
    wanted = sorted({str(item).strip() for item in scopes if str(item).strip()})
    unknown = set(wanted) - set(PERMISSION_CATALOG)
    if unknown:
        raise HTTPException(
            status_code=422, detail=f"Unknown service scopes: {sorted(unknown)}"
        )
    private = set(wanted) & SENSITIVE_PRIVATE_PERMISSIONS
    if private:
        raise HTTPException(
            status_code=422,
            detail=(
                "Service identities cannot receive private learner permissions; "
                f"owner/share/break-glass access is required: {sorted(private)}"
            ),
        )
    if len(wanted) > MAX_SCOPE_COUNT:
        raise HTTPException(status_code=422, detail="Too many service scopes.")
    return wanted


def create_credential(
    db: Session,
    actor: User,
    *,
    name: str,
    scopes: list[str],
    days: int = 90,
    institution_id: str | None = None,
) -> tuple[ServiceCredential, str]:
    name = (name or "").strip()
    if len(name) < 3:
        raise HTTPException(status_code=422, detail="A service name is required.")
    scope_list = _normalize_scopes(scopes)
    if not scope_list:
        raise HTTPException(status_code=422, detail="At least one scope is required.")
    lifetime = max(1, min(int(days or 90), 365))
    suffix = uuid.uuid4().hex[:12]
    service_user = User(
        username=f"svc_{suffix}",
        email=f"svc_{suffix}@service.invalid",
        hashed_password=get_password_hash(secrets.token_urlsafe(32)),
        is_active=True,
        is_approved=True,
        is_admin=False,
        role="service_account",
        password_login_disabled=True,
        password_rehashed_at=_now(),
        institution_id=institution_id or getattr(actor, "institution_id", "default"),
    )
    db.add(service_user)
    db.flush()

    secret = secrets.token_urlsafe(32)
    row = ServiceCredential(
        user_id=service_user.id,
        name=name[:120],
        token_hash=_hash(secret),
        scopes=json.dumps(scope_list),
        institution_id=service_user.institution_id,
        created_by_id=getattr(actor, "id", None),
        expires_at=_now() + timedelta(days=lifetime),
    )
    db.add(row)
    db.flush()
    # The credential id, not the user id, is the lookup key.
    token = f"{TOKEN_PREFIX}_{row.id}_{secret}"
    db.commit()
    db.refresh(row)
    security_events.record(
        "service_identity.created",
        actor=actor,
        target_type="service_credential",
        target_id=row.id,
        target_label=service_user.username,
        detail={
            "name": row.name,
            "scopes": scope_list,
            "days": lifetime,
            "institution_id": row.institution_id,
        },
    )
    return row, token


def resolve_token(db: Session, token: str) -> User | None:
    if not token.startswith(TOKEN_PREFIX + "_"):
        return None
    try:
        _, _, credential_id, secret = token.split("_", 3)
        credential_id_int = int(credential_id)
    except (ValueError, TypeError):
        return None
    row = db.get(ServiceCredential, credential_id_int)
    if row is None or row.revoked_at is not None or row.expires_at <= _now():
        return None
    if not hmac.compare_digest(row.token_hash, _hash(secret)):
        return None
    user = db.get(User, row.user_id)
    if (
        user is None
        or not user.is_active
        or not user.is_approved
        or user.role != "service_account"
    ):
        return None
    try:
        scopes = json.loads(row.scopes or "[]")
    except json.JSONDecodeError:
        scopes = []
    if not isinstance(scopes, list):
        scopes = []
    user._service_scopes = frozenset(str(item) for item in scopes)
    user._service_credential_id = row.id
    row.last_used_at = _now()
    db.commit()
    return user


def list_credentials(db: Session, *, institution_id: str | None = None) -> list[dict]:
    query = db.query(ServiceCredential)
    if institution_id:
        query = query.filter(ServiceCredential.institution_id == institution_id)
    rows = query.order_by(ServiceCredential.id.desc()).limit(200).all()
    users = {
        row.id: row
        for row in db.query(User)
        .filter(User.id.in_({item.user_id for item in rows}))
        .all()
    } if rows else {}
    payload = []
    for row in rows:
        try:
            scopes = json.loads(row.scopes or "[]")
        except json.JSONDecodeError:
            scopes = []
        payload.append(
            {
                "id": row.id,
                "name": row.name,
                "user_id": row.user_id,
                "username": getattr(users.get(row.user_id), "username", None),
                "institution_id": row.institution_id,
                "scopes": scopes,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "expires_at": row.expires_at.isoformat() if row.expires_at else None,
                "last_used_at": row.last_used_at.isoformat() if row.last_used_at else None,
                "revoked_at": row.revoked_at.isoformat() if row.revoked_at else None,
                "active": row.revoked_at is None and row.expires_at > _now(),
            }
        )
    return payload


def revoke_credential(db: Session, actor: User, credential_id: int) -> bool:
    row = db.get(ServiceCredential, credential_id)
    if row is None:
        return False
    if row.revoked_at is not None:
        return True
    row.revoked_at = _now()
    row.revoked_by_id = getattr(actor, "id", None)
    db.commit()
    security_events.record(
        "service_identity.revoked",
        actor=actor,
        target_type="service_credential",
        target_id=row.id,
        target_label=row.name,
    )
    return True
