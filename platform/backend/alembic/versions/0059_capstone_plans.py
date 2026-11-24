"""Add persisted capstone plans.

Revision ID: 0059_capstone_plans
Revises: 0058_practice_sessions
Create Date: 2026-11-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0059_capstone_plans"
down_revision: Union[str, None] = "0058_practice_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    tables = set(inspector.get_table_names())

    if "capstone_plans" not in tables:
        op.create_table(
            "capstone_plans",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "institution_id",
                sa.String(length=64),
                nullable=False,
                server_default=sa.text("'default'"),
            ),
            sa.Column(
                "owner_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("profile_id", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column(
                "status",
                sa.String(length=16),
                nullable=False,
                server_default="draft",
            ),
            sa.Column(
                "version",
                sa.Integer(),
                nullable=False,
                server_default="1",
            ),
            sa.Column("request", sa.JSON(), nullable=False),
            sa.Column("plan", sa.JSON(), nullable=False),
            sa.Column("validation", sa.JSON(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column("approved_at", sa.DateTime(), nullable=True),
            sa.Column(
                "approved_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
        op.create_index(
            "ix_capstone_plans_institution_id",
            "capstone_plans",
            ["institution_id"],
        )
        op.create_index(
            "ix_capstone_plans_owner_id",
            "capstone_plans",
            ["owner_id"],
        )
        op.create_index(
            "ix_capstone_plans_profile_id",
            "capstone_plans",
            ["profile_id"],
        )
        op.create_index(
            "ix_capstone_plans_status",
            "capstone_plans",
            ["status"],
        )
        op.create_index(
            "ix_capstone_plans_owner_status",
            "capstone_plans",
            ["owner_id", "status"],
        )
        op.create_index(
            "ix_capstone_plans_tenant_status",
            "capstone_plans",
            ["institution_id", "status"],
        )

    from app.services import tenant_rls

    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "capstone_plans" in set(inspector.get_table_names()):
        op.drop_table("capstone_plans")
