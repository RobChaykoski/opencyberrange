"""Consent state, revocation workflow, job queue, and proof-only audit tables.

These tables deliberately store no derived learner payloads. The audit table
keeps a keyed subject hash so a proof can survive account erasure without
retaining the account identifier.
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)

from app.database import Base


class ConsentState(Base):
    """Current consent state for one learner and one feature."""

    __tablename__ = "consent_states"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consent_type = Column(String(32), nullable=False)
    granted = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    version = Column(Integer, nullable=False, default=1, server_default=text("1"))
    revocation_in_progress = Column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    revoked_at = Column(DateTime, nullable=True)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "consent_type", name="uq_consent_state_user_type"
        ),
        Index("ix_consent_state_type_granted", "consent_type", "granted"),
    )


class ConsentEvent(Base):
    """Append-only consent decision history. Rows are never updated."""

    __tablename__ = "consent_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consent_type = Column(String(32), nullable=False)
    action = Column(String(16), nullable=False)  # grant | revoke
    consent_version = Column(Integer, nullable=False)
    actor = Column(String(16), nullable=False, default="self")
    reason = Column(String(500), nullable=True)
    occurred_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_consent_events_user_time", "user_id", "occurred_at"),
        Index("ix_consent_events_type_time", "consent_type", "occurred_at"),
    )


class ConsentRevocation(Base):
    """One revocation workflow for one learner and consent type."""

    __tablename__ = "consent_revocations"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consent_type = Column(String(32), nullable=False)
    consent_version = Column(Integer, nullable=False)
    audit_id = Column(String(36), nullable=False, unique=True, index=True)
    status = Column(
        String(16), nullable=False, default="pending", server_default="pending"
    )
    requested_at = Column(DateTime, server_default=func.now(), nullable=False)
    started_at = Column(DateTime, nullable=True)
    purge_completed_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verification_attempts = Column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    suppression_recorded = Column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    last_error = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "consent_type",
            "consent_version",
            name="uq_consent_revocation_version",
        ),
        Index("ix_consent_revocations_status", "status"),
    )


class ConsentJob(Base):
    """Durable purge or verification work item.

    Purge jobs are grouped by revocation and executed in one database
    transaction, so a failure leaves the whole revocation untouched. The rows
    remain individually visible for dashboards and retries.
    """

    __tablename__ = "consent_jobs"

    id = Column(Integer, primary_key=True)
    revocation_id = Column(
        Integer,
        ForeignKey("consent_revocations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consent_type = Column(String(32), nullable=False)
    kind = Column(String(16), nullable=False)  # purge | verify
    service = Column(String(32), nullable=False)
    action = Column(String(64), nullable=False)
    slot = Column(String(16), nullable=False, default="", server_default="")
    status = Column(
        String(16), nullable=False, default="queued", server_default="queued"
    )
    attempts = Column(Integer, nullable=False, default=0, server_default=text("0"))
    available_at = Column(DateTime, server_default=func.now(), nullable=False)
    lease_until = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "revocation_id",
            "kind",
            "service",
            "action",
            "slot",
            name="uq_consent_job_target",
        ),
        Index("ix_consent_jobs_due", "status", "available_at"),
    )


class ConsentAudit(Base):
    """Proof that a revocation was processed. Stores no deleted payload."""

    __tablename__ = "consent_audits"

    id = Column(Integer, primary_key=True)
    audit_id = Column(String(36), nullable=False, unique=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    subject_hash = Column(String(64), nullable=False, index=True)
    consent_type = Column(String(32), nullable=False)
    consent_version = Column(Integer, nullable=False)
    revoked_at = Column(DateTime, nullable=False)
    jobs_completed = Column(Text, nullable=False, default="[]", server_default="[]")
    verified = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    verified_at = Column(DateTime, nullable=True)
    verification_slots = Column(Text, nullable=False, default="[]", server_default="[]")
    suppression_recorded = Column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_consent_audits_subject_type", "subject_hash", "consent_type"),
    )


class ConsentSuppression(Base):
    """Database mirror of the file-backed suppression ledger.

    The file ledger is the restore-proof source of truth. This table lets the
    dashboard and sweep find subject identifiers without scanning every user.
    """

    __tablename__ = "consent_suppressions"

    id = Column(Integer, primary_key=True)
    subject_hash = Column(String(64), nullable=False, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    consent_type = Column(String(32), nullable=False)
    consent_version = Column(Integer, nullable=False)
    reason = Column(String(64), nullable=False, default="consent_revoked")
    recorded_at = Column(DateTime, server_default=func.now(), nullable=False)
    cancelled_at = Column(DateTime, nullable=True)
    ledger_path = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "subject_hash",
            "consent_type",
            "consent_version",
            name="uq_consent_suppression_version",
        ),
        Index("ix_consent_suppressions_user_type", "user_id", "consent_type"),
    )
