"""ORM models for auth."""

from app.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    student_id = Column(String(20), unique=True, index=True, nullable=True)
    first_name = Column(String(80), nullable=True)
    last_name = Column(String(80), nullable=True)
    organization = Column(String(120), nullable=True)
    # Tenant boundary. Institution administrators and every non-system role are
    # confined to this value by the Authorization Service; platform `admin` is
    # the only cross-tenant role and still needs break-glass for private data.
    institution_id = Column(
        String(64),
        nullable=False,
        default="default",
        server_default=text("'default'"),
        index=True,
    )
    # Optional profile avatar as a small base64 data URL (image/png|jpeg|webp).
    # Stored in the row so it survives container rebuilds and needs no shared
    # upload volume; the browser downsizes images before upload.
    avatar_data = deferred(Column(Text, nullable=True))
    # Cosmetic ring around the avatar, used on the profile and celebration wall.
    # Values are #RRGGBB hex colours (or an original named token from an older
    # profile), validated by the settings endpoint before they reach the row.
    avatar_border_style = Column(
        String(20), default="solid", server_default=text("'solid'"), nullable=False
    )
    avatar_border_color = Column(
        String(20), default="blue", server_default=text("'blue'"), nullable=False
    )

    # --- Optional user security/privacy settings ---
    # MFA recovery (backup) codes, stored hashed (JSON array of hashes).
    mfa_recovery_codes = Column(Text, nullable=True)
    # Show this user on public scoreboards / leaderboards. Public visibility is
    # private by default; a learner must opt in. This also keeps school and
    # auto-provisioned accounts private when age is not known.
    show_on_scoreboard = Column(Boolean, default=False, server_default=text("false"), nullable=False)
    # How the user's name appears on public scoreboards / the celebration wall:
    # "real_name", "username", or "anonymous".
    scoreboard_name_mode = Column(
        String(20),
        default="anonymous",
        server_default=text("'anonymous'"),
        nullable=False,
    )
    # Trusted devices (JSON list of {id, name, created_at, last_used}).
    trusted_devices = Column(Text, nullable=True)
    # IANA tz name (e.g. "America/Chicago"); null = UTC.
    timezone = Column(String(64), nullable=True)
    # JSON object of notification toggles.
    notification_prefs = Column(Text, nullable=True)
    # Show hidden/secret badges on the profile. Off by default so a learner is
    # not surprised by a badge they did not know existed.
    show_hidden_achievements = Column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    # Opt-in privacy flag for learners under 18. Reporting and analytics
    # endpoints exclude these accounts; the learner still sees their own work.
    is_minor = Column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    # Privacy-preserving age band. Exact dates of birth are never collected.
    # under_13 | 13_15 | 16_17 | 18_plus. Null means "not stated".
    age_band = Column(String(16), nullable=True)
    # Under-13 accounts are institution-managed. This stores the institution's
    # parental/guardian consent reference, never identity documents.
    parental_consent_reference = Column(String(255), nullable=True)
    parental_consent_recorded_at = Column(DateTime, nullable=True)
    # Set when the account holder acknowledges the privacy notice. Accounts
    # created by an instructor or an identity provider acknowledge on first use.
    privacy_acknowledged_at = Column(DateTime, nullable=True)
    # Registration attribution from conference QR links and campaigns. The
    # source is a short normalized label (gdg, linkedin, swocts, direct, ...);
    # the campaign identifies the specific event or placement.
    registration_source = Column(String(50), nullable=True, index=True)
    registration_campaign = Column(String(100), nullable=True)
    # Allow the public certificate verification page to confirm this account's
    # certificates. Public visibility is off by default; the account holder must
    # opt in. Their own certificate view and PDF still work either way.
    certificates_public = Column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    # Equipped achievement title (key from app.services.titles). Null shows the
    # learner's current Skill DNA class instead.
    equipped_title = Column(String(64), nullable=True)
    # SSO-provisioned accounts cannot use the local password form. Existing
    # local accounts keep their password unless an administrator changes this.
    password_login_disabled = Column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    # Email the user on a new login from a new IP.
    login_notifications = Column(Boolean, default=True, server_default=text("true"), nullable=False)
    # Consent to optional account email. Essential security/service messages may
    # still be sent where required; the version and timestamp make the consent
    # record auditable and support withdrawal under PIPEDA. Optional email is
    # opt-in, including for auto-provisioned SSO/LTI accounts.
    email_notifications = Column(Boolean, default=False, server_default=text("false"), nullable=False)
    email_consent_version = Column(String(32), nullable=True)
    email_consent_updated_at = Column(DateTime, nullable=True)
    # Consecutive UTC calendar days with a successful sign-in. Kept separately
    # from last_login_at so the dashboard can show a stable streak even when a
    # learner signs in several times in one day.
    login_streak = Column(Integer, default=0, server_default=text("0"), nullable=False)
    last_login_day = Column(Date, nullable=True)
    # --- Optional survey consent (platform/usage surveys only) ---
    # Opt-in is explicit and separate from account creation. The timestamp and
    # statement version make the consent record auditable and support withdrawal.
    survey_opt_in = Column(Boolean, default=False, server_default=text("false"), nullable=False)
    survey_opt_in_at = Column(DateTime, nullable=True)
    survey_consent_version = Column(String(32), nullable=True)
    # Last time the account holder downloaded a copy of their personal data.
    data_exported_at = Column(DateTime, nullable=True)
    # Last successful login metadata (for session awareness).
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(64), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Kept for backward compat; derived from role
    role = Column(String(20), default="student", nullable=False)  # student | instructor | admin
    is_approved = Column(Boolean, default=False)

    # Account locking
    is_locked = Column(Boolean, default=False)
    failed_attempts = Column(Integer, default=0)
    locked_at = Column(DateTime, nullable=True)

    # VPN registration status
    vpn_registered = Column(Boolean, default=False)

    # Force password change on next login
    must_change_password = Column(Boolean, default=False, nullable=True)

    # Diagnostic mode: activity events before this timestamp are tagged as diagnostic
    diagnostic_until = Column(DateTime, nullable=True)

    # MFA (TOTP). totp_secret stays null until the user enrolls; sized for an
    # encrypted-at-rest secret, not just the raw base32 value.
    totp_secret = Column(String(255), nullable=True)
    mfa_enabled = Column(Boolean, default=False, server_default=text("false"), nullable=False)
    # MFA brute-force throttling. These are separate from password lockout so a
    # stolen password cannot exhaust the account lockout counter with bad TOTP
    # codes, and a valid password plus bad MFA codes has its own delay.
    mfa_failed_attempts = Column(
        Integer, default=0, server_default=text("0"), nullable=False
    )
    mfa_last_failed_at = Column(DateTime, nullable=True)
    mfa_locked_until = Column(DateTime, nullable=True)
    # Recovery-code lifecycle. The hashes remain in mfa_recovery_codes; this
    # timestamp lets the platform expire and rotate the set.
    mfa_recovery_generated_at = Column(DateTime, nullable=True)
    # Last time the stored password hash was rehashed with current Argon2id
    # parameters. Null means "unknown; rehash on the next successful login".
    password_rehashed_at = Column(DateTime, nullable=True)
    # Monotonic security version. Role, tenant, password, or MFA changes bump
    # it; access tokens carry the version they were minted with, so a stale
    # token cannot retain old authority.
    security_version = Column(
        Integer, nullable=False, default=1, server_default=text("1")
    )

    created_at = Column(DateTime, server_default=func.now())

    @property
    def is_instructor(self):
        """True if user has instructor or admin role."""
        return self.role in ('instructor', 'admin')

    @property
    def display_name(self):
        """Name shown to people: full name when provided, else username.

        Certificates and other human-facing output use this instead of the
        login handle. Either name part is enough; whitespace-only values are
        treated as missing so a blank profile field cannot print as " ".
        """
        parts = [
            part.strip()
            for part in (self.first_name, self.last_name)
            if part and part.strip()
        ]
        return " ".join(parts) if parts else self.username

    @property
    def scoreboard_name(self):
        """Name to publish on the celebration wall / leaderboards.

        Users choose between their real name, their login handle, or a neutral
        anonymous label. Unknown/legacy values fall back to the real name so a
        missing migration cannot hide everyone.
        """
        if getattr(self, "is_minor", False):
            return "Anonymous participant"
        mode = getattr(self, "scoreboard_name_mode", None) or "anonymous"
        if mode == "anonymous":
            return "Anonymous participant"
        if mode == "username":
            return self.username
        return self.display_name

    # Relationships
    sessions = relationship("LabSession", back_populates="user", foreign_keys="[LabSession.user_id]")
    wireguard_config = relationship("WireGuardConfig", back_populates="user", uselist=False)
    completions = relationship("LabCompletion", back_populates="user")
    flag_attempts = relationship("FlagAttempt", back_populates="user")
    instructed_courses = relationship("Course", back_populates="instructor")
    course_enrollments = relationship(
        "CourseEnrollment",
        back_populates="user",
        foreign_keys="CourseEnrollment.user_id",
    )
    achievements = relationship("Achievement", back_populates="user")


