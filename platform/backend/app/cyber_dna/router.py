"""Owner-only Cyber DNA v3 API.

The exercise router is deliberately not imported here. The only platform
dependencies are authentication, the database session, the feature gate, and
the rate limiter.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.consent import service as consent_service
from app.cyber_dna.service import (
    SNAPSHOT_KINDS,
    build_affinity,
    build_behavior,
    build_dna,
    build_interest,
    competency_scores,
    evidence_items,
    get_snapshot,
    list_snapshots,
    record_snapshot,
    snapshot_meta,
    snapshot_payload,
)
from app.database import get_db
from app.models import User
from app.ratelimit import create_limiter
from app.security.dependencies import require_permission
from app.security.permissions import PolicyDecision
from app.services.feature_flags import cyber_dna_v3_enabled

router = APIRouter()
limiter = create_limiter()


def _require_v3(db: Session) -> None:
    if not cyber_dna_v3_enabled(db):
        raise HTTPException(
            status_code=404,
            detail="Cyber DNA v3 is not enabled on this deployment.",
        )


def _require_consent(db: Session, user: User) -> None:
    status = consent_service.blocked_status(db, user.id, "cyber_dna")
    if status:
        raise HTTPException(
            status_code=403,
            detail=(
                "Cyber DNA consent is revoked or a revocation is in progress. "
                "Re-enable it from Privacy and consent."
            ),
            headers={"X-Consent-Status": status},
        )


@router.get("/v3/evidence", summary="Cyber DNA evidence ledger")
@limiter.limit("30/minute")
async def get_evidence(
    request: Request,
    competency_id: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("dna.view.self")),
):
    _require_v3(db)
    _require_consent(db, current_user)
    items, total = evidence_items(
        db,
        current_user.id,
        competency_id=competency_id,
        domain_id=domain,
        limit=limit,
        offset=offset,
    )
    return JSONResponse(
        content={"version": "evidence-2026.1", "items": items, "total": total},
        headers={"Cache-Control": "no-store"},
    )


@router.get("/v3/behavior", summary="Cyber DNA behavior profile")
@limiter.limit("30/minute")
async def get_behavior(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("dna.view.self")),
):
    _require_v3(db)
    _require_consent(db, current_user)
    return JSONResponse(
        content=build_behavior(db, current_user.id),
        headers={"Cache-Control": "no-store"},
    )


@router.get("/v3/interest", summary="Cyber DNA interest vector")
@limiter.limit("30/minute")
async def get_interest(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("dna.view.self")),
):
    _require_v3(db)
    _require_consent(db, current_user)
    return JSONResponse(
        content=build_interest(db, current_user.id),
        headers={"Cache-Control": "no-store"},
    )


@router.get("/v3/affinity", summary="Cyber DNA career affinity")
@limiter.limit("20/minute")
async def get_affinity(
    request: Request,
    pathway_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("dna.view.self")),
):
    _require_v3(db)
    _require_consent(db, current_user)
    from app.security.policy import require_allowed

    require_allowed(db, current_user, "career_affinity.view.self")
    try:
        return JSONResponse(
            content=build_affinity(db, current_user.id, pathway_id=pathway_id),
            headers={"Cache-Control": "no-store"},
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/v3/competencies", summary="Cyber DNA competency scores")
@limiter.limit("30/minute")
async def get_competencies(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("dna.view.self")),
):
    _require_v3(db)
    _require_consent(db, current_user)
    from app.security.policy import require_allowed

    require_allowed(db, current_user, "competency.view.self")
    return JSONResponse(
        content={
            "version": "evidence-2026.1",
            "competencies": competency_scores(db, current_user.id),
        },
        headers={"Cache-Control": "no-store"},
    )


@router.get("/v3/dna", summary="Cyber DNA learner payload")
@limiter.limit("20/minute")
async def get_dna(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("dna.view.self")),
):
    _require_v3(db)
    _require_consent(db, current_user)
    return JSONResponse(
        content=build_dna(db, current_user.id),
        headers={"Cache-Control": "no-store"},
    )


@router.post("/v3/snapshots", summary="Record a Cyber DNA snapshot")
@limiter.limit("10/minute")
async def create_snapshot(
    request: Request,
    kind: str = Query(
        ...,
        pattern="^(behavior_profile|interest_profile|career_affinity)$",
    ),
    pathway_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("dna.view.self")),
):
    _require_v3(db)
    _require_consent(db, current_user)
    if kind == "career_affinity":
        from app.security.policy import require_allowed

        require_allowed(db, current_user, "career_affinity.view.self")
    if kind == "behavior_profile":
        payload = build_behavior(db, current_user.id)
    elif kind == "interest_profile":
        payload = build_interest(db, current_user.id)
    else:
        affinity = build_affinity(db, current_user.id, pathway_id=pathway_id)
        if pathway_id:
            if not affinity.get("pathways"):
                raise HTTPException(status_code=404, detail="Pathway not found.")
            payload = {
                **affinity["pathways"][0],
                "version": affinity["version"],
                "gate": affinity["gate"],
                "weights": affinity["pathways"][0].get("weights", {}),
            }
        else:
            payload = affinity
    row, _ = record_snapshot(db, current_user.id, kind, payload)
    return JSONResponse(
        content={
            "snapshot": snapshot_meta(row),
            "payload": payload,
        },
        headers={
            "Cache-Control": "no-store",
            "X-OCR-Snapshot-ID": str(row.id),
            "X-OCR-Snapshot-SHA256": row.content_sha256,
        },
    )


@router.get("/v3/snapshots", summary="List Cyber DNA snapshots")
@limiter.limit("30/minute")
async def get_snapshots(
    request: Request,
    kind: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("dna.view.self")),
):
    _require_v3(db)
    _require_consent(db, current_user)
    if kind and kind not in SNAPSHOT_KINDS:
        raise HTTPException(status_code=422, detail="Unknown snapshot kind.")
    rows = list_snapshots(db, current_user.id, kind=kind, limit=limit)
    return JSONResponse(
        content={"snapshots": [snapshot_meta(row) for row in rows]},
        headers={"Cache-Control": "no-store"},
    )


@router.get("/v3/snapshots/{snapshot_id}", summary="Cyber DNA snapshot")
@limiter.limit("30/minute")
async def get_one_snapshot(
    request: Request,
    snapshot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("dna.view.self")),
):
    _require_v3(db)
    _require_consent(db, current_user)
    row = get_snapshot(db, current_user.id, snapshot_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Snapshot not found.")
    return JSONResponse(
        content={
            "snapshot": snapshot_meta(row),
            "payload": snapshot_payload(row),
        },
        headers={"Cache-Control": "no-store"},
    )
