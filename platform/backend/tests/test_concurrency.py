"""Concurrency and race-condition invariants."""

from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app import database
from app.auth import get_password_hash
from app.models import Course, CourseEnrollment, LabCompletion, LabSession, User
from app.services import db_invariants

PASSWORD = "Correct#Horse7Battery"  # conftest TEST_PASSWORD; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role="student"):
    suffix = uuid.uuid4().hex[:8]
    row = User(
        username=f"race_{role}_{suffix}",
        email=f"race_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role=role,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _course(db, instructor):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    row = Course(
        name=f"Race Course {suffix}",
        code=f"RC{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"RC-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _login(client, user):
    response = client.post(
        "/api/auth/login", data={"username": user.username, "password": PASSWORD}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_double_enrollment_race_creates_one_row(client, db_session):
    db_invariants.apply(database.engine)
    instructor = _user(db_session, "instructor")
    student = _user(db_session)
    course = _course(db_session, instructor)
    headers = _login(client, student)

    def join():
        return client.post(
            "/api/courses/join", json={"invite_code": course.invite_code}, headers=headers
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: join(), range(2)))
    assert sorted(r.status_code for r in responses) == [200, 400]
    rows = db_session.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course.id,
        CourseEnrollment.user_id == student.id,
    ).all()
    assert len(rows) == 1


def test_concurrent_flag_submissions_create_one_completion(
    client, db_session, test_user, test_lab, test_flag
):
    headers = _login(client, test_user)

    def submit():
        return client.post(
            f"/api/exercises/labs/{test_lab.id}/submit-flag",
            json={"flag": test_flag},
            headers=headers,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: submit(), range(2)))
    assert all(r.status_code < 500 for r in responses), [r.text for r in responses]
    rows = db_session.query(LabCompletion).filter(
        LabCompletion.user_id == test_user.id,
        LabCompletion.lab_id == test_lab.id,
    ).all()
    assert len(rows) == 1


def test_database_allows_only_one_active_session_per_user(db_session, test_lab):
    db_invariants.apply(database.engine)
    user = _user(db_session)
    now = datetime.now(timezone.utc)
    first = LabSession(
        user_id=user.id,
        lab_id=test_lab.id,
        status="running",
        started_at=now,
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(first)
    db_session.commit()
    db_session.add(
        LabSession(
            user_id=user.id,
            lab_id=test_lab.id,
            status="starting",
            started_at=now,
            expires_at=now + timedelta(hours=1),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    db_session.query(LabSession).filter(LabSession.id == first.id).delete()
    db_session.commit()


def test_erasure_and_active_request_do_not_produce_a_server_error(
    client, db_session, test_user, auth_headers
):
    def delete():
        return client.request(
            "POST",
            "/api/auth/delete-account",
            json={
                "password": "Correct#Horse7Battery",
                "confirm": "DELETE",
            },
            headers=auth_headers,
        )

    def me():
        return client.get("/api/auth/me", headers=auth_headers)

    with ThreadPoolExecutor(max_workers=2) as pool:
        delete_future = pool.submit(delete)
        me_future = pool.submit(me)
        deleted = delete_future.result()
        active = me_future.result()
    assert deleted.status_code < 500, deleted.text
    assert active.status_code in {200, 401}
    assert db_session.query(User).filter(User.id == test_user.id).first() is None
