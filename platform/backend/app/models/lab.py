"""ORM models for lab."""

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


class Track(Base):
    """Learning tracks (Windows, Linux, Web, Network)"""
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    description = Column(Text)
    icon = Column(String(50))  # Icon component name
    color = Column(String(20))  # Hex color
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    sequential = Column(Boolean, default=True, server_default="true", nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    levels = relationship("Level", back_populates="track", order_by="Level.level_number")


class Level(Base):
    """Levels within tracks"""
    __tablename__ = "levels"
    
    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    level_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    
    # Relationships
    track = relationship("Track", back_populates="levels")
    labs = relationship("Lab", back_populates="level", order_by="Lab.sort_order")
    
    __table_args__ = (
        Index('ix_level_track_number', 'track_id', 'level_number', unique=True),
    )


class Lab(Base):
    __tablename__ = "labs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    description = Column(Text)
    scenario = Column(Text, nullable=True)  # Full narrative scenario for immersive experience
    scenario_brief = Column(Text, nullable=True)  # Short version for lab list view (optional)
    difficulty = Column(String(20), default="beginner")
    category = Column(String(50), default="general")
    objectives = Column(Text)  # JSON array of learning outcomes stored as text
    compose_file = Column(Text, nullable=False)
    duration_minutes = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Curriculum fields
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    flag_hash = Column(String(255), nullable=True)  # SHA256 of correct flag
    hints = Column(Text, nullable=True)  # JSON array of hints
    tools = Column(Text, nullable=True)  # JSON array of tools
    hostnames = Column(Text, nullable=True)  # JSON array of hostname mappings: [{"ip_offset": "17", "hostname": "vulnerable.lab", "description": "Main web app"}]
    # Reveal per-node target IPs in the Exercise Network panel (drills / guided tours)
    show_target_ips = Column(Boolean, default=False)
    # JSON array of topology nodes [{"id","label","ip_offset",...}] used to compute target IPs
    topology_nodes = Column(Text, nullable=True)
    # Lab depends on a VM the host runs under KVM, so it needs /dev/kvm
    requires_kvm = Column(Boolean, default=False)
    # Bonus labs are part of the level but do not block the level certificate.
    # This keeps existing awards valid when a new optional exercise is added.
    counts_toward_certificate = Column(
        Boolean, default=True, server_default=text("true"), nullable=False
    )
    # Course-exclusive: only visible to students enrolled in a course that assigns this lab
    is_course_exclusive = Column(Boolean, default=False)  # Deprecated — use visibility
    # Course-available: lab is designated for course assignments
    is_course_available = Column(Boolean, default=False)  # Deprecated — use visibility
    # Lab visibility lifecycle: draft | course | pending_public | public
    visibility = Column(String(20), default="public", nullable=False)
    # Wiki page path for workbook deep-link (e.g. "CH01_Enumeration/01_Basic_Port_Scan/")
    workbook = Column(String(255), nullable=True)
    # Display chapter identifier from curriculum-manifest.yaml (e.g. "WIN01").
    chapter_id = Column(String(32), nullable=True)

    @property
    def chapter_name(self):
        from app.services.curriculum_manifest import chapter_name
        return chapter_name(self.chapter_id)

    # Selective framework alignment: exactly one primary competency, one or two
    # framework references, and one measurable outcome per lab.
    primary_competency = Column(String(64), nullable=True)
    framework_refs = Column(Text, nullable=True)  # JSON array of framework IDs
    measurable_outcome = Column(Text, nullable=True)

    @property
    def framework_refs_list(self):
        import json
        try:
            value = json.loads(self.framework_refs or "[]")
            return value if isinstance(value, list) else []
        except Exception:
            return []
    # Curriculum week number for auto-assignment grouping (e.g. week: 3 → "Week 3" assignment)
    week = Column(Integer, nullable=True)
    # Who created this lab (NULL for system-discovered labs)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Static validation results (populated by lab scanner / validate-lab.py)
    validation_status = Column(String(20), nullable=True)  # ok | warning | error
    validation_errors = Column(Text, nullable=True)  # JSON array of {name, passed, message, severity}
    validated_at = Column(DateTime, nullable=True)
    # Content version from lab.yaml. Analytics groups by this so feedback and
    # completion from an old lab revision do not contaminate a revised lab.
    content_version = Column(String(32), nullable=True)
    # Canonical lab metadata from lab.yaml. JSON arrays keep the catalog and
    # competency model driven by the authored manifest instead of heuristics.
    prerequisites = Column(Text, nullable=True)  # JSON array of lab slugs
    mapped_skills = Column(Text, nullable=True)  # JSON array of competency keys
    assessment_criteria = Column(Text, nullable=True)  # JSON array of criteria
    # ICS attack-coverage tags from lab.yaml ics_techniques: JSON array of
    # {tactic, technique_id, technique_name, note}. Powers the coverage matrix
    # generator and per-lab technique display.
    ics_techniques = Column(Text, nullable=True)
    # MITRE ATT&CK mappings from lab.yaml mitre_attack: JSON array of
    # {tactic, technique, technique_name, detection}. Applies to every track,
    # not only ICS.
    mitre_attack = Column(Text, nullable=True)

    # Relationships
    level = relationship("Level", back_populates="labs")
    creator = relationship("User", foreign_keys=[created_by])
    sessions = relationship("LabSession", back_populates="lab")
    completions = relationship("LabCompletion", back_populates="lab")
    flag_attempts = relationship("FlagAttempt", back_populates="lab")
    course_assignments = relationship("CourseLabAssignment", back_populates="lab")


class LevelQuiz(Base):
    """Optional 20-question quiz attached to a level."""
    __tablename__ = "level_quizzes"

    id = Column(Integer, primary_key=True)
    level_id = Column(Integer, ForeignKey("levels.id", ondelete="CASCADE"), nullable=False, unique=True)
    title = Column(String(120), nullable=False, default="Level Quiz")
    passing_score = Column(Integer, nullable=False, default=70)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    level = relationship("Level")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.sort_order")


class QuizQuestion(Base):
    """A single multiple-choice question for a level quiz."""
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("level_quizzes.id", ondelete="CASCADE"), nullable=False)
    sort_order = Column(Integer, default=0)
    question = Column(Text, nullable=False)
    # JSON array of option strings
    options = Column(Text, nullable=False)
    # Index of the correct option
    correct_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)

    quiz = relationship("LevelQuiz", back_populates="questions")


