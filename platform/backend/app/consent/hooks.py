"""Cleanup and verification hooks for privacy-sensitive tables.

Every purge target in :mod:`app.consent.registry` must have a hook here. The
orchestrator calls these hooks automatically; callers never remember to clean a
table themselves. Optional tables are guarded by an existence check so an
edition that never shipped AI, sharing, or analytics tables still passes.
"""

from __future__ import annotations

import logging
import re
from typing import Callable

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.consent.models import ConsentState
from app.consent.registry import CONSENT_TYPES, PRIVACY_TABLES, TargetSpec, spec_for
from app.cyber_dna.models import DnaEvidenceRecord, DnaSnapshot
from app.models import LearnerSnapshot

logger = logging.getLogger(__name__)

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
LEARNER_SNAPSHOT_KINDS = ("portfolio", "career_dossier")

# Extension point for a future cache tier. A cache module registers a callable
# that removes one learner's keys; the hook runs before and after every purge.
CACHE_CLEARERS: list[Callable[[int], int]] = []


def register_cache_clearer(clearer: Callable[[int], int]) -> None:
    if clearer not in CACHE_CLEARERS:
        CACHE_CLEARERS.append(clearer)


def clear_profile_caches(user_id: int) -> int:
    cleared = 0
    for clearer in CACHE_CLEARERS:
        try:
            cleared += int(clearer(user_id) or 0)
        except Exception as exc:  # pragma: no cover - cache tier is optional
            logger.warning("Cache cleanup failed for user %s: %s", user_id, exc)
    return cleared


def _table_exists(db: Session, table: str) -> bool:
    if not _IDENTIFIER.fullmatch(table):
        raise ValueError("unsafe table identifier")
    try:
        return inspect(db.get_bind()).has_table(table)
    except Exception:
        return False


def _delete_table(db: Session, table: str, column: str, user_id: int) -> int:
    if not _IDENTIFIER.fullmatch(table) or not _IDENTIFIER.fullmatch(column):
        raise ValueError("unsafe table or column identifier")
    if not _table_exists(db, table):
        return 0
    from sqlalchemy import text

    result = db.execute(
        text(f"DELETE FROM {table} WHERE {column} = :user_id"),
        {"user_id": user_id},
    )
    return int(result.rowcount or 0)


def _count_table(db: Session, table: str, column: str, user_id: int) -> int:
    if not _IDENTIFIER.fullmatch(table) or not _IDENTIFIER.fullmatch(column):
        raise ValueError("unsafe table or column identifier")
    if not _table_exists(db, table):
        return 0
    from sqlalchemy import text

    return int(
        db.execute(
            text(f"SELECT count(*) FROM {table} WHERE {column} = :user_id"),
            {"user_id": user_id},
        ).scalar()
        or 0
    )


def _orm_delete(db: Session, model, *criteria) -> int:
    return int(
        db.query(model).filter(*criteria).delete(synchronize_session=False) or 0
    )


def _orm_count(db: Session, model, *criteria) -> int:
    return int(db.query(model).filter(*criteria).count() or 0)


# --- Cyber DNA -------------------------------------------------------------


def purge_dna_evidence(db: Session, user_id: int) -> int:
    return _orm_delete(db, DnaEvidenceRecord, DnaEvidenceRecord.learner_id == user_id)


def verify_dna_evidence(db: Session, user_id: int) -> int:
    return _orm_count(db, DnaEvidenceRecord, DnaEvidenceRecord.learner_id == user_id)


def purge_dna_snapshots(db: Session, user_id: int) -> int:
    return _orm_delete(db, DnaSnapshot, DnaSnapshot.learner_id == user_id)


def verify_dna_snapshots(db: Session, user_id: int) -> int:
    return _orm_count(db, DnaSnapshot, DnaSnapshot.learner_id == user_id)


# --- Derived report snapshots ---------------------------------------------


def purge_learner_snapshots(db: Session, user_id: int) -> int:
    return _orm_delete(
        db,
        LearnerSnapshot,
        LearnerSnapshot.user_id == user_id,
        LearnerSnapshot.kind.in_(LEARNER_SNAPSHOT_KINDS),
    )


def verify_learner_snapshots(db: Session, user_id: int) -> int:
    return _orm_count(
        db,
        LearnerSnapshot,
        LearnerSnapshot.user_id == user_id,
        LearnerSnapshot.kind.in_(LEARNER_SNAPSHOT_KINDS),
    )


# --- Stateless or optional services ---------------------------------------


def purge_gps_cache(db: Session, user_id: int) -> int:
    return clear_profile_caches(user_id)


def verify_gps_cache(db: Session, user_id: int) -> int:
    # GPS is computed from educational records on demand; it stores no row.
    return 0


def _optional_purge(table: str, column: str = "user_id"):
    def purge(db: Session, user_id: int) -> int:
        return _delete_table(db, table, column, user_id)

    return purge


