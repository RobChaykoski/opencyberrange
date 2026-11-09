"""Add canonical lab metadata columns.

Revision ID: 0007_lab_metadata
Revises: 0006_id_indexes
Create Date: 2026-11-09

The lab manifest now standardizes on ``title``/``estimated_time``/
``learning_outcomes`` plus prerequisites, mapped skills, and assessment
criteria. Learning outcomes continue to use the existing ``objectives``
column; the three new arrays are stored alongside it.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007_lab_metadata"
down_revision: Union[str, None] = "0006_id_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_COLUMNS = (
    "prerequisites",
    "mapped_skills",
    "assessment_criteria",
)


def _existing_lab_columns() -> set[str]:
    if "labs" not in sa.inspect(op.get_bind()).get_table_names():
        return set()
    return {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns("labs")
    }


def upgrade() -> None:
    existing = _existing_lab_columns()
    for column in _COLUMNS:
        if column not in existing:
            op.add_column("labs", sa.Column(column, sa.Text(), nullable=True))


def downgrade() -> None:
    existing = _existing_lab_columns()
    for column in _COLUMNS:
        if column in existing:
            op.drop_column("labs", column)
