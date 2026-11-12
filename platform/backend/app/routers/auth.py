"""
Authentication routes for login and registration
"""

from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from typing import Literal, Optional
import base64
import io
import logging
import qrcode
import re

from app.ratelimit import create_limiter
from app.services.input_safety import normalize_text
from app.database import get_db
from app.models import (
    User, WireGuardConfig, Lab, CourseLabAssignment, CourseEnrollment,
    Course, ExerciseReaction, InviteCode, Assignment, AssignmentLab,
    Competition, CompetitionParticipant, SurveyConsentEvent,
)
from app.auth import (
    authenticate_user,
    get_password_hash,
    create_access_token,
    get_user_by_username,
    get_current_active_user,
    verify_password,
    validate_privileged_password,
    is_impersonating,
    create_impersonation_token,
    revoke_token,
    revoke_all_user_tokens,
    _decode_token,
    oauth2_scheme,
)
from app.services import mail
from app.services import totp as totp_service
from app.config import settings
from app.schemas import ChangePasswordRequest, ImpersonateRequest, ImpersonateResponse, _validate_password, _password_policy_error
from app.services.wireguard_manager import WireGuardManager
from app.services.activity import log_activity, EventTypes
from app.services.audit import log_admin_action, AuditActions
from app.services.erasure import erase_user, ErasureBlocked
from app.services.settings_service import get_setting_fresh
from app.services.privacy import redact_ip
from app.services.survey_consent import (
    SURVEY_CONSENT_UPDATED,
    SURVEY_CONSENT_VERSION,
    survey_privacy_statement,
)

wireguard_manager = WireGuardManager()

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiter for auth endpoints - stricter limits for security
limiter = create_limiter()


def _registration_rate_limit() -> str:
    """Per-IP registration limits, relaxed while a competition is live.

    A DevFest-style event sends a room of sign-ups through one NAT address in
    a few minutes, which the normal limits would reject. Inside an active,
    non-archived event window the burst allowance applies; outside it the
    stricter limits do. Read at request time so no restart is needed.
    """
    try:
        from datetime import datetime, timezone

        from app.database import SessionLocal
        from app.models import Competition

        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            live = db.query(Competition.id).filter(
                Competition.is_active == True,
                Competition.is_archived == False,
                Competition.start_at <= now,
                Competition.end_at >= now,
            ).first()
        finally:
            db.close()
        if live:
            return "20/minute;120/hour;400/day"
    except Exception:
        logger.warning("Registration burst check failed; using strict limits", exc_info=True)
    return "5/minute;30/hour;100/day"



