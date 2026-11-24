"""ORM models for survey."""

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
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Survey(Base):
    """Instructor-created survey attached to one or more courses."""
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    # JSON array of {prompt, type, options} question definitions.
    questions = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, server_default=text("true"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    creator = relationship("User", foreign_keys=[created_by])
    attachments = relationship(
        "SurveyAttachment", back_populates="survey", cascade="all, delete-orphan"
    )


class SurveyAttachment(Base):
    __tablename__ = "survey_attachments"
    institution_id = Column(
        String(64), nullable=False, default="default", server_default="default", index=True
    )

    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    survey = relationship("Survey", back_populates="attachments")
    course = relationship("Course")

    __table_args__ = (
        Index("ix_survey_attachment_unique", "survey_id", "course_id", unique=True),
    )


class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    institution_id = Column(
        String(64), nullable=False, default="default", server_default="default", index=True
    )

    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    answers = Column(Text, nullable=False)
    submitted_at = Column(DateTime, server_default=func.now())

    survey = relationship("Survey")
    user = relationship("User")
    course = relationship("Course")

    __table_args__ = (
        Index("ix_survey_response_unique", "survey_id", "user_id", unique=True),
    )


class CourseFeedback(Base):
    """Two-way course feedback.

    ``student_course`` rows are the learner's private check-in on the course
    and instructor. ``instructor_student`` rows are coaching notes addressed to
    one enrolled student. Student rows keep the author id for duplicate
    prevention and the student's own view, but instructor summaries aggregate
    them and never expose the author.
    """
    __tablename__ = "course_feedback"
    institution_id = Column(
        String(64), nullable=False, default="default", server_default="default", index=True
    )

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    direction = Column(String(24), nullable=False)  # student_course | instructor_student
    clarity = Column(Integer, nullable=True)
    challenge = Column(Integer, nullable=True)
    engagement = Column(Integer, nullable=True)
    confidence = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    is_anonymous = Column(Boolean, default=True, server_default=text("true"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    course = relationship("Course")
    author = relationship("User", foreign_keys=[author_id])
    subject = relationship("User", foreign_keys=[subject_user_id])

    __table_args__ = (
        Index("ix_course_feedback_course_direction", "course_id", "direction"),
    )


class ExercisePulseSurvey(Base):
    """Three-question learner pulse taken after an exercise.

    One response per learner and exercise. ``course_id`` records the course
    context when the response was collected so course analytics can aggregate
    the right surveys without exposing free text to other learners.
    """
    __tablename__ = "exercise_pulse_surveys"
    institution_id = Column(
        String(64), nullable=False, default="default", server_default="default", index=True
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)
    # 1 = much too easy / very little learning, 5 = much too difficult / extensive.
    difficulty = Column(Integer, nullable=False)
    learning = Column(Integer, nullable=False)
    unclear = Column(Text, nullable=True)
    # Optional learner interest signal used for the trending-topics report.
    topic_interest = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    lab = relationship("Lab")
    course = relationship("Course")

    __table_args__ = (
        Index("ix_pulse_user_lab_unique", "user_id", "lab_id", unique=True),
        Index("ix_pulse_course_lab", "course_id", "lab_id"),
    )


class ExerciseReaction(Base):
    """Lightweight thumbs-up / thumbs-down feedback on an exercise.

    Separate from ``ExercisePulseSurvey`` because this control is available
    while a learner is working, is not gated by survey consent, and feeds a
    simple course report. One reaction is kept per learner and exercise; the
    course context is stored so course reports do not mix cohorts.
    """
    __tablename__ = "exercise_reactions"
    institution_id = Column(
        String(64), nullable=False, default="default", server_default="default", index=True
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    reaction = Column(String(10), nullable=False)  # like or dislike
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    lab = relationship("Lab")
    course = relationship("Course")

    __table_args__ = (
        Index("ix_reaction_user_lab_unique", "user_id", "lab_id", unique=True),
        Index("ix_reaction_course_lab", "course_id", "lab_id"),
    )


class SurveyConsentEvent(Base):
    """Append-only record of survey consent decisions.

    The user row carries the current state; this table preserves the history
    needed to show when and under which statement version consent was given or
    withdrawn. Rows cascade with the account so erasure removes them.
    """

    __tablename__ = "survey_consent_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action = Column(String(16), nullable=False)  # opt_in | opt_out
    policy_version = Column(String(32), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
