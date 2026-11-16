"""Learner consent controls and administrator revocation operations."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.consent import service
from app.consent.registry import CONSENT_TYPES
from app.database import get_db
from app.models import User
from app.ratelimit import create_limiter
from app.security.dependencies import require_permission
from app.security.permissions import PolicyDecision

router = APIRouter()
limiter = create_limiter()


class ConsentRevokeRequest(BaseModel):
    version: Optional[int] = Field(None, ge=0)
    reason: Optional[str] = Field(None, max_length=500)


class ConsentGrantRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=500)


class RunJobsRequest(BaseModel):
    limit: int = Field(20, ge=1, le=100)


def _spec_or_404(consent_type: str):
    if consent_type not in CONSENT_TYPES:
        raise HTTPException(status_code=404, detail="Unknown consent type.")
    return CONSENT_TYPES[consent_type]


@router.get("/", summary="Learner consent and revocation status")
@limiter.limit("30/minute")
async def get_consent(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return service.dashboard(db, current_user.id)


@router.get("/types", summary="Available consent types")
async def get_consent_types(
    current_user: User = Depends(get_current_active_user),
):
    return {
        "types": [
            {
                "id": spec.id,
                "label": spec.label,
                "description": spec.description,
                "default_granted": spec.default_granted,
                "removed": list(spec.removed),
                "kept": list(spec.kept),
                "targets": [
                    {"service": target.service, "action": target.action}
                    for target in spec.targets
                ],
            }
            for spec in CONSENT_TYPES.values()
        ]
    }


@router.get("/revocations", summary="The learner's own revocation history")
@limiter.limit("20/minute")
async def get_own_revocations(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return {
        "revocations": service.list_revocations(
            db, user_id=current_user.id, limit=limit
        )
    }


@router.post("/{consent_type}/revoke", status_code=202)
@limiter.limit("10/minute")
async def revoke_consent(
    request: Request,
    consent_type: str,
    payload: ConsentRevokeRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Immediately block a feature and queue destructive cleanup."""
    _spec_or_404(consent_type)
    payload = payload or ConsentRevokeRequest()
    try:
        revocation = service.revoke(
            db,
            current_user.id,
            consent_type,
            actor="self",
            reason=payload.reason,
            expected_version=payload.version,
        )
    except service.ConsentConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    from app.services import security_events

    security_events.record(
        "consent.revoked",
        actor=current_user,
        target_type="consent",
        target_id=consent_type,
        target_label=consent_type,
        detail={
            "consent_type": consent_type,
            "version": getattr(revocation, "consent_version", None),
            "reason": payload.reason,
        },
    )
    security_events.mark_request_recorded()
    return {
        "message": (
            "Consent revoked. The feature is blocked immediately while derived "
            "data is removed."
        ),
        "revocation": service.revocation_payload(db, revocation),
        "state": service.state_for(db, current_user.id, consent_type),
    }


@router.post("/{consent_type}/grant")
@limiter.limit("10/minute")
async def grant_consent(
    request: Request,
    consent_type: str,
    payload: ConsentGrantRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Re-enable a feature. Previously deleted data stays deleted."""
    _spec_or_404(consent_type)
    payload = payload or ConsentGrantRequest()
    state = service.grant(
        db,
        current_user.id,
        consent_type,
        actor="self",
        reason=payload.reason,
    )
    from app.services import security_events

    security_events.record(
        "consent.granted",
        actor=current_user,
        target_type="consent",
        target_id=consent_type,
        target_label=consent_type,
        detail={
            "consent_type": consent_type,
            "version": state.get("version"),
            "reason": payload.reason,
        },
    )
    security_events.mark_request_recorded()
    return {
        "message": (
            "Consent granted. New activity may be processed again; previously "
            "deleted data is not restored."
        ),
        "state": state,
    }


# --- Administrator operations ---------------------------------------------


@router.get("/admin/revocations", summary="All revocation workflows")
async def admin_revocations(
    status: Optional[str] = Query(None),
    consent_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(
        require_permission("privacy.audit.view")
    ),
):
    if status and status not in service.REVOCATION_STATUSES:
        raise HTTPException(status_code=422, detail="Unknown revocation status.")
    if consent_type and consent_type not in CONSENT_TYPES:
        raise HTTPException(status_code=404, detail="Unknown consent type.")
    return {
        "revocations": service.list_revocations(
            db, status=status, consent_type=consent_type, limit=limit
        )
    }


@router.post("/admin/run-jobs", summary="Run due purge and verification jobs")
async def admin_run_jobs(
    payload: RunJobsRequest | None = None,
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(
        require_permission("privacy.revocation.execute")
    ),
):
    payload = payload or RunJobsRequest()
    return service.run_due_jobs(db, limit=payload.limit)


@router.post("/admin/enforce-suppressions", summary="Apply the suppression ledger")
async def admin_enforce_suppressions(
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(
        require_permission("privacy.revocation.execute")
    ),
):
    return service.enforce_suppressions(db)


@router.get("/admin/metrics", summary="Revocation verification metrics")
async def admin_metrics(
    db: Session = Depends(get_db),
    _decision: PolicyDecision = Depends(
        require_permission("privacy.audit.view")
    ),
):
    return service.metrics(db)
