"""Add LTI 1.3 platform registry and login state.

Revision ID: 0015_lti_platforms
Revises: 0014_performance_indexes
Create Date: 2026-11-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0015_lti_platforms"
down_revision: Union[str, None] = "0014_performance_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())

    if "lti_platforms" not in tables:
        op.create_table(
            "lti_platforms",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("issuer", sa.String(255), nullable=False),
            sa.Column("client_id", sa.String(255), nullable=False),
            sa.Column("deployment_id", sa.String(255), nullable=False),
            sa.Column("auth_login_url", sa.String(500), nullable=False),
            sa.Column("token_url", sa.String(500), nullable=False),
            sa.Column("jwks_url", sa.String(500), nullable=False),
            sa.Column(
                "identity_provider_id",
                sa.Integer(),
                sa.ForeignKey("identity_providers.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("private_key", sa.Text(), nullable=True),
            sa.Column(
                "enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")
            ),
            sa.Column(
                "created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
            ),
            sa.Column(
                "updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
            ),
            sa.UniqueConstraint(
                "issuer", "client_id", "deployment_id",
                name="uq_lti_platform_deployment",
            ),
        )
        op.create_index("ix_lti_platforms_issuer", "lti_platforms", ["issuer"])
        op.create_index("ix_lti_platforms_client_id", "lti_platforms", ["client_id"])
        op.create_index(
            "ix_lti_platforms_deployment_id", "lti_platforms", ["deployment_id"]
        )

    if "lti_login_states" not in tables:
        op.create_table(
            "lti_login_states",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("state", sa.String(128), nullable=False),
            sa.Column(
                "platform_id",
                sa.Integer(),
                sa.ForeignKey("lti_platforms.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("nonce", sa.String(128), nullable=False),
            sa.Column("target_link_uri", sa.String(500), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")
            ),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("consumed_at", sa.DateTime(), nullable=True),
        )
        op.create_index(
            "ix_lti_login_states_state", "lti_login_states", ["state"], unique=True
        )
        op.create_index(
            "ix_lti_login_states_platform_id", "lti_login_states", ["platform_id"]
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "lti_login_states" in tables:
        op.drop_table("lti_login_states")
    if "lti_platforms" in tables:
        op.drop_table("lti_platforms")
