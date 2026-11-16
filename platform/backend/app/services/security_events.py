"""Append-only security, audit, and privacy event store.

The store answers three operational questions:

* **security** - who tried to authenticate, escalate, or reach a denied action?
* **audit** - who changed a role, setting, record, or configuration?
* **privacy** - who accessed, exported, revoked, or erased personal data?

Every write is one INSERT. PostgreSQL row-level security removes UPDATE and
DELETE capability, so an operator with the application credentials cannot
rewrite evidence. Reads are tenant-scoped: a system administrator sets the
``ocr.system_admin`` GUC; an institution user sees only its own institution and
platform-wide events.
"""

from __future__ import annotations

import json
import logging
import re
from contextvars import ContextVar
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database import SessionLocal, engine
from app.models import SecurityEvent, User
from app.security.tenant import get_tenant as _get_tenant
from app.security.tenant import set_tenant as _set_tenant

logger = logging.getLogger(__name__)

CATEGORIES = frozenset({"security", "audit", "privacy"})
SEVERITIES = frozenset({"info", "notice", "warning", "critical"})
OUTCOMES = frozenset({"success", "failure", "denied", "error"})

TRUTHY = {"true", "1", "yes", "on", "enabled"}
_SENSITIVE_KEY = re.compile(
    r"(?:pass(?:word|wd)?|secret|token|api[_-]?key|credential|private[_-]?key|authorization)",
    re.IGNORECASE,
)
_DEFAULT_DETAIL_LIMIT = 8000

# A compact event vocabulary keeps dashboards and alerts stable. New call sites
# may use a dotted type from the same namespace.
EVENT_TYPES = {
    "auth.login": ("security", "notice"),
    "auth.login_failed": ("security", "warning"),
    "auth.mfa_failed": ("security", "warning"),
    "auth.mfa_locked": ("security", "warning"),
    "auth.mfa_enabled": ("security", "notice"),
    "auth.mfa_disabled": ("security", "warning"),
    "auth.mfa_reset": ("security", "critical"),
    "auth.recovery_codes_generated": ("security", "notice"),
    "auth.recovery_codes_expired": ("security", "warning"),
    "auth.recovery_code_used": ("security", "warning"),
    "auth.password_changed": ("security", "notice"),
    "auth.password_reset": ("security", "notice"),
    "auth.password_rehashed": ("security", "info"),
    "auth.registered": ("security", "info"),
    "auth.account_locked": ("security", "warning"),
    "auth.reauthenticated": ("security", "notice"),
    "auth.reauth_failed": ("security", "warning"),
    "auth.refresh_rotated": ("security", "info"),
    "auth.refresh_invalid": ("security", "warning"),
    "auth.refresh_reuse": ("security", "critical"),
    "auth.session_created": ("security", "info"),
    "auth.session_revoked": ("security", "notice"),
    "auth.denied": ("security", "warning"),
    "authz.denied": ("security", "warning"),
    "rbac.role_granted": ("audit", "warning"),
    "rbac.role_revoked": ("audit", "warning"),
    "rbac.permissions_changed": ("audit", "warning"),
    "service_identity.created": ("audit", "warning"),
    "service_identity.revoked": ("audit", "warning"),
    "service_identity.auth_failed": ("security", "warning"),
    "break_glass.requested": ("security", "notice"),
    "break_glass.approved": ("security", "warning"),
    "break_glass.used": ("security", "critical"),
    "break_glass.revoked": ("security", "warning"),
    "break_glass.reviewed": ("audit", "notice"),
    "break_glass.expired": ("security", "notice"),
    "security.alert": ("security", "warning"),
    "consent.granted": ("privacy", "notice"),
    "consent.revoked": ("privacy", "warning"),
    "privacy.exported": ("privacy", "notice"),
    "privacy.deletion_requested": ("privacy", "warning"),
    "privacy.revocation_executed": ("privacy", "notice"),
    "export.allowed": ("audit", "info"),
    "export.denied": ("security", "warning"),
    "portfolio.share_created": ("privacy", "notice"),
    "portfolio.share_used": ("privacy", "notice"),
    "portfolio.share_revoked": ("privacy", "notice"),
    "security.events_read": ("audit", "info"),
    "settings.change_applied": ("audit", "notice"),
    "settings.change_reverted": ("audit", "warning"),
    "production.cutover": ("security", "critical"),
    "production.cutover_denied": ("security", "critical"),
    "http.denied": ("security", "warning"),
}

