"""Admin activity-log export and clear endpoints."""

import uuid
from datetime import datetime, timedelta, timezone

from app.auth import get_password_hash
from app.models import ActivityEvent, User

PASSWORD = "Admin#Pass123"


def _make_admin(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    admin = User(
        username=f"pytest_admin_{suffix}",
        email=f"pytest_admin_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=True,
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    resp = client.post(
        "/api/auth/login",
        data={"username": admin.username, "password": PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return admin, {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_activity_export_and_clear(client, db_session):
    admin, headers = _make_admin(client, db_session)
    old_event = None
    try:
        old_event = ActivityEvent(
            event_type="lab_started",
            actor_id=admin.id,
            target_type="lab",
            target_label="export-clear-test",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=2),
        )
        db_session.add(old_event)
        db_session.commit()

        exported = client.get(
            "/api/admin/activity/export?format=json", headers=headers
        )
        assert exported.status_code == 200, exported.text
        assert "attachment" in exported.headers["content-disposition"]
        assert "export-clear-test" in exported.text

        bad = client.post(
            "/api/admin/activity/clear",
            headers=headers,
            json={"confirm": "NO"},
        )
        assert bad.status_code == 400

        cleared = client.post(
            "/api/admin/activity/clear",
            headers=headers,
            json={"confirm": "CLEAR", "older_than_days": 1},
        )
        assert cleared.status_code == 200, cleared.text
        assert cleared.json()["deleted"] >= 1

        remaining = client.get(
            "/api/admin/activity?page=1&per_page=20", headers=headers
        )
        assert remaining.status_code == 200
        assert any(
            event["event_type"] == "activity_log_cleared"
            for event in remaining.json()["events"]
        )
    finally:
        db_session.query(ActivityEvent).filter(
            ActivityEvent.actor_id == admin.id
        ).delete(synchronize_session=False)
        db_session.query(ActivityEvent).filter(
            ActivityEvent.target_label == "export-clear-test"
        ).delete(synchronize_session=False)
        db_session.query(User).filter(User.id == admin.id).delete()
        db_session.commit()
