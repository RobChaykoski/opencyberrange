"""ORM models for authoring."""

from app.database import Base
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ExerciseTemplate(Base):
    """A reusable, vetted lab template that can be instantiated and reskinned.

    Covers ephemeral (Linux/Network/Web container labs)
    (Windows AD) classes. The structural manifest is locked on a cosmetic
    instantiate; only the cosmetic_schema fields can be overridden.
    """
    __tablename__ = "exercise_templates"

    id = Column(Integer, primary_key=True)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    klass = Column(String(20), nullable=False)        # ephemeral
    archetype = Column(String(50), nullable=False)    # linux | network | web | windows
    description = Column(Text, nullable=True)

    # Structural metadata (locked on cosmetic instantiate). JSON encoded as Text.
    structural_manifest = Column(Text, nullable=False)  # {ip_offsets, exploit_path, tester_spec, topology, ...}
    cosmetic_schema = Column(Text, nullable=False)      # {company, persona, hostname, scenario, ...} with defaults
    env_contract = Column(Text, nullable=False)         # {FLAG, CRED_<role>_USER, CRED_<role>_PASS, *_OFFSET}

    # Provenance
    source_lab_slug = Column(String(150), nullable=True)  # which existing lab this was seeded from
    latest_version = Column(Integer, default=1)
    status = Column(String(20), default="draft", nullable=False)  # draft | published | deprecated

    # Lifecycle
    tags = Column(Text, nullable=True)  # JSON array of strings
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    instances = relationship("TemplateInstance", back_populates="template")

    __table_args__ = (
        Index("ix_template_status_created", "status", "created_at"),
        CheckConstraint("status IN ('draft', 'published', 'deprecated')", name="ck_template_status"),
        CheckConstraint("klass IN ('ephemeral')", name="ck_template_klass"),
        CheckConstraint("archetype IN ('linux', 'network', 'web', 'windows')", name="ck_template_archetype"),
    )


class TemplateInstance(Base):
    """An instance of a template: instantiated by an instructor with cosmetic
    overrides, optionally materialized as a draft Lab row once approved.

    For Phase 0 only fork_type='cosmetic' is produced. The override_values JSON
    holds the reskin (company, scenario, hostname, credentials, flag) and is the
    source for per-instance FLAG/CRED_* env injection at spawn time.
    """
    __tablename__ = "template_instances"

    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey("exercise_templates.id"), nullable=False)
    template_version = Column(Integer, nullable=False)  # which template version was cloned
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)  # nullable for standalone
    instructor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # cosmetic: only cosmetic_schema overrides, structure locked (Phase 0)
    # exposed: unlocked some structure but not the core (Phase 2+)
    # full_fork: changed structural_manifest, requires security scan (Phase 2+)
    fork_type = Column(String(20), nullable=False)

    # Cosmetic overrides (instructor's reskin). JSON encoded as Text.
    override_values = Column(Text, nullable=True)  # {company, scenario, hostname, credentials, flag, ...}

    # Fork provenance (for 3-way merge and patch notifications, Phase 1+)
    base_snapshot = Column(Text, nullable=True)  # structural_manifest + cosmetic_schema at fork time

    # Materialized Lab row (populated on approval; visibility='draft')
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="SET NULL"), nullable=True, unique=True)

    # Lifecycle
    status = Column(String(20), default="draft", nullable=False)  # draft | staged | published | rejected
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    template = relationship("ExerciseTemplate", back_populates="instances")
    course = relationship("Course", foreign_keys=[course_id])
    instructor = relationship("User", foreign_keys=[instructor_id])
    lab = relationship("Lab", foreign_keys=[lab_id], uselist=False)

    __table_args__ = (
        Index("ix_instance_template_instructor", "template_id", "instructor_id"),
        Index("ix_instance_course_status", "course_id", "status"),
        CheckConstraint("fork_type IN ('cosmetic', 'exposed', 'full_fork')", name="ck_instance_fork_type"),
        CheckConstraint("status IN ('draft', 'staged', 'published', 'rejected')", name="ck_instance_status"),
    )