_REQUEST_RECORDED: ContextVar[bool] = ContextVar("ocr_security_event_recorded", default=False)


def set_tenant_context(institution_id: str | None, *, system_admin: bool = False) -> None:
    _set_tenant(institution_id, system_admin=system_admin)


def get_tenant_context() -> tuple[str | None, bool]:
    return _get_tenant()


def clear_tenant_context() -> None:
    _set_tenant(None, system_admin=False)
    _REQUEST_RECORDED.set(False)


def mark_request_recorded() -> None:
    _REQUEST_RECORDED.set(True)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: ("[redacted]" if _SENSITIVE_KEY.search(str(key)) else _redact(item))
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    return value


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _setting(db: Session, key: str, default: str) -> str:
    try:
        from app.services import settings_service

        return (
            settings_service.get_setting_fresh(db, key, default) or default
        ).strip()
    except Exception:
        return default


def _truthy(value: str, default: bool = False) -> bool:
    text_value = (value or "").strip().lower()
    return text_value in TRUTHY if text_value else default


def _event_defaults(event_type: str) -> tuple[str, str]:
    return EVENT_TYPES.get(event_type, ("audit", "info"))


def record(
    event_type: str,
    *,
    category: str | None = None,
    severity: str | None = None,
    outcome: str = "success",
    actor: User | None = None,
    actor_id: int | None = None,
    actor_username: str | None = None,
    actor_role: str | None = None,
    institution_id: str | None = None,
    target_type: str | None = None,
    target_id: int | str | None = None,
    target_label: str | None = None,
    action: str | None = None,
    resource: str | None = None,
    method: str | None = None,
    path: str | None = None,
    status_code: int | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
    detail: dict[str, Any] | None = None,
    session: Session | None = None,
    enabled: bool | None = None,
) -> SecurityEvent | None:
    """Insert one event. This function never breaks the caller's action.

    Pass ``session`` only when the caller already owns the transaction and wants
    the event to share its commit. Otherwise a short-lived session commits the
    event independently so a later rollback cannot erase the evidence.
    """
    default_category, default_severity = _event_defaults(event_type)
    category = category or default_category
    severity = severity or default_severity
    if category not in CATEGORIES:
        category = "audit"
    if severity not in SEVERITIES:
        severity = "info"
    if outcome not in OUTCOMES:
        outcome = "success"

    own_session = session is None
    db = session or SessionLocal()
    try:
        if enabled is None:
            enabled = _truthy(_setting(db, "security_event_store_enabled", "true"), True)
        if not enabled:
            return None

        if actor is not None:
            actor_id = getattr(actor, "id", actor_id)
            actor_username = getattr(actor, "username", actor_username)
            actor_role = getattr(actor, "role", actor_role)
            institution_id = getattr(actor, "institution_id", institution_id)
        if institution_id is None:
            tenant, system_admin = get_tenant_context()
            if tenant and not system_admin:
                institution_id = tenant

        payload = json.dumps(_redact(detail or {}), default=str, sort_keys=True)
        if len(payload) > _DEFAULT_DETAIL_LIMIT:
            payload = json.dumps(
                {"truncated": True, "preview": payload[:_DEFAULT_DETAIL_LIMIT]}
            )

        row = SecurityEvent(
            category=category,
            event_type=event_type,
            severity=severity,
            outcome=outcome,
            action=(action or event_type)[:120],
            actor_id=actor_id,
            actor_username=(actor_username or "")[:120] or None,
            actor_role=(actor_role or "")[:32] or None,
            institution_id=(str(institution_id)[:64] if institution_id else None),
            target_type=(target_type or "")[:40] or None,
            target_id=(str(target_id)[:64] if target_id is not None else None),
            target_label=(target_label or "")[:200] or None,
            resource=(resource or "")[:300] or None,
            method=(method or "")[:10] or None,
            path=(path or "")[:300] or None,
            status_code=status_code,
            ip_address=(ip_address or "")[:64] or None,
            user_agent=(user_agent or "")[:300] or None,
            request_id=(request_id or "")[:64] or None,
            detail=payload,
        )
        db.add(row)
        if own_session:
            db.commit()
            db.refresh(row)
        else:
            db.flush()
        return row
    except Exception:
        if own_session:
            db.rollback()
        # Fallback evidence trail if the database write fails. This is not a
        # substitute for the store, but it keeps the action visible in logs.
        logger.exception("Security event store write failed: %s", event_type)
        return None
    finally:
        if own_session:
            db.close()


