"""Security event store, RBAC tables, break-glass, and portfolio shares.

Revision ID: 0034_security_events_rbac
Revises: 0033_consent_revocation
Create Date: 2026-11-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0034_security_events_rbac"
down_revision: Union[str, None] = "0033_consent_revocation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    columns = {column["name"] for column in inspector.get_columns("users")}
    if "institution_id" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "institution_id",
                sa.String(length=64),
                nullable=False,
                server_default=sa.text("'default'"),
            ),
        )
        op.create_index("ix_users_institution_id", "users", ["institution_id"])

    if "security_events" not in tables:
        op.create_table(
            "security_events",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "occurred_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("category", sa.String(length=16), nullable=False),
            sa.Column("event_type", sa.String(length=80), nullable=False),
            sa.Column(
                "severity", sa.String(length=16), nullable=False, server_default="info"
            ),
            sa.Column(
                "outcome", sa.String(length=16), nullable=False, server_default="success"
            ),
            sa.Column("action", sa.String(length=120), nullable=True),
            sa.Column("actor_id", sa.Integer(), nullable=True),
            sa.Column("actor_username", sa.String(length=120), nullable=True),
            sa.Column("actor_role", sa.String(length=32), nullable=True),
            sa.Column("institution_id", sa.String(length=64), nullable=True),
            sa.Column("target_type", sa.String(length=40), nullable=True),
            sa.Column("target_id", sa.String(length=64), nullable=True),
            sa.Column("target_label", sa.String(length=200), nullable=True),
            sa.Column("resource", sa.String(length=300), nullable=True),
            sa.Column("method", sa.String(length=10), nullable=True),
            sa.Column("path", sa.String(length=300), nullable=True),
            sa.Column("status_code", sa.Integer(), nullable=True),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.Column("user_agent", sa.String(length=300), nullable=True),
            sa.Column("request_id", sa.String(length=64), nullable=True),
            sa.Column("detail", sa.Text(), nullable=True),
        )
        op.create_index("ix_security_events_occurred_at", "security_events", ["occurred_at"])
        op.create_index("ix_security_events_category", "security_events", ["category"])
        op.create_index("ix_security_events_event_type", "security_events", ["event_type"])
        op.create_index("ix_security_events_actor_id", "security_events", ["actor_id"])
        op.create_index(
            "ix_security_events_institution_id", "security_events", ["institution_id"]
        )
        op.create_index(
            "ix_security_events_category_time",
            "security_events",
            ["category", "occurred_at"],
        )
        op.create_index(
            "ix_security_events_type_time",
            "security_events",
            ["event_type", "occurred_at"],
        )
        op.create_index(
            "ix_security_events_actor_time",
            "security_events",
            ["actor_id", "occurred_at"],
        )
        op.create_index(
            "ix_security_events_institution_time",
            "security_events",
            ["institution_id", "occurred_at"],
        )
        op.create_index(
            "ix_security_events_severity_time",
            "security_events",
            ["severity", "occurred_at"],
        )

    if "rbac_roles" not in tables:
        op.create_table(
            "rbac_roles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("key", sa.String(length=32), nullable=False, unique=True),
            sa.Column("label", sa.String(length=80), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("rank", sa.Integer(), nullable=False, server_default="100"),
            sa.Column(
                "is_system", sa.Boolean(), nullable=False, server_default=sa.text("true")
            ),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
        op.create_index("ix_rbac_roles_key", "rbac_roles", ["key"])

    if "rbac_permissions" not in tables:
        op.create_table(
            "rbac_permissions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("key", sa.String(length=120), nullable=False, unique=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("category", sa.String(length=40), nullable=True),
            sa.Column(
                "sensitivity",
                sa.String(length=16),
                nullable=False,
                server_default="medium",
            ),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
        op.create_index("ix_rbac_permissions_key", "rbac_permissions", ["key"])
        op.create_index("ix_rbac_permissions_category", "rbac_permissions", ["category"])

    if "rbac_role_permissions" not in tables:
        op.create_table(
            "rbac_role_permissions",
            sa.Column(
                "role_id",
                sa.Integer(),
                sa.ForeignKey("rbac_roles.id", ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column(
                "permission_id",
                sa.Integer(),
                sa.ForeignKey("rbac_permissions.id", ondelete="CASCADE"),
                primary_key=True,
            ),
        )

    if "rbac_user_roles" not in tables:
        op.create_table(
            "rbac_user_roles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "role_key",
                sa.String(length=32),
                sa.ForeignKey("rbac_roles.key", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("institution_id", sa.String(length=64), nullable=True),
            sa.Column(
                "granted_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("reason", sa.String(length=500), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint("user_id", "role_key", name="uq_rbac_user_role"),
        )
        op.create_index("ix_rbac_user_roles_user_id", "rbac_user_roles", ["user_id"])
        op.create_index(
            "ix_rbac_user_roles_institution_id", "rbac_user_roles", ["institution_id"]
        )
        op.create_index("ix_rbac_user_roles_expires_at", "rbac_user_roles", ["expires_at"])
        op.create_index(
            "ix_rbac_user_roles_user_expiry", "rbac_user_roles", ["user_id", "expires_at"]
        )

    if "break_glass_grants" not in tables:
        op.create_table(
            "break_glass_grants",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("permission", sa.String(length=120), nullable=False),
            sa.Column("scope_user_id", sa.Integer(), nullable=True),
            sa.Column("scope_course_id", sa.Integer(), nullable=True),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("reference", sa.String(length=120), nullable=True),
            sa.Column(
                "status", sa.String(length=16), nullable=False, server_default="pending"
            ),
            sa.Column(
                "requested_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "approved_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("approved_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
            sa.Column(
                "revoked_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("last_used_at", sa.DateTime(), nullable=True),
            sa.Column("use_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column(
                "review_status",
                sa.String(length=16),
                nullable=False,
                server_default="pending",
            ),
            sa.Column(
                "reviewed_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("reviewed_at", sa.DateTime(), nullable=True),
            sa.Column("review_note", sa.Text(), nullable=True),
        )
        op.create_index("ix_break_glass_grants_user_id", "break_glass_grants", ["user_id"])
        op.create_index(
            "ix_break_glass_grants_permission", "break_glass_grants", ["permission"]
        )
        op.create_index(
            "ix_break_glass_grants_scope_user_id", "break_glass_grants", ["scope_user_id"]
        )
        op.create_index(
            "ix_break_glass_grants_scope_course_id",
            "break_glass_grants",
            ["scope_course_id"],
        )
        op.create_index(
            "ix_break_glass_grants_expires_at", "break_glass_grants", ["expires_at"]
        )
        op.create_index(
            "ix_break_glass_user_status", "break_glass_grants", ["user_id", "status"]
        )
        op.create_index(
            "ix_break_glass_permission_status",
            "break_glass_grants",
            ["permission", "status"],
        )

    if "portfolio_share_tokens" not in tables:
        op.create_table(
            "portfolio_share_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("token_hash", sa.String(length=64), nullable=False, unique=True),
            sa.Column("label", sa.String(length=120), nullable=True),
            sa.Column("audience", sa.String(length=120), nullable=True),
            sa.Column(
                "created_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
            sa.Column(
                "single_use", sa.Boolean(), nullable=False, server_default=sa.text("false")
            ),
            sa.Column("max_uses", sa.Integer(), nullable=True),
            sa.Column("use_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("last_used_at", sa.DateTime(), nullable=True),
            sa.Column("last_used_ip", sa.String(length=64), nullable=True),
            sa.Column("consent_version", sa.Integer(), nullable=True),
        )
        op.create_index(
            "ix_portfolio_share_tokens_user_id", "portfolio_share_tokens", ["user_id"]
        )
        op.create_index(
            "ix_portfolio_share_tokens_token_hash",
            "portfolio_share_tokens",
            ["token_hash"],
        )
        op.create_index(
            "ix_portfolio_share_tokens_expires_at",
            "portfolio_share_tokens",
            ["expires_at"],
        )
        op.create_index(
            "ix_portfolio_share_user_created",
            "portfolio_share_tokens",
            ["user_id", "created_at"],
        )

    if bind.dialect.name == "postgresql":
        statements = (
            "ALTER TABLE security_events ENABLE ROW LEVEL SECURITY",
            "ALTER TABLE security_events FORCE ROW LEVEL SECURITY",
            "DROP POLICY IF EXISTS security_events_insert ON security_events",
            "DROP POLICY IF EXISTS security_events_select ON security_events",
            "DROP POLICY IF EXISTS security_events_no_update ON security_events",
            "DROP POLICY IF EXISTS security_events_no_delete ON security_events",
            "CREATE POLICY security_events_insert ON security_events "
            "FOR INSERT WITH CHECK (true)",
            "CREATE POLICY security_events_select ON security_events FOR SELECT USING ("
            "current_setting('ocr.system_admin', true) = 'true' "
            "OR institution_id IS NULL "
            "OR institution_id = NULLIF(current_setting('ocr.institution_id', true), ''))",
            "CREATE POLICY security_events_no_update ON security_events "
            "FOR UPDATE USING (false) WITH CHECK (false)",
            "CREATE POLICY security_events_no_delete ON security_events "
            "FOR DELETE USING (false)",
            "REVOKE UPDATE, DELETE ON security_events FROM PUBLIC",
        )
        for statement in statements:
            op.execute(statement)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    for table in (
        "portfolio_share_tokens",
        "break_glass_grants",
        "rbac_user_roles",
        "rbac_role_permissions",
        "rbac_permissions",
        "rbac_roles",
        "security_events",
    ):
        if table in tables:
            op.drop_table(table)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "institution_id" in columns:
        op.drop_index("ix_users_institution_id", table_name="users")
        op.drop_column("users", "institution_id")
