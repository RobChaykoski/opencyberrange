"""Add per-course retention clock and run evidence.

Revision ID: 0024_retention
Revises: 0023_minor_consent
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0024_retention"
down_revision: Union[str, None] = "0023_minor_consent"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("courses")}
    if "retention_until" not in columns:
        op.add_column("courses", sa.Column("retention_until", sa.DateTime(), nullable=True))
    if "retention_note" not in columns:
        op.add_column("courses", sa.Column("retention_note", sa.String(500), nullable=True))
    if "retention_set_by_id" not in columns:
        op.add_column("courses", sa.Column("retention_set_by_id", sa.Integer(), nullable=True))
    if "retention_set_at" not in columns:
        op.add_column("courses", sa.Column("retention_set_at", sa.DateTime(), nullable=True))

    if "retention_runs" not in inspector.get_table_names():
        op.create_table(
            "retention_runs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "course_id",
                sa.Integer(),
                sa.ForeignKey("courses.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "actor_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("action", sa.String(20), nullable=False),
            sa.Column("counts", sa.Text(), nullable=True),
            sa.Column("note", sa.String(500), nullable=True),
            sa.Column("reference", sa.String(200), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=True,
                server_default=sa.text("now()"),
            ),
        )
        op.create_index("ix_retention_runs_course_id", "retention_runs", ["course_id"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "retention_runs" in inspector.get_table_names():
        op.drop_table("retention_runs")
    columns = {column["name"] for column in inspector.get_columns("courses")}
    if "retention_set_at" in columns:
        op.drop_column("courses", "retention_set_at")
    if "retention_set_by_id" in columns:
        op.drop_column("courses", "retention_set_by_id")
    if "retention_note" in columns:
        op.drop_column("courses", "retention_note")
    if "retention_until" in columns:
        op.drop_column("courses", "retention_until")
