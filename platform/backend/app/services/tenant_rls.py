"""Tenant columns, derivation triggers, and row-level security.

The Authorization Service is the first line of tenant defence. This module is
the database backstop for the tenant-owned tables that hold learner records:
an institution's rows are invisible to another institution even if a future
query forgets the service check.

Two rules make the rollout safe:

* an ``institution_id`` is derived from the owning user/course by a trigger, so
  a client cannot choose a tenant;
* background jobs and startup code run as the system principal, while an
  unauthenticated HTTP request sees only the default institution.
"""

from __future__ import annotations

import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)

# table -> (owner column, optional course column)
#
# Only learner/user-owned records are listed here. Authentication tables
# (sessions, refresh tokens, SSO tickets, RBAC roles), secrets (WireGuard keys,
# service credentials), and platform operations (security events, audit,
# break-glass, settings changes) are deliberately excluded: they are read
# before a tenant context exists, are global by design, or have their own
# controls. Course-owned content tables without a user owner (cohorts,
# assignments, requirements, attachments, report exports) remain service- and
# course-scoped; see docs/TENANT-ISOLATION-STATUS.md for the classification.
TENANT_TABLES: dict[str, dict[str, str | None]] = {
    "courses": {"owner": "instructor_id", "course": None},
    "course_enrollments": {"owner": "user_id", "course": "course_id"},
    "lab_sessions": {"owner": "user_id", "course": None},
    "lab_completions": {"owner": "user_id", "course": None},
    "achievements": {"owner": "user_id", "course": "course_id"},
    "learner_snapshots": {"owner": "user_id", "course": None},
    "portfolio_share_tokens": {"owner": "user_id", "course": None},
    "dna_evidence_records": {"owner": "learner_id", "course": None},
    "dna_snapshots": {"owner": "learner_id", "course": None},
    # Legacy learner-owned tables migrated in 0041.
    "flag_attempts": {"owner": "user_id", "course": None},
    "review_requests": {"owner": "user_id", "course": "course_id"},
    "survey_responses": {"owner": "user_id", "course": "course_id"},
    "user_accommodations": {"owner": "user_id", "course": None},
    "accommodation_events": {"owner": "user_id", "course": None},
    "exercise_quiz_attempts": {"owner": "user_id", "course": "course_id"},
    "exercise_quiz_feedback": {"owner": "user_id", "course": "course_id"},
    "exercise_reactions": {"owner": "user_id", "course": "course_id"},
    "exercise_pulse_surveys": {"owner": "user_id", "course": "course_id"},
    "course_feedback": {"owner": "author_id", "course": "course_id"},
    "course_completion_resets": {"owner": "user_id", "course": "course_id"},
    "course_cohort_members": {"owner": "user_id", "course": None},
    "quiz_attempts": {"owner": "user_id", "course": None},
    "open_badge_credentials": {"owner": "user_id", "course": None},
    "lti_scores": {"owner": "user_id", "course": None},
    "activity_events": {"owner": "actor_id", "course": None},
    "readiness_student_notes": {"owner": "learner_id", "course": "course_id"},
    "readiness_lab_reviews": {"owner": "created_by_id", "course": "course_id"},
}

_RLS_USING = (
    "current_setting('ocr.system_admin', true) = 'true' "
    "OR institution_id IS NULL "
    "OR institution_id = NULLIF(current_setting('ocr.institution_id', true), '')"
)


def _table_exists(conn, table: str) -> bool:
    """True when the table exists.

    Migrations import the live ``TENANT_TABLES`` map, so an early revision must
    skip tables that a later revision has not created yet. Without this check a
    fresh database would fail at the first tenant migration.
    """
    try:
        return (
            conn.execute(
                text("SELECT to_regclass(:name)"), {"name": f"public.{table}"}
            ).scalar()
            is not None
        )
    except Exception:  # pragma: no cover - dialect without to_regclass
        return True


