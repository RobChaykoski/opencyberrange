"""Pydantic schemas for auth."""

import re
from app.schemas.lab import LabSessionResponse
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ValidationInfo,
    field_validator,
)

from app.schemas.common import SafeTextModel, _validate_password


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
    password_login_disabled: Optional[bool] = False

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
    institution_id: Optional[str] = None
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
    password_login_disabled: Optional[bool] = False
    is_minor: Optional[bool] = False
    age_band: Optional[str] = None
    parental_consent_reference: Optional[str] = None
    parental_consent_recorded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserPage(BaseModel):
    """One page of admin user rows, with the total for the current scope."""

    users: List[UserAdminResponse]
    total: int
    page: int
    per_page: int
    pages: int


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
    institution_id: Optional[str] = None
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
    password_login_disabled: Optional[bool] = False
    is_minor: Optional[bool] = False
    age_band: Optional[str] = None
    parental_consent_reference: Optional[str] = None
    parental_consent_recorded_at: Optional[datetime] = None

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


ASSIGNABLE_ROLES = (
    "student",
    "instructor",
    "teaching_assistant",
    "mentor",
    "auditor",
    "privacy_officer",
    "institution_admin",
    "admin",
)


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
    institution_id: Optional[str] = Field(None, max_length=64)
    # Privacy-preserving age band. Under-13 accounts require an institution
    # parental/guardian consent reference; exact dates of birth are not stored.
    age_band: Optional[Literal["under_13", "13_15", "16_17", "18_plus"]] = None
    parental_consent_reference: Optional[str] = Field(None, max_length=255)

    __safe_text_fields__ = {
        "first_name": "short",
        "last_name": "short",
        "parental_consent_reference": "short",
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
        if v is not None and v not in ASSIGNABLE_ROLES:
            raise ValueError("Role must be one of: " + ", ".join(ASSIGNABLE_ROLES))
        return v


class UpdateUserRequest(SafeTextModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    first_name: Optional[str] = Field(None, max_length=80)
    last_name: Optional[str] = Field(None, max_length=80)
    organization: Optional[str] = Field(None, max_length=120)
    institution_id: Optional[str] = Field(None, max_length=64)
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None
    is_admin: Optional[bool] = None
    role: Optional[str] = None
    must_change_password: Optional[bool] = None
    age_band: Optional[Literal["under_13", "13_15", "16_17", "18_plus"]] = None
    parental_consent_reference: Optional[str] = Field(None, max_length=255)

    __safe_text_fields__ = {
        "first_name": "short",
        "last_name": "short",
        "organization": "short",
        "parental_consent_reference": "short",
    }

    @field_validator('role')
    @classmethod
    def role_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ASSIGNABLE_ROLES:
            raise ValueError("Role must be one of: " + ", ".join(ASSIGNABLE_ROLES))
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


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=16, max_length=512)


class ReauthRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=128)
    totp_code: Optional[str] = Field(None, min_length=6, max_length=16)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    session_id: Optional[str] = None


class SetupRequest(SafeTextModel):
    admin_username: str = Field(..., min_length=3, max_length=50)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8, max_length=128)
    first_name: Optional[str] = Field(None, max_length=80)
    last_name: Optional[str] = Field(None, max_length=80)
    organization: Optional[str] = Field(None, max_length=120)
    require_approval: Optional[bool] = True
    # One-time install token. First-run setup always requires the operator to
    # configure SETUP_TOKEN (see /setup/complete); there is no unguarded path.
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