class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    student_id: Optional[str] = None
    is_admin: bool
    is_approved: bool
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    """Registration request with input validation for security"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=100)
    student_id: Optional[str] = Field(None, min_length=5, max_length=20)
    first_name: Optional[str] = Field(None, max_length=80)
    last_name: Optional[str] = Field(None, max_length=80)
    organization: Optional[str] = Field(None, max_length=120)
    password: str = Field(..., min_length=8, max_length=128)
    invite_code: Optional[str] = Field(None, min_length=4, max_length=64)
    # Optional competition sign-up link. A valid, open competition adds the new
    # account to the participant roster as a "new_user" registration.
    competition_id: Optional[int] = None
    # Transactional account email. The registration form asks the learner to
    # opt in; an explicit false suppresses the message without affecting the
    # account or approval state.
    send_registration_email: bool = True
    # Privacy control for learners under 18. When true, reporting and analytics
    # endpoints exclude this account from instructor-facing datasets.
    is_minor: bool = False

    @field_validator('username')
    @classmethod
    def username_valid(cls, v: str) -> str:
        """Username must start with letter and contain only alphanumeric, underscore, hyphen"""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError('Username must start with a letter and contain only letters, numbers, underscores, and hyphens')
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def name_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return normalize_text(v, field="name", allow_newlines=False)

    @field_validator('organization')
    @classmethod
    def organization_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return normalize_text(v, field="organization", allow_newlines=False)
    
    @field_validator('email')
    @classmethod
    def email_valid(cls, v: str) -> str:
        """Basic email format validation"""
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError('Invalid email format')
        return v.lower()  # Normalize to lowercase
    
    @field_validator('student_id')
    @classmethod
    def student_id_valid(cls, v: Optional[str]) -> Optional[str]:
        """Student ID must contain only alphanumeric characters (if provided)"""
        if v is None:
            return None
        if not re.match(r'^[A-Za-z0-9]+$', v):
            raise ValueError('Student ID must contain only letters and numbers')
        return v.upper()  # Normalize to uppercase
    
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


class UsernameReminderRequest(BaseModel):
    """Email address for the "forgot username" flow."""

    email: str = Field(..., min_length=3, max_length=254)

    @field_validator("email")
    @classmethod
    def email_valid(cls, value: str) -> str:
        email = value.strip().lower()
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            raise ValueError("Invalid email format")
        return email


@router.post("/forgot-username")
@limiter.limit("3/minute")
async def forgot_username(
    request: Request,
    payload: UsernameReminderRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Email the username to the address already on the account.

    The response is always the same, whether or not the address is registered,
    so this endpoint cannot be used to enumerate accounts. Mail is sent to the
    address supplied only after it matches an account; no other address is
    ever used.
    """
    email = payload.email
    rows = db.query(User).filter(func.lower(User.email) == email).all()
    usernames = sorted({row.username for row in rows if row.username})
    if usernames:
        background_tasks.add_task(
            mail.send_username_reminder_email,
            to_email=email,
            usernames=usernames,
            request_base=str(request.base_url),
        )
    return {
        "message": (
            "If that email is registered, we have sent the username to it."
        )
    }


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")  # 10 login attempts per minute per IP
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    totp_code: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Login endpoint - rate limited to 10 attempts per minute"""
    # Authenticate first — returns None for non-existent users, wrong
    # passwords, AND locked accounts.  We intentionally return the same
    # generic error for all cases to prevent username enumeration.
    from app.auth import LOCKOUT_DURATION_MINUTES

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Check if the account is locked so we can log it, but NEVER
        # reveal this distinction to the caller.
        existing_user = get_user_by_username(db, form_data.username)
        if existing_user and existing_user.is_locked:
            if existing_user.locked_at:
                locked_at = existing_user.locked_at
                if locked_at.tzinfo is None:
                    locked_at = locked_at.replace(tzinfo=timezone.utc)
                lockout_expires = locked_at + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                now = datetime.now(timezone.utc)
                if now >= lockout_expires:
                    # Lockout expired — tell user to try again (same generic message)
                    pass
                else:
                    logger.info(f"Login attempt for locked account: {form_data.username}")
            else:
                # Admin-locked account
                logger.info(f"Login attempt for admin-locked account: {form_data.username}")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is approved
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is locked (shouldn't happen after authenticate_user, but double-check)
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if is_active exists and is False
    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Second factor. Only enforced after the password checks out, so the
    # X-MFA-Required hint never leaks whether an account exists.
    if getattr(user, "mfa_enabled", False):
        if not totp_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA code required",
                headers={"WWW-Authenticate": "Bearer", "X-MFA-Required": "true"},
            )
        # Accept either a live TOTP code or a single-use recovery code.
        ok = totp_service.verify_code(user.totp_secret, totp_code)
        if not ok and getattr(user, "mfa_recovery_codes", None):
            try:
                stored = _json.loads(user.mfa_recovery_codes)
            except Exception:
                stored = []
            h = hashlib.sha256(totp_code.strip().upper().encode()).hexdigest()
            if h in stored:
                stored.remove(h)
                user.mfa_recovery_codes = _json.dumps(stored)
                db.commit()
                ok = True
                logger.info(f"User {user.username} used a recovery code at login")
        if not ok:
            logger.info(f"Failed MFA attempt for user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code",
                headers={"WWW-Authenticate": "Bearer", "X-MFA-Required": "true"},
            )

    # Record login metadata (session awareness / login notifications).
    client_ip = request.client.host if request.client else None
    is_new_ip = bool(client_ip and user.last_login_ip and client_ip != user.last_login_ip)
    now = datetime.now(timezone.utc)
    today = now.date()
    previous_login_day = getattr(user, "last_login_day", None)
    if previous_login_day == today:
        pass
    elif previous_login_day == today - timedelta(days=1):
        user.login_streak = (getattr(user, "login_streak", 0) or 0) + 1
    else:
        user.login_streak = 1
    user.last_login_day = today
    user.last_login_at = now
    user.last_login_ip = client_ip
    db.commit()

    # Streak and learning badges are global and idempotent. A failure here must
    # never block a valid sign-in.
    try:
        from app.services.achievements import (
            check_learning_achievements,
            check_login_streak_achievements,
        )
        check_login_streak_achievements(
            db, user.id, getattr(user, "login_streak", 1) or 1
        )
        check_learning_achievements(db, user.id)
    except Exception:
        db.rollback()
        logger.exception("Could not evaluate engagement achievements for user %s", user.username)

    if getattr(user, "login_notifications", True) and is_new_ip:
        logger.info(
            "Login notification: user %s logged in from new IP %s (previous %s)",
            user.username, client_ip, user.last_login_ip,
        )
        # Email delivery is not configured in this deployment; the event is
        # recorded above and surfaced through the activity feed instead.

    # Create access token
    access_token_expires = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    # Return token and user info
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "student_id": user.student_id,
        "role": getattr(user, 'role', 'admin' if user.is_admin else 'student'),
        "is_admin": user.role == 'admin' if hasattr(user, 'role') else user.is_admin,
        "is_approved": user.is_approved,
        "must_change_password": getattr(user, 'must_change_password', False),
        "timezone": getattr(user, 'timezone', None),
    }
    
    # Add is_active if it exists
    if hasattr(user, 'is_active'):
        user_dict["is_active"] = user.is_active
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }


# ==================== User settings (optional security/privacy) ====================

import hashlib
import json as _json
import secrets as _secrets

# Avatars are stored inline as a data URL so they survive container rebuilds
# without a shared upload volume. The browser resizes before upload; the cap
# here is a server-side guard, not the expected size (~30-80 KB).
_AVATAR_DATA_URL_RE = re.compile(
    r"^data:image/(png|jpeg|jpg|webp);base64,([A-Za-z0-9+/=\s]+)$"
)
_MAX_AVATAR_BYTES = 512 * 1024

# Cosmetic avatar ring. Values are short tokens; the frontend maps them to CSS,
# so a profile row can never inject arbitrary style text into the page.
AVATAR_BORDER_STYLES = ("none", "solid", "dashed", "double", "glow", "gradient")
AVATAR_BORDER_COLORS = (
    "blue", "violet", "emerald", "amber", "rose", "cyan", "slate", "gold",
)


def _validate_avatar_data(value: Optional[str]) -> Optional[str]:
    """Accept only a small, real raster image as a base64 data URL."""
    from app.services.image_validation import validate_image_data_url

    return validate_image_data_url(
        value,
        label="Avatar",
        max_bytes=_MAX_AVATAR_BYTES,
        max_pixels=4_000_000,
    )


EMAIL_CONSENT_VERSION = "2026-11-04"

# Avatar border colours are chosen with a hue slider, so new values are plain
# #RRGGBB hex. The original eight named tokens are still accepted so existing
# profiles keep working until their owner next saves the border.
_AVATAR_BORDER_HEX = re.compile(r"^#[0-9a-f]{6}$")
_LEGACY_AVATAR_BORDER_COLORS = {
    "blue": "#3b82f6",
    "violet": "#8b5cf6",
    "emerald": "#10b981",
    "amber": "#f59e0b",
    "rose": "#f43f5e",
    "cyan": "#06b6d4",
    "slate": "#64748b",
    "gold": "#d4a017",
}


class UserSettingsUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=80)
    last_name: Optional[str] = Field(None, max_length=80)
    organization: Optional[str] = Field(None, max_length=120)
    avatar_data: Optional[str] = Field(None, max_length=800_000)
    avatar_border_style: Optional[Literal[
        "none", "solid", "dashed", "double", "glow", "gradient"
    ]] = None
    avatar_border_color: Optional[str] = Field(None, max_length=7)
    timezone: Optional[str] = Field(None, max_length=64)
    show_on_scoreboard: Optional[bool] = None
    scoreboard_name_mode: Optional[Literal["real_name", "username", "anonymous"]] = None
    login_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    notification_prefs: Optional[dict] = None
    show_hidden_achievements: Optional[bool] = None
    certificates_public: Optional[bool] = None
    is_minor: Optional[bool] = None

    @field_validator("avatar_data")
    @classmethod
    def avatar_valid(cls, v: Optional[str]) -> Optional[str]:
        return _validate_avatar_data(v)

    @field_validator("avatar_border_color")
    @classmethod
    def avatar_border_color_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        value = v.strip().lower()
        if value in _LEGACY_AVATAR_BORDER_COLORS or _AVATAR_BORDER_HEX.match(value):
            return value
        raise ValueError("avatar border colour must be a #RRGGBB hex value")

    @field_validator("first_name", "last_name")
    @classmethod
    def name_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return normalize_text(v, field="name", allow_newlines=False)

    @field_validator("organization")
    @classmethod
    def organization_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return normalize_text(v, field="organization", allow_newlines=False)

    @field_validator("timezone")
    @classmethod
    def timezone_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = normalize_text(v, field="timezone", allow_newlines=False, max_length=64)
        return cleaned or None

class RecoveryCodeVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=32)

@router.get("/settings")
async def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    prefs = None
    if getattr(current_user, "notification_prefs", None):
        try:
            prefs = _json.loads(current_user.notification_prefs)
        except Exception:
            prefs = None
    recovery_count = 0
    if getattr(current_user, "mfa_recovery_codes", None):
        try:
            recovery_count = len(_json.loads(current_user.mfa_recovery_codes))
        except Exception:
            recovery_count = 0
    return {
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "organization": current_user.organization,
        "avatar_data": getattr(current_user, "avatar_data", None),
        "avatar_border_style": getattr(current_user, "avatar_border_style", None) or "solid",
        "avatar_border_color": getattr(current_user, "avatar_border_color", None) or "blue",
        "timezone": current_user.timezone,
        "show_on_scoreboard": getattr(current_user, "show_on_scoreboard", True),
        "scoreboard_name_mode": getattr(current_user, "scoreboard_name_mode", None) or "real_name",
        "login_notifications": getattr(current_user, "login_notifications", True),
        "email_notifications": getattr(current_user, "email_notifications", True),
        "email_consent_version": getattr(current_user, "email_consent_version", None),
        "email_consent_updated_at": getattr(current_user, "email_consent_updated_at", None),
        "notification_prefs": prefs or {},
        "show_hidden_achievements": bool(
            getattr(current_user, "show_hidden_achievements", False)
        ),
        "survey_opt_in": bool(getattr(current_user, "survey_opt_in", False)),
        "survey_consent_version": getattr(current_user, "survey_consent_version", None),
        "certificates_public": bool(
            getattr(current_user, "certificates_public", True)
        ),
        "is_minor": bool(getattr(current_user, "is_minor", False)),
        "data_exported_at": getattr(current_user, "data_exported_at", None),
        "mfa_enabled": getattr(current_user, "mfa_enabled", False),
        "recovery_codes_remaining": recovery_count,
        "last_login_at": current_user.last_login_at,
        "last_login_ip": redact_ip(current_user.last_login_ip),
    }

@router.put("/settings")
@limiter.limit("20/minute")
async def update_user_settings(
    request: Request,
    payload: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if payload.first_name is not None:
        current_user.first_name = payload.first_name
    if payload.last_name is not None:
        current_user.last_name = payload.last_name
    if payload.organization is not None:
        current_user.organization = payload.organization
    if payload.avatar_data is not None:
        current_user.avatar_data = payload.avatar_data or None
    if payload.avatar_border_style is not None:
        current_user.avatar_border_style = payload.avatar_border_style
    if payload.avatar_border_color is not None:
        current_user.avatar_border_color = payload.avatar_border_color
    if payload.timezone is not None:
        current_user.timezone = payload.timezone
    if payload.show_on_scoreboard is not None:
        if payload.show_on_scoreboard and getattr(current_user, "is_minor", False):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Learners under 18 cannot be listed on public scoreboards. "
                    "Clear the under-18 setting first if that is no longer accurate."
                ),
            )
        current_user.show_on_scoreboard = payload.show_on_scoreboard
    if payload.scoreboard_name_mode is not None:
        current_user.scoreboard_name_mode = payload.scoreboard_name_mode
    if payload.is_minor is not None:
        current_user.is_minor = payload.is_minor
        if payload.is_minor:
            # Enforce the privacy rule immediately, even for an account that
            # previously opted into the scoreboard.
            current_user.show_on_scoreboard = False
            current_user.scoreboard_name_mode = "anonymous"
    if payload.login_notifications is not None:
        current_user.login_notifications = payload.login_notifications
    if payload.email_notifications is not None:
        current_user.email_notifications = payload.email_notifications
        current_user.email_consent_version = EMAIL_CONSENT_VERSION
        current_user.email_consent_updated_at = datetime.now(timezone.utc)
    if payload.notification_prefs is not None:
        current_user.notification_prefs = _json.dumps(payload.notification_prefs)
    if payload.show_hidden_achievements is not None:
        current_user.show_hidden_achievements = payload.show_hidden_achievements
    if payload.certificates_public is not None:
        current_user.certificates_public = payload.certificates_public
    db.commit()
    db.refresh(current_user)
    return {"message": "Settings updated"}


class SurveyConsentUpdate(BaseModel):
    opt_in: bool
    policy_version: Optional[str] = Field(None, max_length=32)


def _survey_consent_state(user: User, *, include_statement: bool = False) -> dict:
    state = {
        "opt_in": bool(getattr(user, "survey_opt_in", False)),
        "opted_in_at": getattr(user, "survey_opt_in_at", None),
        "consent_version": getattr(user, "survey_consent_version", None),
        "current_version": SURVEY_CONSENT_VERSION,
        "statement_updated": SURVEY_CONSENT_UPDATED,
    }
    if include_statement:
        state["statement"] = survey_privacy_statement(
            settings.PRIVACY_CONTACT_EMAIL
        )
    return state


@router.get("/survey-consent")
async def get_survey_consent(
    current_user: User = Depends(get_current_active_user),
):
    """Return the account's survey opt-in state and the current statement."""
    return _survey_consent_state(current_user, include_statement=True)


