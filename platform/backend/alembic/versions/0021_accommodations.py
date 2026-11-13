"""Add per-student accessibility accommodations.

Revision ID: 0021_accommodations
Revises: 0020_lti_dl_multiple
Create Date: 2026-11-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0021_accommodations"
down_revision: Union[str, None] = "0020_lti_dl_multiple"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = inspector.get_table_names()
    if "user_accommodations" not in tables:
        op.create_table(
            "user_accommodations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "time_multiplier",
                sa.Float(),
                nullable=False,
                server_default="1",
            ),
            sa.Column(
                "due_date_extension_days",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.Column("notes", sa.String(500), nullable=True),
            sa.Column(
                "updated_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=True,
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=True,
                server_default=sa.text("now()"),
            ),
        )
        op.create_index(
            "ix_user_accommodations_user_id",
            "user_accommodations",
            ["user_id"],
            unique=True,
        )

    if "accommodation_events" not in tables:
        op.create_table(
            "accommodation_events",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "actor_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("action", sa.String(20), nullable=False),
            sa.Column("time_multiplier", sa.Float(), nullable=True),
            sa.Column("due_date_extension_days", sa.Integer(), nullable=True),
            sa.Column("reason", sa.String(500), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=True,
                server_default=sa.text("now()"),
            ),
        )
        op.create_index(
            "ix_accommodation_events_user_id",
            "accommodation_events",
            ["user_id"],
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = inspector.get_table_names()
    if "accommodation_events" in tables:
        op.drop_table("accommodation_events")
    if "user_accommodations" in tables:
        op.drop_table("user_accommodations")
