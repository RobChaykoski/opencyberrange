"""Profile avatars: users.avatar_data.

Revision ID: 0004_user_avatar
Revises: 0003_auth_mfa_invites
Create Date: 2026-10-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_user_avatar"
down_revision: Union[str, None] = "0003_auth_mfa_invites"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_data", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_data")
