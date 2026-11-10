"""Read-only data-integrity summary used by the admin portal."""

import uuid

from sqlalchemy import create_engine, text

from app.auth import get_password_hash
from app.database import engine
from app.models import User
from app.services.db_integrity import LEDGER_TABLES, ensure_ledger, ledger_summary

TEST_PASSWORD = "Correct#Horse7Battery"


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
    assert summary["coverage_tables"] == len(LEDGER_TABLES)
    assert isinstance(summary["unattributed_7d"], int)
    assert isinstance(summary["unreviewed_7d"], int)
    assert isinstance(summary["unattributed"], list)
    assert isinstance(summary["reviews"], list)


def test_non_admin_cannot_review_integrity_write(client, auth_headers):
    resp = client.post(
        "/api/admin/system/data-integrity/review",
        json={
            "table": "platform_settings",
            "operation": "INSERT",
            "decision": "expected",
            "note": "Unauthorized attempt should not be recorded.",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 403


def test_admin_can_resolve_unattributed_write(client, db_session):
    ensure_ledger(engine)

    suffix = uuid.uuid4().hex[:8]
    admin = User(
        username=f"integrity_admin_{suffix}",
        email=f"integrity_admin_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=True,
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()

    # A separate connection without the app's application_name is recorded as
    # unattributed by the ledger trigger, like a manual psql session.
    manual_engine = create_engine(
        engine.url,
        connect_args={"application_name": "integrity-manual-test"},
    )
    key = f"integrity-review-test-{suffix}"
    try:
        with manual_engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO platform_settings (key, value, category) "
                    "VALUES (:key, '1', 'general')"
                ),
                {"key": key},
            )

        summary = ledger_summary(engine)
        row = next(
            item
            for item in summary["unattributed"]
            if item["table"] == "platform_settings" and item["operation"] == "INSERT"
        )
        assert row["review"] is None

        login = client.post(
            "/api/auth/login",
            data={"username": admin.username, "password": TEST_PASSWORD},
        )
        assert login.status_code == 200, login.text
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        review = client.post(
            "/api/admin/system/data-integrity/review",
            json={
                "table": "platform_settings",
                "operation": "INSERT",
                "decision": "expected",
                "note": "Matched to an approved maintenance-window settings change.",
            },
            headers=headers,
        )
        assert review.status_code == 200, review.text
        assert review.json()["review"]["reviewed_by"] == admin.username

        refreshed = client.get(
            "/api/admin/system/data-integrity", headers=headers
        )
        assert refreshed.status_code == 200, refreshed.text
        body = refreshed.json()
        assert body["unreviewed_7d"] == 0
        assert body["status"] == "ok"
        reviewed = next(
            item
            for item in body["unattributed"]
            if item["table"] == "platform_settings" and item["operation"] == "INSERT"
        )
        assert reviewed["review"]["decision"] == "expected"
        assert reviewed["review"]["reviewed_by"] == admin.username
    finally:
        manual_engine.dispose()
        db_session.query(User).filter(User.id == admin.id).delete()
        db_session.commit()
