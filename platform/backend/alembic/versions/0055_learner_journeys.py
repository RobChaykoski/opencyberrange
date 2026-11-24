"""Add learner-chosen journeys.

Revision ID: 0055_learner_journeys
Revises: 0054_evidence_appeals
Create Date: 2026-11-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0055_learner_journeys"
down_revision: Union[str, None] = "0054_evidence_appeals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    tables = set(inspector.get_table_names())

    if "learner_journeys" not in tables:
        op.create_table(
            "learner_journeys",
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
            sa.Column("journey_id", sa.String(length=64), nullable=False),
            sa.Column(
                "is_primary",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column(
                "status",
                sa.String(length=16),
                nullable=False,
                server_default="active",
            ),
            sa.Column(
                "chosen_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "user_id",
                "journey_id",
                name="uq_learner_journey",
            ),
        )
        op.create_index(
            "ix_learner_journeys_institution_id",
            "learner_journeys",
            ["institution_id"],
        )
        op.create_index(
            "ix_learner_journeys_user_id",
            "learner_journeys",
            ["user_id"],
        )
        op.create_index(
            "ix_learner_journeys_journey_id",
            "learner_journeys",
            ["journey_id"],
        )
        op.create_index(
            "ix_learner_journey_primary",
            "learner_journeys",
            ["user_id", "is_primary"],
        )

    from app.services import tenant_rls

    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "learner_journeys" in set(inspector.get_table_names()):
        op.drop_table("learner_journeys")
