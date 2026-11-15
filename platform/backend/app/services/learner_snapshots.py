"""Immutable learner report snapshots.

A snapshot stores the rendered report payload and the factor weights that
produced it. Reports are re-rendered from the stored payload, so a later
formula or weight change cannot rewrite a report a learner already downloaded.

The payload is canonical JSON in a Text column, matching the existing
``lab_completions.competency_mapping`` convention. No new dependency and no
dialect-specific JSON type is needed.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import LearnerSnapshot, User

SCHEMA_VERSION = "2026.1"
KINDS = ("career_dossier", "portfolio")


def canonical_json(value: dict) -> str:
    """Stable JSON for hashing and storage."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


# Fields that change on every build but do not change what the report says.
# The content hash and deduplication ignore them so a repeated view of an
# unchanged report does not create a new row.
VOLATILE_KEYS = {
    "generated_at",
    "portfolio_id",
    "export_metadata",
    "snapshot",
    "verification",
}


def _stable_content(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if key not in VOLATILE_KEYS}


def content_hash(payload: dict) -> str:
    return hashlib.sha256(
        canonical_json(_stable_content(payload)).encode("utf-8")
    ).hexdigest()


def weights_for(kind: str, payload: dict) -> dict:
    """Collect the versions and factor weights that shaped the report."""
    if kind not in KINDS:
        raise ValueError(f"unknown snapshot kind: {kind}")
    dna = payload.get("cyber_dna") or {}
    growth = payload.get("growth_velocity") or {}
    momentum = payload.get("momentum") or {}
    atlas = payload.get("career_atlas") or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": kind,
        "formula_versions": {
            "skill_dna": dna.get("formula_version"),
            "growth_velocity": growth.get("version"),
            "momentum": momentum.get("version"),
            "career_atlas": atlas.get("version"),
        },
        "factor_weights": {
            "skill_dna": dna.get("factor_weights"),
            "growth_velocity": growth.get("factor_weights"),
            "momentum": momentum.get("factor_weights"),
        },
    }


def _formula_version(payload: dict) -> str | None:
    return (payload.get("cyber_dna") or {}).get("formula_version")


def record_snapshot(
    db: Session,
    user: User,
    kind: str,
    payload: dict,
) -> tuple[LearnerSnapshot, bool]:
    """Store a report payload, deduplicating identical reports.

    Returns ``(row, created)``. The unique key is the owner, kind, and payload
    hash, so repeated exports of an unchanged report do not create duplicates.
    """
    if kind not in KINDS:
        raise ValueError(f"unknown snapshot kind: {kind}")
    body = canonical_json(payload)
    digest = content_hash(payload)
    existing = (
        db.query(LearnerSnapshot)
        .filter(
            LearnerSnapshot.user_id == user.id,
            LearnerSnapshot.kind == kind,
            LearnerSnapshot.content_sha256 == digest,
        )
        .first()
    )
    if existing is not None:
        return existing, False

    row = LearnerSnapshot(
        user_id=user.id,
        kind=kind,
        schema_version=SCHEMA_VERSION,
        formula_version=_formula_version(payload),
        weights=canonical_json(weights_for(kind, payload)),
        payload=body,
        content_sha256=digest,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        # A concurrent export of the same report won the insert.
        db.rollback()
        existing = (
            db.query(LearnerSnapshot)
            .filter(
                LearnerSnapshot.user_id == user.id,
                LearnerSnapshot.kind == kind,
                LearnerSnapshot.content_sha256 == digest,
            )
            .first()
        )
        if existing is None:
            raise
        return existing, False
    db.refresh(row)
    return row, True


def list_snapshots(
    db: Session,
    user_id: int,
    kind: str | None = None,
    limit: int = 20,
) -> list[LearnerSnapshot]:
    query = db.query(LearnerSnapshot).filter(LearnerSnapshot.user_id == user_id)
    if kind:
        query = query.filter(LearnerSnapshot.kind == kind)
    return (
        query.order_by(LearnerSnapshot.created_at.desc(), LearnerSnapshot.id.desc())
        .limit(max(1, min(limit, 100)))
        .all()
    )


def get_snapshot(
    db: Session,
    user_id: int,
    snapshot_id: int,
) -> LearnerSnapshot | None:
    return (
        db.query(LearnerSnapshot)
        .filter(
            LearnerSnapshot.id == snapshot_id,
            LearnerSnapshot.user_id == user_id,
        )
        .first()
    )


def snapshot_meta(row: LearnerSnapshot, include_weights: bool = False) -> dict:
    created = row.created_at
    if isinstance(created, datetime) and created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    meta = {
        "snapshot_id": row.id,
        "kind": row.kind,
        "schema_version": row.schema_version,
        "formula_version": row.formula_version,
        "content_sha256": row.content_sha256,
        "created_at": created.isoformat() if isinstance(created, datetime) else created,
    }
    if include_weights:
        meta["weights"] = json.loads(row.weights)
    return meta


def snapshot_payload(row: LearnerSnapshot) -> dict:
    return json.loads(row.payload)
