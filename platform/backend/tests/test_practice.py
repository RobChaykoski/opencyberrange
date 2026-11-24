"""Standalone certification practice sessions."""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest

from app.auth import get_password_hash
from app.models import (
    PracticeSession,
    PracticeSessionQuestion,
    User,
)
from app.services import certification_quiz
from app.services import practice as service

PASSWORD = "Practice#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db

PATHWAY = "comptia-security-plus"


def _user(db, role: str = "student") -> User:
    suffix = uuid.uuid4().hex[:10]
    user = User(
        username=f"practice_{role}_{suffix}",
        email=f"practice_{role}_{suffix}@example.org",
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
    session_ids = [
        row[0]
        for row in db.query(PracticeSession.id)
        .filter(PracticeSession.user_id.in_(ids))
        .all()
    ]
    if session_ids:
        db.query(PracticeSessionQuestion).filter(
            PracticeSessionQuestion.session_id.in_(session_ids)
        ).delete(synchronize_session=False)
        db.query(PracticeSession).filter(
            PracticeSession.id.in_(session_ids)
        ).delete(synchronize_session=False)
    for user in users:
        db.delete(user)
    db.commit()


def _correct_index(question_id: str, options: list[str]) -> int:
    for pathway in certification_quiz.pathways():
        for question in pathway.get("questions") or []:
            if str(question["id"]) == str(question_id):
                return options.index(question["options"][question["correct"]])
    raise AssertionError(f"question {question_id} not found")


def test_prioritise_prefers_unseen_then_wrong():
    pool = [{"id": f"q{i}"} for i in range(1, 6)]
    now = datetime(2026, 6, 1)
    history = {
        "q1": {"seen": 2, "wrong": 2, "last": now},
        "q2": {"seen": 2, "wrong": 1, "last": now},
        "q3": {"seen": 2, "wrong": 0, "last": now},
        "q4": {"seen": 1, "wrong": 0, "last": now},
    }
    unseen = service.prioritise(pool, history, 1)
    assert unseen[0]["id"] == "q5"

    weak = service.prioritise(pool, history, 2)
    assert {row["id"] for row in weak} == {"q1", "q5"}

    recent = service.prioritise(pool, history, 4)
    assert {row["id"] for row in recent} == {"q1", "q2", "q3", "q5"}


def test_start_submit_and_review_a_mock_session(client, db_session):
    learner = _user(db_session)
    try:
        headers = _headers(client, learner)
        started = client.post(
            "/api/practice/sessions",
            json={"pathway_id": PATHWAY, "mode": "mock", "question_count": 5},
            headers=headers,
        )
        assert started.status_code == 201, started.text
        payload = started.json()
        session = payload["session"]
        assert session["status"] == "active"
        assert session["question_count"] == 5
        assert session["pass_mark"] == 70
        assert payload["pathway"]["code"]
        assert len(payload["questions"]) == 5
        for question in payload["questions"]:
            assert question["options"]
            assert "explanation" not in question
            assert "correct_index" not in question
            assert "reference" not in question

        answers = [
            {
                "position": question["position"],
                "selected_index": _correct_index(
                    question["question_id"], question["options"]
                ),
            }
            for question in payload["questions"]
        ]
        submitted = client.post(
            f"/api/practice/sessions/{session['id']}/submit",
            json={"answers": answers},
            headers=headers,
        )
        assert submitted.status_code == 200, submitted.text
        review = submitted.json()
        assert review["session"]["status"] == "submitted"
        assert review["session"]["score"] == 5
        assert review["session"]["percentage"] == 100.0
        assert review["session"]["passed"] is True
        assert all(q["is_correct"] is True for q in review["questions"])
        assert all(q["explanation"] for q in review["questions"])
        assert all(q["reference"] for q in review["questions"])

        again = client.post(
            f"/api/practice/sessions/{session['id']}/submit",
            json={"answers": answers},
            headers=headers,
        )
        assert again.status_code == 409
        assert again.headers["X-Error-Code"] == "practice_session_submitted"
    finally:
        _cleanup(db_session, [learner])


def test_a_domain_drill_stays_in_one_domain(client, db_session):
    learner = _user(db_session)
    try:
        headers = _headers(client, learner)
        pathways = client.get("/api/practice/pathways", headers=headers)
        assert pathways.status_code == 200
        pathway = next(
            row for row in pathways.json()["pathways"] if row["id"] == PATHWAY
        )
        domain = next(row for row in pathway["domain_list"] if row["question_count"])
        started = client.post(
            "/api/practice/sessions",
            json={
                "pathway_id": PATHWAY,
                "mode": "domain",
                "domain_id": domain["id"],
                "question_count": 3,
            },
            headers=headers,
        )
        assert started.status_code == 201, started.text
        payload = started.json()
        assert {row["domain_id"] for row in payload["questions"]} == {domain["id"]}
    finally:
        _cleanup(db_session, [learner])


def test_sessions_are_private_and_listed_in_history(client, db_session):
    learner = _user(db_session)
    other = _user(db_session)
    try:
        headers = _headers(client, learner)
        started = client.post(
            "/api/practice/sessions",
            json={"pathway_id": PATHWAY, "question_count": 3},
            headers=headers,
        ).json()
        session_id = started["session"]["id"]

        other_headers = _headers(client, other)
        hidden = client.get(
            f"/api/practice/sessions/{session_id}", headers=other_headers
        )
        assert hidden.status_code == 404

        history = client.get("/api/practice/sessions", headers=headers).json()
        assert [row["id"] for row in history["sessions"]] == [session_id]
        other_history = client.get(
            "/api/practice/sessions", headers=other_headers
        ).json()
        assert other_history["sessions"] == []

        answers = [
            {
                "position": question["position"],
                "selected_index": _correct_index(
                    question["question_id"], question["options"]
                ),
            }
            for question in started["questions"]
        ]
        client.post(
            f"/api/practice/sessions/{session_id}/submit",
            json={"answers": answers},
            headers=headers,
        )
        progress = client.get("/api/practice/progress", headers=headers).json()
        assert progress["pathways"][0]["pathway_id"] == PATHWAY
        assert progress["pathways"][0]["best_percentage"] == 100.0
        assert progress["domains"]
        assert other_history["sessions"] == []
    finally:
        _cleanup(db_session, [learner, other])


def test_unknown_pathway_and_bad_mode_are_rejected(client, db_session):
    learner = _user(db_session)
    try:
        headers = _headers(client, learner)
        unknown = client.post(
            "/api/practice/sessions",
            json={"pathway_id": "not-a-pathway"},
            headers=headers,
        )
        assert unknown.status_code == 404
        assert unknown.headers["X-Error-Code"] == "practice_pathway_unknown"

        bad_mode = client.post(
            "/api/practice/sessions",
            json={"pathway_id": PATHWAY, "mode": "exam"},
            headers=headers,
        )
        assert bad_mode.status_code == 400
        assert bad_mode.headers["X-Error-Code"] == "practice_mode_invalid"
    finally:
        _cleanup(db_session, [learner])


def test_practice_requires_authentication(client):
    assert client.get("/api/practice/pathways").status_code == 401
    assert client.get("/api/practice/progress").status_code == 401
