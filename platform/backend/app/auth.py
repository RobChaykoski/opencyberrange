"""
Authentication utilities and dependencies
"""

import logging
import secrets
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import jwt  # PyJWT
from jwt import ExpiredSignatureError
from jwt import InvalidAudienceError
from jwt import InvalidIssuerError
from jwt import InvalidTokenError
from jwt import MissingRequiredClaimError
from jwt import PyJWTError as JWTError
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.config import settings
from app.actor import set_actor

logger = logging.getLogger(__name__)

# Argon2id baseline (OWASP-style: 64 MiB, 3 iterations, 4 lanes). Values are
# explicit so a library default change cannot silently weaken new hashes.
ARGON2_PARAMS = {
    "time_cost": settings.ARGON2_TIME_COST,
    "memory_cost": settings.ARGON2_MEMORY_COST,
    "parallelism": settings.ARGON2_PARALLELISM,
    "hash_len": settings.ARGON2_HASH_LEN,
    "salt_len": settings.ARGON2_SALT_LEN,
}
pwd_context = PasswordHash((Argon2Hasher(**ARGON2_PARAMS), BcryptHasher()))


def password_rehash_due(user: User, db: Session | None = None) -> bool:
    """Return True when the stored hash should be refreshed on login."""
    if not (getattr(user, "hashed_password", "") or "").startswith("$argon2id$"):
        return True
    stamp = getattr(user, "password_rehashed_at", None)
    if stamp is None:
        return True
    days = settings.PASSWORD_REHASH_DAYS
    if db is not None:
        try:
            from app.services import settings_service

            days = int(
                settings_service.get_setting_fresh(
                    db, "password_rehash_days", str(settings.PASSWORD_REHASH_DAYS)
                )
            )
        except (TypeError, ValueError):
            days = settings.PASSWORD_REHASH_DAYS
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - stamp >= timedelta(days=max(1, days))

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_password_hash(password: str) -> str:
    """Hash a password with Argon2id."""
    return pwd_context.hash(password)


def set_user_password(user: User, password: str) -> None:
    """Set a user's password and stamp the current rehash policy."""
    user.hashed_password = get_password_hash(password)
    user.password_rehashed_at = datetime.now(timezone.utc)
    bump_security_version(user)


