"""Add report export manifests for tamper verification.

Revision ID: 0009_report_exports
Revises: 0008_mitre_attack
Create Date: 2026-11-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0009_report_exports"
down_revision: Union[str, None] = "0008_mitre_attack"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _has_table("report_exports"):
        return
    op.create_table(
        "report_exports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("report_id", sa.String(length=36), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_type", sa.String(length=40), nullable=False),
        sa.Column("format", sa.String(length=10), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("signature", sa.String(length=64), nullable=False),
        sa.Column("generated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("generated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_report_exports_report_id", "report_exports", ["report_id"], unique=True)
    op.create_index("ix_report_exports_course_id", "report_exports", ["course_id"])


def downgrade() -> None:
    if _has_table("report_exports"):
        op.drop_index("ix_report_exports_course_id", table_name="report_exports")
        op.drop_index("ix_report_exports_report_id", table_name="report_exports")
        op.drop_table("report_exports")
