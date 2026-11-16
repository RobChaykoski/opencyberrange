"""Scoped non-human service credentials.

Revision ID: 0036_service_identities
Revises: 0035_tenant_rls
Create Date: 2026-11-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0036_service_identities"
down_revision: Union[str, None] = "0035_tenant_rls"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "service_credentials" in set(inspector.get_table_names()):
        return
    op.create_table(
        "service_credentials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("scopes", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("institution_id", sa.String(length=64), nullable=True),
        sa.Column(
            "created_by_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column(
            "revoked_by_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_service_credentials_user_id", "service_credentials", ["user_id"])
    op.create_index(
        "ix_service_credentials_token_hash", "service_credentials", ["token_hash"]
    )
    op.create_index(
        "ix_service_credentials_institution_id",
        "service_credentials",
        ["institution_id"],
    )
    op.create_index(
        "ix_service_credentials_expires_at", "service_credentials", ["expires_at"]
    )
    op.create_index(
        "ix_service_credentials_user_created",
        "service_credentials",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "service_credentials" in set(inspector.get_table_names()):
        op.drop_table("service_credentials")
