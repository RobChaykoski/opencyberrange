"""Instructor readiness workflow records.

Revision ID: 0042_readiness_workflow
Revises: 0041_tenant_rls_legacy
Create Date: 2026-11-19

Adds append-only context, support-action, flag-state, and lab-review records.
Tenant columns and RLS are applied by the same helper used by earlier
learner-owned tables.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.services import tenant_rls

revision: str = "0042_readiness_workflow"
down_revision: Union[str, None] = "0041_tenant_rls_legacy"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "readiness_student_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.String(64), nullable=True, server_default="default"),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("learner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(24), nullable=False),
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column("state", sa.String(24), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("start_at", sa.DateTime(), nullable=True),
        sa.Column("end_at", sa.DateTime(), nullable=True),
        sa.Column("follow_up_at", sa.DateTime(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_readiness_student_notes_course_id", "readiness_student_notes", ["course_id"])
    op.create_index("ix_readiness_student_notes_learner_id", "readiness_student_notes", ["learner_id"])
    op.create_index("ix_readiness_student_notes_kind", "readiness_student_notes", ["kind"])
    op.create_index(
        "ix_readiness_notes_course_learner",
        "readiness_student_notes",
        ["course_id", "learner_id"],
    )

    op.create_table(
        "readiness_lab_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.String(64), nullable=True, server_default="default"),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lab_id", sa.Integer(), sa.ForeignKey("labs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("finding", sa.Text(), nullable=True),
        sa.Column("action", sa.Text(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_readiness_lab_reviews_course_id", "readiness_lab_reviews", ["course_id"])
    op.create_index("ix_readiness_lab_reviews_lab_id", "readiness_lab_reviews", ["lab_id"])
    op.create_index(
        "ix_readiness_lab_reviews_course_lab",
        "readiness_lab_reviews",
        ["course_id", "lab_id"],
    )

    binding = op.get_bind()
    if binding.dialect.name == "postgresql":
        tenant_rls.ensure_tenant_schema(binding)
        tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    op.drop_table("readiness_lab_reviews")
    op.drop_table("readiness_student_notes")
