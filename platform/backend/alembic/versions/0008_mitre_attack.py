"""Add MITRE ATT&CK mappings to labs.

Revision ID: 0008_mitre_attack
Revises: 0007_lab_metadata
Create Date: 2026-11-09

Each lab now stores at least one {tactic, technique, technique_name,
detection} mapping from its lab.yaml.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008_mitre_attack"
down_revision: Union[str, None] = "0007_lab_metadata"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _existing_columns() -> set[str]:
    if "labs" not in sa.inspect(op.get_bind()).get_table_names():
        return set()
    return {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns("labs")
    }


def upgrade() -> None:
    if "mitre_attack" not in _existing_columns():
        op.add_column("labs", sa.Column("mitre_attack", sa.Text(), nullable=True))


def downgrade() -> None:
    if "mitre_attack" in _existing_columns():
        op.drop_column("labs", "mitre_attack")