@router.post("/survey-consent")
async def update_survey_consent(
    payload: SurveyConsentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record an explicit survey opt-in or withdrawal.

    Opting in requires the caller to have reviewed the current statement. Every
    change is appended to ``survey_consent_events`` with the statement version
    so the consent decision remains auditable after the user row changes.
    """
    currently_in = bool(getattr(current_user, "survey_opt_in", False))

    if payload.opt_in:
        if payload.policy_version != SURVEY_CONSENT_VERSION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Please review the current survey privacy statement "
                    "before opting in."
                ),
            )
        if not currently_in:
            current_user.survey_opt_in = True
            current_user.survey_opt_in_at = datetime.now(timezone.utc)
            current_user.survey_consent_version = SURVEY_CONSENT_VERSION
            db.add(
                SurveyConsentEvent(
                    user_id=current_user.id,
                    action="opt_in",
                    policy_version=SURVEY_CONSENT_VERSION,
                )
            )
            logger.info(
                "User %s opted in to platform surveys (policy %s)",
                current_user.username,
                SURVEY_CONSENT_VERSION,
            )
    else:
        # Withdrawal is always allowed and is recorded even if the account was
        # already opted out, so the user's request is visible in the history.
        current_user.survey_opt_in = False
        current_user.survey_opt_in_at = None
        if not getattr(current_user, "survey_consent_version", None):
            current_user.survey_consent_version = SURVEY_CONSENT_VERSION
        db.add(
            SurveyConsentEvent(
                user_id=current_user.id,
                action="opt_out",
                policy_version=SURVEY_CONSENT_VERSION,
            )
        )
        logger.info(
            "User %s withdrew consent for platform surveys (policy %s)",
            current_user.username,
            SURVEY_CONSENT_VERSION,
        )

    db.commit()
    db.refresh(current_user)
    return {
        **_survey_consent_state(current_user),
        "message": (
            "You are opted in to optional platform surveys."
            if current_user.survey_opt_in
            else "You are opted out of platform surveys."
        ),
    }

@router.post("/mfa/recovery-codes")
async def generate_recovery_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Generate 10 single-use codes; store only their hashes.
    codes = [_secrets.token_hex(4).upper() for _ in range(10)]
    hashed = [hashlib.sha256(c.encode()).hexdigest() for c in codes]
    current_user.mfa_recovery_codes = _json.dumps(hashed)
    db.commit()
    logger.info(f"User {current_user.username} generated MFA recovery codes")
    return {"codes": codes, "message": "Store these codes safely. They will not be shown again."}

@router.post("/mfa/recovery-codes/verify")
async def verify_recovery_code(
    body: RecoveryCodeVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.mfa_recovery_codes:
        raise HTTPException(status_code=400, detail="No recovery codes available")
    try:
        stored = _json.loads(current_user.mfa_recovery_codes)
    except Exception:
        stored = []
    h = hashlib.sha256(body.code.strip().upper().encode()).hexdigest()
    if h not in stored:
        raise HTTPException(status_code=401, detail="Invalid recovery code")
    stored.remove(h)
    current_user.mfa_recovery_codes = _json.dumps(stored)
    db.commit()
    return {"message": "Recovery code accepted", "remaining": len(stored)}

@router.get("/sessions")
async def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return {
        "current": {
            "last_login_at": current_user.last_login_at,
            "last_login_ip": redact_ip(current_user.last_login_ip),
        },
        "note": "Individual session tracking is not stored; use 'Sign out everywhere' to revoke all tokens.",
    }

@router.post("/sessions/revoke-all")
async def revoke_all_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    revoke_all_user_tokens(current_user.username)
    logger.info(f"User {current_user.username} revoked all sessions")
    return {"message": "All sessions revoked. Please log in again."}

@router.get("/export")
async def export_user_data(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the account holder's personal data in a portable JSON document.

    Secrets are deliberately excluded (password hash, TOTP secret, recovery
    codes, trusted-device tokens and the WireGuard private key). Everything
    else the platform holds about the account is included so this can serve as
    the response to a subject-access request.
    """
    from app.models import (
        Achievement,
        ActivityEvent,
        Competition,
        CompetitionParticipant,
        Course,
        CourseEnrollment,
        ExternalIdentity,
        FlagAttempt,
        IdentityProvider,
        Lab,
        LabCompletion,
        LabSession,
        LevelQuiz,
        QuizAttempt,
        SsoSession,
        SurveyConsentEvent,
        WireGuardConfig,
    )

    def _json_or_raw(value):
        if not value:
            return None
        try:
            return _json.loads(value)
        except Exception:
            return value

    uid = current_user.id
    completions = db.query(LabCompletion).filter(LabCompletion.user_id == uid).all()
    reactions = db.query(ExerciseReaction).filter(
        ExerciseReaction.user_id == uid
    ).all()
    achievements = db.query(Achievement).filter(Achievement.user_id == uid).all()
    attempts = db.query(FlagAttempt).filter(FlagAttempt.user_id == uid).all()
    quiz_attempts = (
        db.query(QuizAttempt, LevelQuiz)
        .join(LevelQuiz, LevelQuiz.id == QuizAttempt.quiz_id, isouter=True)
        .filter(QuizAttempt.user_id == uid)
        .all()
    )
    enrollments = (
        db.query(CourseEnrollment, Course)
        .join(Course, Course.id == CourseEnrollment.course_id, isouter=True)
        .filter(CourseEnrollment.user_id == uid)
        .all()
    )
    sessions = (
        db.query(LabSession, Lab)
        .join(Lab, Lab.id == LabSession.lab_id, isouter=True)
        .filter(LabSession.user_id == uid)
        .all()
    )
    competitions = (
        db.query(CompetitionParticipant, Competition)
        .join(Competition, Competition.id == CompetitionParticipant.competition_id, isouter=True)
        .filter(CompetitionParticipant.user_id == uid)
        .all()
    )
    activity = (
        db.query(ActivityEvent)
        .filter(
            (ActivityEvent.actor_id == uid)
            | (
                (ActivityEvent.target_type == "user")
                & (ActivityEvent.target_id == uid)
            )
        )
        .order_by(ActivityEvent.created_at)
        .all()
    )
    vpn = db.query(WireGuardConfig).filter(WireGuardConfig.user_id == uid).first()
    consent_events = (
        db.query(SurveyConsentEvent)
        .filter(SurveyConsentEvent.user_id == uid)
        .order_by(SurveyConsentEvent.created_at)
        .all()
    )
    external_identities = (
        db.query(ExternalIdentity, IdentityProvider)
        .join(IdentityProvider, IdentityProvider.id == ExternalIdentity.provider_id, isouter=True)
        .filter(ExternalIdentity.user_id == uid)
        .order_by(ExternalIdentity.created_at)
        .all()
    )
    sso_sessions = (
        db.query(SsoSession, IdentityProvider)
        .join(IdentityProvider, IdentityProvider.id == SsoSession.provider_id, isouter=True)
        .filter(SsoSession.user_id == uid)
        .order_by(SsoSession.created_at)
        .all()
    )

    completion_lab_ids = [c.lab_id for c in completions]
    completion_lab_ids += [r.lab_id for r in reactions]
    lab_by_id = {
        row.id: row
        for row in db.query(Lab).filter(Lab.id.in_(completion_lab_ids)).all()
    } if completion_lab_ids else {}

    exported_at = datetime.now(timezone.utc)
    current_user.data_exported_at = exported_at
    db.commit()

    # The account holder's request is itself the reason. Record it so the
    # compliance trail is complete without prompting the user for a purpose.
    log_admin_action(
        action=AuditActions.USER_DATA_EXPORTED,
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        target_type="user",
        target_id=current_user.id,
        details={"reason": "Self-service subject access request"},
        ip_address=request.client.host if request.client else None,
    )

    return {
        "format_version": 2,
        "generated_at": exported_at,
        "account": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "student_id": current_user.student_id,
            "organization": current_user.organization,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "is_approved": current_user.is_approved,
            "is_locked": current_user.is_locked,
            "avatar_data": current_user.avatar_data,
            "avatar_border_style": getattr(current_user, "avatar_border_style", None) or "solid",
            "avatar_border_color": getattr(current_user, "avatar_border_color", None) or "blue",
            "created_at": current_user.created_at,
            "last_login_at": current_user.last_login_at,
            "last_login_ip": redact_ip(current_user.last_login_ip),
            "timezone": current_user.timezone,
            "show_on_scoreboard": current_user.show_on_scoreboard,
            "is_minor": bool(getattr(current_user, "is_minor", False)),
            "scoreboard_name_mode": getattr(current_user, "scoreboard_name_mode", None) or "real_name",
            "login_notifications": current_user.login_notifications,
            "email_notifications": getattr(current_user, "email_notifications", True),
            "email_consent_version": getattr(current_user, "email_consent_version", None),
            "email_consent_updated_at": getattr(current_user, "email_consent_updated_at", None),
            "login_streak": getattr(current_user, "login_streak", 0),
            "last_login_day": getattr(current_user, "last_login_day", None),
            "notification_prefs": _json_or_raw(current_user.notification_prefs),
            "mfa_enabled": bool(current_user.mfa_enabled),
            "vpn_registered": bool(current_user.vpn_registered),
        },
        "vpn": (
            {
                "client_ip": redact_ip(vpn.client_ip),
                "public_key": vpn.public_key,
                "created_at": vpn.created_at,
            }
            if vpn
            else None
        ),
        # Identity-federation data: which external account this local account
        # is linked to. The provider secret and the encrypted ID token are not
        # personal data about the learner and are deliberately omitted.
        "external_identities": [
            {
                "provider": provider.name if provider else None,
                "provider_kind": provider.kind if provider else None,
                "subject": link.subject,
                "email": link.email,
                "linked_at": link.created_at,
                "last_login_at": link.last_login_at,
            }
            for link, provider in external_identities
        ],
        "sso_sessions": [
            {
                "provider": provider.name if provider else None,
                "created_at": session.created_at,
                "expires_at": session.expires_at,
            }
            for session, provider in sso_sessions
        ],
        "courses": [
            {
                "course_id": course.id if course else enrollment.course_id,
                "code": course.code if course else None,
                "name": course.name if course else None,
                "semester": course.semester if course else None,
                "enrolled_at": enrollment.enrolled_at,
                "seat_number": enrollment.seat_number,
            }
            for enrollment, course in enrollments
        ],
        "completions": [
            {
                "lab_id": c.lab_id,
                "lab_name": lab_by_id[c.lab_id].name if c.lab_id in lab_by_id else None,
                "lab_slug": lab_by_id[c.lab_id].slug if c.lab_id in lab_by_id else None,
                "chapter_id": lab_by_id[c.lab_id].chapter_id if c.lab_id in lab_by_id else None,
                "chapter_name": lab_by_id[c.lab_id].chapter_name if c.lab_id in lab_by_id else None,
                "primary_competency": lab_by_id[c.lab_id].primary_competency if c.lab_id in lab_by_id else None,
                "framework_refs": lab_by_id[c.lab_id].framework_refs_list if c.lab_id in lab_by_id else [],
                "measurable_outcome": lab_by_id[c.lab_id].measurable_outcome if c.lab_id in lab_by_id else None,
                "completed_at": c.completed_at,
                "attempts": c.attempts,
                "hints_used": c.hints_used,
                "time_spent_minutes": c.time_spent_minutes,
            }
            for c in completions
        ],
        "exercise_reactions": [
            {
                "lab_id": r.lab_id,
                "lab_name": lab_by_id[r.lab_id].name if r.lab_id in lab_by_id else None,
                "lab_slug": lab_by_id[r.lab_id].slug if r.lab_id in lab_by_id else None,
                "course_id": r.course_id,
                "reaction": r.reaction,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in reactions
        ],
        "flag_attempts": [
            {
                "lab_id": a.lab_id,
                "is_correct": a.is_correct,
                "attempted_at": a.attempted_at,
            }
            for a in attempts
        ],
        "quiz_attempts": [
            {
                "quiz_id": attempt.quiz_id,
                "quiz_title": quiz.title if quiz else None,
                "score": attempt.score,
                "total": attempt.total,
                "correct": attempt.correct,
                "passed": attempt.passed,
                "taken_at": attempt.taken_at,
                "answers": _json_or_raw(attempt.answers),
            }
            for attempt, quiz in quiz_attempts
        ],
        "achievements": [
            {
                "type": a.achievement_type,
                "course_id": a.course_id,
                "lab_id": a.lab_id,
                "awarded_at": a.awarded_at,
            }
            for a in achievements
        ],
        "lab_sessions": [
            {
                "lab_id": session.lab_id,
                "lab_name": lab.name if lab else None,
                "lab_slug": lab.slug if lab else None,
                "status": session.status,
                "started_at": session.started_at,
                "expires_at": session.expires_at,
                "stopped_at": session.stopped_at,
            }
            for session, lab in sessions
        ],
        "competitions": [
            {
                "competition_id": participant.competition_id,
                "name": competition.name if competition else None,
                "joined_at": participant.joined_at,
                "source": participant.source,
            }
            for participant, competition in competitions
        ],
        "activity": [
            {
                "event_type": event.event_type,
                "target_type": event.target_type,
                "target_label": event.target_label,
                "detail": _json_or_raw(event.detail),
                "ip_address": redact_ip(event.ip_address),
                "created_at": event.created_at,
            }
            for event in activity
        ],
        "survey_consent": {
            "opt_in": bool(getattr(current_user, "survey_opt_in", False)),
            "opted_in_at": getattr(current_user, "survey_opt_in_at", None),
            "consent_version": getattr(current_user, "survey_consent_version", None),
            "current_version": SURVEY_CONSENT_VERSION,
            "history": [
                {
                    "action": event.action,
                    "policy_version": event.policy_version,
                    "created_at": event.created_at,
                }
                for event in consent_events
            ],
        },
    }


@router.get("/export-status")
async def export_status(
    current_user: User = Depends(get_current_active_user),
):
    """Return when the account last downloaded a copy of its data."""
    return {
        "last_exported_at": getattr(current_user, "data_exported_at", None),
    }


class DeleteAccountRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=128)
    code: Optional[str] = Field(None, min_length=6, max_length=8)
    confirm: str = Field(..., min_length=1, max_length=16)


