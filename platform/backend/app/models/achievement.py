"""ORM models for achievement."""

from app.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Achievement(Base):
    """Micro-credentials awarded to students within a course, or globally.

    ``course_id`` is NULL for awards earned outside a course (standalone labs,
    DevFest competition) so the hidden/global achievements remain reachable
    without an enrollment.
    """
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=True, index=True)
    achievement_type = Column(String(30), nullable=False)
    awarded_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="achievements")
    course = relationship("Course", back_populates="achievements")
    lab = relationship("Lab")

    __table_args__ = (
        Index('ix_achievement_unique', 'user_id', 'course_id', 'achievement_type', 'lab_id', unique=True),
        Index('ix_achievements_awarded_at', awarded_at.desc()),
    )


class AchievementCelebration(Base):
    """One voluntary, anonymous celebration of a public achievement.

    The ``user_id`` exists only to enforce one celebration per person and to
    prevent duplicate rows. The celebration wall never returns the celebrator's
    identity; it exposes the count only. Celebrations are not learning metrics
    and are never joined to analytics, progress, or grading.
    """
    __tablename__ = "achievement_celebrations"

    id = Column(Integer, primary_key=True)
    achievement_id = Column(
        Integer,
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime, server_default=func.now())

    achievement = relationship("Achievement")
    user = relationship("User")

    __table_args__ = (
        Index(
            "ix_achievement_celebration_unique",
            "achievement_id",
            "user_id",
            unique=True,
        ),
    )


class CustomAchievement(Base):
    """Admin-defined achievement awarded for aggregate progress.

    Built-in achievements are fixed code paths; this table lets an operator add
    extra goals (for example "complete 10 exercises without hints") without a
    deployment. Awards are stored in ``achievements`` as ``custom_<id>``.
    """
    __tablename__ = "custom_achievements"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(16), nullable=False, default="\U0001F3C5")
    trigger = Column(String(30), nullable=False, default="labs_completed")
    threshold = Column(Integer, nullable=False, default=1)
    # Presentation and value metadata. ``points`` is derived from tier and
    # difficulty so a harder badge is worth more without a second scoring table.
    group_key = Column(String(30), nullable=False, default="custom")
    tier = Column(String(20), nullable=False, default="bronze")
    difficulty = Column(String(20), nullable=False, default="standard")
    points = Column(Integer, nullable=False, default=10)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())


class OpenBadgeCredential(Base):
    """Hosted Open Badges 3.0 credential for a completed level certificate."""

    __tablename__ = "open_badge_credentials"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    certificate_id = Column(String(80), nullable=False, index=True)
    track_slug = Column(String(100), nullable=False)
    level_id = Column(Integer, ForeignKey("levels.id", ondelete="SET NULL"), nullable=True)
    subject_id = Column(String(64), nullable=False, unique=True, index=True)
    jti = Column(String(64), nullable=False, unique=True, index=True)
    achievement_name = Column(String(200), nullable=False)
    achievement_description = Column(Text, nullable=True)
    criteria_url = Column(String(500), nullable=True)
    evidence_url = Column(String(500), nullable=True)
    issued_at = Column(DateTime, server_default=func.now())
    recipient_name_opt_in = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    revocation_reason = Column(String(500), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "certificate_id", name="uq_open_badge_source"),
    )

    user = relationship("User", foreign_keys=[user_id])
