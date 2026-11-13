"""LTI 1.3 platform registry, login state, and launch validation.

The LMS is the identity provider. This module keeps the LTI-specific pieces
(platform registration, third-party initiated login state, id_token validation,
and account linking) separate from the generic OIDC/SAML adapters.
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
import ssl
from datetime import timedelta
from urllib.parse import urlencode, urlsplit

import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models import IdentityProvider, LtiLoginState, LtiPlatform, User
from app.services import sso_flow
from app.services.external_identity import (
    ExternalUser,
    SSOError,
    provision_or_link_external_user,
    utcnow,
)

logger = logging.getLogger(__name__)

LTI_DEPLOYMENT_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/deployment_id"
LTI_MESSAGE_TYPE_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/message_type"
LTI_RESOURCE_LINK_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/resource_link"
LTI_CONTEXT_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/context"
ALLOWED_MESSAGE_TYPES = {"LtiResourceLinkRequest", "LtiDeepLinkingRequest"}
ALLOWED_SIGNING_ALGORITHMS = ["RS256", "RS384", "ES256", "ES384"]


class LTIError(RuntimeError):
    """A safe, operator-facing LTI failure."""


def valid_lti_url(value: str, *, allow_http: bool = False) -> bool:
    parsed = urlsplit((value or "").strip())
    if parsed.scheme not in ({"https", "http"} if allow_http else {"https"}):
        return False
    return bool(parsed.netloc) and not parsed.fragment


def _tls_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    if settings.SSO_ALLOW_INSECURE_HTTP:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    return context


def create_login_state(
    db: Session,
    *,
    platform: LtiPlatform,
    target_link_uri: str,
) -> tuple[str, str]:
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    db.add(
        LtiLoginState(
            state=state,
            platform_id=platform.id,
            nonce=nonce,
            target_link_uri=target_link_uri[:500],
            expires_at=utcnow() + timedelta(seconds=settings.LTI_STATE_TTL_SECONDS),
        )
    )
    db.commit()
    return state, nonce


def consume_login_state(db: Session, state: str, platform_id: int) -> LtiLoginState:
    now = utcnow()
    updated = (
        db.query(LtiLoginState)
        .filter(
            LtiLoginState.state == state,
            LtiLoginState.platform_id == platform_id,
            LtiLoginState.consumed_at.is_(None),
            LtiLoginState.expires_at >= now,
        )
        .update({LtiLoginState.consumed_at: now}, synchronize_session=False)
    )
    db.commit()
    if updated != 1:
        raise LTIError("This launch request has expired or was already used.")
    return db.query(LtiLoginState).filter(LtiLoginState.state == state).first()


def cleanup_expired(db: Session) -> None:
    cutoff = utcnow() - timedelta(days=1)
    db.query(LtiLoginState).filter(LtiLoginState.expires_at < cutoff).delete(
        synchronize_session=False
    )
    db.commit()


def build_login_redirect(
    platform: LtiPlatform,
    *,
    state: str,
    nonce: str,
    login_hint: str,
    launch_url: str,
) -> str:
    params = {
        "response_type": "id_token",
        "response_mode": "form_post",
        "scope": "openid",
        "prompt": "none",
        "client_id": platform.client_id,
        "redirect_uri": launch_url,
        "login_hint": login_hint,
        "state": state,
        "nonce": nonce,
        "lti_deployment_id": platform.deployment_id,
    }
    return f"{platform.auth_login_url}?{urlencode(params)}"


def _get_provider(db: Session, platform: LtiPlatform) -> IdentityProvider:
    provider = None
    if platform.identity_provider_id:
        provider = (
            db.query(IdentityProvider)
            .filter(IdentityProvider.id == platform.identity_provider_id)
            .first()
        )
    if provider is None:
        provider = (
            db.query(IdentityProvider)
            .filter(IdentityProvider.name == f"LTI: {platform.name}")
            .first()
        )
    if provider is None:
        provider = IdentityProvider(
            name=f"LTI: {platform.name}"[:120],
            kind="lti",
            enabled=True,
            is_default=False,
            config=json.dumps(
                {
                    "auto_provision": True,
                    "auto_approve": True,
                    "default_role": "student",
                    "link_existing_by_email": False,
                }
            ),
        )
        db.add(provider)
        db.flush()
    platform.identity_provider_id = provider.id
    db.commit()
    return provider


def validate_launch_token(platform: LtiPlatform, id_token: str, nonce: str) -> dict:
    if not id_token:
        raise LTIError("The launch did not include an id_token.")
    try:
        client = jwt.PyJWKClient(
            platform.jwks_url,
            timeout=settings.SSO_HTTP_TIMEOUT_SECONDS,
            ssl_context=_tls_context(),
        )
        signing_key = client.get_signing_key_from_jwt(id_token)
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=ALLOWED_SIGNING_ALGORITHMS,
            audience=platform.client_id,
            issuer=platform.issuer,
            options={"require": ["exp", "iat", "sub", "nonce"]},
        )
    except Exception as exc:
        raise LTIError("The launch token could not be verified.") from exc

    if claims.get("nonce") != nonce:
        raise LTIError("The launch nonce does not match this login request.")
    if claims.get(LTI_DEPLOYMENT_CLAIM) != platform.deployment_id:
        raise LTIError("The launch is for a different LTI deployment.")
    if claims.get(LTI_MESSAGE_TYPE_CLAIM) not in ALLOWED_MESSAGE_TYPES:
        raise LTIError("This LTI message type is not supported.")
    return claims


def provision_launch_user(
    db: Session,
    platform: LtiPlatform,
    claims: dict,
) -> User:
    subject = str(claims.get("sub") or "").strip()
    if not subject:
        raise LTIError("The launch did not include a subject.")
    provider = _get_provider(db, platform)
    email = str(claims.get("email") or "").strip()
    if not email:
        digest = hashlib.sha256(f"{platform.id}:{subject}".encode()).hexdigest()[:12]
        email = f"lti-{platform.id}-{digest}@lti.invalid"
    identity = ExternalUser(
        subject=subject,
        email=email,
        email_verified=bool(claims.get("email_verified") and email),
        username_hint=str(claims.get("preferred_username") or ""),
        first_name=claims.get("given_name"),
        last_name=claims.get("family_name"),
        name=claims.get("name"),
    )
    try:
        user, provisioned, linked = provision_or_link_external_user(
            db, provider, identity
        )
    except SSOError as exc:
        raise LTIError(str(exc)) from exc
    logger.info(
        "LTI launch linked user=%s platform=%s provisioned=%s linked=%s",
        user.username,
        platform.name,
        provisioned,
        linked,
    )
    return user


def ticket_url(db: Session, user: User, platform: LtiPlatform) -> str:
    provider = _get_provider(db, platform)
    ticket = sso_flow.create_login_ticket(
        db, user=user, provider=provider, return_to="/dashboard"
    )
    return sso_flow.callback_url({"ticket": ticket, "return_to": "/dashboard"})
