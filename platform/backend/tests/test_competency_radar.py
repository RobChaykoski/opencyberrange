"""Competency radar scoring, overlays, drill-down, and cohort suppression."""

import json
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import (
    Course,
    CourseEnrollment,
    CourseFeedback,
    ExercisePulseSurvey,
    ExerciseQuizAttempt,
    Lab,
    LabCompletion,
    Level,
    Track,
    User,
)
from app.services.competency_model import AXIS_KEYS, mapping_for_lab
from app.services.competency_radar import build_cohort_radar, build_individual_radar

pytestmark = pytest.mark.db
PASSWORD = "Radar#Pass123"


def _user(db, prefix, role="student"):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"{prefix}_{suffix}",
        email=f"{prefix}_{suffix}@example.invalid",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role=role,
        survey_opt_in=True,
    )
    db.add(user)
    db.flush()
    return user


def _course(db, instructor):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    course = Course(
        name=f"Radar Course {suffix}",
        code=f"RAD{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"RAD-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=20),
        end_date=now + timedelta(days=20),
        is_active=True,
    )
    db.add(course)
    db.flush()
    return course


def _lab(db, suffix):
    track = db.query(Track).filter(Track.slug == "web").first()
    if track is None:
        track = Track(name=f"Radar Web {suffix}", slug="web", is_active=True)
        db.add(track)
        db.flush()
    level = db.query(Level).filter(
        Level.track_id == track.id, Level.level_number == 1
    ).first()
    if level is None:
        level = Level(track_id=track.id, level_number=1, name="Radar Level")
        db.add(level)
        db.flush()
    lab = Lab(
        name=f"Radar Web Lab {suffix}",
        slug=f"radar-web-lab-{suffix}",
        description="Radar test lab",
        compose_file="services: {}\n",
        is_active=True,
        visibility="public",
        level_id=level.id,
        duration_minutes=30,
        difficulty="beginner",
    )
    db.add(lab)
    db.flush()
    return lab


def _seed_student(db, course, lab, index):
    student = _user(db, f"radar_student_{index}")
    db.add(CourseEnrollment(course_id=course.id, user_id=student.id))
    now = datetime.now(timezone.utc)
    mapping = mapping_for_lab(lab)
    db.add(LabCompletion(
        user_id=student.id,
        lab_id=lab.id,
        flag_submitted="OCR{radar_test}",
        attempts=1,
        hints_used=0,
        time_spent_minutes=25,
        started_at=now - timedelta(days=2),
        completed_at=now - timedelta(days=1),
        competency_model_version=mapping["model_version"],
        competency_mapping=json.dumps(mapping),
        lab_difficulty_snapshot="beginner",
    ))
    db.add(ExerciseQuizAttempt(
        user_id=student.id,
        lab_id=lab.id,
        course_id=course.id,
        question_keys=json.dumps(["q1"]),
        answers=json.dumps({"q1": 0}),
        score=80 + index,
        correct=1,
        total=1,
        passed=True,
        taken_at=now - timedelta(days=1),
        completed_at=now - timedelta(days=1),
    ))
    db.add(CourseFeedback(
        course_id=course.id,
        author_id=course.instructor_id,
        subject_user_id=student.id,
        direction="instructor_student",
        clarity=4,
        challenge=3,
        engagement=4,
        confidence=4,
    ))
    db.add(ExercisePulseSurvey(
        user_id=student.id,
        lab_id=lab.id,
        course_id=course.id,
        difficulty=3,
        learning=4,
    ))
    return student


def test_individual_radar_has_eight_axes_and_evidence_drilldown(db_session):
    instructor = _user(db_session, "radar_instructor", "instructor")
    course = _course(db_session, instructor)
    lab = _lab(db_session, uuid.uuid4().hex[:6])
    student = _seed_student(db_session, course, lab, 1)
    db_session.commit()

    radar = build_individual_radar(db_session, student.id)
    assert [axis["key"] for axis in radar["axes"]] == list(AXIS_KEYS)
    web = next(axis for axis in radar["axes"] if axis["key"] == "web_api")
    assert web["baseline"] is not None
    assert web["current"] is not None
    assert web["target"] == 80.0
    assert web["components"]["assessment"] is not None
    assert web["components"]["independent"] == 100.0
    assert web["components"]["instructor"] is not None
    assert web["contributing_labs"][0]["lab_name"] == lab.name
    assert web["model_version"] == "2026.1"
    assert web["self_confidence"]["responses"] == 1
    assert radar["weights"]["assessment"] == 0.5


def test_radar_marks_missing_components_as_provisional(db_session):
    instructor = _user(db_session, "radar_instructor", "instructor")
    course = _course(db_session, instructor)
    lab = _lab(db_session, uuid.uuid4().hex[:6])
    student = _user(db_session, "radar_only_completion")
    db_session.add(CourseEnrollment(course_id=course.id, user_id=student.id))
    now = datetime.now(timezone.utc)
    mapping = mapping_for_lab(lab)
    db_session.add(LabCompletion(
        user_id=student.id,
        lab_id=lab.id,
        flag_submitted="OCR{radar_test}",
        attempts=1,
        hints_used=0,
        completed_at=now,
        competency_model_version=mapping["model_version"],
        competency_mapping=json.dumps(mapping),
        lab_difficulty_snapshot="beginner",
    ))
    db_session.commit()

    radar = build_individual_radar(db_session, student.id)
    web = next(axis for axis in radar["axes"] if axis["key"] == "web_api")
    assert web["provisional"] is True
    assert web["weight_coverage_pct"] < 100
    assert web["components"]["assessment"] is None
    assert web["components"]["instructor"] is None


def test_cohort_radar_suppresses_below_minimum_and_allows_at_minimum(db_session):
    instructor = _user(db_session, "radar_instructor", "instructor")
    course = _course(db_session, instructor)
    lab = _lab(db_session, uuid.uuid4().hex[:6])
    students = [_seed_student(db_session, course, lab, index) for index in range(5)]
    db_session.commit()

    cohort = build_cohort_radar(db_session, course, [s.id for s in students], minimum=5)
    assert cohort["suppressed"] is False
    web = next(axis for axis in cohort["axes"] if axis["key"] == "web_api")
    assert web["cohort_median"] is not None
    assert web["cohort_q1"] is not None
    assert web["cohort_q3"] is not None
    assert web["learners_with_evidence"] == 5

    small = build_cohort_radar(db_session, course, [s.id for s in students[:3]], minimum=5)
    assert small["suppressed"] is True
    small_web = next(axis for axis in small["axes"] if axis["key"] == "web_api")
    assert small_web["cohort_median"] is None
    assert small_web["suppressed"] is True