class QuizAttempt(Base):
    """A student's attempt at a level quiz."""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("level_quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)  # percentage 0-100
    total = Column(Integer, nullable=False)
    correct = Column(Integer, nullable=False)
    passed = Column(Boolean, default=False)
    answers = Column(Text, nullable=True)  # JSON array of selected indices
    taken_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('ix_quiz_attempt_user_quiz', 'user_id', 'quiz_id'),
    )


class LabSession(Base):
    __tablename__ = "lab_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False, index=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    network_id = Column(String(100))
    network_subnet = Column(String(20))
    status = Column(String(20), default="starting")  # starting, running, stopped, expired, error
    is_diagnostic = Column(Boolean, default=False)
    rangebox_enabled = Column(Boolean, default=False)
    impersonated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # admin who launched this session
    # Per-student flag support: when a lab seeds a unique flag into this
    # session's containers, the SHA256 of that flag is stored here and checked
    # before the shared labs.flag_hash. Chosen over a separate LabFlag table
    # because a session-scoped hash is the lighter change and matches the
    # existing flag_hash comparison path.
    seeded_flag_hash = Column(String(255), nullable=True)
    started_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    stopped_at = Column(DateTime, nullable=True)
    # Accommodation pause: while paused_at is set the expiry clock is frozen and
    # the scheduler must not reap the session. Resume credits the paused time.
    paused_at = Column(DateTime, nullable=True)
    paused_seconds = Column(Integer, nullable=False, default=0, server_default="0")
    pause_reason = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions", foreign_keys=[user_id])
    lab = relationship("Lab", back_populates="sessions")

    __table_args__ = (
        Index('ix_labsession_status', 'status'),
        Index('ix_labsession_user_status', 'user_id', 'status'),
        Index('ix_lab_sessions_started_at', 'started_at'),
    )


