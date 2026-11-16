"""Portfolio share links with expiry, revocation, and single-use control.

The raw bearer token is returned once and never stored. Only its SHA-256 hash
is persisted. A share is additionally gated by the learner's live
``portfolio_sharing`` consent, so a revoked consent disables every existing link
immediately, before any expiry or revocation sweep.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import PortfolioShare, User
from app.services import security_events, settings_service

TRUTHY = {"true", "1", "yes", "on", "enabled"}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _setting(db: Session, key: str, default: str) -> str:
    return (
        settings_service.get_setting_fresh(db, key, default) or default
    ).strip()


def _default_days(db: Session) -> int:
    try:
        return max(1, min(int(_setting(db, "portfolio_share_lifetime_days", "30")), 365))
    except (TypeError, ValueError):
        return 30


def _consent_blocked(db: Session, user_id: int) -> str | None:
    try:
        from app.consent import service as consent_service

        return consent_service.blocked_status(db, user_id, "portfolio_sharing")
    except Exception:
        return "unavailable"


def create_share(
    db: Session,
    user: User,
    *,
    label: str | None = None,
    audience: str | None = None,
    days: int | None = None,
    single_use: bool = False,
    max_uses: int | None = None,
    actor: User | None = None,
) -> tuple[PortfolioShare, str]:
    status = _consent_blocked(db, user.id)
    if status:
        raise HTTPException(
            status_code=403,
            detail=(
                "Portfolio sharing consent is not active. Grant it from Privacy "
                "and consent before creating a share link."
            ),
            headers={"X-Consent-Status": status},
        )
    lifetime = max(1, min(int(days or _default_days(db)), 365))
    if single_use:
        max_uses = 1
    if max_uses is not None:
        max_uses = max(1, min(int(max_uses), 1000))
    token = secrets.token_urlsafe(32)
    row = PortfolioShare(
        user_id=user.id,
        token_hash=_hash(token),
        label=(label or "")[:120] or None,
        audience=(audience or "")[:120] or None,
        created_by_id=getattr(actor or user, "id", user.id),
        expires_at=_now() + timedelta(days=lifetime),
        single_use=bool(single_use),
        max_uses=max_uses,
        consent_version=None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    security_events.record(
        "portfolio.share_created",
        actor=actor or user,
        target_type="portfolio_share",
        target_id=row.id,
        detail={
            "label": row.label,
            "audience": row.audience,
            "days": lifetime,
            "single_use": row.single_use,
            "max_uses": row.max_uses,
        },
    )
    return row, token


def resolve_share(
    db: Session,
    token: str,
    *,
    ip_address: str | None = None,
) -> PortfolioShare | None:
    if not token:
        return None
    row = (
        db.query(PortfolioShare)
        .filter(PortfolioShare.token_hash == _hash(token))
        .first()
    )
    if row is None:
        return None
    now = _now()
    if row.revoked_at is not None or row.expires_at <= now:
        return None
    if _consent_blocked(db, row.user_id):
        return None
    conditions = [PortfolioShare.id == row.id, PortfolioShare.revoked_at.is_(None)]
    if row.max_uses is not None:
        conditions.append(PortfolioShare.use_count < row.max_uses)
    result = db.execute(
        update(PortfolioShare)
        .where(*conditions)
        .values(
            use_count=PortfolioShare.use_count + 1,
            last_used_at=now,
            last_used_ip=(ip_address or "")[:64] or None,
        )
    )
    db.commit()
    if result.rowcount != 1:
        return None
    db.refresh(row)
    security_events.record(
        "portfolio.share_used",
        actor_id=row.user_id,
        actor_username=None,
        target_type="portfolio_share",
        target_id=row.id,
        ip_address=ip_address,
        detail={"use_count": row.use_count, "single_use": row.single_use},
    )
    return row


def revoke_share(db: Session, user: User, share_id: int) -> bool:
    row = (
        db.query(PortfolioShare)
        .filter(PortfolioShare.id == share_id, PortfolioShare.user_id == user.id)
        .first()
    )
    if row is None:
        return False
    row.revoked_at = _now()
    db.commit()
    security_events.record(
        "portfolio.share_revoked",
        actor=user,
        target_type="portfolio_share",
        target_id=row.id,
    )
    return True


def list_shares(db: Session, user: User) -> list[PortfolioShare]:
    return (
        db.query(PortfolioShare)
        .filter(PortfolioShare.user_id == user.id)
        .order_by(PortfolioShare.id.desc())
        .limit(100)
        .all()
    )


def share_payload(row: PortfolioShare) -> dict:
    return {
        "id": row.id,
        "label": row.label,
        "audience": row.audience,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        "revoked_at": row.revoked_at.isoformat() if row.revoked_at else None,
        "single_use": row.single_use,
        "max_uses": row.max_uses,
        "use_count": row.use_count,
        "last_used_at": row.last_used_at.isoformat() if row.last_used_at else None,
        "active": row.revoked_at is None and row.expires_at > _now(),
    }
