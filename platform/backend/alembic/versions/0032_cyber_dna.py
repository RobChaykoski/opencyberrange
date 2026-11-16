"""Add the Cyber DNA evidence ledger and snapshots.

Revision ID: 0032_cyber_dna
Revises: 0031_learner_snapshots
Create Date: 2026-11-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0032_cyber_dna"
down_revision: Union[str, None] = "0031_learner_snapshots"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "dna_evidence_records" not in tables:
        op.create_table(
            "dna_evidence_records",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("learner_id", sa.Integer(), nullable=False),
            sa.Column("event_id", sa.String(length=120), nullable=False),
            sa.Column("activity_id", sa.String(length=160), nullable=False),
            sa.Column("activity_category", sa.String(length=64), nullable=False),
            sa.Column("competency_id", sa.String(length=32), nullable=False),
            sa.Column("domain_id", sa.String(length=16), nullable=False),
            sa.Column("mapping_weight", sa.Float(), nullable=False),
            sa.Column("score_contribution", sa.Float(), nullable=False),
            sa.Column("difficulty", sa.String(length=20), nullable=True),
            sa.Column("attempts", sa.Integer(), nullable=True),
            sa.Column("hints_used", sa.Integer(), nullable=True),
            sa.Column("duration_minutes", sa.Integer(), nullable=True),
            sa.Column("prior_failed_attempts", sa.Integer(), nullable=True),
            sa.Column(
                "voluntary",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
            sa.Column("source_version", sa.String(length=32), nullable=False),
            sa.Column("occurred_at", sa.DateTime(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "event_id",
                "competency_id",
                name="uq_dna_evidence_event_competency",
            ),
        )
        op.create_index(
            "ix_dna_evidence_learner_competency",
            "dna_evidence_records",
            ["learner_id", "competency_id", "occurred_at"],
        )
        op.create_index(
            "ix_dna_evidence_learner_time",
            "dna_evidence_records",
            ["learner_id", "occurred_at"],
        )
        op.create_index(
            "ix_dna_evidence_records_learner_id",
            "dna_evidence_records",
            ["learner_id"],
        )

    if "dna_snapshots" not in tables:
        op.create_table(
            "dna_snapshots",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("learner_id", sa.Integer(), nullable=False),
            sa.Column("kind", sa.String(length=32), nullable=False),
            sa.Column("schema_version", sa.String(length=32), nullable=False),
            sa.Column("formula_version", sa.String(length=32), nullable=True),
            sa.Column("weights", sa.Text(), nullable=False),
            sa.Column("payload", sa.Text(), nullable=False),
            sa.Column("content_sha256", sa.String(length=64), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "learner_id",
                "kind",
                "content_sha256",
                name="uq_dna_snapshot_content",
            ),
        )
        op.create_index(
            "ix_dna_snapshot_learner_kind",
            "dna_snapshots",
            ["learner_id", "kind"],
        )
        op.create_index(
            "ix_dna_snapshots_learner_id",
            "dna_snapshots",
            ["learner_id"],
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "dna_snapshots" in tables:
        op.drop_index("ix_dna_snapshots_learner_id", table_name="dna_snapshots")
        op.drop_index("ix_dna_snapshot_learner_kind", table_name="dna_snapshots")
        op.drop_table("dna_snapshots")
    if "dna_evidence_records" in tables:
        op.drop_index(
            "ix_dna_evidence_records_learner_id",
            table_name="dna_evidence_records",
        )
        op.drop_index("ix_dna_evidence_learner_time", table_name="dna_evidence_records")
        op.drop_index(
            "ix_dna_evidence_learner_competency",
            table_name="dna_evidence_records",
        )
        op.drop_table("dna_evidence_records")
