"""OIDC authorization-code flow with PKCE and shared flow state.

The flow is deliberately stateless in the API process. The authorization
request state, nonce, PKCE verifier, and the final one-time ticket live in the
shared PostgreSQL database, so any API replica can complete the callback.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import jwt
import requests
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_password_hash
from app.config import settings
from app.crypto import decrypt_secret, encrypt_secret
from app.models import (
    ExternalIdentity,
    IdentityProvider,
    SsoLoginState,
    SsoLoginTicket,
    SsoSession,
    User,
)
from app.services.achievements import (
    check_learning_achievements,
    check_login_streak_achievements,
)

logger = logging.getLogger(__name__)

_DISCOVERY_CACHE: dict[str, tuple[float, dict]] = {}


class OIDCError(RuntimeError):
    """A safe, operator-facing OIDC failure."""


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def public_base_url() -> str:
    configured = (settings.PUBLIC_BASE_URL or "").strip()
    if configured:
        return configured.rstrip("/")
    host = (settings.SERVER_PUBLIC_HOST or "localhost").strip()
    if host.startswith(("http://", "https://")):
        return host.rstrip("/")
    return f"https://{host}"


def frontend_base_url() -> str:
    configured = (settings.FRONTEND_BASE_URL or "").strip()
    return configured.rstrip("/") if configured else public_base_url()


def redirect_uri(provider_id: int) -> str:
    return f"{public_base_url()}/api/auth/sso/oidc/{provider_id}/callback"


def sanitize_return_to(value: str | None) -> str:
    value = (value or "").strip()
    if not value.startswith("/") or value.startswith("//"):
        return "/dashboard"
    return value[:500]


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
        return {}
    return data if isinstance(data, dict) else {}


def _http_get_json(url: str) -> dict:
    try:
        response = requests.get(
            url,
            timeout=settings.SSO_HTTP_TIMEOUT_SECONDS,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        raise OIDCError(f"Could not reach the identity provider discovery document: {exc}") from exc
    if not isinstance(data, dict):
        raise OIDCError("The identity provider discovery document is not a JSON object.")
    return data


def discover(provider: IdentityProvider) -> dict:
    config = provider_config(provider)
    issuer = str(config.get("issuer", "")).rstrip("/")
    discovery_url = str(config.get("discovery_url", "")).strip() or (
        f"{issuer}/.well-known/openid-configuration"
    )
    now = time.monotonic()
    cached = _DISCOVERY_CACHE.get(discovery_url)
    if cached and now - cached[0] < settings.SSO_DISCOVERY_CACHE_SECONDS:
        return cached[1]

    document = _http_get_json(discovery_url)
    required = ("authorization_endpoint", "token_endpoint", "jwks_uri", "issuer")
    missing = [key for key in required if not document.get(key)]
    if missing:
        raise OIDCError(f"Discovery document is missing: {', '.join(missing)}")
    if str(document["issuer"]).rstrip("/") != issuer:
        raise OIDCError("Discovery issuer does not match the configured issuer.")

    _DISCOVERY_CACHE[discovery_url] = (now, document)
    return document


def generate_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return verifier, challenge


def authorization_url(
    provider: IdentityProvider,
    *,
    state: str,
    nonce: str,
    code_challenge: str,
    redirect: str,
) -> str:
    config = provider_config(provider)
    document = discover(provider)
    params = {
        "response_type": "code",
        "client_id": str(config.get("client_id", "")),
        "redirect_uri": redirect,
        "scope": str(config.get("scopes", "openid email profile")),
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    endpoint = str(document["authorization_endpoint"])
    separator = "&" if "?" in endpoint else "?"
    return f"{endpoint}{separator}{urlencode(params)}"


def exchange_code(
    provider: IdentityProvider,
    *,
    code: str,
    code_verifier: str,
    redirect: str,
) -> dict:
    config = provider_config(provider)
    secrets_ = provider_secrets(provider)
    document = discover(provider)
    client_id = str(config.get("client_id", ""))
    client_secret = str(secrets_.get("client_secret", "") or "")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }
    methods = document.get("token_endpoint_auth_methods_supported") or []
    auth = None
    if client_secret:
        if "client_secret_basic" in methods and "client_secret_post" not in methods:
            auth = (client_id, client_secret)
        else:
            data["client_secret"] = client_secret

    try:
        response = requests.post(
            str(document["token_endpoint"]),
            data=data,
            auth=auth,
            timeout=settings.SSO_HTTP_TIMEOUT_SECONDS,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise OIDCError(f"Token exchange failed: {exc}") from exc
    if not isinstance(payload, dict) or not payload.get("id_token"):
        raise OIDCError("The identity provider did not return an ID token.")
    return payload


def validate_id_token(provider: IdentityProvider, id_token: str, nonce: str) -> dict:
    config = provider_config(provider)
    document = discover(provider)
    issuer = str(config.get("issuer", "")).rstrip("/")
    client_id = str(config.get("client_id", ""))
    algorithms = document.get("id_token_signing_alg_values_supported") or ["RS256"]
    try:
        jwk_client = jwt.PyJWKClient(str(document["jwks_uri"]))
        signing_key = jwk_client.get_signing_key_from_jwt(id_token)
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=list(algorithms),
            audience=client_id,
            issuer=issuer,
            options={"require": ["exp", "iat", "sub"]},
        )
    except Exception as exc:
        raise OIDCError(f"ID token validation failed: {exc}") from exc
    if str(claims.get("nonce", "")) != nonce:
        raise OIDCError("ID token nonce does not match the authorization request.")
    return claims


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _safe_username(candidate: str, db: Session) -> str:
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


def _identity_from_claims(claims: dict, config: dict | None = None) -> dict:
    config = config or {}
    email_claim = str(config.get("email_claim", "email"))
    username_claim = str(config.get("username_claim", "preferred_username"))
    name_claim = str(config.get("name_claim", "name"))
    subject = str(claims.get("sub", "")).strip()
    if not subject:
        raise OIDCError("The identity provider did not return a subject.")
    email = str(claims.get(email_claim) or "").strip()
    if not email and "@" in str(claims.get(username_claim) or ""):
        email = str(claims.get(username_claim)).strip()
    if not email:
        raise OIDCError("The identity provider did not return an email address.")
    first_name = str(claims.get("given_name") or "").strip() or None
    last_name = str(claims.get("family_name") or "").strip() or None
    full_name = str(claims.get(name_claim) or "").strip()
    if not first_name and not last_name and full_name:
        parts = full_name.split(None, 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else None
    username_hint = (
        claims.get(username_claim)
        or email.split("@", 1)[0]
        or f"user-{subject[:10]}"
    )
    return {
        "subject": subject,
        "email": email,
        "email_verified": _truthy(claims.get("email_verified")),
        "username_hint": str(username_hint),
        "first_name": first_name,
        "last_name": last_name,
        "name": full_name or None,
    }


def provision_or_link_user(
    db: Session,
    provider: IdentityProvider,
    claims: dict,
    *,
    client_ip: str | None = None,
) -> tuple[User, bool, bool]:
    """Return (user, provisioned, linked_existing)."""
    config = provider_config(provider)
    identity = _identity_from_claims(claims, config)
    link = (
        db.query(ExternalIdentity)
        .filter(
            ExternalIdentity.provider_id == provider.id,
            ExternalIdentity.subject == identity["subject"],
        )
        .first()
    )
    if link is not None:
        user = db.query(User).filter(User.id == link.user_id).first()
        if user is None:
            raise OIDCError("The linked local account no longer exists.")
        if not user.is_active:
            raise OIDCError("The linked local account is disabled.")
        if not user.is_approved:
            raise OIDCError("The linked local account is not approved.")
        link.email = identity["email"]
        link.last_login_at = utcnow()
        db.commit()
        return user, False, False

    existing = (
        db.query(User)
        .filter(func.lower(User.email) == identity["email"].lower())
        .first()
    )
    if existing is not None:
        if existing.role == "admin" or existing.is_admin:
            raise OIDCError(
                "An administrator account already uses this email. "
                "Contact an administrator to link it explicitly."
            )
        link_existing = bool(config.get("link_existing_by_email", True))
        if not link_existing or not identity["email_verified"]:
            raise OIDCError(
                "An account with this email already exists. "
                "Sign in with your local password or ask an administrator to link it."
            )
        db.add(
            ExternalIdentity(
                provider_id=provider.id,
                subject=identity["subject"],
                user_id=existing.id,
                email=identity["email"],
                last_login_at=utcnow(),
            )
        )
        db.commit()
        return existing, False, True

    if not bool(config.get("auto_provision", True)):
        raise OIDCError(
            "No local account is linked to this identity. "
            "Ask an administrator to create or link your account."
        )

    role = str(config.get("default_role", "student")).strip().lower()
    if role not in {"student", "instructor"}:
        role = "student"
    approve = bool(config.get("auto_approve", True))
    user = User(
        username=_safe_username(identity["username_hint"], db),
        email=identity["email"],
        first_name=identity["first_name"],
        last_name=identity["last_name"],
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
            subject=identity["subject"],
            user_id=user.id,
            email=identity["email"],
            last_login_at=utcnow(),
        )
    )
    db.commit()
    db.refresh(user)
    logger.info("Provisioned SSO user %s from provider %s", user.username, provider.name)
    return user, True, False


def record_login(db: Session, user: User, client_ip: str | None) -> None:
    now = utcnow()
    today = now.date()
    previous_login_day = getattr(user, "last_login_day", None)
    if previous_login_day == today:
        pass
    elif previous_login_day == today - timedelta(days=1):
        user.login_streak = (getattr(user, "login_streak", 0) or 0) + 1
    else:
        user.login_streak = 1
    user.last_login_day = today
    user.last_login_at = now
    user.last_login_ip = client_ip
    db.commit()
    try:
        check_login_streak_achievements(db, user.id, getattr(user, "login_streak", 1) or 1)
        check_learning_achievements(db, user.id)
    except Exception:
        logger.exception("Could not evaluate SSO login achievements for %s", user.username)


def create_sso_session(
    db: Session,
    *,
    user: User,
    provider: IdentityProvider,
    id_token: str | None,
    session_state: str | None,
    claims: dict,
) -> None:
    """Store the latest ID token for RP-initiated logout.

    Failures here must not break login. The caller logs and continues.
    """
    expires = utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    exp = claims.get("exp") if isinstance(claims, dict) else None
    if isinstance(exp, (int, float)):
        try:
            expires = datetime.fromtimestamp(float(exp), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            pass
    encrypted = encrypt_secret(id_token) if id_token else None
    row = (
        db.query(SsoSession)
        .filter(SsoSession.user_id == user.id, SsoSession.provider_id == provider.id)
        .first()
    )
    if row is None:
        db.add(
            SsoSession(
                user_id=user.id,
                provider_id=provider.id,
                id_token=encrypted,
                session_state=session_state,
                expires_at=expires,
            )
        )
    else:
        row.id_token = encrypted
        row.session_state = session_state
        row.expires_at = expires
        row.updated_at = utcnow()
    db.commit()


def build_end_session_url(db: Session, user: User, provider_id: int) -> str | None:
    """Build the IdP end-session URL for an SSO-issued platform token."""
    session = (
        db.query(SsoSession)
        .filter(SsoSession.user_id == user.id, SsoSession.provider_id == provider_id)
        .first()
    )
    if session is None:
        return None
    provider = db.query(IdentityProvider).filter(IdentityProvider.id == provider_id).first()
    if provider is None:
        return None
    try:
        document = discover(provider)
    except OIDCError:
        return None
    endpoint = document.get("end_session_endpoint")
    if not endpoint:
        return None

    config = provider_config(provider)
    params: dict[str, str] = {
        "post_logout_redirect_uri": f"{frontend_base_url()}/login",
    }
    if config.get("client_id"):
        params["client_id"] = str(config["client_id"])
    if session.id_token:
        try:
            params["id_token_hint"] = decrypt_secret(session.id_token)
        except Exception:
            logger.warning("Could not decrypt the stored SSO ID token for logout")
    if session.session_state:
        params["session_state"] = session.session_state
    separator = "&" if "?" in endpoint else "?"
    url = f"{endpoint}{separator}{urlencode(params)}"
    db.delete(session)
    db.commit()
    return url


def login_payload(user: User, provider_id: int | None = None) -> dict:
    token_data = {"sub": user.username}
    if provider_id is not None:
        token_data["sso_provider_id"] = provider_id
    token = create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "student_id": user.student_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_admin": user.is_admin,
            "is_approved": user.is_approved,
            "is_active": user.is_active,
            "must_change_password": user.must_change_password,
            "timezone": getattr(user, "timezone", None),
            "equipped_title": getattr(user, "equipped_title", None),
        },
    }


def create_login_ticket(
    db: Session,
    *,
    user: User,
    provider: IdentityProvider,
    return_to: str,
) -> str:
    ticket = secrets.token_urlsafe(32)
    db.add(
        SsoLoginTicket(
            ticket=ticket,
            user_id=user.id,
            provider_id=provider.id,
            return_to=sanitize_return_to(return_to),
            expires_at=utcnow() + timedelta(seconds=settings.SSO_TICKET_TTL_SECONDS),
        )
    )
    db.commit()
    return ticket


def consume_login_ticket(db: Session, ticket: str) -> SsoLoginTicket:
    now = utcnow()
    updated = (
        db.query(SsoLoginTicket)
        .filter(
            SsoLoginTicket.ticket == ticket,
            SsoLoginTicket.consumed_at.is_(None),
            SsoLoginTicket.expires_at >= now,
        )
        .update({SsoLoginTicket.consumed_at: now}, synchronize_session=False)
    )
    db.commit()
    if updated != 1:
        raise OIDCError("This sign-in link has expired or was already used.")
    return db.query(SsoLoginTicket).filter(SsoLoginTicket.ticket == ticket).first()


def consume_login_state(db: Session, state: str, provider_id: int) -> SsoLoginState:
    now = utcnow()
    updated = (
        db.query(SsoLoginState)
        .filter(
            SsoLoginState.state == state,
            SsoLoginState.provider_id == provider_id,
            SsoLoginState.consumed_at.is_(None),
            SsoLoginState.expires_at >= now,
        )
        .update({SsoLoginState.consumed_at: now}, synchronize_session=False)
    )
    db.commit()
    if updated != 1:
        raise OIDCError("This sign-in request has expired or was already used.")
    return db.query(SsoLoginState).filter(SsoLoginState.state == state).first()


def cleanup_expired(db: Session) -> None:
    now = utcnow()
    db.query(SsoLoginState).filter(
        SsoLoginState.expires_at < now - timedelta(days=1)
    ).delete(synchronize_session=False)
    db.query(SsoLoginTicket).filter(
        SsoLoginTicket.expires_at < now - timedelta(days=1)
    ).delete(synchronize_session=False)
    db.commit()


def create_login_state(
    db: Session,
    *,
    provider: IdentityProvider,
    return_to: str,
) -> tuple[str, str, str, str]:
    verifier, challenge = generate_pkce()
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    db.add(
        SsoLoginState(
            state=state,
            provider_id=provider.id,
            nonce=nonce,
            code_verifier=verifier,
            redirect_uri=redirect_uri(provider.id),
            return_to=sanitize_return_to(return_to),
            expires_at=utcnow() + timedelta(seconds=settings.SSO_STATE_TTL_SECONDS),
        )
    )
    db.commit()
    return state, nonce, verifier, challenge


def test_provider(provider: IdentityProvider) -> dict:
    document = discover(provider)
    try:
        response = requests.get(
            str(document["jwks_uri"]),
            timeout=settings.SSO_HTTP_TIMEOUT_SECONDS,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        keys = response.json().get("keys", [])
    except Exception as exc:
        raise OIDCError(f"Could not fetch the JWKS document: {exc}") from exc
    return {
        "issuer": document.get("issuer"),
        "authorization_endpoint": document.get("authorization_endpoint"),
        "token_endpoint": document.get("token_endpoint"),
        "jwks_uri": document.get("jwks_uri"),
        "userinfo_endpoint": document.get("userinfo_endpoint"),
        "end_session_endpoint": document.get("end_session_endpoint"),
        "signing_keys": len(keys),
        "scopes_supported": document.get("scopes_supported", []),
    }
