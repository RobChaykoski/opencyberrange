"""Add NICE mapping review metadata per lab.

Revision ID: 0047_lab_nice_metadata
Revises: 0046_course_staff
Create Date: 2026-11-19

Separates review status and provenance from the selected component rows so a
provisional derivation can be queued for review and a manual edit can mark the
mapping reviewed.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0047_lab_nice_metadata"
down_revision: Union[str, None] = "0046_course_staff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    if inspector.has_table("lab_nice_metadata"):
        return
    op.create_table(
        "lab_nice_metadata",
        sa.Column(
            "lab_id",
            sa.Integer(),
            sa.ForeignKey("labs.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "review_status",
            sa.String(24),
            nullable=False,
            server_default="provisional",
        ),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("confidence", sa.String(16), nullable=True),
        sa.Column("policy_version", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "reviewed_by_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_table("lab_nice_metadata")
