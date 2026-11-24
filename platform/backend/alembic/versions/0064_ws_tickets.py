"""Create the WebSocket ticket table.

Revision ID: 0064_ws_tickets
Revises: 0063_missing_fk_indexes
Create Date: 2026-11-24

The table was previously created by runtime DDL in ``main.py``. The model now
owns it; this migration brings existing databases into the graph without
changing a populated table.
"""

from alembic import op

revision = "0064_ws_tickets"
down_revision = "0063_missing_fk_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TABLE IF NOT EXISTS ws_tickets ("
        " ticket VARCHAR(64) PRIMARY KEY,"
        " user_id INTEGER NOT NULL,"
        " expires_at TIMESTAMP NOT NULL)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_ws_tickets_expires "
        "ON ws_tickets (expires_at)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ws_tickets")
