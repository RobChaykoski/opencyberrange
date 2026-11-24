"""Release 6 evidence ledger: creation, scope, review, and append-only rules."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import (
    Course,
    CourseEnrollment,
    EvidenceRecord,
    User,
)

PASSWORD = "Evidence#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role: str = "student", institution: str = "default") -> User:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"evidence_{role}_{suffix}",
        email=f"evidence_{role}_{suffix}@example.org",
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


def _headers(client, user: User) -> dict:
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _course(db, instructor: User) -> Course:
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    course = Course(
        name=f"Evidence Course {suffix}",
        code=f"EV{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"EV-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def _payload(learner_id: int, **overrides) -> dict:
    suffix = uuid.uuid4().hex[:10]
    payload = {
        "learner_id": learner_id,
        "source_type": "artifact",
        "source_id": f"artifact-{suffix}",
        "competencies": [
            {
                "competency_id": "NET-001",
                "criteria": ["accuracy", "evidence"],
                "weight": 1.0,
            }
        ],
        "rubric_id": "blue-team-timeline",
        "rubric_version": "1.0",
        "confidence": "high",
        "confidence_reason": "Artifact reviewed by the test harness.",
        "provenance": "pytest",
        "visibility": "both",
        "artifact": {
            "uri": f"evidence://timeline-{suffix}.csv",
            "mime": "text/csv",
            "size": 128,
            "sha256": "a" * 64,
        },
    }
    payload.update(overrides)
    return payload


def _create(client, admin: User, payload: dict) -> dict:
    response = client.post(
        "/api/evidence",
        json=payload,
        headers=_headers(client, admin),
    )
    assert response.status_code in (200, 201), response.text
    return response.json()


def test_create_is_idempotent(client, db_session):
    admin = _user(db_session, "admin")
    learner = _user(db_session)
    payload = _payload(learner.id)

    first = _create(client, admin, payload)
    assert first["created"] is True
    assert first["evidence"]["status"] == "collected"
    assert first["evidence"]["rubric"]["id"] == "blue-team-timeline"
    assert first["evidence"]["artifact"]["sha256"] == "a" * 64
    assert first["evidence"]["competencies"][0]["competency_id"] == "NET-001"

    second = _create(client, admin, payload)
    assert second["created"] is False
    assert second["evidence"]["id"] == first["evidence"]["id"]


def test_rubric_catalog_is_available_to_reviewers(client, db_session):
    admin = _user(db_session, "admin")
    response = client.get(
        "/api/evidence/rubrics",
        headers=_headers(client, admin),
    )
    assert response.status_code == 200, response.text
    rubrics = {row["rubric"]: row for row in response.json()["rubrics"]}
    assert "blue-team-timeline" in rubrics
    assert rubrics["blue-team-timeline"]["version"] == "1.0"
    assert rubrics["blue-team-timeline"]["criteria"]


def test_record_carries_the_learner_identity_for_reviewers(client, db_session):
    admin = _user(db_session, "admin")
    learner = _user(db_session)
    created = _create(client, admin, _payload(learner.id))
    response = client.get(
        f"/api/evidence/{created['evidence']['id']}",
        headers=_headers(client, admin),
    )
    assert response.status_code == 200, response.text
    assert response.json()["evidence"]["learner"]["username"] == learner.username


def test_unknown_rubric_and_competency_are_rejected(client, db_session):
    admin = _user(db_session, "admin")
    learner = _user(db_session)

    bad_rubric = client.post(
        "/api/evidence",
        json=_payload(learner.id, rubric_id="not-a-rubric"),
        headers=_headers(client, admin),
    )
    assert bad_rubric.status_code == 400
    assert bad_rubric.headers["X-Error-Code"] == "evidence_rubric_unknown"

    bad_competency = client.post(
        "/api/evidence",
        json=_payload(
            learner.id,
            competencies=[
                {
                    "competency_id": "NOPE-999",
                    "criteria": ["accuracy"],
                    "weight": 1.0,
                }
            ],
        ),
        headers=_headers(client, admin),
    )
    assert bad_competency.status_code == 400
    assert bad_competency.headers["X-Error-Code"] == "evidence_competency_unknown"


def test_learner_sees_only_own_evidence(client, db_session):
    admin = _user(db_session, "admin")
    learner = _user(db_session)
    other = _user(db_session)
    created = _create(client, admin, _payload(learner.id))
    evidence_id = created["evidence"]["id"]

    own = client.get("/api/evidence", headers=_headers(client, learner))
    assert own.status_code == 200
    assert [row["id"] for row in own.json()["evidence"]] == [evidence_id]

    other_list = client.get("/api/evidence", headers=_headers(client, other))
    assert other_list.status_code == 200
    assert other_list.json()["evidence"] == []

    other_read = client.get(
        f"/api/evidence/{evidence_id}",
        headers=_headers(client, other),
    )
    assert other_read.status_code == 404


def test_instructor_sees_enrolled_learner_evidence(client, db_session):
    admin = _user(db_session, "admin")
    instructor = _user(db_session, "instructor")
    outsider = _user(db_session, "instructor")
    learner = _user(db_session)
    course = _course(db_session, instructor)
    db_session.add(CourseEnrollment(course_id=course.id, user_id=learner.id))
    db_session.commit()

    _create(client, admin, _payload(learner.id))

    allowed = client.get(
        "/api/evidence",
        headers=_headers(client, instructor),
    )
    assert allowed.status_code == 200
    assert len(allowed.json()["evidence"]) == 1

    denied = client.get(
        "/api/evidence",
        headers=_headers(client, outsider),
    )
    assert denied.status_code == 200
    assert denied.json()["evidence"] == []


def test_review_accepts_and_scores_the_rubric(client, db_session):
    admin = _user(db_session, "admin")
    instructor = _user(db_session, "instructor")
    learner = _user(db_session)
    course = _course(db_session, instructor)
    db_session.add(CourseEnrollment(course_id=course.id, user_id=learner.id))
    db_session.commit()
    created = _create(client, admin, _payload(learner.id))
    evidence_id = created["evidence"]["id"]

    response = client.post(
        f"/api/evidence/{evidence_id}/review",
        json={
            "decision": "accepted",
            "criterion_scores": {
                "accuracy": 3,
                "evidence": 3,
                "analysis": 2,
                "communication": 3,
            },
            "notes": "Clear timeline with source provenance.",
        },
        headers=_headers(client, instructor),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["evidence"]["status"] == "accepted"
    assert body["review"]["decision"] == "accepted"
    assert body["review"]["weighted_score"] == pytest.approx(0.9167, abs=0.001)
    assert body["evidence"]["latest_review"]["id"] == body["review"]["id"]

    again = client.post(
        f"/api/evidence/{evidence_id}/review",
        json={"decision": "accepted", "criterion_scores": {"accuracy": 3}},
        headers=_headers(client, instructor),
    )
    assert again.status_code == 409
    assert again.headers["X-Error-Code"] == "evidence_review_conflict"


def test_review_requires_a_reason_and_scores(client, db_session):
    admin = _user(db_session, "admin")
    learner = _user(db_session)
    evidence_id = _create(client, admin, _payload(learner.id))["evidence"]["id"]

    missing_notes = client.post(
        f"/api/evidence/{evidence_id}/review",
        json={"decision": "rejected", "criterion_scores": {}},
        headers=_headers(client, admin),
    )
    assert missing_notes.status_code == 400
    assert missing_notes.headers["X-Error-Code"] == "evidence_review_invalid"

    incomplete = client.post(
        f"/api/evidence/{evidence_id}/review",
        json={"decision": "accepted", "criterion_scores": {"accuracy": 3}},
        headers=_headers(client, admin),
    )
    assert incomplete.status_code == 400
    assert incomplete.headers["X-Error-Code"] == "evidence_review_invalid"


def test_queue_lists_unreviewed_evidence(client, db_session):
    admin = _user(db_session, "admin")
    learner = _user(db_session)
    evidence_id = _create(client, admin, _payload(learner.id))["evidence"]["id"]

    queue = client.get("/api/evidence/queue", headers=_headers(client, admin))
    assert queue.status_code == 200
    assert evidence_id in [row["id"] for row in queue.json()["evidence"]]

    student_queue = client.get(
        "/api/evidence/queue",
        headers=_headers(client, learner),
    )
    assert student_queue.status_code == 403


def test_competency_summary_reports_accepted_evidence(client, db_session):
    admin = _user(db_session, "admin")
    learner = _user(db_session)
    evidence_id = _create(client, admin, _payload(learner.id))["evidence"]["id"]
    client.post(
        f"/api/evidence/{evidence_id}/review",
        json={
            "decision": "accepted",
            "criterion_scores": {
                "accuracy": 3,
                "evidence": 3,
                "analysis": 3,
                "communication": 3,
            },
        },
        headers=_headers(client, admin),
    )

    response = client.get(
        f"/api/competencies/NET-001/evidence?learner_id={learner.id}",
        headers=_headers(client, admin),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["competency_id"] == "NET-001"
    assert body["total"] == 1
    assert body["accepted"] == 1
    assert body["validated"] is True


def test_content_is_append_only(db_session):
    learner = _user(db_session)
    record = EvidenceRecord(
        institution_id="default",
        learner_id=learner.id,
        source_type="artifact",
        source_id="append-only-test",
        rubric_id="blue-team-timeline",
        rubric_version="1.0",
        confidence="medium",
        collected_at=datetime.now(timezone.utc).replace(tzinfo=None),
        provenance="pytest",
        visibility="both",
        status="collected",
        formula_version="competency-v1",
        source_fingerprint=uuid.uuid4().hex * 2,
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    record.source_id = "changed-in-place"
    with pytest.raises(ValueError):
        db_session.commit()
    db_session.rollback()
