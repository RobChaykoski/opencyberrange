"""Drop any remaining exact-duplicate non-unique indexes.

Revision ID: 0062_index_dedupe
Revises: 0061_index_hygiene
Create Date: 2026-11-24

A restored or long-lived database can accumulate two indexes on the same
columns from different model or migration generations. This migration keeps the
primary key and a unique index when one exists; otherwise it keeps the
lexicographically first index name and drops the rest.
"""

from alembic import op

revision = "0062_index_dedupe"
down_revision = "0061_index_hygiene"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
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
                WHERE c.relnamespace = 'public'::regnamespace
                  AND c.relkind = 'r'
                  AND NOT i.indisprimary
                  AND NOT i.indisunique
                  AND (
                    EXISTS (
                        SELECT 1 FROM pg_index u
                        WHERE u.indrelid = i.indrelid
                          AND u.indisunique
                          AND u.indkey::text = i.indkey::text
                          AND u.indexrelid <> i.indexrelid
                    )
                    OR EXISTS (
                        SELECT 1 FROM pg_index o
                        JOIN pg_class oc ON oc.oid = o.indexrelid
                        WHERE o.indrelid = i.indrelid
                          AND o.indkey::text = i.indkey::text
                          AND NOT o.indisprimary
                          AND oc.relname < ic.relname
                    )
                  )
            LOOP
                EXECUTE format('DROP INDEX IF EXISTS %I', r.index_name);
            END LOOP;
        END $$;
        """
    )


def downgrade() -> None:
    # The dropped indexes were exact duplicates; recreating them would restore
    # only write amplification. Keep the cleanup one-way.
    pass