@router.post("/delete-account")
@limiter.limit("3/minute")
async def delete_my_account(
    request: Request,
    body: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Permanently erase the signed-in account and its personal data.

    Requires the current password, a live TOTP code (or an unused recovery
    code) when MFA is enabled, and the literal confirmation ``DELETE``.
    """
    if is_impersonating(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete an account while impersonating another user.",
        )
    if body.confirm != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type DELETE exactly to confirm account deletion.",
        )
    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect.",
        )

    if getattr(current_user, "mfa_enabled", False):
        if not body.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enter your authenticator code to delete this account.",
            )
        ok = totp_service.verify_code(current_user.totp_secret, body.code)
        if not ok and getattr(current_user, "mfa_recovery_codes", None):
            try:
                stored = _json.loads(current_user.mfa_recovery_codes)
            except Exception:
                stored = []
            h = hashlib.sha256(body.code.strip().upper().encode()).hexdigest()
            # Do not consume the code here: if erasure is blocked (owned
            # courses or last admin), the code must remain valid.
            ok = h in stored
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authenticator or recovery code.",
            )

    captured_id = current_user.id
    try:
        result = erase_user(db, current_user, actor="self")
    except ErasureBlocked as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        ) from exc

    log_admin_action(
        action=AuditActions.USER_SELF_DELETED,
        admin_user_id=captured_id,
        admin_username="self-service",
        target_type="user",
        target_id=None,
        target_identifier=None,
        details={
            "erased": result.deleted,
            "anonymised": result.anonymised,
        },
        ip_address=request.client.host if request.client else None,
    )

    return {
        "message": "Your account and personal data have been deleted.",
        "erased": result.deleted,
        "anonymised": result.anonymised,
    }


@router.post("/delete-request", status_code=status.HTTP_410_GONE)
async def request_account_deletion(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retired no-op endpoint.

    It previously claimed to record a request while only writing a log line.
    Self-service deletion is now immediate and authenticated; keep this route
    so older clients get a clear instruction instead of a silent no-op.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail=(
            "Deletion requests are no longer queued. Use "
            "POST /api/auth/delete-account from the Profile page."
        ),
    )

@router.post("/register", response_model=UserResponse)
@limiter.limit(_registration_rate_limit)
async def register(
    request: Request,
    user_data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user.

    Per-IP limits are strict normally (5/minute; 30/hour; 100/day) and relax
    to a burst allowance (20/minute; 120/hour; 400/day) while a competition
    window is live. The invite-code and approval gates remain the controls
    that decide *who* may register.
    """
    # Check for existing username, email, or student_id.
    # Use a single generic error to prevent account enumeration.
    existing = get_user_by_username(db, user_data.username)
    if not existing:
        existing = db.query(User).filter(User.email == user_data.email).first()
    if not existing and user_data.student_id:
        existing = db.query(User).filter(User.student_id == user_data.student_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with these credentials already exists"
        )
    
    # Invite gate: registration needs a valid, unused InviteCode. The gate is
    # OFF by default; a deployment turns it on with the runtime
    # "require_invite_code" setting when it wants registration limited to
    # issued codes. Errors stay generic so codes cannot be probed for their
    # state (nonexistent vs used vs expired vs wrong email).
    #
    # The default used to be ON, which blocked every fresh install. A new
    # install has no codes issued, and the sign-up form does not show a code
    # field until the server asks for one, so nobody could register at all.
    # The approval gate below is the control that was actually wanted.
    #
    # Read fresh rather than cached: a gate that controls access must not go
    # on enforcing for up to the cache TTL on whichever workers missed the
    # write (see settings_service.get_setting_fresh).
    invite = None
    require_invite = get_setting_fresh(db, "require_invite_code", "false") == "true"
    supplied_code = (user_data.invite_code or "").strip()
    if require_invite:
        if not supplied_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An invite code is required to register"
            )
        # Row lock so two concurrent registrations cannot both consume
        # the same single-use code.
        invite = db.query(InviteCode).filter(
            InviteCode.code == supplied_code
        ).with_for_update().first()
        invite_valid = (
            invite is not None
            and invite.used_by is None
            and invite.used_at is None
        )
        if invite_valid:
            expires = invite.expires_at
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if expires < datetime.now(timezone.utc):
                invite_valid = False
        if invite_valid and invite.email:
            # Email-pinned codes only register their own address
            if invite.email.lower() != user_data.email:
                invite_valid = False
        if not invite_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired invite code"
            )

    # Approval gate honors the runtime "require_approval" setting: when an admin
    # turns approval off, registrations are auto-approved and can log in at once.
    require_approval = get_setting_fresh(db, "require_approval", "true") != "false"

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        student_id=user_data.student_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        organization=user_data.organization,
        hashed_password=hashed_password,
        is_admin=False,
        is_approved=not require_approval,
        is_active=True if hasattr(User, 'is_active') else None,
        is_locked=False,
        failed_attempts=0
    )
    
    db.add(new_user)
    db.flush()  # assign new_user.id without ending the transaction

    # Competition sign-up link: add the new account to the event roster in the
    # same transaction as the user insert. A closed or missing competition never
    # blocks account creation; it simply does not add a roster entry.
    if user_data.competition_id:
        competition = db.query(Competition).filter(
            Competition.id == user_data.competition_id,
            Competition.is_active == True,
        ).first()
        if competition:
            end_at = competition.end_at
            if end_at.tzinfo is None:
                end_at = end_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) <= end_at:
                db.add(CompetitionParticipant(
                    competition_id=competition.id,
                    user_id=new_user.id,
                    source="new_user",
                ))

    # Burn the invite code in the same transaction as the user insert, so
    # the with_for_update() row lock holds until both changes land together.
    if invite is not None:
        invite.used_by = new_user.id
        invite.used_at = datetime.now(timezone.utc)

    new_user.email_notifications = bool(user_data.send_registration_email)
    new_user.email_consent_version = EMAIL_CONSENT_VERSION
    new_user.email_consent_updated_at = datetime.now(timezone.utc)
    new_user.is_minor = bool(user_data.is_minor)
    if new_user.is_minor:
        new_user.show_on_scoreboard = False
        new_user.scoreboard_name_mode = "anonymous"

    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {new_user.username} (ID: {new_user.id})")

    log_activity(db, EventTypes.USER_REGISTERED,
                  actor_id=new_user.id, target_type="user",
                  target_id=new_user.id, target_label=new_user.username)

    if user_data.send_registration_email:
        background_tasks.add_task(
            mail.send_registration_email,
            user_id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            display_name=new_user.display_name,
            approved=bool(new_user.is_approved),
            request_base=str(request.base_url),
        )

    return new_user


