"""Drop redundant indexes and add hot-path indexes.

Revision ID: 0061_index_hygiene
Revises: 0060_competency_reviews
Create Date: 2026-11-24

Some restored databases retained legacy non-unique indexes that duplicate a
primary key or a unique constraint. Migration 0005 and 0006 dropped many of
them, but a later restore can reintroduce the old schema. This migration is
idempotent and cleans any database at this revision.

The added indexes cover the instructor course filter and the lab-session FK.
"""

from alembic import op

revision = "0061_index_hygiene"
down_revision = "0060_competency_reviews"
branch_labels = None
depends_on = None


_LEGACY_DUPLICATES = (
    "ix_data_integrity_ledger_table_name",
    "ix_data_integrity_ledger_entry_hash",
    "ix_refresh_tokens_session_id",
    "ix_nice_components_type_code",
    "ix_instance_lab_id",
    "ix_wireguard_configs_user_id",
)


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        # Any non-unique index whose column list is exactly the primary key is
        # pure write amplification. This also covers the legacy ix_*_id names.
        op.execute(
            """
            DO $$
            DECLARE r record;
            BEGIN
                FOR r IN
                    SELECT ic.relname AS index_name
                    FROM pg_index i
                    JOIN pg_class c ON c.oid = i.indrelid
                    JOIN pg_class ic ON ic.oid = i.indexrelid
                    JOIN pg_index p
                      ON p.indrelid = i.indrelid AND p.indisprimary
                    WHERE c.relnamespace = 'public'::regnamespace
                      AND c.relkind = 'r'
                      AND NOT i.indisprimary
                      AND NOT i.indisunique
                      AND i.indkey::text = p.indkey::text
                LOOP
                    EXECUTE format('DROP INDEX IF EXISTS %I', r.index_name);
                END LOOP;
            END $$;
            """
        )

    for name in _LEGACY_DUPLICATES:
        op.execute(f"DROP INDEX IF EXISTS {name}")

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lab_sessions_lab_id "
        "ON lab_sessions (lab_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_courses_instructor_id "
        "ON courses (instructor_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_courses_instructor_id")
    op.execute("DROP INDEX IF EXISTS ix_lab_sessions_lab_id")

    # Restore the explicitly named duplicates. The primary-key duplicates are
    # intentionally not restored: they were never useful and have no consumer.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_data_integrity_ledger_table_name "
        "ON data_integrity_ledger (table_name)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_data_integrity_ledger_entry_hash "
        "ON data_integrity_ledger (entry_hash)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_refresh_tokens_session_id "
        "ON refresh_tokens (session_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_nice_components_type_code "
        "ON nice_components (component_type, code)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_instance_lab_id "
        "ON template_instances (lab_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_wireguard_configs_user_id "
        "ON wireguard_configs (user_id)"
    )
