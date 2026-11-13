"""Add persisted NRPS roster membership records.

Revision ID: 0018_lti_roster
Revises: 0017_lti_nrps
Create Date: 2026-11-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0018_lti_roster"
down_revision: Union[str, None] = "0017_lti_nrps"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "lti_roster_members" in inspector.get_table_names():
        return
    op.create_table(
        "lti_roster_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "link_id",
            sa.Integer(),
            sa.ForeignKey("lti_links.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "platform_id",
            sa.Integer(),
            sa.ForeignKey("lti_platforms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("roles", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="Active"),
        sa.Column("context_id", sa.String(255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
        ),
        sa.UniqueConstraint("link_id", "subject", name="uq_lti_roster_member"),
    )
    op.create_index("ix_lti_roster_members_link_id", "lti_roster_members", ["link_id"])
    op.create_index(
        "ix_lti_roster_members_platform_id", "lti_roster_members", ["platform_id"]
    )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "lti_roster_members" in inspector.get_table_names():
        op.drop_table("lti_roster_members")
