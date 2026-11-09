"""DB-backed coverage for course progress and the teaching-focus aggregates.

These exercise the response builders directly so the tests stay focused on
the data semantics (enrollment boundary, resets, certificate proximity) rather
than HTTP plumbing that other suites already cover.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import (
    Course,
    CourseCompletionReset,
    CourseEnrollment,
    CourseLabAssignment,
    Lab,
    LabCompletion,
    Level,
    Track,
    User,
)
from app.routers.courses import _course_response
from app.routers.dashboard import _instructor_teaching_focus

NOW = datetime.now(timezone.utc)


def _make_user(db, role, suffix):
    user = User(
        username=f"focus_{role}_{suffix}",
        email=f"focus_{role}_{suffix}@university.edu",
        hashed_password=get_password_hash("Correct#Horse7Battery"),
        is_active=True,
        is_admin=False,
        role=role,
        is_approved=True,
        last_login_at=NOW - timedelta(hours=1),
    )
    db.add(user)
    db.flush()
    return user


def _make_course(db, instructor, lab_count, suffix):
    track = Track(
        name=f"Focus Track {suffix}",
        slug=f"focus-track-{suffix}",
        is_active=True,
    )
    db.add(track)
    db.flush()
    level = Level(track_id=track.id, level_number=1, name="Focus Level")
    db.add(level)
    db.flush()

    labs = []
    for index in range(lab_count):
        lab = Lab(
            name=f"Focus Lab {index + 1} {suffix}",
            slug=f"focus-lab-{index + 1}-{suffix}",
            description="Teaching focus test lab",
            compose_file="services: {}\n",
            is_active=True,
            visibility="public",
            level_id=level.id,
            duration_minutes=30,
            difficulty="easy",
        )
        db.add(lab)
        labs.append(lab)
    db.flush()

    course = Course(
        name=f"Focus Course {suffix}",
        code=f"FC{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"FC-{suffix}",
        instructor_id=instructor.id,
        start_date=NOW - timedelta(days=30),
        end_date=NOW + timedelta(days=30),
        is_active=True,
    )
    db.add(course)
    db.flush()
    for order, lab in enumerate(labs):
        db.add(CourseLabAssignment(
            course_id=course.id, lab_id=lab.id, sort_order=order,
        ))
    db.flush()
    return course, level, labs


def _complete(db, user, lab, when, flag="OCR{focus}"):
    completion = db.query(LabCompletion).filter(
        LabCompletion.user_id == user.id,
        LabCompletion.lab_id == lab.id,
    ).first()
    if completion is None:
        completion = LabCompletion(
            user_id=user.id,
            lab_id=lab.id,
            attempts=1,
            hints_used=0,
            time_spent_minutes=10,
        )
        db.add(completion)
    completion.flag_submitted = flag
    completion.completed_at = when
    db.flush()


@pytest.fixture()
def focus_setup(db_session):
    suffix = uuid.uuid4().hex[:8]
    instructor = _make_user(db_session, "instructor", suffix)
    student = _make_user(db_session, "student", suffix)
    inactive = _make_user(db_session, "student", f"{suffix}i")
    inactive.last_login_at = NOW - timedelta(days=10)
    course, level, labs = _make_course(
        db_session, instructor, 3, suffix,
    )
    db_session.add_all([
        CourseEnrollment(
            course_id=course.id,
            user_id=student.id,
            enrolled_at=NOW - timedelta(days=10),
        ),
        CourseEnrollment(
            course_id=course.id,
            user_id=inactive.id,
            enrolled_at=NOW - timedelta(days=15),
        ),
    ])
    db_session.flush()
    return {
        "instructor": instructor,
        "student": student,
        "inactive": inactive,
        "course": course,
        "level": level,
        "labs": labs,
    }


def test_course_response_includes_learner_progress(db_session, focus_setup):
    student = focus_setup["student"]
    course = focus_setup["course"]
    labs = focus_setup["labs"]

    _complete(db_session, student, labs[0], NOW - timedelta(days=2))
    _complete(db_session, student, labs[1], NOW - timedelta(days=1))

    learner_view = _course_response(course, db_session, student.id)
    assert learner_view["completed_labs"] == 2
    assert learner_view["progress_percent"] == 67

    staff_view = _course_response(course, db_session)
    assert staff_view["completed_labs"] is None
    assert staff_view["progress_percent"] is None


def test_teaching_focus_counts_only_post_enrollment_completions(
    db_session, focus_setup,
):
    instructor = focus_setup["instructor"]
    student = focus_setup["student"]
    labs = focus_setup["labs"]

    # Lab 1 was earned before this learner enrolled, so it must not count.
    _complete(db_session, student, labs[0], NOW - timedelta(days=20))
    _complete(db_session, student, labs[1], NOW - timedelta(days=2))

    focus = _instructor_teaching_focus(
        db_session, instructor, NOW, admin_ids=set(),
    )
    assert focus["near_certificate_count"] == 0
    assert focus["recent_completions_count"] == 1

    _complete(db_session, student, labs[2], NOW - timedelta(hours=1))
    focus = _instructor_teaching_focus(
        db_session, instructor, NOW, admin_ids=set(),
    )
    assert focus["near_certificate_count"] == 1
    near = focus["near_certificate"][0]
    assert near["username"] == student.username
    assert (near["completed"], near["total"]) == (2, 3)

    # Re-earning the pre-enrollment lab now completes the level.
    _complete(db_session, student, labs[0], NOW - timedelta(minutes=30))
    focus = _instructor_teaching_focus(
        db_session, instructor, NOW, admin_ids=set(),
    )
    assert focus["near_certificate_count"] == 0
    assert focus["recent_certificates_count"] == 1
    assert focus["recent_certificates"][0]["username"] == student.username

    assert focus["inactive_students_count"] == 1
    assert focus["inactive_students"][0]["username"] == focus_setup["inactive"].username


def test_teaching_focus_honors_completion_resets(db_session, focus_setup):
    instructor = focus_setup["instructor"]
    student = focus_setup["student"]
    course = focus_setup["course"]
    labs = focus_setup["labs"]

    _complete(db_session, student, labs[0], NOW - timedelta(days=2))
    _complete(db_session, student, labs[1], NOW - timedelta(days=2))
    _complete(db_session, student, labs[2], NOW - timedelta(days=2))
    db_session.add(CourseCompletionReset(
        course_id=course.id,
        user_id=student.id,
        lab_id=labs[0].id,
        reset_at=NOW - timedelta(days=1),
    ))
    db_session.flush()

    focus = _instructor_teaching_focus(
        db_session, instructor, NOW, admin_ids=set(),
    )
    assert focus["near_certificate_count"] == 1
    near = focus["near_certificate"][0]
    assert (near["completed"], near["total"]) == (2, 3)
