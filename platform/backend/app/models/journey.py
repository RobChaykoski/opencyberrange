"""Learner-chosen journeys.

A journey is a direction, not a permanent label. The learner can choose one
primary journey at a time and change it later; the evidence record keeps the
history.
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
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class LearnerJourney(Base):
    __tablename__ = "learner_journeys"

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
    journey_id = Column(String(64), nullable=False, index=True)
    is_primary = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    status = Column(
        String(16),
        nullable=False,
        default="active",
        server_default="active",
    )
    chosen_at = Column(DateTime, server_default=func.now(), nullable=False)

    learner = relationship("User")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "journey_id",
            name="uq_learner_journey",
        ),
        Index("ix_learner_journey_primary", "user_id", "is_primary"),
    )
