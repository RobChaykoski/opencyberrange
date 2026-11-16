"""Password breach checking using the Pwned Passwords range API.

The full password is never sent to a third party. The service computes a
SHA-1 digest locally, sends only the first five hexadecimal characters to the
Have I Been Pwned range endpoint, and matches the remaining suffix in the
response. The API is queried with ``Add-Padding`` so response sizes do not leak
information about the suffix.

The check is opt-in. When the admin setting is off, no request is made. When the
API is unreachable or returns an unexpected response, the check fails open: a
network problem must not block registration or a password reset. SHA-1 is used
only as a lookup index here; passwords are still stored with Argon2id.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging

import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services.feature_flags import password_breach_check_enabled

logger = logging.getLogger(__name__)

HIBP_RANGE_URL = "https://api.pwnedpasswords.com/range/"
REQUEST_TIMEOUT_SECONDS = 3.0
USER_AGENT = "OpenCyberRange-PasswordBreachCheck/1.0"


def password_sha1(password: str) -> str:
    """Return the uppercase SHA-1 lookup digest for a password."""
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def _split_digest(digest: str) -> tuple[str, str]:
    return digest[:5], digest[5:]


def parse_range_response(text: str, suffix: str) -> int:
    """Return the breach count for a digest suffix, or 0 when not listed."""
    expected = suffix.strip().upper()
    for line in (text or "").splitlines():
        if ":" not in line:
            continue
        candidate, count = line.split(":", 1)
        if candidate.strip().upper() != expected:
            continue
        try:
            return int(count.strip())
        except ValueError:
            return 0
    return 0


def _fetch_range(prefix: str) -> str | None:
    """Fetch one HIBP range response. Returns None when unavailable."""
    try:
        response = requests.get(
            HIBP_RANGE_URL + prefix,
            headers={
                "Add-Padding": "true",
                "User-Agent": USER_AGENT,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        logger.warning("Password breach check request failed: %s", exc)
        return None
    if response.status_code != 200:
        logger.warning(
            "Password breach check returned HTTP %s",
            response.status_code,
        )
        return None
    return response.text


async def breach_count(password: str) -> int | None:
    """Return how many times a password appears in Pwned Passwords.

    ``None`` means the check could not be completed. The caller should fail
    open in that case. Zero means the password was not found.
    """
    digest = password_sha1(password)
    prefix, suffix = _split_digest(digest)
    text = await asyncio.to_thread(_fetch_range, prefix)
    if text is None:
        return None
    return parse_range_response(text, suffix)


async def enforce_password_breach_check(db: Session, password: str) -> int | None:
    """Reject a breached password when the admin has enabled the check.

    Returns the breach count (0 when clean) or None when the check is disabled
    or unavailable. Raises ``HTTPException(400)`` for a breached password.
    """
    if not password_breach_check_enabled(db):
        return None
    count = await breach_count(password)
    if count is None:
        return None
    if count > 0:
        logger.info("Password breach check rejected a password (%d hits)", count)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This password has appeared in a known data breach. "
                "Choose a different password."
            ),
        )
    return 0