def bump_security_version(user: User) -> int:
    """Invalidate tokens minted before a security-relevant change."""
    user.security_version = int(getattr(user, "security_version", 1) or 1) + 1
    return user.security_version


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash, whatever scheme produced it."""
    try:
        valid, _ = pwd_context.verify_and_update(plain_password, hashed_password)
        return valid
    except Exception:
        return False


def verify_password_and_upgrade(
    plain_password: str, hashed_password: str
) -> tuple[bool, Optional[str]]:
    """Verify and return an upgraded hash when the stored scheme is legacy.

    ``verify_and_update`` returns ``(valid, new_hash)``; ``new_hash`` is None
    when the stored hash already uses the preferred scheme.
    """
    try:
        return pwd_context.verify_and_update(plain_password, hashed_password)
    except Exception:
        return False, None


PRIVILEGED_PASSWORD_MIN_LENGTH = 14


def validate_privileged_password(password: str) -> Optional[str]:
    """Password policy for instructor/admin accounts.

    Returns an error message when the password is too weak, else None.
    Privileged accounts authenticate from the open internet, so they carry
    a stricter policy than the 8-char student minimum.
    """
    if len(password) < PRIVILEGED_PASSWORD_MIN_LENGTH:
        return (
            f"Instructor/admin passwords must be at least "
            f"{PRIVILEGED_PASSWORD_MIN_LENGTH} characters"
        )
    classes = sum([
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(not c.isalnum() for c in password),
    ])
    if classes < 3:
        return (
            "Instructor/admin passwords need at least three of: lowercase, "
            "uppercase, digit, symbol"
        )
    # Length and character classes are not enough: "Password123456!" still
    # fails here because the base is a common word.
    from app.schemas import _password_policy_error

    return _password_policy_error(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    *,
    token_type: str = "access",
    security_version: int | None = None,
) -> str:
    """Create a JWT with issuer, audience, purpose, and required claims.

    ``type`` keeps access, impersonation, refresh, reset, and portfolio tokens
    from being interchangeable. Platform refresh tokens are opaque and never
    validated by this function.
    """
    now = datetime.now(timezone.utc)
    to_encode = data.copy()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    to_encode.update(
        {
            "exp": expire,
            "nbf": now,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "type": token_type,
            "sec": int(security_version if security_version is not None else data.get("sec", 1)),
        }
    )
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


# ─── Token Revocation (DB-backed) ────────────────────────────────────
# Revocations live in the revoked_tokens table so they apply across every
# uvicorn worker (the old in-process dict was invisible to sibling workers).
# Two row shapes share the table:
#   jti = "<uuid>"                  one specific token is dead
#   jti = "revoke-all:<username>"   tokens issued before revoked_at are dead
# Rows older than the JWT lifetime are pruned opportunistically; by then the
# tokens they refer to have expired on their own.

_REVOKE_ALL_PREFIX = "revoke-all:"


def _revocation_sentinel(username: str) -> str:
    """Sentinel jti for a per-user mass revocation row.

    The jti column is 64 chars and usernames are capped at 50, so the
    truncation guard never fires in practice."""
    return f"{_REVOKE_ALL_PREFIX}{username}"[:64]


def _prune_expired_revocations(db) -> int:
    """Delete revocation rows older than the JWT lifetime plus slack."""
    from app.models import RevokedToken
    cutoff = datetime.now(timezone.utc) - timedelta(
        hours=settings.JWT_EXPIRATION_HOURS,
        seconds=max(0, int(settings.JWT_LEEWAY_SECONDS)) + 3600,
    )
    return db.query(RevokedToken).filter(RevokedToken.revoked_at < cutoff).delete(
        synchronize_session=False
    )


def prune_expired_revocations() -> int:
    """Prune expired revocation rows from the scheduler, not the logout path."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        deleted = _prune_expired_revocations(db)
        db.commit()
        return deleted
    except Exception:
        db.rollback()
        logger.exception("Failed to prune expired token revocations")
        return 0
    finally:
        db.close()


def revoke_token(jti: str, expires_at_epoch: float, user_id: Optional[int] = None) -> None:
    """Persist a token's jti to the revocation table.

    expires_at_epoch is kept for API compatibility; pruning now keys off
    revoked_at instead. user_id is required because the revoked_tokens
    table attributes every row to an account."""
    if user_id is None:
        raise ValueError("revoke_token requires user_id for DB-backed revocation")
    from app.database import SessionLocal
    from app.models import RevokedToken
    db = SessionLocal()
    try:
        if db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is None:
            db.add(RevokedToken(
                jti=jti,
                user_id=user_id,
                revoked_at=datetime.now(timezone.utc),
            ))
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to persist token revocation for jti %s", jti)
        raise
    finally:
        db.close()


def revoke_all_user_tokens(username: str) -> None:
    """Revoke every outstanding token for a user.

    Writes (or refreshes) a per-user sentinel row; tokens whose iat predates
    the sentinel's revoked_at are rejected in _decode_token(). DB-backed, so
    the revocation is visible to all workers immediately."""
    from app.database import SessionLocal
    from app.models import RevokedToken
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            return
        sentinel = _revocation_sentinel(username)
        now = datetime.now(timezone.utc)
        row = db.query(RevokedToken).filter(RevokedToken.jti == sentinel).first()
        if row is None:
            db.add(RevokedToken(jti=sentinel, user_id=user.id, revoked_at=now))
        else:
            row.revoked_at = now
        db.commit()
        from app.services import auth_sessions

        auth_sessions.revoke_all_for_user(db, user.id, "revoke_all_tokens")
    except Exception:
        db.rollback()
        logger.exception("Failed to persist mass revocation for user %s", username)
        raise
    finally:
        db.close()


