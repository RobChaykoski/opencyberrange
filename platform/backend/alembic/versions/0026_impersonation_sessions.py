"""Add server-side impersonation session records.

Revision ID: 0026_impersonation_sessions
Revises: 0025_review_requests
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0026_impersonation_sessions"
down_revision: Union[str, None] = "0025_review_requests"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "impersonation_sessions" in inspector.get_table_names():
        return
    op.create_table(
        "impersonation_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(64), nullable=False),
        sa.Column(
            "actor_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("actor_username", sa.String(120), nullable=False),
        sa.Column(
            "target_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("target_username", sa.String(120), nullable=True),
        sa.Column("mode", sa.String(30), nullable=False),
        sa.Column(
            "course_id",
            sa.Integer(),
            sa.ForeignKey("courses.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("read_only", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "started_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("end_reason", sa.String(30), nullable=True),
    )
    op.create_index(
        "ix_impersonation_sessions_session_id",
        "impersonation_sessions",
        ["session_id"],
        unique=True,
    )
    op.create_index(
        "ix_impersonation_sessions_actor_id",
        "impersonation_sessions",
        ["actor_id"],
    )
    op.create_index(
        "ix_impersonation_sessions_target_user_id",
        "impersonation_sessions",
        ["target_user_id"],
    )
    op.create_index(
        "ix_impersonation_sessions_started_at",
        "impersonation_sessions",
        ["started_at"],
    )
    op.create_index(
        "ix_impersonation_sessions_expires_at",
        "impersonation_sessions",
        ["expires_at"],
    )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "impersonation_sessions" in inspector.get_table_names():
        op.drop_table("impersonation_sessions")
