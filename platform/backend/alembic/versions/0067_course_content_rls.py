"""Course-owned content RLS wave.

Revision ID: 0067_course_content_rls
Revises: 0066_tenant_baseline
Create Date: 2026-11-24

Adds `institution_id` to the six course-owned content tables, derives it from
`course_id`, and enables forced row-level security with the standard tenant
policies. There is no user owner on these tables; a client cannot choose the
tenant.

The runtime `tenant_rls` service applies the same policies at startup, so this
migration is idempotent on hosts that have already run it.
"""

from alembic import op

revision = "0067_course_content_rls"
down_revision = "0066_tenant_baseline"
branch_labels = None
depends_on = None

_TABLES = (
    "course_cohorts",
    "course_lab_assignments",
    "course_requirements",
    "survey_attachments",
    "exercise_sets",
    "report_exports",
)

_USING = (
    "current_setting('ocr.system_admin', true) = 'true' "
    "OR institution_id IS NULL "
    "OR institution_id = NULLIF(current_setting('ocr.institution_id', true), '')"
)


def upgrade() -> None:
    for table in _TABLES:
        op.execute(
            f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS "
            "institution_id VARCHAR(64)"
        )
        op.execute(
            f"UPDATE {table} AS t SET institution_id = c.institution_id "
            f"FROM courses c WHERE c.id = t.course_id "
            "AND (t.institution_id IS NULL OR t.institution_id = '')"
        )
        op.execute(
            f"UPDATE {table} SET institution_id = 'default' "
            "WHERE institution_id IS NULL OR institution_id = ''"
        )
        op.execute(
            f"ALTER TABLE {table} ALTER COLUMN institution_id "
            "SET DEFAULT 'default'"
        )
        op.execute(
            f"ALTER TABLE {table} ALTER COLUMN institution_id SET NOT NULL"
        )
        op.execute(
            f"CREATE INDEX IF NOT EXISTS ix_{table}_institution_id "
            f"ON {table} (institution_id)"
        )
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        for suffix in ("select", "insert", "update", "delete"):
            op.execute(
                f"DROP POLICY IF EXISTS {table}_tenant_{suffix} ON {table}"
            )
        op.execute(
            f"CREATE POLICY {table}_tenant_select ON {table} "
            f"FOR SELECT USING ({_USING})"
        )
        op.execute(
            f"CREATE POLICY {table}_tenant_insert ON {table} "
            f"FOR INSERT WITH CHECK ({_USING})"
        )
        op.execute(
            f"CREATE POLICY {table}_tenant_update ON {table} "
            f"FOR UPDATE USING ({_USING}) WITH CHECK ({_USING})"
        )
        op.execute(
            f"CREATE POLICY {table}_tenant_delete ON {table} "
            f"FOR DELETE USING ({_USING})"
        )


def downgrade() -> None:
    for table in _TABLES:
        for suffix in ("select", "insert", "update", "delete"):
            op.execute(
                f"DROP POLICY IF EXISTS {table}_tenant_{suffix} ON {table}"
            )
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
        op.execute(f"DROP INDEX IF EXISTS ix_{table}_institution_id")
        op.execute(
            f"ALTER TABLE {table} DROP COLUMN IF EXISTS institution_id"
        )
