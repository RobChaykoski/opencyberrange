"""Public OIDC single sign-on flow.

Flow state and one-time tickets live in PostgreSQL, so the login can start on
one API replica and finish on another. No process-local session is used.
"""

from __future__ import annotations

import logging
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import IdentityProvider, User
from app.ratelimit import create_limiter
from app.services.activity import EventTypes, log_activity
from app.services import oidc

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = create_limiter()


class SsoExchangeRequest(BaseModel):
    ticket: str = Field(..., min_length=10, max_length=200)


def _provider(db: Session, provider_id: int) -> IdentityProvider:
    row = db.query(IdentityProvider).filter(IdentityProvider.id == provider_id).first()
    if row is None or not row.enabled:
        raise HTTPException(status_code=404, detail="Identity provider not found")
    if row.kind != "oidc":
        raise HTTPException(status_code=400, detail="This provider is not configured for OIDC")
    return row


def _frontend_error(code: str) -> RedirectResponse:
    return RedirectResponse(
        f"{oidc.frontend_base_url()}/sso/callback?{urlencode({'error': code})}",
        status_code=302,
    )


@router.get("/providers")
async def list_sso_providers(db: Session = Depends(get_db)):
    """List enabled OIDC providers for the login screen."""
    rows = (
        db.query(IdentityProvider)
        .filter(IdentityProvider.enabled == True, IdentityProvider.kind == "oidc")
        .order_by(IdentityProvider.is_default.desc(), IdentityProvider.name)
        .all()
    )
    return {
        "providers": [
            {
                "id": row.id,
                "name": row.name,
                "kind": row.kind,
                "is_default": bool(row.is_default),
                "login_path": f"/api/auth/sso/oidc/{row.id}/login",
            }
            for row in rows
        ]
    }


@router.get("/oidc/{provider_id}/login")
@limiter.limit("30/minute")
async def oidc_login(
    request: Request,
    provider_id: int,
    return_to: str = "/dashboard",
    db: Session = Depends(get_db),
):
    provider = _provider(db, provider_id)
    oidc.cleanup_expired(db)
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
        return RedirectResponse(
            f"{oidc.frontend_base_url()}/login?sso_error=unavailable",
            status_code=302,
        )
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
    provider = _provider(db, provider_id)
    if error:
        logger.info("OIDC provider %s returned error=%s", provider.name, error)
        return _frontend_error("access_denied")
    if not code or not state:
        return _frontend_error("invalid_request")

    client_ip = request.client.host if request.client else None
    try:
        state_row = oidc.consume_login_state(db, state, provider.id)
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
        oidc.record_login(db, user, client_ip)
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
        ticket = oidc.create_login_ticket(
            db, user=user, provider=provider, return_to=state_row.return_to
        )
        log_activity(
            db,
            EventTypes.SSO_LOGIN_SUCCESS,
            actor_id=user.id,
            target_type="identity_provider",
            target_id=provider.id,
            target_label=provider.name,
            detail={"provisioned": provisioned, "linked": linked},
            ip_address=client_ip,
        )
        if provisioned:
            log_activity(
                db,
                EventTypes.SSO_USER_PROVISIONED,
                actor_id=user.id,
                target_type="user",
                target_id=user.id,
                target_label=user.username,
                detail={"provider": provider.name},
                ip_address=client_ip,
            )
        elif linked:
            log_activity(
                db,
                EventTypes.SSO_ACCOUNT_LINKED,
                actor_id=user.id,
                target_type="user",
                target_id=user.id,
                target_label=user.username,
                detail={"provider": provider.name},
                ip_address=client_ip,
            )
    except oidc.OIDCError as exc:
        logger.warning("OIDC callback failed for provider %s: %s", provider.name, exc)
        return _frontend_error("sso_failed")
    except Exception:
        logger.exception("Unexpected OIDC callback failure for provider %s", provider.name)
        db.rollback()
        return _frontend_error("sso_failed")

    params = urlencode(
        {
            "ticket": ticket,
            "return_to": oidc.sanitize_return_to(state_row.return_to),
        }
    )
    return RedirectResponse(
        f"{oidc.frontend_base_url()}/sso/callback?{params}",
        status_code=302,
    )


@router.post("/exchange")
@limiter.limit("30/minute")
async def exchange_ticket(
    request: Request,
    payload: SsoExchangeRequest,
    db: Session = Depends(get_db),
):
    """Exchange the one-time callback ticket for the platform JWT."""
    try:
        ticket = oidc.consume_login_ticket(db, payload.ticket)
    except oidc.OIDCError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = db.query(User).filter(User.id == ticket.user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=403, detail="Account is not active")
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="Account is awaiting administrator approval")

    client_ip = request.client.host if request.client else None
    oidc.record_login(db, user, client_ip)
    response = oidc.login_payload(user, provider_id=ticket.provider_id)
    response["return_to"] = ticket.return_to or "/dashboard"
    return JSONResponse(response, headers={"Cache-Control": "no-store"})
