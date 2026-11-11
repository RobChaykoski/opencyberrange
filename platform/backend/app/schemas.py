"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator, model_validator
from typing import Optional, List, ClassVar
from datetime import datetime
import re
import unicodedata

from app.services.input_safety import normalize_text


# Common bases are matched after the password is normalised (case-folded,
# reduced to letters/digits, and stripped of trailing counters/years). That
# catches the real-world habit of taking a dictionary word and appending a
# digit or symbol: Password1, P@ssw0rd!, Summer2026!.
_COMMON_PASSWORD_BASES = frozenset({
    "password", "passw0rd", "passwd", "pass", "qwerty", "qwertyuiop",
    "azerty", "abc123", "123456", "1234567", "12345678", "123456789",
    "1234567890", "111111", "000000", "letmein", "welcome", "admin",
    "administrator", "root", "toor", "login", "iloveyou", "monkey",
    "dragon", "master", "sunshine", "princess", "football", "baseball",
    "shadow", "superman", "batman", "trustno1", "starwars", "whatever",
    "freedom", "hello", "secret", "changeme", "changeit", "default",
    "guest", "user", "test", "testing", "student", "teacher", "instructor",
    "school", "college", "university", "cyber", "security", "range",
    "rangebox", "opencyberrange", "ocr", "kali", "ubuntu", "remnux",
    "linux", "windows", "summer", "winter", "spring", "autumn", "fall",
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december", "monday",
    "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "northwind", "swocts", "academy", "course", "lab", "flag",
})

# Fold common substitutions back to the base word. Symbols are folded first,
# then trailing counters/years are removed, then digit substitutions. That order
# turns P@ssw0rd1! into "password" without turning Password1 into
# "passwordl".
_SYMBOL_TRANSLATION = str.maketrans({
    "@": "a", "$": "s", "+": "t",
})
_DIGIT_TRANSLATION = str.maketrans({
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "8": "b",
})

_SEQUENCES = (
    "0123456789",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
)


def _password_normalise(value: str) -> str:
    """Case-fold and reduce a password to letters/digits for comparison."""
    return "".join(
        ch for ch in unicodedata.normalize("NFKC", value).casefold()
        if ch.isalnum()
    )


def _password_base(value: str) -> str:
    """Return the dictionary-like base of a password, ignoring suffixes."""
    folded = unicodedata.normalize("NFKC", value).casefold()
    folded = folded.translate(_SYMBOL_TRANSLATION)
    normalised = "".join(ch for ch in folded if ch.isalnum())
    without_counter = normalised.rstrip("0123456789")
    translated = (without_counter or normalised).translate(_DIGIT_TRANSLATION)
    return translated


def _has_sequential_run(value: str, run_length: int = 4) -> bool:
    """True when value contains an obvious ascending/descending/keyboard run."""
    if len(value) < run_length:
        return False
    for start in range(len(value) - run_length + 1):
        chunk = value[start:start + run_length]
        if not chunk.isalnum():
            continue
        deltas = [
            ord(chunk[i + 1]) - ord(chunk[i])
            for i in range(len(chunk) - 1)
        ]
        if all(delta == 1 for delta in deltas) or all(delta == -1 for delta in deltas):
            return True
    for sequence in _SEQUENCES:
        for start in range(len(sequence) - run_length + 1):
            if sequence[start:start + run_length] in value:
                return True
    return False


def _is_repeated_pattern(value: str) -> bool:
    if len(value) >= 4 and len(set(value)) == 1:
        return True
    return re.fullmatch(r"(.+?)\1+", value) is not None


