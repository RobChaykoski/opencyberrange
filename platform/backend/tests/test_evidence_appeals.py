"""Learner appeals and the second-review path."""

from __future__ import annotations

import uuid

import pytest

from app.auth import get_password_hash
from app.models import EvidenceRecord, User

PASSWORD = "Appeal#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role: str = "student") -> User:
    suffix = uuid.uuid4().hex[:10]
    user = User(
        username=f"appeal_{role}_{suffix}",
        email=f"appeal_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id="default",
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


def _evidence(client, admin: User, learner: User) -> dict:
    response = client.post(
        "/api/evidence",
        json={
            "learner_id": learner.id,
            "source_type": "artifact",
            "source_id": f"appeal-{uuid.uuid4().hex[:10]}",
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
            "provenance": "pytest",
            "visibility": "both",
            "artifact": {
                "uri": "evidence://appeal.csv",
                "mime": "text/csv",
                "size": 64,
                "sha256": "b" * 64,
            },
        },
        headers=_headers(client, admin),
    )
    assert response.status_code in (200, 201), response.text
    return response.json()["evidence"]


def _reject(client, admin: User, evidence_id: int) -> None:
    response = client.post(
        f"/api/evidence/{evidence_id}/review",
        json={
            "decision": "rejected",
            "criterion_scores": {
                "accuracy": 1,
                "evidence": 1,
                "analysis": 1,
                "communication": 1,
            },
            "notes": "The timeline is not yet supported by the cited sources.",
            "next_step": "Add the source for each material event and resubmit.",
        },
        headers=_headers(client, admin),
    )
    assert response.status_code == 200, response.text


def _cleanup(db, users: list[User]) -> None:
    ids = [user.id for user in users]
    if ids:
        db.query(EvidenceRecord).filter(
            EvidenceRecord.learner_id.in_(ids)
        ).delete(synchronize_session=False)
        for user in users:
            db.delete(user)
        db.commit()


def test_rejected_evidence_can_be_appealed_and_reopened(client, db_session):
    admin = _user(db_session, "admin")
    learner = _user(db_session)
    try:
        evidence = _evidence(client, admin, learner)
        _reject(client, admin, evidence["id"])

        appeal = client.post(
            f"/api/evidence/{evidence['id']}/appeal",
            json={
                "reason": "The source log was attached but the reviewer may have missed it."
            },
            headers=_headers(client, learner),
        )
        assert appeal.status_code == 201, appeal.text
        appeal_body = appeal.json()["appeal"]
        assert appeal_body["status"] == "pending"
        assert appeal_body["evidence"]["status"] == "rejected"

        duplicate = client.post(
            f"/api/evidence/{evidence['id']}/appeal",
            json={"reason": "A second pending appeal should not be accepted."},
            headers=_headers(client, learner),
        )
        assert duplicate.status_code == 409
        assert duplicate.headers["X-Error-Code"] == "evidence_appeal_conflict"

        admin_headers = _headers(client, admin)
        queue = client.get("/api/evidence/appeals/queue", headers=admin_headers)
        assert queue.status_code == 200
        assert queue.json()["appeals"][0]["id"] == appeal_body["id"]

        decision = client.post(
            f"/api/evidence/appeals/{appeal_body['id']}/decision",
            json={
                "decision": "accepted",
                "notes": "The attached log is visible; return the record for a second review.",
            },
            headers=admin_headers,
        )
        assert decision.status_code == 200, decision.text
        assert decision.json()["appeal"]["status"] == "accepted"
        assert decision.json()["evidence"]["status"] == "in_review"

        second_review = client.post(
            f"/api/evidence/{evidence['id']}/review",
            json={
                "decision": "accepted",
                "criterion_scores": {
                    "accuracy": 3,
                    "evidence": 3,
                    "analysis": 2,
                    "communication": 3,
                },
                "notes": "The source log resolves the earlier gap.",
            },
            headers=admin_headers,
        )
        assert second_review.status_code == 200, second_review.text
        assert second_review.json()["evidence"]["status"] == "accepted"
    finally:
        _cleanup(db_session, [learner, admin])


def test_appeal_is_only_for_the_owner_and_rejected_evidence(client, db_session):
    admin = _user(db_session, "admin")
    learner = _user(db_session)
    other = _user(db_session)
    try:
        evidence = _evidence(client, admin, learner)
        not_rejected = client.post(
            f"/api/evidence/{evidence['id']}/appeal",
            json={"reason": "This record is still collected and should be rejected first."},
            headers=_headers(client, learner),
        )
        assert not_rejected.status_code == 400
        assert not_rejected.headers["X-Error-Code"] == "evidence_appeal_invalid"

        _reject(client, admin, evidence["id"])
        forbidden = client.post(
            f"/api/evidence/{evidence['id']}/appeal",
            json={"reason": "I do not own this evidence and must not appeal it."},
            headers=_headers(client, other),
        )
        assert forbidden.status_code == 404
    finally:
        _cleanup(db_session, [learner, other, admin])


def test_student_cannot_read_the_appeal_queue(client, db_session):
    learner = _user(db_session)
    try:
        response = client.get(
            "/api/evidence/appeals/queue",
            headers=_headers(client, learner),
        )
        assert response.status_code == 403
    finally:
        _cleanup(db_session, [learner])
