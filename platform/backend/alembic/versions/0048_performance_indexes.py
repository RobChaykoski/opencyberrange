"""Add indexes for common report, session, and activity queries.

Revision ID: 0048_performance_indexes
Revises: 0047_lab_nice_metadata
Create Date: 2026-11-19
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0048_performance_indexes"
down_revision: Union[str, None] = "0047_lab_nice_metadata"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEXES = (
    (
        "ix_achievements_awarded_at",
        "CREATE INDEX IF NOT EXISTS ix_achievements_awarded_at "
        "ON achievements (awarded_at DESC)",
    ),
    (
        "ix_lab_sessions_started_at",
        "CREATE INDEX IF NOT EXISTS ix_lab_sessions_started_at "
        "ON lab_sessions (started_at DESC)",
    ),
    (
        "ix_assignments_course_id",
        "CREATE INDEX IF NOT EXISTS ix_assignments_course_id "
        "ON assignments (course_id)",
    ),
    (
        "ix_assignment_labs_lab_id",
        "CREATE INDEX IF NOT EXISTS ix_assignment_labs_lab_id "
        "ON assignment_labs (lab_id)",
    ),
    (
        "ix_lab_completions_lab_completed",
        "CREATE INDEX IF NOT EXISTS ix_lab_completions_lab_completed "
        "ON lab_completions (lab_id, completed_at DESC)",
    ),
)


def upgrade() -> None:
    for _name, statement in INDEXES:
        op.execute(statement)


def downgrade() -> None:
    for name, _statement in reversed(INDEXES):
        op.execute(f"DROP INDEX IF EXISTS {name}")
