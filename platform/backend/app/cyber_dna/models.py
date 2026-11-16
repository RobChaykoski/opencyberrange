"""Cyber DNA tables. No foreign keys into exercise content.

``learner_id`` is the platform user id, but it is stored as a plain integer so
the DNA schema can be extracted or rebuilt without an exercise-table migration.
Erasure is handled by the DNA service, not by a database cascade.
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)

from app.database import Base


class DnaEvidenceRecord(Base):
    """Append-only evidence for one activity and one competency."""

    __tablename__ = "dna_evidence_records"

    id = Column(Integer, primary_key=True)
    learner_id = Column(Integer, nullable=False, index=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    event_id = Column(String(120), nullable=False)
    activity_id = Column(String(160), nullable=False)
    activity_category = Column(String(64), nullable=False)
    competency_id = Column(String(32), nullable=False)
    domain_id = Column(String(16), nullable=False)
    mapping_weight = Column(Float, nullable=False)
    score_contribution = Column(Float, nullable=False)
    difficulty = Column(String(20), nullable=True)
    attempts = Column(Integer, nullable=True)
    hints_used = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    prior_failed_attempts = Column(Integer, nullable=True)
    voluntary = Column(Boolean, nullable=False, default=True)
    source_version = Column(String(32), nullable=False)
    occurred_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "competency_id",
            name="uq_dna_evidence_event_competency",
        ),
        Index(
            "ix_dna_evidence_learner_competency",
            "learner_id",
            "competency_id",
            "occurred_at",
        ),
        Index("ix_dna_evidence_learner_time", "learner_id", "occurred_at"),
    )


class DnaSnapshot(Base):
    """Immutable behavior, interest, or affinity payload with its weights."""

    __tablename__ = "dna_snapshots"

    id = Column(Integer, primary_key=True)
    learner_id = Column(Integer, nullable=False, index=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    kind = Column(String(32), nullable=False)
    schema_version = Column(String(32), nullable=False)
    formula_version = Column(String(32), nullable=True)
    weights = Column(Text, nullable=False)
    payload = Column(Text, nullable=False)
    content_sha256 = Column(String(64), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            "kind",
            "content_sha256",
            name="uq_dna_snapshot_content",
        ),
        Index("ix_dna_snapshot_learner_kind", "learner_id", "kind"),
    )
