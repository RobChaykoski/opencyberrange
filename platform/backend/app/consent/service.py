"""Consent revocation orchestrator.

The orchestrator never deletes data inline in the HTTP request. A revoke
transaction writes the suppression proof, locks the feature, records the
immutable event, and enqueues one purge job per registered target. A worker
then executes all targets for a revocation in a single database transaction so
a mid-purge failure leaves every table untouched. Verification runs
immediately and again at 24 hours and 7 days.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.consent import hooks, suppression
from app.consent.models import (
    ConsentAudit,
    ConsentEvent,
    ConsentJob,
    ConsentRevocation,
    ConsentState,
    ConsentSuppression,
)
from app.consent.registry import (
    CONSENT_TYPES,
    MAX_JOB_ATTEMPTS,
    REVOCATION_SLA_SECONDS,
    VERIFY_SLOTS,
    spec_for,
)
from app.cyber_dna.models import DnaEvidenceRecord, DnaSnapshot
from app.models import Achievement, CourseEnrollment, LabCompletion, LearnerSnapshot

logger = logging.getLogger(__name__)

REVOCATION_STATUSES = ("pending", "running", "verifying", "complete", "failed", "cancelled")


class ConsentError(Exception):
    """Base class for consent workflow errors."""


class ConsentBlocked(ConsentError):
    def __init__(self, consent_type: str, status: str):
        self.consent_type = consent_type
        self.status = status
        super().__init__(f"{consent_type} is {status}")


class ConsentConflict(ConsentError):
    def __init__(self, expected: int, actual: int):
        self.expected = expected
        self.actual = actual
        super().__init__(f"consent version changed (expected {expected}, now {actual})")


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() + "Z" if value else None


def _subject_hash(user_id: int) -> str:
    return suppression.subject_hash(user_id)


def _state_row(db: Session, user_id: int, consent_type: str) -> ConsentState | None:
    return (
        db.query(ConsentState)
        .filter(
            ConsentState.user_id == user_id,
            ConsentState.consent_type == consent_type,
        )
        .first()
    )


def _latest_revocation(
    db: Session, user_id: int, consent_type: str
) -> ConsentRevocation | None:
    return (
        db.query(ConsentRevocation)
        .filter(
            ConsentRevocation.user_id == user_id,
            ConsentRevocation.consent_type == consent_type,
        )
        .order_by(ConsentRevocation.consent_version.desc())
        .first()
    )


def _state_payload(
    consent_type: str, row: ConsentState | None
) -> dict:
    spec = spec_for(consent_type)
    granted = row.granted if row is not None else spec.default_granted
    version = row.version if row is not None else 0
    in_progress = bool(row.revocation_in_progress) if row is not None else False
    return {
        "consent_type": consent_type,
        "label": spec.label,
        "description": spec.description,
        "granted": bool(granted),
        "default_granted": spec.default_granted,
        "version": version,
        "revocation_in_progress": in_progress,
        "revoked_at": _iso(row.revoked_at) if row is not None else None,
        "blocked": (not granted) or in_progress,
        "removed": list(spec.removed),
        "kept": list(spec.kept),
        "targets": [
            {"service": target.service, "action": target.action}
            for target in spec.targets
        ],
    }


def state_for(db: Session, user_id: int, consent_type: str) -> dict:
    return _state_payload(consent_type, _state_row(db, user_id, consent_type))


def all_states(db: Session, user_id: int) -> dict[str, dict]:
    rows = {
        row.consent_type: row
        for row in db.query(ConsentState)
        .filter(ConsentState.user_id == user_id)
        .all()
    }
    return {
        consent_type: _state_payload(consent_type, rows.get(consent_type))
        for consent_type in CONSENT_TYPES
    }


def is_granted(db: Session, user_id: int, consent_type: str) -> bool:
    spec = spec_for(consent_type)
    row = _state_row(db, user_id, consent_type)
    return bool(row.granted) if row is not None else spec.default_granted


def blocked_status(db: Session, user_id: int, consent_type: str) -> str | None:
    row = _state_row(db, user_id, consent_type)
    if row is None:
        return None if spec_for(consent_type).default_granted else "revoked"
    if row.revocation_in_progress:
        return "revocation_in_progress"
    if not row.granted:
        return "revoked"
    return None


def ensure_allowed(db: Session, user_id: int, consent_type: str) -> None:
    status = blocked_status(db, user_id, consent_type)
    if status:
        raise ConsentBlocked(consent_type, status)


def _event(
    db: Session,
    user_id: int,
    consent_type: str,
    action: str,
    version: int,
    actor: str,
    reason: str | None,
) -> None:
    db.add(
        ConsentEvent(
            user_id=user_id,
            consent_type=consent_type,
            action=action,
            consent_version=version,
            actor=actor,
            reason=(reason or "")[:500] or None,
        )
    )


def _purge_jobs(
    db: Session, revocation: ConsentRevocation, now: datetime
) -> list[ConsentJob]:
    jobs = []
    for target in spec_for(revocation.consent_type).targets:
        job = ConsentJob(
            revocation_id=revocation.id,
            user_id=revocation.user_id,
            consent_type=revocation.consent_type,
            kind="purge",
            service=target.service,
            action=target.action,
            slot="",
            status="queued",
            available_at=now,
        )
        db.add(job)
        jobs.append(job)
    return jobs


def revoke(
    db: Session,
    user_id: int,
    consent_type: str,
    *,
    actor: str = "self",
    reason: str | None = None,
    expected_version: int | None = None,
) -> ConsentRevocation:
    """Start a revocation. The feature is blocked before this returns."""
    spec_for(consent_type)
    now = _now()
    row = _state_row(db, user_id, consent_type)
    latest = _latest_revocation(db, user_id, consent_type)

    if row is not None and not row.granted:
        if latest is not None and latest.status == "failed":
            _requeue_purge_jobs(db, latest, now)
            db.commit()
            return latest
        if latest is not None and latest.status != "cancelled":
            return latest

    current_version = row.version if row is not None else 0
    new_version = current_version + 1
    if expected_version is not None and expected_version != new_version:
        raise ConsentConflict(expected_version, new_version)

    # Fail closed: the suppression proof is durable on disk before any database
    # row changes. A restore that predates this revocation must see it.
    ledger_path = suppression.append_suppression(
        user_id,
        consent_type,
        new_version,
        reason=reason or "consent_revoked",
    )

    audit_id = str(uuid.uuid4())
    try:
        if row is None:
            row = ConsentState(
                user_id=user_id,
                consent_type=consent_type,
                granted=False,
                version=new_version,
                revocation_in_progress=True,
                revoked_at=now,
            )
            db.add(row)
        else:
            row.granted = False
            row.version = new_version
            row.revoked_at = now
            row.revocation_in_progress = True

        revocation = ConsentRevocation(
            user_id=user_id,
            consent_type=consent_type,
            consent_version=new_version,
            audit_id=audit_id,
            status="pending",
            requested_at=now,
            suppression_recorded=True,
        )
        db.add(revocation)
        db.flush()

        _purge_jobs(db, revocation, now)
        _event(db, user_id, consent_type, "revoke", new_version, actor, reason)
        db.add(
            ConsentSuppression(
                subject_hash=_subject_hash(user_id),
                user_id=user_id,
                consent_type=consent_type,
                consent_version=new_version,
                reason=(reason or "consent_revoked")[:64],
                ledger_path=ledger_path[:255],
            )
        )
        db.add(
            ConsentAudit(
                audit_id=audit_id,
                user_id=user_id,
                subject_hash=_subject_hash(user_id),
                consent_type=consent_type,
                consent_version=new_version,
                revoked_at=now,
                jobs_completed="[]",
                verified=False,
                verification_slots="[]",
                suppression_recorded=True,
            )
        )
        hooks.before_profile_purge(db, user_id, consent_type)
        db.commit()
    except IntegrityError:
        db.rollback()
        suppression.append_suppression(
            user_id,
            consent_type,
            new_version,
            status="cancelled",
            reason="concurrent_revoke",
        )
        existing = _latest_revocation(db, user_id, consent_type)
        if existing is not None:
            return existing
        raise
    except Exception:
        db.rollback()
        try:
            suppression.append_suppression(
                user_id,
                consent_type,
                new_version,
                status="cancelled",
                reason="revoke_rolled_back",
            )
        except Exception:  # pragma: no cover - cancellation is best effort
            logger.exception("Could not cancel consent suppression after rollback")
        raise

    db.refresh(revocation)
    logger.info(
        "Consent revoked: user_id=%s type=%s version=%s audit=%s",
        user_id,
        consent_type,
        new_version,
        audit_id,
    )
    return revocation


def grant(
    db: Session,
    user_id: int,
    consent_type: str,
    *,
    actor: str = "self",
    reason: str | None = None,
) -> dict:
    """Re-enable a feature. Deleted data is never restored."""
    spec = spec_for(consent_type)
    row = _state_row(db, user_id, consent_type)
    if row is None and spec.default_granted:
        return _state_payload(consent_type, None)

    now = _now()
    if row is None:
        row = ConsentState(
            user_id=user_id,
            consent_type=consent_type,
            granted=True,
            version=1,
            revocation_in_progress=False,
        )
        db.add(row)
        version = 1
    else:
        if row.granted and not row.revocation_in_progress:
            return _state_payload(consent_type, row)
        version = row.version + 1
        row.granted = True
        row.version = version
        row.revoked_at = None
        row.revocation_in_progress = False

    # Cancel queued work for a revocation the learner reversed before it ran.
    for active in (
        db.query(ConsentRevocation)
        .filter(
            ConsentRevocation.user_id == user_id,
            ConsentRevocation.consent_type == consent_type,
            ConsentRevocation.status.in_(("pending", "running")),
        )
        .all()
    ):
        active.status = "cancelled"
        db.query(ConsentJob).filter(
            ConsentJob.revocation_id == active.id,
            ConsentJob.status == "queued",
        ).update(
            {ConsentJob.status: "cancelled", ConsentJob.completed_at: now},
            synchronize_session=False,
        )

    # A later cancellation entry wins over the earlier suppression. New activity
    # may be recorded again, but anything already deleted stays deleted.
    suppression.append_suppression(
        user_id,
        consent_type,
        version,
        status="cancelled",
        reason="consent_regranted",
    )
    db.query(ConsentSuppression).filter(
        ConsentSuppression.user_id == user_id,
        ConsentSuppression.consent_type == consent_type,
        ConsentSuppression.cancelled_at.is_(None),
    ).update(
        {ConsentSuppression.cancelled_at: now},
        synchronize_session=False,
    )
    _event(db, user_id, consent_type, "grant", version, actor, reason)
    db.commit()
    db.refresh(row)
    return _state_payload(consent_type, row)


def _requeue_purge_jobs(
    db: Session, revocation: ConsentRevocation, now: datetime
) -> None:
    for job in revocation_jobs(db, revocation.id, kind="purge"):
        if job.status != "complete":
            job.status = "queued"
            job.available_at = now
            job.lease_until = None
            job.last_error = None
    revocation.status = "pending"
    revocation.last_error = None


def revocation_jobs(
    db: Session, revocation_id: int, kind: str | None = None
) -> list[ConsentJob]:
    query = db.query(ConsentJob).filter(ConsentJob.revocation_id == revocation_id)
    if kind:
        query = query.filter(ConsentJob.kind == kind)
    return query.order_by(ConsentJob.id).all()


def _enqueue_verification_jobs(
    db: Session, revocation: ConsentRevocation, now: datetime
) -> None:
    for slot, offset in VERIFY_SLOTS:
        exists = (
            db.query(ConsentJob.id)
            .filter(
                ConsentJob.revocation_id == revocation.id,
                ConsentJob.kind == "verify",
                ConsentJob.service == "orchestrator",
                ConsentJob.action == "verify",
                ConsentJob.slot == slot,
            )
            .first()
        )
        if exists:
            continue
        db.add(
            ConsentJob(
                revocation_id=revocation.id,
                user_id=revocation.user_id,
                consent_type=revocation.consent_type,
                kind="verify",
                service="orchestrator",
                action="verify",
                slot=slot,
                status="queued",
                available_at=now + timedelta(seconds=offset),
            )
        )


def _audit_for(db: Session, revocation: ConsentRevocation) -> ConsentAudit | None:
    return (
        db.query(ConsentAudit)
        .filter(ConsentAudit.audit_id == revocation.audit_id)
        .first()
    )


def _jobs_completed(db: Session, revocation: ConsentRevocation) -> str:
    rows = [
        f"{job.service}:{job.action}"
        for job in revocation_jobs(db, revocation.id, kind="purge")
        if job.status == "complete"
    ]
    return json.dumps(sorted(rows))


def _record_verification(
    db: Session,
    revocation: ConsentRevocation,
    slot: str,
    now: datetime,
    remaining: dict[str, int],
) -> None:
    audit = _audit_for(db, revocation)
    if audit is not None:
        slots = set(json.loads(audit.verification_slots or "[]"))
        slots.add(slot)
        audit.verification_slots = json.dumps(sorted(slots))
        audit.jobs_completed = _jobs_completed(db, revocation)
        audit.verified = True
        audit.verified_at = now
    revocation.verified_at = now
    revocation.verification_attempts = int(revocation.verification_attempts or 0) + 1
    revocation.last_error = None
    if slot == "immediate":
        revocation.status = "complete"
        state = _state_row(db, revocation.user_id, revocation.consent_type)
        if state is not None:
            state.revocation_in_progress = False
    logger.info(
        "Consent verification passed: user_id=%s type=%s slot=%s remaining=%s",
        revocation.user_id,
        revocation.consent_type,
        slot,
        remaining,
    )


def _fail_verification(
    db: Session,
    revocation: ConsentRevocation,
    slot: str,
    now: datetime,
    remaining: dict[str, int],
) -> None:
    revocation.status = "failed"
    revocation.last_error = f"verification {slot} found remaining rows: {remaining}"[:500]
    revocation.verification_attempts = int(revocation.verification_attempts or 0) + 1
    for job in revocation_jobs(db, revocation.id, kind="purge"):
        if job.status == "complete":
            job.status = "queued"
            job.attempts = 0
            job.available_at = now
            job.lease_until = None
    state = _state_row(db, revocation.user_id, revocation.consent_type)
    if state is not None:
        state.revocation_in_progress = True


def _claim_due_revocation_ids(db: Session, now: datetime, limit: int) -> list[int]:
    rows = (
        db.query(ConsentJob.revocation_id)
        .filter(
            ConsentJob.kind == "purge",
            ConsentJob.status == "queued",
            ConsentJob.available_at <= now,
        )
        .distinct()
        .order_by(ConsentJob.revocation_id)
        .limit(limit)
        .all()
    )
    return [row[0] for row in rows]


def _run_purge_group(db: Session, revocation_id: int, now: datetime) -> bool:
    revocation = (
        db.query(ConsentRevocation)
        .filter(ConsentRevocation.id == revocation_id)
        .with_for_update(skip_locked=True)
        .first()
    )
    if revocation is None:
        return False
    if revocation.status in {"cancelled", "complete"}:
        db.query(ConsentJob).filter(
            ConsentJob.revocation_id == revocation_id,
            ConsentJob.status == "queued",
        ).update(
            {ConsentJob.status: "cancelled", ConsentJob.completed_at: now},
            synchronize_session=False,
        )
        db.commit()
        return False

    try:
        revocation.status = "running"
        revocation.started_at = revocation.started_at or now
        jobs = revocation_jobs(db, revocation_id, kind="purge")
        for job in jobs:
            job.status = "running"
            job.attempts = int(job.attempts or 0) + 1
            job.lease_until = now + timedelta(minutes=5)
        db.flush()

        hooks.before_profile_purge(db, revocation.user_id, revocation.consent_type)
        for target in spec_for(revocation.consent_type).targets:
            hooks.execute_target(
                db, revocation.user_id, target.service, target.action
            )

        remaining, ok = hooks.verify_cleanup(
            db, revocation.user_id, revocation.consent_type
        )
        if not ok:
            raise RuntimeError(f"purge verification failed: {remaining}")

        for job in jobs:
            job.status = "complete"
            job.completed_at = now
            job.lease_until = None
            job.last_error = None
        revocation.status = "verifying"
        revocation.purge_completed_at = now
        revocation.last_error = None
        hooks.after_profile_purge(db, revocation.user_id, revocation.consent_type)
        _enqueue_verification_jobs(db, revocation, now)
        db.commit()
        return True
    except Exception as exc:
        db.rollback()
        failed = db.query(ConsentRevocation).filter(ConsentRevocation.id == revocation_id).first()
        if failed is None:
            return False
        for job in revocation_jobs(db, revocation_id, kind="purge"):
            job.attempts = int(job.attempts or 0) + 1
            job.last_error = str(exc)[:500]
            job.lease_until = None
            if job.attempts >= MAX_JOB_ATTEMPTS:
                job.status = "failed"
                job.completed_at = now
            else:
                job.status = "queued"
                job.available_at = now + timedelta(seconds=job.attempts)
        failed.status = "failed"
        failed.last_error = str(exc)[:500]
        db.commit()
        logger.error(
            "Consent purge rolled back: user_id=%s type=%s error=%s",
            failed.user_id,
            failed.consent_type,
            exc,
        )
        return False


def _claim_verify_jobs(db: Session, now: datetime, limit: int) -> list[ConsentJob]:
    return (
        db.query(ConsentJob)
        .filter(
            ConsentJob.kind == "verify",
            ConsentJob.status == "queued",
            ConsentJob.available_at <= now,
        )
        .order_by(ConsentJob.available_at, ConsentJob.id)
        .limit(limit)
        .with_for_update(skip_locked=True)
        .all()
    )


def _run_verify_job(db: Session, job: ConsentJob, now: datetime) -> bool:
    revocation = (
        db.query(ConsentRevocation)
        .filter(ConsentRevocation.id == job.revocation_id)
        .first()
    )
    if revocation is None:
        job.status = "cancelled"
        job.completed_at = now
        db.commit()
        return False
    if revocation.status == "cancelled":
        job.status = "cancelled"
        job.completed_at = now
        db.commit()
        return False

    job.status = "running"
    job.attempts = int(job.attempts or 0) + 1
    job.lease_until = now + timedelta(minutes=5)
    db.flush()
    remaining, ok = hooks.verify_cleanup(
        db, revocation.user_id, revocation.consent_type
    )
    if ok:
        job.status = "complete"
        job.completed_at = now
        job.lease_until = None
        job.last_error = None
        _record_verification(db, revocation, job.slot, now, remaining)
        db.commit()
        return True

    job.status = "failed"
    job.completed_at = now
    job.last_error = f"remaining rows: {remaining}"[:500]
    _fail_verification(db, revocation, job.slot, now, remaining)
    db.commit()
    logger.error(
        "Consent verification failed: user_id=%s type=%s remaining=%s",
        revocation.user_id,
        revocation.consent_type,
        remaining,
    )
    return False


def _reclaim_expired(db: Session, now: datetime) -> int:
    return (
        db.query(ConsentJob)
        .filter(
            ConsentJob.status == "running",
            ConsentJob.lease_until.isnot(None),
            ConsentJob.lease_until < now,
        )
        .update(
            {
                ConsentJob.status: "queued",
                ConsentJob.lease_until: None,
                ConsentJob.available_at: now,
            },
            synchronize_session=False,
        )
    )


def run_due_jobs(
    db: Session, *, now: datetime | None = None, limit: int = 20
) -> dict:
    """Process due purges and verifications. Safe to call repeatedly."""
    now = now or _now()
    reclaimed = _reclaim_expired(db, now)
    db.commit()

    purged = 0
    for revocation_id in _claim_due_revocation_ids(db, now, limit):
        if _run_purge_group(db, revocation_id, now):
            purged += 1

    verified = 0
    for job in _claim_verify_jobs(db, now, max(1, limit - purged)):
        if _run_verify_job(db, job, now):
            verified += 1

    return {
        "reclaimed": int(reclaimed or 0),
        "purges": purged,
        "verifications": verified,
        "now": _iso(now),
    }


def enforce_suppressions(db: Session, *, now: datetime | None = None) -> dict:
    """Apply the suppression ledger to restored or replayed learner rows.

    The ledger is the source of truth. A restored consent row that says
    ``granted`` is flipped back to revoked, and every registered target is
    purged and verified. This is the backup-restore control.
    """
    now = now or _now()
    entries = suppression.load_suppressions()
    if not entries:
        return {"profiles": 0, "purged": 0, "failed": 0, "targets": []}

    candidates: set[int] = set()
    for query in (
        db.query(DnaEvidenceRecord.learner_id).distinct(),
        db.query(DnaSnapshot.learner_id).distinct(),
        db.query(LearnerSnapshot.user_id).distinct(),
        db.query(ConsentState.user_id).distinct(),
        db.query(ConsentSuppression.user_id).filter(
            ConsentSuppression.user_id.isnot(None)
        ).distinct(),
    ):
        candidates.update(row[0] for row in query.all() if row[0] is not None)

    purged = 0
    failed = 0
    touched_targets: list[str] = []
    for user_id in sorted(candidates):
        # Every consent type the learner may have revoked.
        for consent_type in CONSENT_TYPES:
            entry = entries.get((_subject_hash(user_id), consent_type))
            if not entry or (entry.get("status") or "committed") != "committed":
                continue
            version = int(entry.get("consent_version") or 0)
            state = _state_row(db, user_id, consent_type)
            if state is None:
                state = ConsentState(
                    user_id=user_id,
                    consent_type=consent_type,
                    granted=False,
                    version=max(1, version),
                    revocation_in_progress=False,
                    revoked_at=now,
                )
                db.add(state)
            else:
                state.granted = False
                state.version = max(int(state.version or 0), version)
                state.revoked_at = state.revoked_at or now
                state.revocation_in_progress = False
            db.flush()

            try:
                for target in spec_for(consent_type).targets:
                    hooks.execute_target(db, user_id, target.service, target.action)
                    touched_targets.append(f"{consent_type}:{target.service}:{target.action}")
                remaining, ok = hooks.verify_cleanup(db, user_id, consent_type)
                if not ok:
                    raise RuntimeError(f"remaining rows after sweep: {remaining}")
                audit = (
                    db.query(ConsentAudit)
                    .filter(
                        ConsentAudit.subject_hash == _subject_hash(user_id),
                        ConsentAudit.consent_type == consent_type,
                    )
                    .order_by(ConsentAudit.id.desc())
                    .first()
                )
                if audit is None:
                    audit = ConsentAudit(
                        audit_id=str(uuid.uuid4()),
                        user_id=user_id,
                        subject_hash=_subject_hash(user_id),
                        consent_type=consent_type,
                        consent_version=version,
                        revoked_at=now,
                        jobs_completed=json.dumps(
                            [
                                f"{target.service}:{target.action}"
                                for target in spec_for(consent_type).targets
                            ]
                        ),
                        verified=True,
                        verified_at=now,
                        verification_slots=json.dumps(["suppression_sweep"]),
                        suppression_recorded=True,
                    )
                    db.add(audit)
                else:
                    audit.verified = True
                    audit.verified_at = now
                    slots = set(json.loads(audit.verification_slots or "[]"))
                    slots.add("suppression_sweep")
                    audit.verification_slots = json.dumps(sorted(slots))
                purged += 1
            except Exception as exc:
                failed += 1
                logger.error(
                    "Suppression sweep failed for user %s type %s: %s",
                    user_id,
                    consent_type,
                    exc,
                )
                db.rollback()
                return {
                    "profiles": len(candidates),
                    "purged": purged,
                    "failed": failed,
                    "targets": sorted(set(touched_targets)),
                    "error": str(exc)[:500],
                }
    db.commit()
    return {
        "profiles": len(candidates),
        "purged": purged,
        "failed": failed,
        "targets": sorted(set(touched_targets)),
    }


def list_revocations(
    db: Session,
    *,
    user_id: int | None = None,
    status: str | None = None,
    consent_type: str | None = None,
    limit: int = 100,
) -> list[dict]:
    query = db.query(ConsentRevocation)
    if user_id is not None:
        query = query.filter(ConsentRevocation.user_id == user_id)
    if status:
        query = query.filter(ConsentRevocation.status == status)
    if consent_type:
        query = query.filter(ConsentRevocation.consent_type == consent_type)
    rows = query.order_by(ConsentRevocation.id.desc()).limit(max(1, min(limit, 500))).all()
    return [revocation_payload(db, row) for row in rows]


def revocation_payload(db: Session, row: ConsentRevocation) -> dict:
    audit = _audit_for(db, row)
    return {
        "id": row.id,
        "audit_id": row.audit_id,
        "user_id": row.user_id,
        "consent_type": row.consent_type,
        "version": row.consent_version,
        "status": row.status,
        "requested_at": _iso(row.requested_at),
        "started_at": _iso(row.started_at),
        "purge_completed_at": _iso(row.purge_completed_at),
        "verified_at": _iso(row.verified_at),
        "verification_attempts": int(row.verification_attempts or 0),
        "suppression_recorded": bool(row.suppression_recorded),
        "last_error": row.last_error,
        "jobs": [
            {
                "kind": job.kind,
                "service": job.service,
                "action": job.action,
                "slot": job.slot,
                "status": job.status,
                "attempts": int(job.attempts or 0),
                "available_at": _iso(job.available_at),
                "completed_at": _iso(job.completed_at),
                "last_error": job.last_error,
            }
            for job in revocation_jobs(db, row.id)
        ],
        "audit": (
            {
                "audit_id": audit.audit_id,
                "verified": bool(audit.verified),
                "verified_at": _iso(audit.verified_at),
                "jobs_completed": json.loads(audit.jobs_completed or "[]"),
                "verification_slots": json.loads(audit.verification_slots or "[]"),
                "suppression_recorded": bool(audit.suppression_recorded),
            }
            if audit is not None
            else None
        ),
    }


def history(db: Session, user_id: int, limit: int = 50) -> list[dict]:
    rows = (
        db.query(ConsentEvent)
        .filter(ConsentEvent.user_id == user_id)
        .order_by(ConsentEvent.id.desc())
        .limit(max(1, min(limit, 200)))
        .all()
    )
    return [
        {
            "consent_type": row.consent_type,
            "action": row.action,
            "version": row.consent_version,
            "actor": row.actor,
            "reason": row.reason,
            "occurred_at": _iso(row.occurred_at),
        }
        for row in rows
    ]


def export_state(db: Session, user_id: int) -> dict:
    """Consent section for the account data export. No derived payloads."""
    return {
        "consents": all_states(db, user_id),
        "history": history(db, user_id),
        "revocations": list_revocations(db, user_id=user_id, limit=100),
        "note": (
            "Revoking a consent removes derived intelligence. Educational "
            "records such as completions, attempts, certificates, and "
            "achievements are retained."
        ),
    }


def dashboard(db: Session, user_id: int) -> dict:
    """Learner-facing revocation status and what remains."""
    return {
        "consents": all_states(db, user_id),
        "history": history(db, user_id, limit=20),
        "revocations": list_revocations(db, user_id=user_id, limit=20),
        "remaining_records": {
            "completed_exercises": db.query(LabCompletion)
            .filter(LabCompletion.user_id == user_id)
            .count(),
            "achievements": db.query(Achievement)
            .filter(Achievement.user_id == user_id)
            .count(),
            "course_enrollments": db.query(CourseEnrollment)
            .filter(CourseEnrollment.user_id == user_id)
            .count(),
        },
        "retention_note": (
            "Revocation destroys derived intelligence. Transcript, "
            "certificates, completions, and assessment results remain part of "
            "the educational record."
        ),
    }


def metrics(db: Session) -> dict:
    revocations = db.query(ConsentRevocation).all()
    total = len(revocations)
    complete = sum(1 for row in revocations if row.status == "complete")
    failed = sum(1 for row in revocations if row.status == "failed")
    pending = sum(
        1 for row in revocations if row.status in ("pending", "running", "verifying")
    )
    verified_audits = (
        db.query(ConsentAudit).filter(ConsentAudit.verified.is_(True)).count()
    )
    durations = [
        (row.verified_at - row.requested_at).total_seconds()
        for row in revocations
        if row.verified_at is not None and row.requested_at is not None
    ]
    active_suppressions = suppression.load_suppressions()
    try:
        hooks.assert_privacy_targets_registered()
        registry_ok = True
    except AssertionError:
        registry_ok = False
    return {
        "revocations": {
            "total": total,
            "complete": complete,
            "pending": pending,
            "failed": failed,
        },
        "purge_verification_rate": (
            round(verified_audits / total * 100, 1) if total else 100.0
        ),
        "revocation_sla": {
            "target_seconds": REVOCATION_SLA_SECONDS,
            "average_seconds": round(sum(durations) / len(durations), 2)
            if durations
            else None,
            "within_target": (
                sum(1 for value in durations if value <= REVOCATION_SLA_SECONDS)
                if durations
                else 0
            ),
            "measured": len(durations),
        },
        "suppression_entries": len(active_suppressions),
        "privacy_registry_complete": registry_ok,
        "derived_rows": {
            "dna_evidence": db.query(DnaEvidenceRecord).count(),
            "dna_snapshots": db.query(DnaSnapshot).count(),
            "learner_snapshots": db.query(LearnerSnapshot)
            .filter(LearnerSnapshot.kind.in_(("portfolio", "career_dossier")))
            .count(),
        },
    }
