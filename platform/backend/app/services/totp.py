"""
TOTP MFA helpers.

Secrets are generated with pyotp and stored Fernet-encrypted (app.crypto,
same key/scheme as the WireGuard and BYO-API-key helpers) in
users.totp_secret. Decryption tolerates legacy plaintext rows so an
enrollment that predates encryption keeps working.
"""

import hmac
import time

import pyotp

from app.crypto import encrypt_secret, decrypt_secret, is_encrypted

ISSUER_NAME = "SWOCTS Cyber Range"

# Accept one 30-second step of clock drift in either direction.
TOTP_VALID_WINDOW = 1
TOTP_STEP_SECONDS = 30


def generate_secret() -> str:
    """Generate a fresh base32 TOTP secret."""
    return pyotp.random_base32()


def encrypt_totp_secret(secret: str) -> str:
    """Encrypt a TOTP secret for storage in users.totp_secret."""
    return encrypt_secret(secret)


def _plain_secret(stored: str) -> str:
    """Return the usable base32 secret from a stored column value."""
    if is_encrypted(stored):
        return decrypt_secret(stored)
    return stored


def provisioning_uri(secret: str, account_name: str) -> str:
    """Build the otpauth:// URI an authenticator app enrolls from.

    Takes the PLAINTEXT secret (call right after generate_secret, before
    the encrypted copy is stored)."""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=account_name, issuer_name=ISSUER_NAME
    )


def verify_code_step(stored_secret: str, code: str) -> int | None:
    """Return the matching TOTP timestep, or None.

    The caller stores the accepted step so the same code cannot be replayed.
    """
    if not stored_secret or not code:
        return None
    code = code.strip().replace(" ", "")
    if not code.isdigit():
        return None
    try:
        secret = _plain_secret(stored_secret)
        totp = pyotp.TOTP(secret)
        current = int(time.time()) // TOTP_STEP_SECONDS
        for offset in range(-TOTP_VALID_WINDOW, TOTP_VALID_WINDOW + 1):
            step = current + offset
            if hmac.compare_digest(totp.generate_otp(step), code):
                return step
    except Exception:
        return None
    return None


def verify_code(stored_secret: str, code: str) -> bool:
    """Verify a user-supplied TOTP code against the stored secret.

    stored_secret is the raw column value (encrypted or legacy plaintext).
    Returns False on any failure, including decryption errors, rather than
    raising into the login path."""
    return verify_code_step(stored_secret, code) is not None
