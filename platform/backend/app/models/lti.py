"""ORM models for lti."""

from app.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.sql import func


class LtiPlatform(Base):
    """Registered LTI 1.3 platform (one LMS deployment).

    ``issuer`` + ``client_id`` + ``deployment_id`` identify the tenant. The
    token and JWKS endpoints are used for Assignment and Grade Services and
    launch-token verification.
    """

    __tablename__ = "lti_platforms"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    issuer = Column(String(255), nullable=False, index=True)
    client_id = Column(String(255), nullable=False, index=True)
    deployment_id = Column(String(255), nullable=False, index=True)
    auth_login_url = Column(String(500), nullable=False)
    token_url = Column(String(500), nullable=False)
    jwks_url = Column(String(500), nullable=False)
    # Local identity-provider row used for ExternalIdentity links.
    identity_provider_id = Column(
        Integer,
        ForeignKey("identity_providers.id", ondelete="SET NULL"),
        nullable=True,
    )
    # RSA private key for client_assertion, encrypted like provider secrets.
    private_key = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True, server_default=text("true"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "issuer", "client_id", "deployment_id",
            name="uq_lti_platform_deployment",
        ),
    )


class LtiLoginState(Base):
    """Single-use OIDC third-party-initiated login state for LTI 1.3."""

    __tablename__ = "lti_login_states"

    id = Column(Integer, primary_key=True)
    state = Column(String(128), unique=True, nullable=False, index=True)
    platform_id = Column(
        Integer,
        ForeignKey("lti_platforms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nonce = Column(String(128), nullable=False)
    target_link_uri = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    consumed_at = Column(DateTime, nullable=True)


class LtiLink(Base):
    """One LMS resource link launched into the platform.

    The LMS resource-link id is the stable key. AGS endpoints and scopes come
    from the launch claim; ``lab_id`` is filled when the link is mapped to a
    local exercise.
    """

    __tablename__ = "lti_links"

    id = Column(Integer, primary_key=True)
    platform_id = Column(
        Integer,
        ForeignKey("lti_platforms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resource_link_id = Column(String(255), nullable=False, index=True)
    context_id = Column(String(255), nullable=True, index=True)
    context_title = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    ags_lineitem_url = Column(String(500), nullable=True)
    ags_lineitems_url = Column(String(500), nullable=True)
    ags_scopes = Column(Text, nullable=True)
    nrps_url = Column(String(500), nullable=True)
    nrps_versions = Column(Text, nullable=True)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "platform_id", "resource_link_id", name="uq_lti_link_resource"
        ),
    )


class LtiScore(Base):
    """Append-only record of a score passback attempt."""

    __tablename__ = "lti_scores"

    id = Column(Integer, primary_key=True)
    link_id = Column(
        Integer,
        ForeignKey("lti_links.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)
    reason = Column(String(500), nullable=True)
    lms_response = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class LtiRosterMember(Base):
    """Minimum NRPS roster record: LMS subject, role, status, context.

    Names, email addresses, and other directory fields are deliberately not
    stored. The roster is refreshed explicitly by an administrator.
    """

    __tablename__ = "lti_roster_members"

    id = Column(Integer, primary_key=True)
    link_id = Column(
        Integer,
        ForeignKey("lti_links.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_id = Column(
        Integer,
        ForeignKey("lti_platforms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject = Column(String(255), nullable=False)
    roles = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="Active")
    context_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("link_id", "subject", name="uq_lti_roster_member"),
    )


class LtiDeepLinkSession(Base):
    """One Deep Linking 2.0 picker session bound to the launching instructor."""

    __tablename__ = "lti_deep_link_sessions"

    id = Column(Integer, primary_key=True)
    token = Column(String(128), unique=True, nullable=False, index=True)
    platform_id = Column(
        Integer,
        ForeignKey("lti_platforms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    return_url = Column(String(500), nullable=False)
    data = Column(String(500), nullable=True)
    accept_multiple = Column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    nonce = Column(String(128), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    consumed_at = Column(DateTime, nullable=True)