def resolve_request_user(request: Request, db: Session) -> User | None:
    header = request.headers.get("authorization") or ""
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    token = token.strip()
    try:
        if token.startswith("ocr_svc_"):
            from app.services.service_identities import resolve_token

            return resolve_token(db, token)
        from app.auth import _decode_token, get_user_by_username

        payload = _decode_token(token, db)
        user = get_user_by_username(db, username=payload.get("sub"))
        if user is not None:
            from app.services import auth_sessions

            auth_sessions.bind_user(db, user, payload)
        return user
    except Exception:
        return None


def request_metadata(request: Request) -> dict[str, Any]:
    client_ip = request.client.host if request.client else None
    return {
        "method": request.method,
        "path": request.url.path,
        "ip_address": client_ip,
        "user_agent": request.headers.get("user-agent"),
        "request_id": request.headers.get("x-request-id"),
    }


def record_request(
    request: Request,
    *,
    event_type: str,
    outcome: str = "success",
    status_code: int | None = None,
    category: str | None = None,
    severity: str | None = None,
    actor: User | None = None,
    target_type: str | None = None,
    target_id: int | str | None = None,
    action: str | None = None,
    detail: dict[str, Any] | None = None,
    session: Session | None = None,
) -> SecurityEvent | None:
    """Record an event with request metadata and actor resolution."""
    db = session or SessionLocal()
    try:
        user = actor or resolve_request_user(request, db)
        row = record(
            event_type,
            outcome=outcome,
            status_code=status_code,
            category=category,
            severity=severity,
            actor=user,
            target_type=target_type,
            target_id=target_id,
            action=action,
            detail=detail,
            session=session,
            **request_metadata(request),
        )
        mark_request_recorded()
        return row
    finally:
        if session is None:
            db.close()


# --- PostgreSQL row-level security -----------------------------------------


def ensure_rls(bind=None) -> bool:
    """Enable append-only, tenant-scoped RLS for ``security_events``.

    The function is idempotent and PostgreSQL-only. It returns False when RLS
    cannot be installed (for example SQLite in a unit test).
    """
    bind = bind or engine
    if bind.dialect.name != "postgresql":
        return False
    statements = (
        "ALTER TABLE security_events ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE security_events FORCE ROW LEVEL SECURITY",
        "DROP POLICY IF EXISTS security_events_insert ON security_events",
        "DROP POLICY IF EXISTS security_events_select ON security_events",
        "DROP POLICY IF EXISTS security_events_no_update ON security_events",
        "DROP POLICY IF EXISTS security_events_no_delete ON security_events",
        "CREATE POLICY security_events_insert ON security_events "
        "FOR INSERT WITH CHECK (true)",
        "CREATE POLICY security_events_select ON security_events FOR SELECT USING ("
        "current_setting('ocr.system_admin', true) = 'true' "
        "OR institution_id IS NULL "
        "OR institution_id = NULLIF(current_setting('ocr.institution_id', true), ''))",
        "CREATE POLICY security_events_no_update ON security_events "
        "FOR UPDATE USING (false) WITH CHECK (false)",
        "CREATE POLICY security_events_no_delete ON security_events "
        "FOR DELETE USING (false)",
        "REVOKE UPDATE, DELETE ON security_events FROM PUBLIC",
    )
    with bind.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
        is_superuser = conn.execute(
            text("SELECT current_setting('is_superuser') = 'on'")
        ).scalar()
    if is_superuser:
        logger.warning(
            "The application database role is a superuser; PostgreSQL RLS is "
            "bypassed. Use a non-superuser runtime role in production."
        )
    logger.info("Security event store RLS enabled (append-only, tenant-scoped)")
    return True


