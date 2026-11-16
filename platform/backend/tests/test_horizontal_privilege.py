"""Horizontal and vertical privilege regression tests.

These are the two tests every learner-scoped endpoint must have:

* owner access succeeds;
* non-owner access is denied without revealing whether the record exists.

The suite also checks that role claims come from the database, that faculty
cannot reach private affinity data, and that an instructor cannot enumerate
learners outside their own courses.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.consent import service as consent_service
from app.cyber_dna.models import DnaSnapshot
from app.models import (
    Course,
    CourseEnrollment,
    LearnerSnapshot,
    PlatformSetting,
    User,
)

PASSWORD = "Horiz#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role="student", institution="default"):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"horiz_{role}_{suffix}",
        email=f"horiz_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id=institution,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _headers(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _setting(db, key, value):
    row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if row is None:
        row = PlatformSetting(
            key=key,
            value=str(value),
            category="features",
            description="test",
            is_secret=False,
        )
        db.add(row)
    else:
        row.value = str(value)
    db.commit()


def _snapshot(db, owner):
    row = LearnerSnapshot(
        user_id=owner.id,
        kind="career_dossier",
        schema_version="test",
        formula_version="test",
        weights="{}",
        payload=json.dumps({"owner": owner.username}),
        content_sha256=uuid.uuid4().hex,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _dna_snapshot(db, owner):
    row = DnaSnapshot(
        learner_id=owner.id,
        kind="behavior_profile",
        schema_version="test",
        formula_version="test",
        weights="{}",
        payload=json.dumps({"owner": owner.username}),
        content_sha256=uuid.uuid4().hex,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _course(db, instructor):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    row = Course(
        name=f"Horiz Course {suffix}",
        code=f"HZ{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"HZ-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def test_profile_snapshot_owner_succeeds_and_non_owner_gets_404(
    client, db_session
):
    owner = _user(db_session)
    outsider = _user(db_session)
    consent_service.grant(db_session, owner.id, "portfolio")
    consent_service.grant(db_session, owner.id, "cyber_dna")
    consent_service.grant(db_session, outsider.id, "portfolio")
    consent_service.grant(db_session, outsider.id, "cyber_dna")
    snapshot = _snapshot(db_session, owner)

    owner_headers = _headers(client, owner)
    outsider_headers = _headers(client, outsider)

    allowed = client.get(
        f"/api/profile/snapshots/{snapshot.id}", headers=owner_headers
    )
    assert allowed.status_code == 200, allowed.text

    denied = client.get(
        f"/api/profile/snapshots/{snapshot.id}", headers=outsider_headers
    )
    assert denied.status_code == 404
    assert "not found" in denied.json()["detail"].lower()

    for suffix in ("markdown", "html"):
        denied = client.get(
            f"/api/profile/snapshots/{snapshot.id}/{suffix}", headers=outsider_headers
        )
        assert denied.status_code == 404


def test_cyber_dna_snapshot_owner_succeeds_and_non_owner_gets_404(
    client, db_session
):
    owner = _user(db_session)
    outsider = _user(db_session)
    consent_service.grant(db_session, owner.id, "cyber_dna")
    consent_service.grant(db_session, outsider.id, "cyber_dna")
    snapshot = _dna_snapshot(db_session, owner)
    _setting(db_session, "cyber_dna_v3_enabled", "true")

    owner_headers = _headers(client, owner)
    outsider_headers = _headers(client, outsider)

    allowed = client.get(
        f"/api/dna/v3/snapshots/{snapshot.id}", headers=owner_headers
    )
    assert allowed.status_code == 200, allowed.text

    denied = client.get(
        f"/api/dna/v3/snapshots/{snapshot.id}", headers=outsider_headers
    )
    assert denied.status_code == 404


def test_jwt_role_tampering_cannot_promote_a_student(client, db_session):
    """Authorization uses the DB row, not a role claim in the token."""
    student = _user(db_session)
    headers = _headers(client, student)
    # The token has no role claim at all; this asserts the admin surface still
    # rejects the student even if a client fabricates one.
    headers["X-Debug-Role"] = "admin"
    response = client.get("/api/admin/security/events", headers=headers)
    assert response.status_code == 403


def test_faculty_cannot_read_private_career_affinity(client, db_session):
    instructor = _user(db_session, "instructor")
    _setting(db_session, "cyber_dna_v3_enabled", "true")
    response = client.get(
        "/api/dna/v3/affinity", headers=_headers(client, instructor)
    )
    assert response.status_code == 403


def test_instructor_cannot_enumerate_learners_outside_own_courses(
    client, db_session
):
    instructor = _user(db_session, "instructor")
    known = _user(db_session, "student")
    unknown = _user(db_session, "student")
    course = _course(db_session, instructor)
    db_session.add(CourseEnrollment(course_id=course.id, user_id=known.id))
    db_session.commit()

    response = client.get(
        f"/api/instructor/courses/{course.id}/enrollable-users",
        headers=_headers(client, instructor),
    )
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()}
    assert known.id not in ids  # already enrolled in this course
    assert unknown.id not in ids  # never taught by this instructor
    assert ids == set()


def test_instructor_sees_known_but_not_yet_enrolled_learners(
    client, db_session
):
    instructor = _user(db_session, "instructor")
    known = _user(db_session, "student")
    other_known = _user(db_session, "student")
    unknown = _user(db_session, "student")
    first = _course(db_session, instructor)
    second = _course(db_session, instructor)
    db_session.add(CourseEnrollment(course_id=first.id, user_id=known.id))
    db_session.add(CourseEnrollment(course_id=first.id, user_id=other_known.id))
    db_session.commit()

    response = client.get(
        f"/api/instructor/courses/{second.id}/enrollable-users",
        headers=_headers(client, instructor),
    )
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()}
    assert ids == {known.id, other_known.id}
    assert unknown.id not in ids
