"""Production change control: ticket-gated settings, revert, and cutover.

Security properties:
* ticket numbers, reasons, and notes are Fernet-encrypted in PostgreSQL;
* secret setting values are never written to change-set snapshots;
* every apply, revert, and cutover is written to the append-only security
  event store and the audit log;
* production cutover is one-way from the application and requires a ticket,
  the current password, and explicit data-loss/one-way acknowledgements;
* sample/test accounts are erased through the existing privacy erasure path,
  so audit evidence is anonymised rather than silently destroyed.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import verify_password
from app.crypto import decrypt_secret, encrypt_secret, is_encrypted
from app.models import (
    Achievement,
    AuthSession,
    Course,
    CourseEnrollment,
    FlagAttempt,
    LabCompletion,
    LabSession,
    LearnerSnapshot,
    PlatformSetting,
    ProductionCutover,
    QuizAttempt,
    RefreshToken,
    SettingsChangeRequest,
    User,
)
from app.services import audit, security_events, settings_service
from app.services.erasure import ErasureBlocked, erase_user

TICKET_MODES = {"off", "optional", "required"}
PROTECTED_PHASE_KEYS = {"deployment_mode", "data_collection_mode"}
TICKET_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/#-]{1,79}$")
CONFIRMATION_PHRASE = "GO PRODUCTION"
SAMPLE_USER_RE = re.compile(
    r"^(pytest_|test_|demo_|qa_|seed_|sample_)"
    r"|@(example\.(org|com)|test\.local|pytest\.local)$",
    re.IGNORECASE,
)


class ProductionControlError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        details: dict | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _decrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    if is_encrypted(value):
        try:
            return decrypt_secret(value)
        except ValueError:
            return "[unreadable]"
    return value


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def deployment_mode(db: Session) -> str:
    return (
        settings_service.get_setting_fresh(db, "deployment_mode", "development")
        or "development"
    ).strip().lower()


def data_collection_mode(db: Session) -> str:
    return (
        settings_service.get_setting_fresh(db, "data_collection_mode", "sample")
        or "sample"
    ).strip().lower()


def ticket_mode(db: Session) -> str:
    value = (
        settings_service.get_setting_fresh(
            db, "settings_change_ticket_mode", "optional"
        )
        or "optional"
    ).strip().lower()
    return value if value in TICKET_MODES else "optional"


def require_ticket(db: Session, ticket_number: str | None, *, force: bool = False) -> str | None:
    mode = ticket_mode(db)
    value = (ticket_number or "").strip()
    if force or mode == "required":
        if not value:
            raise ProductionControlError(
                "ticket_required",
                "A change ticket number is required before this action can be applied.",
                status_code=422,
            )
    if value and not TICKET_RE.match(value):
        raise ProductionControlError(
            "ticket_invalid",
            "Ticket numbers must be 2-80 characters using letters, numbers, '.', '_', '/', '#', or '-'.",
            status_code=422,
        )
    return value or None


def _setting_rows(db: Session, keys: list[str]) -> dict[str, PlatformSetting]:
    return {
        row.key: row
        for row in db.query(PlatformSetting).filter(PlatformSetting.key.in_(keys)).all()
    }


def _snapshot(db: Session, keys: list[str]) -> tuple[dict[str, str], list[str]]:
    rows = _setting_rows(db, keys)
    values: dict[str, str] = {}
    secrets: list[str] = []
    for key in keys:
        row = rows.get(key)
        if row is not None and row.is_secret:
            values[key] = "[secret]"
            secrets.append(key)
        elif row is not None:
            values[key] = row.value or ""
        else:
            values[key] = ""
    return values, secrets


def _requested_snapshot(
    db: Session, changes: dict[str, object]
) -> tuple[dict[str, str], list[str]]:
    rows = _setting_rows(db, list(changes))
    values: dict[str, str] = {}
    secrets: list[str] = []
    for key, value in changes.items():
        row = rows.get(key)
        if row is not None and row.is_secret:
            values[key] = "[secret]"
            secrets.append(key)
        elif key in settings_service._SECRET_KEYS:
            values[key] = "[secret]"
            secrets.append(key)
        else:
            values[key] = "" if value is None else str(value)
    return values, secrets


def _serialize_change(row: SettingsChangeRequest) -> dict:
    return {
        "id": row.id,
        "ticket_number": _decrypt_text(row.ticket_number),
        "reason": _decrypt_text(row.reason),
        "environment": row.environment,
        "status": row.status,
        "actor_username": row.actor_username,
        "before": json.loads(row.before_values or "{}"),
        "after": json.loads(row.after_values or "{}"),
        "secret_keys": json.loads(row.secret_keys or "[]"),
        "change_hash": row.change_hash,
        "applied_at": row.applied_at.isoformat() if row.applied_at else None,
        "reverted_at": row.reverted_at.isoformat() if row.reverted_at else None,
        "reverted_by_username": row.reverted_by_username,
        "revert_reason": _decrypt_text(row.revert_reason),
    }


def list_changes(db: Session, limit: int = 50) -> list[dict]:
    rows = (
        db.query(SettingsChangeRequest)
        .order_by(SettingsChangeRequest.applied_at.desc(), SettingsChangeRequest.id.desc())
        .limit(max(1, min(limit, 200)))
        .all()
    )
    return [_serialize_change(row) for row in rows]


def apply_change_set(
    db: Session,
    actor: User,
    changes: dict[str, object],
    *,
    ticket_number: str | None,
    reason: str | None,
    request_ip: str | None = None,
) -> dict:
    if not changes:
        raise ProductionControlError("empty", "No settings were provided.", status_code=422)
    environment = deployment_mode(db)
    # Production always requires a ticket, even if an administrator later sets
    # the ticket mode to optional. The mode controls development behaviour and
    # the UI label; it cannot weaken the production gate.
    ticket = require_ticket(db, ticket_number, force=environment == "production")
    if environment == "production" and ticket_mode(db) == "off":
        raise ProductionControlError(
            "ticket_mode_invalid",
            "Production settings changes cannot use ticket mode 'off'.",
            status_code=422,
        )
    protected = PROTECTED_PHASE_KEYS & set(changes)
    if protected:
        raise ProductionControlError(
            "phase_locked",
            "Production phase settings can only be changed through the one-way cutover workflow.",
            status_code=403,
            details={"keys": sorted(protected)},
        )
    if environment == "production" and str(changes.get("settings_change_ticket_mode", "")) == "off":
        raise ProductionControlError(
            "ticket_mode_invalid",
            "Production cannot switch ticket enforcement off.",
            status_code=422,
        )
    reason_text = (reason or "").strip()
    if (ticket_mode(db) == "required" or environment == "production") and len(reason_text) < 5:
        raise ProductionControlError(
            "reason_required",
            "Describe the change and its ticket context in at least 5 characters.",
            status_code=422,
        )

    before, before_secrets = _snapshot(db, list(changes))
    after, after_secrets = _requested_snapshot(db, changes)
    secret_keys = sorted(set(before_secrets) | set(after_secrets))
    count = settings_service.bulk_update_settings(
        db, {key: str(value) for key, value in changes.items()}
    )
    if "rangebox_capacity_percent" in changes:
        from app.services import rangebox_capacity

        rangebox_capacity.invalidate_cache()

    change_hash = _hash(
        json.dumps(
            {
                "ticket": ticket or "",
                "actor_id": actor.id,
                "environment": environment,
                "before": before,
                "after": after,
            },
            sort_keys=True,
        )
    )
    row = SettingsChangeRequest(
        ticket_number=encrypt_secret(ticket) if ticket else None,
        reason=encrypt_secret(reason_text) if reason_text else None,
        environment=environment,
        status="applied",
        actor_id=actor.id,
        actor_username=actor.username,
        before_values=json.dumps(before, sort_keys=True),
        after_values=json.dumps(after, sort_keys=True),
        secret_keys=json.dumps(secret_keys),
        change_hash=change_hash,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    audit.log_admin_action(
        action="SETTINGS_CHANGE_APPLIED",
        admin_user_id=actor.id,
        admin_username=actor.username,
        target_type="settings_change",
        target_id=row.id,
        details={
            "keys": sorted(changes),
            "ticket_hash": _hash(ticket) if ticket else None,
            "change_hash": change_hash,
            "count": count,
        },
        ip_address=request_ip,
    )
    security_events.record(
        "settings.change_applied",
        category="audit",
        severity="notice",
        outcome="success",
        actor=actor,
        target_type="settings_change",
        target_id=row.id,
        detail={
            "keys": sorted(changes),
            "secret_keys": secret_keys,
            "ticket_present": bool(ticket),
            "ticket_hash": _hash(ticket) if ticket else None,
            "change_hash": change_hash,
        },
    )
    return _serialize_change(row)


def revert_change_set(
    db: Session,
    actor: User,
    change_id: int,
    *,
    reason: str,
    request_ip: str | None = None,
) -> dict:
    row = db.query(SettingsChangeRequest).filter(SettingsChangeRequest.id == change_id).first()
    if row is None:
        raise ProductionControlError("not_found", "Change set not found.", status_code=404)
    if row.status != "applied":
        raise ProductionControlError(
            "not_revertable",
            "Only an applied change set can be reverted.",
            status_code=409,
        )
    secret_keys = json.loads(row.secret_keys or "[]")
    if secret_keys:
        raise ProductionControlError(
            "secret_not_revertable",
            "This change set includes secret values. Restore them through the provider workflow; they are deliberately not stored in the change set.",
            status_code=409,
            details={"keys": secret_keys},
        )
    before = json.loads(row.before_values or "{}")
    after = json.loads(row.after_values or "{}")
    current = {
        key: settings_service.get_setting_fresh(db, key, "") or "" for key in after
    }
    drifted = [key for key, value in after.items() if current.get(key) != value]
    if drifted:
        raise ProductionControlError(
            "drifted",
            "The current settings no longer match this change set. Review the drift before reverting.",
            status_code=409,
            details={"keys": drifted},
        )
    reason_text = (reason or "").strip()
    if len(reason_text) < 5:
        raise ProductionControlError(
            "reason_required",
            "Describe why the change is being reverted in at least 5 characters.",
            status_code=422,
        )

    settings_service.bulk_update_settings(db, before)
    row.status = "reverted"
    row.reverted_at = _now()
    row.reverted_by_username = actor.username
    row.revert_reason = encrypt_secret(reason_text)
    db.commit()
    db.refresh(row)

    audit.log_admin_action(
        action="SETTINGS_CHANGE_REVERTED",
        admin_user_id=actor.id,
        admin_username=actor.username,
        target_type="settings_change",
        target_id=row.id,
        details={"change_id": row.id, "keys": sorted(before), "reason": reason_text},
        ip_address=request_ip,
    )
    security_events.record(
        "settings.change_reverted",
        category="audit",
        severity="warning",
        outcome="success",
        actor=actor,
        target_type="settings_change",
        target_id=row.id,
        detail={"keys": sorted(before), "change_id": row.id},
    )
    return _serialize_change(row)


def _sample_users(db: Session) -> list[User]:
    users = db.query(User).all()
    return [
        user
        for user in users
        if SAMPLE_USER_RE.search(user.username or "")
        or SAMPLE_USER_RE.search(user.email or "")
    ]


def _sample_counts(db: Session, user_ids: list[int]) -> dict[str, int]:
    if not user_ids:
        return {name: 0 for name in (
            "auth_sessions", "refresh_tokens", "lab_sessions", "lab_completions",
            "flag_attempts", "quiz_attempts", "course_enrollments", "achievements",
            "learner_snapshots",
        )}
    models = [
        ("auth_sessions", AuthSession, AuthSession.user_id),
        ("refresh_tokens", RefreshToken, RefreshToken.user_id),
        ("lab_sessions", LabSession, LabSession.user_id),
        ("lab_completions", LabCompletion, LabCompletion.user_id),
        ("flag_attempts", FlagAttempt, FlagAttempt.user_id),
        ("quiz_attempts", QuizAttempt, QuizAttempt.user_id),
        ("course_enrollments", CourseEnrollment, CourseEnrollment.user_id),
        ("achievements", Achievement, Achievement.user_id),
        ("learner_snapshots", LearnerSnapshot, LearnerSnapshot.user_id),
    ]
    return {
        name: int(
            db.query(func.count())
            .select_from(model)
            .filter(column.in_(user_ids))
            .scalar()
            or 0
        )
        for name, model, column in models
    }


def sample_data_preview(db: Session) -> dict:
    users = _sample_users(db)
    ids = [user.id for user in users]
    owned_courses = (
        int(db.query(func.count()).select_from(Course).filter(Course.instructor_id.in_(ids)).scalar() or 0)
        if ids
        else 0
    )
    return {
        "deployment_mode": deployment_mode(db),
        "data_collection_mode": data_collection_mode(db),
        "is_production": deployment_mode(db) == "production",
        "ticket_mode": ticket_mode(db),
        "confirmation_phrase": CONFIRMATION_PHRASE,
        "sample_users": len(users),
        "counts": _sample_counts(db, ids),
        "owned_courses_blocked": owned_courses,
        "warnings": [
            "This permanently deletes sample/test accounts and their learner records from this deployment.",
            "This cannot be reversed from the application. Returning to development requires a database restore and operator approval.",
            "Security, audit, and consent evidence is retained or anonymised; it is not silently deleted.",
            "The password, ticket, actor, timestamp, counts, and evidence hash are recorded for the one-way transition.",
            "After cutover, settings changes require a ticket and are tracked as revertible change sets.",
        ],
    }


def cutover_to_production(
    db: Session,
    actor: User,
    *,
    ticket_number: str,
    password: str,
    confirmation: str,
    acknowledge_data_loss: bool,
    acknowledge_one_way: bool,
    reason: str | None,
    request_ip: str | None = None,
) -> dict:
    if deployment_mode(db) == "production" or db.query(ProductionCutover).count():
        raise ProductionControlError(
            "already_production",
            "This deployment has already completed the one-way production cutover.",
            status_code=409,
        )
    if confirmation != CONFIRMATION_PHRASE:
        raise ProductionControlError(
            "confirmation_mismatch",
            f"Type {CONFIRMATION_PHRASE} exactly to confirm the cutover.",
            status_code=422,
        )
    if not acknowledge_data_loss or not acknowledge_one_way:
        raise ProductionControlError(
            "acknowledgement_required",
            "Acknowledge both the sample-data deletion and the one-way transition.",
            status_code=422,
        )
    if not verify_password(password, actor.hashed_password):
        security_events.record(
            "production.cutover_denied",
            category="security",
            severity="critical",
            outcome="denied",
            actor=actor,
            detail={"reason": "password_mismatch"},
        )
        raise ProductionControlError(
            "password_invalid",
            "The current administrator password is incorrect.",
            status_code=401,
        )
    ticket = require_ticket(db, ticket_number, force=True)
    notes = (reason or "").strip()
    if len(notes) < 5:
        raise ProductionControlError(
            "reason_required",
            "Describe the cutover ticket and approval context in at least 5 characters.",
            status_code=422,
        )

    preview = sample_data_preview(db)
    users = _sample_users(db)
    cleared = 0
    blocked = 0
    for user in users:
        if user.role == "admin":
            blocked += 1
            continue
        if db.query(Course).filter(Course.instructor_id == user.id).first() is not None:
            blocked += 1
            continue
        try:
            erase_user(
                db,
                user,
                actor="production-cutover",
                external_cleanup=False,
                write_ledger=False,
            )
            cleared += 1
        except ErasureBlocked:
            db.rollback()
            blocked += 1
        except Exception:
            db.rollback()
            blocked += 1

    summary = {
        "sample_users_seen": len(users),
        "users_cleared": cleared,
        "users_blocked": blocked,
        "before_counts": preview["counts"],
        "owned_courses_blocked": preview["owned_courses_blocked"],
    }
    cutover_at = _now()
    evidence = {
        "actor_id": actor.id,
        "actor_username": actor.username,
        "ticket_hash": _hash(ticket),
        "cutover_at": cutover_at.isoformat(),
        "summary": summary,
    }
    evidence_hash = _hash(json.dumps(evidence, sort_keys=True))

    # Keep the phase change and its evidence in one transaction. The generic
    # settings API refuses these keys, so this is the only forward path.
    for key, value in {
        "deployment_mode": "production",
        "data_collection_mode": "production",
        "settings_change_ticket_mode": "required",
    }.items():
        row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
        if row is None:
            db.add(PlatformSetting(key=key, value=value))
        else:
            row.value = value
    row = ProductionCutover(
        actor_id=actor.id,
        actor_username=actor.username,
        ticket_number=encrypt_secret(ticket),
        notes=encrypt_secret(notes),
        cutover_at=cutover_at,
        sample_data_summary=json.dumps(summary, sort_keys=True),
        password_confirmed=True,
        evidence_hash=evidence_hash,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    settings_service.invalidate_cache()

    audit.log_admin_action(
        action="PRODUCTION_CUTOVER",
        admin_user_id=actor.id,
        admin_username=actor.username,
        target_type="deployment",
        target_id=row.id,
        details={
            "ticket_hash": _hash(ticket),
            "summary": summary,
            "evidence_hash": evidence_hash,
        },
        ip_address=request_ip,
    )
    security_events.record(
        "production.cutover",
        category="security",
        severity="critical",
        outcome="success",
        actor=actor,
        target_type="deployment",
        target_id=row.id,
        detail={
            "ticket_hash": _hash(ticket),
            "summary": summary,
            "evidence_hash": evidence_hash,
            "password_confirmed": True,
        },
    )
    return {
        "cutover_id": row.id,
        "evidence_hash": evidence_hash,
        "summary": summary,
        "warnings": preview["warnings"],
        "production_locked": True,
    }
