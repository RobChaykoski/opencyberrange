"""TOTP lifecycle, recovery codes, and MFA brute-force throttling.

Recovery codes are single-use, expire with the configured TTL, and are replaced
as a set. MFA failures have a separate counter and lock from password lockout,
so a stolen password plus guessed codes cannot lock the account's password
channel or bypass the second factor.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.services import security_events
from app.services import totp as totp_service

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
TRUTHY = {"true", "1", "yes", "on", "enabled"}
DEFAULT_CODE_COUNT = 10
DEFAULT_TTL_DAYS = 365


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _setting(db: Session, key: str, default: str) -> str:
    from app.services import settings_service

    return (
        settings_service.get_setting_fresh(db, key, default) or default
    ).strip()


def _int_setting(db: Session, key: str, default: int) -> int:
    try:
        return int(_setting(db, key, str(default)))
    except (TypeError, ValueError):
        return default


def _normalize(code: str) -> str:
    return (code or "").strip().replace(" ", "").replace("-", "").upper()


def _hash(code: str) -> str:
    return hashlib.sha256(_normalize(code).encode("utf-8")).hexdigest()


def _load_codes(user: User) -> list[str]:
    if not user.mfa_recovery_codes:
        return []
    try:
        value = json.loads(user.mfa_recovery_codes)
    except (TypeError, json.JSONDecodeError):
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    return []


def _save_codes(user: User, codes: list[str]) -> None:
    user.mfa_recovery_codes = json.dumps(codes) if codes else None


def _ttl_days(db: Session) -> int:
    return max(1, min(_int_setting(db, "mfa_recovery_code_ttl_days", DEFAULT_TTL_DAYS), 3650))


def recovery_expires_at(db: Session, user: User) -> datetime | None:
    generated = getattr(user, "mfa_recovery_generated_at", None)
    if generated is None:
        return None
    if generated.tzinfo is not None:
        generated = generated.astimezone(timezone.utc).replace(tzinfo=None)
    return generated + timedelta(days=_ttl_days(db))


def codes_expired(db: Session, user: User) -> bool:
    expires_at = recovery_expires_at(db, user)
    return bool(expires_at and expires_at <= _now())


def recovery_remaining(user: User) -> int:
    return len(_load_codes(user))


def generate_recovery_codes(db: Session, user: User) -> tuple[list[str], datetime]:
    count = max(4, min(_int_setting(db, "mfa_recovery_code_count", DEFAULT_CODE_COUNT), 20))
    codes = [
        "".join(secrets.choice(CODE_ALPHABET) for _ in range(10))
        for _ in range(count)
    ]
    _save_codes(user, [_hash(code) for code in codes])
    user.mfa_recovery_generated_at = _now()
    user.mfa_failed_attempts = 0
    user.mfa_locked_until = None
    db.commit()
    expires_at = recovery_expires_at(db, user)
    security_events.record(
        "auth.recovery_codes_generated",
        actor=user,
        target_type="user",
        target_id=user.id,
        target_label=user.username,
        detail={"count": count, "expires_at": expires_at.isoformat() if expires_at else None},
    )
    return codes, expires_at


def clear_recovery_codes(db: Session, user: User, *, commit: bool = True) -> None:
    _save_codes(user, [])
    user.mfa_recovery_generated_at = None
    if commit:
        db.commit()


def assert_mfa_allowed(user: User, db: Session | None = None) -> None:
    locked_until = getattr(user, "mfa_locked_until", None)
    if locked_until is None:
        return
    if locked_until.tzinfo is not None:
        locked_until = locked_until.astimezone(timezone.utc).replace(tzinfo=None)
    now = _now()
    if locked_until <= now:
        if db is not None:
            user.mfa_locked_until = None
            db.commit()
        return
    retry_after = max(1, int((locked_until - now).total_seconds()))
    raise HTTPException(
        status_code=429,
        detail="Too many invalid MFA codes. Try again later.",
        headers={"Retry-After": str(retry_after), "X-MFA-Locked": "true"},
    )


def record_failure(db: Session, user: User) -> None:
    threshold = max(1, _int_setting(db, "mfa_max_failed_attempts", 5))
    lock_minutes = max(1, min(_int_setting(db, "mfa_lockout_minutes", 15), 1440))
    user.mfa_failed_attempts = (user.mfa_failed_attempts or 0) + 1
    user.mfa_last_failed_at = _now()
    if user.mfa_failed_attempts >= threshold:
        user.mfa_locked_until = _now() + timedelta(minutes=lock_minutes)
        security_events.record(
            "auth.mfa_locked",
            outcome="denied",
            severity="warning",
            actor=user,
            target_type="user",
            target_id=user.id,
            target_label=user.username,
            detail={
                "failed_attempts": user.mfa_failed_attempts,
                "locked_until": user.mfa_locked_until.isoformat(),
                "lock_minutes": lock_minutes,
            },
        )
    db.commit()


def reset_failures(db: Session, user: User) -> None:
    if (user.mfa_failed_attempts or 0) or user.mfa_locked_until is not None:
        user.mfa_failed_attempts = 0
        user.mfa_locked_until = None
        db.commit()


def consume_recovery_code(db: Session, user: User, code: str) -> int | None:
    """Consume one recovery code atomically and return the remaining count.

    Returns None when the code is invalid or the set has expired. The row lock
    prevents two concurrent logins from using the same code.
    """
    if codes_expired(db, user):
        clear_recovery_codes(db, user)
        security_events.record(
            "auth.recovery_codes_expired",
            actor=user,
            target_type="user",
            target_id=user.id,
            target_label=user.username,
        )
        return None
    hashed = _hash(code)
    row = (
        db.query(User)
        .filter(User.id == user.id)
        .with_for_update()
        .first()
    )
    if row is None:
        return None
    stored = _load_codes(row)
    match_index = next(
        (index for index, item in enumerate(stored) if hmac.compare_digest(item, hashed)),
        None,
    )
    if match_index is None:
        return None
    stored.pop(match_index)
    _save_codes(row, stored)
    db.commit()
    db.refresh(user)
    security_events.record(
        "auth.recovery_code_used",
        actor=user,
        target_type="user",
        target_id=user.id,
        target_label=user.username,
        detail={"remaining": len(stored)},
    )
    return len(stored)


def recovery_code_valid(db: Session, user: User, code: str) -> bool:
    """Check a recovery code without consuming it.

    Used by destructive flows that must not burn a valid code when the action
    is later blocked by a business rule.
    """
    if codes_expired(db, user):
        return False
    hashed = _hash(code)
    return any(
        hmac.compare_digest(item, hashed) for item in _load_codes(user)
    )


def verify_totp_or_recovery(db: Session, user: User, code: str) -> tuple[bool, str | None]:
    """Return ``(valid, method)`` for a login/MFA challenge code."""
    if totp_service.verify_code(user.totp_secret, code):
        reset_failures(db, user)
        return True, "totp"
    remaining = consume_recovery_code(db, user, code)
    if remaining is not None:
        reset_failures(db, user)
        return True, "recovery"
    return False, None


def verify_totp(user: User, code: str) -> bool:
    return totp_service.verify_code(user.totp_secret, code)