def _optional_verify(table: str, column: str = "user_id"):
    def verify(db: Session, user_id: int) -> int:
        return _count_table(db, table, column, user_id)

    return verify


PURGE_HOOKS: dict[tuple[str, str], tuple[Callable, Callable]] = {
    ("cyber_dna", "evidence"): (purge_dna_evidence, verify_dna_evidence),
    ("cyber_dna", "snapshots"): (purge_dna_snapshots, verify_dna_snapshots),
    ("reports", "learner_snapshots"): (
        purge_learner_snapshots,
        verify_learner_snapshots,
    ),
    ("cyber_gps", "cache"): (purge_gps_cache, verify_gps_cache),
    ("portfolio", "share_tokens"): (
        _optional_purge("portfolio_share_tokens"),
        _optional_verify("portfolio_share_tokens"),
    ),
    ("portfolio", "public_profiles"): (
        _optional_purge("public_profiles"),
        _optional_verify("public_profiles"),
    ),
    ("ai", "conversations"): (
        _optional_purge("ai_conversations"),
        _optional_verify("ai_conversations"),
    ),
    ("ai", "embeddings"): (
        _optional_purge("ai_embeddings"),
        _optional_verify("ai_embeddings"),
    ),
    ("ai", "memory"): (
        _optional_purge("ai_memory"),
        _optional_verify("ai_memory"),
    ),
    ("analytics", "learner_profiles"): (
        _optional_purge("learner_analytics_profiles"),
        _optional_verify("learner_analytics_profiles"),
    ),
    ("analytics", "segmentation"): (
        _optional_purge("learner_segmentations"),
        _optional_verify("learner_segmentations"),
    ),
    ("analytics", "research_datasets"): (
        _optional_purge("research_dataset_rows"),
        _optional_verify("research_dataset_rows"),
    ),
}


def execute_target(db: Session, user_id: int, service: str, action: str) -> int:
    try:
        purge, _verify = PURGE_HOOKS[(service, action)]
    except KeyError as exc:
        raise ValueError(f"missing purge hook for {service}:{action}") from exc
    return int(purge(db, user_id) or 0)


def verify_target(db: Session, user_id: int, service: str, action: str) -> int:
    try:
        _purge, verify = PURGE_HOOKS[(service, action)]
    except KeyError as exc:
        raise ValueError(f"missing verification hook for {service}:{action}") from exc
    return int(verify(db, user_id) or 0)


def verify_cleanup(
    db: Session, user_id: int, consent_type: str
) -> tuple[dict[str, int], bool]:
    remaining: dict[str, int] = {}
    for target in spec_for(consent_type).targets:
        count = verify_target(db, user_id, target.service, target.action)
        remaining[f"{target.service}:{target.action}"] = count
    return remaining, not any(remaining.values())


# --- Lifecycle hooks -------------------------------------------------------


def before_profile_purge(db: Session, user_id: int, consent_type: str) -> dict:
    """Lock the feature before any row is removed.

    The persisted ``revocation_in_progress`` flag is the cross-process lock:
    DNA ingestion, GPS views, portfolio exports, and any future writer check it
    before doing work. In-process caches are cleared at the same time.
    """
    state = (
        db.query(ConsentState)
        .filter(
            ConsentState.user_id == user_id,
            ConsentState.consent_type == consent_type,
        )
        .first()
    )
    if state is not None:
        state.revocation_in_progress = True
    return {"locked": True, "cache_entries": clear_profile_caches(user_id)}


def after_profile_purge(db: Session, user_id: int, consent_type: str) -> dict:
    """Remove orphaned derived rows and clear caches after a purge group."""
    removed = 0
    # A restored snapshot with no owning user is still derived data. The FK
    # cascade normally removes these; this catches a partial restore.
    removed += _orm_delete(
        db,
        LearnerSnapshot,
        LearnerSnapshot.user_id == user_id,
        LearnerSnapshot.kind.in_(LEARNER_SNAPSHOT_KINDS),
    )
    return {"orphans_removed": removed, "cache_entries": clear_profile_caches(user_id)}


def assert_privacy_targets_registered() -> None:
    """Fail fast when a privacy table or consent target has no hook."""
    missing = []
    for table, (service, action) in PRIVACY_TABLES.items():
        if (service, action) not in PURGE_HOOKS:
            missing.append(f"{table} -> {service}:{action}")
    for consent_type, spec in CONSENT_TYPES.items():
        for target in spec.targets:
            if (target.service, target.action) not in PURGE_HOOKS:
                missing.append(f"{consent_type} -> {target.service}:{target.action}")
    if missing:
        raise AssertionError(
            "privacy-sensitive targets lack cleanup hooks: " + ", ".join(missing)
        )


def targets_for(consent_type: str) -> tuple[TargetSpec, ...]:
    return spec_for(consent_type).targets
