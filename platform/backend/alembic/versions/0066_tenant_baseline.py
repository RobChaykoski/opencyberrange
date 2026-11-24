"""Tenant baseline: own the runtime institution_id columns and indexes.

Revision ID: 0066_tenant_baseline
Revises: 0065_legacy_kali_columns
Create Date: 2026-11-24

`app.services.tenant_rls.ensure_tenant_schema` has been adding `institution_id`
columns, backfilling them, and creating one index per table at startup. The
models did not declare those columns for every table, so `alembic check`
proposed removing them.

This migration moves the schema ownership into the migration graph. It is
idempotent, so it is a no-op on databases where the runtime DDL already ran,
and it gives a fresh restore the same columns and indexes. Triggers, backfill
derivations, and RLS policies stay in `tenant_rls` for now; this baseline covers
the columns and indexes that autogenerate compares.

Only aggregates were reviewed before this migration: every row in the affected
tables has `institution_id = 'default'`, with no nulls, on development and
production.
"""

from alembic import op

revision = "0066_tenant_baseline"
down_revision = "0065_legacy_kali_columns"
branch_labels = None
depends_on = None

_TABLES = (
    "accommodation_events",
    "activity_events",
    "course_cohort_members",
    "course_completion_resets",
    "course_feedback",
    "course_staff",
    "exercise_pulse_surveys",
    "exercise_quiz_attempts",
    "exercise_quiz_feedback",
    "exercise_reactions",
    "flag_attempts",
    "lti_scores",
    "open_badge_credentials",
    "practice_session_questions",
    "quiz_attempts",
    "review_requests",
    "survey_responses",
    "user_accommodations",
    "readiness_lab_reviews",
    "readiness_student_notes",
)


def upgrade() -> None:
    for table in _TABLES:
        op.execute(
            f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS "
            "institution_id VARCHAR(64)"
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


def downgrade() -> None:
    for table in _TABLES:
        op.execute(
            f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = '{table}'
                      AND column_name = 'institution_id'
                ) AND EXISTS (
                    SELECT 1 FROM {table}
                    WHERE institution_id IS DISTINCT FROM 'default'
                ) THEN
                    RAISE EXCEPTION
                        'refusing to drop {table}.institution_id: '
                        'non-default tenant data exists';
                END IF;
            END $$;
            """
        )
        op.execute(f"DROP INDEX IF EXISTS ix_{table}_institution_id")
        op.execute(
            f"ALTER TABLE {table} DROP COLUMN IF EXISTS institution_id"
        )
