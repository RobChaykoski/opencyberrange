"""Learner workbook answers.

The workbook is a static Markdown site, so the platform keeps the learner's
current answer separately and snapshots each distinct version into the evidence
ledger. The live row is editable; evidence records are not.
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


class WorkbookAnswer(Base):
    """The learner's current answer for one prompt on one exercise."""

    __tablename__ = "workbook_answers"

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
    lab_id = Column(
        Integer,
        ForeignKey("labs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prompt_key = Column(String(64), nullable=False, default="reflection")
    answer_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    learner = relationship("User")
    lab = relationship("Lab")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "lab_id",
            "prompt_key",
            name="uq_workbook_answer",
        ),
        Index("ix_workbook_answer_user_lab", "user_id", "lab_id"),
    )
