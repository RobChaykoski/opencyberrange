"""Track whether the LMS accepts multiple Deep Linking content items.

Revision ID: 0020_lti_dl_multiple
Revises: 0019_lti_deep_link
Create Date: 2026-11-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0020_lti_dl_multiple"
down_revision: Union[str, None] = "0019_lti_deep_link"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {
        column["name"]
        for column in inspector.get_columns("lti_deep_link_sessions")
    }
    if "accept_multiple" in columns:
        return
    op.add_column(
        "lti_deep_link_sessions",
        sa.Column(
            "accept_multiple",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {
        column["name"]
        for column in inspector.get_columns("lti_deep_link_sessions")
    }
    if "accept_multiple" in columns:
        op.drop_column("lti_deep_link_sessions", "accept_multiple")
