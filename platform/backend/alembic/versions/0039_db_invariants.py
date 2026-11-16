"""Consent evidence append-only protection and enrollment uniqueness.

Revision ID: 0039_db_invariants
Revises: 0038_security_version
Create Date: 2026-11-16
"""

from typing import Sequence, Union

from alembic import op

from app.services import db_invariants

revision: str = "0039_db_invariants"
down_revision: Union[str, None] = "0038_security_version"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    if binding.dialect.name == "postgresql":
        # Consent history is evidence and must outlive an erased account. The
        # subject is anonymized (SET NULL) instead of cascading a DELETE.
        op.execute(
            "ALTER TABLE consent_events ALTER COLUMN user_id DROP NOT NULL"
        )
        op.execute(
            "ALTER TABLE consent_events "
            "DROP CONSTRAINT IF EXISTS consent_events_user_id_fkey"
        )
        op.execute(
            "ALTER TABLE consent_events ADD CONSTRAINT consent_events_user_id_fkey "
            "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL"
        )
    db_invariants.ensure_enrollment_unique(binding)
    db_invariants.ensure_one_active_session(binding)
    db_invariants.ensure_audit_protection(binding)


def downgrade() -> None:
    binding = op.get_bind()
    if binding.dialect.name != "postgresql":
        return
    for table in ("consent_events", "consent_audits"):
        op.execute(f"DROP TRIGGER IF EXISTS ocr_{table}_append_only ON {table}")
    op.execute("DROP FUNCTION IF EXISTS ocr_block_audit_mutation()")
    op.execute("DROP INDEX IF EXISTS ix_enrollment_course_user")
    op.execute("DROP INDEX IF EXISTS uq_active_lab_session_user")
    op.execute(
        "ALTER TABLE consent_events "
        "DROP CONSTRAINT IF EXISTS consent_events_user_id_fkey"
    )
    op.execute("DELETE FROM consent_events WHERE user_id IS NULL")
    op.execute(
        "ALTER TABLE consent_events ADD CONSTRAINT consent_events_user_id_fkey "
        "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
    )
    op.execute("ALTER TABLE consent_events ALTER COLUMN user_id SET NOT NULL")
