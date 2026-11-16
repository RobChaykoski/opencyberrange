"""Database invariants: unique enrollment and append-only consent evidence."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app import database
from app.auth import get_password_hash
from app.models import ConsentAudit, ConsentEvent, Course, CourseEnrollment, User
from app.services import db_invariants

pytestmark = pytest.mark.db


def _user(db):
    suffix = uuid.uuid4().hex[:8]
    row = User(
        username=f"inv_{suffix}",
        email=f"inv_{suffix}@example.org",
        hashed_password=get_password_hash("Invariant#Pass123"),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def test_duplicate_enrollment_is_rejected_by_the_database(db_session):
    db_invariants.apply(database.engine)
    user = _user(db_session)
    instructor = _user(db_session)
    course = Course(
        name="Invariant Course",
        code=f"IV{uuid.uuid4().hex[:5].upper()}",
        semester="Fall",
        invite_code=f"IV-{uuid.uuid4().hex[:8]}",
        instructor_id=instructor.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        is_active=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.add(CourseEnrollment(course_id=course.id, user_id=user.id))
    db_session.commit()
    db_session.add(CourseEnrollment(course_id=course.id, user_id=user.id))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_consent_events_and_audit_proof_cannot_be_deleted(db_session):
    db_invariants.apply(database.engine)
    user = _user(db_session)
    event = ConsentEvent(
        user_id=user.id,
        consent_type="cyber_dna",
        action="grant",
        consent_version=1,
        actor="self",
    )
    audit = ConsentAudit(
        audit_id=str(uuid.uuid4()),
        user_id=user.id,
        subject_hash=uuid.uuid4().hex,
        consent_type="cyber_dna",
        consent_version=1,
        revoked_at=datetime.now(),
    )
    db_session.add_all([event, audit])
    db_session.commit()

    with pytest.raises(DBAPIError):
        db_session.execute(
            text("UPDATE consent_events SET action = 'revoke' WHERE id = :id"),
            {"id": event.id},
        )
    db_session.rollback()

    with pytest.raises(DBAPIError):
        db_session.execute(
            text("DELETE FROM consent_events WHERE id = :id"), {"id": event.id}
        )
    db_session.rollback()

    with pytest.raises(DBAPIError):
        db_session.execute(
            text("DELETE FROM consent_audits WHERE id = :id"), {"id": audit.id}
        )
    db_session.rollback()
