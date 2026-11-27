"""Add the TOTP replay guard column.

Revision ID: 0068_mfa_replay_guard
Revises: 0067_course_content_rls
Create Date: 2026-11-26

The last accepted TOTP timestep is stored per user. A code at or below that
step is rejected, so a captured code cannot be replayed within its 30-second
window.
"""

from alembic import op

revision = "0068_mfa_replay_guard"
down_revision = "0067_course_content_rls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS mfa_last_used_step INTEGER"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS mfa_last_used_step")
