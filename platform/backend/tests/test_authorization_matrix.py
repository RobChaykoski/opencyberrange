"""Formal role and cross-tenant authorization matrix.

This is a boundary test, not a feature test. It proves that a student cannot
reach instructor or admin surfaces, an instructor cannot reach another
instructor's course analytics, and unauthenticated callers cannot reach
authenticated APIs.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import (
    Course, CourseEnrollment, CourseLabAssignment, Lab, Level, Track, User,
)

PASSWORD = "Matrix#Pass123"
pytestmark = pytest.mark.db


def _make_user(db_session, role: str, *, is_admin: bool = False) -> User:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"matrix_{role}_{suffix}",
        email=f"matrix_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=is_admin,
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _headers(client, user: User) -> dict:
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _course(db_session, instructor: User) -> Course:
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    course = Course(
        name=f"Matrix Course {suffix}",
        code=f"MX{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"MX-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=10),
        end_date=now + timedelta(days=10),
        is_active=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


def _lab(db_session) -> Lab:
    suffix = uuid.uuid4().hex[:8]
    track = Track(name=f"Matrix Track {suffix}", slug=f"matrix-{suffix}", is_active=True)
    db_session.add(track)
    db_session.flush()
    level = Level(track_id=track.id, level_number=1, name="Matrix Level")
    db_session.add(level)
    db_session.flush()
    lab = Lab(
        name=f"Matrix Lab {suffix}",
        slug=f"matrix-lab-{suffix}",
        description="Authorization matrix lab",
        compose_file="services: {}\n",
        is_active=True,
        visibility="public",
        level_id=level.id,
        duration_minutes=30,
        difficulty="beginner",
    )
    db_session.add(lab)
    db_session.commit()
    db_session.refresh(lab)
    return lab


def test_unauthenticated_calls_are_rejected(client):
    for path in (
        "/api/auth/me",
        "/api/admin/users",
        "/api/admin/system/data-integrity",
        "/api/settings/",
        "/api/instructor/courses",
    ):
        response = client.get(path)
        assert response.status_code == 401, (path, response.status_code)


def test_student_cannot_reach_staff_or_admin_surfaces(client, db_session):
    student = _make_user(db_session, "student")
    headers = _headers(client, student)

    for path in (
        "/api/admin/users",
        "/api/admin/stats",
        "/api/settings/",
        "/api/instructor/courses",
        "/api/admin/rangebox-capacity",
        "/api/admin/users/export?reason=matrix-test",
        "/api/admin/activity/export?format=json&reason=matrix-test",
        "/api/admin/system/backups",
        "/api/admin/system/data-integrity",
        "/api/analytics/reports/export.pdf?reason=matrix-test",
    ):
        response = client.get(path, headers=headers)
        assert response.status_code == 403, (path, response.status_code, response.text)


def test_instructor_cannot_reach_admin_surfaces(client, db_session):
    instructor = _make_user(db_session, "instructor")
    headers = _headers(client, instructor)

    for path in (
        "/api/admin/users",
        "/api/settings/",
        "/api/admin/rangebox-capacity",
        "/api/admin/users/export?reason=matrix-test",
        "/api/admin/activity/export?format=json&reason=matrix-test",
        "/api/admin/system/backups",
        "/api/admin/system/data-integrity",
    ):
        response = client.get(path, headers=headers)
        assert response.status_code == 403, (path, response.status_code, response.text)


def test_instructor_can_export_owned_course_report(client, db_session):
    """Instructor reports are scoped to owned courses, not admin-wide data."""
    instructor = _make_user(db_session, "instructor")
    headers = _headers(client, instructor)

    response = client.get(
        "/api/analytics/reports/export.pdf?reason=matrix-test",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.content.startswith(b"%PDF")


def test_instructor_only_sees_own_course_analytics(client, db_session):
    owner = _make_user(db_session, "instructor")
    outsider = _make_user(db_session, "instructor")
    student = _make_user(db_session, "student")
    course = _course(db_session, owner)
    db_session.add(CourseEnrollment(course_id=course.id, user_id=student.id))
    db_session.commit()
    _lab(db_session)

    owner_headers = _headers(client, owner)
    outsider_headers = _headers(client, outsider)
    student_headers = _headers(client, student)

    allowed = client.get(
        f"/api/analytics/courses/{course.id}/overview", headers=owner_headers
    )
    assert allowed.status_code == 200, allowed.text

    denied = client.get(
        f"/api/analytics/courses/{course.id}/overview", headers=outsider_headers
    )
    assert denied.status_code == 403, denied.text

    student_denied = client.get(
        f"/api/analytics/courses/{course.id}/overview", headers=student_headers
    )
    assert student_denied.status_code == 403, student_denied.text


def test_instructor_cannot_read_another_instructors_course_exports(client, db_session):
    owner = _make_user(db_session, "instructor")
    outsider = _make_user(db_session, "instructor")
    student = _make_user(db_session, "student")
    course = _course(db_session, owner)
    lab = _lab(db_session)
    db_session.add(CourseEnrollment(course_id=course.id, user_id=student.id))
    db_session.add(CourseLabAssignment(course_id=course.id, lab_id=lab.id))
    db_session.commit()

    owner_headers = _headers(client, owner)
    outsider_headers = _headers(client, outsider)
    student_headers = _headers(client, student)
    reason = "matrix-export-test"

    paths = (
        f"/api/courses/{course.id}/report?reason={reason}",
        f"/api/courses/{course.id}/report/{student.id}?reason={reason}",
        f"/api/courses/{course.id}/students/{student.id}/labs/{lab.id}/attempts",
        f"/api/dashboard/instructor/report?format=csv&reason={reason}&course_id={course.id}",
        f"/api/dashboard/instructor/report?format=csv&reason={reason}&user_id={student.id}",
    )
    for path in paths:
        for headers in (outsider_headers, student_headers):
            response = client.get(path, headers=headers)
            assert response.status_code == 403, (
                path, response.status_code, response.text,
            )

    # The owner still gets the same dashboard export the UI offers.
    allowed = client.get(
        f"/api/dashboard/instructor/report?format=csv&reason={reason}&course_id={course.id}",
        headers=owner_headers,
    )
    assert allowed.status_code == 200, allowed.text
    assert "text/csv" in allowed.headers["content-type"]


def test_admin_can_reach_admin_surface(client, db_session):
    admin = _make_user(db_session, "admin", is_admin=True)
    headers = _headers(client, admin)

    response = client.get("/api/admin/users", headers=headers)
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_instructor_can_reach_instructor_surface(client, db_session):
    instructor = _make_user(db_session, "instructor")
    headers = _headers(client, instructor)

    response = client.get("/api/instructor/courses", headers=headers)
    assert response.status_code == 200, response.text


def test_public_endpoints_do_not_require_auth(client):
    assert client.get("/api/version").status_code == 200
    # A malformed certificate ID is rejected by the format check, not by auth.
    assert (
        client.get("/api/exercises/verify/certificate/not-a-certificate").status_code
        == 400
    )