class StudioPendingReview(Base):
    """Admin approval queue: tracks staged instances awaiting human sign-off
    before they are ingested as Labs with visibility='draft'.
    """
    __tablename__ = "studio_pending_review"

    id = Column(Integer, primary_key=True)
    instance_id = Column(Integer, ForeignKey("template_instances.id"), nullable=False, unique=True)
    instructor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)

    # What changed (mirrors the instance) and how rigorous review should be
    fork_type = Column(String(20), nullable=False)  # cosmetic | exposed | full_fork
    tier = Column(String(20), nullable=False)       # parameterize | remix | author

    # Gate stage results (from the publish pipeline)
    lint_status = Column(String(20), nullable=True)           # pass | warn | fail
    security_scan_status = Column(String(20), nullable=True)  # pass | warn | fail | not_required
    tester_status = Column(String(20), nullable=True)         # pass | fail | not_run

    # Gate artifacts (JSON encoded as Text, for display in the review pane)
    lint_report = Column(Text, nullable=True)    # {errors: [], warnings: []}
    tester_report = Column(Text, nullable=True)  # {steps: [], passed: bool}

    # Admin review outcome
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approval_status = Column(String(20), default="pending", nullable=False)  # pending | approved | rejected | changes_requested
    reviewer_notes = Column(Text, nullable=True)

    # Audit
    submitted_at = Column(DateTime, server_default=func.now())

    # Relationships
    instance = relationship("TemplateInstance", foreign_keys=[instance_id])
    submitter = relationship("User", foreign_keys=[instructor_id])
    course = relationship("Course", foreign_keys=[course_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    __table_args__ = (
        Index("ix_pending_approval_status", "approval_status"),
        Index("ix_pending_reviewer", "reviewed_by"),
        Index("ix_pending_submitted", "submitted_at"),
        CheckConstraint("approval_status IN ('pending', 'approved', 'rejected', 'changes_requested')", name="ck_pending_approval"),
        CheckConstraint("fork_type IN ('cosmetic', 'exposed', 'full_fork')", name="ck_pending_fork_type"),
        CheckConstraint("tier IN ('parameterize', 'remix', 'author')", name="ck_pending_tier"),
    )


class ExerciseGenJob(Base):
    """An AI generation job: a syllabus/prompt -> N planned exercises.

    Lives entirely in the DB (PRD 5.7): the background worker advances it, and
    the browser only observes. status: planning -> awaiting_plan ->
    building -> awaiting_review -> done | failed. Tokens are accumulated for the
    audit trail.
    """
    __tablename__ = "exercise_gen_jobs"

    id = Column(Integer, primary_key=True)
    instructor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    input_syllabus = Column(Text, nullable=True)
    params = Column(Text, nullable=True)  # JSON: {track, count, difficulty, techniques, attach}
    model = Column(String(50), default="", nullable=False)
    provider_profile_id = Column(Integer, nullable=True)  # which InstructorApiKey ran this job
    status = Column(String(30), default="planning", nullable=False)
    token_cost = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    # Job-level claim-lease (the planning step is one model call).
    claimed_by = Column(String(64), nullable=True)
    lease_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    items = relationship("ExerciseGenItem", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_genjob_status", "status"),
        Index("ix_genjob_instructor", "instructor_id"),
        CheckConstraint(
            "status IN ('planning', 'awaiting_plan', 'building', 'awaiting_review', 'done', 'failed')",
            name="ck_genjob_status",
        ),
    )


class ExerciseGenItem(Base):
    """One planned exercise within a job. The worker claims it and advances it
    select -> generate -> gate -> ingest, reusing template_engine + the gate.

    Tier is parameterize|remix (catalog templates) for Phase 2; author (free-form
    new infra) is recognized but parked as ``needs_infra`` until Phase 3.
    """
    __tablename__ = "exercise_gen_items"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("exercise_gen_jobs.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=True)
    technique = Column(String(255), nullable=True)
    tier = Column(String(20), default="parameterize", nullable=False)
    template_slug = Column(String(150), nullable=True)   # chosen catalog template
    stage = Column(String(20), default="select", nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    overrides = Column(Text, nullable=True)   # JSON: model-proposed cosmetic overrides
    instance_id = Column(Integer, ForeignKey("template_instances.id", ondelete="SET NULL"), nullable=True)
    pending_review_id = Column(Integer, nullable=True)
    lab_id = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    # Per-item claim-lease for safe parallel build across the 17 uvicorn workers.
    claimed_by = Column(String(64), nullable=True)
    lease_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    job = relationship("ExerciseGenJob", back_populates="items")

    __table_args__ = (
        Index("ix_genitem_job_status", "job_id", "status"),
        CheckConstraint("tier IN ('parameterize', 'remix', 'author')", name="ck_genitem_tier"),
        CheckConstraint(
            "status IN ('pending', 'building', 'ready', 'failed', 'needs_infra', 'skipped')",
            name="ck_genitem_status",
        ),
    )


class ExerciseTestResult(Base):
    """Persisted exercise-test result — one row per lab_slug (latest replaces older)."""
    __tablename__ = "exercise_test_results"

    id = Column(Integer, primary_key=True)
    lab_slug = Column(String(100), unique=True, nullable=False, index=True)
    lab_name = Column(String(200), nullable=False)
    track = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False)          # ok | warning | error | cancelled
    duration_seconds = Column(Float, nullable=True)
    tested_at = Column(DateTime, server_default=func.now())
    tested_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    run_id = Column(String(20), nullable=True)
    sections_json = Column(Text, nullable=True)           # JSON array of section objects

    tested_by = relationship("User", foreign_keys=[tested_by_id])
