"""Self-service password reset tokens.

The token is a short-lived, purpose-scoped JWT signed with the platform JWT
secret. It is deliberately not an access token: it has no issuer, audience,
or role claims, so the normal API authenticator rejects it. A fingerprint of
the current password hash is bound into the token, which makes the link
single-use without a database table: once the password changes, the stored
hash (and therefore the fingerprint) changes and the old link stops working.

Nothing in this module writes to the database or sends mail. The caller owns
the user lookup and the background mail task so the response time and the
generic "if that address exists" answer stay constant.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from app.config import settings

RESET_TOKEN_TTL_MINUTES = 30
_RESET_PURPOSE = "password_reset"
_RESET_ISSUER = "opencyberrange-password-reset"
_RESET_AUDIENCE = "ocr-password-reset"


class InvalidResetToken(Exception):
    """The token is missing, malformed, expired, or no longer valid."""


def _password_fingerprint(hashed_password: str) -> str:
    return hashlib.sha256((hashed_password or "").encode("utf-8")).hexdigest()[:32]


def create_reset_token(user) -> str:
    """Create a reset token for ``user`` that expires in 30 minutes."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "purpose": _RESET_PURPOSE,
        "pwd": _password_fingerprint(user.hashed_password),
        "iss": _RESET_ISSUER,
        "aud": _RESET_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=RESET_TOKEN_TTL_MINUTES),
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_reset_token(token: str) -> dict:
    """Validate the token's signature, expiry, scope, and required claims."""
    if not token or len(token) > 4096:
        raise InvalidResetToken("missing token")
    try:
        header = jwt.get_unverified_header(token)
        if set(header) & {"jku", "jwk", "x5u", "x5c", "kid"}:
            raise InvalidResetToken("unexpected token header")
        if header.get("alg") != settings.JWT_ALGORITHM:
            raise InvalidResetToken("unexpected algorithm")
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=_RESET_ISSUER,
            audience=_RESET_AUDIENCE,
            leeway=max(0, int(settings.JWT_LEEWAY_SECONDS)),
            options={"require": ["sub", "purpose", "pwd", "exp", "iat"]},
        )
    except jwt.PyJWTError as exc:
        raise InvalidResetToken("invalid or expired token") from exc

    if payload.get("purpose") != _RESET_PURPOSE:
        raise InvalidResetToken("wrong token purpose")
    return payload


def token_matches_user(payload: dict, user) -> bool:
    """True when the token's password fingerprint is still current."""
    if not payload or user is None:
        return False
    if str(payload.get("sub")) != str(user.id):
        return False
    expected = _password_fingerprint(user.hashed_password)
    return secrets.compare_digest(str(payload.get("pwd", "")), expected)


def user_id_from_payload(payload: dict) -> Optional[int]:
    try:
        return int(payload.get("sub"))
    except (TypeError, ValueError):
        return None
