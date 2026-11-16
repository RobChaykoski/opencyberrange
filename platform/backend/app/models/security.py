"""Security event store, RBAC tables, break-glass, and portfolio share tokens.

The security event store is append-only. PostgreSQL row-level security is
applied by :mod:`app.services.security_events` so UPDATE and DELETE affect no
rows even for the table owner; the application only inserts and reads.

RBAC tables let an institution review and adjust role grants without a code
change. The static catalog in ``permissions.yaml`` remains the seed and the
deny-by-default baseline.
"""

from __future__ import annotations

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

from app.database import Base


class SecurityEvent(Base):
    """One security, audit, or privacy event.

    ``detail`` is a redacted JSON object. Callers must never put passwords,
    tokens, keys, or raw private payloads in it; the service redacts obvious
    secret keys as a second line of defence.
    """

    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True)
    occurred_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    category = Column(String(16), nullable=False, index=True)  # security|audit|privacy
    event_type = Column(String(80), nullable=False, index=True)
    severity = Column(String(16), nullable=False, default="info", server_default="info")
    outcome = Column(String(16), nullable=False, default="success", server_default="success")
    action = Column(String(120), nullable=True)
    actor_id = Column(Integer, nullable=True, index=True)
    actor_username = Column(String(120), nullable=True)
    actor_role = Column(String(32), nullable=True)
    # Null is a platform-wide event; a value is an institution-scoped event.
    institution_id = Column(String(64), nullable=True, index=True)
    target_type = Column(String(40), nullable=True)
    target_id = Column(String(64), nullable=True)
    target_label = Column(String(200), nullable=True)
    resource = Column(String(300), nullable=True)
    method = Column(String(10), nullable=True)
    path = Column(String(300), nullable=True)
    status_code = Column(Integer, nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(300), nullable=True)
    request_id = Column(String(64), nullable=True)
    detail = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_security_events_category_time", "category", "occurred_at"),
        Index("ix_security_events_type_time", "event_type", "occurred_at"),
        Index("ix_security_events_actor_time", "actor_id", "occurred_at"),
        Index("ix_security_events_institution_time", "institution_id", "occurred_at"),
        Index("ix_security_events_severity_time", "severity", "occurred_at"),
    )


class RbacRole(Base):
    """A named role. ``User.role`` stays the primary assignment."""

    __tablename__ = "rbac_roles"

    id = Column(Integer, primary_key=True)
    key = Column(String(32), unique=True, nullable=False, index=True)
    label = Column(String(80), nullable=False)
    description = Column(Text, nullable=True)
    rank = Column(Integer, nullable=False, default=100, server_default=text("100"))
    is_system = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    permissions = relationship(
        "RbacPermission", secondary="rbac_role_permissions", lazy="selectin"
    )


class RbacPermission(Base):
    """The persisted permission catalog, seeded from ``permissions.yaml``."""

    __tablename__ = "rbac_permissions"

    id = Column(Integer, primary_key=True)
    key = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(40), nullable=True, index=True)
    sensitivity = Column(String(16), nullable=False, default="medium", server_default="medium")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class RbacRolePermission(Base):
    """Explicit role-to-permission grant."""

    __tablename__ = "rbac_role_permissions"

    role_id = Column(
        Integer,
        ForeignKey("rbac_roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id = Column(
        Integer,
        ForeignKey("rbac_permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )


class RbacUserRole(Base):
    """An additional role for a user, optionally expiring.

    ``User.role`` remains the base role. These rows add scoped capability, for
    example a privacy officer rotating into a review role for one week.
    """

    __tablename__ = "rbac_user_roles"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_key = Column(
        String(32), ForeignKey("rbac_roles.key", ondelete="CASCADE"), nullable=False
    )
    institution_id = Column(String(64), nullable=True, index=True)
    granted_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "role_key", name="uq_rbac_user_role"),
        Index("ix_rbac_user_roles_user_expiry", "user_id", "expires_at"),
    )


class BreakGlassGrant(Base):
    """Time-bound emergency access to one sensitive permission.

    A grant never changes the user's role. The Authorization Service checks it
    only after the normal policy denies, and every use is written to the
    security event store.
    """

    __tablename__ = "break_glass_grants"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    permission = Column(String(120), nullable=False, index=True)
    scope_user_id = Column(Integer, nullable=True, index=True)
    scope_course_id = Column(Integer, nullable=True, index=True)
    reason = Column(Text, nullable=False)
    reference = Column(String(120), nullable=True)  # incident/ticket identifier
    status = Column(
        String(16), nullable=False, default="pending", server_default="pending"
    )  # pending|active|revoked|expired
    requested_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    approved_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_used_at = Column(DateTime, nullable=True)
    use_count = Column(Integer, nullable=False, default=0, server_default=text("0"))
    review_status = Column(
        String(16), nullable=False, default="pending", server_default="pending"
    )  # pending|reviewed
    reviewed_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at = Column(DateTime, nullable=True)
    review_note = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_break_glass_user_status", "user_id", "status"),
        Index("ix_break_glass_permission_status", "permission", "status"),
    )


class ServiceCredential(Base):
    """A hashed bearer credential for a non-human service identity.

    The service principal is a normal ``User`` with role ``service_account`` and
    no password login. Its permissions come from the explicit ``scopes`` list,
    never from a shared administrator account. The raw token is returned once.
    """

    __tablename__ = "service_credentials"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(120), nullable=False)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    scopes = Column(Text, nullable=False, default="[]", server_default="[]")
    institution_id = Column(String(64), nullable=True, index=True)
    created_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    last_used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        Index("ix_service_credentials_user_created", "user_id", "created_at"),
    )


class PortfolioShare(Base):
    """Bearer share link for a learner portfolio.

    Only the SHA-256 hash of the token is stored. The raw token is returned
    once, at creation. Default life is 30 days; a single-use grant is consumed
    atomically on first successful read.
    """

    __tablename__ = "portfolio_share_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    institution_id = Column(String(64), nullable=True, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    label = Column(String(120), nullable=True)
    audience = Column(String(120), nullable=True)
    created_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    single_use = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    max_uses = Column(Integer, nullable=True)
    use_count = Column(Integer, nullable=False, default=0, server_default=text("0"))
    last_used_at = Column(DateTime, nullable=True)
    last_used_ip = Column(String(64), nullable=True)
    consent_version = Column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_portfolio_share_user_created", "user_id", "created_at"),
    )
