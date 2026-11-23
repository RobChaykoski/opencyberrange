"""Add registration attribution to user accounts.

Revision ID: 0051_registration_attribution
Revises: 0050_child_privacy_defaults
Create Date: 2026-11-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0051_registration_attribution"
down_revision: Union[str, None] = "0050_child_privacy_defaults"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEW_COLUMNS = (
    ("registration_source", "VARCHAR(50)"),
    ("registration_campaign", "VARCHAR(100)"),
)


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    columns = {column["name"] for column in inspector.get_columns("users")}
    for name, ddl in NEW_COLUMNS:
        if name not in columns:
            op.execute(f"ALTER TABLE users ADD COLUMN {name} {ddl}")

    indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_registration_source" not in indexes:
        op.create_index(
            "ix_users_registration_source",
            "users",
            ["registration_source"],
            unique=False,
        )


def downgrade() -> None:
    indexes = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes("users")}
    if "ix_users_registration_source" in indexes:
        op.drop_index("ix_users_registration_source", table_name="users")
    for name, _ddl in reversed(NEW_COLUMNS):
        op.execute(f"ALTER TABLE users DROP COLUMN IF EXISTS {name}")
