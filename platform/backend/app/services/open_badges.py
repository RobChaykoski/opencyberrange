"""Open Badges 3.0 hosting: Ed25519 keys, JWT-VC signing, and status."""

from __future__ import annotations

import base64
import hashlib
import json
import uuid
from datetime import datetime, timezone

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from sqlalchemy.orm import Session, joinedload

from app.models import Level, OpenBadgeCredential, Track, User
from app.services import settings_service
from app.services.sso_flow import public_base_url


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def issuer_url(db: Session) -> str:
    configured = (
        settings_service.get_setting_fresh(db, "open_badge_issuer_url", "") or ""
    ).strip()
    return (configured or public_base_url()).rstrip("/")


def issuer_name(db: Session) -> str:
    return (
        settings_service.get_setting_fresh(db, "open_badge_issuer_name", "")
        or "SWOCTS Cyber Range"
    ).strip()


def _generate_private() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.generate()


def _private_pem(private: Ed25519PrivateKey) -> str:
    return private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")


def _jwk_for(private: Ed25519PrivateKey) -> dict:
    raw_public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    x = _b64url(raw_public)
    thumb_input = json.dumps(
        {"crv": "Ed25519", "kty": "OKP", "x": x}, separators=(",", ":"), sort_keys=True
    )
    kid = _b64url(hashlib.sha256(thumb_input.encode("ascii")).digest())
    return {"kty": "OKP", "crv": "Ed25519", "x": x, "kid": kid, "use": "sig", "alg": "EdDSA"}


def _key_material(db: Session) -> tuple[Ed25519PrivateKey, str, dict]:
    pem = settings_service.get_setting_fresh(db, "open_badge_signing_key", "") or ""
    if not pem:
        private = _generate_private()
        pem = _private_pem(private)
        settings_service.set_setting(db, "open_badge_signing_key", pem)
    private = serialization.load_pem_private_key(pem.encode("ascii"), password=None)
    jwk = _jwk_for(private)
    return private, jwk["kid"], jwk


def _retired_keys(db: Session) -> list[dict]:
    raw = settings_service.get_setting_fresh(db, "open_badge_retired_keys", "[]") or "[]"
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return []
    return [row for row in data if isinstance(row, dict) and row.get("kid")] if isinstance(data, list) else []


def public_jwks(db: Session) -> dict:
    _, _, current = _key_material(db)
    keys = [current]
    for row in _retired_keys(db):
        if row.get("kid") != current.get("kid"):
            keys.append(row)
    return {"keys": keys}


def rotate_key(db: Session) -> dict:
    """Keep the old public key for verification, then generate a new key."""
    _, _, current = _key_material(db)
    retired = [row for row in _retired_keys(db) if row.get("kid") != current.get("kid")]
    retired.insert(0, current)
    retired = retired[:5]
    settings_service.set_setting(
        db, "open_badge_retired_keys", json.dumps(retired, separators=(",", ":"))
    )
    private = _generate_private()
    settings_service.set_setting(db, "open_badge_signing_key", _private_pem(private))
    return _jwk_for(private)


def _subject_url(issuer: str, row: OpenBadgeCredential) -> str:
    return f"{issuer}/api/badges/subjects/{row.subject_id}"


def _recipient_name(user: User) -> str:
    name = " ".join(
        part for part in (user.first_name or "", user.last_name or "") if part
    ).strip()
    return name or user.username


