"""Add immutable learner report snapshots.

Revision ID: 0031_learner_snapshots
Revises: 0030_cohort_strict
Create Date: 2026-11-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0031_learner_snapshots"
down_revision: Union[str, None] = "0030_cohort_strict"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "learner_snapshots" in inspector.get_table_names():
        return
    op.create_table(
        "learner_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("formula_version", sa.String(length=32), nullable=True),
        sa.Column("weights", sa.Text(), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_learner_snapshots_user_kind",
        "learner_snapshots",
        ["user_id", "kind"],
    )
    op.create_index(
        "ix_learner_snapshots_unique",
        "learner_snapshots",
        ["user_id", "kind", "content_sha256"],
        unique=True,
    )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "learner_snapshots" not in inspector.get_table_names():
        return
    op.drop_index("ix_learner_snapshots_unique", table_name="learner_snapshots")
    op.drop_index("ix_learner_snapshots_user_kind", table_name="learner_snapshots")
    op.drop_table("learner_snapshots")
