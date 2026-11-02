"""Achievement trigger tests for the OSINT track.

The custom-achievement evaluator is course-scoped, so these tests set up a
small OSINT course, assign one test lab to it, and submit a correct flag. The
submission path runs the achievement check in a background task; TestClient
waits for it before returning.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models import (
    Achievement,
    Course,
    CourseEnrollment,
    CourseLabAssignment,
    CustomAchievement,
    Lab,
    Level,
    Track,
)

pytestmark = pytest.mark.db


@pytest.fixture()
def osint_course(db_session, test_user, test_lab):
    """A one-lab OSINT course with every OSINT trigger represented."""
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)

    track = Track(
        name=f"OSINT Test {suffix}",
        slug="osint",
        description="Test-only OSINT track",
        icon="osint",
        color="#0EA5E9",
        sort_order=99,
        is_active=True,
        sequential=False,
    )
    db_session.add(track)
    db_session.flush()

    level = Level(
        track_id=track.id,
        level_number=1,
        name="OSINT Test Level",
        description="Test-only level",
        sort_order=1,
    )
    db_session.add(level)
    db_session.flush()

    test_lab.level_id = level.id

    course = Course(
        name=f"OSINT Achievement Test {suffix}",
        code=f"OS{suffix[:5].upper()}",
        semester="Test",
        invite_code=f"OSINT-{suffix}",
        instructor_id=test_user.id,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db_session.add(course)
    db_session.flush()

    db_session.add_all([
        CourseEnrollment(
            course_id=course.id,
            user_id=test_user.id,
            enrolled_at=now - timedelta(hours=1),
        ),
        CourseLabAssignment(
            course_id=course.id,
            lab_id=test_lab.id,
            sort_order=1,
        ),
    ])
    db_session.flush()

    definitions = [
        CustomAchievement(
            name=f"OSINT First {suffix}",
            description="Complete one OSINT exercise.",
            icon="\U0001F50E",
            trigger="osint_labs_completed",
            threshold=1,
            is_active=True,
        ),
        CustomAchievement(
            name=f"OSINT No Hints {suffix}",
            description="Complete one OSINT exercise without hints.",
            icon="\U0001F9ED",
            trigger="osint_no_hint_labs",
            threshold=1,
            is_active=True,
        ),
        CustomAchievement(
            name=f"OSINT Perfect {suffix}",
            description="Complete one OSINT exercise on the first attempt.",
            icon="\U0001F6F0",
            trigger="osint_perfect_labs",
            threshold=1,
            is_active=True,
        ),
        CustomAchievement(
            name=f"OSINT Complete {suffix}",
            description="Complete every assigned OSINT exercise.",
            icon="\U0001F310",
            trigger="osint_track_completed",
            threshold=1,
            is_active=True,
        ),
    ]
    db_session.add_all(definitions)
    db_session.commit()

    yield {
        "course": course,
        "definitions": definitions,
        "track": track,
        "level": level,
    }

    db_session.query(Achievement).filter(
        Achievement.course_id == course.id
    ).delete()
    db_session.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course.id
    ).delete()
    db_session.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course.id
    ).delete()
    db_session.query(Course).filter(Course.id == course.id).delete()
    for definition in definitions:
        db_session.query(CustomAchievement).filter(
            CustomAchievement.id == definition.id
        ).delete()
    db_session.query(Lab).filter(Lab.id == test_lab.id).update({"level_id": None})
    db_session.query(Level).filter(Level.id == level.id).delete()
    db_session.query(Track).filter(Track.id == track.id).delete()
    db_session.commit()


def test_osint_triggers_award_all_matching_achievements(
    client, auth_headers, test_user, test_lab, test_flag, osint_course, db_session
):
    resp = client.post(
        f"/api/exercises/labs/{test_lab.id}/submit-flag",
        json={"flag": test_flag},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["correct"] is True

    db_session.expire_all()
    awarded = {
        row.achievement_type
        for row in db_session.query(Achievement).filter(
            Achievement.user_id == test_user.id,
            Achievement.course_id == osint_course["course"].id,
        ).all()
    }

    for definition in osint_course["definitions"]:
        assert f"custom_{definition.id}" in awarded, definition.name


def _submit_flag(client, auth_headers, lab, flag):
    resp = client.post(
        f"/api/exercises/labs/{lab.id}/submit-flag",
        json={"flag": flag},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["correct"] is True


def test_hidden_shell_shocked_awarded(
    client, auth_headers, test_user, test_lab, test_flag, osint_course, db_session
):
    test_lab.slug = "software-security-2-1-diagnostics-command-injection"
    db_session.commit()
    _submit_flag(client, auth_headers, test_lab, test_flag)

    db_session.expire_all()
    awarded = {
        row.achievement_type
        for row in db_session.query(Achievement).filter(
            Achievement.user_id == test_user.id,
            Achievement.course_id == osint_course["course"].id,
        ).all()
    }
    assert "shell_shocked" in awarded


def test_hidden_source_whisperer_awarded(
    client, auth_headers, test_user, test_lab, test_flag, osint_course, db_session
):
    test_lab.slug = "software-security-1-1-hidden-export-route"
    db_session.commit()
    _submit_flag(client, auth_headers, test_lab, test_flag)

    db_session.expire_all()
    awarded = {
        row.achievement_type
        for row in db_session.query(Achievement).filter(
            Achievement.user_id == test_user.id,
            Achievement.course_id == osint_course["course"].id,
        ).all()
    }
    assert "source_whisperer" in awarded


def test_hidden_devfest_ghost_custom_trigger(
    client, auth_headers, test_user, test_lab, test_flag, osint_course, db_session
):
    test_lab.slug = "high-school-12-1-devfest-community-portal"
    db_session.commit()

    definition = CustomAchievement(
        name=f"DevFest Ghost Test {uuid.uuid4().hex[:6]}",
        description="Complete a DevFest starter without hints.",
        icon="\U0001F47B",
        trigger="devfest_no_hint_labs",
        threshold=1,
        is_active=True,
    )
    db_session.add(definition)
    db_session.commit()

    try:
        _submit_flag(client, auth_headers, test_lab, test_flag)
        db_session.expire_all()
        awarded = {
            row.achievement_type
            for row in db_session.query(Achievement).filter(
                Achievement.user_id == test_user.id,
                Achievement.course_id == osint_course["course"].id,
            ).all()
        }
        assert f"custom_{definition.id}" in awarded
    finally:
        db_session.query(Achievement).filter(
            Achievement.course_id == osint_course["course"].id,
            Achievement.achievement_type == f"custom_{definition.id}",
        ).delete()
        db_session.query(CustomAchievement).filter(
            CustomAchievement.id == definition.id
        ).delete()
        db_session.commit()


def test_hidden_comeback_trigger(
    client, auth_headers, test_user, test_lab, test_flag, osint_course, db_session
):
    definition = CustomAchievement(
        name=f"Phoenix Test {uuid.uuid4().hex[:6]}",
        description="Return after five failed attempts.",
        icon="\U0001F525",
        trigger="comeback_labs",
        threshold=1,
        is_active=True,
    )
    db_session.add(definition)
    db_session.commit()

    try:
        for _ in range(5):
            wrong = client.post(
                f"/api/exercises/labs/{test_lab.id}/submit-flag",
                json={"flag": "OCR{definitely_not_the_flag}"},
                headers=auth_headers,
            )
            assert wrong.status_code == 200, wrong.text
            assert wrong.json()["correct"] is False

        _submit_flag(client, auth_headers, test_lab, test_flag)
        db_session.expire_all()
        awarded = {
            row.achievement_type
            for row in db_session.query(Achievement).filter(
                Achievement.user_id == test_user.id,
                Achievement.course_id == osint_course["course"].id,
            ).all()
        }
        assert f"custom_{definition.id}" in awarded
    finally:
        db_session.query(Achievement).filter(
            Achievement.course_id == osint_course["course"].id,
            Achievement.achievement_type == f"custom_{definition.id}",
        ).delete()
        db_session.query(CustomAchievement).filter(
            CustomAchievement.id == definition.id
        ).delete()
        db_session.commit()
