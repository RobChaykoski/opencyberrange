"""Encryption utilities for sensitive data.

Envelope format: ``v1:<fernet token>``. Unprefixed values are treated as v0
(legacy single-key) tokens so existing rows keep decrypting.

Rotation is additive: set ``WG_ENCRYPTION_KEY`` to the new key and
``WG_ENCRYPTION_KEY_PREVIOUS`` to a comma-separated list of old keys. New writes
use the new key; old rows still decrypt. Run
``python -m app.scripts.reencrypt_secrets`` to move old rows forward, then drop
the previous keys.
"""

from __future__ import annotations

import logging

from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from app.config import settings

logger = logging.getLogger(__name__)

ENVELOPE_PREFIX = "v1:"
LEGACY_PREFIX = "gAAAAA"

_multi: MultiFernet | None = None
_primary: Fernet | None = None


def _load_keys() -> tuple[MultiFernet, Fernet]:
    primary = (settings.WG_ENCRYPTION_KEY or "").strip()
    if not primary:
        raise ValueError(
            "WG_ENCRYPTION_KEY must be set for secret encryption. "
            "Generate with: python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    previous = [
        value.strip()
        for value in (settings.WG_ENCRYPTION_KEY_PREVIOUS or "").split(",")
        if value.strip()
    ]
    keys = [primary.encode()]
    keys.extend(value.encode() for value in previous)
    try:
        fernets = [Fernet(key) for key in keys]
        return MultiFernet(fernets), fernets[0]
    except Exception as exc:
        raise ValueError(f"Invalid encryption key format: {exc}") from exc


def _instances() -> tuple[MultiFernet, Fernet]:
    global _multi, _primary
    if _multi is None or _primary is None:
        _multi, _primary = _load_keys()
    return _multi, _primary


def reset_cache() -> None:
    """Clear the cached key material (tests and post-rotation reloads)."""
    global _multi, _primary
    _multi = None
    _primary = None


def encrypt_secret(value: str) -> str:
    """Encrypt with the newest key and wrap the token in a v1 envelope."""
    multi, _primary_fernet = _instances()
    token = multi.encrypt(value.encode()).decode()
    return f"{ENVELOPE_PREFIX}{token}"


def decrypt_secret(token: str) -> str:
    """Decrypt a v1 envelope or a bare legacy Fernet token."""
    if not token:
        raise ValueError("Cannot decrypt an empty secret")
    payload = token[len(ENVELOPE_PREFIX):] if token.startswith(ENVELOPE_PREFIX) else token
    multi, _primary_fernet = _instances()
    try:
        return multi.decrypt(payload.encode()).decode()
    except (InvalidToken, TypeError, ValueError) as exc:
        raise ValueError(
            "Failed to decrypt secret - invalid encryption key or corrupted data"
        ) from exc


def is_encrypted(value: str) -> bool:
    """True for v1 envelopes and bare legacy Fernet tokens."""
    if not isinstance(value, str):
        return False
    return value.startswith(ENVELOPE_PREFIX) or value.startswith(LEGACY_PREFIX)


def needs_reencryption(token: str) -> bool:
    """True when a stored secret is not on the current key or envelope.

    The maintenance script uses this to find rows that should be rewritten with
    ``encrypt_secret``. It deliberately does not raise on malformed input; the
    caller decides whether to skip or flag the row.
    """
    if not is_encrypted(token):
        return True
    payload = token[len(ENVELOPE_PREFIX):] if token.startswith(ENVELOPE_PREFIX) else token
    try:
        _multi_instance, primary = _instances()
        primary.decrypt(payload.encode())
        return not token.startswith(ENVELOPE_PREFIX)
    except (InvalidToken, TypeError, ValueError):
        return True


# Backwards-compatible aliases used by the WireGuard and TOTP services.
encrypt_private_key = encrypt_secret
decrypt_private_key = decrypt_secret


def generate_encryption_key() -> str:
    """Generate a new Fernet key for WG_ENCRYPTION_KEY."""
    return Fernet.generate_key().decode()
