"""Hosted Open Badges 3.0 issuer, credentials, and status endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_active_user, get_current_admin_user
from app.database import get_db
from app.models import (
    Competition,
    CompetitionParticipant,
    OpenBadgeCredential,
    User,
)
from app.services import badge_image, open_badges, settings_service
from app.services.activity import EventTypes, log_activity

router = APIRouter()


class IssueRequest(BaseModel):
    track_slug: str = Field(..., min_length=1, max_length=100)
    level_id: int
    include_name: bool = False


class EventIssueRequest(BaseModel):
    competition_id: int
    award: str = Field(..., min_length=1, max_length=40)
    include_name: bool = False


class ConsentRequest(BaseModel):
    include_name: bool


class RevokeRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class BadgeSettingsUpdate(BaseModel):
    issuer_name: str = Field(..., min_length=1, max_length=120)
    issuer_url: str = Field("", max_length=500)
    confirm_change: bool = False


def _credential_or_404(db: Session, jti: str) -> OpenBadgeCredential:
    row = (
        db.query(OpenBadgeCredential)
        .filter(OpenBadgeCredential.jti == jti)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Credential not found")
    return row


@router.get("/admin/badges/settings")
def badge_settings(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    jwks = open_badges.public_jwks(db)
    current = jwks["keys"][0] if jwks["keys"] else {}
    count = db.query(OpenBadgeCredential).count()
    return {
        "issuer_name": open_badges.issuer_name(db),
        "issuer_url": open_badges.issuer_url(db),
        "current_kid": current.get("kid"),
        "signing_keys": len(jwks["keys"]),
        "credential_count": count,
    }


@router.put("/admin/badges/settings")
def update_badge_settings(
    payload: BadgeSettingsUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    url = payload.issuer_url.strip().rstrip("/")
    if url and not url.startswith(("https://", "http://")):
        raise HTTPException(status_code=400, detail="Issuer URL must be http(s)")
    current_url = (
        settings_service.get_setting_fresh(db, "open_badge_issuer_url", "") or ""
    ).strip().rstrip("/")
    if (
        url != current_url
        and db.query(OpenBadgeCredential).count()
        and not payload.confirm_change
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Credentials already exist at this issuer URL. Confirm the change: "
                "older credentials keep their original issuer and status location."
            ),
        )
    settings_service.set_setting(
        db, "open_badge_issuer_name", payload.issuer_name.strip()
    )
    settings_service.set_setting(db, "open_badge_issuer_url", url)
    log_activity(
        db,
        EventTypes.OPEN_BADGE_SETTINGS_CHANGED,
        actor_id=admin.id,
        target_type="platform",
        detail={"issuer_name": payload.issuer_name.strip(), "issuer_url": url},
    )
    return {
        "issuer_name": open_badges.issuer_name(db),
        "issuer_url": open_badges.issuer_url(db),
    }


@router.post("/admin/badges/rotate-key")
def rotate_badge_key(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    jwk = open_badges.rotate_key(db)
    log_activity(
        db,
        EventTypes.OPEN_BADGE_KEY_ROTATED,
        actor_id=admin.id,
        target_type="platform",
        detail={"kid": jwk.get("kid")},
    )
    return {"kid": jwk.get("kid"), "keys": len(open_badges.public_jwks(db)["keys"])}


@router.get("/admin/badges")
def list_badges(
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    rows = (
        db.query(OpenBadgeCredential)
        .order_by(OpenBadgeCredential.issued_at.desc())
        .limit(min(max(limit, 1), 500))
        .all()
    )
    return {
        "credentials": [
            {
                "id": row.id,
                "jti": row.jti,
                "certificate_id": row.certificate_id,
                "username": row.user.username if row.user else None,
                "achievement_name": row.achievement_name,
                "issued_at": row.issued_at.isoformat() if row.issued_at else None,
                "status": open_badges.credential_status(row),
                "revocation_reason": row.revocation_reason,
            }
            for row in rows
        ]
    }


@router.get("/badges/issuer")
def issuer_profile(db: Session = Depends(get_db)):
    issuer = open_badges.issuer_url(db)
    return {
        "id": issuer,
        "type": ["Profile"],
        "name": open_badges.issuer_name(db),
        "url": issuer,
        "jwks_uri": f"{issuer}/api/badges/issuer/jwks",
    }


@router.get("/badges/issuer/jwks")
def issuer_jwks(db: Session = Depends(get_db)):
    return open_badges.public_jwks(db)


@router.get("/badges/achievements/{certificate_id}")
def achievement_definition(certificate_id: str, db: Session = Depends(get_db)):
    row = (
        db.query(OpenBadgeCredential)
        .filter(OpenBadgeCredential.certificate_id == certificate_id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    payload = open_badges.credential_payload(db, row)
    return payload["vc"]["credentialSubject"]["achievement"]


@router.get("/badges/achievements/{certificate_id}/image.png")
def achievement_image(certificate_id: str, db: Session = Depends(get_db)):
    row = (
        db.query(OpenBadgeCredential)
        .filter(OpenBadgeCredential.certificate_id == certificate_id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    is_event = bool(row.track_slug and row.track_slug.startswith("event:"))
    png = badge_image.badge_png(
        row.achievement_name,
        subtitle="Event award" if is_event else "Level credential",
        footer=row.certificate_id[-10:],
        kind="event" if is_event else "level",
    )
    return Response(
        content=png,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/badges/credentials/{jti}")
def hosted_credential(jti: str, db: Session = Depends(get_db)):
    row = _credential_or_404(db, jti)
    return {
        "jti": row.jti,
        "status": open_badges.credential_status(row),
        "format": "jwt_vc_json",
        "credential": open_badges.sign_credential(db, row),
    }


@router.get("/badges/credentials/{jti}/jwt")
def hosted_credential_jwt(jti: str, db: Session = Depends(get_db)):
    row = _credential_or_404(db, jti)
    token = open_badges.sign_credential(db, row)
    return Response(
        content=token,
        media_type="application/vc+jwt",
        headers={
            "Cache-Control": "no-store",
            "Content-Disposition": f'inline; filename="{row.jti}.jwt"',
        },
    )


@router.get("/badges/credentials/{jti}/status")
def credential_status(jti: str, db: Session = Depends(get_db)):
    row = _credential_or_404(db, jti)
    return {
        "jti": row.jti,
        "status": open_badges.credential_status(row),
        "revoked_at": row.revoked_at.isoformat() if row.revoked_at else None,
    }


@router.get("/badges/mine")
def my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    issuer = open_badges.issuer_url(db)
    rows = (
        db.query(OpenBadgeCredential)
        .filter(OpenBadgeCredential.user_id == current_user.id)
        .order_by(OpenBadgeCredential.issued_at.desc())
        .all()
    )
    return {
        "credentials": [
            {
                "id": row.id,
                "jti": row.jti,
                "certificate_id": row.certificate_id,
                "achievement_name": row.achievement_name,
                "issued_at": row.issued_at.isoformat() if row.issued_at else None,
                "status": open_badges.credential_status(row),
                "recipient_name_opt_in": bool(row.recipient_name_opt_in),
                "url": f"{issuer}/api/badges/credentials/{row.jti}",
                "status_url": f"{issuer}/api/badges/credentials/{row.jti}/status",
            }
            for row in rows
        ]
    }


@router.post("/badges/issue", status_code=201)
def issue_badge(
    payload: IssueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        row = open_badges.issue_badge(
            db,
            current_user,
            payload.track_slug,
            payload.level_id,
            include_name=payload.include_name,
        )
    except ValueError as exc:
        reason = str(exc)
        if reason in ("track_not_found", "level_not_found"):
            raise HTTPException(status_code=404, detail="Certificate source not found") from exc
        raise HTTPException(
            status_code=409,
            detail="Complete every required exercise in this level before requesting a badge.",
        ) from exc
    log_activity(
        db,
        EventTypes.OPEN_BADGE_ISSUED,
        actor_id=current_user.id,
        target_type="user",
        target_id=current_user.id,
        target_label=current_user.username,
        detail={"jti": row.jti, "certificate_id": row.certificate_id},
    )
    return {
        "id": row.id,
        "jti": row.jti,
        "status": open_badges.credential_status(row),
        "credential": open_badges.sign_credential(db, row),
    }


@router.post("/badges/events/issue", status_code=201)
def issue_event_badge(
    payload: EventIssueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition = (
        db.query(Competition)
        .filter(Competition.id == payload.competition_id)
        .first()
    )
    if competition is None:
        raise HTTPException(status_code=404, detail="Event not found")
    participant = (
        db.query(CompetitionParticipant)
        .filter(
            CompetitionParticipant.competition_id == competition.id,
            CompetitionParticipant.user_id == current_user.id,
        )
        .first()
    )
    if participant is None:
        raise HTTPException(
            status_code=403, detail="Join the event before requesting a badge."
        )
    if not current_user.is_approved:
        raise HTTPException(status_code=403, detail="Account is not approved.")
    try:
        row = open_badges.issue_event_badge(
            db,
            current_user,
            competition,
            payload.award.strip().lower(),
            include_name=payload.include_name,
        )
    except ValueError as exc:
        if str(exc) == "event_not_ended":
            raise HTTPException(
                status_code=409,
                detail="Event badges are available after the event ends.",
            ) from exc
        raise HTTPException(
            status_code=404, detail="That event award is not available."
        ) from exc
    log_activity(
        db,
        EventTypes.OPEN_BADGE_ISSUED,
        actor_id=current_user.id,
        target_type="user",
        target_id=current_user.id,
        target_label=current_user.username,
        detail={
            "jti": row.jti,
            "certificate_id": row.certificate_id,
            "event_id": competition.id,
            "award": payload.award,
        },
    )
    return {
        "id": row.id,
        "jti": row.jti,
        "status": open_badges.credential_status(row),
        "credential": open_badges.sign_credential(db, row),
    }


@router.post("/badges/{badge_id}/consent")
def badge_consent(
    badge_id: int,
    payload: ConsentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    row = (
        db.query(OpenBadgeCredential)
        .filter(
            OpenBadgeCredential.id == badge_id,
            OpenBadgeCredential.user_id == current_user.id,
        )
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Badge not found")
    if open_badges.credential_status(row) == "revoked":
        raise HTTPException(status_code=409, detail="Revoked credentials cannot be changed")
    row.recipient_name_opt_in = bool(payload.include_name)
    db.commit()
    log_activity(
        db,
        EventTypes.OPEN_BADGE_CONSENT_CHANGED,
        actor_id=current_user.id,
        target_type="user",
        target_id=current_user.id,
        target_label=row.jti,
        detail={"include_name": bool(row.recipient_name_opt_in)},
    )
    return {"ok": True, "recipient_name_opt_in": bool(row.recipient_name_opt_in)}


@router.post("/admin/badges/{badge_id}/revoke")
def revoke_badge(
    badge_id: int,
    payload: RevokeRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    row = db.query(OpenBadgeCredential).filter(OpenBadgeCredential.id == badge_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Badge not found")
    reason = payload.reason.strip()
    if not reason:
        raise HTTPException(status_code=400, detail="A revocation reason is required")
    open_badges.revoke_badge(db, row, admin, reason)
    log_activity(
        db,
        EventTypes.OPEN_BADGE_REVOKED,
        actor_id=admin.id,
        target_type="user",
        target_id=row.user_id,
        detail={"jti": row.jti, "reason": reason},
    )
    return {"ok": True, "status": open_badges.credential_status(row)}