@router.get("/me")
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information - syncs VPN registration status with Peer Manager.
    When impersonating, returns the effective (impersonated) identity with metadata."""
    imp = is_impersonating(current_user)
    imp_mode = getattr(current_user, '_imp_mode', None)

    # For synthetic impersonation modes, override the returned identity
    if imp and imp_mode in ('role_course', 'role_global'):
        imp_course_id = getattr(current_user, '_imp_course_id', None)
        course_name = None
        if imp_course_id:
            course = db.query(Course).filter(Course.id == imp_course_id).first()
            course_name = course.name if course else None

        return {
            "id": current_user.id,
            "username": f"_preview_{current_user.username}",
            "email": current_user.email,
            "student_id": None,
            "is_active": True,
            "is_approved": True,
            "is_admin": False,
            "role": "student" if imp_mode == 'role_course' else getattr(current_user, '_imp_mode', 'student'),
            "must_change_password": False,
            "mfa_enabled": False,
            "timezone": getattr(current_user, 'timezone', None),
            "impersonating": True,
            "impersonation": {
                "original_user": {
                    "id": current_user._imp_original_id,
                    "username": current_user._imp_original_username,
                },
                "mode": imp_mode,
                "course_id": imp_course_id,
                "course_name": course_name,
                "read_only": True,
            },
        }

    # Sync VPN registration status with Peer Manager (same logic as /labs/vpn-status)
    if not imp:
        wg_config = db.query(WireGuardConfig).filter(
            WireGuardConfig.user_id == current_user.id
        ).first()

        if wg_config and wg_config.public_key:
            try:
                actually_registered = wireguard_manager.peer_exists(wg_config.public_key)

                # Sync database flag if it's out of sync
                if actually_registered != current_user.vpn_registered:
                    current_user.vpn_registered = actually_registered
                    db.commit()
                    logger.info(f"Synced VPN registration status for user {current_user.username}: {actually_registered}")
            except Exception as e:
                logger.warning(f"Could not verify peer status with Peer Manager: {e}")

    # Build response
    resp = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "student_id": current_user.student_id,
        "first_name": getattr(current_user, 'first_name', None),
        "last_name": getattr(current_user, 'last_name', None),
        "organization": getattr(current_user, 'organization', None),
        "avatar_data": getattr(current_user, 'avatar_data', None),
        "avatar_border_style": getattr(current_user, 'avatar_border_style', None) or "solid",
        "avatar_border_color": getattr(current_user, 'avatar_border_color', None) or "blue",
        "is_active": getattr(current_user, 'is_active', True),
        "is_approved": current_user.is_approved,
        "is_admin": current_user.role == 'admin',
        "role": current_user.role,
        "must_change_password": getattr(current_user, 'must_change_password', False),
        "mfa_enabled": bool(getattr(current_user, "mfa_enabled", False)),
        "timezone": getattr(current_user, 'timezone', None),
        "show_on_scoreboard": getattr(current_user, "show_on_scoreboard", True),
        "is_minor": bool(getattr(current_user, "is_minor", False)),
        "scoreboard_name_mode": getattr(current_user, "scoreboard_name_mode", None) or "real_name",
        "show_hidden_achievements": bool(
            getattr(current_user, "show_hidden_achievements", False)
        ),
    }

    if imp:
        resp["impersonating"] = True
        resp["impersonation"] = {
            "original_user": {
                "id": current_user._imp_original_id,
                "username": current_user._imp_original_username,
            },
            "mode": imp_mode,
            "course_id": getattr(current_user, '_imp_course_id', None),
            "read_only": True,
        }

    return resp


def _require_workbook_released(db, current_user, original_uri: str) -> None:
    """Hold a course workbook page until its assignment opens.

    Enrollment alone used to open every chapter, so a student could read the
    Week 15 walkthrough during Week 1 while the Week 15 exercise stayed locked.
    The exercise list and the workbook are two views of the same schedule and
    should release together.

    The page is mapped to its assignment through data rather than by parsing
    week numbers out of directory names: the requested path is matched against
    ``Lab.workbook`` prefixes, and those labs are followed through
    ``assignment_labs`` to their assignments.

    Deliberately permissive when there is nothing to enforce. A path that
    matches no lab (a chapter index, the wiki root, a shared asset) is allowed,
    and so is a lab that no assignment schedules. A page reachable from several
    assignments opens with the earliest of them, so shared pages are never
    stranded behind the latest week that happens to cite them.
    """
    wiki_path = _normalize_wiki_path(original_uri)
    if not wiki_path:
        return

    labs = db.query(Lab).filter(
        Lab.workbook.isnot(None), Lab.workbook != ""
    ).all()
    lab_ids = []
    for lab in labs:
        # Older rows store a bare chapter path with no leading "wiki/" segment.
        # _normalize_wiki_path returns "" for those, and "".startswith() is
        # True for every request, so an unguarded comparison matched every lab
        # in the catalogue and pulled in unrelated courses' assignments. An
        # empty prefix is not a match.
        prefix = _normalize_wiki_path("/" + lab.workbook.lstrip("/"))
        if not prefix:
            prefix = _normalize_wiki_path("/wiki/" + lab.workbook.lstrip("/"))
        if not prefix:
            continue
        if wiki_path.startswith(prefix):
            lab_ids.append(lab.id)
            continue
        # Also hold the rest of the chapter the lab lives in. Workbook paths
        # point at a single page, so a chapter's introduction and its index
        # match no lab at all and would stay readable while every graded page
        # in the same week is held back.
        chapter = prefix.rstrip("/").rsplit("/", 1)[0] + "/"
        if chapter.count("/") >= 3 and wiki_path.startswith(chapter):
            lab_ids.append(lab.id)
    if not lab_ids:
        return

    rows = db.query(Assignment).join(
        AssignmentLab, AssignmentLab.assignment_id == Assignment.id
    ).filter(AssignmentLab.lab_id.in_(lab_ids)).all()
    if not rows:
        return

    now = datetime.now(timezone.utc)
    for asn in rows:
        if asn.locked:
            continue
        start = asn.start_date
        if start is None:
            return                      # unscheduled assignment: nothing to hold
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if start <= now:
            return                      # at least one assignment has opened
    raise HTTPException(
        status_code=403,
        detail="This workbook opens when its assignment does.",
    )


def _normalize_wiki_path(original_uri: str) -> str:
    """Reduce an X-Original-URI to the space that ``Lab.workbook`` is stored in.

    Workbook paths are recorded inconsistently across the lab catalogue: most
    rows carry a leading ``wiki/`` segment (``wiki/range/<track>/CH_.../00_X/``)
    while older rows store the bare chapter path (``CH_COURSE01_.../01_Y/``).
    Requests arrive as ``/wiki/<rest>`` or ``/wiki-<id>/<rest>``.  Both sides
    get reduced to ``<rest>`` here so a prefix comparison is meaningful.

    Returning "" means the URI is not a wiki path at all.
    """
    path = original_uri.split("?", 1)[0].split("#", 1)[0]
    if not path.startswith("/wiki"):
        return ""
    path = path.lstrip("/")
    # Drop the routing prefix: "wiki/", "wiki-oscp/", "wiki-1234/", ...
    first, sep, rest = path.partition("/")
    if not sep or not (first == "wiki" or first.startswith("wiki-")):
        return ""
    # Some rows keep a redundant leading "wiki/" of their own.
    if rest.startswith("wiki/"):
        rest = rest[len("wiki/"):]
    return rest


def _normalize_workbook(workbook: str) -> str:
    """Reduce a stored ``Lab.workbook`` value to the same space as above."""
    wb = (workbook or "").strip().lstrip("/")
    if wb.startswith("wiki/"):
        wb = wb[len("wiki/"):]
    return wb


@router.get("/wiki-released")
async def wiki_released_chapters(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Chapter directories of a course wiki this user may open right now.

    Feeds the workbook's own navigation so a learner is not shown links that
    the release gate will refuse. Purely cosmetic: /wiki-access is still the
    enforcement point, and hiding a link protects nothing on its own.

    Returns every chapter when the caller is staff or the course has no
    schedule, which matches the gate's permissive default.

    Authenticates from the ``wiki_auth`` cookie as well as a bearer header.
    The caller is a script running inside a workbook page, which carries the
    wiki cookie and no Authorization header; nginx only rewrites that cookie
    into a bearer for its internal auth_request locations, not for /api. Taking
    the header alone made this 401 for every learner, and since the script fails
    open the navigation then listed every chapter as though nothing was gated.
    """
    token = ""
    header = request.headers.get("Authorization", "")
    if header.lower().startswith("bearer "):
        token = header.split(" ", 1)[1].strip()
    if not token:
        token = request.cookies.get("wiki_auth", "")
    if not token:
        # Unauthenticated: reveal nothing, and let the caller leave the nav be.
        return {"all": True, "chapters": []}
    try:
        payload = _decode_token(token)
        current_user = get_user_by_username(db, payload.get("sub"))
    except HTTPException:
        return {"all": True, "chapters": []}
    if not current_user or not getattr(current_user, "is_active", True):
        return {"all": True, "chapters": []}

    course = db.query(Course).filter(Course.wiki_slug == slug).first()
    if not course:
        return {"all": True, "chapters": []}

    staff = current_user.role == "admin" or course.instructor_id == current_user.id
    if staff:
        return {"all": True, "chapters": []}

    prefix = f"course/{slug}/"
    labs = db.query(Lab).filter(Lab.workbook.isnot(None), Lab.workbook != "").all()
    released, seen_any = set(), False
    now = datetime.now(timezone.utc)
    for lab in labs:
        p = _normalize_wiki_path("/" + lab.workbook.lstrip("/")) or \
            _normalize_wiki_path("/wiki/" + lab.workbook.lstrip("/"))
        if not p or not p.startswith(prefix):
            continue
        chapter = p[len(prefix):].split("/", 1)[0]
        if not chapter:
            continue
        rows = db.query(Assignment).join(
            AssignmentLab, AssignmentLab.assignment_id == Assignment.id
        ).filter(AssignmentLab.lab_id == lab.id).all()
        if not rows:
            released.add(chapter)
            continue
        seen_any = True
        for asn in rows:
            if asn.locked:
                continue
            start = asn.start_date
            if start is None:
                released.add(chapter)
                break
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if start <= now:
                released.add(chapter)
                break
    if not seen_any:
        return {"all": True, "chapters": []}
    return {"all": False, "chapters": sorted(released)}


