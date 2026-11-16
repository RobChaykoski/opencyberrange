"""Database invariants that must survive application regressions.

These are deliberately installed in the database, not enforced only in route
code: unique enrollment, append-only consent evidence, and the PostgreSQL
tenant policies installed by :mod:`app.services.tenant_rls`.
"""

from __future__ import annotations

import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)


def ensure_audit_protection(conn) -> None:
    """Block UPDATE/DELETE on append-only consent evidence.

    ``consent_audits`` still legitimately updates verification status, so only
    DELETE is blocked there. ``consent_events`` is fully append-only, with one
    deliberate exception: deleting a user lets the ``ON DELETE SET NULL``
    foreign key anonymize the subject. That is the only permitted update; the
    decision itself (type, action, version, actor, reason, timestamp) must stay
    byte-for-byte identical or the trigger raises.
    """
    if conn.dialect.name != "postgresql":
        return
    conn.execute(
        text(
            """
            CREATE OR REPLACE FUNCTION ocr_block_audit_mutation()
            RETURNS trigger AS $$
            BEGIN
                IF TG_TABLE_NAME = 'consent_events' AND TG_OP = 'UPDATE'
                   AND OLD.user_id IS NOT NULL AND NEW.user_id IS NULL
                   AND NEW.id IS NOT DISTINCT FROM OLD.id
                   AND NEW.consent_type IS NOT DISTINCT FROM OLD.consent_type
                   AND NEW.action IS NOT DISTINCT FROM OLD.action
                   AND NEW.consent_version IS NOT DISTINCT FROM OLD.consent_version
                   AND NEW.actor IS NOT DISTINCT FROM OLD.actor
                   AND NEW.reason IS NOT DISTINCT FROM OLD.reason
                   AND NEW.occurred_at IS NOT DISTINCT FROM OLD.occurred_at
                THEN
                    -- Account erasure anonymizes the subject. Consent evidence
                    -- survives the account; it is proof, not learner data.
                    RETURN NEW;
                END IF;
                RAISE EXCEPTION '% is append-only', TG_TABLE_NAME;
            END;
            $$ LANGUAGE plpgsql;
            """
        )
    )
    for table, operation in (
        ("consent_events", "UPDATE OR DELETE"),
        ("consent_audits", "DELETE"),
    ):
        conn.execute(
            text(f"DROP TRIGGER IF EXISTS ocr_{table}_append_only ON {table}")
        )
        conn.execute(
            text(
                f"CREATE TRIGGER ocr_{table}_append_only "
                f"BEFORE {operation} ON {table} "
                "FOR EACH ROW EXECUTE FUNCTION ocr_block_audit_mutation()"
            )
        )
    logger.info("Consent audit append-only protection ready")


def ensure_enrollment_unique(conn) -> None:
    if conn.dialect.name != "postgresql":
        return
    # Older data can contain duplicates from the pre-unique-index race. Keep
    # the earliest row and remove the rest so the index can be created.
    conn.execute(
        text(
            "DELETE FROM course_enrollments a USING course_enrollments b "
            "WHERE a.id > b.id AND a.course_id = b.course_id "
            "AND a.user_id = b.user_id"
        )
    )
    conn.execute(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_enrollment_course_user "
            "ON course_enrollments (course_id, user_id)"
        )
    )
    logger.info("Course enrollment uniqueness index ready")


def ensure_one_active_session(conn) -> None:
    """Allow at most one starting/running lab session per user."""
    if conn.dialect.name != "postgresql":
        return
    conn.execute(
        text(
            """
            WITH ranked AS (
                SELECT id, row_number() OVER (
                    PARTITION BY user_id ORDER BY started_at DESC NULLS LAST, id DESC
                ) AS rn
                FROM lab_sessions
                WHERE status IN ('starting', 'running')
            )
            UPDATE lab_sessions AS s
            SET status = 'expired', stopped_at = now()
            FROM ranked
            WHERE s.id = ranked.id AND ranked.rn > 1
            """
        )
    )
    conn.execute(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_active_lab_session_user "
            "ON lab_sessions (user_id) "
            "WHERE status IN ('starting', 'running')"
        )
    )
    logger.info("Active lab-session uniqueness index ready")


def apply(engine) -> None:
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        ensure_enrollment_unique(conn)
        ensure_one_active_session(conn)
        ensure_audit_protection(conn)
