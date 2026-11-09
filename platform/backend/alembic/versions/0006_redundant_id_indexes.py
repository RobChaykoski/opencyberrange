"""Drop redundant single-column indexes on primary-key ``id`` columns.

Revision ID: 0006_id_indexes
Revises: 0005_db_perf
Create Date: 2026-11-09

Every table's ``id`` column was declared ``primary_key=True, index=True``.
The primary key already has a btree index, so these extra non-unique indexes
only add write amplification. They are not constraints and dropping them
cannot affect referential integrity.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0006_id_indexes"
down_revision: Union[str, None] = "0005_db_perf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_ID_INDEXES = (
    ("ix_achievement_celebrations_id", "achievement_celebrations"),
    ("ix_achievements_id", "achievements"),
    ("ix_activity_events_id", "activity_events"),
    ("ix_assignment_labs_id", "assignment_labs"),
    ("ix_assignments_id", "assignments"),
    ("ix_competition_labs_id", "competition_labs"),
    ("ix_competition_participants_id", "competition_participants"),
    ("ix_competition_sponsors_id", "competition_sponsors"),
    ("ix_competitions_id", "competitions"),
    ("ix_course_completion_resets_id", "course_completion_resets"),
    ("ix_course_enrollments_id", "course_enrollments"),
    ("ix_course_feedback_id", "course_feedback"),
    ("ix_course_lab_assignments_id", "course_lab_assignments"),
    ("ix_courses_id", "courses"),
    ("ix_custom_achievements_id", "custom_achievements"),
    ("ix_data_integrity_ledger_id", "data_integrity_ledger"),
    ("ix_exercise_gen_items_id", "exercise_gen_items"),
    ("ix_exercise_gen_jobs_id", "exercise_gen_jobs"),
    ("ix_exercise_pulse_surveys_id", "exercise_pulse_surveys"),
    ("ix_exercise_quiz_attempts_id", "exercise_quiz_attempts"),
    ("ix_exercise_quiz_feedback_id", "exercise_quiz_feedback"),
    ("ix_exercise_reactions_id", "exercise_reactions"),
    ("ix_exercise_templates_id", "exercise_templates"),
    ("ix_exercise_test_results_id", "exercise_test_results"),
    ("ix_flag_attempts_id", "flag_attempts"),
    ("ix_instructor_api_keys_id", "instructor_api_keys"),
    ("ix_lab_completions_id", "lab_completions"),
    ("ix_lab_sessions_id", "lab_sessions"),
    ("ix_labs_id", "labs"),
    ("ix_level_quizzes_id", "level_quizzes"),
    ("ix_levels_id", "levels"),
    ("ix_platform_settings_id", "platform_settings"),
    ("ix_quiz_attempts_id", "quiz_attempts"),
    ("ix_quiz_questions_id", "quiz_questions"),
    ("ix_studio_pending_review_id", "studio_pending_review"),
    ("ix_survey_attachments_id", "survey_attachments"),
    ("ix_survey_consent_events_id", "survey_consent_events"),
    ("ix_survey_responses_id", "survey_responses"),
    ("ix_surveys_id", "surveys"),
    ("ix_template_instances_id", "template_instances"),
    ("ix_tracks_id", "tracks"),
    ("ix_users_id", "users"),
    ("ix_wireguard_configs_id", "wireguard_configs"),
)


def _tables() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    tables = _tables()
    for index_name, table_name in _ID_INDEXES:
        if table_name in tables:
            op.execute(f"DROP INDEX IF EXISTS {index_name}")


def downgrade() -> None:
    tables = _tables()
    for index_name, table_name in _ID_INDEXES:
        if table_name in tables:
            op.execute(
                f"CREATE INDEX IF NOT EXISTS {index_name} "
                f"ON {table_name} (id)"
            )
