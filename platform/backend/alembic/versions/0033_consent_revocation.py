"""Add consent state, revocation jobs, proof audits, and suppressions.

Revision ID: 0033_consent_revocation
Revises: 0032_cyber_dna
Create Date: 2026-11-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0033_consent_revocation"
down_revision: Union[str, None] = "0032_cyber_dna"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())

    if "consent_states" not in tables:
        op.create_table(
            "consent_states",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("consent_type", sa.String(length=32), nullable=False),
            sa.Column(
                "granted", sa.Boolean(), nullable=False, server_default=sa.text("true")
            ),
            sa.Column(
                "version", sa.Integer(), nullable=False, server_default=sa.text("1")
            ),
            sa.Column(
                "revocation_in_progress",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "user_id", "consent_type", name="uq_consent_state_user_type"
            ),
        )
        op.create_index("ix_consent_states_user_id", "consent_states", ["user_id"])
        op.create_index(
            "ix_consent_state_type_granted",
            "consent_states",
            ["consent_type", "granted"],
        )

    if "consent_events" not in tables:
        op.create_table(
            "consent_events",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("consent_type", sa.String(length=32), nullable=False),
            sa.Column("action", sa.String(length=16), nullable=False),
            sa.Column("consent_version", sa.Integer(), nullable=False),
            sa.Column(
                "actor", sa.String(length=16), nullable=False, server_default="self"
            ),
            sa.Column("reason", sa.String(length=500), nullable=True),
            sa.Column(
                "occurred_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
        op.create_index("ix_consent_events_user_id", "consent_events", ["user_id"])
        op.create_index(
            "ix_consent_events_user_time",
            "consent_events",
            ["user_id", "occurred_at"],
        )
        op.create_index(
            "ix_consent_events_type_time",
            "consent_events",
            ["consent_type", "occurred_at"],
        )

    if "consent_revocations" not in tables:
        op.create_table(
            "consent_revocations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("consent_type", sa.String(length=32), nullable=False),
            sa.Column("consent_version", sa.Integer(), nullable=False),
            sa.Column("audit_id", sa.String(length=36), nullable=False),
            sa.Column(
                "status",
                sa.String(length=16),
                nullable=False,
                server_default="pending",
            ),
            sa.Column(
                "requested_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("started_at", sa.DateTime(), nullable=True),
            sa.Column("purge_completed_at", sa.DateTime(), nullable=True),
            sa.Column("verified_at", sa.DateTime(), nullable=True),
            sa.Column(
                "verification_attempts",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
            sa.Column(
                "suppression_recorded",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column("last_error", sa.Text(), nullable=True),
            sa.UniqueConstraint(
                "user_id",
                "consent_type",
                "consent_version",
                name="uq_consent_revocation_version",
            ),
        )
        op.create_index(
            "ix_consent_revocations_user_id", "consent_revocations", ["user_id"]
        )
        op.create_index(
            "ix_consent_revocations_audit_id",
            "consent_revocations",
            ["audit_id"],
            unique=True,
        )
        op.create_index(
            "ix_consent_revocations_status", "consent_revocations", ["status"]
        )

    if "consent_jobs" not in tables:
        op.create_table(
            "consent_jobs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "revocation_id",
                sa.Integer(),
                sa.ForeignKey("consent_revocations.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("consent_type", sa.String(length=32), nullable=False),
            sa.Column("kind", sa.String(length=16), nullable=False),
            sa.Column("service", sa.String(length=32), nullable=False),
            sa.Column("action", sa.String(length=64), nullable=False),
            sa.Column(
                "slot", sa.String(length=16), nullable=False, server_default=""
            ),
            sa.Column(
                "status",
                sa.String(length=16),
                nullable=False,
                server_default="queued",
            ),
            sa.Column(
                "attempts", sa.Integer(), nullable=False, server_default=sa.text("0")
            ),
            sa.Column(
                "available_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("lease_until", sa.DateTime(), nullable=True),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.Column("last_error", sa.Text(), nullable=True),
            sa.UniqueConstraint(
                "revocation_id",
                "kind",
                "service",
                "action",
                "slot",
                name="uq_consent_job_target",
            ),
        )
        op.create_index(
            "ix_consent_jobs_revocation_id", "consent_jobs", ["revocation_id"]
        )
        op.create_index("ix_consent_jobs_user_id", "consent_jobs", ["user_id"])
        op.create_index(
            "ix_consent_jobs_due", "consent_jobs", ["status", "available_at"]
        )

    if "consent_audits" not in tables:
        op.create_table(
            "consent_audits",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("audit_id", sa.String(length=36), nullable=False),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("subject_hash", sa.String(length=64), nullable=False),
            sa.Column("consent_type", sa.String(length=32), nullable=False),
            sa.Column("consent_version", sa.Integer(), nullable=False),
            sa.Column("revoked_at", sa.DateTime(), nullable=False),
            sa.Column(
                "jobs_completed",
                sa.Text(),
                nullable=False,
                server_default=sa.text("'[]'"),
            ),
            sa.Column(
                "verified",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column("verified_at", sa.DateTime(), nullable=True),
            sa.Column(
                "verification_slots",
                sa.Text(),
                nullable=False,
                server_default=sa.text("'[]'"),
            ),
            sa.Column(
                "suppression_recorded",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
        op.create_index(
            "ix_consent_audits_audit_id", "consent_audits", ["audit_id"], unique=True
        )
        op.create_index("ix_consent_audits_user_id", "consent_audits", ["user_id"])
        op.create_index(
            "ix_consent_audits_subject_hash", "consent_audits", ["subject_hash"]
        )
        op.create_index(
            "ix_consent_audits_subject_type",
            "consent_audits",
            ["subject_hash", "consent_type"],
        )

    if "consent_suppressions" not in tables:
        op.create_table(
            "consent_suppressions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("subject_hash", sa.String(length=64), nullable=False),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("consent_type", sa.String(length=32), nullable=False),
            sa.Column("consent_version", sa.Integer(), nullable=False),
            sa.Column(
                "reason",
                sa.String(length=64),
                nullable=False,
                server_default="consent_revoked",
            ),
            sa.Column(
                "recorded_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("cancelled_at", sa.DateTime(), nullable=True),
            sa.Column("ledger_path", sa.String(length=255), nullable=True),
            sa.UniqueConstraint(
                "subject_hash",
                "consent_type",
                "consent_version",
                name="uq_consent_suppression_version",
            ),
        )
        op.create_index(
            "ix_consent_suppressions_subject_hash",
            "consent_suppressions",
            ["subject_hash"],
        )
        op.create_index(
            "ix_consent_suppressions_user_id", "consent_suppressions", ["user_id"]
        )
        op.create_index(
            "ix_consent_suppressions_user_type",
            "consent_suppressions",
            ["user_id", "consent_type"],
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    for table, indexes in (
        (
            "consent_suppressions",
            [
                "ix_consent_suppressions_user_type",
                "ix_consent_suppressions_user_id",
                "ix_consent_suppressions_subject_hash",
            ],
        ),
        (
            "consent_audits",
            [
                "ix_consent_audits_subject_type",
                "ix_consent_audits_subject_hash",
                "ix_consent_audits_user_id",
                "ix_consent_audits_audit_id",
            ],
        ),
        (
            "consent_jobs",
            [
                "ix_consent_jobs_due",
                "ix_consent_jobs_user_id",
                "ix_consent_jobs_revocation_id",
            ],
        ),
        (
            "consent_revocations",
            [
                "ix_consent_revocations_status",
                "ix_consent_revocations_audit_id",
                "ix_consent_revocations_user_id",
            ],
        ),
        (
            "consent_events",
            [
                "ix_consent_events_type_time",
                "ix_consent_events_user_time",
                "ix_consent_events_user_id",
            ],
        ),
        (
            "consent_states",
            ["ix_consent_state_type_granted", "ix_consent_states_user_id"],
        ),
    ):
        if table not in tables:
            continue
        for index in indexes:
            op.drop_index(index, table_name=table)
        op.drop_table(table)
