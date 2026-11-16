"""Security event store, append-only RLS, and admin read API."""

from __future__ import annotations

import json
import uuid

import pytest
from sqlalchemy import text

from app import database
from app.auth import get_password_hash
from app.models import PlatformSetting, SecurityEvent, User
from app.services import security_events

PASSWORD = "Event#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _set(db_session, **values):
    for key, value in values.items():
        row = (
            db_session.query(PlatformSetting)
            .filter(PlatformSetting.key == key)
            .first()
        )
        if row is None:
            row = PlatformSetting(
                key=key,
                value=str(value),
                category="security",
                description="test",
                is_secret=False,
            )
            db_session.add(row)
        else:
            row.value = str(value)
    db_session.commit()


def _user(db_session, role="admin", institution="default", mfa=False):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"event_{role}_{suffix}",
        email=f"event_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id=institution,
        mfa_enabled=mfa,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _headers(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_event_store_records_actor_category_and_redacts_secrets(db_session):
    user = _user(db_session, "student")
    row = security_events.record(
        "auth.password_changed",
        actor=user,
        target_type="user",
        target_id=user.id,
        detail={"password": "do-not-store", "nested": {"token": "also-secret", "ok": 1}},
    )
    assert row is not None
    row = db_session.query(SecurityEvent).filter(SecurityEvent.id == row.id).one()
    assert row.category == "security"
    assert row.severity == "notice"
    assert row.actor_id == user.id
    assert row.actor_username == user.username
    payload = json.loads(row.detail)
    assert payload["password"] == "[redacted]"
    assert payload["nested"]["token"] == "[redacted]"
    assert payload["nested"]["ok"] == 1


def test_http_coverage_records_denials_and_skips_health(client, db_session):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    # /api/does-not-exist is not a sensitive prefix and is not 401/403, so the
    # coverage middleware intentionally skips it.
    rows = db_session.query(SecurityEvent).filter(SecurityEvent.path == "/api/does-not-exist").all()
    assert rows == []

    denied = client.get("/api/admin/security/events")
    assert denied.status_code == 401
    row = (
        db_session.query(SecurityEvent)
        .filter(SecurityEvent.event_type.in_(("http.denied", "authz.denied")))
        .order_by(SecurityEvent.id.desc())
        .first()
    )
    assert row is not None
    assert row.status_code == 401


def test_admin_can_query_and_summarize_events(client, db_session):
    admin = _user(db_session, "admin")
    security_events.record(
        "export.denied",
        outcome="denied",
        severity="warning",
        actor=admin,
        detail={"classification": "Restricted"},
    )
    headers = _headers(client, admin)
    response = client.get(
        "/api/admin/security/events?category=security&limit=10", headers=headers
    )
    assert response.status_code == 200, response.text
    assert response.json()["events"]
    summary = client.get("/api/admin/security/events/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["by_severity"]["warning"] >= 1


def test_student_cannot_read_the_security_event_store(client, db_session):
    student = _user(db_session, "student")
    response = client.get(
        "/api/admin/security/events", headers=_headers(client, student)
    )
    assert response.status_code == 403


def test_admin_action_logger_mirrors_into_the_store(db_session):
    from app.services.audit import log_admin_action

    admin = _user(db_session, "admin")
    log_admin_action(
        action="USER_UPDATED",
        admin_user_id=admin.id,
        admin_username=admin.username,
        target_type="user",
        target_id=42,
        details={"password": "never-store", "field": "email"},
    )
    row = (
        db_session.query(SecurityEvent)
        .filter(SecurityEvent.event_type == "admin.action")
        .order_by(SecurityEvent.id.desc())
        .first()
    )
    assert row is not None
    assert row.category == "audit"
    assert row.action == "USER_UPDATED"
    payload = json.loads(row.detail)
    assert payload["password"] == "[redacted]"


def test_repeated_failures_raise_a_deduplicated_alert(db_session):
    from app.services import security_alerts

    _set(
        db_session,
        security_alert_enabled="true",
        security_alert_window_minutes="15",
        security_alert_threshold="2",
    )
    for _ in range(2):
        security_events.record(
            "auth.login_failed",
            outcome="failure",
            actor_username="alert-probe",
            ip_address="203.0.113.50",
            detail={"reason": "invalid_credentials"},
        )
    found = security_alerts.scan(db_session)
    assert any(item["event_type"] == "auth.login_failed" for item in found)

    first = security_alerts.scan_and_record(db_session)
    assert first["recorded"] >= 1
    second = security_alerts.scan_and_record(db_session)
    assert second["recorded"] == 0

    row = (
        db_session.query(SecurityEvent)
        .filter(SecurityEvent.event_type == "security.alert")
        .order_by(SecurityEvent.id.desc())
        .first()
    )
    assert row is not None
    assert row.severity in {"warning", "critical"}


@pytest.mark.skipif(
    database.engine.dialect.name != "postgresql",
    reason="PostgreSQL row-level security",
)
def test_rls_denies_update_delete_and_scopes_tenants(db_session):
    security_events.ensure_rls(database.engine)
    row = security_events.record(
        "security.events_read",
        actor_id=None,
        actor_username="probe",
        institution_id="tenant-a",
        detail={"probe": True},
    )
    assert row is not None
    event_id = row.id

    with database.engine.connect() as conn:
        trans = conn.begin()
        conn.execute(
            text(
                "DO $$ BEGIN "
                "IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ocr_rls_probe') "
                "THEN CREATE ROLE ocr_rls_probe NOLOGIN; END IF; "
                "END $$"
            )
        )
        conn.execute(text("GRANT USAGE ON SCHEMA public TO ocr_rls_probe"))
        conn.execute(
            text(
                "GRANT SELECT, INSERT, UPDATE, DELETE ON security_events "
                "TO ocr_rls_probe"
            )
        )
        conn.execute(text("SET LOCAL ROLE ocr_rls_probe"))
        conn.execute(text("SET LOCAL ocr.institution_id = 'tenant-b'"))
        assert (
            conn.execute(
                text("SELECT COUNT(*) FROM security_events WHERE id = :id"),
                {"id": event_id},
            ).scalar()
            == 0
        )
        conn.execute(text("SET LOCAL ocr.institution_id = 'tenant-a'"))
        assert (
            conn.execute(
                text("SELECT COUNT(*) FROM security_events WHERE id = :id"),
                {"id": event_id},
            ).scalar()
            == 1
        )
        updated = conn.execute(
            text("UPDATE security_events SET severity = 'critical' WHERE id = :id"),
            {"id": event_id},
        )
        deleted = conn.execute(
            text("DELETE FROM security_events WHERE id = :id"), {"id": event_id}
        )
        assert updated.rowcount == 0
        assert deleted.rowcount == 0
        trans.commit()

    db_session.expire_all()
    unchanged = db_session.query(SecurityEvent).filter(SecurityEvent.id == event_id).one()
    assert unchanged.severity == "info"
