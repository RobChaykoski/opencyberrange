"""Add workbook-answer capture and evidence content snapshots.

Revision ID: 0053_workbook_answers
Revises: 0052_evidence_engine
Create Date: 2026-11-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0053_workbook_answers"
down_revision: Union[str, None] = "0052_evidence_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    tables = set(inspector.get_table_names())

    if "workbook_answers" not in tables:
        op.create_table(
            "workbook_answers",
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
            sa.Column(
                "lab_id",
                sa.Integer(),
                sa.ForeignKey("labs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "prompt_key",
                sa.String(length=64),
                nullable=False,
                server_default="reflection",
            ),
            sa.Column("answer_text", sa.Text(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "user_id",
                "lab_id",
                "prompt_key",
                name="uq_workbook_answer",
            ),
        )
        op.create_index(
            "ix_workbook_answers_institution_id",
            "workbook_answers",
            ["institution_id"],
        )
        op.create_index(
            "ix_workbook_answers_user_id",
            "workbook_answers",
            ["user_id"],
        )
        op.create_index(
            "ix_workbook_answers_lab_id",
            "workbook_answers",
            ["lab_id"],
        )
        op.create_index(
            "ix_workbook_answer_user_lab",
            "workbook_answers",
            ["user_id", "lab_id"],
        )

    columns = {column["name"] for column in inspector.get_columns("evidence_records")}
    if "content_text" not in columns:
        op.add_column(
            "evidence_records",
            sa.Column("content_text", sa.Text(), nullable=True),
        )

    from app.services import evidence as evidence_service
    from app.services import tenant_rls

    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)
    evidence_service.ensure_append_only(binding)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "workbook_answers" in tables:
        op.drop_table("workbook_answers")
    columns = {column["name"] for column in inspector.get_columns("evidence_records")}
    if "content_text" in columns:
        op.drop_column("evidence_records", "content_text")
