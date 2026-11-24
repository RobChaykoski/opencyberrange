"""Persisted capstone plans.

A plan is a proposal with a request, a generated plan, and a validation report.
Saving or editing a plan does not publish it. Approval is a separate action and
requires the validation gate to pass. Publication to a course is later.
"""

from __future__ import annotations

from sqlalchemy import (
    JSON,
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

CAPSTONE_STATUSES = ("draft", "approved", "archived")


class CapstonePlan(Base):
    __tablename__ = "capstone_plans"

    id = Column(Integer, primary_key=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    profile_id = Column(String(64), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    status = Column(
        String(16),
        nullable=False,
        default="draft",
        server_default="draft",
        index=True,
    )
    version = Column(Integer, nullable=False, default=1, server_default="1")
    request = Column(JSON, nullable=False)
    plan = Column(JSON, nullable=False)
    validation = Column(JSON, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    approved_at = Column(DateTime, nullable=True)
    approved_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    owner = relationship("User", foreign_keys=[owner_id])
    approver = relationship("User", foreign_keys=[approved_by_id])

    __table_args__ = (
        Index("ix_capstone_plans_owner_status", "owner_id", "status"),
        Index("ix_capstone_plans_tenant_status", "institution_id", "status"),
    )
