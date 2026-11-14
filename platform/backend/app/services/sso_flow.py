"""Replica-safe SSO flow state, one-time tickets, and login payloads.

The state and ticket rows live in PostgreSQL, so a login can start on one API
replica and finish on another. No process-local session is used.
"""

from __future__ import annotations

import logging
import secrets
from datetime import timedelta
from urllib.parse import urlencode

from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.config import settings
from app.models import (
    IdentityProvider,
    SsoLoginState,
    SsoLoginTicket,
    SsoSession,
    User,
)
from app.services.activity import EventTypes, log_activity
from app.services.achievements import (
    check_learning_achievements,
    check_login_streak_achievements,
)
from app.services.external_identity import SSOError, utcnow

logger = logging.getLogger(__name__)


def public_base_url() -> str:
    """Return the stable external origin used to build callback URLs."""
    configured = (settings.PUBLIC_BASE_URL or "").strip()
    if configured:
        return configured.rstrip("/")
    host = (settings.SERVER_PUBLIC_HOST or "localhost").strip()
    if host.startswith(("http://", "https://")):
        return host.rstrip("/")
    return f"https://{host}"


def frontend_base_url() -> str:
    configured = (settings.FRONTEND_BASE_URL or "").strip()
    return configured.rstrip("/") if configured else public_base_url()


def tls_verify() -> bool:
    """TLS verification for outbound IdP calls.

    Verification stays on in production. The opt-in flag exists for local
    development, where the platform is served behind a self-signed certificate.
    """
    return not settings.SSO_ALLOW_INSECURE_HTTP


def sanitize_return_to(value: str | None) -> str:
    value = (value or "").strip()
    if not value.startswith("/") or value.startswith("//"):
        return "/dashboard"
    return value[:500]


def create_login_ticket(
    db: Session,
    *,
    user: User,
    provider: IdentityProvider,
    return_to: str,
) -> str:
    ticket = secrets.token_urlsafe(32)
    db.add(
        SsoLoginTicket(
            ticket=ticket,
            user_id=user.id,
            provider_id=provider.id,
            return_to=sanitize_return_to(return_to),
            expires_at=utcnow() + timedelta(seconds=settings.SSO_TICKET_TTL_SECONDS),
        )
    )
    db.commit()
    return ticket


def consume_login_ticket(db: Session, ticket: str) -> SsoLoginTicket:
    now = utcnow()
    updated = (
        db.query(SsoLoginTicket)
        .filter(
            SsoLoginTicket.ticket == ticket,
            SsoLoginTicket.consumed_at.is_(None),
            SsoLoginTicket.expires_at >= now,
        )
        .update({SsoLoginTicket.consumed_at: now}, synchronize_session=False)
    )
    db.commit()
    if updated != 1:
        raise SSOError("This sign-in link has expired or was already used.")
    return db.query(SsoLoginTicket).filter(SsoLoginTicket.ticket == ticket).first()


def consume_login_state(db: Session, state: str, provider_id: int) -> SsoLoginState:
    now = utcnow()
    updated = (
        db.query(SsoLoginState)
        .filter(
            SsoLoginState.state == state,
            SsoLoginState.provider_id == provider_id,
            SsoLoginState.consumed_at.is_(None),
            SsoLoginState.expires_at >= now,
        )
        .update({SsoLoginState.consumed_at: now}, synchronize_session=False)
    )
    db.commit()
    if updated != 1:
        raise SSOError("This sign-in request has expired or was already used.")
    return db.query(SsoLoginState).filter(SsoLoginState.state == state).first()


def create_flow_state(
    db: Session,
    *,
    provider: IdentityProvider,
    return_to: str,
    nonce: str = "",
    code_verifier: str = "",
    redirect_uri: str = "",
) -> str:
    """Create a shared state row and return its random state token.

    OIDC uses ``nonce`` for the ID-token nonce and ``code_verifier`` for PKCE.
    SAML uses ``nonce`` for the AuthnRequest ID and stores the ACS URL in
    ``redirect_uri``. LDAP performs a single request and does not need state.
    """
    state = secrets.token_urlsafe(32)
    db.add(
        SsoLoginState(
            state=state,
            provider_id=provider.id,
            nonce=nonce or "",
            code_verifier=code_verifier or "",
            redirect_uri=redirect_uri or "",
            return_to=sanitize_return_to(return_to),
            expires_at=utcnow() + timedelta(seconds=settings.SSO_STATE_TTL_SECONDS),
        )
    )
    db.commit()
    return state


def cleanup_expired(db: Session) -> None:
    now = utcnow()
    db.query(SsoLoginState).filter(
        SsoLoginState.expires_at < now - timedelta(days=1)
    ).delete(synchronize_session=False)
    db.query(SsoLoginTicket).filter(
        SsoLoginTicket.expires_at < now - timedelta(days=1)
    ).delete(synchronize_session=False)
    db.query(SsoSession).filter(SsoSession.expires_at < now).delete(
        synchronize_session=False
    )
    db.commit()


def record_login(db: Session, user: User, client_ip: str | None) -> None:
    now = utcnow()
    today = now.date()
    previous_login_day = getattr(user, "last_login_day", None)
    if previous_login_day == today:
        pass
    elif previous_login_day == today - timedelta(days=1):
        user.login_streak = (getattr(user, "login_streak", 0) or 0) + 1
    else:
        user.login_streak = 1
    user.last_login_day = today
    user.last_login_at = now
    user.last_login_ip = client_ip
    db.commit()
    try:
        check_login_streak_achievements(db, user.id, getattr(user, "login_streak", 1) or 1)
        check_learning_achievements(db, user.id)
    except Exception:
        logger.exception("Could not evaluate SSO login achievements for %s", user.username)


def login_payload(user: User, provider_id: int | None = None) -> dict:
    token_data = {"sub": user.username}
    if provider_id is not None:
        token_data["sso_provider_id"] = provider_id
    token = create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "student_id": user.student_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_admin": user.is_admin,
            "is_approved": user.is_approved,
            "is_active": user.is_active,
            "must_change_password": user.must_change_password,
            "timezone": getattr(user, "timezone", None),
            "equipped_title": getattr(user, "equipped_title", None),
        },
    }


def log_sso_login(
    db: Session,
    *,
    provider: IdentityProvider,
    user: User,
    provisioned: bool,
    linked: bool,
    client_ip: str | None,
) -> None:
    log_activity(
        db,
        EventTypes.SSO_LOGIN_SUCCESS,
        actor_id=user.id,
        target_type="identity_provider",
        target_id=provider.id,
        target_label=provider.name,
        detail={"provisioned": provisioned, "linked": linked},
        ip_address=client_ip,
    )
    if provisioned:
        log_activity(
            db,
            EventTypes.SSO_USER_PROVISIONED,
            actor_id=user.id,
            target_type="user",
            target_id=user.id,
            target_label=user.username,
            detail={"provider": provider.name},
            ip_address=client_ip,
        )
    elif linked:
        log_activity(
            db,
            EventTypes.SSO_ACCOUNT_LINKED,
            actor_id=user.id,
            target_type="user",
            target_id=user.id,
            target_label=user.username,
            detail={"provider": provider.name},
            ip_address=client_ip,
        )


def callback_url(params: dict, path: str = "/sso/callback") -> str:
    return f"{frontend_base_url()}{path}?{urlencode(params)}"