class IdentityProvider(Base):
    """V3-only LDAP/SSO identity provider configuration.

    ``config`` holds non-secret provider settings as JSON. ``secrets`` holds an
    encrypted JSON object for bind passwords, client secrets, and private keys.
    Secret values are never returned by the API.
    """
    __tablename__ = "identity_providers"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    kind = Column(String(20), nullable=False)  # ldap, oidc, saml
    enabled = Column(Boolean, default=False, server_default=text("false"), nullable=False)
    is_default = Column(Boolean, default=False, server_default=text("false"), nullable=False)
    config = Column(Text, nullable=False, default="{}", server_default=text("'{}'"))
    secrets = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_identity_provider_name", "name", unique=True),
        Index("ix_identity_provider_kind", "kind"),
    )


class ExternalIdentity(Base):
    """Link a local account to an external IdP subject.

    The provider + subject pair is the stable identity. Email is stored for
    diagnostics only; it is not the key. The unique constraint prevents two
    local accounts from claiming the same external identity.
    """

    __tablename__ = "external_identities"

    id = Column(Integer, primary_key=True)
    provider_id = Column(
        Integer,
        ForeignKey("identity_providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject = Column(String(255), nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login_at = Column(DateTime, nullable=True)

    provider = relationship("IdentityProvider")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("provider_id", "subject", name="uq_external_identity_subject"),
    )


class SsoLoginState(Base):
    """Short-lived login flow state shared by OIDC and SAML.

    Stored in the shared database, not process memory, so any API replica can
    complete the callback. The row is consumed atomically to prevent replay.
    OIDC stores the nonce and PKCE verifier; SAML stores the AuthnRequest ID and
    ACS URL.
    """

    __tablename__ = "sso_login_states"

    id = Column(Integer, primary_key=True)
    state = Column(String(128), unique=True, nullable=False, index=True)
    provider_id = Column(
        Integer,
        ForeignKey("identity_providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nonce = Column(String(128), nullable=False)
    code_verifier = Column(String(128), nullable=False)
    redirect_uri = Column(String(500), nullable=False)
    return_to = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    consumed_at = Column(DateTime, nullable=True)


class SsoLoginTicket(Base):
    """One-time ticket exchanged by the SPA for a platform JWT."""

    __tablename__ = "sso_login_tickets"

    id = Column(Integer, primary_key=True)
    ticket = Column(String(128), unique=True, nullable=False, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_id = Column(
        Integer,
        ForeignKey("identity_providers.id", ondelete="SET NULL"),
        nullable=True,
    )
    return_to = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    consumed_at = Column(DateTime, nullable=True)


class SsoSession(Base):
    """Latest OIDC session per user/provider for RP-initiated logout.

    The ID token is stored encrypted. It is only used as ``id_token_hint`` when
    the user logs out and the provider advertises an end-session endpoint.
    """

    __tablename__ = "sso_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_id = Column(
        Integer,
        ForeignKey("identity_providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_token = Column(Text, nullable=True)
    session_state = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime, nullable=False)

    provider = relationship("IdentityProvider")

    __table_args__ = (
        UniqueConstraint("user_id", "provider_id", name="uq_sso_session_user_provider"),
    )


class RevokedToken(Base):
    """DB-backed JWT revocation list. A token whose jti appears here is dead
    regardless of its exp claim. Rows can be purged once revoked_at is older
    than the JWT lifetime."""
    __tablename__ = "revoked_tokens"

    jti = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    revoked_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_revoked_tokens_user', 'user_id'),
        Index('ix_revoked_at', 'revoked_at'),
    )


class AuthSession(Base):
    """Server-side login session bound to one tenant.

    Access tokens carry the session id. The tenant is captured at login and
    re-checked on every request, so moving an account between institutions
    invalidates its existing sessions instead of silently changing their scope.
    """

    __tablename__ = "auth_sessions"

    id = Column(String(36), primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    institution_id = Column(String(64), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_seen_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(String(64), nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(300), nullable=True)
    mfa_verified_at = Column(DateTime, nullable=True)
    reauth_at = Column(DateTime, nullable=True)
    created_by = Column(String(32), nullable=True)

    __table_args__ = (
        Index("ix_auth_sessions_user_active", "user_id", "revoked_at", "expires_at"),
        Index("ix_auth_sessions_institution", "institution_id"),
    )


class RefreshToken(Base):
    """Rotating opaque refresh token. Only its SHA-256 hash is stored.

    A token belongs to a session and a rotation family. Presenting a token that
    has already been rotated is treated as theft: the whole family and its
    session are revoked.
    """

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    jti = Column(String(64), unique=True, nullable=False, index=True)
    session_id = Column(
        String(36),
        ForeignKey("auth_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    family_id = Column(String(36), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, index=True)
    institution_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    rotated_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    replaced_by_jti = Column(String(64), nullable=True)
    reuse_detected_at = Column(DateTime, nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(300), nullable=True)

    __table_args__ = (
        Index("ix_refresh_tokens_family_active", "family_id", "revoked_at"),
        Index("ix_refresh_tokens_session", "session_id"),
    )


class WebSocketTicket(Base):
    """Single-use ticket for a RangeBox WebSocket handshake."""

    __tablename__ = "ws_tickets"

    ticket = Column(String(64), primary_key=True)
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    __table_args__ = (Index("idx_ws_tickets_expires", "expires_at"),)


class InviteCode(Base):
    """Invite-gated registration. A code is single-use; email, when set,
    pins the code to one address."""
    __tablename__ = "invite_codes"

    code = Column(String(64), primary_key=True)
    email = Column(String(100), nullable=True)  # optional: restrict code to this address
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    used_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class ImpersonationSession(Base):
    """Server-side record of an impersonation token for audit and live status."""

    __tablename__ = "impersonation_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(64), nullable=False, unique=True, index=True)
    actor_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    actor_username = Column(String(120), nullable=False)
    target_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    target_username = Column(String(120), nullable=True)
    mode = Column(String(30), nullable=False)
    course_id = Column(
        Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True
    )
    read_only = Column(Boolean, default=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    started_at = Column(DateTime, server_default=func.now(), index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)
    end_reason = Column(String(30), nullable=True)


class UserAccommodation(Base):
    """Per-student accessibility accommodation.

    A single row per learner: the multiplier applies to timed lab sessions and
    the extension applies to course assignment due dates. Changes are appended
    to ``accommodation_events`` so the reason and actor remain auditable.
    """

    __tablename__ = "user_accommodations"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    time_multiplier = Column(Float, nullable=False, default=1.0, server_default="1")
    due_date_extension_days = Column(
        Integer, nullable=False, default=0, server_default="0"
    )
    notes = Column(String(500), nullable=True)
    updated_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AccommodationEvent(Base):
    """Append-only record of accommodation changes."""

    __tablename__ = "accommodation_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action = Column(String(20), nullable=False)
    time_multiplier = Column(Float, nullable=True)
    due_date_extension_days = Column(Integer, nullable=True)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class InstructorApiKey(Base):
    """A saved LLM provider connection for AI generation (BYO).

    An instructor may have several profiles (e.g. a hosted key and a local
    Ollama endpoint); one is marked is_default. The plaintext key is never
    stored or logged, only the Fernet-encrypted token (see app.crypto). Local
    providers such as Ollama carry a base_url and no key, so encrypted_key is
    nullable. The legacy table name is kept; think of each row as a provider
    profile, not strictly an API key.
    """
    __tablename__ = "instructor_api_keys"

    id = Column(Integer, primary_key=True)
    instructor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(30), default="custom", nullable=False)  # a custom or self-hosted provider
    label = Column(String(120), nullable=True)
    base_url = Column(Text, nullable=True)          # OpenAI-compatible endpoint (Ollama/vLLM/OpenAI)
    model = Column(String(120), nullable=True)
    encrypted_key = Column(Text, nullable=True)     # nullable: Ollama needs no key
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
