"""Two-owner / two-tenant object authorization regression matrix."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import (
    Achievement,
    Competition,
    Course,
    CourseEnrollment,
    LabSession,
    User,
    WireGuardConfig,
)

PASSWORD = "Idor#Matrix123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role="student", tenant="default"):
    suffix = uuid.uuid4().hex[:8]
    row = User(
        username=f"idor_{role}_{suffix}",
        email=f"idor_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id=tenant,
        vpn_registered=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _course(db, instructor, tenant="default"):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    row = Course(
        name=f"IDOR Course {suffix}",
        code=f"ID{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"ID-{suffix}",
        instructor_id=instructor.id,
        institution_id=tenant,
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


@pytest.fixture
def rangebox_session(db_session, test_lab):
    owner = _user(db_session)
    session = LabSession(
        user_id=owner.id,
        lab_id=test_lab.id,
        status="running",
        rangebox_enabled=True,
        started_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    yield owner, session
    db_session.query(LabSession).filter(LabSession.id == session.id).delete()
    db_session.commit()


def test_rangebox_object_id_is_owner_scoped(client, db_session, rangebox_session):
    _owner, session = rangebox_session
    outsider = _user(db_session)

    headers = _headers(client, outsider)
    for suffix in ("lab", "status"):
        response = client.get(
            f"/api/rangebox/{session.id}/{suffix}", headers=headers
        )
        assert response.status_code == 404, (suffix, response.text)


def test_wireguard_config_never_returns_another_users_key(client, db_session):
    owner = _user(db_session)
    outsider = _user(db_session)
    owner_key = f"OWNER-{uuid.uuid4().hex}"
    outsider_key = f"OUTSIDER-{uuid.uuid4().hex}"
    seed = int(uuid.uuid4().hex[:4], 16) % 200 + 20
    db_session.add_all(
        [
            WireGuardConfig(
                user_id=owner.id,
                private_key=owner_key,
                public_key=f"pub-{uuid.uuid4().hex}",
                client_ip=f"10.251.{seed}.10",
            ),
            WireGuardConfig(
                user_id=outsider.id,
                private_key=outsider_key,
                public_key=f"pub-{uuid.uuid4().hex}",
                client_ip=f"10.251.{seed}.11",
            ),
        ]
    )
    db_session.commit()

    response = client.get(
        "/api/labs/vpn-config", headers=_headers(client, outsider)
    )
    assert response.status_code == 200, response.text
    assert owner_key not in response.text


def test_instructor_cannot_access_another_course(client, db_session):
    instructor_a = _user(db_session, "instructor", "tenant-a")
    instructor_b = _user(db_session, "instructor", "tenant-b")
    learner_a = _user(db_session, "student", "tenant-a")
    course_a = _course(db_session, instructor_a, "tenant-a")
    _course(db_session, instructor_b, "tenant-b")
    db_session.add(CourseEnrollment(course_id=course_a.id, user_id=learner_a.id))
    db_session.commit()

    headers = _headers(client, instructor_b)
    checks = (
        f"/api/courses/{course_a.id}/students",
        f"/api/courses/{course_a.id}/report?reason=security%20test",
        f"/api/courses/{course_a.id}/report/{learner_a.id}?reason=security%20test",
        f"/api/analytics/courses/{course_a.id}/overview",
        f"/api/courses/{course_a.id}/reports",
        f"/api/courses/{course_a.id}/students/{learner_a.id}/history",
    )
    for path in checks:
        response = client.get(path, headers=headers)
        assert response.status_code in {403, 404}, (path, response.status_code, response.text)
        assert learner_a.email not in response.text


def test_competition_organizer_scope_and_inactive_visibility(client, db_session):
    organizer_a = _user(db_session, "instructor", "tenant-a")
    organizer_b = _user(db_session, "instructor", "tenant-b")
    now = datetime.now(timezone.utc)
    event = Competition(
        name="Inactive IDOR Event",
        description="test",
        start_at=now - timedelta(days=1),
        end_at=now + timedelta(days=1),
        is_active=False,
        created_by=organizer_a.id,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    headers_b = _headers(client, organizer_b)
    detail = client.get(f"/api/competitions/{event.id}", headers=headers_b)
    assert detail.status_code == 404, detail.text
    update = client.patch(
        f"/api/competitions/{event.id}",
        json={"name": "Hijacked"},
        headers=headers_b,
    )
    assert update.status_code == 403, update.text

    owner_detail = client.get(
        f"/api/competitions/{event.id}", headers=_headers(client, organizer_a)
    )
    assert owner_detail.status_code == 200, owner_detail.text


def test_impersonation_cannot_read_private_or_export_surfaces(client, db_session):
    admin = _user(db_session, "admin")
    target = _user(db_session, "student")
    response = client.post(
        "/api/auth/impersonate",
        json={"target_user_id": target.id},
        headers=_headers(client, admin),
    )
    assert response.status_code == 200, response.text
    imp_headers = {"Authorization": f"Bearer {response.json()['token']}"}

    for path in (
        "/api/labs/vpn-config",
        "/api/profile/summary",
        "/api/consent/",
        "/api/auth/export",
    ):
        blocked = client.get(path, headers=imp_headers)
        assert blocked.status_code == 403, (path, blocked.status_code, blocked.text)


def test_celebration_wall_has_no_stable_learner_identifier(client, db_session):
    owner = _user(db_session)
    viewer = _user(db_session)
    db_session.add(
        Achievement(
            user_id=owner.id,
            achievement_type="first_blood",
            awarded_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
    )
    db_session.commit()

    response = client.get(
        "/api/dashboard/celebrations", headers=_headers(client, viewer)
    )
    assert response.status_code == 200, response.text
    body = response.json()
    for row in body.get("recent", []):
        assert row.get("user_id") is None
    for row in body.get("spotlight", []):
        assert row.get("user_id") is None
    assert owner.email not in response.text
