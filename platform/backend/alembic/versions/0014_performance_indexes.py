"""Add indexes for scheduler, revocation-prune, and generation-lease paths.

Revision ID: 0014_performance_indexes
Revises: 0013_achievement_event_metadata
Create Date: 2026-11-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0014_performance_indexes"
down_revision: Union[str, None] = "0013_achievement_event_metadata"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEXES = (
    ("ix_labsession_expires", "lab_sessions", ["status", "expires_at"]),
    ("ix_revoked_at", "revoked_tokens", ["revoked_at"]),
    ("ix_genitem_lease", "exercise_gen_items", ["status", "lease_until"]),
)


def _existing_indexes(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table not in inspector.get_table_names():
        return set()
    return {item["name"] for item in inspector.get_indexes(table)}


def upgrade() -> None:
    for name, table, columns in INDEXES:
        if name not in _existing_indexes(table):
            op.create_index(name, table, columns)


def downgrade() -> None:
    for name, table, _columns in INDEXES:
        if name in _existing_indexes(table):
            op.drop_index(name, table_name=table)
