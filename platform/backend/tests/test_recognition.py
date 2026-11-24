"""Achievement catalogue and award checks."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from app.auth import get_password_hash
from app.models import ImpactContribution, RecognitionAward, User
from app.services import recognition as service
from app.services import journeys as journey_service

PASSWORD = "Achieve#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role: str = "student") -> User:
    suffix = uuid.uuid4().hex[:10]
    user = User(
        username=f"achieve_{role}_{suffix}",
        email=f"achieve_{role}_{suffix}@example.org",
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


def _contribution(db, user, **overrides) -> ImpactContribution:
    now = datetime(2026, 6, 1)
    values = dict(
        institution_id="default",
        user_id=user.id,
        dimension="build",
        kind="tool",
        title="A small utility",
        base_points=60,
        reach_count=20,
        quality_rating=4.0,
        validation_level="instructor",
        originality="original",
        status="verified",
        occurred_at=now,
        verified_at=now,
        last_used_at=now,
    )
    values.update(overrides)
    row = ImpactContribution(**values)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _cleanup(db, users: list[User]) -> None:
    ids = [user.id for user in users]
    db.query(RecognitionAward).filter(RecognitionAward.user_id.in_(ids)).delete(
        synchronize_session=False
    )
    db.query(ImpactContribution).filter(
        ImpactContribution.user_id.in_(ids)
    ).delete(synchronize_session=False)
    for user in users:
        db.delete(user)
    db.commit()


def test_catalogue_is_consistent_and_secrets_have_clues():
    rows = service.awards()
    keys = [row["key"] for row in rows]
    assert len(keys) >= 30
    assert len(keys) == len(set(keys))
    for row in rows:
        assert row["tier"] in {"public", "secret", "legendary", "mythic"}
        if row["tier"] in {"secret", "legendary"}:
            assert row.get("clue"), row["key"]
        if row.get("status") == "active":
            assert row.get("rule") in service.RULES, row["key"]
        for required in row.get("requires") or []:
            assert required in keys
    legacy = service._by_key()["legacy"]
    assert legacy["tier"] == "mythic"
    assert legacy.get("clue") is None
    tradition_titles = {
        row["title"] for row in journey_service.traditions()
    }
    assert len(tradition_titles) == 8
    for row in rows:
        assert row.get("tradition") in tradition_titles, row["key"]


def test_unearned_board_reveals_clues_but_not_triggers(client, db_session):
    learner = _user(db_session)
    try:
        headers = _headers(client, learner)
        response = client.get("/api/recognition/me", headers=headers)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["earned"] == []
        assert body["sealed"] >= 1
        assert body["visible"]
        for item in body["visible"]:
            assert "rule" not in item
            assert "trigger" not in item
            if item["tier"] == "secret":
                assert item["title"] == "Unknown"
            if item["tier"] == "legendary":
                assert item["title"] == "????"
            assert item["earned"] is False
        titles = {item["title"] for item in body["visible"]}
        assert "Legacy" not in titles
        assert "The Lighthouse" not in titles
    finally:
        _cleanup(db_session, [learner])


def test_verified_build_awards_are_idempotent(client, db_session):
    learner = _user(db_session)
    try:
        _contribution(db_session, learner, kind="tool", reach_count=50)
        headers = _headers(client, learner)
        first = client.post("/api/recognition/evaluate", headers=headers)
        assert first.status_code == 200, first.text
        keys = {row["key"] for row in first.json()["newly_earned"]}
        assert "toolmaker" in keys
        assert "hidden_foundation" not in keys

        second = client.post("/api/recognition/evaluate", headers=headers)
        assert second.json()["newly_earned"] == []

        board = client.get("/api/recognition/me", headers=headers).json()
        earned = {row["key"]: row for row in board["earned"]}
        assert "toolmaker" in earned
        assert earned["toolmaker"]["earned_message"]
        assert earned["toolmaker"]["unseen"] is True

        marked = client.post("/api/recognition/seen", headers=headers)
        assert marked.status_code == 200
        assert marked.json()["marked"] >= 1
        board = client.get("/api/recognition/me", headers=headers).json()
        assert all(row["unseen"] is False for row in board["earned"])
    finally:
        _cleanup(db_session, [learner])


def test_chain_advances_only_when_the_previous_stage_is_earned(client, db_session):
    learner = _user(db_session)
    try:
        headers = _headers(client, learner)
        board = client.get("/api/recognition/me", headers=headers).json()
        clues = {item["clue"] for item in board["visible"]}
        assert "The first step is helping." in clues
        assert "Helping once is easy." not in clues

        _contribution(
            db_session,
            learner,
            dimension="teach",
            kind="workshop",
            title="A short workshop",
            base_points=40,
            reach_count=10,
        )
        client.post("/api/recognition/evaluate", headers=headers)
        board = client.get("/api/recognition/me", headers=headers).json()
        clues = {item["clue"] for item in board["visible"]}
        assert "Helping once is easy." in clues
        assert "Helping consistently changes people." not in clues
    finally:
        _cleanup(db_session, [learner])


def test_manual_award_needs_admin_evidence_and_unlocked_stage(client, db_session):
    learner = _user(db_session)
    instructor = _user(db_session, "instructor")
    admin = _user(db_session, "admin")
    try:
        learner_headers = _headers(client, learner)
        instructor_headers = _headers(client, instructor)
        admin_headers = _headers(client, admin)

        forbidden = client.post(
            f"/api/recognition/{learner.id}/award",
            json={
                "key": "first_responder",
                "evidence_ref": "forum-thread-42",
                "note": "Answered the same learner ten times.",
            },
            headers=instructor_headers,
        )
        assert forbidden.status_code == 403

        no_reference = client.post(
            f"/api/recognition/{learner.id}/award",
            json={
                "key": "first_responder",
                "evidence_ref": "",
                "note": "Answered the same learner ten times.",
            },
            headers=admin_headers,
        )
        assert no_reference.status_code == 422

        locked = client.post(
            f"/api/recognition/{learner.id}/award",
            json={
                "key": "helping_4",
                "evidence_ref": "mentor-log-7",
                "note": "Three mentees have become mentors.",
            },
            headers=admin_headers,
        )
        assert locked.status_code == 400
        assert locked.headers["X-Error-Code"] == "achievement_locked"

        not_manual = client.post(
            f"/api/recognition/{learner.id}/award",
            json={
                "key": "toolmaker",
                "evidence_ref": "tool-usage-1",
                "note": "The tool is used by ten learners.",
            },
            headers=admin_headers,
        )
        assert not_manual.status_code == 400
        assert not_manual.headers["X-Error-Code"] == "achievement_not_manual"

        allowed = client.post(
            f"/api/recognition/{learner.id}/award",
            json={
                "key": "first_responder",
                "evidence_ref": "forum-thread-42",
                "note": "Answered the same learner ten times.",
            },
            headers=admin_headers,
        )
        assert allowed.status_code == 201, allowed.text
        assert allowed.json()["earned"] is True
        assert allowed.json()["source"] == "manual"

        board = client.get("/api/recognition/me", headers=learner_headers).json()
        assert {row["key"] for row in board["earned"]} == {"first_responder"}
    finally:
        _cleanup(db_session, [learner, instructor, admin])


def test_legacy_requires_the_whole_chain_and_three_years(client, db_session):
    learner = _user(db_session)
    admin = _user(db_session, "admin")
    try:
        headers = _headers(client, learner)
        admin_headers = _headers(client, admin)
        now = datetime(2026, 6, 1)
        _contribution(
            db_session,
            learner,
            dimension="protect",
            kind="assessment",
            title="A non-profit assessment",
            base_points=40,
            occurred_at=now - timedelta(days=365 * 3),
            verified_at=now - timedelta(days=365 * 3),
            last_used_at=now - timedelta(days=365 * 3),
            reach_count=12,
        )
        _contribution(
            db_session,
            learner,
            dimension="teach",
            kind="mentoring",
            title="Mentoring a new analyst",
            base_points=20,
            occurred_at=now - timedelta(days=365 * 2),
            verified_at=now - timedelta(days=365 * 2),
            last_used_at=now - timedelta(days=365 * 2),
            reach_count=3,
        )
        _contribution(
            db_session,
            learner,
            dimension="teach",
            kind="workshop",
            title="A community workshop",
            base_points=40,
            occurred_at=now - timedelta(days=365),
            verified_at=now - timedelta(days=365),
            last_used_at=now - timedelta(days=365),
            reach_count=40,
        )
        _contribution(
            db_session,
            learner,
            dimension="serve",
            kind="nonprofit_support",
            title="A non-profit security review",
            base_points=40,
            occurred_at=now - timedelta(days=365 * 3 + 20),
            verified_at=now - timedelta(days=365 * 3 + 20),
            last_used_at=now - timedelta(days=365 * 3 + 20),
            reach_count=6,
        )
        _contribution(
            db_session,
            learner,
            dimension="serve",
            kind="community_event",
            title="A community awareness evening",
            base_points=30,
            occurred_at=now - timedelta(days=365 * 2 + 20),
            verified_at=now - timedelta(days=365 * 2 + 20),
            last_used_at=now - timedelta(days=365 * 2 + 20),
            reach_count=25,
        )
        _contribution(
            db_session,
            learner,
            dimension="serve",
            kind="student_support",
            title="Support for a new student group",
            base_points=20,
            occurred_at=now - timedelta(days=365 + 20),
            verified_at=now - timedelta(days=365 + 20),
            last_used_at=now - timedelta(days=365 + 20),
            reach_count=8,
        )
        _contribution(
            db_session,
            learner,
            dimension="build",
            kind="tool",
            title="A tool still in use",
            base_points=60,
            occurred_at=now - timedelta(days=30),
            verified_at=now - timedelta(days=400),
            last_used_at=now,
            reach_count=10,
        )

        gained = client.post("/api/recognition/evaluate", headers=headers).json()
        keys = {row["key"] for row in gained["newly_earned"]}
        assert "helping_1" in keys
        assert "helping_2" in keys
        assert "helping_3" in keys
        assert "legacy" not in keys

        manual = client.post(
            f"/api/recognition/{learner.id}/award",
            json={
                "key": "helping_4",
                "evidence_ref": "mentor-log-9",
                "note": "Three mentees now mentor other learners.",
            },
            headers=admin_headers,
        )
        assert manual.status_code == 201, manual.text

        gained = client.post("/api/recognition/evaluate", headers=headers).json()
        keys = {row["key"] for row in gained["newly_earned"]}
        assert "legacy" in keys
        board = client.get("/api/recognition/me", headers=headers).json()
        legacy = [row for row in board["earned"] if row["key"] == "legacy"][0]
        assert legacy["title"] == "Legacy"
        assert legacy["earned_message"] == "The community is better because you were here."
    finally:
        _cleanup(db_session, [learner, admin])


def test_achievements_require_authentication(client):
    assert client.get("/api/recognition/me").status_code == 401
