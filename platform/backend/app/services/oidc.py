"""OIDC authorization-code flow with PKCE and shared flow state.

The flow is deliberately stateless in the API process. The authorization
request state, nonce, PKCE verifier, and the final one-time ticket live in the
shared PostgreSQL database, so any API replica can complete the callback.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import jwt
import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.crypto import decrypt_secret, encrypt_secret
from app.models import IdentityProvider, SsoSession, User
from app.services.external_identity import (
    SSOError,
    ExternalUser,
    provider_config,
    provider_secrets,
    truthy,
    utcnow,
)
from app.services.sso_flow import (
    cleanup_expired,
    consume_login_state,
    consume_login_ticket,
    create_flow_state,
    create_login_ticket,
    frontend_base_url,
    login_payload,
    public_base_url,
    record_login,
    sanitize_return_to,
)

logger = logging.getLogger(__name__)

_DISCOVERY_CACHE: dict[str, tuple[float, dict]] = {}

# Kept as an alias so existing callers and tests can catch every adapter error.
OIDCError = SSOError


def redirect_uri(provider_id: int) -> str:
    return f"{public_base_url()}/api/auth/sso/oidc/{provider_id}/callback"


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


def _identity_from_claims(claims: dict, config: dict | None = None) -> ExternalUser:
    config = config or {}
    email_claim = str(config.get("email_claim", "email"))
    username_claim = str(config.get("username_claim", "preferred_username"))
    name_claim = str(config.get("name_claim", "name"))
    groups_claim = str(config.get("groups_claim", "groups"))
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
    raw_groups = claims.get(groups_claim)
    if isinstance(raw_groups, str):
        groups = [part for part in raw_groups.replace(";", ",").split(",") if part.strip()]
    elif isinstance(raw_groups, (list, tuple)):
        groups = [str(value) for value in raw_groups if str(value).strip()]
    else:
        groups = []
    return ExternalUser(
        subject=subject,
        email=email,
        email_verified=truthy(claims.get("email_verified")),
        username_hint=str(username_hint),
        first_name=first_name,
        last_name=last_name,
        name=full_name or None,
        groups=groups,
    )


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
    from app.services.external_identity import provision_or_link_external_user

    return provision_or_link_external_user(
        db, provider, identity, client_ip=client_ip
    )


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
    if provider is None or provider.kind != "oidc":
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


def create_login_state(
    db: Session,
    *,
    provider: IdentityProvider,
    return_to: str,
) -> tuple[str, str, str, str]:
    verifier, challenge = generate_pkce()
    nonce = secrets.token_urlsafe(32)
    state = create_flow_state(
        db,
        provider=provider,
        return_to=return_to,
        nonce=nonce,
        code_verifier=verifier,
        redirect_uri=redirect_uri(provider.id),
    )
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
        "message": (
            f"Discovery OK · {document.get('issuer')} · "
            f"{len(keys)} signing key{'s' if len(keys) != 1 else ''}"
        ),
        "issuer": document.get("issuer"),
        "authorization_endpoint": document.get("authorization_endpoint"),
        "token_endpoint": document.get("token_endpoint"),
        "jwks_uri": document.get("jwks_uri"),
        "userinfo_endpoint": document.get("userinfo_endpoint"),
        "end_session_endpoint": document.get("end_session_endpoint"),
        "signing_keys": len(keys),
        "scopes_supported": document.get("scopes_supported", []),
    }