class LabCompletion(Base):
    """Track user lab completions"""
    __tablename__ = "lab_completions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False, index=True)
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    completed_at = Column(DateTime, server_default=func.now())
    flag_submitted = Column(String(100))
    attempts = Column(Integer, default=1)
    hints_used = Column(Integer, default=0)
    time_spent_minutes = Column(Integer, nullable=True)
    started_at = Column(DateTime, nullable=True)  # Track when user started working on lab for time-based hints
    # Versioned competency snapshot captured when the completion was created.
    competency_model_version = Column(String(32), nullable=True)
    competency_mapping = Column(Text, nullable=True)  # JSON: model/mapping version + axis weights
    lab_difficulty_snapshot = Column(String(20), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="completions")
    lab = relationship("Lab", back_populates="completions")
    
    __table_args__ = (
        Index('ix_completion_user_lab', 'user_id', 'lab_id', unique=True),
        Index('ix_lab_completions_lab_completed', 'lab_id', 'completed_at'),
    )


class LearnerSnapshot(Base):
    """Immutable report snapshot with the formula and factor weights used.

    A persisted report is rendered from this row, not rebuilt from live
    evidence. That way a later scoring change cannot rewrite an old report.
    Payload and weights are canonical JSON in Text columns, matching the
    existing ``competency_mapping`` convention.
    """

    __tablename__ = "learner_snapshots"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    kind = Column(String(32), nullable=False)  # career_dossier | portfolio
    schema_version = Column(String(32), nullable=False)
    formula_version = Column(String(32), nullable=True)
    weights = Column(Text, nullable=False)
    payload = Column(Text, nullable=False)
    content_sha256 = Column(String(64), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User")
    __table_args__ = (
        Index("ix_learner_snapshots_user_kind", "user_id", "kind"),
        Index(
            "ix_learner_snapshots_unique",
            "user_id",
            "kind",
            "content_sha256",
            unique=True,
        ),
    )


class FlagAttempt(Base):
    """Log all flag submission attempts"""
    __tablename__ = "flag_attempts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False, index=True)
    flag_submitted = Column(String(100))
    is_correct = Column(Boolean, default=False)
    attempted_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="flag_attempts")
    lab = relationship("Lab", back_populates="flag_attempts")
    
    __table_args__ = (
        Index('ix_attempt_user_lab_time', 'user_id', 'lab_id', 'attempted_at'),
    )


class ExerciseQuizAttempt(Base):
    """One attempt at an optional exercise knowledge check.

    The question bank lives in ``quiz.yaml`` beside the lab, so it can grow
    without a schema change. The attempt stores the selected question keys and
    answers so results remain reproducible even if the bank is edited later.
    """
    __tablename__ = "exercise_quiz_attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)
    certification = Column(String(120), nullable=True)
    question_keys = Column(Text, nullable=False)  # JSON array of bank question ids
    answers = Column(Text, nullable=False, default="{}")  # JSON object key -> option index
    score = Column(Integer, default=0)
    correct = Column(Integer, default=0)
    total = Column(Integer, default=0)
    passed = Column(Boolean, default=False, server_default=text("false"))
    taken_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User")
    lab = relationship("Lab")
    course = relationship("Course")

    __table_args__ = (
        Index("ix_exercise_quiz_user_lab", "user_id", "lab_id"),
        Index("ix_exercise_quiz_course", "course_id"),
    )


class ExerciseQuizFeedback(Base):
    """Optional post-quiz feedback that feeds course experience metrics.

    One response per learner and exercise, updated in place. The four ratings
    are the course-level satisfaction, relevance, usefulness, and ease-of-use
    signals; the free-text comment is optional.
    """
    __tablename__ = "exercise_quiz_feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)
    satisfaction = Column(Integer, nullable=True)
    relevance = Column(Integer, nullable=True)
    usefulness = Column(Integer, nullable=True)
    ease_of_use = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    lab = relationship("Lab")
    course = relationship("Course")

    __table_args__ = (
        Index("ix_exercise_quiz_feedback_user_lab", "user_id", "lab_id", unique=True),
    )


class WireGuardConfig(Base):
    __tablename__ = "wireguard_configs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    private_key = Column(String(256), nullable=False)  # Fernet-encrypted keys can be ~128 chars
    public_key = Column(String(100), nullable=False)
    client_ip = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="wireguard_config")