def credential_payload(db: Session, row: OpenBadgeCredential) -> dict:
    issuer = issuer_url(db)
    subject = _subject_url(issuer, row)
    user = row.user if getattr(row, "user", None) else None
    achievement = {
        "id": f"{issuer}/api/badges/achievements/{row.certificate_id}",
        "type": ["Achievement"],
        "name": row.achievement_name,
        "description": row.achievement_description or row.achievement_name,
        "criteria": {
            "narrative": (
                "Completed every required exercise in this level of the "
                "SWOCTS Cyber Range."
            )
        },
    }
    credential_subject = {"id": subject, "achievement": achievement}
    if row.recipient_name_opt_in and user is not None:
        credential_subject["name"] = _recipient_name(user)
    payload = {
        "iss": issuer,
        "sub": subject,
        "jti": row.jti,
        "iat": int(row.issued_at.timestamp()) if row.issued_at else int(datetime.now(timezone.utc).timestamp()),
        "nbf": int(row.issued_at.timestamp()) if row.issued_at else int(datetime.now(timezone.utc).timestamp()),
        "vc": {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://purl.imsglobal.org/spec/ob/v3p0/context.json",
            ],
            "type": ["VerifiableCredential", "OpenBadgeCredential"],
            "name": row.achievement_name,
            "issuer": {"id": issuer, "name": issuer_name(db)},
            "validFrom": (row.issued_at or datetime.now(timezone.utc)).isoformat(),
            "credentialSubject": credential_subject,
            "evidence": [
                {
                    "id": row.evidence_url or issuer,
                    "type": ["Evidence"],
                    "narrative": "Certificate verification record",
                }
            ],
            "credentialStatus": {
                "id": f"{issuer}/api/badges/credentials/{row.jti}/status",
                "type": "OpenBadgeCredentialStatus",
            },
        },
    }
    return payload


def sign_credential(db: Session, row: OpenBadgeCredential) -> str:
    private, kid, _ = _key_material(db)
    payload = credential_payload(db, row)
    return jwt.encode(
        payload,
        private,
        algorithm="EdDSA",
        headers={"kid": kid, "typ": "JWT"},
    )


def credential_status(row: OpenBadgeCredential) -> str:
    return "revoked" if row.revoked_at else "active"


def issue_badge(
    db: Session,
    user: User,
    track_slug: str,
    level_id: int,
    *,
    include_name: bool = False,
) -> OpenBadgeCredential:
    """Issue for a completed level certificate; idempotent per learner/source."""
    from app.routers.curriculum import (
        _visible_lab_ids,
        build_level_certificate,
        get_accessible_exclusive_lab_ids,
        get_user_completions,
    )

    track = (
        db.query(Track)
        .options(joinedload(Track.levels).joinedload(Level.labs))
        .filter(Track.slug == track_slug)
        .first()
    )
    if track is None:
        raise ValueError("track_not_found")
    level = next((row for row in track.levels if row.id == level_id), None)
    if level is None:
        raise ValueError("level_not_found")
    completions = get_user_completions(db, user.id)
    accessible = get_accessible_exclusive_lab_ids(db, user.id)
    visible_ids = _visible_lab_ids(track, user, accessible)
    visible_labs = [
        lab for lab in level.labs if lab.id in visible_ids
    ]
    certificate = build_level_certificate(
        db,
        user,
        track,
        level,
        visible_labs,
        completions,
        include_qr=False,
        include_achievements=False,
        base_url=issuer_url(db),
    )
    if certificate is None:
        raise ValueError("not_eligible")

    existing = (
        db.query(OpenBadgeCredential)
        .filter(
            OpenBadgeCredential.user_id == user.id,
            OpenBadgeCredential.certificate_id == certificate["certificate_id"],
        )
        .first()
    )
    if existing is not None:
        if include_name and not existing.recipient_name_opt_in:
            existing.recipient_name_opt_in = True
            db.commit()
        return existing

    verify_url = certificate.get("verify_url") or f"{issuer_url(db)}/verify/certificate/{certificate['certificate_id']}"
    row = OpenBadgeCredential(
        user_id=user.id,
        certificate_id=certificate["certificate_id"],
        track_slug=track.slug,
        level_id=level.id,
        subject_id=uuid.uuid4().hex,
        jti=uuid.uuid4().hex,
        achievement_name=f"{certificate['track_name']} — {certificate['level_name']}",
        achievement_description=certificate.get("level_description")
        or f"Level {certificate['level_number']} of {certificate['track_name']}",
        criteria_url=verify_url,
        evidence_url=verify_url,
        recipient_name_opt_in=bool(include_name),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def revoke_badge(
    db: Session, row: OpenBadgeCredential, actor: User, reason: str
) -> OpenBadgeCredential:
    row.revoked_at = datetime.now(timezone.utc)
    row.revoked_by_id = actor.id
    row.revocation_reason = reason.strip()[:500] or None
    db.commit()
    db.refresh(row)
    return row

