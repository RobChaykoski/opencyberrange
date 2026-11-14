"""Add pause/resume state to lab sessions.

Revision ID: 0022_lab_pause
Revises: 0021_accommodations
Create Date: 2026-11-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0022_lab_pause"
down_revision: Union[str, None] = "0021_accommodations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("lab_sessions")}
    if "paused_at" not in columns:
        op.add_column("lab_sessions", sa.Column("paused_at", sa.DateTime(), nullable=True))
    if "paused_seconds" not in columns:
        op.add_column(
            "lab_sessions",
            sa.Column(
                "paused_seconds",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )
    if "pause_reason" not in columns:
        op.add_column(
            "lab_sessions", sa.Column("pause_reason", sa.String(500), nullable=True)
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("lab_sessions")}
    if "pause_reason" in columns:
        op.drop_column("lab_sessions", "pause_reason")
    if "paused_seconds" in columns:
        op.drop_column("lab_sessions", "paused_seconds")
    if "paused_at" in columns:
        op.drop_column("lab_sessions", "paused_at")