def is_token_revoked(jti: str) -> bool:
    """Check if a specific token has been revoked by jti."""
    from app.database import SessionLocal
    from app.models import RevokedToken
    db = SessionLocal()
    try:
        return db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is not None
    finally:
        db.close()


def _check_token_revocation(
    username: str,
    jti: Optional[str],
    iat_epoch: float,
    db: Optional[Session] = None,
) -> bool:
    """Return True when the token is revoked, either individually (jti row)
    or by a per-user mass revocation issued after the token's iat.

    Pass the request's session when one is available so authentication does
    not open a second pooled connection on every request. Fails closed: if the
    revocation store errors, the caller receives 503 rather than a token that
    might be revoked."""
    from app.database import SessionLocal
    from app.models import RevokedToken
    keys = [_revocation_sentinel(username)]
    if jti:
        keys.append(jti)
    owns_session = db is None
    if owns_session:
        db = SessionLocal()
    try:
        rows = db.query(RevokedToken).filter(RevokedToken.jti.in_(keys)).all()
        for row in rows:
            if jti and row.jti == jti:
                return True
            if row.jti.startswith(_REVOKE_ALL_PREFIX):
                revoked_at = row.revoked_at
                if revoked_at.tzinfo is None:
                    revoked_at = revoked_at.replace(tzinfo=timezone.utc)
                if iat_epoch < revoked_at.timestamp():
                    return True
        return False
    except Exception as exc:
        logger.error(
            "Revocation check failed; denying authentication (fail-closed)",
            exc_info=True,
        )
        raise RevocationUnavailable("revocation store unavailable") from exc
    finally:
        if owns_session:
            db.close()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


# Account lockout constants. The hard lock is now admin-only; automatic
# throttling is keyed by (username, client IP) so a spray from one address
# cannot lock a known student out everywhere.
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
LOGIN_FAILURE_WINDOW_SECONDS = 15 * 60
LOGIN_BACKOFF_MAX_SECONDS = 60

_login_failures: dict[tuple[str, str], list[float]] = {}
_login_failures_lock = threading.Lock()

# A verified Argon2 hash is needed even for unknown usernames. Computing it
# lazily keeps import cheap while still paying the real verification cost.
_dummy_hash: Optional[str] = None
_dummy_hash_lock = threading.Lock()


def _dummy_verify(password: str) -> None:
    global _dummy_hash
    if _dummy_hash is None:
        with _dummy_hash_lock:
            if _dummy_hash is None:
                _dummy_hash = get_password_hash(secrets.token_urlsafe(16))
    verify_password(password, _dummy_hash)


def _login_key(username: str, ip_address: Optional[str]) -> tuple[str, str]:
    return ((username or "").strip().lower(), ip_address or "unknown")


def _login_failure_record(username: str, ip_address: Optional[str]) -> int:
    """Record a failure and return the current count for this key."""
    now = time.monotonic()
    key = _login_key(username, ip_address)
    with _login_failures_lock:
        entry = _login_failures.get(key)
        if entry and now - entry[0] > LOGIN_FAILURE_WINDOW_SECONDS:
            entry = None
        if entry is None:
            entry = [now, 0.0]
            _login_failures[key] = entry
        entry[1] = int(entry[1]) + 1
        # Keep the map bounded under a distributed spray.
        if len(_login_failures) > 10000:
            for stale in [
                k for k, v in _login_failures.items()
                if now - v[0] > LOGIN_FAILURE_WINDOW_SECONDS
            ]:
                _login_failures.pop(stale, None)
        return int(entry[1])


