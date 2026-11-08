"""Database integrity ledger migration and verification helpers.

The ledger is append-only. One PostgreSQL trigger per critical table records a
row hash, the actor context, and a chained entry hash. Manual SQL outside the
application is recorded as ``unattributed`` (or ``system`` if it uses the app
engine without a user).

This module owns the DDL. The read-only verification lives in
``scripts/database_integrity.py`` so it can run without importing the app.
"""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

LEDGER_TABLES = (
    "users",
    "courses",
    "course_enrollments",
    "course_lab_assignments",
    "labs",
    "levels",
    "tracks",
    "lab_completions",
    "lab_sessions",
    "achievements",
    "achievement_celebrations",
    "exercise_quiz_attempts",
    "exercise_quiz_feedback",
    "course_feedback",
    "survey_responses",
    "platform_settings",
)

_LEDGER_DDL = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS data_integrity_ledger (
    id SERIAL PRIMARY KEY,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    table_name VARCHAR(64) NOT NULL,
    row_pk VARCHAR(128) NOT NULL,
    operation VARCHAR(8) NOT NULL,
    row_hash VARCHAR(64) NOT NULL,
    actor_type VARCHAR(16) NOT NULL DEFAULT 'unattributed',
    actor_id INTEGER NULL,
    request_id VARCHAR(64) NULL,
    prev_hash VARCHAR(64) NOT NULL,
    entry_hash VARCHAR(64) NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_data_integrity_ledger_table
    ON data_integrity_ledger (table_name);
CREATE INDEX IF NOT EXISTS ix_data_integrity_ledger_entry
    ON data_integrity_ledger (entry_hash);

CREATE OR REPLACE FUNCTION ocr_integrity_trigger()
RETURNS trigger AS $$
DECLARE
    v_actor_type text;
    v_actor_id text;
    v_request_id text;
    v_app text;
    v_pk text;
    v_row_hash text;
    v_prev text;
    v_now timestamptz;
    v_entry text;
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_pk := OLD.id::text;
        v_row_hash := encode(digest(row_to_json(OLD)::text, 'sha256'), 'hex');
    ELSE
        v_pk := NEW.id::text;
        v_row_hash := encode(digest(row_to_json(NEW)::text, 'sha256'), 'hex');
    END IF;

    v_actor_type := nullif(current_setting('ocr.actor_type', true), '');
    v_actor_id := nullif(current_setting('ocr.actor_id', true), '');
    v_request_id := nullif(current_setting('ocr.request_id', true), '');
    IF v_actor_type IS NULL THEN
        v_app := coalesce(current_setting('application_name', true), '');
        IF v_app LIKE 'ocr-app%' THEN
            v_actor_type := 'system';
        ELSE
            v_actor_type := 'unattributed';
        END IF;
    END IF;

    PERFORM pg_advisory_xact_lock(hashtext('ocr.data_integrity_ledger'));
    SELECT entry_hash INTO v_prev
    FROM data_integrity_ledger
    ORDER BY id DESC
    LIMIT 1;
    v_prev := coalesce(v_prev, repeat('0', 64));
    v_now := clock_timestamp();
    v_entry := encode(digest(
        v_prev || TG_TABLE_NAME || v_pk || TG_OP || v_row_hash ||
        coalesce(v_actor_type, 'unattributed') || coalesce(v_actor_id, '') ||
        coalesce(v_request_id, '') || v_now::text,
        'sha256'
    ), 'hex');

    INSERT INTO data_integrity_ledger (
        occurred_at, table_name, row_pk, operation, row_hash,
        actor_type, actor_id, request_id, prev_hash, entry_hash
    ) VALUES (
        v_now, TG_TABLE_NAME, v_pk, TG_OP, v_row_hash,
        coalesce(v_actor_type, 'unattributed'),
        CASE WHEN v_actor_id ~ '^[0-9]+$' THEN v_actor_id::integer ELSE NULL END,
        v_request_id, v_prev, v_entry
    );
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION ocr_integrity_ledger_immutable()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'data_integrity_ledger is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS ocr_integrity_ledger_no_update ON data_integrity_ledger;
CREATE TRIGGER ocr_integrity_ledger_no_update
    BEFORE UPDATE OR DELETE ON data_integrity_ledger
    FOR EACH ROW EXECUTE FUNCTION ocr_integrity_ledger_immutable();

REVOKE UPDATE, DELETE ON data_integrity_ledger FROM PUBLIC;
"""


def ensure_ledger(engine: Engine) -> None:
    """Create the ledger and triggers. PostgreSQL only.

    The DDL is idempotent. It is safe to run on every startup.
    """
    if engine.dialect.name != "postgresql":
        logger.info("Database integrity ledger skipped: PostgreSQL is required")
        return

    with engine.begin() as conn:
        # Uvicorn starts several workers at once. Serialise the ledger DDL so
        # two workers cannot drop/create the same trigger concurrently and
        # abort one worker's startup.
        conn.execute(
            text("SELECT pg_advisory_xact_lock(hashtext('ocr.data_integrity_ledger_ddl'))")
        )
        conn.execute(text(_LEDGER_DDL))
        for table in LEDGER_TABLES:
            exists = conn.execute(
                text("SELECT to_regclass(:name) IS NOT NULL"),
                {"name": f"public.{table}"},
            ).scalar()
            if not exists:
                logger.warning("Integrity trigger skipped: table %s is missing", table)
                continue
            trigger = f"ocr_integrity_{table}"
            conn.execute(text(f'DROP TRIGGER IF EXISTS {trigger} ON "{table}"'))
            conn.execute(
                text(
                    f'CREATE TRIGGER {trigger} '
                    f'AFTER INSERT OR UPDATE OR DELETE ON "{table}" '
                    "FOR EACH ROW EXECUTE FUNCTION ocr_integrity_trigger()"
                )
            )
    logger.info(
        "Database integrity ledger ready (%d critical tables)",
        len(LEDGER_TABLES),
    )
