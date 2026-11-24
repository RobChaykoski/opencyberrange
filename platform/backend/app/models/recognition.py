"""Recognition awards.

This is the values-based recognition layer: integrity, mentorship, service,
curiosity, and durable contribution. It is separate from the course
micro-credentials in ``achievement.py`` and separate from the Legacy Score.
Recognition is never currency: an award changes no score, permission, or grade.
"""

from __future__ import annotations

from sqlalchemy import (
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
from sqlalchemy.orm import relationship

from app.database import Base


class RecognitionAward(Base):
    __tablename__ = "achievement_awards"

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
    achievement_key = Column(String(64), nullable=False, index=True)
    source = Column(
        String(16),
        nullable=False,
        default="auto",
        server_default="auto",
    )
    awarded_at = Column(DateTime, nullable=False, server_default=func.now())
    awarded_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    evidence_ref = Column(String(300), nullable=True)
    note = Column(Text, nullable=True)
    seen_at = Column(DateTime, nullable=True)

    learner = relationship("User", foreign_keys=[user_id])
    awarder = relationship("User", foreign_keys=[awarded_by_id])

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "achievement_key",
            name="uq_achievement_award",
        ),
        Index("ix_achievement_awards_user_seen", "user_id", "seen_at"),
    )
