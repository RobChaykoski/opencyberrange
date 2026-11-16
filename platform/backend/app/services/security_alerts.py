"""Threshold alerts over the security event store.

The scheduler calls this periodically. Alerts are written back as
``security.alert`` events, so the same append-only evidence trail and admin
console show the detection, the triggering window, and the actor.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import SecurityEvent, User
from app.services import security_events, settings_service

logger = logging.getLogger(__name__)

TRUTHY = {"true", "1", "yes", "on", "enabled"}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _setting(db: Session, key: str, default: str) -> str:
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


def scan(db: Session, *, minutes: int | None = None) -> list[dict]:
    """Return alert candidates for the current window."""
    window = max(1, min(minutes or _int_setting(db, "security_alert_window_minutes", 15), 1440))
    threshold = max(1, _int_setting(db, "security_alert_threshold", 5))
    since = _now() - timedelta(minutes=window)
    alerts: list[dict] = []

    break_glass = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.event_type == "break_glass.used",
            SecurityEvent.occurred_at >= since,
        )
        .all()
    )
    for row in break_glass:
        alerts.append(
            {
                "signature": f"break_glass:{row.id}",
                "severity": "critical",
                "title": "Break-glass access used",
                "event_type": row.event_type,
                "actor_id": row.actor_id,
                "actor_username": row.actor_username,
                "institution_id": row.institution_id,
                "count": 1,
                "window_minutes": window,
                "detail": row.detail,
            }
        )

    grouped = (
        db.query(
            SecurityEvent.event_type,
            SecurityEvent.actor_id,
            SecurityEvent.ip_address,
            SecurityEvent.institution_id,
            func.count(SecurityEvent.id).label("count"),
        )
        .filter(
            SecurityEvent.occurred_at >= since,
            SecurityEvent.event_type.in_(
                (
                    "auth.login_failed",
                    "auth.mfa_failed",
                    "authz.denied",
                    "http.denied",
                    "export.denied",
                    "service_identity.auth_failed",
                )
            ),
        )
        .group_by(
            SecurityEvent.event_type,
            SecurityEvent.actor_id,
            SecurityEvent.ip_address,
            SecurityEvent.institution_id,
        )
        .all()
    )
    for event_type, actor_id, ip_address, institution_id, count in grouped:
        if count < threshold:
            continue
        alerts.append(
            {
                "signature": f"{event_type}:{actor_id}:{ip_address}:{count}",
                "severity": "critical" if event_type == "export.denied" else "warning",
                "title": f"Repeated {event_type}",
                "event_type": event_type,
                "actor_id": actor_id,
                "actor_username": None,
                "ip_address": ip_address,
                "institution_id": institution_id,
                "count": int(count),
                "window_minutes": window,
                "detail": {"threshold": threshold},
            }
        )
    return alerts


def _already_recorded(db: Session, signature: str, since: datetime) -> bool:
    rows = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.event_type == "security.alert",
            SecurityEvent.occurred_at >= since,
        )
        .all()
    )
    for row in rows:
        try:
            if json.loads(row.detail or "{}").get("signature") == signature:
                return True
        except json.JSONDecodeError:
            continue
    return False


def scan_and_record(db: Session | None = None) -> dict:
    """Scan, deduplicate, and write alert events. Safe to call repeatedly."""
    own = db is None
    session = db or SessionLocal()
    try:
        if not _truthy(_setting(session, "security_alert_enabled", "true"), True):
            return {"alerts": 0, "recorded": 0}
        alerts = scan(session)
        since = _now() - timedelta(
            minutes=max(1, _int_setting(session, "security_alert_window_minutes", 15))
        )
        recorded = 0
        for alert in alerts:
            if _already_recorded(session, alert["signature"], since):
                continue
            actor = None
            if alert.get("actor_id"):
                actor = session.get(User, alert["actor_id"])
            security_events.record(
                "security.alert",
                category="security",
                severity=alert["severity"],
                outcome="failure",
                actor=actor,
                actor_id=alert.get("actor_id"),
                actor_username=alert.get("actor_username"),
                institution_id=alert.get("institution_id"),
                ip_address=alert.get("ip_address"),
                detail={**alert, "detected_at": _now().isoformat()},
                session=session,
            )
            recorded += 1
        if recorded:
            session.commit()
            logger.warning(
                "Security alert scan recorded %d alert(s) over %d minutes",
                recorded,
                since and _int_setting(session, "security_alert_window_minutes", 15),
            )
        return {"alerts": len(alerts), "recorded": recorded}
    except Exception:
        session.rollback()
        logger.exception("Security alert scan failed")
        return {"alerts": 0, "recorded": 0, "error": True}
    finally:
        if own:
            session.close()
