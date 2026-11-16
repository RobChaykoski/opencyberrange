"""Extend tenant columns, derivation triggers, and forced RLS to legacy
learner-owned tables.

Revision ID: 0041_tenant_rls_legacy
Revises: 0040_settings_change_control
Create Date: 2026-11-16

The table list lives in :mod:`app.services.tenant_rls`. This revision is
idempotent: it re-runs the same helpers as 0035, adding only the tables that
exist at this point in the migration chain. Authentication, secret, and
platform-operation tables are intentionally excluded; see the module comment
and ``docs/TENANT-ISOLATION-STATUS.md``.
"""

from typing import Sequence, Union

from alembic import op

from app.services import tenant_rls

revision: str = "0041_tenant_rls_legacy"
down_revision: Union[str, None] = "0040_settings_change_control"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    if binding.dialect.name != "postgresql":
        return
    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    """Intentionally additive.

    Dropping ``institution_id`` and the policies from learner tables would
    remove a security control from live data. Rolling back the feature is a
    forward migration, not an automatic column drop.
    """
    return
