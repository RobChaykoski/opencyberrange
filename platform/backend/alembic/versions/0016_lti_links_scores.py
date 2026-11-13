"""Add LTI links and score-passback ledger.

Revision ID: 0016_lti_links_scores
Revises: 0015_lti_platforms
Create Date: 2026-11-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0016_lti_links_scores"
down_revision: Union[str, None] = "0015_lti_platforms"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())

    if "lti_links" not in tables:
        op.create_table(
            "lti_links",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "platform_id",
                sa.Integer(),
                sa.ForeignKey("lti_platforms.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("resource_link_id", sa.String(255), nullable=False),
            sa.Column("context_id", sa.String(255), nullable=True),
            sa.Column("context_title", sa.String(255), nullable=True),
            sa.Column("title", sa.String(255), nullable=True),
            sa.Column("ags_lineitem_url", sa.String(500), nullable=True),
            sa.Column("ags_lineitems_url", sa.String(500), nullable=True),
            sa.Column("ags_scopes", sa.Text(), nullable=True),
            sa.Column(
                "lab_id",
                sa.Integer(),
                sa.ForeignKey("labs.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
            ),
            sa.Column(
                "updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
            ),
            sa.UniqueConstraint(
                "platform_id", "resource_link_id", name="uq_lti_link_resource"
            ),
        )
        op.create_index("ix_lti_links_platform_id", "lti_links", ["platform_id"])
        op.create_index("ix_lti_links_resource_link_id", "lti_links", ["resource_link_id"])
        op.create_index("ix_lti_links_context_id", "lti_links", ["context_id"])

    if "lti_scores" not in tables:
        op.create_table(
            "lti_scores",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "link_id",
                sa.Integer(),
                sa.ForeignKey("lti_links.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "reviewer_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("score", sa.Float(), nullable=False),
            sa.Column("max_score", sa.Float(), nullable=False),
            sa.Column("status", sa.String(20), nullable=False),
            sa.Column("reason", sa.String(500), nullable=True),
            sa.Column("lms_response", sa.Text(), nullable=True),
            sa.Column(
                "created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
            ),
        )
        op.create_index("ix_lti_scores_link_id", "lti_scores", ["link_id"])
        op.create_index("ix_lti_scores_user_id", "lti_scores", ["user_id"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "lti_scores" in tables:
        op.drop_table("lti_scores")
    if "lti_links" in tables:
        op.drop_table("lti_links")
