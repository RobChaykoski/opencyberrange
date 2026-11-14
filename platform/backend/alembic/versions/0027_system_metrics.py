"""Add sampled host/platform metrics for the admin graphs.

Revision ID: 0027_system_metrics
Revises: 0026_impersonation_sessions
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0027_system_metrics"
down_revision: Union[str, None] = "0026_impersonation_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "system_metrics" in inspector.get_table_names():
        return
    op.create_table(
        "system_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
        ),
        sa.Column("load1", sa.Float(), nullable=True),
        sa.Column("load5", sa.Float(), nullable=True),
        sa.Column("load15", sa.Float(), nullable=True),
        sa.Column("cpu_count", sa.Integer(), nullable=True),
        sa.Column("mem_total_mb", sa.Integer(), nullable=True),
        sa.Column("mem_used_mb", sa.Integer(), nullable=True),
        sa.Column("disk_total_gb", sa.Float(), nullable=True),
        sa.Column("disk_used_gb", sa.Float(), nullable=True),
        sa.Column("active_sessions", sa.Integer(), nullable=True),
        sa.Column("rangebox_count", sa.Integer(), nullable=True),
        sa.Column("docker_containers", sa.Integer(), nullable=True),
        sa.Column("docker_images", sa.Integer(), nullable=True),
        sa.Column("db_connections", sa.Integer(), nullable=True),
    )
    op.create_index("ix_system_metrics_created_at", "system_metrics", ["created_at"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "system_metrics" in inspector.get_table_names():
        op.drop_table("system_metrics")