def _login_retry_after(username: str, ip_address: Optional[str]) -> int:
    """Seconds to wait for this key, or 0 when it is within budget."""
    key = _login_key(username, ip_address)
    now = time.monotonic()
    with _login_failures_lock:
        entry = _login_failures.get(key)
        if not entry or now - entry[0] > LOGIN_FAILURE_WINDOW_SECONDS:
            return 0
        count = int(entry[1])
    if count < MAX_FAILED_ATTEMPTS:
        return 0
    return min(LOGIN_BACKOFF_MAX_SECONDS, 2 ** (count - MAX_FAILED_ATTEMPTS))


def _clear_login_failures(username: str, ip_address: Optional[str]) -> None:
    with _login_failures_lock:
        _login_failures.pop(_login_key(username, ip_address), None)


def authenticate_user(
    db: Session,
    username: str,
    password: str,
    ip_address: Optional[str] = None,
) -> Optional[User]:
    """
    Authenticate a user with username and password.

    Failures are throttled per (username, client IP). The persisted account
    lock remains for administrator-initiated locks only, so spraying a known
    username from one address cannot lock out the real user.

    Args:
        db: Database session
        username: User's username
        password: User's plaintext password
        ip_address: Client address used for failure scoring

    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user_by_username(db, username)
    if not user:
        # Pay the same hashing cost as a real user so timing does not reveal
        # whether the username exists.
        _dummy_verify(password)
        _login_failure_record(username, ip_address)
        return None

    # SSO-provisioned accounts must use the identity provider. Do not reveal
    # the difference between a missing user and an SSO-only account.
    if getattr(user, "password_login_disabled", False):
        _dummy_verify(password)
        _login_failure_record(username, ip_address)
        return None

    # Check if account is locked
    if user.is_locked:
        # Check if lockout period has expired
        if user.locked_at:
            locked_at = user.locked_at
            # Ensure timezone awareness
            if locked_at.tzinfo is None:
                locked_at = locked_at.replace(tzinfo=timezone.utc)
            
            lockout_expires = locked_at + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            
            if datetime.now(timezone.utc) > lockout_expires:
                # Lockout expired, unlock the account
                user.is_locked = False
                user.failed_attempts = 0
                user.locked_at = None
                db.commit()
            else:
                # Still locked - return None without incrementing attempts
                return None
        else:
            # Locked without timestamp (manual lock by admin), don't auto-unlock
            return None
    
    # Verify password (bcrypt legacy hashes are upgraded to Argon2 here)
    valid, upgraded_hash = verify_password_and_upgrade(password, user.hashed_password)
    if not valid:
        # Keep the persisted counter for operator visibility, but never
        # auto-lock the account: the per-IP throttle below is what rejects
        # the attempt. This removes the cross-IP lockout DoS.
        user.failed_attempts = (user.failed_attempts or 0) + 1
        _login_failure_record(username, ip_address)
        db.commit()
        return None
    
    # Successful login - reset failed attempts and upgrade a legacy or stale
    # hash. ``verify_and_update`` handles a scheme change (bcrypt -> Argon2id);
    # ``password_rehash_due`` handles an Argon2id parameter change or an old
    # rehash stamp, so the policy keeps applying after the initial migration.
    _clear_login_failures(username, ip_address)
    if user.failed_attempts and user.failed_attempts > 0:
        user.failed_attempts = 0
        db.commit()
    if upgraded_hash or password_rehash_due(user, db):
        new_hash = upgraded_hash or get_password_hash(password)
        if new_hash != user.hashed_password:
            user.hashed_password = new_hash
            user.password_rehashed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info("Rehashed password for user %s with current Argon2id parameters", user.username)
            try:
                from app.services import security_events

                security_events.record(
                    "auth.password_rehashed",
                    actor=user,
                    target_type="user",
                    target_id=user.id,
                    target_label=user.username,
                    detail={"scheme": "argon2id", "params": ARGON2_PARAMS},
                )
            except Exception:
                logger.exception("Could not record password rehash event")

    return user


_JWT_REQUIRED_CLAIMS = ("sub", "exp", "iat", "nbf", "jti", "iss", "aud", "type", "sec")
_JWT_FORBIDDEN_HEADERS = {"jku", "x5u", "jwk"}


class RevocationUnavailable(RuntimeError):
    """The revocation store could not be queried; authentication must deny."""


def _enforce_revocation(payload: dict, db: Optional[Session]) -> None:
    """Reject a revoked token; deny when the revocation store is unavailable."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        revoked = _check_token_revocation(
            payload["sub"], payload["jti"], payload.get("iat", 0), db=db
        )
    except RevocationUnavailable:
        logger.error("JWT rejected: revocation store unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is temporarily unavailable",
        )
    if revoked:
        raise credentials_exception


