"""Add a public-certificate verification preference per user.

Revision ID: 0010_certificate_visibility
Revises: 0009_report_exports
Create Date: 2026-11-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0010_certificate_visibility"
down_revision: Union[str, None] = "0009_report_exports"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    if table not in sa.inspect(op.get_bind()).get_table_names():
        return False
    return column in {
        item["name"] for item in sa.inspect(op.get_bind()).get_columns(table)
    }


def upgrade() -> None:
    if not _has_column("users", "certificates_public"):
        op.add_column(
            "users",
            sa.Column(
                "certificates_public",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
        )


def downgrade() -> None:
    if _has_column("users", "certificates_public"):
        op.drop_column("users", "certificates_public")
