"""Add evidence appeals.

Revision ID: 0054_evidence_appeals
Revises: 0053_workbook_answers
Create Date: 2026-11-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0054_evidence_appeals"
down_revision: Union[str, None] = "0053_workbook_answers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    tables = set(inspector.get_table_names())

    if "evidence_appeals" not in tables:
        op.create_table(
            "evidence_appeals",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "institution_id",
                sa.String(length=64),
                nullable=False,
                server_default=sa.text("'default'"),
            ),
            sa.Column(
                "evidence_id",
                sa.Integer(),
                sa.ForeignKey("evidence_records.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "learner_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default="pending",
            ),
            sa.Column(
                "reviewer_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("decision_notes", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        )
        op.create_index(
            "ix_evidence_appeals_institution_id",
            "evidence_appeals",
            ["institution_id"],
        )
        op.create_index(
            "ix_evidence_appeals_evidence_id",
            "evidence_appeals",
            ["evidence_id"],
        )
        op.create_index(
            "ix_evidence_appeals_learner_id",
            "evidence_appeals",
            ["learner_id"],
        )
        op.create_index(
            "ix_evidence_appeals_reviewer_id",
            "evidence_appeals",
            ["reviewer_id"],
        )
        op.create_index(
            "ix_evidence_appeals_evidence_status",
            "evidence_appeals",
            ["evidence_id", "status"],
        )
        op.create_index(
            "ix_evidence_appeals_learner_time",
            "evidence_appeals",
            ["learner_id", "created_at"],
        )

    from app.services import tenant_rls

    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "evidence_appeals" in set(inspector.get_table_names()):
        op.drop_table("evidence_appeals")
