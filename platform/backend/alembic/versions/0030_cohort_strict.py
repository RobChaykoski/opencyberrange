"""Add strict cohort access and default cohort selection.

Revision ID: 0030_cohort_strict
Revises: 0029_open_badges
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0030_cohort_strict"
down_revision: Union[str, None] = "0029_open_badges"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    course_columns = {column["name"] for column in inspector.get_columns("courses")}
    if "cohort_strict" not in course_columns:
        op.add_column(
            "courses",
            sa.Column(
                "cohort_strict",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )
    cohort_columns = {
        column["name"] for column in inspector.get_columns("course_cohorts")
    }
    if "is_default" not in cohort_columns:
        op.add_column(
            "course_cohorts",
            sa.Column(
                "is_default",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    cohort_columns = {
        column["name"] for column in inspector.get_columns("course_cohorts")
    }
    if "is_default" in cohort_columns:
        op.drop_column("course_cohorts", "is_default")
    course_columns = {column["name"] for column in inspector.get_columns("courses")}
    if "cohort_strict" in course_columns:
        op.drop_column("courses", "cohort_strict")
