"""Add competency contract review records and cycles.

Revision ID: 0060_competency_reviews
Revises: 0059_capstone_plans
Create Date: 2026-11-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0060_competency_reviews"
down_revision: Union[str, None] = "0059_capstone_plans"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    tables = set(inspector.get_table_names())

    if "competency_contract_reviews" not in tables:
        op.create_table(
            "competency_contract_reviews",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "institution_id",
                sa.String(length=64),
                nullable=False,
                server_default=sa.text("'default'"),
            ),
            sa.Column("lab_slug", sa.String(length=120), nullable=False),
            sa.Column(
                "status",
                sa.String(length=24),
                nullable=False,
                server_default="draft",
            ),
            sa.Column("decision", sa.String(length=24), nullable=True),
            sa.Column("contract_snapshot", sa.JSON(), nullable=False),
            sa.Column("contract_hash", sa.String(length=64), nullable=False),
            sa.Column("baseline_hash", sa.String(length=64), nullable=True),
            sa.Column("deviation", sa.JSON(), nullable=True),
            sa.Column("lab_hash", sa.String(length=64), nullable=False),
            sa.Column("taxonomy_hash", sa.String(length=64), nullable=False),
            sa.Column("rationale", sa.Text(), nullable=False),
            sa.Column(
                "attestation",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column(
                "reviewer_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("reviewer_name", sa.String(length=120), nullable=True),
            sa.Column("reviewer_role", sa.String(length=32), nullable=False),
            sa.Column(
                "review_cycle_months",
                sa.Integer(),
                nullable=False,
                server_default="12",
            ),
            sa.Column("next_review_at", sa.DateTime(), nullable=True),
            sa.Column("signed_at", sa.DateTime(), nullable=True),
            sa.Column("exported_at", sa.DateTime(), nullable=True),
            sa.Column(
                "exported_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
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
        )
        op.create_index(
            "ix_competency_contract_reviews_institution_id",
            "competency_contract_reviews",
            ["institution_id"],
        )
        op.create_index(
            "ix_competency_contract_reviews_lab_slug",
            "competency_contract_reviews",
            ["lab_slug"],
        )
        op.create_index(
            "ix_competency_contract_reviews_status",
            "competency_contract_reviews",
            ["status"],
        )
        op.create_index(
            "ix_competency_contract_reviews_reviewer_id",
            "competency_contract_reviews",
            ["reviewer_id"],
        )
        op.create_index(
            "ix_competency_contract_reviews_next_review_at",
            "competency_contract_reviews",
            ["next_review_at"],
        )
        op.create_index(
            "ix_contract_reviews_lab_status",
            "competency_contract_reviews",
            ["lab_slug", "status"],
        )
        op.create_index(
            "ix_contract_reviews_tenant_status",
            "competency_contract_reviews",
            ["institution_id", "status"],
        )
        op.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_contract_review_active "
            "ON competency_contract_reviews (institution_id, lab_slug) "
            "WHERE status = 'signed'"
        )

    from app.services import tenant_rls

    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)

    if "competency_contract_reviews" in sa.inspect(binding).get_table_names():
        op.execute(
            """
            CREATE OR REPLACE FUNCTION zz_ocr_contract_review_guard()
            RETURNS trigger AS $$
            BEGIN
              NEW.institution_id := OLD.institution_id;
              IF OLD.status IN ('signed', 'superseded') THEN
                NEW.contract_snapshot := OLD.contract_snapshot;
                NEW.contract_hash := OLD.contract_hash;
                NEW.baseline_hash := OLD.baseline_hash;
                NEW.deviation := OLD.deviation;
                NEW.lab_hash := OLD.lab_hash;
                NEW.taxonomy_hash := OLD.taxonomy_hash;
                NEW.reviewer_id := OLD.reviewer_id;
                NEW.reviewer_name := OLD.reviewer_name;
                NEW.reviewer_role := OLD.reviewer_role;
                NEW.signed_at := OLD.signed_at;
                NEW.decision := OLD.decision;
                NEW.attestation := OLD.attestation;
                NEW.rationale := OLD.rationale;
                NEW.review_cycle_months := OLD.review_cycle_months;
                NEW.next_review_at := OLD.next_review_at;
              END IF;
              RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        op.execute(
            "DROP TRIGGER IF EXISTS zz_contract_review_guard "
            "ON competency_contract_reviews"
        )
        op.execute(
            "CREATE TRIGGER zz_contract_review_guard "
            "BEFORE UPDATE ON competency_contract_reviews "
            "FOR EACH ROW EXECUTE FUNCTION zz_ocr_contract_review_guard()"
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "competency_contract_reviews" in set(inspector.get_table_names()):
        op.drop_table("competency_contract_reviews")
    op.execute("DROP FUNCTION IF EXISTS zz_ocr_contract_review_guard()")
