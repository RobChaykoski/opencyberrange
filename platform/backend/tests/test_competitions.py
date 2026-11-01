"""Opt-in competition API tests.

Competitions are time-boxed and separate from the learning record. These tests
cover creation, joining, scoring inside the event window, privacy masking, and
student permission boundaries.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import Competition, User

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
