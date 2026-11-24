"""Add standalone certification practice sessions.

Revision ID: 0058_practice_sessions
Revises: 0057_achievement_awards
Create Date: 2026-11-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0058_practice_sessions"
down_revision: Union[str, None] = "0057_achievement_awards"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)
    tables = set(inspector.get_table_names())

    if "practice_sessions" not in tables:
        op.create_table(
            "practice_sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "institution_id",
                sa.String(length=64),
                nullable=False,
                server_default=sa.text("'default'"),
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("pathway_id", sa.String(length=64), nullable=False),
            sa.Column("pathway_name", sa.String(length=120), nullable=False),
            sa.Column(
                "mode",
                sa.String(length=16),
                nullable=False,
                server_default="mock",
            ),
            sa.Column("domain_id", sa.String(length=32), nullable=True),
            sa.Column("question_count", sa.Integer(), nullable=False),
            sa.Column("duration_minutes", sa.Integer(), nullable=False),
            sa.Column(
                "pass_mark",
                sa.Integer(),
                nullable=False,
                server_default="70",
            ),
            sa.Column(
                "status",
                sa.String(length=16),
                nullable=False,
                server_default="active",
            ),
            sa.Column(
                "started_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("submitted_at", sa.DateTime(), nullable=True),
            sa.Column("score", sa.Integer(), nullable=True),
            sa.Column("total", sa.Integer(), nullable=True),
            sa.Column("percentage", sa.Float(), nullable=True),
            sa.Column("passed", sa.Boolean(), nullable=True),
            sa.Column(
                "timed_out",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )
        op.create_index(
            "ix_practice_sessions_institution_id",
            "practice_sessions",
            ["institution_id"],
        )
        op.create_index(
            "ix_practice_sessions_user_id",
            "practice_sessions",
            ["user_id"],
        )
        op.create_index(
            "ix_practice_sessions_pathway_id",
            "practice_sessions",
            ["pathway_id"],
        )
        op.create_index(
            "ix_practice_sessions_status",
            "practice_sessions",
            ["status"],
        )
        op.create_index(
            "ix_practice_sessions_user_started",
            "practice_sessions",
            ["user_id", "started_at"],
        )

    if "practice_session_questions" not in tables:
        op.create_table(
            "practice_session_questions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "session_id",
                sa.Integer(),
                sa.ForeignKey("practice_sessions.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("question_id", sa.String(length=64), nullable=False),
            sa.Column("domain_id", sa.String(length=32), nullable=True),
            sa.Column("option_order", sa.JSON(), nullable=False),
            sa.Column("selected_index", sa.Integer(), nullable=True),
            sa.Column("is_correct", sa.Boolean(), nullable=True),
            sa.Column("answered_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint(
                "session_id",
                "position",
                name="uq_practice_session_position",
            ),
        )
        op.create_index(
            "ix_practice_session_questions_session_id",
            "practice_session_questions",
            ["session_id"],
        )
        op.create_index(
            "ix_practice_session_questions_question_id",
            "practice_session_questions",
            ["question_id"],
        )

    from app.services import tenant_rls

    tenant_rls.ensure_tenant_schema(binding)
    tenant_rls.ensure_tenant_rls(binding)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "practice_session_questions" in tables:
        op.drop_table("practice_session_questions")
    if "practice_sessions" in tables:
        op.drop_table("practice_sessions")
