"""Add case ownership and priority to learner readiness notes.

Revision ID: 0044_readiness_case_owner
Revises: 0043_readiness_tenant_fix
Create Date: 2026-11-19

A ``case`` note now carries the current owner, priority, status, and next
follow-up. Owner references are nulled, not deleted, when an instructor
account is erased.

Startup ``create_all`` can create the table and columns before this revision
runs, so each column, foreign key, and index is guarded by an inspector check.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0044_readiness_case_owner"
down_revision: Union[str, None] = "0043_readiness_tenant_fix"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "readiness_student_notes"
FK_NAME = "fk_readiness_student_notes_owner_id_users"
INDEX_NAME = "ix_readiness_student_notes_owner_id"


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    columns = {column["name"] for column in inspector.get_columns(TABLE)}
    foreign_keys = inspector.get_foreign_keys(TABLE)
    indexes = inspector.get_indexes(TABLE)
    has_owner_fk = any(
        fk.get("constrained_columns") == ["owner_id"] for fk in foreign_keys
    )
    has_owner_index = any(
        index.get("column_names") == ["owner_id"] for index in indexes
    )

    with op.batch_alter_table(TABLE) as batch:
        if "owner_id" not in columns:
            batch.add_column(sa.Column("owner_id", sa.Integer(), nullable=True))
        if "priority" not in columns:
            batch.add_column(sa.Column("priority", sa.String(16), nullable=True))
        if not has_owner_fk:
            batch.create_foreign_key(
                FK_NAME,
                "users",
                ["owner_id"],
                ["id"],
                ondelete="SET NULL",
            )
        if not has_owner_index:
            batch.create_index(INDEX_NAME, ["owner_id"])


def downgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    columns = {column["name"] for column in inspector.get_columns(TABLE)}
    foreign_keys = inspector.get_foreign_keys(TABLE)
    indexes = inspector.get_indexes(TABLE)
    has_owner_fk = any(
        fk.get("constrained_columns") == ["owner_id"] for fk in foreign_keys
    )
    has_owner_index = any(
        index.get("column_names") == ["owner_id"] for index in indexes
    )

    with op.batch_alter_table(TABLE) as batch:
        if has_owner_index:
            batch.drop_index(INDEX_NAME)
        if has_owner_fk:
            batch.drop_constraint(FK_NAME, type_="foreignkey")
        if "priority" in columns:
            batch.drop_column("priority")
        if "owner_id" in columns:
            batch.drop_column("owner_id")
