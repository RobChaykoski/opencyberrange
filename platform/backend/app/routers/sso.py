"""Public single sign-on flows for OIDC, SAML, and LDAP.

Flow state and one-time tickets live in PostgreSQL, so a login can start on one
API replica and finish on another. No process-local session is used.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.database import get_db
from app.models import IdentityProvider, SsoLoginState, User
from app.ratelimit import create_limiter
from app.services import ldap_auth, oidc, saml_auth, sso_flow
from app.services.external_identity import SSOError, provision_or_link_external_user
from app.services.settings_service import get_setting_fresh

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = create_limiter()


class SsoExchangeRequest(BaseModel):
    ticket: str = Field(..., min_length=10, max_length=200)


class LdapLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=1024)
    return_to: str = Field("/dashboard", max_length=500)


def sso_enabled(db: Session) -> bool:
    """Return the deployment-wide SSO switch.

    Read fresh, not from the settings cache: an administrator who turns SSO off
    must not leave another worker accepting new SSO logins for the cache TTL.
    Local password login is deliberately not part of this switch.
    """
    raw = get_setting_fresh(db, "sso_enabled", "true")
    return str(raw or "true").strip().lower() in ("true", "1", "yes", "on")


def _require_sso_enabled(db: Session) -> None:
    if not sso_enabled(db):
        raise HTTPException(
            status_code=403,
            detail=(
                "Single sign-on is disabled for this deployment. Use local "
                "password sign-in or contact the administrator."
            ),
        )


def _provider(db: Session, provider_id: int, kind: str) -> IdentityProvider:
    _require_sso_enabled(db)
    row = db.query(IdentityProvider).filter(IdentityProvider.id == provider_id).first()
    if row is None or not row.enabled:
        raise HTTPException(status_code=404, detail="Identity provider not found")
    if row.kind != kind:
        raise HTTPException(
            status_code=400,
            detail=f"This provider is not configured for {kind.upper()}",
        )
    return row


def _frontend_error(code: str) -> RedirectResponse:
    return RedirectResponse(
        f"{sso_flow.frontend_base_url()}/sso/callback?error={code}",
        status_code=302,
    )


def _login_unavailable() -> RedirectResponse:
    return RedirectResponse(
        f"{sso_flow.frontend_base_url()}/login?sso_error=unavailable",
        status_code=302,
    )


@router.get("/providers")
async def list_sso_providers(db: Session = Depends(get_db)):
    """List enabled providers for the login screen.

    The global switch is evaluated here as well as in every flow endpoint, so
    turning SSO off removes the institution sign-in panel immediately rather
    than only rejecting the click that follows.
    """
    if not sso_enabled(db):
        return {"providers": [], "sso_enabled": False}
    rows = (
        db.query(IdentityProvider)
        .filter(IdentityProvider.enabled == True)
        .order_by(IdentityProvider.is_default.desc(), IdentityProvider.name)
        .all()
    )
    providers = []
    for row in rows:
        if row.kind == "oidc":
            login_path = f"/api/auth/sso/oidc/{row.id}/login"
        elif row.kind == "saml":
            login_path = f"/api/auth/sso/saml/{row.id}/login"
        elif row.kind == "ldap":
            login_path = None
        else:
            continue
        providers.append(
            {
                "id": row.id,
                "name": row.name,
                "kind": row.kind,
                "is_default": bool(row.is_default),
                "login_path": login_path,
            }
        )
    return {"providers": providers, "sso_enabled": True}


@router.get("/oidc/{provider_id}/login")
@limiter.limit("30/minute")
async def oidc_login(
    request: Request,
    provider_id: int,
    return_to: str = "/dashboard",
    db: Session = Depends(get_db),
):
    provider = _provider(db, provider_id, "oidc")
    sso_flow.cleanup_expired(db)
    state, nonce, _verifier, challenge = oidc.create_login_state(
        db, provider=provider, return_to=return_to
    )
    try:
        url = await run_in_threadpool(
            oidc.authorization_url,
            provider,
            state=state,
            nonce=nonce,
            code_challenge=challenge,
            redirect=oidc.redirect_uri(provider.id),
        )
    except oidc.OIDCError as exc:
        logger.warning("OIDC login start failed for provider %s: %s", provider.name, exc)
        return _login_unavailable()
    return RedirectResponse(url, status_code=302)


@router.get("/oidc/{provider_id}/callback")
@limiter.limit("30/minute")
async def oidc_callback(
    request: Request,
    provider_id: int,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    provider = _provider(db, provider_id, "oidc")
    if error:
        logger.info("OIDC provider %s returned error=%s", provider.name, error)
        return _frontend_error("access_denied")
    if not code or not state:
        return _frontend_error("invalid_request")

    client_ip = request.client.host if request.client else None
    try:
        state_row = sso_flow.consume_login_state(db, state, provider.id)
        tokens = await run_in_threadpool(
            oidc.exchange_code,
            provider,
            code=code,
            code_verifier=state_row.code_verifier,
            redirect=state_row.redirect_uri,
        )
        claims = await run_in_threadpool(
            oidc.validate_id_token, provider, tokens["id_token"], state_row.nonce
        )
        user, provisioned, linked = oidc.provision_or_link_user(
            db, provider, claims, client_ip=client_ip
        )
        if not user.is_active:
            raise oidc.OIDCError("The local account is disabled.")
        if not user.is_approved:
            return _frontend_error("pending_approval")
        sso_flow.record_login(db, user, client_ip)
        try:
            oidc.create_sso_session(
                db,
                user=user,
                provider=provider,
                id_token=tokens.get("id_token"),
                session_state=tokens.get("session_state"),
                claims=claims,
            )
        except Exception:
            logger.exception("Could not store the SSO session for logout")
        ticket = sso_flow.create_login_ticket(
            db, user=user, provider=provider, return_to=state_row.return_to
        )
        sso_flow.log_sso_login(
            db,
            provider=provider,
            user=user,
            provisioned=provisioned,
            linked=linked,
            client_ip=client_ip,
        )
    except oidc.OIDCError as exc:
        logger.warning("OIDC callback failed for provider %s: %s", provider.name, exc)
        return _frontend_error("sso_failed")
    except Exception:
        logger.exception("Unexpected OIDC callback failure for provider %s", provider.name)
        db.rollback()
        return _frontend_error("sso_failed")

    return RedirectResponse(
        sso_flow.callback_url(
            {
                "ticket": ticket,
                "return_to": sso_flow.sanitize_return_to(state_row.return_to),
            }
        ),
        status_code=302,
    )


@router.get("/saml/{provider_id}/login")
@limiter.limit("30/minute")
async def saml_login(
    request: Request,
    provider_id: int,
    return_to: str = "/dashboard",
    db: Session = Depends(get_db),
):
    provider = _provider(db, provider_id, "saml")
    sso_flow.cleanup_expired(db)
    state = sso_flow.create_flow_state(
        db,
        provider=provider,
        return_to=return_to,
        redirect_uri=saml_auth.resolved_acs_url(provider),
    )
    try:
        url, request_id = await run_in_threadpool(
            saml_auth.start_login, provider, state
        )
    except SSOError as exc:
        logger.warning("SAML login start failed for provider %s: %s", provider.name, exc)
        return _login_unavailable()

    row = db.query(SsoLoginState).filter(SsoLoginState.state == state).first()
    if row is None:
        return _login_unavailable()
    row.nonce = request_id
    db.commit()
    return RedirectResponse(url, status_code=302)


@router.post("/saml/{provider_id}/acs")
@limiter.limit("60/minute")
async def saml_acs(
    request: Request,
    provider_id: int,
    db: Session = Depends(get_db),
):
    provider = _provider(db, provider_id, "saml")
    form = await request.form()
    post_data = {str(key): str(value) for key, value in form.items()}
    relay_state = post_data.get("RelayState", "")
    if not relay_state or "SAMLResponse" not in post_data:
        return _frontend_error("invalid_request")

    client_ip = request.client.host if request.client else None
    try:
        state_row = sso_flow.consume_login_state(db, relay_state, provider.id)
        identity, _session = await run_in_threadpool(
            saml_auth.process_response, provider, post_data, state_row.nonce
        )
        user, provisioned, linked = provision_or_link_external_user(
            db, provider, identity, client_ip=client_ip
        )
        if not user.is_active:
            raise SSOError("The local account is disabled.")
        if not user.is_approved:
            return _frontend_error("pending_approval")
        sso_flow.record_login(db, user, client_ip)
        ticket = sso_flow.create_login_ticket(
            db, user=user, provider=provider, return_to=state_row.return_to
        )
        sso_flow.log_sso_login(
            db,
            provider=provider,
            user=user,
            provisioned=provisioned,
            linked=linked,
            client_ip=client_ip,
        )
    except SSOError as exc:
        logger.warning("SAML ACS failed for provider %s: %s", provider.name, exc)
        return _frontend_error("sso_failed")
    except Exception:
        logger.exception("Unexpected SAML ACS failure for provider %s", provider.name)
        db.rollback()
        return _frontend_error("sso_failed")

    return RedirectResponse(
        sso_flow.callback_url(
            {
                "ticket": ticket,
                "return_to": sso_flow.sanitize_return_to(state_row.return_to),
            }
        ),
        status_code=302,
    )


@router.post("/ldap/{provider_id}/login")
@limiter.limit("20/minute")
async def ldap_login(
    request: Request,
    provider_id: int,
    payload: LdapLoginRequest,
    db: Session = Depends(get_db),
):
    provider = _provider(db, provider_id, "ldap")
    client_ip = request.client.host if request.client else None
    try:
        identity = await run_in_threadpool(
            ldap_auth.authenticate, provider, payload.username, payload.password
        )
    except SSOError as exc:
        logger.warning("LDAP login failed for provider %s: %s", provider.name, exc)
        if exc.code == "invalid_credentials":
            raise HTTPException(
                status_code=401, detail="Invalid username or password."
            ) from exc
        raise HTTPException(
            status_code=503,
            detail="The institution directory is unavailable. Try again later.",
        ) from exc

    try:
        user, provisioned, linked = provision_or_link_external_user(
            db, provider, identity, client_ip=client_ip
        )
    except SSOError as exc:
        logger.warning("LDAP provisioning failed for provider %s: %s", provider.name, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is not active")
    if not user.is_approved:
        raise HTTPException(
            status_code=403, detail="Account is awaiting administrator approval"
        )

    sso_flow.record_login(db, user, client_ip)
    ticket = sso_flow.create_login_ticket(
        db, user=user, provider=provider, return_to=payload.return_to
    )
    sso_flow.log_sso_login(
        db,
        provider=provider,
        user=user,
        provisioned=provisioned,
        linked=linked,
        client_ip=client_ip,
    )
    return JSONResponse(
        {
            "ticket": ticket,
            "return_to": sso_flow.sanitize_return_to(payload.return_to),
        },
        headers={"Cache-Control": "no-store"},
    )


@router.post("/exchange")
@limiter.limit("30/minute")
async def exchange_ticket(
    request: Request,
    payload: SsoExchangeRequest,
    db: Session = Depends(get_db),
):
    """Exchange the one-time callback ticket for the platform JWT."""
    _require_sso_enabled(db)
    try:
        ticket = sso_flow.consume_login_ticket(db, payload.ticket)
    except SSOError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = db.query(User).filter(User.id == ticket.user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=403, detail="Account is not active")
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="Account is awaiting administrator approval")

    client_ip = request.client.host if request.client else None
    sso_flow.record_login(db, user, client_ip)
    response = sso_flow.login_payload(user, provider_id=ticket.provider_id)
    response["return_to"] = ticket.return_to or "/dashboard"
    return JSONResponse(response, headers={"Cache-Control": "no-store"})
