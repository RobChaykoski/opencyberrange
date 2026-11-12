"""Add achievement value metadata and the event experience key.

Revision ID: 0013_achievement_event_metadata
Revises: 0012_user_is_minor
Create Date: 2026-11-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0013_achievement_event_metadata"
down_revision: Union[str, None] = "0012_user_is_minor"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table not in inspector.get_table_names():
        return set()
    return {item["name"] for item in inspector.get_columns(table)}


def _indexes(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table not in inspector.get_table_names():
        return set()
    return {item["name"] for item in inspector.get_indexes(table)}


def upgrade() -> None:
    custom_columns = _columns("custom_achievements")
    if "group_key" not in custom_columns:
        op.add_column(
            "custom_achievements",
            sa.Column("group_key", sa.String(30), nullable=False, server_default="custom"),
        )
    if "tier" not in custom_columns:
        op.add_column(
            "custom_achievements",
            sa.Column("tier", sa.String(20), nullable=False, server_default="bronze"),
        )
    if "difficulty" not in custom_columns:
        op.add_column(
            "custom_achievements",
            sa.Column("difficulty", sa.String(20), nullable=False, server_default="standard"),
        )
    if "points" not in custom_columns:
        op.add_column(
            "custom_achievements",
            sa.Column("points", sa.Integer(), nullable=False, server_default="10"),
        )

    competition_columns = _columns("competitions")
    if "experience_key" not in competition_columns:
        op.add_column(
            "competitions",
            sa.Column("experience_key", sa.String(40), nullable=True),
        )
    if "ix_competitions_experience_key" not in _indexes("competitions"):
        op.create_index(
            "ix_competitions_experience_key",
            "competitions",
            ["experience_key"],
        )


def downgrade() -> None:
    if "ix_competitions_experience_key" in _indexes("competitions"):
        op.drop_index("ix_competitions_experience_key", table_name="competitions")
    if "experience_key" in _columns("competitions"):
        op.drop_column("competitions", "experience_key")

    custom_columns = _columns("custom_achievements")
    for column in ("points", "difficulty", "tier", "group_key"):
        if column in custom_columns:
            op.drop_column("custom_achievements", column)
