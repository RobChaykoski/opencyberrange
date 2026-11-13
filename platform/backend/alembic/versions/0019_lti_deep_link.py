"""Add LTI Deep Linking picker sessions.

Revision ID: 0019_lti_deep_link
Revises: 0018_lti_roster
Create Date: 2026-11-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0019_lti_deep_link"
down_revision: Union[str, None] = "0018_lti_roster"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "lti_deep_link_sessions" in inspector.get_table_names():
        return
    op.create_table(
        "lti_deep_link_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(128), nullable=False),
        sa.Column(
            "platform_id",
            sa.Integer(),
            sa.ForeignKey("lti_platforms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("return_url", sa.String(500), nullable=False),
        sa.Column("data", sa.String(500), nullable=True),
        sa.Column("nonce", sa.String(128), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_lti_deep_link_sessions_token",
        "lti_deep_link_sessions",
        ["token"],
        unique=True,
    )
    op.create_index(
        "ix_lti_deep_link_sessions_platform_id",
        "lti_deep_link_sessions",
        ["platform_id"],
    )
    op.create_index(
        "ix_lti_deep_link_sessions_user_id",
        "lti_deep_link_sessions",
        ["user_id"],
    )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "lti_deep_link_sessions" in inspector.get_table_names():
        op.drop_table("lti_deep_link_sessions")
