"""Authentication sessions, refresh tokens, MFA lifecycle, and rehash stamps.

Revision ID: 0037_auth_lifecycle
Revises: 0036_service_identities
Create Date: 2026-11-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0037_auth_lifecycle"
down_revision: Union[str, None] = "0036_service_identities"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    columns = {column["name"] for column in inspector.get_columns("users")}

    user_columns = {
        "mfa_failed_attempts": "INTEGER NOT NULL DEFAULT 0",
        "mfa_last_failed_at": "TIMESTAMP",
        "mfa_locked_until": "TIMESTAMP",
        "mfa_recovery_generated_at": "TIMESTAMP",
        "password_rehashed_at": "TIMESTAMP",
    }
    for name, ddl in user_columns.items():
        if name not in columns:
            op.execute(f"ALTER TABLE users ADD COLUMN {name} {ddl}")

    if "auth_sessions" not in tables:
        op.create_table(
            "auth_sessions",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("institution_id", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("last_seen_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
            sa.Column("revoked_reason", sa.String(length=64), nullable=True),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.Column("user_agent", sa.String(length=300), nullable=True),
            sa.Column("mfa_verified_at", sa.DateTime(), nullable=True),
            sa.Column("reauth_at", sa.DateTime(), nullable=True),
            sa.Column("created_by", sa.String(length=32), nullable=True),
        )
        op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
        op.create_index("ix_auth_sessions_institution_id", "auth_sessions", ["institution_id"])
        op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
        op.create_index(
            "ix_auth_sessions_user_active",
            "auth_sessions",
            ["user_id", "revoked_at", "expires_at"],
        )
        op.create_index("ix_auth_sessions_institution", "auth_sessions", ["institution_id"])

    if "refresh_tokens" not in tables:
        op.create_table(
            "refresh_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("jti", sa.String(length=64), nullable=False, unique=True),
            sa.Column(
                "session_id",
                sa.String(length=36),
                sa.ForeignKey("auth_sessions.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("family_id", sa.String(length=36), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("institution_id", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("rotated_at", sa.DateTime(), nullable=True),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
            sa.Column("replaced_by_jti", sa.String(length=64), nullable=True),
            sa.Column("reuse_detected_at", sa.DateTime(), nullable=True),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.Column("user_agent", sa.String(length=300), nullable=True),
        )
        op.create_index("ix_refresh_tokens_jti", "refresh_tokens", ["jti"])
        op.create_index("ix_refresh_tokens_session_id", "refresh_tokens", ["session_id"])
        op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
        op.create_index("ix_refresh_tokens_family_id", "refresh_tokens", ["family_id"])
        op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])
        op.create_index("ix_refresh_tokens_institution_id", "refresh_tokens", ["institution_id"])
        op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])
        op.create_index(
            "ix_refresh_tokens_family_active",
            "refresh_tokens",
            ["family_id", "revoked_at"],
        )
        op.create_index("ix_refresh_tokens_session", "refresh_tokens", ["session_id"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "refresh_tokens" in tables:
        op.drop_table("refresh_tokens")
    if "auth_sessions" in tables:
        op.drop_table("auth_sessions")
    columns = {column["name"] for column in inspector.get_columns("users")}
    for name in (
        "password_rehashed_at",
        "mfa_recovery_generated_at",
        "mfa_locked_until",
        "mfa_last_failed_at",
        "mfa_failed_attempts",
    ):
        if name in columns:
            op.drop_column("users", name)
