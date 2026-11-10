"""Add administrator reviews for unattributed integrity-ledger writes.

Revision ID: 0011_integrity_reviews
Revises: 0010_certificate_visibility
Create Date: 2026-11-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0011_integrity_reviews"
down_revision: Union[str, None] = "0010_certificate_visibility"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _has_table("data_integrity_reviews"):
        return
    op.create_table(
        "data_integrity_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("table_name", sa.String(length=64), nullable=False),
        sa.Column("operation", sa.String(length=8), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("write_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("decision", sa.String(length=24), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column(
            "reviewed_by_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reviewed_by_username", sa.String(length=64), nullable=False),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_data_integrity_reviews_table_name",
        "data_integrity_reviews",
        ["table_name"],
    )


def downgrade() -> None:
    if _has_table("data_integrity_reviews"):
        op.drop_index(
            "ix_data_integrity_reviews_table_name",
            table_name="data_integrity_reviews",
        )
        op.drop_table("data_integrity_reviews")
