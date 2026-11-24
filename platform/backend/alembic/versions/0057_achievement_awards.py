"""Add achievement awards.

Revision ID: 0057_achievement_awards
Revises: 0056_impact_ledger
Create Date: 2026-11-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0057_achievement_awards"
down_revision: Union[str, None] = "0056_impact_ledger"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    tables = set(inspector.get_table_names())

    if "achievement_awards" not in tables:
        op.create_table(
            "achievement_awards",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "institution_id",
                sa.String(length=64),
                nullable=False,
                server_default=sa.text("'default'"),
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("achievement_key", sa.String(length=64), nullable=False),
            sa.Column(
                "source",
                sa.String(length=16),
                nullable=False,
                server_default="auto",
            ),
            sa.Column(
                "awarded_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "awarded_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("evidence_ref", sa.String(length=300), nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("seen_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint(
                "user_id",
                "achievement_key",
                name="uq_achievement_award",
            ),
        )
        op.create_index(
            "ix_achievement_awards_institution_id",
            "achievement_awards",
            ["institution_id"],
        )
        op.create_index(
            "ix_achievement_awards_user_id",
            "achievement_awards",
            ["user_id"],
        )
        op.create_index(
            "ix_achievement_awards_achievement_key",
            "achievement_awards",
            ["achievement_key"],
        )
        op.create_index(
            "ix_achievement_awards_user_seen",
            "achievement_awards",
            ["user_id", "seen_at"],
        )

    from app.services import tenant_rls

    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "achievement_awards" in set(inspector.get_table_names()):
        op.drop_table("achievement_awards")
