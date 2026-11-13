"""Add NRPS membership endpoint fields to LTI links.

Revision ID: 0017_lti_nrps
Revises: 0016_lti_links_scores
Create Date: 2026-11-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0017_lti_nrps"
down_revision: Union[str, None] = "0016_lti_links_scores"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "lti_links" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("lti_links")}
    if "nrps_url" not in columns:
        op.add_column("lti_links", sa.Column("nrps_url", sa.String(500), nullable=True))
    if "nrps_versions" not in columns:
        op.add_column("lti_links", sa.Column("nrps_versions", sa.Text(), nullable=True))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "lti_links" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("lti_links")}
    if "nrps_versions" in columns:
        op.drop_column("lti_links", "nrps_versions")
    if "nrps_url" in columns:
        op.drop_column("lti_links", "nrps_url")
