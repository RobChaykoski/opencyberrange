"""Drop the legacy Kali terminal columns.

Revision ID: 0065_legacy_kali_columns
Revises: 0064_ws_tickets
Create Date: 2026-11-24

The Kali terminal fields predate the RangeBox/Kasm desktop path. No application
code reads them. The columns are nullable and dropping them is a metadata-only
PostgreSQL operation; the downgrade restores the original types.
"""

from alembic import op

revision = "0065_legacy_kali_columns"
down_revision = "0064_ws_tickets"
branch_labels = None
depends_on = None


_COLUMNS = (
    ("lab_sessions", "kali_terminal_url"),
    ("lab_sessions", "kali_container_id"),
    ("lab_sessions", "kali_port"),
    ("lab_sessions", "kali_activity_heartbeat"),
    ("lab_sessions", "kali_last_activity"),
    ("labs", "provides_kali_terminal"),
)


def upgrade() -> None:
    for table, column in _COLUMNS:
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS {column}")


def downgrade() -> None:
    op.execute("ALTER TABLE lab_sessions ADD COLUMN IF NOT EXISTS kali_terminal_url VARCHAR(255)")
    op.execute("ALTER TABLE lab_sessions ADD COLUMN IF NOT EXISTS kali_container_id VARCHAR(100)")
    op.execute("ALTER TABLE lab_sessions ADD COLUMN IF NOT EXISTS kali_port INTEGER")
    op.execute(
        "ALTER TABLE lab_sessions ADD COLUMN IF NOT EXISTS "
        "kali_activity_heartbeat TIMESTAMP"
    )
    op.execute(
        "ALTER TABLE lab_sessions ADD COLUMN IF NOT EXISTS kali_last_activity TIMESTAMP"
    )
    op.execute(
        "ALTER TABLE labs ADD COLUMN IF NOT EXISTS provides_kali_terminal BOOLEAN"
    )
