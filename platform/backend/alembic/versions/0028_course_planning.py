"""Add course cohorts, exercise sets, and requirements.

Revision ID: 0028_course_planning
Revises: 0027_system_metrics
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0028_course_planning"
down_revision: Union[str, None] = "0027_system_metrics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())

    if "course_cohorts" not in tables:
        op.create_table(
            "course_cohorts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "course_id",
                sa.Integer(),
                sa.ForeignKey("courses.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("description", sa.String(500), nullable=True),
            sa.Column(
                "created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
            ),
            sa.UniqueConstraint("course_id", "name", name="uq_course_cohort_name"),
        )
        op.create_index("ix_course_cohorts_course_id", "course_cohorts", ["course_id"])

    if "course_cohort_members" not in tables:
        op.create_table(
            "course_cohort_members",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "cohort_id",
                sa.Integer(),
                sa.ForeignKey("course_cohorts.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "cohort_id", "user_id", name="uq_course_cohort_member"
            ),
        )
        op.create_index(
            "ix_course_cohort_members_cohort_id",
            "course_cohort_members",
            ["cohort_id"],
        )
        op.create_index(
            "ix_course_cohort_members_user_id", "course_cohort_members", ["user_id"]
        )

    if "exercise_sets" not in tables:
        op.create_table(
            "exercise_sets",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "course_id",
                sa.Integer(),
                sa.ForeignKey("courses.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("description", sa.String(500), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column(
                "created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
            ),
            sa.UniqueConstraint("course_id", "name", name="uq_exercise_set_name"),
        )
        op.create_index("ix_exercise_sets_course_id", "exercise_sets", ["course_id"])

    if "exercise_set_items" not in tables:
        op.create_table(
            "exercise_set_items",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "set_id",
                sa.Integer(),
                sa.ForeignKey("exercise_sets.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "lab_id",
                sa.Integer(),
                sa.ForeignKey("labs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column(
                "required", sa.Boolean(), nullable=False, server_default=sa.true()
            ),
            sa.UniqueConstraint("set_id", "lab_id", name="uq_exercise_set_item"),
        )
        op.create_index(
            "ix_exercise_set_items_set_id", "exercise_set_items", ["set_id"]
        )
        op.create_index(
            "ix_exercise_set_items_lab_id", "exercise_set_items", ["lab_id"]
        )

    if "course_requirements" not in tables:
        op.create_table(
            "course_requirements",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "course_id",
                sa.Integer(),
                sa.ForeignKey("courses.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "cohort_id",
                sa.Integer(),
                sa.ForeignKey("course_cohorts.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "set_id",
                sa.Integer(),
                sa.ForeignKey("exercise_sets.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "rule_type", sa.String(20), nullable=False, server_default="complete_all"
            ),
            sa.Column("threshold", sa.Integer(), nullable=True),
            sa.Column("due_at", sa.DateTime(), nullable=True),
            sa.Column("note", sa.String(500), nullable=True),
            sa.Column(
                "created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
            ),
        )
        op.create_index(
            "ix_course_requirements_course_id", "course_requirements", ["course_id"]
        )
        op.create_index(
            "ix_course_requirements_cohort_id", "course_requirements", ["cohort_id"]
        )
        op.create_index(
            "ix_course_requirements_set_id", "course_requirements", ["set_id"]
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = inspector.get_table_names()
    for table in (
        "course_requirements",
        "exercise_set_items",
        "exercise_sets",
        "course_cohort_members",
        "course_cohorts",
    ):
        if table in tables:
            op.drop_table(table)
