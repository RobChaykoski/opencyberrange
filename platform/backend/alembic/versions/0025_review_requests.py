"""Add human review requests for deterministic results.

Revision ID: 0025_review_requests
Revises: 0024_retention
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0025_review_requests"
down_revision: Union[str, None] = "0024_retention"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "review_requests" in inspector.get_table_names():
        return
    op.create_table(
        "review_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            sa.Integer(),
            sa.ForeignKey("courses.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "lab_id",
            sa.Integer(),
            sa.ForeignKey("labs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("source", sa.String(30), nullable=False, server_default="flag"),
        sa.Column("reason", sa.String(1000), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column(
            "rule_version",
            sa.String(50),
            nullable=False,
            server_default="deterministic-v1",
        ),
        sa.Column("primary_factors", sa.Text(), nullable=True),
        sa.Column("decision_note", sa.String(1000), nullable=True),
        sa.Column(
            "decided_by_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "requested_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("now()"),
        ),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_review_requests_user_id", "review_requests", ["user_id"])
    op.create_index("ix_review_requests_course_id", "review_requests", ["course_id"])
    op.create_index("ix_review_requests_lab_id", "review_requests", ["lab_id"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "review_requests" in inspector.get_table_names():
        op.drop_table("review_requests")
