"""Privacy helpers for user-facing responses.

User-facing account exports and session views should not reveal private,
loopback, link-local, or otherwise non-global addresses. Administrators still
see the raw value in admin-only audit views.
"""
import hashlib
import hmac
import ipaddress

from app.config import settings


REDACTED_IP = "redacted"


def pseudonymous_user_id(user_id: int, *, scope: str = "analytics") -> str:
    """Return a keyed, stable pseudonym for an instructor-facing response.

    The raw user id is an internal identifier. Survey and research responses
    use this value so a reviewer can distinguish rows without receiving the
    account id. The key is the report signing key, with the JWT secret as the
    documented fallback.
    """
    key = settings.REPORT_SIGNING_KEY or settings.JWT_SECRET
    if not key:
        raise RuntimeError("a signing key is required for pseudonymous ids")
    return hmac.new(
        key.encode("utf-8"),
        f"{scope}:{user_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def redact_ip(value):
    """Return a global IP unchanged, or a redaction marker otherwise.

    Missing values stay missing. Malformed values are redacted rather than
    echoed, because the source is often a proxy header or an older row.
    """
    if value is None or value == "":
        return value
    try:
        address = ipaddress.ip_address(str(value).strip())
    except ValueError:
        return REDACTED_IP
    if not address.is_global:
        return REDACTED_IP
    return str(address)
