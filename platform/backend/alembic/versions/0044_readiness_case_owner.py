"""Add case ownership and priority to learner readiness notes.

Revision ID: 0044_readiness_case_owner
Revises: 0043_readiness_tenant_fix
Create Date: 2026-11-19

A ``case`` note now carries the current owner, priority, status, and next
follow-up. Owner references are nulled, not deleted, when an instructor
account is erased.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0044_readiness_case_owner"
down_revision: Union[str, None] = "0043_readiness_tenant_fix"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("readiness_student_notes") as batch:
        batch.add_column(sa.Column("owner_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("priority", sa.String(16), nullable=True))
        batch.create_foreign_key(
            "fk_readiness_student_notes_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.create_index("ix_readiness_student_notes_owner_id", ["owner_id"])


def downgrade() -> None:
    with op.batch_alter_table("readiness_student_notes") as batch:
        batch.drop_index("ix_readiness_student_notes_owner_id")
        batch.drop_constraint(
            "fk_readiness_student_notes_owner_id_users",
            type_="foreignkey",
        )
        batch.drop_column("priority")
        batch.drop_column("owner_id")
