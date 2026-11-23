"""Release 6 evidence ledger.

An evidence record is a demonstrated capability, not an activity signal. It
keeps the rubric it was judged against, the competencies and criteria it
supports, the artifact hash, and its provenance. Content is append-only: a
correction is a new record that supersedes the old one. Only review workflow
fields (``status``, ``reviewer_id``, ``review_notes``) may change after insert.
"""

from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
    func,
    inspect,
    text,
)
from sqlalchemy.orm import relationship

from app.database import Base

EVIDENCE_SOURCE_TYPES = (
    "flag",
    "validation_step",
    "workbook",
    "analyst_answer",
    "quiz",
    "artifact",
    "capstone",
    "instructor",
)
EVIDENCE_STATUSES = ("collected", "in_review", "accepted", "rejected", "superseded")
EVIDENCE_VISIBILITIES = ("learner", "instructor", "both")
EVIDENCE_CONFIDENCES = ("low", "medium", "high")
EVIDENCE_DECISIONS = ("accepted", "rejected", "more_evidence")

# Content columns that must never change after the record is created. Review
# transitions are limited to status, reviewer_id, and review_notes.
IMMUTABLE_EVIDENCE_FIELDS = frozenset(
    {
        "institution_id",
        "learner_id",
        "source_type",
        "source_id",
        "rubric_id",
        "rubric_version",
        "confidence",
        "confidence_reason",
        "collected_at",
        "provenance",
        "provenance_version",
        "visibility",
        "formula_version",
        "supersedes_id",
        "source_fingerprint",
        "artifact_uri",
        "artifact_mime",
        "artifact_size",
        "artifact_sha256",
    }
)


class EvidenceRecord(Base):
    """One demonstrated capability, scoped to a learner and a tenant."""

    __tablename__ = "evidence_records"

    id = Column(Integer, primary_key=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    learner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type = Column(String(32), nullable=False)
    source_id = Column(String(160), nullable=False)
    rubric_id = Column(String(64), nullable=False)
    rubric_version = Column(String(16), nullable=False)
    confidence = Column(String(16), nullable=False, default="medium")
    confidence_reason = Column(String(500), nullable=True)
    collected_at = Column(DateTime, nullable=False)
    provenance = Column(String(255), nullable=False)
    provenance_version = Column(String(32), nullable=True)
    visibility = Column(String(16), nullable=False, default="both", server_default="both")
    status = Column(
        String(16),
        nullable=False,
        default="collected",
        server_default="collected",
    )
    reviewer_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    review_notes = Column(String(1000), nullable=True)
    formula_version = Column(String(32), nullable=False)
    supersedes_id = Column(
        Integer,
        ForeignKey("evidence_records.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_fingerprint = Column(String(64), nullable=False)
    artifact_uri = Column(String(500), nullable=True)
    artifact_mime = Column(String(120), nullable=True)
    artifact_size = Column(Integer, nullable=True)
    artifact_sha256 = Column(String(64), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    learner = relationship("User", foreign_keys=[learner_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    competencies = relationship(
        "EvidenceCompetency",
        back_populates="evidence",
        order_by="EvidenceCompetency.id",
    )
    reviews = relationship(
        "EvidenceReview",
        back_populates="evidence",
        order_by="EvidenceReview.id",
    )

    __table_args__ = (
        UniqueConstraint(
            "source_fingerprint",
            name="uq_evidence_source_fingerprint",
        ),
        Index("ix_evidence_learner_collected", "learner_id", "collected_at"),
        Index("ix_evidence_learner_status", "learner_id", "status"),
        Index("ix_evidence_tenant_status", "institution_id", "status"),
        Index("ix_evidence_rubric", "rubric_id", "rubric_version"),
    )


class EvidenceCompetency(Base):
    """Link from an evidence record to one taxonomy competency."""

    __tablename__ = "evidence_competencies"

    id = Column(Integer, primary_key=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    evidence_id = Column(
        Integer,
        ForeignKey("evidence_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    competency_id = Column(String(32), nullable=False, index=True)
    criteria = Column(Text, nullable=False, default="[]")  # JSON array of rubric criteria
    weight = Column(Float, nullable=False, default=1.0, server_default=text("1.0"))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    evidence = relationship("EvidenceRecord", back_populates="competencies")

    __table_args__ = (
        UniqueConstraint(
            "evidence_id",
            "competency_id",
            name="uq_evidence_competency",
        ),
        Index("ix_evidence_competency_lookup", "competency_id", "evidence_id"),
    )


class EvidenceReview(Base):
    """Append-only instructor decision. A new decision is a new row."""

    __tablename__ = "evidence_reviews"

    id = Column(Integer, primary_key=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    evidence_id = Column(
        Integer,
        ForeignKey("evidence_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rubric_id = Column(String(64), nullable=False)
    rubric_version = Column(String(16), nullable=False)
    decision = Column(String(20), nullable=False)
    criterion_scores = Column(Text, nullable=False, default="{}")  # JSON id -> 0..3
    weighted_score = Column(Float, nullable=True)
    notes = Column(String(1000), nullable=True)
    next_step = Column(String(500), nullable=True)
    reviewed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    evidence = relationship("EvidenceRecord", back_populates="reviews")
    reviewer = relationship("User")

    __table_args__ = (
        Index("ix_evidence_reviews_record_time", "evidence_id", "reviewed_at"),
    )


@event.listens_for(EvidenceRecord, "before_update")
def _guard_evidence_content(mapper, connection, target):  # noqa: ARG001
    """Reject an in-place edit of record content.

    The database trigger installed at startup enforces the same rule on
    PostgreSQL. This listener keeps the local SQLite test suite honest.
    """

    state = inspect(target)
    changed = {
        name
        for name in IMMUTABLE_EVIDENCE_FIELDS
        if getattr(state.attrs, name).history.has_changes()
    }
    if changed:
        raise ValueError(
            "evidence content is append-only; create a new record that "
            f"supersedes this one (changed: {', '.join(sorted(changed))})"
        )
