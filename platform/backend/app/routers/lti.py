"""LTI 1.3 platform registration, login redirect, and launch exchange."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_admin_user
from app.config import settings
from app.crypto import encrypt_secret
from app.database import get_db
from app.models import (
    ExternalIdentity,
    IdentityProvider,
    LtiLink,
    LtiPlatform,
    LtiScore,
    User,
)
from app.ratelimit import create_limiter
from app.services import lti as lti_service
from app.services import sso_flow

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = create_limiter()


class LtiPlatformCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    issuer: str = Field(..., min_length=1, max_length=255)
    client_id: str = Field(..., min_length=1, max_length=255)
    deployment_id: str = Field(..., min_length=1, max_length=255)
    auth_login_url: str = Field(..., min_length=1, max_length=500)
    token_url: str = Field(..., min_length=1, max_length=500)
    jwks_url: str = Field(..., min_length=1, max_length=500)
    private_key: str | None = Field(None, max_length=12000)
    enabled: bool = True


class LtiScoreRequest(BaseModel):
    user_id: int
    score: float = Field(..., ge=0)
    max_score: float = Field(..., gt=0)
    reason: str = Field(..., min_length=3, max_length=500)


class LtiLineItemRequest(BaseModel):
    label: str = Field(..., min_length=1, max_length=255)
    max_score: float = Field(..., gt=0)


class LtiPlatformUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    issuer: str | None = Field(None, min_length=1, max_length=255)
    client_id: str | None = Field(None, min_length=1, max_length=255)
    deployment_id: str | None = Field(None, min_length=1, max_length=255)
    auth_login_url: str | None = Field(None, min_length=1, max_length=500)
    token_url: str | None = Field(None, min_length=1, max_length=500)
    jwks_url: str | None = Field(None, min_length=1, max_length=500)
    private_key: str | None = Field(None, max_length=12000)
    enabled: bool | None = None


def _validate_platform(payload: LtiPlatformCreate | LtiPlatformUpdate) -> None:
    allow_http = settings.SSO_ALLOW_INSECURE_HTTP
    for field in ("auth_login_url", "token_url", "jwks_url"):
        value = getattr(payload, field, None)
        if value is not None and not lti_service.valid_lti_url(
            value, allow_http=allow_http
        ):
            raise HTTPException(
                status_code=400,
                detail=f"{field} must be an http(s) URL without a fragment.",
            )
    for field in ("issuer", "client_id", "deployment_id"):
        value = getattr(payload, field, None)
        if value is not None and not str(value).strip():
            raise HTTPException(status_code=400, detail=f"{field} is required.")


def _serialize(platform: LtiPlatform) -> dict:
    return {
        "id": platform.id,
        "name": platform.name,
        "issuer": platform.issuer,
        "client_id": platform.client_id,
        "deployment_id": platform.deployment_id,
        "auth_login_url": platform.auth_login_url,
        "token_url": platform.token_url,
        "jwks_url": platform.jwks_url,
        "enabled": bool(platform.enabled),
        "has_private_key": bool(platform.private_key),
        "created_at": platform.created_at.isoformat() if platform.created_at else None,
        "updated_at": platform.updated_at.isoformat() if platform.updated_at else None,
    }


@router.get("/admin/platforms")
async def list_platforms(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    rows = db.query(LtiPlatform).order_by(LtiPlatform.name).all()
    return {"platforms": [_serialize(row) for row in rows]}


@router.post("/admin/platforms", status_code=201)
async def create_platform(
    payload: LtiPlatformCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    _validate_platform(payload)
    exists = (
        db.query(LtiPlatform)
        .filter(
            LtiPlatform.issuer == payload.issuer.strip(),
            LtiPlatform.client_id == payload.client_id.strip(),
            LtiPlatform.deployment_id == payload.deployment_id.strip(),
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="This LTI deployment is already registered.")
    platform = LtiPlatform(
        name=payload.name.strip(),
        issuer=payload.issuer.strip(),
        client_id=payload.client_id.strip(),
        deployment_id=payload.deployment_id.strip(),
        auth_login_url=payload.auth_login_url.strip(),
        token_url=payload.token_url.strip(),
        jwks_url=payload.jwks_url.strip(),
        private_key=(
            encrypt_secret(payload.private_key.strip())
            if (payload.private_key or "").strip() else None
        ),
        enabled=payload.enabled,
    )
    db.add(platform)
    db.commit()
    db.refresh(platform)
    # Create/reuse the local identity-provider row now so the launch flow never
    # has to do this on the hot path.
    lti_service._get_provider(db, platform)
    return _serialize(platform)


@router.patch("/admin/platforms/{platform_id}")
async def update_platform(
    platform_id: int,
    payload: LtiPlatformUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    _validate_platform(payload)
    platform = db.query(LtiPlatform).filter(LtiPlatform.id == platform_id).first()
    if platform is None:
        raise HTTPException(status_code=404, detail="LTI platform not found")
    for field in (
        "name", "issuer", "client_id", "deployment_id",
        "auth_login_url", "token_url", "jwks_url",
    ):
        value = getattr(payload, field)
        if value is not None:
            setattr(platform, field, value.strip())
    if payload.private_key is not None:
        value = payload.private_key.strip()
        platform.private_key = encrypt_secret(value) if value else None
    if payload.enabled is not None:
        platform.enabled = payload.enabled
    db.commit()
    db.refresh(platform)
    return _serialize(platform)


@router.get("/admin/links")
async def list_links(
    platform_id: int | None = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    query = db.query(LtiLink).order_by(LtiLink.updated_at.desc())
    if platform_id is not None:
        query = query.filter(LtiLink.platform_id == platform_id)
    rows = query.limit(200).all()
    return {
        "links": [
            {
                "id": link.id,
                "platform_id": link.platform_id,
                "resource_link_id": link.resource_link_id,
                "context_id": link.context_id,
                "context_title": link.context_title,
                "title": link.title,
                "lab_id": link.lab_id,
                "has_lineitem": bool(link.ags_lineitem_url),
                "updated_at": link.updated_at.isoformat() if link.updated_at else None,
            }
            for link in rows
        ]
    }


@router.get("/admin/links/{link_id}/scores")
async def list_link_scores(
    link_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    link = db.query(LtiLink).filter(LtiLink.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=404, detail="LTI link not found")
    rows = (
        db.query(LtiScore)
        .filter(LtiScore.link_id == link.id)
        .order_by(LtiScore.created_at.desc())
        .limit(100)
        .all()
    )
    return {
        "scores": [
            {
                "id": row.id,
                "user_id": row.user_id,
                "reviewer_id": row.reviewer_id,
                "score": row.score,
                "max_score": row.max_score,
                "status": row.status,
                "reason": row.reason,
                "lms_response": row.lms_response,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]
    }


@router.post("/admin/links/{link_id}/lineitem")
async def create_link_lineitem(
    link_id: int,
    payload: LtiLineItemRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    link = db.query(LtiLink).filter(LtiLink.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=404, detail="LTI link not found")
    platform = (
        db.query(LtiPlatform).filter(LtiPlatform.id == link.platform_id).first()
    )
    if platform is None or not platform.enabled:
        raise HTTPException(status_code=404, detail="LTI platform not found")
    try:
        lineitem = lti_service.ensure_lineitem(
            db,
            platform,
            link,
            label=payload.label,
            max_score=payload.max_score,
        )
    except lti_service.LTIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"lineitem_url": lineitem}


@router.get("/admin/links/{link_id}/results")
async def get_link_results(
    link_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    link = db.query(LtiLink).filter(LtiLink.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=404, detail="LTI link not found")
    platform = (
        db.query(LtiPlatform).filter(LtiPlatform.id == link.platform_id).first()
    )
    if platform is None or not platform.enabled:
        raise HTTPException(status_code=404, detail="LTI platform not found")
    try:
        return lti_service.get_results(platform, link)
    except lti_service.LTIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/admin/links/{link_id}/score")
async def post_link_score(
    link_id: int,
    payload: LtiScoreRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Post a reviewed score to the LMS and record the attempt."""
    link = db.query(LtiLink).filter(LtiLink.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=404, detail="LTI link not found")
    platform = (
        db.query(LtiPlatform).filter(LtiPlatform.id == link.platform_id).first()
    )
    if platform is None or not platform.enabled:
        raise HTTPException(status_code=404, detail="LTI platform not found")
    if payload.score > payload.max_score:
        raise HTTPException(status_code=400, detail="Score cannot exceed max_score")
    user = db.query(User).filter(User.id == payload.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Learner not found")

    try:
        lti_service.ensure_lineitem(
            db,
            platform,
            link,
            label=link.title or "OpenCyberRange exercise",
            max_score=payload.max_score,
        )
        subject = lti_service.subject_for_user(db, platform, user.id)
        response = lti_service.post_score(
            platform,
            link,
            subject=subject,
            score=payload.score,
            max_score=payload.max_score,
        )
        status = "posted"
        lms_response = response.get("body") or f"HTTP {response['status_code']}"
    except lti_service.LTIError as exc:
        status = "failed"
        lms_response = str(exc)[:2000]

    # The ledger row is written once, after the attempt, so it remains
    # append-only even when the LMS rejects the score.
    record = LtiScore(
        link_id=link.id,
        user_id=user.id,
        reviewer_id=admin.id,
        score=payload.score,
        max_score=payload.max_score,
        status=status,
        reason=payload.reason.strip(),
        lms_response=lms_response,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    if status != "posted":
        raise HTTPException(status_code=502, detail=lms_response)
    return {"status": status, "score_id": record.id}


@router.post("/admin/platforms/{platform_id}/test")
async def test_platform(
    platform_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    platform = db.query(LtiPlatform).filter(LtiPlatform.id == platform_id).first()
    if platform is None:
        raise HTTPException(status_code=404, detail="LTI platform not found")
    try:
        return lti_service.test_platform_keys(platform)
    except lti_service.LTIError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/admin/platforms/{platform_id}", status_code=204)
async def delete_platform(
    platform_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    platform = db.query(LtiPlatform).filter(LtiPlatform.id == platform_id).first()
    if platform is None:
        raise HTTPException(status_code=404, detail="LTI platform not found")
    db.query(lti_service.LtiLoginState).filter(
        lti_service.LtiLoginState.platform_id == platform.id
    ).delete(synchronize_session=False)
    provider = None
    if platform.identity_provider_id:
        provider = (
            db.query(IdentityProvider)
            .filter(IdentityProvider.id == platform.identity_provider_id)
            .first()
        )
    db.delete(platform)
    if provider is not None:
        has_links = (
            db.query(ExternalIdentity)
            .filter(ExternalIdentity.provider_id == provider.id)
            .first()
        )
        if has_links is None:
            db.delete(provider)
    db.commit()


@router.get("/login")
@limiter.limit("30/minute")
async def lti_login(
    request: Request,
    iss: str,
    login_hint: str = "",
    target_link_uri: str = "/dashboard",
    lti_deployment_id: str = "",
    client_id: str = "",
    db: Session = Depends(get_db),
):
    """OIDC third-party initiated login from the LMS."""
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id is required")
    platform = (
        db.query(LtiPlatform)
        .filter(
            LtiPlatform.issuer == iss,
            LtiPlatform.client_id == client_id,
        )
        .first()
    )
    if platform is None or not platform.enabled:
        raise HTTPException(status_code=404, detail="LTI platform not found")
    if lti_deployment_id and lti_deployment_id != platform.deployment_id:
        raise HTTPException(status_code=400, detail="Unknown LTI deployment")
    lti_service.cleanup_expired(db)
    state, nonce = lti_service.create_login_state(
        db, platform=platform, target_link_uri=target_link_uri
    )
    launch_url = f"{sso_flow.public_base_url()}/api/lti/launch"
    url = lti_service.build_login_redirect(
        platform,
        state=state,
        nonce=nonce,
        login_hint=login_hint,
        launch_url=launch_url,
    )
    return RedirectResponse(url, status_code=302)


@router.post("/launch")
@limiter.limit("60/minute")
async def lti_launch(
    request: Request,
    id_token: str = Form(""),
    state: str = Form(""),
    db: Session = Depends(get_db),
):
    """Validate the LMS launch and hand off to the normal SPA exchange."""
    if not state:
        raise HTTPException(status_code=400, detail="Missing launch state")
    state_row = db.query(lti_service.LtiLoginState).filter(
        lti_service.LtiLoginState.state == state
    ).first()
    if state_row is None:
        raise HTTPException(status_code=400, detail="Unknown launch state")
    platform = (
        db.query(LtiPlatform)
        .filter(LtiPlatform.id == state_row.platform_id)
        .first()
    )
    if platform is None or not platform.enabled:
        raise HTTPException(status_code=404, detail="LTI platform not found")
    try:
        state_row = lti_service.consume_login_state(db, state, platform.id)
        claims = lti_service.validate_launch_token(
            platform, id_token, state_row.nonce
        )
        user = lti_service.provision_launch_user(db, platform, claims)
        lti_service.record_launch_link(db, platform, claims)
        target = lti_service.ticket_url(db, user, platform)
    except lti_service.LTIError as exc:
        logger.warning("LTI launch rejected for platform %s: %s", platform.name, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RedirectResponse(target, status_code=302)
