"""Add allow/deny rules for sign-in and registration.

Revision ID: 0049_network_access_rules
Revises: 0048_performance_indexes
Create Date: 2026-11-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0049_network_access_rules"
down_revision: Union[str, None] = "0048_performance_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    if inspector.has_table("network_access_rules"):
        return
    op.create_table(
        "network_access_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scope", sa.String(16), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("value", sa.String(255), nullable=False),
        sa.Column("action", sa.String(8), nullable=False),
        sa.Column("note", sa.String(255), nullable=True),
        sa.Column(
            "created_by_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("scope", "kind", "value", "action", name="uq_network_access_rule"),
    )
    op.create_index("ix_network_access_rules_scope", "network_access_rules", ["scope"])
    op.create_index("ix_network_access_rules_value", "network_access_rules", ["value"])
    op.create_index("ix_network_access_rules_created_at", "network_access_rules", ["created_at"])
    op.create_index("ix_network_access_rules_expires_at", "network_access_rules", ["expires_at"])
    op.create_index(
        "ix_network_access_rules_scope_action",
        "network_access_rules",
        ["scope", "action"],
    )


def downgrade() -> None:
    op.drop_table("network_access_rules")
