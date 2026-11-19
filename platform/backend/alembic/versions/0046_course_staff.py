"""Add course staff assignments.

Revision ID: 0046_course_staff
Revises: 0045_nice_framework
Create Date: 2026-11-19

Mentors and teaching assistants need a course-scoped assignment before report
access can be broader than the course owner. The table is tenant-scoped from the
course and the assigned user.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.services import tenant_rls

revision: str = "0046_course_staff"
down_revision: Union[str, None] = "0045_nice_framework"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    if not inspector.has_table("course_staff"):
        op.create_table(
            "course_staff",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "course_id",
                sa.Integer(),
                sa.ForeignKey("courses.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("staff_role", sa.String(24), nullable=False),
            sa.Column(
                "created_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
            sa.UniqueConstraint(
                "course_id", "user_id", "staff_role", name="uq_course_staff_role"
            ),
        )
        op.create_index("ix_course_staff_course_id", "course_staff", ["course_id"])
        op.create_index("ix_course_staff_user_id", "course_staff", ["user_id"])

    if binding.dialect.name == "postgresql":
        tenant_rls.ensure_tenant_schema(binding)
        tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    op.drop_table("course_staff")
