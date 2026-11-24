"""ORM models for platform."""

from app.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class PlatformSetting(Base):
    """Key-value store for runtime-configurable platform settings.
    Replaces hardcoded .env values with web-editable configuration."""
    __tablename__ = "platform_settings"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)
    category = Column(String(50), default="general")  # general, security, vpn, labs, appearance
    description = Column(Text, nullable=True)
    is_secret = Column(Boolean, default=False)  # If true, value is never returned in GET responses
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ActivityEvent(Base):
    """Polymorphic event log for dashboard feeds and analytics."""
    __tablename__ = "activity_events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    target_type = Column(String(30), nullable=True)
    target_id = Column(Integer, nullable=True)
    target_label = Column(String(200), nullable=True)
    detail = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    actor = relationship("User", foreign_keys=[actor_id])


class SystemMetric(Base):
    """Point-in-time host and platform metrics for the admin graphs."""

    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    load1 = Column(Float, nullable=True)
    load5 = Column(Float, nullable=True)
    load15 = Column(Float, nullable=True)
    cpu_count = Column(Integer, nullable=True)
    mem_total_mb = Column(Integer, nullable=True)
    mem_used_mb = Column(Integer, nullable=True)
    disk_total_gb = Column(Float, nullable=True)
    disk_used_gb = Column(Float, nullable=True)
    active_sessions = Column(Integer, nullable=True)
    rangebox_count = Column(Integer, nullable=True)
    docker_containers = Column(Integer, nullable=True)
    docker_images = Column(Integer, nullable=True)
    db_connections = Column(Integer, nullable=True)


class DataIntegrityLedger(Base):
    """Append-only ledger of application writes to critical tables.

    A PostgreSQL trigger writes one row per INSERT, UPDATE, or DELETE. The
    ``actor_type`` is ``user`` when the application has an authenticated actor,
    ``system`` for an application job with no user, and ``unattributed`` for a
    write that bypassed the application (for example, manual SQL).

    The ledger stores row hashes, not row contents. It is evidence of change,
    not a copy of the data.
    """
    __tablename__ = "data_integrity_ledger"

    id = Column(Integer, primary_key=True)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    table_name = Column(String(64), nullable=False)
    row_pk = Column(String(128), nullable=False)
    operation = Column(String(8), nullable=False)
    row_hash = Column(String(64), nullable=False)
    actor_type = Column(String(16), nullable=False, server_default="unattributed")
    actor_id = Column(Integer, nullable=True)
    request_id = Column(String(64), nullable=True)
    prev_hash = Column(String(64), nullable=False)
    entry_hash = Column(String(64), nullable=False)


class DataIntegrityReview(Base):
    """Administrator review of an unattributed integrity-ledger write.

    The ledger is append-only, so a review never edits or hides the original
    evidence. It records who reviewed the table/operation, the decision, and
    the reason. Rows are immutable and are themselves covered by the ledger.
    """
    __tablename__ = "data_integrity_reviews"

    id = Column(Integer, primary_key=True)
    table_name = Column(String(64), nullable=False, index=True)
    operation = Column(String(8), nullable=False)
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    write_count = Column(Integer, nullable=False, default=0)
    decision = Column(String(24), nullable=False)
    note = Column(Text, nullable=False)
    # Snapshot the reviewer's identity. Do not use a foreign key here: deleting
    # a user must not rewrite an immutable review row.
    reviewed_by_id = Column(Integer, nullable=True)
    reviewed_by_username = Column(String(64), nullable=False)
    reviewed_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ReportExport(Base):
    """Immutable manifest for a generated instructor report.

    The report carries its report id in the footer or filename. Verification
    recomputes the file checksum and the keyed signature stored here, so a
    fabricated or edited report cannot be made to look platform-generated.
    """
    __tablename__ = "report_exports"

    id = Column(Integer, primary_key=True)
    report_id = Column(String(36), unique=True, index=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(40), nullable=False)
    format = Column(String(10), nullable=False)
    filename = Column(String(255), nullable=False)
    sha256 = Column(String(64), nullable=False)
    signature = Column(String(64), nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    generated_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

    course = relationship("Course")
    generator = relationship("User")


class SettingsChangeRequest(Base):
    """A reviewed settings change set.

    ``ticket_number``, ``reason``, and the before/after snapshots are stored
    encrypted or redacted. Secret setting values never enter this table in
    clear text. The row is the audit record for an apply/revert pair.
    """

    __tablename__ = "settings_change_requests"

    id = Column(Integer, primary_key=True)
    ticket_number = Column(Text, nullable=True)  # Fernet-encrypted
    reason = Column(Text, nullable=True)  # Fernet-encrypted
    environment = Column(String(20), nullable=False, default="development")
    status = Column(String(16), nullable=False, default="applied", index=True)
    actor_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    actor_username = Column(String(64), nullable=False)
    before_values = Column(Text, nullable=False)  # JSON; secrets replaced
    after_values = Column(Text, nullable=False)
    secret_keys = Column(Text, nullable=False, default="[]")
    change_hash = Column(String(64), nullable=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reverted_at = Column(DateTime(timezone=True), nullable=True)
    reverted_by_username = Column(String(64), nullable=True)
    revert_reason = Column(Text, nullable=True)  # Fernet-encrypted


class ProductionCutover(Base):
    """One-way production transition evidence.

    Stores counts and hashes, not learner identifiers or passwords. The ticket
    and notes are encrypted at rest; the password is never stored.
    """

    __tablename__ = "production_cutovers"

    id = Column(Integer, primary_key=True)
    actor_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    actor_username = Column(String(64), nullable=False)
    ticket_number = Column(Text, nullable=False)  # Fernet-encrypted
    notes = Column(Text, nullable=True)  # Fernet-encrypted
    cutover_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sample_data_summary = Column(Text, nullable=False)  # JSON counts only
    password_confirmed = Column(Boolean, nullable=False, default=False)
    evidence_hash = Column(String(64), nullable=False, index=True)
