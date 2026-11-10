"""Add the under-18 reporting privacy flag to users.

Revision ID: 0012_user_is_minor
Revises: 0011_integrity_reviews
Create Date: 2026-11-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0012_user_is_minor"
down_revision: Union[str, None] = "0011_integrity_reviews"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    if table not in sa.inspect(op.get_bind()).get_table_names():
        return False
    return column in {
        item["name"] for item in sa.inspect(op.get_bind()).get_columns(table)
    }


def upgrade() -> None:
    if not _has_column("users", "is_minor"):
        op.add_column(
            "users",
            sa.Column(
                "is_minor",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )


def downgrade() -> None:
    if _has_column("users", "is_minor"):
        op.drop_column("users", "is_minor")
