"""Competency contract reviews with a review cycle.

A review is an append-only record of what an instructor inspected, what they
approved, and when the contract is due again. The generated contract file stays
the release artifact; a signed review is exported into the overrides file by an
administrator.
"""

from __future__ import annotations

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.database import Base

REVIEW_STATUSES = (
    "draft",
    "signed",
    "changes_requested",
    "superseded",
)
REVIEW_DECISIONS = ("approved", "changes_requested")


class CompetencyContractReview(Base):
    __tablename__ = "competency_contract_reviews"

    id = Column(Integer, primary_key=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    lab_slug = Column(String(120), nullable=False, index=True)
    status = Column(
        String(24),
        nullable=False,
        default="draft",
        server_default="draft",
        index=True,
    )
    decision = Column(String(24), nullable=True)
    contract_snapshot = Column(JSON, nullable=False)
    contract_hash = Column(String(64), nullable=False)
    baseline_hash = Column(String(64), nullable=True)
    deviation = Column(JSON, nullable=True)
    lab_hash = Column(String(64), nullable=False)
    taxonomy_hash = Column(String(64), nullable=False)
    rationale = Column(Text, nullable=False)
    attestation = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    reviewer_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reviewer_name = Column(String(120), nullable=True)
    reviewer_role = Column(String(32), nullable=False)
    review_cycle_months = Column(
        Integer,
        nullable=False,
        default=12,
        server_default="12",
    )
    next_review_at = Column(DateTime, nullable=True, index=True)
    signed_at = Column(DateTime, nullable=True)
    exported_at = Column(DateTime, nullable=True)
    exported_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    reviewer = relationship("User", foreign_keys=[reviewer_id])
    exporter = relationship("User", foreign_keys=[exported_by_id])

    __table_args__ = (
        Index("ix_contract_reviews_lab_status", "lab_slug", "status"),
        Index("ix_contract_reviews_tenant_status", "institution_id", "status"),
        Index("ix_contract_reviews_next_review", "next_review_at"),
    )
