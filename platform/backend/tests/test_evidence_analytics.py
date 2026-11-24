"""Aggregate evidence operations for instructors and administrators."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import Course, CourseEnrollment, EvidenceRecord, User
from app.services.evidence import auto_accept_record, create_record
from app.services.evidence_analytics import overview

PASSWORD = "Analytics#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role: str = "student") -> User:
    suffix = uuid.uuid4().hex[:10]
    user = User(
        username=f"analytics_{role}_{suffix}",
        email=f"analytics_{role}_{suffix}@example.org",
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


def _record(db, user: User, source_id: str, *, accept: bool = True):
    record, _created = create_record(
        db,
        learner_id=user.id,
        source_type="flag",
        source_id=source_id,
        competencies=[
            {
                "competency_id": "NET-001",
                "criteria": ["verified"],
                "weight": 1.0,
            }
        ],
        rubric_id="automatic-check",
        rubric_version="1.0",
        confidence="high",
        provenance="analytics-test",
        formula_version="competency-v1",
    )
    if accept:
        auto_accept_record(db, record, note="Automated test acceptance.")
    return record


def _cleanup(db, users: list[User]) -> None:
    user_ids = [user.id for user in users]
    if user_ids:
        db.query(CourseEnrollment).filter(
            CourseEnrollment.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(EvidenceRecord).filter(
            EvidenceRecord.learner_id.in_(user_ids)
        ).delete(synchronize_session=False)
        for user in users:
            db.delete(user)
        db.commit()


def test_overview_counts_accepted_evidence_and_backlog(client, db_session):
    instructor = _user(db_session, "instructor")
    learners = [_user(db_session) for _ in range(5)]
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    course = Course(
        name=f"Analytics Course {suffix}",
        code=f"AN{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"AN-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    try:
        for learner in learners:
            db_session.add(
                CourseEnrollment(course_id=course.id, user_id=learner.id)
            )
        db_session.commit()
        for index, learner in enumerate(learners):
            _record(db_session, learner, f"analytics-{index}")
        _record(db_session, learners[0], "analytics-pending", accept=False)

        login = client.post(
            "/api/auth/login",
            data={"username": instructor.username, "password": PASSWORD},
        )
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        response = client.get("/api/evidence/analytics", headers=headers)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["totals"]["evidence"] == 6
        assert body["totals"]["learners"] == 5
        assert body["totals"]["accepted"] == 5
        assert body["totals"]["awaiting_review"] == 1
        assert body["backlog"]["awaiting_review"] == 1
        assert body["suppressed"] is False
        assert body["sources"] == [{"source_type": "flag", "count": 6}]
        assert body["competencies"][0]["competency_id"] == "NET-001"
        assert body["competencies"][0]["accepted"] == 5
        assert body["strongest_competencies"][0]["learners"] == 5
        assert body["weakest_competencies"][0]["competency_id"] == "NET-001"
        assert body["weakest_competencies"][0]["acceptance_rate"] == 83.3
        assert body["documentation"]["total"] == 0
        assert body["confidence_trend"]["recent_average"] == 3.0
        assert body["program_effectiveness"]["accepted_rate"] == 83.3
        assert body["program_effectiveness"]["evidence_per_learner"] == 1.2
    finally:
        db_session.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course.id
        ).delete(synchronize_session=False)
        db_session.delete(course)
        db_session.commit()
        _cleanup(db_session, learners)
        _cleanup(db_session, [instructor])


def test_overview_suppresses_a_small_cohort(db_session):
    learner = _user(db_session)
    try:
        _record(db_session, learner, "analytics-single")
        body = overview(db_session, learner)
        assert body["totals"]["learners"] == 1
        assert body["suppressed"] is True
        assert body["sources"] == []
        assert body["competencies"] == []
        assert body["strongest_competencies"] == []
        assert body["weakest_competencies"] == []
        assert body["documentation"]["total"] == 0
        assert body["program_effectiveness"]["accepted_rate"] == 100.0
        assert "fewer than 5" in (body["suppression_note"] or "")
    finally:
        _cleanup(db_session, [learner])


def test_analytics_endpoint_requires_a_reviewer_role(client, db_session):
    learner = _user(db_session)
    try:
        login = client.post(
            "/api/auth/login",
            data={"username": learner.username, "password": PASSWORD},
        )
        assert login.status_code == 200
        response = client.get(
            "/api/evidence/analytics",
            headers={"Authorization": f"Bearer {login.json()['access_token']}"},
        )
        assert response.status_code == 403
    finally:
        _cleanup(db_session, [learner])
