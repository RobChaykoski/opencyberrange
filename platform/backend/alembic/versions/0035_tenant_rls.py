"""Tenant columns, derivation triggers, and forced RLS on learner data.

Revision ID: 0035_tenant_rls
Revises: 0034_security_events_rbac
Create Date: 2026-11-16
"""

from typing import Sequence, Union

from alembic import op

from app.services import tenant_rls

revision: str = "0035_tenant_rls"
down_revision: Union[str, None] = "0034_security_events_rbac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    if binding.dialect.name != "postgresql":
        return
    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    binding = op.get_bind()
    if binding.dialect.name != "postgresql":
        return
    for table in tenant_rls.TENANT_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_tenant_select ON {table}")
        op.execute(f"DROP POLICY IF EXISTS {table}_tenant_insert ON {table}")
        op.execute(f"DROP POLICY IF EXISTS {table}_tenant_update ON {table}")
        op.execute(f"DROP POLICY IF EXISTS {table}_tenant_delete ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
        op.execute(f"DROP TRIGGER IF EXISTS ocr_{table}_tenant ON {table}")
        op.execute(f"DROP FUNCTION IF EXISTS ocr_{table}_tenant()")
        op.execute(f"DROP INDEX IF EXISTS ix_{table}_institution_id")
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS institution_id")