def _owner_function(table: str, owner: str, course: str | None) -> str:
    function = f"ocr_{table}_tenant()"
    if course:
        body = f"""
        SELECT institution_id INTO NEW.institution_id
          FROM courses WHERE id = NEW.{course};
        IF NEW.institution_id IS NULL OR NEW.institution_id = '' THEN
          SELECT institution_id INTO NEW.institution_id
            FROM users WHERE id = NEW.{owner};
        END IF;
        """
    else:
        body = f"""
        SELECT institution_id INTO NEW.institution_id
          FROM users WHERE id = NEW.{owner};
        """
    return f"""
    CREATE OR REPLACE FUNCTION {function}
    RETURNS trigger AS $$
    BEGIN
        {body}
        IF NEW.institution_id IS NULL OR NEW.institution_id = '' THEN
            NEW.institution_id := 'default';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """


def ensure_tenant_schema(conn) -> None:
    """Add columns, backfill them, and install derivation triggers."""
    if conn.dialect.name != "postgresql":
        return
    for table, spec in TENANT_TABLES.items():
        if not _table_exists(conn, table):
            logger.info("Tenant schema skipped for absent table %s", table)
            continue
        owner = str(spec["owner"])
        course = spec.get("course")
        conn.execute(
            text(
                f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS "
                "institution_id VARCHAR(64)"
            )
        )
        conn.execute(
            text(
                f"ALTER TABLE {table} ALTER COLUMN institution_id "
                "SET DEFAULT 'default'"
            )
        )
        if course:
            conn.execute(
                text(
                    f"UPDATE {table} AS t SET institution_id = c.institution_id "
                    f"FROM courses c WHERE c.id = t.{course} "
                    "AND (t.institution_id IS NULL OR t.institution_id = '')"
                )
            )
        conn.execute(
            text(
                f"UPDATE {table} AS t SET institution_id = u.institution_id "
                f"FROM users u WHERE u.id = t.{owner} "
                "AND (t.institution_id IS NULL OR t.institution_id = '')"
            )
        )
        conn.execute(
            text(
                f"UPDATE {table} SET institution_id = 'default' "
                "WHERE institution_id IS NULL OR institution_id = ''"
            )
        )
        conn.execute(
            text(f"ALTER TABLE {table} ALTER COLUMN institution_id SET NOT NULL")
        )
        conn.execute(
            text(
                f"CREATE INDEX IF NOT EXISTS ix_{table}_institution_id "
                f"ON {table} (institution_id)"
            )
        )
        conn.execute(text(_owner_function(table, owner, course)))
        conn.execute(text(f"DROP TRIGGER IF EXISTS ocr_{table}_tenant ON {table}"))
        conn.execute(
            text(
                f"CREATE TRIGGER ocr_{table}_tenant "
                f"BEFORE INSERT OR UPDATE ON {table} "
                f"FOR EACH ROW EXECUTE FUNCTION ocr_{table}_tenant()"
            )
        )
    logger.info("Tenant columns and derivation triggers ready (%d tables)", len(TENANT_TABLES))


def ensure_tenant_rls(conn) -> None:
    """Enable forced RLS and tenant policies on every tenant-owned table."""
    if conn.dialect.name != "postgresql":
        return
    for table in TENANT_TABLES:
        if not _table_exists(conn, table):
            continue
        conn.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
        conn.execute(text(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY"))
        for suffix in ("select", "insert", "update", "delete"):
            conn.execute(
                text(f"DROP POLICY IF EXISTS {table}_tenant_{suffix} ON {table}")
            )
        conn.execute(
            text(
                f"CREATE POLICY {table}_tenant_select ON {table} "
                f"FOR SELECT USING ({_RLS_USING})"
            )
        )
        conn.execute(
            text(
                f"CREATE POLICY {table}_tenant_insert ON {table} "
                f"FOR INSERT WITH CHECK ({_RLS_USING})"
            )
        )
        conn.execute(
            text(
                f"CREATE POLICY {table}_tenant_update ON {table} "
                f"FOR UPDATE USING ({_RLS_USING}) WITH CHECK ({_RLS_USING})"
            )
        )
        conn.execute(
            text(
                f"CREATE POLICY {table}_tenant_delete ON {table} "
                f"FOR DELETE USING ({_RLS_USING})"
            )
        )
    logger.info("Tenant row-level security enabled (%d tables)", len(TENANT_TABLES))


def apply(engine) -> None:
    """Apply columns, triggers, and RLS in one transaction."""
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        ensure_tenant_schema(conn)
        ensure_tenant_rls(conn)
