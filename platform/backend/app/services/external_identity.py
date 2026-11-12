"""Shared external-identity policy for OIDC, SAML, and LDAP logins.

All three adapters turn a provider response into an :class:`ExternalUser` and
then call :func:`provision_or_link_external_user`. Keeping the policy in one
place means the account-linking and role rules cannot drift between adapters.

Policy:

* The provider + subject pair is the stable identity. Email is not the key.
* An existing link is reused; a disabled or unapproved local account stays
  blocked.
* An existing local account is linked only by a verified email address, and
  never if it is an administrator account.
* New accounts are provisioned as ``student`` or ``instructor``. They are never
  administrators, and they cannot use the local password form.
"""

from __future__ import annotations

import json
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.crypto import decrypt_secret
from app.models import ExternalIdentity, IdentityProvider, User

logger = logging.getLogger(__name__)


class SSOError(RuntimeError):
    """A safe, operator-facing SSO failure.

    Adapters raise this for both configuration and authentication failures. The
    routers log the detail and return a generic message to the browser. ``code``
    lets a direct-login adapter distinguish bad credentials from an outage.
    """

    def __init__(self, message: str, *, code: str = "sso_failed"):
        super().__init__(message)
        self.code = code


@dataclass
class ExternalUser:
    """Normalised identity returned by an adapter."""

    subject: str
    email: str
    email_verified: bool = True
    username_hint: str = ""
    first_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    groups: list[str] = field(default_factory=list)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def provider_config(provider: IdentityProvider) -> dict:
    try:
        data = json.loads(provider.config or "{}")
    except (TypeError, ValueError):
        data = {}
    return data if isinstance(data, dict) else {}


def provider_secrets(provider: IdentityProvider) -> dict:
    if not provider.secrets:
        return {}
    try:
        data = json.loads(decrypt_secret(provider.secrets))
    except Exception:
        logger.warning("Could not decrypt secrets for provider %s", provider.name)
        return {}
    return data if isinstance(data, dict) else {}


def safe_username(candidate: str, db: Session) -> str:
    raw = (candidate or "").strip().lower()
    cleaned = "".join(ch if ch.isalnum() or ch in "_-" else "-" for ch in raw)
    cleaned = cleaned.strip("-_")
    if not cleaned or not cleaned[0].isalpha():
        cleaned = f"user-{cleaned or secrets.token_hex(3)}"
    cleaned = cleaned[:50]
    base = cleaned
    index = 2
    while db.query(User).filter(func.lower(User.username) == cleaned).first():
        suffix = f"-{index}"
        cleaned = f"{base[: 50 - len(suffix)]}{suffix}"
        index += 1
    return cleaned


def _group_matches(group: str, wanted: str) -> bool:
    """Match a configured group against a directory group value.

    Administrators often configure a short CN (``instructors``) while LDAP
    returns a full DN (``CN=Instructors,OU=Groups,DC=example,DC=edu``), so match
    both the whole value and each RDN value.
    """
    group_value = (group or "").strip().lower()
    wanted_value = (wanted or "").strip().lower()
    if not group_value or not wanted_value:
        return False
    if group_value == wanted_value:
        return True
    for part in group_value.split(","):
        value = part.split("=", 1)[-1].strip()
        if value == wanted_value:
            return True
    return False


def role_for(config: dict, groups: list[str] | None) -> str:
    """Return the role for a newly provisioned account.

    Only ``student`` and ``instructor`` are possible. An administrator role is
    never granted by an external identity.
    """
    default = str(config.get("default_role", "student")).strip().lower()
    if default not in {"student", "instructor"}:
        default = "student"
    instructor_group = str(config.get("instructor_group", "")).strip()
    if instructor_group:
        for group in groups or []:
            if _group_matches(str(group), instructor_group):
                return "instructor"
    return default


def provision_or_link_external_user(
    db: Session,
    provider: IdentityProvider,
    identity: ExternalUser,
    *,
    client_ip: str | None = None,
) -> tuple[User, bool, bool]:
    """Return ``(user, provisioned, linked_existing)`` for an external login."""
    config = provider_config(provider)
    subject = (identity.subject or "").strip()
    email = (identity.email or "").strip()
    if not subject:
        raise SSOError("The identity provider did not return a subject.")
    if not email:
        raise SSOError("The identity provider did not return an email address.")

    link = (
        db.query(ExternalIdentity)
        .filter(
            ExternalIdentity.provider_id == provider.id,
            ExternalIdentity.subject == subject,
        )
        .first()
    )
    if link is not None:
        user = db.query(User).filter(User.id == link.user_id).first()
        if user is None:
            raise SSOError("The linked local account no longer exists.")
        if not user.is_active:
            raise SSOError("The linked local account is disabled.")
        if not user.is_approved:
            raise SSOError("The linked local account is not approved.")
        link.email = email
        link.last_login_at = utcnow()
        # SSO-managed accounts follow the directory role mapping on every
        # login, so a group change takes effect without an admin edit. A local
        # account that was linked by email keeps its role, and an administrator
        # is never demoted by a directory claim.
        if user.password_login_disabled and user.role != "admin":
            mapped_role = role_for(config, identity.groups)
            if user.role != mapped_role:
                logger.info(
                    "SSO role change for %s on provider %s: %s -> %s",
                    user.username,
                    provider.name,
                    user.role,
                    mapped_role,
                )
                user.role = mapped_role
        db.commit()
        return user, False, False

    existing = (
        db.query(User).filter(func.lower(User.email) == email.lower()).first()
    )
    if existing is not None:
        if existing.role == "admin" or existing.is_admin:
            raise SSOError(
                "An administrator account already uses this email. "
                "Contact an administrator to link it explicitly."
            )
        link_existing = bool(config.get("link_existing_by_email", True))
        if not link_existing or not identity.email_verified:
            raise SSOError(
                "An account with this email already exists. "
                "Sign in with your local password or ask an administrator to link it."
            )
        db.add(
            ExternalIdentity(
                provider_id=provider.id,
                subject=subject,
                user_id=existing.id,
                email=email,
                last_login_at=utcnow(),
            )
        )
        db.commit()
        return existing, False, True

    if not bool(config.get("auto_provision", True)):
        raise SSOError(
            "No local account is linked to this identity. "
            "Ask an administrator to create or link your account."
        )

    role = role_for(config, identity.groups)
    approve = bool(config.get("auto_approve", True))
    user = User(
        username=safe_username(identity.username_hint or email.split("@", 1)[0], db),
        email=email,
        first_name=identity.first_name,
        last_name=identity.last_name,
        hashed_password=get_password_hash(secrets.token_urlsafe(48)),
        is_active=True,
        is_approved=approve,
        is_admin=False,
        role=role,
        password_login_disabled=True,
    )
    db.add(user)
    db.flush()
    db.add(
        ExternalIdentity(
            provider_id=provider.id,
            subject=subject,
            user_id=user.id,
            email=email,
            last_login_at=utcnow(),
        )
    )
    db.commit()
    db.refresh(user)
    logger.info("Provisioned SSO user %s from provider %s", user.username, provider.name)
    return user, True, False
