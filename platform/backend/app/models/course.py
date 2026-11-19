"""ORM models for course."""

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


class Course(Base):
    """A class/course offering with assigned labs and enrolled students"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    code = Column(String(20), nullable=False)
    semester = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    invite_code = Column(String(20), unique=True, index=True, nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    # When true, a learner sees only the course labs that belong to their
    # cohort's exercise sets. Course-wide labs remain visible when no cohort
    # requirement has been configured, so an unfinished plan never blanks a
    # course by accident.
    cohort_strict = Column(Boolean, default=False, server_default=text("false"), nullable=False)
    wiki_slug = Column(String(50), nullable=True, index=True)
    wiki_theme_color = Column(String(30), default="blue")
    # Per-cohort retention clock. When retention_until passes, the course is
    # listed as retention-due. Actual record deletion is an operator runbook
    # step; previews and completion evidence are stored in retention_runs.
    retention_until = Column(DateTime, nullable=True)
    retention_note = Column(String(500), nullable=True)
    retention_set_by_id = Column(Integer, nullable=True)
    retention_set_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    instructor = relationship("User", back_populates="instructed_courses")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")
    lab_assignments = relationship("CourseLabAssignment", back_populates="course", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan", order_by="Assignment.sort_order")


class RetentionRun(Base):
    """Append-only evidence of a retention preview or operator completion."""

    __tablename__ = "retention_runs"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action = Column(String(20), nullable=False)  # preview | completed
    counts = Column(Text, nullable=True)
    note = Column(String(500), nullable=True)
    reference = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ReviewRequest(Base):
    """Learner request for a human decision on a deterministic result."""

    __tablename__ = "review_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id = Column(
        Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True
    )
    lab_id = Column(
        Integer, ForeignKey("labs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source = Column(String(30), nullable=False, default="flag")
    reason = Column(String(1000), nullable=False)
    status = Column(String(20), nullable=False, default="pending", server_default="pending")
    rule_version = Column(String(50), nullable=False, default="deterministic-v1")
    primary_factors = Column(Text, nullable=True)
    decision_note = Column(String(1000), nullable=True)
    decided_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    requested_at = Column(DateTime, server_default=func.now())
    decided_at = Column(DateTime, nullable=True)


class CourseCohort(Base):
    """A learner group inside one course for targeted requirements."""

    __tablename__ = "course_cohorts"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(120), nullable=False)
    description = Column(String(500), nullable=True)
    # Exactly one cohort per course may be the automatic enrollment target.
    # The API clears the flag from siblings when a new default is selected.
    is_default = Column(Boolean, default=False, server_default=text("false"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("course_id", "name", name="uq_course_cohort_name"),)


class CourseCohortMember(Base):
    __tablename__ = "course_cohort_members"

    id = Column(Integer, primary_key=True, index=True)
    cohort_id = Column(
        Integer,
        ForeignKey("course_cohorts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    __table_args__ = (
        UniqueConstraint("cohort_id", "user_id", name="uq_course_cohort_member"),
    )


class CourseStaff(Base):
    """A mentor, teaching assistant, or co-instructor assigned to a course."""

    __tablename__ = "course_staff"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    staff_role = Column(String(24), nullable=False)  # co_instructor | mentor | teaching_assistant
    created_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "course_id", "user_id", "staff_role", name="uq_course_staff_role"
        ),
    )


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(120), nullable=False)
    description = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("course_id", "name", name="uq_exercise_set_name"),
    )


class ExerciseSetItem(Base):
    __tablename__ = "exercise_set_items"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(
        Integer,
        ForeignKey("exercise_sets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lab_id = Column(
        Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sort_order = Column(Integer, default=0, nullable=False)
    required = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("set_id", "lab_id", name="uq_exercise_set_item"),
    )


class CourseRequirement(Base):
    __tablename__ = "course_requirements"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cohort_id = Column(
        Integer,
        ForeignKey("course_cohorts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    set_id = Column(
        Integer,
        ForeignKey("exercise_sets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_type = Column(String(20), nullable=False, default="complete_all")
    threshold = Column(Integer, nullable=True)
    due_at = Column(DateTime, nullable=True)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class CourseEnrollment(Base):
    """Links students to courses"""
    __tablename__ = "course_enrollments"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    enrolled_at = Column(DateTime, server_default=func.now())
    # Per-student scope token for tracks that scope AD objects per student
    # (e.g. ADPT: svc_kerb_<token>). Auto-assigned on enrollment, NULL for
    # courses whose tracks don't need scoping.
    scope_token = Column(String(4), nullable=True)
    # FERPA-safe classroom-scoreboard identity (Phase 6b): a stable per-course
    # integer assigned in a deterministic course-seeded SHUFFLE (not roster
    # order), shown privately to the student and used on the projected
    # scoreboard so names are never displayed. Assigned lazily; NULL until then.
    seat_number = Column(Integer, nullable=True)
    # Minor-account enrollment: the institution records the parental/guardian
    # consent reference. The platform stores the reference and the staff member,
    # not identity documents.
    consent_reference = Column(String(200), nullable=True)
    consent_recorded_at = Column(DateTime, nullable=True)
    consent_recorded_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    course = relationship("Course", back_populates="enrollments")
    user = relationship(
        "User", back_populates="course_enrollments", foreign_keys=[user_id]
    )

    __table_args__ = (
        Index('ix_enrollment_course_user', 'course_id', 'user_id', unique=True),
    )


class CourseLabAssignment(Base):
    """Labs assigned to a course"""
    __tablename__ = "course_lab_assignments"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True)
    sort_order = Column(Integer, default=0)
    display_name = Column(String(255), nullable=True)
    assigned_at = Column(DateTime, server_default=func.now())

    # Relationships
    course = relationship("Course", back_populates="lab_assignments")
    lab = relationship("Lab", back_populates="course_assignments")

    __table_args__ = (
        Index('ix_course_lab_assignment', 'course_id', 'lab_id', unique=True),
    )


class CourseCompletionReset(Base):
    """Instructor-initiated reset of a lab completion within a course.
    Does NOT delete LabCompletion — just marks it stale for this course."""
    __tablename__ = "course_completion_resets"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False)
    reset_at = Column(DateTime, server_default=func.now())
    reset_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        Index('ix_course_reset_lookup', 'course_id', 'user_id', 'lab_id'),
    )


class Assignment(Base):
    """Named grouping of labs within a course, with optional due date"""
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)
    locked = Column(Boolean, default=False, server_default="false", nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    course = relationship("Course", back_populates="assignments")
    assignment_labs = relationship("AssignmentLab", back_populates="assignment", cascade="all, delete-orphan", order_by="AssignmentLab.sort_order")

    __table_args__ = (
        Index('ix_assignments_course_id', 'course_id'),
    )


class AssignmentLab(Base):
    """Links labs to assignments (labs must also be assigned to the course)"""
    __tablename__ = "assignment_labs"

    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False)
    sort_order = Column(Integer, default=0)

    assignment = relationship("Assignment", back_populates="assignment_labs")
    lab = relationship("Lab")

    __table_args__ = (
        Index('ix_assignment_lab', 'assignment_id', 'lab_id', unique=True),
        Index('ix_assignment_labs_lab_id', 'lab_id'),
    )