@router.get("/wiki-access")
async def check_wiki_access(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_active_user)
):
    """Validate wiki access for a specific path.

    Nginx sends the original URI via X-Original-URI header.  Course-specific
    chapters (``/wiki/course/<slug>/...``, or any path that resolves to a lab
    with visibility='course') require the user to be enrolled in, or to be
    instructing, a course that assigns that lab.  Any other wiki path is open
    to every authenticated user.

    Returns 200 if allowed, raises 403 if denied.
    """
    original_uri = request.headers.get("X-Original-URI", "")

    # Admins always pass
    if current_user.role == "admin":
        return {"status": "ok"}

    # ── Per-course wiki paths: /wiki/course/<slug>/... ──
    # Check enrollment in the specific course identified by its wiki_slug.
    if original_uri.startswith("/wiki/course/"):
        parts = original_uri.split("/", 5)  # ['', 'wiki', 'course', '<slug>', ...]
        if len(parts) >= 4:
            course_slug = parts[3]
            course = db.query(Course).filter(Course.wiki_slug == course_slug).first()
            if course:
                # Instructors of this course always pass
                if course.instructor_id == current_user.id:
                    return {"status": "ok"}
                # Check enrollment + course active
                enrollment = db.query(CourseEnrollment).filter(
                    CourseEnrollment.course_id == course.id,
                    CourseEnrollment.user_id == current_user.id,
                ).first()
                if not enrollment:
                    raise HTTPException(status_code=403, detail="Course enrollment required")
                now = datetime.now(timezone.utc)
                course_end = course.end_date
                if course_end.tzinfo is None:
                    course_end = course_end.replace(tzinfo=timezone.utc)
                if not course.is_active or course_end < now:
                    raise HTTPException(status_code=403, detail="Course is not active")
                _require_workbook_released(db, current_user, original_uri)
                return {"status": "ok"}
        # Course not found or malformed path — deny
        raise HTTPException(status_code=403, detail="Course not found")

    # ── Track and legacy wiki paths: /wiki/range/<track>/..., /wiki-NNNN/... ──
    # Both the request URI and the stored workbook get normalized into the
    # same space first, so a leading-slash difference cannot make a lookup
    # come up empty and fall through to the permissive return below.
    wiki_path = _normalize_wiki_path(original_uri)

    # Check if this path belongs to a course-visibility lab
    if wiki_path:
        # Find labs whose workbook path is a prefix of the requested path
        course_labs = db.query(Lab).filter(
            Lab.workbook.isnot(None),
            Lab.visibility == "course",
        ).all()

        # Multiple labs may share the same workbook path (e.g. a pen-test
        # lab reused across courses).  Grant access if the user is enrolled
        # in ANY course that assigns a matching lab.
        matching_labs = [
            lab for lab in course_labs
            if _normalize_workbook(lab.workbook)
            and wiki_path.startswith(_normalize_workbook(lab.workbook))
        ]
        if matching_labs:
            now = datetime.now(timezone.utc)
            matching_ids = [lab.id for lab in matching_labs]
            has_access = db.query(CourseLabAssignment.id).join(
                Course, Course.id == CourseLabAssignment.course_id
            ).outerjoin(
                CourseEnrollment,
                (CourseEnrollment.course_id == Course.id) &
                (CourseEnrollment.user_id == current_user.id)
            ).filter(
                CourseLabAssignment.lab_id.in_(matching_ids),
                (
                    (CourseEnrollment.id.isnot(None) & (Course.end_date >= now) & (Course.is_active == True)) |
                    (Course.instructor_id == current_user.id)
                )
            ).first()

            if not has_access:
                raise HTTPException(status_code=403, detail="Course enrollment required")

    return {"status": "ok"}




