"""Forced reauthentication for high-impact operations.

A login or explicit reauthentication opens a short window. Privacy changes,
role changes, MFA changes, and exports require that window to still be open.
The check is session-bound, so a stolen access token alone cannot perform those
actions after the window closes.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_active_user, verify_password
from app.database import get_db
from app.models import AuthSession, User
from app.services import auth_sessions, mfa, security_events


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _window_minutes(db: Session) -> int:
    from app.services import settings_service

    try:
        value = settings_service.get_setting_fresh(db, "reauth_window_minutes", "15")
        return max(1, min(int(value), 240))
    except (TypeError, ValueError):
        return 15


def session_for_user(db: Session, user: User) -> AuthSession | None:
    session = getattr(user, "_auth_session", None)
    if session is not None:
        return session
    session_id = getattr(user, "_auth_session_id", None)
    if session_id:
        return auth_sessions.get_active_session(db, session_id)
    return None


def is_recent(db: Session, user: User) -> bool:
    session = session_for_user(db, user)
    return auth_sessions.recent_reauth(session, _window_minutes(db))


def verify_credentials(db: Session, user: User, password: str, totp_code: str | None) -> None:
    """Verify the account password and, when enabled, a live second factor."""
    if not verify_password(password, user.hashed_password):
        security_events.record(
            "auth.reauth_failed",
            outcome="denied",
            actor=user,
            target_type="user",
            target_id=user.id,
            detail={"reason": "password"},
        )
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    if not getattr(user, "mfa_enabled", False):
        return
    if not totp_code:
        raise HTTPException(
            status_code=401,
            detail="A current authenticator or recovery code is required.",
            headers={"X-MFA-Required": "true"},
        )
    mfa.assert_mfa_allowed(user, db)
    ok, method = mfa.verify_totp_or_recovery(db, user, totp_code)
    if not ok:
        mfa.record_failure(db, user)
        security_events.record(
            "auth.reauth_failed",
            outcome="denied",
            actor=user,
            target_type="user",
            target_id=user.id,
            detail={"reason": "mfa"},
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticator or recovery code.",
            headers={"X-MFA-Required": "true"},
        )


def mark_reauthenticated(db: Session, user: User, session: AuthSession) -> None:
    auth_sessions.mark_reauth(db, session)
    security_events.record(
        "auth.reauthenticated",
        actor=user,
        target_type="session",
        target_id=session.id,
        detail={"window_minutes": _window_minutes(db)},
    )


def require_recent_reauth(purpose: str):
    """FastAPI dependency for one high-impact operation."""

    def dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> AuthSession:
        session = session_for_user(db, current_user)
        if session is None:
            raise HTTPException(
                status_code=403,
                detail=f"Re-authentication is required before {purpose}.",
                headers={
                    "X-Reauth-Required": "true",
                    "X-Reauth-Purpose": purpose,
                },
            )
        if not auth_sessions.recent_reauth(session, _window_minutes(db)):
            raise HTTPException(
                status_code=403,
                detail=f"Re-authentication is required before {purpose}.",
                headers={
                    "X-Reauth-Required": "true",
                    "X-Reauth-Purpose": purpose,
                },
            )
        return session

    dependency.__reauth_purpose__ = purpose  # type: ignore[attr-defined]
    dependency.__name__ = f"require_recent_reauth[{purpose}]"
    return dependency


def response_requires_reauth(db: Session, user: User, purpose: str) -> bool:
    """Non-raising form for middleware."""
    if user is None:
        return False
    session = session_for_user(db, user)
    if session is None:
        return True
    return not auth_sessions.recent_reauth(session, _window_minutes(db))
