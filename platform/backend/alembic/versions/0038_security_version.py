"""Security version for token invalidation on authority changes.

Revision ID: 0038_security_version
Revises: 0037_auth_lifecycle
Create Date: 2026-11-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0038_security_version"
down_revision: Union[str, None] = "0037_auth_lifecycle"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "security_version" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "security_version",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("1"),
            ),
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "security_version" in columns:
        op.drop_column("users", "security_version")
