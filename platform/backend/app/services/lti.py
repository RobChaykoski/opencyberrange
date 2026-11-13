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
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, urlsplit

import jwt
import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.crypto import decrypt_secret, is_encrypted
from app.models import (
    ExternalIdentity,
    IdentityProvider,
    LtiLink,
    LtiLoginState,
    LtiPlatform,
    User,
)
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
LTI_AGS_CLAIM = "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint"
LTI_AGS_SCORE_SCOPE = "https://purl.imsglobal.org/spec/lti-ags/scope/score"
LTI_AGS_LINEITEM_SCOPE = "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem"
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


def test_platform_keys(platform: LtiPlatform) -> dict:
    """Fetch the registered platform's JWKS and report how many keys it has."""
    try:
        client = jwt.PyJWKClient(
            platform.jwks_url,
            timeout=settings.SSO_HTTP_TIMEOUT_SECONDS,
            ssl_context=_tls_context(),
        )
        keys = client.get_signing_keys()
    except Exception as exc:
        raise LTIError("Could not fetch the LMS signing keys.") from exc
    if not keys:
        raise LTIError("The LMS JWKS returned no signing keys.")
    return {"ok": True, "keys": len(keys), "message": f"Fetched {len(keys)} signing key(s)."}


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


def record_launch_link(
    db: Session, platform: LtiPlatform, claims: dict
) -> LtiLink | None:
    """Persist the resource link and AGS endpoints from a launch claim."""
    resource = claims.get(LTI_RESOURCE_LINK_CLAIM) or {}
    context = claims.get(LTI_CONTEXT_CLAIM) or {}
    endpoint = claims.get(LTI_AGS_CLAIM) or {}
    resource_link_id = str(resource.get("id") or "").strip()
    if not resource_link_id:
        return None
    link = (
        db.query(LtiLink)
        .filter(
            LtiLink.platform_id == platform.id,
            LtiLink.resource_link_id == resource_link_id,
        )
        .first()
    )
    if link is None:
        link = LtiLink(platform_id=platform.id, resource_link_id=resource_link_id)
        db.add(link)
    link.context_id = str(context.get("id") or "")[:255] or None
    link.context_title = str(context.get("title") or "")[:255] or None
    link.title = str(resource.get("title") or "")[:255] or None
    link.ags_lineitem_url = str(endpoint.get("lineitem") or "")[:500] or None
    link.ags_lineitems_url = str(endpoint.get("lineitems") or "")[:500] or None
    scopes = endpoint.get("scope")
    link.ags_scopes = json.dumps(scopes) if scopes else None
    db.commit()
    db.refresh(link)
    return link


def _private_key(platform: LtiPlatform) -> str:
    if not platform.private_key:
        raise LTIError("No LMS client private key is stored for this platform.")
    value = platform.private_key
    if is_encrypted(value):
        value = decrypt_secret(value)
    return value


def build_client_assertion(platform: LtiPlatform, audience: str | None = None) -> str:
    """Build the private_key_jwt assertion used for an LMS access token."""
    now = int(time.time())
    claims = {
        "iss": platform.client_id,
        "sub": platform.client_id,
        "aud": audience or platform.token_url,
        "iat": now,
        "exp": now + 300,
        "jti": uuid.uuid4().hex,
    }
    try:
        return jwt.encode(claims, _private_key(platform), algorithm="RS256")
    except Exception as exc:
        raise LTIError("Could not sign the LMS client assertion.") from exc


def get_access_token(
    platform: LtiPlatform, scopes: list[str] | tuple[str, ...]
) -> str:
    assertion = build_client_assertion(platform)
    try:
        response = requests.post(
            platform.token_url,
            data={
                "grant_type": "client_credentials",
                "client_assertion_type": (
                    "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
                ),
                "client_assertion": assertion,
                "scope": " ".join(scopes),
            },
            timeout=settings.SSO_HTTP_TIMEOUT_SECONDS,
            verify=not settings.SSO_ALLOW_INSECURE_HTTP,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise LTIError("The LMS did not issue an access token.") from exc
    token = str(payload.get("access_token") or "").strip()
    if not token:
        raise LTIError("The LMS token response did not include an access token.")
    return token


def build_score_payload(
    *,
    subject: str,
    score: float,
    max_score: float,
    timestamp: str | None = None,
) -> dict:
    return {
        "userId": subject,
        "scoreGiven": score,
        "scoreMaximum": max_score,
        "activityProgress": "Completed",
        "gradingProgress": "FullyGraded",
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def post_score(
    platform: LtiPlatform,
    link: LtiLink,
    *,
    subject: str,
    score: float,
    max_score: float,
) -> dict:
    if not link.ags_lineitem_url:
        raise LTIError("This launch did not provide an AGS line-item endpoint.")
    token = get_access_token(platform, [LTI_AGS_SCORE_SCOPE])
    url = link.ags_lineitem_url.rstrip("/") + "/scores"
    payload = build_score_payload(subject=subject, score=score, max_score=max_score)
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=settings.SSO_HTTP_TIMEOUT_SECONDS,
            verify=not settings.SSO_ALLOW_INSECURE_HTTP,
        )
    except Exception as exc:
        raise LTIError("The score passback request failed.") from exc
    if response.status_code not in (200, 201, 204):
        raise LTIError(
            f"The LMS rejected the score passback (HTTP {response.status_code})."
        )
    return {
        "status_code": response.status_code,
        "body": (response.text or "")[:2000],
    }


def subject_for_user(db: Session, platform: LtiPlatform, user_id: int) -> str:
    provider = _get_provider(db, platform)
    link = (
        db.query(ExternalIdentity)
        .filter(
            ExternalIdentity.provider_id == provider.id,
            ExternalIdentity.user_id == user_id,
        )
        .first()
    )
    if link is None:
        raise LTIError("This user is not linked to the selected LTI platform.")
    return link.subject


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
