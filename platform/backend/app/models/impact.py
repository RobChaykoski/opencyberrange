"""Impact and legacy ledger.

Capability evidence answers what a learner can do. A contribution answers what
they chose to do with it. Every contribution is verified by someone other than
the author before it earns full credit, and scoring is deliberately sublinear:
reach grows logarithmically, repeats diminish, and unused work decays.

Stewardship is separate from contribution. It is a trust record with a 100-point
baseline, changed only by an administrator with a stated reason and an evidence
reference.
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
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.database import Base

IMPACT_DIMENSIONS = ("build", "protect", "teach", "serve")
IMPACT_STATUSES = ("draft", "submitted", "verified", "rejected")
IMPACT_VALIDATION_LEVELS = (
    "self",
    "peer",
    "instructor",
    "industry",
    "adoption",
)
IMPACT_ORIGINALITIES = ("copied", "modified", "original", "innovative")
STEWARDSHIP_CATEGORIES = ("positive", "negative", "restoration")
STEWARDSHIP_VISIBILITIES = ("private", "instructor")


class ImpactContribution(Base):
    """One verified or pending contribution to a community or organization."""

    __tablename__ = "impact_contributions"

    id = Column(Integer, primary_key=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dimension = Column(String(16), nullable=False, index=True)
    kind = Column(String(64), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=True)
    base_points = Column(Integer, nullable=False, default=25)
    reach_count = Column(Integer, nullable=False, default=0)
    quality_rating = Column(Float, nullable=True)
    validation_level = Column(
        String(16),
        nullable=False,
        default="self",
        server_default="self",
    )
    originality = Column(
        String(16),
        nullable=False,
        default="original",
        server_default="original",
    )
    status = Column(
        String(16),
        nullable=False,
        default="draft",
        server_default="draft",
        index=True,
    )
    occurred_at = Column(DateTime, nullable=False, server_default=func.now())
    last_used_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verified_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    evidence_id = Column(
        Integer,
        ForeignKey("evidence_records.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    content_hash = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)
    review_notes = Column(Text, nullable=True)

    contributor = relationship("User", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by_id])

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "content_hash",
            name="uq_impact_contribution_hash",
        ),
        Index("ix_impact_contributions_user_status", "user_id", "status"),
        Index("ix_impact_contributions_tenant_status", "institution_id", "status"),
    )


class StewardshipEvent(Base):
    """A trust event. Negative events always name a reason and a reference."""

    __tablename__ = "stewardship_events"

    id = Column(Integer, primary_key=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    points_delta = Column(Integer, nullable=False)
    category = Column(String(16), nullable=False, default="positive")
    reason = Column(String(300), nullable=False)
    occurred_at = Column(DateTime, nullable=False, server_default=func.now())
    recorded_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    evidence_ref = Column(String(300), nullable=True)
    visibility = Column(
        String(16),
        nullable=False,
        default="private",
        server_default="private",
    )

    learner = relationship("User", foreign_keys=[user_id])
    recorder = relationship("User", foreign_keys=[recorded_by_id])

    __table_args__ = (
        Index("ix_stewardship_events_user", "user_id", "occurred_at"),
    )
