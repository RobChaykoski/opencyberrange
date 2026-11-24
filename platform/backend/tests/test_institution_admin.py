"""Institution admins are confined to their own tenant."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import ActivityEvent, Course, User

PASSWORD = "Inst#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role, institution):
    suffix = uuid.uuid4().hex[:8]
    row = User(
        username=f"inst_{role}_{suffix}",
        email=f"inst_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id=institution,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _course(db, instructor, institution):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    row = Course(
        name=f"Institution Course {suffix}",
        code=f"IN{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"IN-{suffix}",
        instructor_id=instructor.id,
        institution_id=institution,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _headers(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_institution_admin_lists_only_own_users(client, db_session):
    admin_a = _user(db_session, "institution_admin", "tenant-a")
    admin_b = _user(db_session, "institution_admin", "tenant-b")
    learner_a = _user(db_session, "student", "tenant-a")
    learner_b = _user(db_session, "student", "tenant-b")

    response = client.get("/api/admin/users", headers=_headers(client, admin_a))
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()}
    assert admin_a.id in ids
    assert learner_a.id in ids
    assert admin_b.id not in ids
    assert learner_b.id not in ids

    denied = client.get(
        f"/api/admin/users/{learner_b.id}", headers=_headers(client, admin_a)
    )
    assert denied.status_code == 404


def test_institution_admin_stats_are_tenant_scoped(client, db_session):
    tenant = f"stats-{uuid.uuid4().hex[:8]}"
    other = f"other-{uuid.uuid4().hex[:8]}"
    admin_a = _user(db_session, "institution_admin", tenant)
    _user(db_session, "student", tenant)
    _user(db_session, "student", other)

    response = client.get("/api/admin/stats", headers=_headers(client, admin_a))
    assert response.status_code == 200, response.text
    assert response.json()["total_users"] == 2


def test_institution_admin_sees_only_own_courses(client, db_session):
    admin_a = _user(db_session, "institution_admin", "tenant-a")
    instructor_a = _user(db_session, "instructor", "tenant-a")
    instructor_b = _user(db_session, "instructor", "tenant-b")
    course_a = _course(db_session, instructor_a, "tenant-a")
    course_b = _course(db_session, instructor_b, "tenant-b")

    response = client.get("/api/courses/", headers=_headers(client, admin_a))
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["courses"]}
    assert course_a.id in ids
    assert course_b.id not in ids

    denied = client.get(
        f"/api/courses/{course_b.id}", headers=_headers(client, admin_a)
    )
    assert denied.status_code == 403


def test_institution_admin_cannot_promote_to_platform_admin(client, db_session):
    admin_a = _user(db_session, "institution_admin", "tenant-a")
    learner = _user(db_session, "student", "tenant-a")
    response = client.put(
        f"/api/admin/users/{learner.id}",
        json={"role": "admin", "is_admin": True},
        headers=_headers(client, admin_a),
    )
    assert response.status_code == 403

def test_institution_admin_pending_and_locked_are_scoped(client, db_session):
    admin_a = _user(db_session, "institution_admin", "tenant-a")
    pending_a = _user(db_session, "student", "tenant-a")
    pending_b = _user(db_session, "student", "tenant-b")
    locked_a = _user(db_session, "student", "tenant-a")
    locked_b = _user(db_session, "student", "tenant-b")
    pending_a.is_approved = False
    pending_b.is_approved = False
    locked_a.is_locked = True
    locked_b.is_locked = True
    db_session.commit()

    headers = _headers(client, admin_a)
    pending = client.get("/api/admin/users/pending", headers=headers)
    assert pending.status_code == 200, pending.text
    pending_ids = {row["id"] for row in pending.json()}
    assert pending_a.id in pending_ids
    assert pending_b.id not in pending_ids

    locked = client.get("/api/admin/users/locked", headers=headers)
    assert locked.status_code == 200, locked.text
    locked_ids = {row["id"] for row in locked.json()}
    assert locked_a.id in locked_ids
    assert locked_b.id not in locked_ids


def test_institution_admin_user_details_are_scoped(client, db_session):
    admin_a = _user(db_session, "institution_admin", "tenant-a")
    learner_b = _user(db_session, "student", "tenant-b")
    response = client.get(
        f"/api/admin/users/{learner_b.id}/details",
        headers=_headers(client, admin_a),
    )
    assert response.status_code == 404


def test_institution_admin_activity_is_scoped(client, db_session):
    admin_a = _user(db_session, "institution_admin", "tenant-a")
    actor_a = _user(db_session, "student", "tenant-a")
    actor_b = _user(db_session, "student", "tenant-b")
    event_a = ActivityEvent(event_type="login", actor_id=actor_a.id)
    event_b = ActivityEvent(event_type="login", actor_id=actor_b.id)
    db_session.add_all([event_a, event_b])
    db_session.commit()

    response = client.get("/api/admin/activity", headers=_headers(client, admin_a))
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["events"]}
    assert event_a.id in ids
    assert event_b.id not in ids