@router.get("/wiki-admin-access")
async def check_wiki_admin_access(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Validate admin-only wiki access.

    Used by nginx auth_request for /wiki-admin/ paths.
    Returns 200 if the user is an admin, raises 403 otherwise.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"status": "ok"}


@router.post("/change-password")
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Change user password - rate limited to 5 per minute"""
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new password matches confirm password
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match"
        )
    
    # Validate new password meets requirements. The shared helper uses
    # Unicode-aware letter/digit classes, rejects control characters, and
    # rejects common bases, account-specific words, repeats, and sequences.
    basic_policy_error = _password_policy_error(
        password_data.new_password,
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
    )
    if basic_policy_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=basic_policy_error
        )

    # Stricter policy for privileged accounts
    if current_user.role in ('instructor', 'admin'):
        policy_error = validate_privileged_password(password_data.new_password)
        if policy_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=policy_error
            )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    
    # Clear must_change_password flag if set
    if hasattr(current_user, 'must_change_password') and current_user.must_change_password:
        current_user.must_change_password = False
    
    db.commit()

    # A password change invalidates every token that existed beforehand. This
    # closes the window where a stolen token keeps working after the victim
    # rotates their credentials.
    revoke_all_user_tokens(current_user.username)

    logger.info(f"User {current_user.username} changed their password and all sessions were revoked")

    return {
        "message": "Password changed successfully. Please log in again.",
        "reauth_required": True,
    }


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Revoke the presented token so it stops working on every worker.

    Revocation is DB-backed (revoked_tokens table), so a logged-out token is
    dead platform-wide, not just on the worker that handled this request."""
    payload = _decode_token(token)
    jti = payload.get("jti")
    if jti:
        revoke_token(jti, float(payload.get("exp", 0)), user_id=current_user.id)

    # Only SSO-issued tokens redirect to the IdP. A local password login for an
    # SSO-linked account stays on the local logout path.
    post_logout_url = None
    provider_id = payload.get("sso_provider_id")
    if provider_id:
        try:
            from app.services import oidc

            post_logout_url = oidc.build_end_session_url(
                db, current_user, int(provider_id)
            )
        except Exception:
            logger.exception("Could not build the SSO end-session URL")
    return {"message": "Logged out", "post_logout_url": post_logout_url}


# ==================== MFA (TOTP) ====================

class MfaCodeRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=8)


class MfaDisableRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=128)
    code: str = Field(..., min_length=6, max_length=8)