def _password_context_tokens(
    username: Optional[str] = None,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> set[str]:
    tokens = set()
    for value in (username, first_name, last_name):
        if value:
            tokens.add(unicodedata.normalize("NFKC", str(value)).casefold())
    if email:
        local = str(email).split("@", 1)[0].casefold()
        tokens.add(local)
        tokens.update(part for part in re.split(r"[^a-z0-9]+", local) if part)
    # One- and two-character names would reject far too much ordinary text.
    return {token for token in tokens if len(token) >= 3}


def _contains_context_token(value: str, token: str) -> bool:
    """Match a username/name only as a word or with a numeric/symbol suffix."""
    escaped = re.escape(token)
    return bool(
        re.fullmatch(rf"{escaped}[0-9\W_]*", value)
        or re.fullmatch(rf"[0-9\W_]*{escaped}", value)
        or re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", value)
    )


def _password_policy_error(
    v: str,
    *,
    username: Optional[str] = None,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Optional[str]:
    """Return the first password-policy error, or None when the password is ok.

    Uses Unicode-aware character classes so kanji, full-width letters, and
    other scripts are not silently treated as symbols. The policy is about
    categories, not the Latin alphabet: an uppercase letter, lowercase letter,
    and digit may come from any script.

    Complexity alone is not enough: this also rejects common bases with a
    number/symbol bolted on, account-specific words, repeated patterns, and
    simple sequences.
    """
    if len(v) < 8:
        return "Password must be at least 8 characters"
    if len(v) > 128:
        return "Password must be at most 128 characters"
    if any(unicodedata.category(ch) == "Cc" for ch in v):
        return "Password must not contain control characters"
    if not any(ch.isupper() for ch in v):
        return "Password must contain at least one uppercase letter"
    if not any(ch.islower() for ch in v):
        return "Password must contain at least one lowercase letter"
    if not any(ch.isdigit() for ch in v):
        return "Password must contain at least one number"

    normalised = _password_normalise(v)
    base = _password_base(v)
    if base in _COMMON_PASSWORD_BASES:
        return (
            "Password is too common. Choose a longer phrase that is not a "
            "common word, name, or simple pattern."
        )

    lower_value = unicodedata.normalize("NFKC", v).casefold()
    for token in _password_context_tokens(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
    ):
        if _contains_context_token(lower_value, token):
            return "Password must not contain your username, email, or name."

    if _is_repeated_pattern(normalised.rstrip("0123456789")):
        return "Password must not repeat the same character or pattern."
    if _has_sequential_run(normalised):
        return (
            "Password must not contain a simple sequence such as 1234, "
            "abcd, or qwerty."
        )
    return None


def _validate_password(
    v: str,
    *,
    username: Optional[str] = None,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> str:
    """Shared password check used by all schemas that accept passwords."""
    error = _password_policy_error(
        v,
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    if error:
        raise ValueError(error)
    return v


class SafeTextModel(BaseModel):
    """Base model that normalises declared human-text fields.

    Subclasses list fields in ``__safe_text_fields__`` with ``"short"`` for
    single-line values and ``"multiline"`` for descriptions and comments.
    Passwords, slugs, flags, code/YAML, and other machine values are not listed
    and are therefore never normalised here.
    """

    __safe_text_fields__: ClassVar[dict[str, str]] = {}

    @model_validator(mode="before")
    @classmethod
    def _normalize_safe_text_fields(cls, data):
        fields = cls.__safe_text_fields__
        if not fields or not isinstance(data, dict):
            return data
        cleaned = dict(data)
        for name, mode in fields.items():
            if name not in cleaned:
                continue
            value = cleaned[name]
            if value is None or not isinstance(value, str):
                continue
            cleaned[name] = normalize_text(
                value,
                field=name.replace("_", " "),
                allow_newlines=(mode == "multiline"),
            )
        return cleaned


# ==================== User Schemas ====================

class UserBase(BaseModel):
    username: str
    email: EmailStr
    student_id: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    student_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None
    is_active: Optional[bool] = True
    is_approved: Optional[bool] = False
    is_admin: Optional[bool] = False
    role: Optional[str] = "student"
    must_change_password: Optional[bool] = False
    equipped_title: Optional[str] = None

    class Config:
        from_attributes = True


class UserAdminResponse(BaseModel):
    id: int
    username: str
    email: str
    student_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None
    is_active: Optional[bool] = True
    is_approved: Optional[bool] = False
    is_admin: Optional[bool] = False
    role: Optional[str] = "student"
    is_locked: Optional[bool] = False
    failed_attempts: Optional[int] = 0
    locked_at: Optional[datetime] = None
    vpn_registered: Optional[bool] = False
    must_change_password: Optional[bool] = False
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    equipped_title: Optional[str] = None

    class Config:
        from_attributes = True


class LabCompletionDetail(BaseModel):
    """Lab completion information for user detail view"""
    lab_id: int
    lab_name: str
    lab_slug: str
    track_name: Optional[str] = None
    level_number: Optional[int] = None
    chapter_id: Optional[str] = None
    chapter_name: Optional[str] = None
    completed_at: datetime
    attempts: int
    hints_used: int
    time_spent_minutes: Optional[int] = None
    
    class Config:
        from_attributes = True


class UserDetailResponse(BaseModel):
    """Detailed user information with completions and statistics"""
    id: int
    username: str
    email: str
    student_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_approved: Optional[bool] = False
    is_admin: Optional[bool] = False
    role: Optional[str] = "student"
    is_locked: Optional[bool] = False
    failed_attempts: Optional[int] = 0
    locked_at: Optional[datetime] = None
    vpn_registered: Optional[bool] = False
    must_change_password: Optional[bool] = False
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    equipped_title: Optional[str] = None

    # Statistics
    total_labs_completed: int = 0
    total_flag_attempts: int = 0
    total_hints_used: int = 0
    average_time_per_lab: Optional[float] = None
    
    # Related data
    completions: List[LabCompletionDetail] = []
    active_sessions: List["LabSessionResponse"] = []
    
    class Config:
        from_attributes = True


class FlagSubmitRequest(BaseModel):
    """A student's flag submission.

    Flags are short training tokens. The explicit type and length cap stop
    malformed or oversized values from being hashed, logged, or stored.
    """

    flag: str = Field(..., min_length=1, max_length=100)


class CreateUserRequest(SafeTextModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    student_id: Optional[str] = None
    first_name: Optional[str] = Field(None, max_length=80)
    last_name: Optional[str] = Field(None, max_length=80)
    password: str = Field(..., min_length=8, max_length=128)
    is_approved: bool = False
    is_admin: bool = False
    role: Optional[str] = "student"

    __safe_text_fields__ = {
        "first_name": "short",
        "last_name": "short",
    }

    @field_validator('password')
    @classmethod
    def password_strong(cls, v: str, info: ValidationInfo) -> str:
        data = info.data
        return _validate_password(
            v,
            username=data.get('username'),
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
        )

    @field_validator('role')
    @classmethod
    def role_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ('student', 'instructor', 'admin'):
            raise ValueError('Role must be student, instructor, or admin')
        return v


class UpdateUserRequest(SafeTextModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    first_name: Optional[str] = Field(None, max_length=80)
    last_name: Optional[str] = Field(None, max_length=80)
    organization: Optional[str] = Field(None, max_length=120)
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None
    is_admin: Optional[bool] = None
    role: Optional[str] = None
    must_change_password: Optional[bool] = None

    __safe_text_fields__ = {
        "first_name": "short",
        "last_name": "short",
        "organization": "short",
    }

    @field_validator('role')
    @classmethod
    def role_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ('student', 'instructor', 'admin'):
            raise ValueError('Role must be student, instructor, or admin')
        return v

    @field_validator('username')
    @classmethod
    def username_valid(cls, v: Optional[str]) -> Optional[str]:
        """Username must start with letter and contain only alphanumeric, underscore, hyphen"""
        if v is None:
            return None
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError('Username must start with a letter and contain only letters, numbers, underscores, and hyphens')
        return v
    
    @field_validator('password')
    @classmethod
    def password_strong(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return None
        data = info.data
        return _validate_password(
            v,
            username=data.get('username'),
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
        )


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=128)
    # Re-authentication: an admin token alone must not be enough to take over
    # another account.
    admin_password: str = Field(..., min_length=1, max_length=128)
    # Force the target to choose a new password at the next sign-in.
    must_change_password: bool = True

    @field_validator('new_password')
    @classmethod
    def password_strong(cls, v: str) -> str:
        return _validate_password(v)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @field_validator('new_password')
    @classmethod
    def password_strong(cls, v: str) -> str:
        return _validate_password(v)


# ==================== Lab Schemas ====================

class LabResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    difficulty: str
    category: str
    duration_minutes: int
    is_active: Optional[bool] = True
    level_id: Optional[int] = None
    sort_order: int
    chapter_id: Optional[str] = None
    chapter_name: Optional[str] = None
    primary_competency: Optional[str] = None
    framework_refs: List[str] = Field(default_factory=list, validation_alias="framework_refs_list")
    measurable_outcome: Optional[str] = None
    
    class Config:
        from_attributes = True


class UpdateLabRequest(SafeTextModel):
    name: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    is_course_exclusive: Optional[bool] = None  # Deprecated — use visibility
    is_course_available: Optional[bool] = None  # Deprecated — use visibility
    visibility: Optional[str] = None  # draft | course | pending_public | public
    level_id: Optional[int] = None  # Send explicit null to clear (uncategorize); omit key to leave unchanged
    prerequisites: Optional[str] = None
    mapped_skills: Optional[str] = None
    assessment_criteria: Optional[str] = None
    mitre_attack: Optional[str] = None

    __safe_text_fields__ = {
        "name": "short",
        "description": "multiline",
        "difficulty": "short",
        "category": "short",
        "prerequisites": "multiline",
        "mapped_skills": "multiline",
        "assessment_criteria": "multiline",
        "mitre_attack": "multiline",
    }

    @field_validator('visibility')
    @classmethod
    def visibility_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ('draft', 'course', 'pending_public', 'public'):
            raise ValueError('Visibility must be draft, course, pending_public, or public')
        return v


# ==================== Lab Session Schemas ====================

class TargetInfo(BaseModel):
    name: str
    ip: str
    ports: List[int] = []


class LabSessionResponse(BaseModel):
    id: int
    lab_id: int
    lab_name: str
    lab_slug: str
    network_subnet: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    targets: List[TargetInfo] = []
    
    class Config:
        from_attributes = True


# ==================== VPN Schemas ====================

class VPNStatusResponse(BaseModel):
    has_config: bool
    vpn_registered: Optional[bool] = False
    client_ip: Optional[str] = None


# ==================== Auth Schemas ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# NOTE: the registration request model is NOT here. It lives in
# app/routers/auth.py, because that is the one the /api/auth/register
# endpoint binds, and it carries the invite_code field that this module
# never had. A duplicate RegisterRequest used to sit here with no
# invite_code, which made it look like the backend could not accept an
# invite code at all. Removed rather than kept in sync.


# ==================== Course Schemas ====================

class CourseCreate(SafeTextModel):
    name: str = Field(..., min_length=3, max_length=150)
    code: str = Field(..., min_length=2, max_length=20)
    semester: str = Field(..., min_length=3, max_length=20)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    instructor_id: Optional[int] = None
    wiki_theme_color: Optional[str] = None

    __safe_text_fields__ = {
        "name": "short",
        "code": "short",
        "semester": "short",
        "description": "multiline",
    }


class CourseUpdate(SafeTextModel):
    name: Optional[str] = Field(None, min_length=3, max_length=150)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    semester: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None
    instructor_id: Optional[int] = None
    wiki_theme_color: Optional[str] = None

    __safe_text_fields__ = {
        "name": "short",
        "code": "short",
        "semester": "short",
        "description": "multiline",
    }


class CourseResponse(BaseModel):
    id: int
    name: str
    code: str
    semester: str
    description: Optional[str] = None
    invite_code: str
    instructor_id: int
    instructor_name: Optional[str] = None
    start_date: datetime
    end_date: datetime
    is_active: bool
    is_archived: bool = False
    wiki_slug: Optional[str] = None
    wiki_theme_color: Optional[str] = "blue"
    created_at: Optional[datetime] = None
    student_count: int = 0
    lab_count: int = 0

    class Config:
        from_attributes = True


class CourseJoinRequest(BaseModel):
    # Allow surrounding whitespace and full-width input to be normalised before
    # the 6-20 character check, so a pasted code is not rejected for formatting.
    invite_code: str = Field(..., min_length=1, max_length=64)

    @field_validator("invite_code")
    @classmethod
    def normalize_invite_code(cls, v: str) -> str:
        value = unicodedata.normalize("NFKC", v)
        value = re.sub(r"\s+", "", value)
        if not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", value):
            raise ValueError(
                "Invite code must be 6-20 letters, numbers, hyphens, or underscores"
            )
        return value


class ExerciseQuizFeedbackInput(SafeTextModel):
    """Optional post-quiz ratings that feed course experience metrics."""

    satisfaction: Optional[int] = Field(None, ge=1, le=5)
    relevance: Optional[int] = Field(None, ge=1, le=5)
    usefulness: Optional[int] = Field(None, ge=1, le=5)
    ease_of_use: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)

    __safe_text_fields__ = {"comment": "multiline"}


class ExerciseQuizSubmitRequest(BaseModel):
    answers: dict = Field(default_factory=dict)
    feedback: Optional[ExerciseQuizFeedbackInput] = None


class CourseFeedbackRequest(SafeTextModel):
    """Student course check-in or instructor coaching note.

    Ratings are 1-5. Students send no ``subject_user_id``; instructors must
    send the enrolled student they are coaching.
    """
    clarity: Optional[int] = Field(None, ge=1, le=5)
    challenge: Optional[int] = Field(None, ge=1, le=5)
    engagement: Optional[int] = Field(None, ge=1, le=5)
    confidence: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)
    subject_user_id: Optional[int] = None

    __safe_text_fields__ = {"comment": "multiline"}


class CourseLabAssignRequest(BaseModel):
    lab_ids: List[int]


class CourseLabBulkRemoveRequest(BaseModel):
    lab_ids: List[int]


class CourseLabReorderRequest(BaseModel):
    lab_order: List[dict]


class AssignmentReorderRequest(BaseModel):
    assignment_order: List[dict]


class CourseLabUpdateRequest(SafeTextModel):
    display_name: Optional[str] = Field(None, max_length=255)

    __safe_text_fields__ = {"display_name": "short"}


class BulkEnrollRequest(BaseModel):
    user_ids: List[int]


class ScoreboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    student_id: Optional[str] = None
    total_score: int
    labs_completed: int
    achievements: List[str] = []
    lab_scores: dict = {}


class ScoreboardResponse(BaseModel):
    course: dict
    labs: List[dict]
    scoreboard: List[ScoreboardEntry]


class AchievementResponse(BaseModel):
    id: int
    user_id: int
    username: str
    achievement_type: str
    lab_id: Optional[int] = None
    lab_name: Optional[str] = None
    awarded_at: datetime

    class Config:
        from_attributes = True


# ==================== Assignment Schemas ====================

class AssignmentCreate(SafeTextModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    locked: Optional[bool] = False

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class AssignmentUpdate(SafeTextModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    locked: Optional[bool] = None

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class AssignmentLabsRequest(BaseModel):
    lab_ids: List[int]


# ==================== Dashboard Schemas ====================

class DashboardStatsResponse(BaseModel):
    active_sessions: int = 0
    submission_rate: int = 0
    pending_approvals: int = 0
    course_activity: int = 0


class ActivityEventResponse(BaseModel):
    id: int
    event_type: str
    event_label: str = ""
    actor_id: Optional[int] = None
    actor_username: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    target_label: Optional[str] = None
    detail: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PulseDataPoint(BaseModel):
    hour: str
    concurrent_labs: int = 0
    flags_submitted: int = 0


class PulseResponse(BaseModel):
    data: List[PulseDataPoint] = []


class StudentDashboardResponse(BaseModel):
    next_objective: Optional[dict] = None
    progress_percent: int = 0
    total_labs: int = 0
    completed_labs: int = 0
    vpn_status: Optional[dict] = None
    scoreboard_rank: Optional[int] = None
    course_name: Optional[str] = None


# ==================== Settings Schemas ====================

class SettingsBulkUpdate(BaseModel):
    settings: dict  # {"key": "value", ...}


class MailTestRequest(BaseModel):
    """Optional recipient for an admin-triggered SMTP test."""
    to: Optional[EmailStr] = None


class CustomAchievementCreate(SafeTextModel):
    """Admin-defined achievement definition."""
    name: str = Field(..., min_length=2, max_length=80)
    description: str | None = Field(None, max_length=500)
    icon: str = Field("\U0001F3C5", max_length=16)
    trigger: str = Field("labs_completed", max_length=30)
    threshold: int = Field(1, ge=1, le=10000)
    is_active: bool = True

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class CustomAchievementUpdate(SafeTextModel):
    name: str | None = Field(None, min_length=2, max_length=80)
    description: str | None = Field(None, max_length=500)
    icon: str | None = Field(None, max_length=16)
    trigger: str | None = Field(None, max_length=30)
    threshold: int | None = Field(None, ge=1, le=10000)
    is_active: bool | None = None

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


# ==================== Curriculum Admin Schemas ====================

class TrackCreate(SafeTextModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = "web"
    color: Optional[str] = "#3b82f6"

    __safe_text_fields__ = {"name": "short", "description": "multiline"}

    @field_validator('slug')
    @classmethod
    def slug_valid(cls, v: str) -> str:
        if not re.match(r'^[a-z][a-z0-9-]*$', v):
            raise ValueError('Slug must start with lowercase letter and contain only lowercase letters, numbers, and hyphens')
        return v


class TrackUpdate(SafeTextModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class LevelCreate(SafeTextModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class LevelUpdate(SafeTextModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class ReorderRequest(BaseModel):
    ordered_ids: List[int]


# ==================== Lab Creation & Flag Schemas ====================

class LabCreate(SafeTextModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    scenario: Optional[str] = None
    difficulty: str = "beginner"
    category: str = "general"
    duration_minutes: int = 60
    level_id: Optional[int] = None
    compose_file: str = ""
    objectives: Optional[str] = None
    prerequisites: Optional[str] = None
    mapped_skills: Optional[str] = None
    assessment_criteria: Optional[str] = None
    mitre_attack: Optional[str] = None
    hints: Optional[str] = None
    tools: Optional[str] = None
    hostnames: Optional[str] = None
    flag: Optional[str] = None
    visibility: Optional[str] = None
    lab_yaml: Optional[str] = None

    __safe_text_fields__ = {
        "name": "short",
        "description": "multiline",
        "scenario": "multiline",
        "objectives": "multiline",
        "hints": "multiline",
        "tools": "multiline",
        "hostnames": "multiline",
        "difficulty": "short",
        "category": "short",
    }
    @field_validator('slug')
    @classmethod
    def slug_valid(cls, v: str) -> str:
        if not re.match(r'^[a-z][a-z0-9-]*$', v):
            raise ValueError('Slug must start with lowercase letter and contain only lowercase letters, numbers, and hyphens')
        return v


class SetupRequest(SafeTextModel):
    admin_username: str = Field(..., min_length=3, max_length=50)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8, max_length=128)
    first_name: Optional[str] = Field(None, max_length=80)
    last_name: Optional[str] = Field(None, max_length=80)
    organization: Optional[str] = Field(None, max_length=120)
    require_approval: Optional[bool] = True
    # One-time install token; required only when the server sets SETUP_TOKEN
    # (see /setup/complete). Blank on isolated installs that don't set it.
    setup_token: Optional[str] = None

    __safe_text_fields__ = {
        "first_name": "short",
        "last_name": "short",
        "organization": "short",
    }

    @field_validator('admin_password')
    @classmethod
    def password_strong(cls, v: str) -> str:
        return _validate_password(v)








# ==================== Impersonation Schemas ====================

class ImpersonateRequest(BaseModel):
    target_user_id: Optional[int] = None
    target_role: Optional[str] = None
    course_id: Optional[int] = None

    @field_validator('target_role')
    @classmethod
    def target_role_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ('student', 'instructor'):
            raise ValueError('target_role must be student or instructor')
        return v


class ImpersonateResponse(BaseModel):
    token: str
    impersonated_user: dict
    original_user: dict
    mode: str  # "user" | "role_course" | "role_global"
    expires_in: int


# Update forward references after all models are defined
UserDetailResponse.update_forward_refs()

