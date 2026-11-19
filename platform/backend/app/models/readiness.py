"""Instructor support workflow records for the readiness dashboard."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, func

from app.database import Base


class ReadinessStudentNote(Base):
    """Context, flag state, or support action for one learner in one course.

    The table is intentionally append-only in practice: a new note records a new
    decision. ``state`` is used only for flag acknowledgements.
    """

    __tablename__ = "readiness_student_notes"

    id = Column(Integer, primary_key=True)
    institution_id = Column(String(64), nullable=True, server_default="default")
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    learner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(24), nullable=False, index=True)
    key = Column(String(64), nullable=False)
    state = Column(String(24), nullable=True)
    note = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)
    start_at = Column(DateTime, nullable=True)
    end_at = Column(DateTime, nullable=True)
    follow_up_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_readiness_notes_course_learner", "course_id", "learner_id"),
    )


class ReadinessLabReview(Base):
    """One lab-health review for a course."""

    __tablename__ = "readiness_lab_reviews"

    id = Column(Integer, primary_key=True)
    institution_id = Column(String(64), nullable=True, server_default="default")
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(24), nullable=False)
    finding = Column(Text, nullable=True)
    action = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_readiness_lab_reviews_course_lab", "course_id", "lab_id"),
    )
