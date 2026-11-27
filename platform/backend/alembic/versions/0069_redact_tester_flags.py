"""Redact plaintext lab flags from stored exercise-test results.

Revision ID: 0069_redact_tester_flags
Revises: 0068_mfa_replay_guard
Create Date: 2026-11-27

The exercise tester discovers a lab's plaintext flag to prove it is solvable.
Older code tracked that value in the per-section lines and persisted them as
``sections_json``, where any instructor who can read tester results could see
the answer. New runs redact flags before they are tracked; this migration
scrubs rows written before the fix.
"""

from alembic import op

revision = "0069_redact_tester_flags"
down_revision = "0068_mfa_replay_guard"
branch_labels = None
depends_on = None

# Matches the flag format enforced by the lab builder: OCR{...}
_FLAG_PATTERN = r"OCR\{[^}\n]*\}"


def upgrade() -> None:
    # A downgrade cannot restore the plaintext, so this is a one-way scrub of
    # data that should never have been written.
    op.execute(
        f"""
        UPDATE exercise_test_results
           SET sections_json = regexp_replace(
                   sections_json, '{_FLAG_PATTERN}', 'OCR{{redacted}}', 'g'
               )
         WHERE sections_json ~ '{_FLAG_PATTERN}'
        """
    )


def downgrade() -> None:
    # Irreversible by design: the removed values are lab answers.
    pass
