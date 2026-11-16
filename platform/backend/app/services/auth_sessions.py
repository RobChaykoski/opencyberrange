"""Server-side login sessions and rotating refresh tokens.

Access tokens are short-lived bearer credentials that carry a session id. The
session stores the tenant captured at login, the MFA/reauthentication timestamps,
and the device metadata. Refresh tokens are opaque, hashed, single-use values
inside a rotation family. Reusing a rotated token revokes the whole family and
the session, which is the standard reuse-detection response to token theft.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models import AuthSession, RefreshToken, User

REFRESH_PREFIX = "ocr_rt"
TRUTHY = {"true", "1", "yes", "on", "enabled"}


class RefreshReuse(Exception):
    """A refresh token that had already been rotated was presented again."""


class RefreshInvalid(Exception):
    """The refresh token is unknown, expired, revoked, or malformed."""


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _client_meta(request) -> tuple[str | None, str | None]:
    if request is None:
        return None, None
    ip = request.client.host if getattr(request, "client", None) else None
    user_agent = request.headers.get("user-agent") if hasattr(request, "headers") else None
    return (ip or "")[:64] or None, (user_agent or "")[:300] or None


def _session_days() -> int:
    try:
        from app.database import SessionLocal
        from app.services import settings_service

        db = SessionLocal()
        try:
            value = settings_service.get_setting_fresh(
                db, "refresh_token_days", str(settings.REFRESH_TOKEN_DAYS)
            )
        finally:
            db.close()
        return max(1, min(int(value), 365))
    except Exception:
        return max(1, min(settings.REFRESH_TOKEN_DAYS, 365))


def create_session(
    db: Session,
    user: User,
    *,
    request=None,
    mfa_verified: bool = False,
    created_by: str = "login",
) -> AuthSession:
    now = _now()
    ip, user_agent = _client_meta(request)
    row = AuthSession(
        id=str(uuid.uuid4()),
        user_id=user.id,
        institution_id=getattr(user, "institution_id", "default") or "default",
        created_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(days=_session_days()),
        ip_address=ip,
        user_agent=user_agent,
        mfa_verified_at=now if mfa_verified else None,
        reauth_at=now,
        created_by=created_by,
    )
    # Keep a bounded number of active sessions. The oldest session is revoked
    # rather than silently allowing unlimited concurrent logins.
    active = (
        db.query(AuthSession)
        .filter(
            AuthSession.user_id == user.id,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > now,
        )
        .order_by(AuthSession.created_at.asc())
        .all()
    )
    limit = max(1, int(settings.SESSION_MAX_PER_USER))
    for old in active[: max(0, len(active) - limit + 1)]:
        old.revoked_at = now
        old.revoked_reason = "session_limit"
        revoke_family(db, old.id, "session_limit", commit=False)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_active_session(db: Session, session_id: str | None) -> AuthSession | None:
    if not session_id:
        return None
    row = db.get(AuthSession, str(session_id))
    if row is None:
        return None
    if row.revoked_at is not None or row.expires_at <= _now():
        return None
    return row


def touch(db: Session, session: AuthSession) -> None:
    now = _now()
    if session.last_seen_at is None or (now - session.last_seen_at) >= timedelta(minutes=5):
        session.last_seen_at = now
        try:
            db.commit()
        except Exception:
            db.rollback()


def bind_user(
    db: Session, user: User, payload: dict
) -> tuple[AuthSession | None, str | None]:
    """Validate the token's session claim and attach it to the user object.

    Returns ``(session, error)``. Legacy tokens without a ``sid`` claim are
    accepted only until their short access-token lifetime expires; they do not
    satisfy a reauthentication check.
    """
    if payload.get("imp"):
        return None, None
    session_id = payload.get("sid")
    if not session_id:
        return None, None
    session = get_active_session(db, session_id)
    if session is None or session.user_id != user.id:
        return None, "session_expired"
    if (session.institution_id or "default") != (
        getattr(user, "institution_id", "default") or "default"
    ):
        revoke_session(db, session, "tenant_changed")
        return None, "tenant_changed"
    user._auth_session_id = session.id
    user._auth_session = session
    touch(db, session)
    return session, None


def issue_refresh(
    db: Session,
    session: AuthSession,
    user: User,
    *,
    request=None,
    family_id: str | None = None,
) -> tuple[RefreshToken, str]:
    secret = secrets.token_urlsafe(32)
    row = RefreshToken(
        jti=str(uuid.uuid4()),
        session_id=session.id,
        user_id=user.id,
        family_id=family_id or str(uuid.uuid4()),
        token_hash=_hash(secret),
        institution_id=session.institution_id,
        expires_at=session.expires_at,
        ip_address=_client_meta(request)[0],
        user_agent=_client_meta(request)[1],
    )
    db.add(row)
    db.flush()
    raw = f"{REFRESH_PREFIX}_{row.id}_{secret}"
    db.commit()
    db.refresh(row)
    return row, raw


def _parse(raw: str) -> tuple[int, str]:
    if not raw or not raw.startswith(REFRESH_PREFIX + "_"):
        raise RefreshInvalid("malformed")
    try:
        _, _, token_id, secret = raw.split("_", 3)
        return int(token_id), secret
    except (TypeError, ValueError) as exc:
        raise RefreshInvalid("malformed") from exc


def rotate_refresh(db: Session, raw: str, *, request=None) -> dict:
    """Consume one refresh token and issue the next pair.

    Raises :class:`RefreshReuse` when a rotated token is replayed. The caller
    turns that into a 401 and the family is already revoked.
    """
    token_id, secret = _parse(raw)
    row = (
        db.query(RefreshToken)
        .filter(RefreshToken.id == token_id)
        .with_for_update()
        .first()
    )
    if row is None:
        raise RefreshInvalid("unknown")
    if row.revoked_at is not None or row.rotated_at is not None:
        now = _now()
        row.reuse_detected_at = now
        try:
            db.commit()
        except Exception:
            db.rollback()
        session = get_active_session(db, row.session_id)
        if session is not None:
            revoke_session(db, session, "refresh_reuse", commit=False)
        revoke_family(db, row.family_id, "refresh_reuse")
        raise RefreshReuse("reused")
    if row.expires_at <= _now():
        raise RefreshInvalid("expired")
    if not hmac.compare_digest(row.token_hash, _hash(secret)):
        raise RefreshInvalid("bad_secret")
    session = get_active_session(db, row.session_id)
    if session is None:
        raise RefreshInvalid("session_expired")
    user = db.get(User, row.user_id)
    if user is None or not user.is_active or not user.is_approved:
        raise RefreshInvalid("account_inactive")

    row.rotated_at = _now()
    replacement, raw_token = issue_refresh(
        db,
        session,
        user,
        request=request,
        family_id=row.family_id,
    )
    row.replaced_by_jti = replacement.jti
    db.commit()
    touch(db, session)
    return {
        "user": user,
        "session": session,
        "refresh": replacement,
        "refresh_token": raw_token,
    }


def revoke_session(
    db: Session, session: AuthSession, reason: str = "revoked", *, commit: bool = True
) -> None:
    if session.revoked_at is None:
        session.revoked_at = _now()
        session.revoked_reason = reason[:64]
    revoke_family(db, session.id, reason, commit=False)
    if commit:
        db.commit()


def revoke_family(
    db: Session, family_or_session: str, reason: str = "revoked", *, commit: bool = True
) -> int:
    now = _now()
    rows = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.revoked_at.is_(None),
            (RefreshToken.family_id == family_or_session)
            | (RefreshToken.session_id == family_or_session),
        )
        .all()
    )
    for row in rows:
        row.revoked_at = now
    if commit:
        db.commit()
    return len(rows)


def revoke_all_for_user(db: Session, user_id: int, reason: str = "revoke_all") -> int:
    now = _now()
    sessions = (
        db.query(AuthSession)
        .filter(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
        .all()
    )
    for session in sessions:
        session.revoked_at = now
        session.revoked_reason = reason[:64]
        revoke_family(db, session.id, reason, commit=False)
    db.commit()
    return len(sessions)


def list_sessions(db: Session, user_id: int) -> list[dict]:
    now = _now()
    rows = (
        db.query(AuthSession)
        .filter(
            AuthSession.user_id == user_id,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > now,
        )
        .order_by(AuthSession.last_seen_at.desc())
        .all()
    )
    return [
        {
            "id": row.id,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "last_seen_at": row.last_seen_at.isoformat() if row.last_seen_at else None,
            "expires_at": row.expires_at.isoformat() if row.expires_at else None,
            "ip_address": row.ip_address,
            "user_agent": row.user_agent,
            "mfa_verified": row.mfa_verified_at is not None,
            "reauth_at": row.reauth_at.isoformat() if row.reauth_at else None,
        }
        for row in rows
    ]


def recent_reauth(session: AuthSession | None, max_minutes: int) -> bool:
    if session is None or session.reauth_at is None:
        return False
    stamp = session.reauth_at
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(timezone.utc).replace(tzinfo=None)
    return stamp >= _now() - timedelta(minutes=max(1, max_minutes))


def mark_reauth(db: Session, session: AuthSession) -> None:
    session.reauth_at = _now()
    db.commit()
