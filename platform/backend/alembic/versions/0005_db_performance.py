"""Database performance: FK indexes, ledger index dedupe, autovacuum.

Revision ID: 0005_db_perf
Revises: 0004_user_avatar
Create Date: 2026-11-09

These changes are additive and do not touch constraints, foreign keys,
unique indexes, triggers, or the integrity ledger chain. They:
  * drop the duplicate model-created ledger indexes (the ledger DDL already
    creates equivalent indexes on table_name and entry_hash),
  * add indexes for foreign-key columns that are filtered directly by the
    application but were only covered as the second column of a composite,
  * lower autovacuum thresholds on update-heavy tables so dead tuples are
    reclaimed promptly after the scheduler's long-lived transaction is gone.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005_db_perf"
down_revision: Union[str, None] = "0004_user_avatar"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_INDEXES = (
    ("ix_course_enrollments_user_id", "course_enrollments", "user_id"),
    ("ix_lab_sessions_lab_id", "lab_sessions", "lab_id"),
    ("ix_lab_completions_lab_id", "lab_completions", "lab_id"),
    ("ix_flag_attempts_lab_id", "flag_attempts", "lab_id"),
    ("ix_course_lab_assignments_lab_id", "course_lab_assignments", "lab_id"),
    ("ix_achievements_course_id", "achievements", "course_id"),
    ("ix_achievements_lab_id", "achievements", "lab_id"),
    ("ix_activity_events_actor_id", "activity_events", "actor_id"),
    ("ix_survey_responses_course_id", "survey_responses", "course_id"),
    ("ix_competition_participants_user_id", "competition_participants", "user_id"),
    ("ix_quiz_attempts_quiz_id", "quiz_attempts", "quiz_id"),
)

_AUTOVACUUM_TABLES = (
    "labs",
    "levels",
    "tracks",
    "courses",
    "course_enrollments",
    "lab_sessions",
    "exercise_quiz_attempts",
    "exercise_quiz_feedback",
    "achievements",
)


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _create_index(name: str, table: str, column: str) -> None:
    # The platform tables are small enough that a transactional index build is
    # brief. If this migration is ever applied to a much larger deployment,
    # build the indexes manually with CREATE INDEX CONCURRENTLY first; the
    # IF NOT EXISTS clause will then skip them here.
    op.execute(f"CREATE INDEX IF NOT EXISTS {name} ON {table} ({column})")


def upgrade() -> None:
    bind = op.get_bind()
    postgres = bind.dialect.name == "postgresql"
    tables = _table_names()

    # The ledger DDL creates ix_data_integrity_ledger_table and
    # ix_data_integrity_ledger_entry. The model's index=True duplicated both.
    op.execute("DROP INDEX IF EXISTS ix_data_integrity_ledger_table_name")
    op.execute("DROP INDEX IF EXISTS ix_data_integrity_ledger_entry_hash")

    for name, table, column in _INDEXES:
        if table in tables:
            _create_index(name, table, column)

    if postgres:
        for table in _AUTOVACUUM_TABLES:
            if table not in tables:
                continue
            op.execute(
                f"ALTER TABLE {table} SET ("
                "autovacuum_vacuum_scale_factor=0.05, "
                "autovacuum_vacuum_threshold=20, "
                "autovacuum_analyze_scale_factor=0.02, "
                "autovacuum_analyze_threshold=20)"
            )


def downgrade() -> None:
    tables = _table_names()
    for name, table, _column in _INDEXES:
        if table in tables:
            op.execute(f"DROP INDEX IF EXISTS {name}")

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_data_integrity_ledger_table_name "
        "ON data_integrity_ledger (table_name)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_data_integrity_ledger_entry_hash "
        "ON data_integrity_ledger (entry_hash)"
    )

    if op.get_bind().dialect.name == "postgresql":
        for table in _AUTOVACUUM_TABLES:
            if table in tables:
                op.execute(f"ALTER TABLE {table} RESET ("
                           "autovacuum_vacuum_scale_factor, "
                           "autovacuum_vacuum_threshold, "
                           "autovacuum_analyze_scale_factor, "
                           "autovacuum_analyze_threshold)")
