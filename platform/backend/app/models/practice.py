"""Certification practice sessions.

A practice session is a standalone drill over the reviewed certification bank.
It is separate from the three-question exercise check: the learner chooses a
pathway, a mock exam or a domain drill, and gets a timed, randomised attempt.

The answer key never leaves the server before submission. Option order is
shuffled per question and stored on the session row, so a client cannot infer
the correct answer from the original bank order.
"""

from __future__ import annotations

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
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


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

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
    pathway_id = Column(String(64), nullable=False, index=True)
    pathway_name = Column(String(120), nullable=False)
    mode = Column(String(16), nullable=False, default="mock")
    domain_id = Column(String(32), nullable=True)
    question_count = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    pass_mark = Column(Integer, nullable=False, default=70)
    status = Column(
        String(16),
        nullable=False,
        default="active",
        server_default="active",
        index=True,
    )
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)
    total = Column(Integer, nullable=True)
    percentage = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=True)
    timed_out = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    learner = relationship("User")
    questions = relationship(
        "PracticeSessionQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="PracticeSessionQuestion.position",
    )

    __table_args__ = (
        Index("ix_practice_sessions_user_started", "user_id", "started_at"),
    )


class PracticeSessionQuestion(Base):
    __tablename__ = "practice_session_questions"

    id = Column(Integer, primary_key=True)
    session_id = Column(
        Integer,
        ForeignKey("practice_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position = Column(Integer, nullable=False)
    question_id = Column(String(64), nullable=False, index=True)
    domain_id = Column(String(32), nullable=True)
    option_order = Column(JSON, nullable=False)
    selected_index = Column(Integer, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    answered_at = Column(DateTime, nullable=True)

    session = relationship("PracticeSession", back_populates="questions")

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "position",
            name="uq_practice_session_position",
        ),
    )
