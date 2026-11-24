"""Impact ledger API and access checks."""

from __future__ import annotations

import uuid

import pytest

from app.auth import get_password_hash
from app.models import ImpactContribution, StewardshipEvent, User

PASSWORD = "Impact#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role: str = "student") -> User:
    suffix = uuid.uuid4().hex[:10]
    user = User(
        username=f"impact_{role}_{suffix}",
        email=f"impact_{role}_{suffix}@example.org",
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


def _cleanup(db, users: list[User]) -> None:
    ids = [user.id for user in users]
    db.query(StewardshipEvent).filter(StewardshipEvent.user_id.in_(ids)).delete(
        synchronize_session=False
    )
    db.query(ImpactContribution).filter(
        ImpactContribution.user_id.in_(ids)
    ).delete(synchronize_session=False)
    for user in users:
        db.delete(user)
    db.commit()


def _submit(client, headers: dict, **overrides) -> dict:
    payload = {
        "dimension": "build",
        "kind": "detection_rule",
        "title": "Sigma rule for suspicious PowerShell",
        "summary": "Rule with a positive and a benign test.",
        "reach_count": 40,
        "originality": "original",
    }
    payload.update(overrides)
    response = client.post(
        "/api/impact/contributions", json=payload, headers=headers
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_self_report_is_pending_and_verification_credits_it(client, db_session):
    learner = _user(db_session)
    admin = _user(db_session, "admin")
    try:
        learner_headers = _headers(client, learner)
        admin_headers = _headers(client, admin)

        submitted = _submit(client, learner_headers)
        assert submitted["status"] == "submitted"
        assert submitted["preview_points"] > 0

        mine = client.get("/api/impact/me", headers=learner_headers)
        assert mine.status_code == 200
        body = mine.json()
        assert body["legacy_score"] == 0
        assert body["pending_impact"] == 1
        assert body["stewardship"]["points"] == 100
        assert body["meaning_index"]["total"] == 0
        assert body["contributions"][0]["status"] == "submitted"
        assert body["contributions"][0]["points"] == 0

        queue = client.get("/api/impact/pending", headers=admin_headers)
        assert queue.status_code == 200
        assert [row["id"] for row in queue.json()["pending"]] == [
            submitted["id"]
        ]

        verified = client.post(
            f"/api/impact/contributions/{submitted['id']}/verify",
            json={
                "validation_level": "instructor",
                "quality_rating": 4.5,
                "reach_count": 40,
                "review_notes": "Positive and benign tests both reproduce.",
            },
            headers=admin_headers,
        )
        assert verified.status_code == 200, verified.text
        assert verified.json()["status"] == "verified"
        assert verified.json()["points"] > 0

        body = client.get("/api/impact/me", headers=learner_headers).json()
        assert body["legacy_score"] > 0
        assert body["dimensions"]["build"] == body["legacy_score"]
        assert body["meaning_index"]["open_source_users"] == 40
        assert body["pending_impact"] == 0
        assert body["legacy_class"] == "Builder"
    finally:
        _cleanup(db_session, [learner, admin])


def test_duplicate_contribution_is_rejected(client, db_session):
    learner = _user(db_session)
    try:
        headers = _headers(client, learner)
        _submit(client, headers)
        duplicate = client.post(
            "/api/impact/contributions",
            json={
                "dimension": "build",
                "kind": "detection_rule",
                "title": "Sigma rule for suspicious PowerShell",
                "reach_count": 40,
            },
            headers=headers,
        )
        assert duplicate.status_code == 409
        assert duplicate.headers["X-Error-Code"] == "impact_duplicate"
    finally:
        _cleanup(db_session, [learner])


def test_unknown_kind_and_short_title_are_rejected(client, db_session):
    learner = _user(db_session)
    try:
        headers = _headers(client, learner)
        bad_kind = client.post(
            "/api/impact/contributions",
            json={"dimension": "build", "kind": "essay", "title": "A valid title"},
            headers=headers,
        )
        assert bad_kind.status_code == 400
        assert bad_kind.headers["X-Error-Code"] == "impact_kind_invalid"
        short = client.post(
            "/api/impact/contributions",
            json={"dimension": "build", "kind": "lab", "title": "No"},
            headers=headers,
        )
        assert short.status_code == 422
    finally:
        _cleanup(db_session, [learner])


def test_verification_requires_rating_and_scope(client, db_session):
    learner = _user(db_session)
    other = _user(db_session, "instructor")
    admin = _user(db_session, "admin")
    try:
        learner_headers = _headers(client, learner)
        other_headers = _headers(client, other)
        admin_headers = _headers(client, admin)
        submitted = _submit(client, learner_headers)

        missing_rating = client.post(
            f"/api/impact/contributions/{submitted['id']}/verify",
            json={"validation_level": "instructor"},
            headers=admin_headers,
        )
        assert missing_rating.status_code == 422

        out_of_scope = client.post(
            f"/api/impact/contributions/{submitted['id']}/verify",
            json={"validation_level": "instructor", "quality_rating": 4.0},
            headers=other_headers,
        )
        assert out_of_scope.status_code == 403
        assert out_of_scope.headers["X-Error-Code"] == "impact_forbidden"

        rejected = client.post(
            f"/api/impact/contributions/{submitted['id']}/reject",
            json={"notes": "The rule has no benign test case yet."},
            headers=admin_headers,
        )
        assert rejected.status_code == 200
        assert rejected.json()["status"] == "rejected"
        body = client.get("/api/impact/me", headers=learner_headers).json()
        assert body["legacy_score"] == 0
    finally:
        _cleanup(db_session, [learner, other, admin])


def test_stewardship_needs_an_admin_and_evidence(client, db_session):
    learner = _user(db_session)
    instructor = _user(db_session, "instructor")
    admin = _user(db_session, "admin")
    try:
        learner_headers = _headers(client, learner)
        instructor_headers = _headers(client, instructor)
        admin_headers = _headers(client, admin)

        forbidden = client.post(
            f"/api/impact/stewardship/{learner.id}",
            json={
                "points_delta": 20,
                "category": "positive",
                "reason": "Responsible disclosure handled well.",
            },
            headers=instructor_headers,
        )
        assert forbidden.status_code == 403

        no_evidence = client.post(
            f"/api/impact/stewardship/{learner.id}",
            json={
                "points_delta": -50,
                "category": "negative",
                "reason": "Academic dishonesty confirmed by the review board.",
            },
            headers=admin_headers,
        )
        assert no_evidence.status_code == 400
        assert no_evidence.headers["X-Error-Code"] == "impact_evidence_required"

        recorded = client.post(
            f"/api/impact/stewardship/{learner.id}",
            json={
                "points_delta": -50,
                "category": "negative",
                "reason": "Academic dishonesty confirmed by the review board.",
                "evidence_ref": "case-2026-014",
            },
            headers=admin_headers,
        )
        assert recorded.status_code == 201, recorded.text

        body = client.get("/api/impact/me", headers=learner_headers).json()
        assert body["stewardship"]["points"] == 50
        assert body["stewardship"]["band"] == "Watch"
        assert body["stewardship"]["events"][0]["reason"].startswith(
            "Academic dishonesty"
        )
    finally:
        _cleanup(db_session, [learner, instructor, admin])


def test_cohort_is_suppressed_below_five_learners(client, db_session):
    learner = _user(db_session)
    instructor = _user(db_session, "instructor")
    admin = _user(db_session, "admin")
    try:
        learner_headers = _headers(client, learner)
        admin_headers = _headers(client, admin)
        submitted = _submit(client, learner_headers)
        client.post(
            f"/api/impact/contributions/{submitted['id']}/verify",
            json={"validation_level": "instructor", "quality_rating": 4.0},
            headers=admin_headers,
        )

        student_view = client.get(
            "/api/impact/cohort", headers=learner_headers
        )
        assert student_view.status_code == 403

        suppressed = client.get(
            "/api/impact/cohort", headers=_headers(client, instructor)
        )
        assert suppressed.status_code == 200
        body = suppressed.json()
        assert body["suppressed"] is True
        assert body["learners"] == 0
        assert body["dimensions"]["build"] == 0

        administrator = client.get(
            "/api/impact/cohort", headers=admin_headers
        )
        assert administrator.status_code == 200
        assert administrator.json()["suppressed"] is False
        assert administrator.json()["learners"] >= 1
    finally:
        _cleanup(db_session, [learner, instructor, admin])


def test_impact_requires_authentication(client):
    assert client.get("/api/impact/me").status_code == 401
    assert client.get("/api/impact/cohort").status_code == 401
