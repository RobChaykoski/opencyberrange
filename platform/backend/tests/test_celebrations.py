"""Celebration wall API tests.

The wall is shared by every signed-in user, so its visibility rules matter:
active users who opted out of scoreboards and diagnostic admin accounts must
not appear in the public feed, stats, or spotlight. A user's own awards are
still returned in the personal corner.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import Achievement, Course, CustomAchievement, User

pytestmark = pytest.mark.db

TEST_PASSWORD = "Correct#Horse7Battery"


@pytest.fixture()
def celebration_data(db_session, test_user):
    """A course with one public earner, one private earner, and an admin."""
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)

    # The wall only projects learners who opted in to a scoreboard name. The
    # personal "my award" corner still needs this opt-in so the first-blood
    # entry is not filtered out before the test can see it.
    test_user.show_on_scoreboard = True
    test_user.scoreboard_name_mode = "real_name"
    db_session.commit()

    instructor = User(
        username=f"celebration_instructor_{suffix}",
        email=f"celebration_instructor_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        role="instructor",
        is_approved=True,
    )
    db_session.add(instructor)
    db_session.flush()

    course = Course(
        name=f"Celebration Test {suffix}",
        code=f"CE{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"CELEB-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=30),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db_session.add(course)
    db_session.flush()

    other = User(
        username=f"celebration_other_{suffix}",
        email=f"celebration_other_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        first_name="Ada",
        last_name="Lovelace",
        is_active=True,
        role="student",
        is_approved=True,
        show_on_scoreboard=True,
        scoreboard_name_mode="real_name",
        avatar_data="data:image/png;base64,cHl0ZXN0LWF2YXRhcg==",
        avatar_border_style="glow",
        avatar_border_color="gold",
    )
    hidden = User(
        username=f"celebration_hidden_{suffix}",
        email=f"celebration_hidden_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        first_name="Hidden",
        last_name="Hacker",
        is_active=True,
        role="student",
        is_approved=True,
        show_on_scoreboard=False,
    )
    admin = User(
        username=f"celebration_admin_{suffix}",
        email=f"celebration_admin_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_admin=True,
        role="admin",
        is_approved=True,
        show_on_scoreboard=True,
    )
    db_session.add_all([other, hidden, admin])
    db_session.flush()

    custom = CustomAchievement(
        name=f"Rocket Rider {suffix}",
        description="Reach a custom celebration milestone.",
        icon="\U0001F680",
        trigger="labs_completed",
        threshold=1,
        is_active=True,
    )
    db_session.add(custom)
    db_session.flush()

    db_session.add_all([
        Achievement(
            user_id=test_user.id,
            course_id=course.id,
            achievement_type="first_blood",
            awarded_at=now - timedelta(minutes=5),
        ),
        Achievement(
            user_id=other.id,
            course_id=course.id,
            achievement_type="no_hints",
            awarded_at=now - timedelta(minutes=4),
        ),
        Achievement(
            user_id=other.id,
            course_id=course.id,
            achievement_type=f"custom_{custom.id}",
            awarded_at=now - timedelta(minutes=3),
        ),
        Achievement(
            user_id=hidden.id,
            course_id=course.id,
            achievement_type="clean_sweep",
            awarded_at=now - timedelta(minutes=2),
        ),
        Achievement(
            user_id=admin.id,
            course_id=course.id,
            achievement_type="perfectionist",
            awarded_at=now - timedelta(minutes=1),
        ),
    ])
    db_session.commit()

    yield {
        "course": course,
        "other": other,
        "hidden": hidden,
        "admin": admin,
        "custom": custom,
    }

    db_session.query(Achievement).filter(
        Achievement.course_id == course.id
    ).delete()
    db_session.query(CustomAchievement).filter(
        CustomAchievement.id == custom.id
    ).delete()
    db_session.query(Course).filter(Course.id == course.id).delete()
    for user_id in (instructor.id, other.id, hidden.id, admin.id):
        db_session.query(User).filter(User.id == user_id).delete()
    db_session.commit()


def test_wall_shows_public_earners_and_resolves_badge_details(
    client, auth_headers, celebration_data, test_user
):
    resp = client.get(
        "/api/dashboard/celebrations?limit=50", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    # The wall must not expose a stable learner id; identity is the public
    # display projection only.
    assert all(item["user_id"] is None for item in body["recent"])
    assert all(row["user_id"] is None for row in body["spotlight"])

    other_items = [
        item for item in body["recent"]
        if item["display_name"] == "Ada Lovelace"
    ]
    assert other_items
    assert all(item["username"] == celebration_data["other"].username for item in other_items)
    assert all(item["avatar_data"] for item in other_items)
    assert all(item["avatar_border_style"] == "glow" for item in other_items)
    assert all(item["avatar_border_color"] == "gold" for item in other_items)

    other_spotlight = next(
        row for row in body["spotlight"]
        if row["display_name"] == "Ada Lovelace"
    )
    assert other_spotlight["avatar_data"]
    assert other_spotlight["avatar_border_style"] == "glow"
    assert other_spotlight["avatar_border_color"] == "gold"

    first = next(
        item for item in body["recent"]
        if item["is_mine"] is True
        and item["achievement_type"] == "first_blood"
    )
    assert first["label"] == "First Blood"
    assert first["icon"] == "\U0001F3AF"
    assert first["description"]
    assert first["is_mine"] is True

    custom = next(
        item for item in body["recent"]
        if item["achievement_type"].startswith("custom_")
    )
    assert custom["label"] == celebration_data["custom"].name
    assert custom["icon"] == "\U0001F680"
    assert custom["description"] == celebration_data["custom"].description

    spotlight_names = {row["display_name"] for row in body["spotlight"]}
    assert any(row["is_mine"] is True for row in body["spotlight"])
    assert "Ada Lovelace" in spotlight_names
    assert "Hidden Hacker" not in spotlight_names
    assert celebration_data["admin"].username not in spotlight_names

    assert body["stats"]["total_awards"] >= 3
    assert body["stats"]["awards_this_week"] >= 3
    assert body["stats"]["first_bloods"] >= 1

    assert body["me"]["badge_count"] == 1
    assert body["me"]["listed"] is True
    assert body["me"]["can_list"] is True
    assert body["me"]["recent"][0]["achievement_type"] == "first_blood"


def test_opted_out_user_keeps_a_private_personal_corner(
    client, auth_headers, celebration_data, test_user, db_session
):
    hidden = client.put(
        "/api/auth/settings",
        json={"show_on_scoreboard": False},
        headers=auth_headers,
    )
    assert hidden.status_code == 200, hidden.text

    own_achievement = (
        db_session.query(Achievement)
        .filter(Achievement.user_id == test_user.id)
        .first()
    )
    blocked = client.post(
        f"/api/dashboard/celebrations/{own_achievement.id}/celebrate",
        headers=auth_headers,
    )
    assert blocked.status_code == 404, "a hidden achievement rejects celebrations"

    resp = client.get(
        "/api/dashboard/celebrations?limit=50", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert not any(item["is_mine"] is True for item in body["recent"])
    assert not any(row["is_mine"] is True for row in body["spotlight"])

    assert body["me"]["listed"] is False
    assert body["me"]["can_list"] is True
    assert body["me"]["badge_count"] == 1
    assert body["me"]["recent"][0]["achievement_type"] == "first_blood"


def test_wall_can_show_the_username(
    client, auth_headers, celebration_data, db_session
):
    other = celebration_data["other"]
    other.scoreboard_name_mode = "username"
    db_session.commit()

    resp = client.get(
        "/api/dashboard/celebrations?limit=50", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    items = [
        item for item in body["recent"]
        if item["display_name"] == other.username
    ]
    assert items
    assert all(item["username"] == other.username for item in items)
    assert all(item["name_mode"] == "username" for item in items)


def test_wall_can_show_an_anonymous_name(
    client, auth_headers, celebration_data, db_session
):
    other = celebration_data["other"]
    other.scoreboard_name_mode = "anonymous"
    db_session.commit()

    resp = client.get(
        "/api/dashboard/celebrations?limit=50", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    items = [
        item for item in body["recent"]
        if item["display_name"] == "Anonymous participant"
    ]
    assert items
    assert all(item["username"] is None for item in items)
    assert all(item["name_mode"] == "anonymous" for item in items)
    assert all(item["avatar_data"] is None for item in items)
    assert any(
        row["display_name"] == "Anonymous participant"
        for row in body["spotlight"]
    )


def test_actor_can_toggle_one_anonymous_celebration(
    client, auth_headers, celebration_data, test_user, db_session
):
    other = celebration_data["other"]
    other_achievement = (
        db_session.query(Achievement)
        .filter(Achievement.user_id == other.id)
        .first()
    )
    own_achievement = (
        db_session.query(Achievement)
        .filter(Achievement.user_id == test_user.id)
        .first()
    )
    hidden = celebration_data["hidden"]
    hidden_achievement = (
        db_session.query(Achievement)
        .filter(Achievement.user_id == hidden.id)
        .first()
    )

    first = client.post(
        f"/api/dashboard/celebrations/{other_achievement.id}/celebrate",
        headers=auth_headers,
    )
    assert first.status_code == 200, first.text
    assert first.json() == {"celebrated": True, "count": 1}

    second = client.post(
        f"/api/dashboard/celebrations/{other_achievement.id}/celebrate",
        headers=auth_headers,
    )
    assert second.status_code == 200, second.text
    assert second.json() == {"celebrated": False, "count": 0}

    own = client.post(
        f"/api/dashboard/celebrations/{own_achievement.id}/celebrate",
        headers=auth_headers,
    )
    assert own.status_code == 400

    hidden_resp = client.post(
        f"/api/dashboard/celebrations/{hidden_achievement.id}/celebrate",
        headers=auth_headers,
    )
    assert hidden_resp.status_code == 404


def test_minor_is_excluded_from_the_public_wall(
    client, auth_headers, celebration_data, db_session
):
    suffix = uuid.uuid4().hex[:8]
    minor = User(
        username=f"celebration_minor_{suffix}",
        email=f"celebration_minor_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        role="student",
        is_approved=True,
        show_on_scoreboard=True,
        scoreboard_name_mode="real_name",
        is_minor=True,
        first_name="Minor",
        last_name="Learner",
    )
    db_session.add(minor)
    db_session.flush()
    db_session.add(
        Achievement(
            user_id=minor.id,
            course_id=celebration_data["course"].id,
            achievement_type="first_blood",
            awarded_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()

    resp = client.get(
        "/api/dashboard/celebrations?limit=50", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert all(item["user_id"] is None for item in body["recent"])
    assert not any(
        item["display_name"] == "Minor Learner" for item in body["recent"]
    )
    assert not any(
        row["display_name"] == "Minor Learner" for row in body["spotlight"]
    )


def test_avatar_border_settings_round_trip(client, auth_headers):
    updated = client.put(
        "/api/auth/settings",
        json={"avatar_border_style": "gradient", "avatar_border_color": "rose"},
        headers=auth_headers,
    )
    assert updated.status_code == 200, updated.text

    settings = client.get("/api/auth/settings", headers=auth_headers)
    assert settings.status_code == 200, settings.text
    assert settings.json()["avatar_border_style"] == "gradient"
    assert settings.json()["avatar_border_color"] == "rose"

    me = client.get("/api/auth/me", headers=auth_headers)
    assert me.status_code == 200, me.text
    assert me.json()["avatar_border_style"] == "gradient"
    assert me.json()["avatar_border_color"] == "rose"

    invalid = client.put(
        "/api/auth/settings",
        json={"avatar_border_color": "not-a-colour"},
        headers=auth_headers,
    )
    assert invalid.status_code == 422, invalid.text


def test_avatar_border_accepts_hex_colour(client, auth_headers):
    updated = client.put(
        "/api/auth/settings",
        json={"avatar_border_color": "#22C55E"},
        headers=auth_headers,
    )
    assert updated.status_code == 200, updated.text

    settings = client.get("/api/auth/settings", headers=auth_headers)
    assert settings.status_code == 200, settings.text
    assert settings.json()["avatar_border_color"] == "#22c55e"

    malformed = client.put(
        "/api/auth/settings",
        json={"avatar_border_color": "#12345"},
        headers=auth_headers,
    )
    assert malformed.status_code == 422, malformed.text
