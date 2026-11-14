"""Record minor-account enrollment consent references.

Revision ID: 0023_minor_consent
Revises: 0022_lab_pause
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0023_minor_consent"
down_revision: Union[str, None] = "0022_lab_pause"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("course_enrollments")}
    if "consent_reference" not in columns:
        op.add_column(
            "course_enrollments",
            sa.Column("consent_reference", sa.String(200), nullable=True),
        )
    if "consent_recorded_at" not in columns:
        op.add_column(
            "course_enrollments",
            sa.Column("consent_recorded_at", sa.DateTime(), nullable=True),
        )
    if "consent_recorded_by_id" not in columns:
        op.add_column(
            "course_enrollments",
            sa.Column(
                "consent_recorded_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("course_enrollments")}
    if "consent_recorded_by_id" in columns:
        op.drop_column("course_enrollments", "consent_recorded_by_id")
    if "consent_recorded_at" in columns:
        op.drop_column("course_enrollments", "consent_recorded_at")
    if "consent_reference" in columns:
        op.drop_column("course_enrollments", "consent_reference")
