"""Tenant derivation and forced RLS on learner-data tables."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import text

from app import database
from app.auth import get_password_hash
from app.models import Course, CourseEnrollment, User
from app.services import tenant_rls

PASSWORD = "Tenant#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, institution):
    suffix = uuid.uuid4().hex[:8]
    row = User(
        username=f"tenant_{suffix}",
        email=f"tenant_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
        institution_id=institution,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _course(db, instructor, institution):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    row = Course(
        name=f"Tenant Course {suffix}",
        code=f"TN{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"TN-{suffix}",
        instructor_id=instructor.id,
        institution_id=institution,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@pytest.mark.skipif(
    database.engine.dialect.name != "postgresql",
    reason="PostgreSQL row-level security",
)
def test_tenant_columns_are_derived_and_rls_hides_other_institutions(db_session):
    tenant_rls.apply(database.engine)

    instructor_a = _user(db_session, "tenant-a")
    instructor_b = _user(db_session, "tenant-b")
    learner_a = _user(db_session, "tenant-a")
    learner_b = _user(db_session, "tenant-b")
    course_a = _course(db_session, instructor_a, "tenant-a")
    course_b = _course(db_session, instructor_b, "tenant-b")
    enrollment_a = CourseEnrollment(course_id=course_a.id, user_id=learner_a.id)
    enrollment_b = CourseEnrollment(course_id=course_b.id, user_id=learner_b.id)
    db_session.add_all([enrollment_a, enrollment_b])
    db_session.commit()
    db_session.refresh(enrollment_a)
    db_session.refresh(enrollment_b)

    # The trigger derives the tenant from the course, not from the caller.
    assert enrollment_a.institution_id == "tenant-a"
    assert enrollment_b.institution_id == "tenant-b"

    with database.engine.connect() as conn:
        trans = conn.begin()
        conn.execute(
            text(
                "DO $$ BEGIN "
                "IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ocr_tenant_probe') "
                "THEN CREATE ROLE ocr_tenant_probe NOLOGIN; END IF; "
                "END $$"
            )
        )
        conn.execute(text("GRANT USAGE ON SCHEMA public TO ocr_tenant_probe"))
        conn.execute(
            text(
                "GRANT SELECT, INSERT, UPDATE, DELETE ON "
                + ", ".join(tenant_rls.TENANT_TABLES)
                + " TO ocr_tenant_probe"
            )
        )
        conn.execute(text("SET LOCAL ROLE ocr_tenant_probe"))
        conn.execute(text("SET LOCAL ocr.institution_id = 'tenant-a'"))
        conn.execute(text("SET LOCAL ocr.system_admin = 'false'"))
        visible = [
            row[0]
            for row in conn.execute(
                text("SELECT id FROM course_enrollments ORDER BY id")
            ).all()
        ]
        assert enrollment_a.id in visible
        assert enrollment_b.id not in visible

        updated = conn.execute(
            text(
                "UPDATE course_enrollments SET seat_number = 99 "
                "WHERE id = :id"
            ),
            {"id": enrollment_b.id},
        )
        assert updated.rowcount == 0

        conn.execute(text("SET LOCAL ocr.system_admin = 'true'"))
        all_visible = {
            row[0]
            for row in conn.execute(text("SELECT id FROM course_enrollments")).all()
        }
        assert {enrollment_a.id, enrollment_b.id}.issubset(all_visible)
        trans.commit()
