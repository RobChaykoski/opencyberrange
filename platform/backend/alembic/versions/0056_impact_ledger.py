"""Add the impact contribution and stewardship ledgers.

Revision ID: 0056_impact_ledger
Revises: 0055_learner_journeys
Create Date: 2026-11-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0056_impact_ledger"
down_revision: Union[str, None] = "0055_learner_journeys"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    tables = set(inspector.get_table_names())

    if "impact_contributions" not in tables:
        op.create_table(
            "impact_contributions",
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
            sa.Column("dimension", sa.String(length=16), nullable=False),
            sa.Column("kind", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column(
                "base_points",
                sa.Integer(),
                nullable=False,
                server_default="25",
            ),
            sa.Column(
                "reach_count",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.Column("quality_rating", sa.Float(), nullable=True),
            sa.Column(
                "validation_level",
                sa.String(length=16),
                nullable=False,
                server_default="self",
            ),
            sa.Column(
                "originality",
                sa.String(length=16),
                nullable=False,
                server_default="original",
            ),
            sa.Column(
                "status",
                sa.String(length=16),
                nullable=False,
                server_default="draft",
            ),
            sa.Column(
                "occurred_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column("last_used_at", sa.DateTime(), nullable=True),
            sa.Column("verified_at", sa.DateTime(), nullable=True),
            sa.Column(
                "verified_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "evidence_id",
                sa.Integer(),
                sa.ForeignKey("evidence_records.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("content_hash", sa.String(length=64), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("review_notes", sa.Text(), nullable=True),
            sa.UniqueConstraint(
                "user_id",
                "content_hash",
                name="uq_impact_contribution_hash",
            ),
        )
        op.create_index(
            "ix_impact_contributions_institution_id",
            "impact_contributions",
            ["institution_id"],
        )
        op.create_index(
            "ix_impact_contributions_user_id",
            "impact_contributions",
            ["user_id"],
        )
        op.create_index(
            "ix_impact_contributions_dimension",
            "impact_contributions",
            ["dimension"],
        )
        op.create_index(
            "ix_impact_contributions_kind",
            "impact_contributions",
            ["kind"],
        )
        op.create_index(
            "ix_impact_contributions_status",
            "impact_contributions",
            ["status"],
        )
        op.create_index(
            "ix_impact_contributions_evidence_id",
            "impact_contributions",
            ["evidence_id"],
        )
        op.create_index(
            "ix_impact_contributions_user_status",
            "impact_contributions",
            ["user_id", "status"],
        )
        op.create_index(
            "ix_impact_contributions_tenant_status",
            "impact_contributions",
            ["institution_id", "status"],
        )

    if "stewardship_events" not in tables:
        op.create_table(
            "stewardship_events",
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
            sa.Column("points_delta", sa.Integer(), nullable=False),
            sa.Column(
                "category",
                sa.String(length=16),
                nullable=False,
                server_default="positive",
            ),
            sa.Column("reason", sa.String(length=300), nullable=False),
            sa.Column(
                "occurred_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "recorded_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("evidence_ref", sa.String(length=300), nullable=True),
            sa.Column(
                "visibility",
                sa.String(length=16),
                nullable=False,
                server_default="private",
            ),
        )
        op.create_index(
            "ix_stewardship_events_institution_id",
            "stewardship_events",
            ["institution_id"],
        )
        op.create_index(
            "ix_stewardship_events_user_id",
            "stewardship_events",
            ["user_id"],
        )
        op.create_index(
            "ix_stewardship_events_user",
            "stewardship_events",
            ["user_id", "occurred_at"],
        )

    from app.services import tenant_rls

    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "stewardship_events" in tables:
        op.drop_table("stewardship_events")
    if "impact_contributions" in tables:
        op.drop_table("impact_contributions")
