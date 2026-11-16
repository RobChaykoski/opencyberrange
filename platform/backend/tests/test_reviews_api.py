"""Human review requests: learner submission, manager listing, decisions."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import Course, CourseEnrollment, CourseLabAssignment, User

# Test-only login credential; security-delta: allow credential-like assignment
PASSWORD = "Review#Pass123"
pytestmark = pytest.mark.db


def _make_user(db_session, role):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"review_{role}_{suffix}",
        email=f"review_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
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


def _course(db_session, instructor):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    course = Course(
        name=f"Review Course {suffix}",
        code=f"RV{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"RV-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=10),
        end_date=now + timedelta(days=10),
        is_active=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


def test_review_request_listing_and_decision(client, db_session, test_lab):
    owner = _make_user(db_session, "instructor")
    outsider = _make_user(db_session, "instructor")
    student = _make_user(db_session, "student")
    course = _course(db_session, owner)
    db_session.add(CourseEnrollment(course_id=course.id, user_id=student.id))
    db_session.add(CourseLabAssignment(course_id=course.id, lab_id=test_lab.id))
    db_session.commit()

    student_headers = _headers(client, student)
    owner_headers = _headers(client, owner)

    unauthenticated = client.post(
        "/api/reviews",
        json={
            "lab_id": test_lab.id,
            "course_id": course.id,
            "reason": "The flag was rejected",
        },
    )
    assert unauthenticated.status_code == 401

    created = client.post(
        "/api/reviews",
        json={
            "lab_id": test_lab.id,
            "reason": "I believe the flag was rejected in error",
            "source": "flag",
        },
        headers=student_headers,
    )
    assert created.status_code == 201, created.text
    review = created.json()
    assert review["status"] == "pending"
    assert review["course_id"] == course.id
    assert review["username"] == student.username
    assert review["rule_version"] == "deterministic-v1"
    assert review["primary_factors"]["attempts"] == 0
    assert review["primary_factors"]["completed"] is False
    assert review["requested_at"] is not None
    review_id = review["id"]

    duplicate = client.post(
        "/api/reviews",
        json={"lab_id": test_lab.id, "reason": "Please check this again"},
        headers=student_headers,
    )
    assert duplicate.status_code == 409

    mine = client.get("/api/reviews/mine", headers=student_headers)
    assert mine.status_code == 200, mine.text
    assert [row["id"] for row in mine.json()["reviews"]] == [review_id]

    listed = client.get(
        f"/api/courses/{course.id}/reviews?status=pending", headers=owner_headers
    )
    assert listed.status_code == 200, listed.text
    row = listed.json()["reviews"][0]
    assert row["username"] == student.username
    assert row["lab_name"] == test_lab.name

    for headers in (_headers(client, outsider), student_headers):
        denied = client.get(
            f"/api/courses/{course.id}/reviews", headers=headers
        )
        assert denied.status_code == 403, denied.text

    for headers in (student_headers, _headers(client, outsider)):
        denied = client.put(
            f"/api/reviews/{review_id}/decision",
            json={"status": "approved"},
            headers=headers,
        )
        assert denied.status_code == 403, denied.text

    decided = client.put(
        f"/api/reviews/{review_id}/decision",
        json={"status": "approved", "note": " Verified manually "},
        headers=owner_headers,
    )
    assert decided.status_code == 200, decided.text
    body = decided.json()
    assert body["status"] == "approved"
    assert body["decision_note"] == "Verified manually"
    assert body["decided_at"] is not None

    repeated = client.put(
        f"/api/reviews/{review_id}/decision",
        json={"status": "rejected"},
        headers=owner_headers,
    )
    assert repeated.status_code == 409

    approved = client.get(
        f"/api/courses/{course.id}/reviews?status=approved", headers=owner_headers
    )
    assert [row["id"] for row in approved.json()["reviews"]] == [review_id]
    pending = client.get(
        f"/api/courses/{course.id}/reviews?status=pending", headers=owner_headers
    )
    assert pending.json()["reviews"] == []

    second = client.post(
        "/api/reviews",
        json={"lab_id": test_lab.id, "reason": "Please re-check the evidence"},
        headers=student_headers,
    )
    assert second.status_code == 201, second.text
    second_id = second.json()["id"]

    invalid = client.put(
        f"/api/reviews/{second_id}/decision",
        json={"status": "maybe"},
        headers=owner_headers,
    )
    assert invalid.status_code == 422

    rejected = client.put(
        f"/api/reviews/{second_id}/decision",
        json={"status": "rejected", "note": "Evidence does not support an override"},
        headers=owner_headers,
    )
    assert rejected.status_code == 200, rejected.text
    assert rejected.json()["status"] == "rejected"


def test_review_request_boundaries(client, db_session, test_lab):
    student = _make_user(db_session, "student")
    admin = _make_user(db_session, "admin")
    owner = _make_user(db_session, "instructor")
    course = _course(db_session, owner)

    student_headers = _headers(client, student)
    admin_headers = _headers(client, admin)

    unknown_lab = client.post(
        "/api/reviews",
        json={"lab_id": 99999999, "reason": "Exercise does not exist"},
        headers=student_headers,
    )
    assert unknown_lab.status_code == 404

    not_enrolled = client.post(
        "/api/reviews",
        json={
            "lab_id": test_lab.id,
            "course_id": course.id,
            "reason": "Enrolled somewhere else",
        },
        headers=student_headers,
    )
    assert not_enrolled.status_code == 403

    too_short = client.post(
        "/api/reviews",
        json={"lab_id": test_lab.id, "reason": "no"},
        headers=student_headers,
    )
    assert too_short.status_code == 422

    unassigned = client.post(
        "/api/reviews",
        json={"lab_id": test_lab.id, "reason": "Please review this exercise"},
        headers=student_headers,
    )
    assert unassigned.status_code == 201, unassigned.text
    assert unassigned.json()["course_id"] is None
    review_id = unassigned.json()["id"]

    admin_listing = client.get(
        f"/api/courses/{course.id}/reviews", headers=admin_headers
    )
    assert admin_listing.status_code == 200, admin_listing.text
    assert admin_listing.json()["reviews"] == []

    decided = client.put(
        f"/api/reviews/{review_id}/decision",
        json={"status": "approved", "note": "Course-less review"},
        headers=admin_headers,
    )
    assert decided.status_code == 200, decided.text
    assert decided.json()["status"] == "approved"
