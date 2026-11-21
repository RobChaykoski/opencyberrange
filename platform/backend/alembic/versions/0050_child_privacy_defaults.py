"""Add age bands, consent references, and private-by-default visibility.

Revision ID: 0050_child_privacy_defaults
Revises: 0049_network_access_rules
Create Date: 2026-11-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0050_child_privacy_defaults"
down_revision: Union[str, None] = "0049_network_access_rules"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEW_COLUMNS = (
    ("age_band", "VARCHAR(16)"),
    ("parental_consent_reference", "VARCHAR(255)"),
    ("parental_consent_recorded_at", "TIMESTAMP"),
    ("privacy_acknowledged_at", "TIMESTAMP"),
)


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    columns = {column["name"] for column in inspector.get_columns("users")}
    for name, ddl in NEW_COLUMNS:
        if name not in columns:
            op.execute(f"ALTER TABLE users ADD COLUMN {name} {ddl}")

    if binding.dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE users ALTER COLUMN show_on_scoreboard SET DEFAULT false"
        )
        op.execute(
            "ALTER TABLE users ALTER COLUMN scoreboard_name_mode SET DEFAULT 'anonymous'"
        )
        op.execute(
            "ALTER TABLE users ALTER COLUMN certificates_public SET DEFAULT false"
        )
        op.execute(
            "ALTER TABLE users ALTER COLUMN email_notifications SET DEFAULT false"
        )

    # A minor account is never publicly visible. This corrective pass is
    # deliberately limited to accounts already marked as minors.
    op.execute(
        "UPDATE users SET show_on_scoreboard = false, "
        "scoreboard_name_mode = 'anonymous', certificates_public = false "
        "WHERE is_minor = true"
    )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE users ALTER COLUMN show_on_scoreboard SET DEFAULT true"
        )
        op.execute(
            "ALTER TABLE users ALTER COLUMN scoreboard_name_mode SET DEFAULT 'real_name'"
        )
        op.execute(
            "ALTER TABLE users ALTER COLUMN certificates_public SET DEFAULT true"
        )
        op.execute(
            "ALTER TABLE users ALTER COLUMN email_notifications SET DEFAULT true"
        )
    for name, _ddl in reversed(NEW_COLUMNS):
        op.execute(f"ALTER TABLE users DROP COLUMN IF EXISTS {name}")
