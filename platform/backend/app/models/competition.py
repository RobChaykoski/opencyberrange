"""ORM models for competition."""

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
    text,
)
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql import func


class Competition(Base):
    """An opt-in, time-boxed special event using a selected set of labs."""
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    # Optional event mark shown on the competition list and detail header.
    logo_data = deferred(Column(Text, nullable=True))
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, server_default=text("true"), nullable=False)
    # Archived events keep every result and leaderboard row but move out of the
    # default list, so a past competition stays readable without cluttering the
    # active ones. Delete remains a separate, explicit action.
    is_archived = Column(Boolean, default=False, server_default=text("false"), nullable=False)
    # Optional experience template. NULL is a standard competition; a key such
    # as "devfest-2027" adds the Cyber Discovery panels and certificate.
    experience_key = Column(String(40), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    creator = relationship("User", foreign_keys=[created_by])
    labs = relationship(
        "CompetitionLab", back_populates="competition", cascade="all, delete-orphan"
    )
    participants = relationship(
        "CompetitionParticipant", back_populates="competition",
        cascade="all, delete-orphan",
    )
    sponsors = relationship(
        "CompetitionSponsor", back_populates="competition",
        cascade="all, delete-orphan",
    )


class CompetitionSponsor(Base):
    """A Gold, Silver, or Bronze sponsor shown with a competition."""
    __tablename__ = "competition_sponsors"

    id = Column(Integer, primary_key=True)
    competition_id = Column(
        Integer, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    logo_data = deferred(Column(Text, nullable=True))
    website_url = Column(String(500), nullable=True)
    tier = Column(String(10), nullable=False, default="gold", server_default="gold")
    sort_order = Column(Integer, default=0)

    competition = relationship("Competition", back_populates="sponsors")

    __table_args__ = (
        Index("ix_competition_sponsor_order", "competition_id", "tier", "sort_order"),
    )


class CompetitionLab(Base):
    """A lab included in a competition."""
    __tablename__ = "competition_labs"

    id = Column(Integer, primary_key=True)
    competition_id = Column(
        Integer, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False
    )
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False)
    sort_order = Column(Integer, default=0)

    competition = relationship("Competition", back_populates="labs")
    lab = relationship("Lab")

    __table_args__ = (
        Index("ix_competition_lab_unique", "competition_id", "lab_id", unique=True),
    )


class CompetitionParticipant(Base):
    """Explicit opt-in for a competition leaderboard."""
    __tablename__ = "competition_participants"

    id = Column(Integer, primary_key=True)
    competition_id = Column(
        Integer, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    joined_at = Column(DateTime, server_default=func.now())
    # "new_user" when the account was created through a competition sign-up
    # link; "opt_in" when an existing account joined from the competitions page.
    source = Column(String(20), default="opt_in", server_default="opt_in", nullable=False)

    competition = relationship("Competition", back_populates="participants")
    user = relationship("User")

    __table_args__ = (
        Index(
            "ix_competition_participant_unique",
            "competition_id", "user_id", unique=True,
        ),
    )
