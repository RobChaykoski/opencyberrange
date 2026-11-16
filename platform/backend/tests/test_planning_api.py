"""Course planning APIs: cohorts, exercise sets, requirements, and coverage."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import Course, CourseEnrollment, LabCompletion, User

# Test-only login credential; security-delta: allow credential-like assignment
PASSWORD = "Planning#Pass123"
pytestmark = pytest.mark.db


def _make_user(db_session, role):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"planning_{role}_{suffix}",
        email=f"planning_{role}_{suffix}@example.org",
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
        name=f"Planning Course {suffix}",
        code=f"PL{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"PL-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=10),
        end_date=now + timedelta(days=10),
        is_active=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


def _enroll(db_session, course, user):
    db_session.add(CourseEnrollment(course_id=course.id, user_id=user.id))
    db_session.commit()


def test_planning_requires_course_manager(client, db_session):
    owner = _make_user(db_session, "instructor")
    outsider = _make_user(db_session, "instructor")
    student = _make_user(db_session, "student")
    course = _course(db_session, owner)

    unauthenticated = client.get(f"/api/courses/{course.id}/planning")
    assert unauthenticated.status_code == 401

    owner_headers = _headers(client, owner)
    allowed = client.get(f"/api/courses/{course.id}/planning", headers=owner_headers)
    assert allowed.status_code == 200, allowed.text

    for user in (outsider, student):
        headers = _headers(client, user)
        denied = client.get(f"/api/courses/{course.id}/planning", headers=headers)
        assert denied.status_code == 403, denied.text
        denied_write = client.post(
            f"/api/courses/{course.id}/cohorts",
            json={"name": "Denied Cohort"},
            headers=headers,
        )
        assert denied_write.status_code == 403, denied_write.text

    missing = client.get("/api/courses/99999999/planning", headers=owner_headers)
    assert missing.status_code == 404


def test_cohort_lifecycle_and_members(client, db_session):
    owner = _make_user(db_session, "instructor")
    first = _make_user(db_session, "student")
    second = _make_user(db_session, "student")
    outsider = _make_user(db_session, "student")
    course = _course(db_session, owner)
    for user in (first, second):
        _enroll(db_session, course, user)
    headers = _headers(client, owner)

    created = client.post(
        f"/api/courses/{course.id}/cohorts",
        json={"name": "Section A", "description": " Morning ", "is_default": True},
        headers=headers,
    )
    assert created.status_code == 201, created.text
    cohort_id = created.json()["id"]
    assert created.json()["is_default"] is True

    duplicate = client.post(
        f"/api/courses/{course.id}/cohorts",
        json={"name": " section a "},
        headers=headers,
    )
    assert duplicate.status_code == 409

    planning = client.get(f"/api/courses/{course.id}/planning", headers=headers)
    assert planning.status_code == 200, planning.text
    body = planning.json()
    assert body["cohort_strict"] is False
    assert [row["name"] for row in body["cohorts"]] == ["Section A"]
    assert body["cohorts"][0]["description"] == "Morning"

    renamed = client.patch(
        f"/api/courses/{course.id}/cohorts/{cohort_id}",
        json={"name": "Section Alpha"},
        headers=headers,
    )
    assert renamed.status_code == 200, renamed.text
    assert renamed.json()["name"] == "Section Alpha"

    rejected = client.put(
        f"/api/courses/{course.id}/cohorts/{cohort_id}/members",
        json={"user_ids": [first.id, outsider.id]},
        headers=headers,
    )
    assert rejected.status_code == 400
    assert "must be enrolled" in rejected.json()["detail"]

    members = client.put(
        f"/api/courses/{course.id}/cohorts/{cohort_id}/members",
        json={"user_ids": [first.id]},
        headers=headers,
    )
    assert members.status_code == 200, members.text
    assert [row["id"] for row in members.json()["members"]] == [first.id]

    synced = client.post(
        f"/api/courses/{course.id}/cohorts/sync-default", headers=headers
    )
    assert synced.status_code == 200, synced.text
    assert synced.json() == {"added": 1}

    strict = client.put(
        f"/api/courses/{course.id}/cohort-settings",
        json={"strict": True},
        headers=headers,
    )
    assert strict.status_code == 200, strict.text
    assert strict.json() == {"cohort_strict": True}
    planning = client.get(f"/api/courses/{course.id}/planning", headers=headers).json()
    assert planning["cohort_strict"] is True

    deleted = client.delete(
        f"/api/courses/{course.id}/cohorts/{cohort_id}", headers=headers
    )
    assert deleted.status_code == 200, deleted.text
    assert deleted.json() == {"ok": True}
    remaining = client.get(
        f"/api/courses/{course.id}/planning", headers=headers
    ).json()
    assert remaining["cohorts"] == []


def test_exercise_sets_requirements_and_coverage(client, db_session, test_lab):
    owner = _make_user(db_session, "instructor")
    student = _make_user(db_session, "student")
    course = _course(db_session, owner)
    other_course = _course(db_session, owner)
    _enroll(db_session, course, student)
    headers = _headers(client, owner)

    created_set = client.post(
        f"/api/courses/{course.id}/exercise-sets",
        json={"name": "Week 1", "description": "Intro drills"},
        headers=headers,
    )
    assert created_set.status_code == 201, created_set.text
    set_id = created_set.json()["id"]

    duplicate = client.post(
        f"/api/courses/{course.id}/exercise-sets",
        json={"name": "week 1"},
        headers=headers,
    )
    assert duplicate.status_code == 409

    renamed = client.patch(
        f"/api/courses/{course.id}/exercise-sets/{set_id}",
        json={"name": "Week One"},
        headers=headers,
    )
    assert renamed.status_code == 200, renamed.text
    assert renamed.json()["name"] == "Week One"

    cohort = client.post(
        f"/api/courses/{course.id}/cohorts",
        json={"name": "Cohort A", "is_default": True},
        headers=headers,
    )
    assert cohort.status_code == 201, cohort.text
    cohort_id = cohort.json()["id"]
    members = client.put(
        f"/api/courses/{course.id}/cohorts/{cohort_id}/members",
        json={"user_ids": [student.id]},
        headers=headers,
    )
    assert members.status_code == 200, members.text

    unknown_items = client.put(
        f"/api/courses/{course.id}/exercise-sets/{set_id}/items",
        json={"items": [{"lab_id": 99999999}]},
        headers=headers,
    )
    assert unknown_items.status_code == 400

    items = client.put(
        f"/api/courses/{course.id}/exercise-sets/{set_id}/items",
        json={"items": [{"lab_id": test_lab.id, "required": True}]},
        headers=headers,
    )
    assert items.status_code == 200, items.text
    assert items.json()["items"][0]["lab_id"] == test_lab.id
    assert items.json()["items"][0]["lab_name"] == test_lab.name
    assert items.json()["items"][0]["required"] is True

    cross_course_items = client.put(
        f"/api/courses/{other_course.id}/exercise-sets/{set_id}/items",
        json={"items": [{"lab_id": test_lab.id}]},
        headers=headers,
    )
    assert cross_course_items.status_code == 404

    unknown_cohort = client.post(
        f"/api/courses/{course.id}/requirements",
        json={"cohort_id": 99999999, "set_id": set_id},
        headers=headers,
    )
    assert unknown_cohort.status_code == 404

    cross_course_requirement = client.post(
        f"/api/courses/{other_course.id}/requirements",
        json={"cohort_id": cohort_id, "set_id": set_id},
        headers=headers,
    )
    assert cross_course_requirement.status_code == 404

    invalid_rule = client.post(
        f"/api/courses/{course.id}/requirements",
        json={"cohort_id": cohort_id, "set_id": set_id, "rule_type": "partial"},
        headers=headers,
    )
    assert invalid_rule.status_code == 422

    invalid_percent = client.post(
        f"/api/courses/{course.id}/requirements",
        json={
            "cohort_id": cohort_id,
            "set_id": set_id,
            "rule_type": "complete_percent",
            "threshold": 200,
        },
        headers=headers,
    )
    assert invalid_percent.status_code == 400

    created_requirement = client.post(
        f"/api/courses/{course.id}/requirements",
        json={
            "cohort_id": cohort_id,
            "set_id": set_id,
            "rule_type": "complete_all",
            "due_at": "2999-01-01T00:00:00Z",
            "note": "  first pass ",
        },
        headers=headers,
    )
    assert created_requirement.status_code == 201, created_requirement.text
    requirement = created_requirement.json()
    requirement_id = requirement["id"]
    assert requirement["note"] == "first pass"
    assert requirement["due_at"].startswith("2999-01-01T00:00:00")

    planning = client.get(f"/api/courses/{course.id}/planning", headers=headers).json()
    assert planning["exercise_sets"][0]["items"][0]["lab_id"] == test_lab.id
    assert planning["requirements"][0]["id"] == requirement_id

    coverage = client.get(
        f"/api/courses/{course.id}/planning/coverage", headers=headers
    )
    assert coverage.status_code == 200, coverage.text
    row = coverage.json()["coverage"][0]
    assert row["total_items"] == 1
    assert row["learners"] == 1
    assert row["met"] == 0
    assert row["missing"] == 1
    assert row["overdue"] is False
    assert row["students"][0]["completed"] == 0
    assert row["students"][0]["met"] is False

    db_session.add(
        LabCompletion(
            user_id=student.id,
            lab_id=test_lab.id,
            attempts=1,
            hints_used=0,
            time_spent_minutes=10,
        )
    )
    db_session.commit()

    covered = client.get(
        f"/api/courses/{course.id}/planning/coverage", headers=headers
    ).json()["coverage"][0]
    assert covered["met"] == 1
    assert covered["missing"] == 0
    assert covered["students"][0]["completed"] == 1
    assert covered["students"][0]["met"] is True

    updated = client.patch(
        f"/api/courses/{course.id}/requirements/{requirement_id}",
        json={"note": "revised"},
        headers=headers,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["note"] == "revised"

    bad_due = client.patch(
        f"/api/courses/{course.id}/requirements/{requirement_id}",
        json={"due_at": "not-a-date"},
        headers=headers,
    )
    assert bad_due.status_code == 400

    deleted = client.delete(
        f"/api/courses/{course.id}/requirements/{requirement_id}", headers=headers
    )
    assert deleted.status_code == 200, deleted.text
    assert deleted.json() == {"ok": True}
    empty = client.get(
        f"/api/courses/{course.id}/planning/coverage", headers=headers
    ).json()
    assert empty["coverage"] == []
