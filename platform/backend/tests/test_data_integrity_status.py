"""Read-only data-integrity summary used by the admin portal."""

from sqlalchemy import text

from app.database import engine
from app.services.db_integrity import ensure_ledger, ledger_summary


def test_ledger_summary_reports_installed_ledger(db_schema, db_session):
    ensure_ledger(engine)

    # A write through the application engine is attributed to "system" by the
    # trigger, which is enough to prove the summary reads real ledger rows.
    db_session.execute(
        text(
            "INSERT INTO platform_settings (key, value, category) "
            "VALUES ('integrity-summary-test', '1', 'general') "
            "ON CONFLICT (key) DO UPDATE SET value = '1'"
        )
    )
    db_session.commit()

    summary = ledger_summary(engine)

    assert summary["available"] is True
    assert summary["installed"] is True
    assert summary["entries"] >= 1
    assert summary["last_entry_at"]
    assert summary["coverage_tables"] == 16
    assert isinstance(summary["unattributed_7d"], int)
    assert isinstance(summary["unattributed"], list)