def _decode_token(
    token: str,
    db: Optional[Session] = None,
    *,
    expected_types: tuple[str, ...] = ("access",),
    check_revocation: bool = True,
) -> dict:
    """Decode and validate a platform JWT.

    The algorithm is fixed server-side, issuer/audience/purpose are checked,
    all security-critical claims are required, and the revocation store is
    fail-closed. External protocol tokens (OIDC/LTI) use their own validators.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        header = jwt.get_unverified_header(token)
        if set(header) & _JWT_FORBIDDEN_HEADERS:
            raise InvalidTokenError("token header requests an external key")
        if header.get("alg") != settings.JWT_ALGORITHM:
            raise InvalidTokenError("unexpected algorithm")
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            leeway=max(0, int(settings.JWT_LEEWAY_SECONDS)),
            options={"require": list(_JWT_REQUIRED_CLAIMS)},
        )
    except ExpiredSignatureError:
        logger.info("JWT rejected: expired")
        raise credentials_exception
    except MissingRequiredClaimError as exc:
        logger.info("JWT rejected: missing claim %s", exc.claim)
        raise credentials_exception
    except InvalidAudienceError:
        logger.info("JWT rejected: wrong audience")
        raise credentials_exception
    except InvalidIssuerError:
        logger.info("JWT rejected: wrong issuer")
        raise credentials_exception
    except JWTError:
        logger.info("JWT rejected: invalid token")
        raise credentials_exception

    if payload.get("type") not in expected_types:
        logger.info(
            "JWT rejected: purpose %s not accepted here",
            payload.get("type"),
        )
        raise credentials_exception
    if payload["type"] == "impersonation":
        act = payload.get("act")
        if payload.get("imp") is not True or not isinstance(act, dict) or not act.get("sub"):
            logger.info("JWT rejected: malformed impersonation claim")
            raise credentials_exception
    elif payload.get("imp"):
        logger.info("JWT rejected: impersonation flag on non-impersonation token")
        raise credentials_exception

    now = datetime.now(timezone.utc).timestamp()
    leeway = max(0, int(settings.JWT_LEEWAY_SECONDS))
    if float(payload.get("iat", 0)) > now + leeway:
        logger.info("JWT rejected: iat in the future")
        raise credentials_exception

    # One DB round trip covers both individual (jti) revocation and per-user
    # mass revocation. A revocation-store failure must deny, not allow. The
    # signature-only variant is used by the impersonation middleware, and
    # get_current_user performs the revocation check with the request session.
    if check_revocation:
        _enforce_revocation(payload, db)
    return payload


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token.

    Checks:
      1. Token is valid and not expired (PyJWT handles this)
      2. Token's jti has not been individually revoked
      3. Token was not issued before a per-user revocation timestamp
      4. User still exists in the database

    For impersonation tokens (imp=True), returns the impersonated user
    but attaches impersonation metadata to the user object.
    """
    if token.startswith("ocr_svc_"):
        from app.services.service_identities import resolve_token

        service_user = resolve_token(db, token)
        if service_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate service credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        from app.security.tenant import set_tenant

        set_tenant(getattr(service_user, "institution_id", None), system_admin=False)
        try:
            from app.services.security_events import set_rls_context

            set_rls_context(
                db,
                institution_id=getattr(service_user, "institution_id", None),
                system_admin=False,
            )
        except Exception:
            pass
        set_actor(actor_type="service", actor_id=service_user.id)
        request.state.user = service_user
        return service_user

    # The impersonation middleware already validated the signature for
    # mutating requests. Reuse that payload so the request pays one decode and
    # one revocation check instead of two of each.
    payload = getattr(request.state, "auth_payload", None)
    if payload is not None:
        if payload.get("type") not in ("access", "impersonation"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Consent and impersonation middleware cache the decoded payload. Only
        # pay for the revocation lookup when the producer did not already do it.
        if not getattr(request.state, "auth_revocation_checked", False):
            _enforce_revocation(payload, db)
            request.state.auth_revocation_checked = True
    else:
        payload = _decode_token(
            token, db=db, expected_types=("access", "impersonation")
        )
        request.state.auth_revocation_checked = True
    request.state.auth_payload = payload
    username = payload.get("sub")

    user = get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Attach impersonation metadata if present
    user._imp = payload.get("imp", False)
    user._imp_original_id = payload.get("imp_original_id")
    user._imp_original_username = payload.get("imp_original")
    user._imp_mode = payload.get("imp_mode")
    user._imp_course_id = payload.get("imp_course_id")
    user._imp_read_only = payload.get("imp_read_only", False)

    if payload.get("type") == "impersonation":
        original = db.query(User).filter(User.id == user._imp_original_id).first()
        if (
            original is None
            or int(payload.get("sec", 0)) != int(getattr(original, "security_version", 1))
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Impersonation session is no longer valid.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    elif int(payload.get("sec", 0)) != int(getattr(user, "security_version", 1)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is no longer valid. Sign in again.",
            headers={"WWW-Authenticate": "Bearer", "X-Security-Version": "stale"},
        )

    # A normal login token carries a session id. The session binds the tenant
    # captured at login and is re-checked on every request. Legacy tokens
    # without a sid remain valid only for their short access-token lifetime.
    from app.services import auth_sessions

    session, session_error = auth_sessions.bind_user(db, user, payload)
    if session_error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or no longer valid. Sign in again.",
            headers={"WWW-Authenticate": "Bearer", "X-Session-Invalid": "true"},
        )

    # Attribute application writes to the authenticated actor. The database
    # integrity trigger records this on the next flush.
    set_actor(user)

    # The tenant comes from the session created at login, never from the JWT.
    from app.security.tenant import set_tenant

    tenant_id = session.institution_id if session is not None else getattr(user, "institution_id", None)
    is_system_admin = (getattr(user, "role", "") or "") == "admin"
    set_tenant(tenant_id, system_admin=is_system_admin)
    try:
        from app.services.security_events import set_rls_context

        set_rls_context(
            db,
            institution_id=tenant_id,
            system_admin=is_system_admin,
        )
    except Exception:
        # RLS context is defence in depth; a non-PostgreSQL test database or a
        # missing table must not break authentication.
        pass

    # Downstream middlewares (export labels, security-event coverage) reuse the
    # already-authenticated user instead of decoding the token again.
    request.state.user = user
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active and approved user"""
    # Check if is_active column exists (for backward compatibility)
    if hasattr(current_user, 'is_active') and not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if not current_user.is_approved:
        raise HTTPException(status_code=403, detail="User not approved")
    if current_user.is_locked:
        raise HTTPException(status_code=403, detail="User account is locked")
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


def get_current_institution_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require a platform admin or a tenant-scoped institution admin.

    Callers must still filter by the actor's ``institution_id`` unless the actor
    is the platform ``admin``. This dependency does not grant platform-wide
    access by itself.
    """
    if current_user.role not in ("admin", "institution_admin"):
        raise HTTPException(status_code=403, detail="Administrator access required")
    return current_user


def get_current_reporting_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require a teaching/reporting role, including tenant institution admins.

    Course ownership or the matching ``institution_id`` is still enforced by
    the route's course-scope check.
    """
    if current_user.role not in (
        "instructor",
        "admin",
        "institution_admin",
        "auditor",
        "privacy_officer",
        "mentor",
        "teaching_assistant",
    ):
        raise HTTPException(status_code=403, detail="Instructor access required")
    return current_user


def get_current_instructor_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require instructor or admin role"""
    if current_user.role not in ('instructor', 'admin'):
        raise HTTPException(status_code=403, detail="Instructor access required")
    return current_user


# ─── Impersonation Helpers ──────────────────────────────────────

def is_impersonating(user: User) -> bool:
    """Check if the current request is an impersonation session."""
    return getattr(user, '_imp', False)


async def enforce_not_impersonating(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency that blocks mutating endpoints during impersonation.
    Returns 403 with impersonating flag so the frontend can show a toast."""
    if is_impersonating(current_user):
        raise HTTPException(
            status_code=403,
            detail="Action blocked: you are viewing as another user",
            headers={"X-Impersonating": "true"},
        )
    return current_user


def create_impersonation_token(
    original_user: User,
    target_username: str,
    target_role: str,
    mode: str,
    course_id: Optional[int] = None,
    expires_delta: Optional[timedelta] = None,
    session_id: Optional[str] = None,
) -> str:
    """Create a JWT for an impersonation session.
    The token carries the target identity plus original-user metadata."""
    if expires_delta is None:
        expires_delta = timedelta(hours=1)
    data = {
        "sub": target_username,
        "imp": True,
        "imp_original": original_user.username,
        "imp_original_id": original_user.id,
        "imp_mode": mode,
        "imp_read_only": True,
        "act": {"sub": str(original_user.id), "username": original_user.username},
        "sec": original_user.security_version,
    }
    if course_id is not None:
        data["imp_course_id"] = course_id
    if session_id:
        data["imp_sid"] = session_id
    return create_access_token(
        data,
        expires_delta=expires_delta,
        token_type="impersonation",
        security_version=original_user.security_version,
    )


# ─── WebSocket Ticket System ────────────────────────────────────────
# Short-lived, single-use tickets that replace JWT in WebSocket URLs.
# Prevents long-lived JWTs from leaking into logs and browser history.
# Stored in the database so tickets work across multiple uvicorn workers.

_WS_TICKET_TTL = 30  # seconds


def create_ws_ticket(user_id: int) -> str:
    """Generate a single-use, 30-second ticket for WebSocket authentication."""
    from app.database import SessionLocal
    ticket = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(seconds=_WS_TICKET_TTL)
    db = SessionLocal()
    try:
        # Prune expired tickets while we're here
        db.execute(
            text("DELETE FROM ws_tickets WHERE expires_at < :now"),
            {"now": datetime.now(timezone.utc)}
        )
        db.execute(
            text(
                "INSERT INTO ws_tickets (ticket, user_id, expires_at) VALUES (:ticket, :user_id, :expires_at)"
            ),
            {"ticket": ticket, "user_id": user_id, "expires_at": expires}
        )
        db.commit()
    finally:
        db.close()
    return ticket


def validate_ws_ticket(ticket: str) -> Optional[int]:
    """Validate and consume a single-use WebSocket ticket.
    Returns user_id on success, None on failure or expiry."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        row = db.execute(
            text(
                "DELETE FROM ws_tickets WHERE ticket = :ticket RETURNING user_id, expires_at"
            ),
            {"ticket": ticket}
        ).fetchone()
        if row is None:
            return None
        user_id, expires_at = row
        if datetime.now(timezone.utc) > (
            expires_at.replace(tzinfo=timezone.utc)
            if expires_at.tzinfo is None
            else expires_at.astimezone(timezone.utc)
        ):
            return None
        db.commit()
        return user_id
    finally:
        db.close()