@router.post("/mfa/enroll")
@limiter.limit("5/minute")
async def enroll_mfa(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start TOTP enrollment: generate a secret and return the otpauth URI.

    The secret is stored Fernet-encrypted; mfa_enabled stays False until the
    user proves possession via /mfa/verify. Re-calling before verification
    rotates the pending secret."""
    if getattr(current_user, "mfa_enabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled. Disable it first to re-enroll."
        )

    secret = totp_service.generate_secret()
    current_user.totp_secret = totp_service.encrypt_totp_secret(secret)
    db.commit()

    logger.info(f"User {current_user.username} started MFA enrollment")

    provisioning_uri = totp_service.provisioning_uri(
        secret, current_user.email or current_user.username
    )
    # The QR is generated on the server so the browser never needs a QR
    # library, and the secret is delivered in one authenticated response.
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_data_url = (
        "data:image/png;base64,"
        + base64.b64encode(qr_buffer.getvalue()).decode("ascii")
    )

    return {
        "secret": secret,
        "provisioning_uri": provisioning_uri,
        "qr_data_url": qr_data_url,
        "issuer": totp_service.ISSUER_NAME,
    }


@router.post("/mfa/verify")
@limiter.limit("10/minute")
async def verify_mfa(
    request: Request,
    body: MfaCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Confirm TOTP enrollment with a code from the authenticator app.

    First valid code flips mfa_enabled on; later calls just report state."""
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No MFA enrollment in progress. Call /mfa/enroll first."
        )

    if not totp_service.verify_code(current_user.totp_secret, body.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )

    if not current_user.mfa_enabled:
        current_user.mfa_enabled = True
        db.commit()
        logger.info(f"User {current_user.username} enabled MFA")

    return {"mfa_enabled": True}


@router.post("/mfa/disable")
@limiter.limit("5/minute")
async def disable_mfa(
    request: Request,
    body: MfaDisableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Turn MFA off. Requires the account password AND a current TOTP code,
    so a hijacked session alone cannot strip the second factor."""
    if not getattr(current_user, "mfa_enabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )

    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect"
        )

    if not totp_service.verify_code(current_user.totp_secret, body.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )

    current_user.mfa_enabled = False
    current_user.totp_secret = None
    db.commit()

    logger.info(f"User {current_user.username} disabled MFA")

    return {"mfa_enabled": False}


# ==================== Impersonation ====================

@router.post("/impersonate", response_model=ImpersonateResponse)
async def start_impersonation(
    body: ImpersonateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start an impersonation session.

    Modes:
      1. target_user_id set          → impersonate a specific user (admin only)
      2. target_role + course_id set  → synthetic student in a course (admin or instructor-of-course)
      3. target_role only             → generic role view (admin only)
    """
    # Block if already impersonating (no nesting)
    if is_impersonating(current_user):
        raise HTTPException(status_code=403, detail="Cannot impersonate while already impersonating")

    # Must be at least instructor
    if current_user.role not in ('admin', 'instructor'):
        raise HTTPException(status_code=403, detail="Impersonation requires admin or instructor role")

    mode = None
    target_user = None
    target_username = None
    target_role = None
    course_id = body.course_id

    # ── Mode 1: Impersonate specific user ──
    if body.target_user_id is not None:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Only admins can impersonate specific users")

        target_user = db.query(User).filter(User.id == body.target_user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        if target_user.role == 'admin':
            raise HTTPException(status_code=403, detail="Cannot impersonate admin users")

        mode = "user"
        target_username = target_user.username
        target_role = target_user.role

    # ── Mode 2/3: Synthetic role ──
    elif body.target_role is not None:
        target_role = body.target_role

        if course_id is not None:
            # Mode 2: role + course
            mode = "role_course"
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            # Instructors can only preview their own courses
            if current_user.role == 'instructor' and course.instructor_id != current_user.id:
                raise HTTPException(status_code=403, detail="You can only preview your own courses")

            # Instructors can only impersonate as student
            if current_user.role == 'instructor' and target_role != 'student':
                raise HTTPException(status_code=403, detail="Instructors can only view as student")

            target_username = f"_preview_{current_user.username}"
        else:
            # Mode 3: global role (admin only)
            if current_user.role != 'admin':
                raise HTTPException(status_code=403, detail="Only admins can impersonate a global role")
            mode = "role_global"
            target_username = f"_preview_{current_user.username}"
    else:
        raise HTTPException(status_code=400, detail="Must specify target_user_id or target_role")

    # For synthetic modes, we need a real user to back the token.
    # We'll use the original user's record but override the role in the JWT.
    # The frontend and /me endpoint will read imp claims to adjust behavior.
    if mode in ("role_course", "role_global"):
        # Use the current user's username as the sub so get_current_user resolves.
        # The imp claims carry the effective role.
        target_username = current_user.username

    # Create impersonation token
    token = create_impersonation_token(
        original_user=current_user,
        target_username=target_username,
        target_role=target_role,
        mode=mode,
        course_id=course_id,
    )

    # Build response user dicts
    if target_user:
        imp_user = {
            "id": target_user.id,
            "username": target_user.username,
            "email": target_user.email,
            "role": target_user.role,
            "student_id": target_user.student_id,
        }
    else:
        imp_user = {
            "id": current_user.id,
            "username": f"_preview_{current_user.username}",
            "email": current_user.email,
            "role": target_role,
            "student_id": None,
        }

    original = {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }

    # Audit log
    log_activity(
        db, EventTypes.IMPERSONATION_START,
        actor_id=current_user.id,
        target_type="user" if target_user else "role",
        target_id=target_user.id if target_user else None,
        target_label=imp_user["username"],
        detail={
            "mode": mode,
            "target_role": target_role,
            "course_id": course_id,
        },
        ip_address=request.client.host if request.client else None,
    )

    logger.info(
        "Impersonation started: %s -> %s (mode=%s, course=%s)",
        current_user.username, imp_user["username"], mode, course_id,
    )

    return ImpersonateResponse(
        token=token,
        impersonated_user=imp_user,
        original_user=original,
        mode=mode,
        expires_in=3600,
    )


@router.post("/impersonate/exit")
async def exit_impersonation(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Exit impersonation and return a fresh token for the original user."""
    payload = _decode_token(token)

    if not payload.get("imp"):
        raise HTTPException(status_code=400, detail="Not currently impersonating")

    original_id = payload.get("imp_original_id")
    if not original_id:
        raise HTTPException(status_code=400, detail="Invalid impersonation token")

    original_user = db.query(User).filter(User.id == original_id).first()
    if not original_user:
        raise HTTPException(status_code=404, detail="Original user not found")

    # Verify the original user is still an admin/instructor
    if original_user.role not in ('admin', 'instructor'):
        raise HTTPException(status_code=403, detail="Original user no longer has impersonation privileges")

    # Create a fresh standard token for the original user
    fresh_token = create_access_token(
        data={"sub": original_user.username},
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS),
    )

    # Audit log
    log_activity(
        db, EventTypes.IMPERSONATION_END,
        actor_id=original_user.id,
        target_type="user",
        target_id=original_user.id,
        target_label=original_user.username,
        detail={"imp_mode": payload.get("imp_mode")},
        ip_address=request.client.host if request.client else None,
    )

    logger.info("Impersonation ended: %s resumed", original_user.username)

    user_dict = {
        "id": original_user.id,
        "username": original_user.username,
        "email": original_user.email,
        "student_id": original_user.student_id,
        "role": original_user.role,
        "is_admin": original_user.role == 'admin',
        "is_approved": original_user.is_approved,
        "must_change_password": getattr(original_user, 'must_change_password', False),
    }

    return {
        "access_token": fresh_token,
        "token_type": "bearer",
        "user": user_dict,
    }


@router.get("/me/impersonation")
async def get_impersonation_status(
    current_user: User = Depends(get_current_active_user),
):
    """Return impersonation metadata for the current session."""
    if not is_impersonating(current_user):
        return {"impersonating": False}

    return {
        "impersonating": True,
        "original_user": {
            "id": current_user._imp_original_id,
            "username": current_user._imp_original_username,
        },
        "mode": current_user._imp_mode,
        "course_id": current_user._imp_course_id,
        "read_only": current_user._imp_read_only,
    }

