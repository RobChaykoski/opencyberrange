"""Learning analytics API tests for V2 Phase 1."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import (
    Course,
    CourseEnrollment,
    CourseLabAssignment,
    ExercisePulseSurvey,
    ExerciseReaction,
    Lab,
    LabCompletion,
    LabSession,
    Level,
    Survey,
    SurveyAttachment,
    SurveyResponse,
    Track,
    User,
)

pytestmark = pytest.mark.db

TEST_PASSWORD = "Correct#Horse7Battery"


def _login(client, user):
    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture()
def analytics_data(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)

    instructor = User(
        username=f"analytics_instructor_{suffix}",
        email=f"analytics_instructor_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="instructor",
    )
    outsider = User(
        username=f"analytics_outsider_{suffix}",
        email=f"analytics_outsider_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="instructor",
    )
    student_one = User(
        username=f"analytics_student_one_{suffix}",
        email=f"analytics_student_one_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
        first_name="Avery",
        last_name="One",
        survey_opt_in=True,
    )
    student_two = User(
        username=f"analytics_student_two_{suffix}",
        email=f"analytics_student_two_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
        first_name="Blake",
        last_name="Two",
    )
    db_session.add_all([instructor, outsider, student_one, student_two])
    db_session.flush()

    track = Track(
        name=f"Analytics Track {suffix}",
        slug="web",
        is_active=True,
    )
    db_session.add(track)
    db_session.flush()
    level = Level(track_id=track.id, level_number=1, name="Analytics Level")
    db_session.add(level)
    db_session.flush()

    labs = []
    for index in range(6):
        lab = Lab(
            name=f"Analytics Lab {index + 1} {suffix}",
            slug=f"analytics-lab-{index + 1}-{suffix}",
            description="Analytics test lab",
            compose_file="services: {}\n",
            is_active=True,
            visibility="public",
            level_id=level.id,
            duration_minutes=60,
            difficulty="medium",
        )
        db_session.add(lab)
        labs.append(lab)
    db_session.flush()

    course = Course(
        name=f"Analytics Course {suffix}",
        code=f"AN{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"AN-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=20),
        end_date=now + timedelta(days=20),
        is_active=True,
    )
    db_session.add(course)
    db_session.flush()
    db_session.add_all([
        CourseEnrollment(
            course_id=course.id, user_id=student_one.id,
            enrolled_at=now - timedelta(days=10),
        ),
        CourseEnrollment(
            course_id=course.id, user_id=student_two.id,
            enrolled_at=now - timedelta(days=10),
        ),
    ])
    for order, lab in enumerate(labs):
        db_session.add(CourseLabAssignment(
            course_id=course.id, lab_id=lab.id, sort_order=order,
        ))
        db_session.add(LabSession(
            user_id=student_one.id,
            lab_id=lab.id,
            status="stopped",
            started_at=now - timedelta(days=5),
            expires_at=now + timedelta(hours=1),
            stopped_at=now - timedelta(days=5) + timedelta(hours=1),
        ))
    for lab in labs[:3]:
        db_session.add(LabSession(
            user_id=student_two.id,
            lab_id=lab.id,
            status="stopped",
            started_at=now - timedelta(days=4),
            expires_at=now + timedelta(hours=1),
            stopped_at=now - timedelta(days=4) + timedelta(hours=1),
        ))

    hint_sequence = [2, 2, 2, 0, 0, 0]
    attempt_sequence = [3, 3, 3, 1, 1, 1]
    time_sequence = [120, 120, 120, 30, 30, 30]
    for index, lab in enumerate(labs):
        db_session.add(LabCompletion(
            user_id=student_one.id,
            lab_id=lab.id,
            flag_submitted="OCR{analytics}",
            completed_at=now - timedelta(days=3) + timedelta(minutes=index),
            attempts=attempt_sequence[index],
            hints_used=hint_sequence[index],
            time_spent_minutes=time_sequence[index],
        ))
    for index, lab in enumerate(labs[:3]):
        db_session.add(LabCompletion(
            user_id=student_two.id,
            lab_id=lab.id,
            flag_submitted="OCR{analytics}",
            completed_at=now - timedelta(days=2) + timedelta(minutes=index),
            attempts=1,
            hints_used=0,
            time_spent_minutes=20,
        ))
    db_session.add_all([
        ExercisePulseSurvey(
            user_id=student_one.id,
            lab_id=labs[0].id,
            course_id=course.id,
            difficulty=3,
            learning=5,
            unclear="The final hint could be clearer.",
        ),
        ExercisePulseSurvey(
            user_id=student_one.id,
            lab_id=labs[1].id,
            course_id=course.id,
            difficulty=2,
            learning=4,
        ),
    ])
    db_session.commit()

    yield {
        "course": course,
        "instructor": instructor,
        "outsider": outsider,
        "student_one": student_one,
        "student_two": student_two,
        "labs": labs,
        "track": track,
        "level": level,
    }

    lab_ids = [lab.id for lab in labs]
    db_session.query(ExercisePulseSurvey).filter(
        ExercisePulseSurvey.lab_id.in_(lab_ids)
    ).delete(synchronize_session=False)
    db_session.query(ExerciseReaction).filter(
        ExerciseReaction.lab_id.in_(lab_ids)
    ).delete(synchronize_session=False)
    db_session.query(LabCompletion).filter(
        LabCompletion.lab_id.in_(lab_ids)
    ).delete(synchronize_session=False)
    db_session.query(LabSession).filter(
        LabSession.lab_id.in_(lab_ids)
    ).delete(synchronize_session=False)
    db_session.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course.id
    ).delete(synchronize_session=False)
    db_session.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course.id
    ).delete(synchronize_session=False)
    db_session.query(Course).filter(Course.id == course.id).delete()
    db_session.query(Lab).filter(Lab.id.in_(lab_ids)).delete(synchronize_session=False)
    db_session.query(Level).filter(Level.id == level.id).delete()
    db_session.query(Track).filter(Track.id == track.id).delete()
    for user in (instructor, outsider, student_one, student_two):
        db_session.query(User).filter(User.id == user.id).delete()
    db_session.commit()


def test_student_analytics_summary_and_growth(client, analytics_data):
    headers = _login(client, analytics_data["student_one"])
    resp = client.get("/api/analytics/student/me", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    summary = body["summary"]
    assert summary["started_exercises"] == 6
    assert summary["completed_exercises"] == 6
    assert summary["completion_rate"] == 100.0
    assert summary["hints_used"] == 6
    assert summary["hint_free_rate"] == 50.0
    assert summary["first_attempt_rate"] == 50.0
    assert summary["reattempt_rate"] == 50.0
    assert summary["total_learning_minutes"] == 450
    assert summary["total_learning_hours"] == 7.5

    growth = {item["label"]: item for item in body["growth"]}
    assert growth["Hint usage"]["status"] == "improving"
    assert growth["First-attempt success"]["status"] == "improving"
    assert growth["Time efficiency"]["status"] == "improving"
    assert growth["Persistence"]["value"] == 3
    assert growth["Breadth"]["value"] == 1

    prompts = {item["id"]: item for item in body["ai_prompts"]}
    assert "hint-coaching" in prompts
    assert "debug-coach" in prompts
    assert "do not give me the flag" in prompts["hint-coaching"]["prompt"].lower()
    assert len(body["ai_prompts"]) <= 4

    domains = {item["key"]: item for item in body["domains"]}
    assert domains["web"]["completed_exercises"] == 6
    assert domains["web"]["evidence_level"] == "strong"
    assert body["learning_impact"]["learning_reported"] == 4.5
    assert body["summary"]["pulse_responses"] == 2


def test_student_analytics_marks_insufficient_evidence(
    client, analytics_data
):
    headers = _login(client, analytics_data["student_two"])
    resp = client.get("/api/analytics/student/me", headers=headers)
    assert resp.status_code == 200, resp.text
    growth = {item["label"]: item for item in resp.json()["growth"]}
    assert growth["Hint usage"]["status"] == "insufficient_evidence"


def test_course_overview_and_exercises(client, analytics_data):
    headers = _login(client, analytics_data["instructor"])
    course_id = analytics_data["course"].id

    overview = client.get(
        f"/api/analytics/courses/{course_id}/overview", headers=headers
    )
    assert overview.status_code == 200, overview.text
    summary = overview.json()["summary"]
    assert summary["enrolled_learners"] == 2
    assert summary["assigned_exercises"] == 6
    assert summary["started_learners"] == 2
    assert summary["completed_learners"] == 2
    assert summary["completion_rate"] == 75.0
    assert summary["hint_free_rate"] == 66.7
    assert summary["first_attempt_rate"] == 66.7
    assert summary["abandonment_rate"] == 0.0
    assert summary["learning_reported"] == 4.5
    assert summary["confidence_gain"] is not None
    assert summary["total_learning_minutes"] == 510
    assert summary["total_learning_hours"] == 8.5
    assert summary["learning_learners"] == 2
    assert summary["median_learning_minutes_per_learner"] == 255.0
    assert summary["rag"] == "amber"

    exercises = client.get(
        f"/api/analytics/courses/{course_id}/exercises", headers=headers
    )
    assert exercises.status_code == 200, exercises.text
    rows = exercises.json()["exercises"]
    assert len(rows) == 6
    first = next(row for row in rows if row["lab_id"] == analytics_data["labs"][0].id)
    assert first["started_learners"] == 2
    assert first["completed_learners"] == 2
    assert first["completion_rate"] == 100.0
    assert first["median_attempts"] == 2.0
    assert first["hint_pressure_rate"] == 50.0
    assert first["learning_reported"] == 5.0
    assert first["pulse_response_rate"] == 50.0
    assert first["rag"] == "green"
    assert "high_hint_pressure" in first["flags"]

    comments = client.get(
        f"/api/analytics/courses/{course_id}/pulse-comments", headers=headers
    )
    assert comments.status_code == 200, comments.text
    assert comments.json()["comments"][0]["unclear"] == "The final hint could be clearer."


def test_exercise_reaction_is_reported_and_can_be_cleared(client, analytics_data):
    student = _login(client, analytics_data["student_one"])
    instructor = _login(client, analytics_data["instructor"])
    lab_id = analytics_data["labs"][0].id
    course_id = analytics_data["course"].id

    initial = client.get(f"/api/analytics/reaction/{lab_id}", headers=student)
    assert initial.status_code == 200, initial.text
    assert initial.json()["reaction"] is None

    liked = client.post(
        f"/api/analytics/reaction/{lab_id}",
        json={"reaction": "like", "course_id": course_id},
        headers=student,
    )
    assert liked.status_code == 200, liked.text
    assert liked.json()["reaction"] == "like"

    overview = client.get(
        f"/api/analytics/courses/{course_id}/overview", headers=instructor
    )
    summary = overview.json()["summary"]
    assert summary["likes"] == 1
    assert summary["dislikes"] == 0
    assert summary["reaction_count"] == 1
    assert summary["positive_rate"] == 100.0

    exercises = client.get(
        f"/api/analytics/courses/{course_id}/exercises", headers=instructor
    )
    row = next(
        item for item in exercises.json()["exercises"]
        if item["lab_id"] == lab_id
    )
    assert row["likes"] == 1
    assert row["reaction_count"] == 1

    changed = client.post(
        f"/api/analytics/reaction/{lab_id}",
        json={"reaction": "dislike", "course_id": course_id},
        headers=student,
    )
    assert changed.status_code == 200, changed.text
    assert changed.json()["reaction"] == "dislike"

    cleared = client.post(
        f"/api/analytics/reaction/{lab_id}",
        json={"reaction": None, "course_id": course_id},
        headers=student,
    )
    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["reaction"] is None


def test_exercise_reaction_requires_started_exercise(client, analytics_data):
    student_two = _login(client, analytics_data["student_two"])
    unstarted_lab = analytics_data["labs"][5].id
    resp = client.post(
        f"/api/analytics/reaction/{unstarted_lab}",
        json={"reaction": "like", "course_id": analytics_data["course"].id},
        headers=student_two,
    )
    assert resp.status_code == 403


def test_reports_pdf_export(client, analytics_data):
    headers = _login(client, analytics_data["instructor"])
    resp = client.get("/api/analytics/reports/export.pdf", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")


def test_pulse_survey_is_completion_gated_and_upserts(
    client, analytics_data
):
    headers = _login(client, analytics_data["student_one"])
    lab_id = analytics_data["labs"][0].id
    course_id = analytics_data["course"].id

    existing = client.get(f"/api/analytics/pulse/{lab_id}", headers=headers)
    assert existing.status_code == 200, existing.text
    assert existing.json()["submitted"] is True

    updated = client.post(
        f"/api/analytics/pulse/{lab_id}",
        json={
            "difficulty": 4,
            "learning": 3,
            "unclear": "The setup step was unclear.",
            "course_id": course_id,
        },
        headers=headers,
    )
    assert updated.status_code == 200, updated.text

    after = client.get(f"/api/analytics/pulse/{lab_id}", headers=headers)
    pulse = after.json()["pulse"]
    assert pulse["difficulty"] == 4
    assert pulse["learning"] == 3
    assert pulse["unclear"] == "The setup step was unclear."


def test_pulse_survey_requires_completion(client, analytics_data, db_session):
    student = analytics_data["student_two"]
    student.survey_opt_in = True
    db_session.commit()
    headers = _login(client, student)
    # Student two has no completion for lab six.
    unfinished_lab = analytics_data["labs"][5].id
    resp = client.post(
        f"/api/analytics/pulse/{unfinished_lab}",
        json={"difficulty": 3, "learning": 3},
        headers=headers,
    )
    assert resp.status_code == 400


def test_surveys_respect_opt_in_and_record_responses(client, analytics_data):
    instructor = _login(client, analytics_data["instructor"])
    student_one = _login(client, analytics_data["student_one"])
    student_two = _login(client, analytics_data["student_two"])
    course_id = analytics_data["course"].id

    created = client.post(
        "/api/analytics/surveys",
        json={
            "title": "Analytics reflection",
            "description": "Short course reflection",
            "course_ids": [course_id],
            "questions": [
                {"prompt": "How useful was this course?", "type": "scale"},
                {"prompt": "Would you recommend it?", "type": "choice", "options": ["Yes", "No"]},
                {"prompt": "What should change?", "type": "text"},
            ],
        },
        headers=instructor,
    )
    assert created.status_code == 200, created.text
    survey_id = created.json()["id"]

    try:
        # Student two has not opted in and must not see or submit the survey.
        blocked_list = client.get("/api/analytics/surveys/available", headers=student_two)
        assert blocked_list.status_code == 200
        assert blocked_list.json()["reason"] == "opt_in_required"
        blocked_submit = client.post(
            f"/api/analytics/surveys/{survey_id}/responses",
            json={"answers": {"0": 5, "1": "Yes", "2": "More labs"}},
            headers=student_two,
        )
        assert blocked_submit.status_code == 403

        # An opted-in learner sees the survey and can respond once.
        available = client.get("/api/analytics/surveys/available", headers=student_one)
        assert available.status_code == 200, available.text
        assert any(item["id"] == survey_id for item in available.json()["surveys"])

        submitted = client.post(
            f"/api/analytics/surveys/{survey_id}/responses",
            json={"answers": {"0": 5, "1": "Yes", "2": "More labs"}},
            headers=student_one,
        )
        assert submitted.status_code == 200, submitted.text

        responses = client.get(
            f"/api/analytics/surveys/{survey_id}/responses", headers=instructor
        )
        assert responses.status_code == 200, responses.text
        body = responses.json()
        assert body["survey"]["response_count"] == 1
        assert body["summary"]["0"]["counts"]["5"] == 1
        assert body["responses"][0]["answers"]["2"] == "More labs"

        listed = client.get("/api/analytics/surveys", headers=instructor)
        assert listed.status_code == 200
        assert any(
            item["id"] == survey_id and item["response_count"] == 1
            for item in listed.json()["surveys"]
        )
    finally:
        client.delete(f"/api/analytics/surveys/{survey_id}", headers=instructor)


def test_analytics_permissions(client, analytics_data):
    instructor_headers = _login(client, analytics_data["instructor"])
    outsider_headers = _login(client, analytics_data["outsider"])
    student_headers = _login(client, analytics_data["student_one"])
    course_id = analytics_data["course"].id

    outsider = client.get(
        f"/api/analytics/courses/{course_id}/overview",
        headers=outsider_headers,
    )
    assert outsider.status_code == 403

    student = client.get(
        f"/api/analytics/courses/{course_id}/overview",
        headers=student_headers,
    )
    assert student.status_code == 403

    metrics = client.get("/api/analytics/metrics", headers=student_headers)
    assert metrics.status_code == 200
    assert any(
        item["key"] == "hints_per_completion"
        for item in metrics.json()["metrics"]
    )

    workbook = client.post(
        "/api/analytics/events/workbook-open",
        json={"title": "Analytics workbook", "url": "/wiki/test/"},
        headers=student_headers,
    )
    assert workbook.status_code == 200, workbook.text

    owner = client.get(
        f"/api/analytics/courses/{course_id}/overview",
        headers=instructor_headers,
    )
    assert owner.status_code == 200


def test_reports_overview_includes_skill_tree(client, analytics_data):
    headers = _login(client, analytics_data["instructor"])
    course_id = analytics_data["course"].id

    resp = client.get("/api/analytics/reports/overview", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    row = next(
        item for item in body["courses"] if item["course"]["id"] == course_id
    )
    tree = row["skill_tree"]
    assert len(tree["dimensions"]) == 5
    assert tree["assigned_total"] == 6
    assert tree["completed_total"] == 6
    dimensions = {item["key"]: item for item in tree["dimensions"]}
    assert dimensions["builder"]["assigned"] == 6
    assert dimensions["builder"]["completed"] == 6
    assert dimensions["builder"]["assigned_pct"] == 100.0

    totals = body["totals"]["skill_tree"]
    assert totals["assigned_total"] == 6
    assert totals["completed_total"] == 6
    assert dimensions["explorer"]["assigned"] == 0
