"""Add the Release 6 evidence ledger.

Revision ID: 0052_evidence_engine
Revises: 0051_registration_attribution
Create Date: 2026-11-23
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0052_evidence_engine"
down_revision: Union[str, None] = "0051_registration_attribution"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    tables = set(inspector.get_table_names())

    if "evidence_records" not in tables:
        op.create_table(
            "evidence_records",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "institution_id",
                sa.String(length=64),
                nullable=False,
                server_default=sa.text("'default'"),
            ),
            sa.Column(
                "learner_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("source_type", sa.String(length=32), nullable=False),
            sa.Column("source_id", sa.String(length=160), nullable=False),
            sa.Column("rubric_id", sa.String(length=64), nullable=False),
            sa.Column("rubric_version", sa.String(length=16), nullable=False),
            sa.Column(
                "confidence",
                sa.String(length=16),
                nullable=False,
                server_default="medium",
            ),
            sa.Column("confidence_reason", sa.String(length=500), nullable=True),
            sa.Column("collected_at", sa.DateTime(), nullable=False),
            sa.Column("provenance", sa.String(length=255), nullable=False),
            sa.Column("provenance_version", sa.String(length=32), nullable=True),
            sa.Column(
                "visibility",
                sa.String(length=16),
                nullable=False,
                server_default="both",
            ),
            sa.Column(
                "status",
                sa.String(length=16),
                nullable=False,
                server_default="collected",
            ),
            sa.Column(
                "reviewer_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("review_notes", sa.String(length=1000), nullable=True),
            sa.Column("formula_version", sa.String(length=32), nullable=False),
            sa.Column(
                "supersedes_id",
                sa.Integer(),
                sa.ForeignKey("evidence_records.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("source_fingerprint", sa.String(length=64), nullable=False),
            sa.Column("artifact_uri", sa.String(length=500), nullable=True),
            sa.Column("artifact_mime", sa.String(length=120), nullable=True),
            sa.Column("artifact_size", sa.Integer(), nullable=True),
            sa.Column("artifact_sha256", sa.String(length=64), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "source_fingerprint",
                name="uq_evidence_source_fingerprint",
            ),
        )
        op.create_index(
            "ix_evidence_records_institution_id",
            "evidence_records",
            ["institution_id"],
        )
        op.create_index(
            "ix_evidence_records_learner_id",
            "evidence_records",
            ["learner_id"],
        )
        op.create_index(
            "ix_evidence_records_reviewer_id",
            "evidence_records",
            ["reviewer_id"],
        )
        op.create_index(
            "ix_evidence_learner_collected",
            "evidence_records",
            ["learner_id", "collected_at"],
        )
        op.create_index(
            "ix_evidence_learner_status",
            "evidence_records",
            ["learner_id", "status"],
        )
        op.create_index(
            "ix_evidence_tenant_status",
            "evidence_records",
            ["institution_id", "status"],
        )
        op.create_index(
            "ix_evidence_rubric",
            "evidence_records",
            ["rubric_id", "rubric_version"],
        )

    if "evidence_competencies" not in tables:
        op.create_table(
            "evidence_competencies",
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
            sa.Column("competency_id", sa.String(length=32), nullable=False),
            sa.Column(
                "criteria",
                sa.Text(),
                nullable=False,
                server_default="[]",
            ),
            sa.Column(
                "weight",
                sa.Float(),
                nullable=False,
                server_default=sa.text("1.0"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "evidence_id",
                "competency_id",
                name="uq_evidence_competency",
            ),
        )
        op.create_index(
            "ix_evidence_competencies_institution_id",
            "evidence_competencies",
            ["institution_id"],
        )
        op.create_index(
            "ix_evidence_competencies_evidence_id",
            "evidence_competencies",
            ["evidence_id"],
        )
        op.create_index(
            "ix_evidence_competencies_competency_id",
            "evidence_competencies",
            ["competency_id"],
        )
        op.create_index(
            "ix_evidence_competency_lookup",
            "evidence_competencies",
            ["competency_id", "evidence_id"],
        )

    if "evidence_reviews" not in tables:
        op.create_table(
            "evidence_reviews",
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
                "reviewer_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("rubric_id", sa.String(length=64), nullable=False),
            sa.Column("rubric_version", sa.String(length=16), nullable=False),
            sa.Column("decision", sa.String(length=20), nullable=False),
            sa.Column(
                "criterion_scores",
                sa.Text(),
                nullable=False,
                server_default="{}",
            ),
            sa.Column("weighted_score", sa.Float(), nullable=True),
            sa.Column("notes", sa.String(length=1000), nullable=True),
            sa.Column("next_step", sa.String(length=500), nullable=True),
            sa.Column("reviewed_at", sa.DateTime(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
        op.create_index(
            "ix_evidence_reviews_institution_id",
            "evidence_reviews",
            ["institution_id"],
        )
        op.create_index(
            "ix_evidence_reviews_evidence_id",
            "evidence_reviews",
            ["evidence_id"],
        )
        op.create_index(
            "ix_evidence_reviews_reviewer_id",
            "evidence_reviews",
            ["reviewer_id"],
        )
        op.create_index(
            "ix_evidence_reviews_record_time",
            "evidence_reviews",
            ["evidence_id", "reviewed_at"],
        )

    from app.services import evidence as evidence_service
    from app.services import tenant_rls

    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)
    evidence_service.ensure_append_only(binding)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "evidence_reviews" in tables:
        op.drop_table("evidence_reviews")
    if "evidence_competencies" in tables:
        op.drop_table("evidence_competencies")
    if "evidence_records" in tables:
        op.drop_table("evidence_records")
