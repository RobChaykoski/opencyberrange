"""Add model-declared foreign-key indexes missing from restored databases.

Revision ID: 0063_missing_fk_indexes
Revises: 0062_index_dedupe
Create Date: 2026-11-24

Several models declare ``index=True`` on a foreign key, but restored databases
predate those declarations. Autogenerate reports them as missing. This migration
adds the legitimate ones with ``IF NOT EXISTS`` so it is safe on any database at
this revision.
"""

from alembic import op

revision = "0063_missing_fk_indexes"
down_revision = "0062_index_dedupe"
branch_labels = None
depends_on = None


_INDEXES = (
    ("ix_achievements_course_id", "achievements", "course_id"),
    ("ix_achievements_lab_id", "achievements", "lab_id"),
    ("ix_activity_events_actor_id", "activity_events", "actor_id"),
    ("ix_competition_participants_user_id", "competition_participants", "user_id"),
    ("ix_course_enrollments_user_id", "course_enrollments", "user_id"),
    ("ix_course_lab_assignments_lab_id", "course_lab_assignments", "lab_id"),
    ("ix_flag_attempts_lab_id", "flag_attempts", "lab_id"),
    ("ix_lab_completions_lab_id", "lab_completions", "lab_id"),
    ("ix_quiz_attempts_quiz_id", "quiz_attempts", "quiz_id"),
    ("ix_survey_responses_course_id", "survey_responses", "course_id"),
)


def upgrade() -> None:
    for name, table, column in _INDEXES:
        op.execute(
            f"CREATE INDEX IF NOT EXISTS {name} ON {table} ({column})"
        )


def downgrade() -> None:
    for name, _table, _column in _INDEXES:
        op.execute(f"DROP INDEX IF EXISTS {name}")
