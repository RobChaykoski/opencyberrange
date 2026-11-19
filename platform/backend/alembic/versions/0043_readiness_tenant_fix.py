"""Re-apply readiness tenant derivation after correcting the lab-review owner.

Revision ID: 0043_readiness_tenant_fix
Revises: 0042_readiness_workflow
Create Date: 2026-11-19

0042 created the lab-review table with ``owner_id`` while the tenant helper
briefly expected ``created_by_id``. This revision re-runs the idempotent tenant
schema and RLS pass with the corrected map so an existing database is repaired
as well as a fresh one.
"""

from typing import Sequence, Union

from alembic import op

from app.services import tenant_rls

revision: str = "0043_readiness_tenant_fix"
down_revision: Union[str, None] = "0042_readiness_workflow"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    if binding.dialect.name != "postgresql":
        return
    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    return
