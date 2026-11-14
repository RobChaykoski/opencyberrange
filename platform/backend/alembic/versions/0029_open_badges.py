"""Add hosted Open Badges 3.0 credentials.

Revision ID: 0029_open_badges
Revises: 0028_course_planning
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0029_open_badges"
down_revision: Union[str, None] = "0028_course_planning"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "open_badge_credentials" in inspector.get_table_names():
        return
    op.create_table(
        "open_badge_credentials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("certificate_id", sa.String(80), nullable=False),
        sa.Column("track_slug", sa.String(100), nullable=False),
        sa.Column(
            "level_id",
            sa.Integer(),
            sa.ForeignKey("levels.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("subject_id", sa.String(64), nullable=False),
        sa.Column("jti", sa.String(64), nullable=False),
        sa.Column("achievement_name", sa.String(200), nullable=False),
        sa.Column("achievement_description", sa.Text(), nullable=True),
        sa.Column("criteria_url", sa.String(500), nullable=True),
        sa.Column("evidence_url", sa.String(500), nullable=True),
        sa.Column(
            "issued_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
        ),
        sa.Column(
            "recipient_name_opt_in",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column(
            "revoked_by_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("revocation_reason", sa.String(500), nullable=True),
        sa.UniqueConstraint("user_id", "certificate_id", name="uq_open_badge_source"),
    )
    op.create_index(
        "ix_open_badge_credentials_user_id", "open_badge_credentials", ["user_id"]
    )
    op.create_index(
        "ix_open_badge_credentials_certificate_id",
        "open_badge_credentials",
        ["certificate_id"],
    )
    op.create_index(
        "ix_open_badge_credentials_subject_id",
        "open_badge_credentials",
        ["subject_id"],
        unique=True,
    )
    op.create_index(
        "ix_open_badge_credentials_jti", "open_badge_credentials", ["jti"], unique=True
    )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "open_badge_credentials" in inspector.get_table_names():
        op.drop_table("open_badge_credentials")
