"""Opt-in competition API tests.

Competitions are time-boxed and separate from the learning record. These tests
cover creation, joining, scoring inside the event window, privacy masking, and
student permission boundaries.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import Competition, CompetitionParticipant, LabCompletion, User

pytestmark = pytest.mark.db

TEST_PASSWORD = "Correct#Horse7Battery"


@pytest.fixture()
def instructor_auth(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    instructor = User(
        username=f"competition_instructor_{suffix}",
        email=f"competition_instructor_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="instructor",
    )
    db_session.add(instructor)
    db_session.commit()
    db_session.refresh(instructor)

    resp = client.post(
        "/api/auth/login",
        data={"username": instructor.username, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    yield headers

    db_session.query(User).filter(User.id == instructor.id).delete()
    db_session.commit()


def _window():
    now = datetime.now(timezone.utc)
    return now - timedelta(hours=1), now + timedelta(hours=1)


def test_competition_join_score_and_privacy(
    client, db_session, auth_headers, test_user, test_lab, test_flag, instructor_auth
):
    start_at, end_at = _window()
    created = client.post(
        "/api/competitions",
        json={
            "name": "Weekend OSINT Sprint",
            "description": "A short opt-in event.",
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
            "lab_ids": [test_lab.id],
        },
        headers=instructor_auth,
    )
    assert created.status_code == 201, created.text
    competition_id = created.json()["id"]

    listing = client.get("/api/competitions", headers=auth_headers)
    assert listing.status_code == 200, listing.text
    assert any(
        item["id"] == competition_id
        for item in listing.json()["competitions"]
    )

    joined = client.post(
        f"/api/competitions/{competition_id}/join", headers=auth_headers
    )
    assert joined.status_code == 200, joined.text
    assert joined.json()["joined"] is True

    solved = client.post(
        f"/api/exercises/labs/{test_lab.id}/submit-flag",
        json={"flag": test_flag},
        headers=auth_headers,
    )
    assert solved.status_code == 200, solved.text
    assert solved.json()["correct"] is True

    detail = client.get(
        f"/api/competitions/{competition_id}", headers=auth_headers
    )
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert body["competition"]["status"] == "active"
    assert body["competition"]["joined"] is True
    assert body["competition"]["lab_count"] == 1

    entries = body["leaderboard"]["entries"]
    assert len(entries) == 1
    assert entries[0]["score"] > 0
    assert entries[0]["solved_count"] == 1
    assert entries[0]["is_me"] is True
    assert body["leaderboard"]["my_entry"]["rank"] == 1
    assert body["leaderboard"]["registration_counts"]["opt_in"] == 1
    # Event-specific awards: solving inside the window earns the competitor
    # badge, and the first solve in the event earns Event First Blood.
    codes = {badge["code"] for badge in entries[0]["achievements"]}
    assert {"c", "fb"}.issubset(codes)
    assert len(body["leaderboard"]["badges"]) == 7

    # Closing the event finalises placement badges on the next view. Move the
    # solve safely inside the window before shortening the event.
    completion = db_session.query(LabCompletion).filter(
        LabCompletion.user_id == test_user.id,
        LabCompletion.lab_id == test_lab.id,
    ).first()
    completion.completed_at = datetime.now(timezone.utc) - timedelta(minutes=2)
    db_session.commit()
    patched = client.patch(
        f"/api/competitions/{competition_id}",
        json={"end_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()},
        headers=instructor_auth,
    )
    assert patched.status_code == 200, patched.text
    ended = client.get(
        f"/api/competitions/{competition_id}", headers=auth_headers
    )
    assert ended.status_code == 200, ended.text
    ended_body = ended.json()
    assert ended_body["competition"]["status"] == "ended"
    ended_codes = {
        badge["code"]
        for badge in ended_body["leaderboard"]["entries"][0]["achievements"]
    }
    assert "ch" in ended_codes

    manager_detail = client.get(
        f"/api/competitions/{competition_id}", headers=instructor_auth
    )
    assert manager_detail.status_code == 200, manager_detail.text
    manager_entry = manager_detail.json()["leaderboard"]["entries"][0]
    assert manager_entry["source"] == "opt_in"
    assert manager_entry["joined_at"]

    # A learner who opted out of public scoreboards is masked on the event
    # leaderboard even though they explicitly joined the event.
    test_user.show_on_scoreboard = False
    db_session.commit()
    masked = client.get(
        f"/api/competitions/{competition_id}", headers=auth_headers
    )
    assert masked.status_code == 200, masked.text
    assert masked.json()["leaderboard"]["entries"][0]["display_name"] == (
        "Anonymous participant"
    )

    left = client.post(
        f"/api/competitions/{competition_id}/leave", headers=auth_headers
    )
    assert left.status_code == 200, left.text
    after_leave = client.get(
        f"/api/competitions/{competition_id}", headers=auth_headers
    )
    assert after_leave.status_code == 200, after_leave.text
    assert after_leave.json()["competition"]["joined"] is False
    assert after_leave.json()["leaderboard"]["entries"] == []

    deleted = client.delete(
        f"/api/competitions/{competition_id}", headers=instructor_auth
    )
    assert deleted.status_code == 200, deleted.text
    assert db_session.query(Competition).filter(
        Competition.id == competition_id
    ).first() is None


def test_new_user_signup_marks_competition_registration(
    client, db_session, test_lab, instructor_auth
):
    start_at, end_at = _window()
    created = client.post(
        "/api/competitions",
        json={
            "name": "DevFest Windsor-Essex 2026",
            "description": "High-school community event.",
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
            "lab_ids": [test_lab.id],
        },
        headers=instructor_auth,
    )
    assert created.status_code == 201, created.text
    competition_id = created.json()["id"]

    public_info = client.get(f"/api/competitions/public/{competition_id}")
    assert public_info.status_code == 200, public_info.text
    assert public_info.json()["competition"]["name"] == "DevFest Windsor-Essex 2026"

    suffix = uuid.uuid4().hex[:8]
    registered = client.post(
        "/api/auth/register",
        json={
            "username": f"devfest_student_{suffix}",
            "email": f"devfest_student_{suffix}@example.invalid",
            "password": TEST_PASSWORD,
            "competition_id": competition_id,
        },
    )
    assert registered.status_code == 200, registered.text
    student_id = registered.json()["id"]

    participant = db_session.query(CompetitionParticipant).filter(
        CompetitionParticipant.competition_id == competition_id,
        CompetitionParticipant.user_id == student_id,
    ).first()
    assert participant is not None
    assert participant.source == "new_user"

    manager_detail = client.get(
        f"/api/competitions/{competition_id}", headers=instructor_auth
    )
    assert manager_detail.status_code == 200, manager_detail.text
    counts = manager_detail.json()["leaderboard"]["registration_counts"]
    assert counts["new_user"] == 1
    assert counts["opt_in"] == 0

    deleted = client.delete(
        f"/api/competitions/{competition_id}", headers=instructor_auth
    )
    assert deleted.status_code == 200, deleted.text
    db_session.query(User).filter(User.id == student_id).delete()
    db_session.commit()


def test_student_cannot_create_competition(client, auth_headers, test_lab):
    start_at, end_at = _window()
    resp = client.post(
        "/api/competitions",
        json={
            "name": "Student Attempt",
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
            "lab_ids": [test_lab.id],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 403
