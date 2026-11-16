"""Settings change control and the one-way production cutover.

Revision ID: 0040_settings_change_control
Revises: 0039_db_invariants
Create Date: 2026-11-16
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0040_settings_change_control"
down_revision: Union[str, None] = "0039_db_invariants"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "settings_change_requests" not in tables:
        op.create_table(
            "settings_change_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("ticket_number", sa.Text(), nullable=True),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("environment", sa.String(20), nullable=False, server_default="development"),
            sa.Column("status", sa.String(16), nullable=False, server_default="applied"),
            sa.Column(
                "actor_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("actor_username", sa.String(64), nullable=False),
            sa.Column("before_values", sa.Text(), nullable=False),
            sa.Column("after_values", sa.Text(), nullable=False),
            sa.Column("secret_keys", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("change_hash", sa.String(64), nullable=False),
            sa.Column(
                "applied_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("reverted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("reverted_by_username", sa.String(64), nullable=True),
            sa.Column("revert_reason", sa.Text(), nullable=True),
        )
        op.create_index(
            "ix_settings_change_requests_status",
            "settings_change_requests",
            ["status"],
        )
        op.create_index(
            "ix_settings_change_requests_applied_at",
            "settings_change_requests",
            ["applied_at"],
        )
    if "production_cutovers" not in tables:
        op.create_table(
            "production_cutovers",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "actor_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("actor_username", sa.String(64), nullable=False),
            sa.Column("ticket_number", sa.Text(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "cutover_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("sample_data_summary", sa.Text(), nullable=False),
            sa.Column(
                "password_confirmed",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column("evidence_hash", sa.String(64), nullable=False),
        )
        op.create_index(
            "ix_production_cutovers_cutover_at",
            "production_cutovers",
            ["cutover_at"],
        )
        op.create_index(
            "ix_production_cutovers_evidence_hash",
            "production_cutovers",
            ["evidence_hash"],
        )


def downgrade() -> None:
    op.drop_index("ix_production_cutovers_evidence_hash", table_name="production_cutovers")
    op.drop_index("ix_production_cutovers_cutover_at", table_name="production_cutovers")
    op.drop_table("production_cutovers")
    op.drop_index("ix_settings_change_requests_applied_at", table_name="settings_change_requests")
    op.drop_index("ix_settings_change_requests_status", table_name="settings_change_requests")
    op.drop_table("settings_change_requests")