def set_rls_context(db: Session, *, institution_id: str | None, system_admin: bool) -> None:
    """Apply the tenant GUCs to the current transaction."""
    if db.bind is None or db.bind.dialect.name != "postgresql":
        return
    db.execute(
        text(
            "SELECT set_config('ocr.institution_id', :institution_id, true), "
            "set_config('ocr.system_admin', :system_admin, true)"
        ),
        {
            "institution_id": institution_id or "",
            "system_admin": "true" if system_admin else "false",
        },
    )


def _viewer_context(viewer: User | None) -> tuple[str | None, bool]:
    if viewer is None:
        return None, False
    institution = getattr(viewer, "institution_id", None)
    return institution, (getattr(viewer, "role", "") or "") == "admin"


def _scoped_query(db: Session, viewer: User | None):
    institution, system_admin = _viewer_context(viewer)
    set_rls_context(db, institution_id=institution, system_admin=system_admin)
    return db.query(SecurityEvent)


def query_events(
    db: Session,
    *,
    viewer: User | None,
    category: str | None = None,
    event_type: str | None = None,
    severity: str | None = None,
    outcome: str | None = None,
    actor_id: int | None = None,
    institution_id: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[SecurityEvent]:
    query = _scoped_query(db, viewer)
    if category:
        query = query.filter(SecurityEvent.category == category)
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    if outcome:
        query = query.filter(SecurityEvent.outcome == outcome)
    if actor_id is not None:
        query = query.filter(SecurityEvent.actor_id == actor_id)
    if institution_id:
        query = query.filter(SecurityEvent.institution_id == institution_id)
    if since:
        query = query.filter(SecurityEvent.occurred_at >= since)
    if until:
        query = query.filter(SecurityEvent.occurred_at <= until)
    if search:
        like = f"%{search.strip()}%"
        query = query.filter(
            SecurityEvent.event_type.ilike(like)
            | SecurityEvent.action.ilike(like)
            | SecurityEvent.actor_username.ilike(like)
            | SecurityEvent.target_label.ilike(like)
            | SecurityEvent.path.ilike(like)
        )
    return (
        query.order_by(SecurityEvent.id.desc())
        .offset(max(0, offset))
        .limit(max(1, min(limit, 500)))
        .all()
    )


def summary(db: Session, *, viewer: User | None, days: int = 30) -> dict[str, Any]:
    from sqlalchemy import func

    since = _now() - timedelta(days=max(1, min(days, 365)))
    base = _scoped_query(db, viewer).filter(SecurityEvent.occurred_at >= since)

    def _counts(column) -> dict[str, int]:
        rows = (
            base.with_entities(column, func.count(SecurityEvent.id))
            .group_by(column)
            .all()
        )
        return {str(key): int(count) for key, count in rows}

    by_category = {key: 0 for key in sorted(CATEGORIES)}
    by_category.update(_counts(SecurityEvent.category))
    by_severity = {key: 0 for key in sorted(SEVERITIES)}
    by_severity.update(_counts(SecurityEvent.severity))
    by_outcome = {key: 0 for key in sorted(OUTCOMES)}
    by_outcome.update(_counts(SecurityEvent.outcome))

    top_rows = (
        base.with_entities(
            SecurityEvent.event_type, func.count(SecurityEvent.id).label("count")
        )
        .group_by(SecurityEvent.event_type)
        .order_by(func.count(SecurityEvent.id).desc())
        .limit(10)
        .all()
    )
    return {
        "window_days": days,
        "total": int(base.count()),
        "by_category": by_category,
        "by_severity": by_severity,
        "by_outcome": by_outcome,
        "top_event_types": [
            {"event_type": key, "count": int(count)} for key, count in top_rows
        ],
        "last_event_at": base.with_entities(
            func.max(SecurityEvent.occurred_at)
        ).scalar(),
    }


# --- HTTP coverage ----------------------------------------------------------

_PRIVACY_PREFIXES = (
    "/api/consent",
    "/api/privacy",
    "/api/auth/export",
    "/api/auth/delete-account",
    "/api/profile/portfolio",
    "/api/profile/career-dossier",
    "/api/profile/snapshots",
    "/api/profile/transcript",
)
_SECURITY_PREFIXES = (
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/change-password",
    "/api/auth/forgot",
    "/api/auth/reset",
    "/api/auth/mfa",
    "/api/auth/sessions",
    "/api/auth/impersonate",
    "/api/setup",
    "/api/identity",
    "/api/admin/security",
    "/api/admin/system/backups",
    "/api/admin/users/export",
)
_AUDIT_PREFIXES = (
    "/api/admin",
    "/api/exercises/import",
    "/api/exercises/export",
    "/api/instructor/labs",
    "/api/reports",
    "/api/analytics",
    "/api/courses",
    "/api/lti",
    "/api/dna",
    "/api/cyber-dna",
)
_READ_SENSITIVE = ("export", "download", "backup", "report", "audit", "security", "break-glass", "sessions")


def _category_for(path: str, status_code: int) -> str:
    if any(path.startswith(prefix) for prefix in _PRIVACY_PREFIXES):
        return "privacy"
    if status_code in {401, 403} or any(path.startswith(prefix) for prefix in _SECURITY_PREFIXES):
        return "security"
    return "audit"


def is_sensitive_request(request: Request, status_code: int = 200) -> bool:
    path = request.url.path
    if not path.startswith("/api/"):
        return False
    if request.method in {"OPTIONS", "HEAD"}:
        return False
    if path in {"/api/health", "/api/version", "/api/auth/me"}:
        return False
    if any(path.startswith(prefix) for prefix in _PRIVACY_PREFIXES + _SECURITY_PREFIXES):
        return True
    if status_code in {401, 403}:
        return True
    if any(path.startswith(prefix) for prefix in _AUDIT_PREFIXES):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            return True
        return any(token in path.lower() for token in _READ_SENSITIVE)
    return False


def record_http(request: Request, status_code: int) -> None:
    """Best-effort coverage for sensitive requests.

    Explicit call sites record richer events and set the context marker so this
    middleware does not duplicate them.
    """
    if _REQUEST_RECORDED.get():
        return
    if not is_sensitive_request(request, status_code):
        return
    category = _category_for(request.url.path, status_code)
    if status_code in {401, 403}:
        event_type = "http.denied" if category == "security" else "authz.denied"
        outcome = "denied"
        severity = "warning"
    elif status_code >= 500:
        event_type = "http.error"
        outcome = "error"
        severity = "warning"
    elif status_code >= 400:
        event_type = "http.rejected"
        outcome = "failure"
        severity = "notice"
    else:
        event_type = "http.sensitive_request"
        outcome = "success"
        severity = "info"
    db = SessionLocal()
    try:
        if not _truthy(_setting(db, "security_event_http_logging", "true"), True):
            return
        user = resolve_request_user(request, db)
        # A sync admin route writes `admin.action` through log_admin_action in a
        # worker thread, where the request context marker cannot propagate back
        # to this middleware. Avoid a duplicate generic event for the same
        # actor/IP within a short window.
        if (
            user is not None
            and request.method in {"POST", "PUT", "PATCH", "DELETE"}
            and request.url.path.startswith("/api/admin")
        ):
            recent = (
                db.query(SecurityEvent)
                .filter(
                    SecurityEvent.event_type == "admin.action",
                    SecurityEvent.actor_id == user.id,
                    SecurityEvent.ip_address
                    == (request.client.host if request.client else None),
                    SecurityEvent.occurred_at >= _now() - timedelta(seconds=10),
                )
                .first()
            )
            if recent is not None:
                return
        record(
            event_type,
            category=category,
            severity=severity,
            outcome=outcome,
            actor=user,
            status_code=status_code,
            session=db,
            **request_metadata(request),
        )
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Security event HTTP coverage failed")
    finally:
        db.close()
