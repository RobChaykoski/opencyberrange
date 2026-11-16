"""Tenant derivation and forced RLS on learner-data tables."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import text

from app import database
from app.auth import get_password_hash
from app.models import Course, CourseEnrollment, ReviewRequest, User, UserAccommodation
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

@pytest.mark.skipif(
    database.engine.dialect.name != "postgresql",
    reason="PostgreSQL row-level security",
)
def test_every_enforced_table_has_institution_column_and_forced_rls(db_session):
    tenant_rls.apply(database.engine)
    expected = set(tenant_rls.TENANT_TABLES)

    columns = {
        row[0]
        for row in db_session.execute(
            text(
                "SELECT table_name FROM information_schema.columns "
                "WHERE table_schema = 'public' AND column_name = 'institution_id'"
            )
        ).all()
    }
    assert expected <= columns

    rows = db_session.execute(
        text(
            "SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity "
            "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = 'public'"
        )
    ).all()
    state = {name: (enabled, forced) for name, enabled, forced in rows}
    for table in expected:
        assert state.get(table) == (True, True), f"{table} is not forced RLS"

    policies: dict[str, set[str]] = {}
    for table, policy in db_session.execute(
        text("SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public'")
    ).all():
        policies.setdefault(table, set()).add(policy)
    for table in expected:
        required = {f"{table}_tenant_{s}" for s in ("select", "insert", "update", "delete")}
        assert required <= policies.get(table, set()), table


@pytest.mark.skipif(
    database.engine.dialect.name != "postgresql",
    reason="PostgreSQL row-level security",
)
def test_new_learner_tables_are_tenant_isolated(db_session):
    tenant_rls.apply(database.engine)
    suffix = uuid.uuid4().hex[:8]
    tenant_a = f"tenant-a-{suffix}"
    tenant_b = f"tenant-b-{suffix}"
    learner_a = _user(db_session, tenant_a)
    learner_b = _user(db_session, tenant_b)

    accommodation_a = UserAccommodation(user_id=learner_a.id, time_multiplier=1.5)
    accommodation_b = UserAccommodation(user_id=learner_b.id, time_multiplier=2.0)
    review_a = ReviewRequest(
        user_id=learner_a.id, reason="tenant a review", status="pending"
    )
    review_b = ReviewRequest(
        user_id=learner_b.id, reason="tenant b review", status="pending"
    )
    db_session.add_all([accommodation_a, accommodation_b, review_a, review_b])
    db_session.commit()
    for row in (accommodation_a, accommodation_b, review_a, review_b):
        db_session.refresh(row)

    derived = {
        (table, row_id): institution
        for table, row_id, institution in db_session.execute(
            text(
                "SELECT 'user_accommodations', id, institution_id FROM user_accommodations "
                "UNION ALL "
                "SELECT 'review_requests', id, institution_id FROM review_requests"
            )
        ).all()
    }
    assert derived[("user_accommodations", accommodation_a.id)] == tenant_a
    assert derived[("user_accommodations", accommodation_b.id)] == tenant_b
    assert derived[("review_requests", review_a.id)] == tenant_a
    assert derived[("review_requests", review_b.id)] == tenant_b

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
        conn.execute(
            text(
                "GRANT SELECT, INSERT, UPDATE, DELETE ON "
                "user_accommodations, review_requests TO ocr_tenant_probe"
            )
        )
        conn.execute(text("SET LOCAL ROLE ocr_tenant_probe"))
        conn.execute(text("SET LOCAL ocr.system_admin = 'false'"))

        conn.execute(text(f"SET LOCAL ocr.institution_id = '{tenant_a}'"))
        visible_a = {
            row[0]
            for row in conn.execute(text("SELECT id FROM user_accommodations")).all()
        }
        assert accommodation_a.id in visible_a
        assert accommodation_b.id not in visible_a
        reviews_a = {
            row[0]
            for row in conn.execute(text("SELECT id FROM review_requests")).all()
        }
        assert review_a.id in reviews_a
        assert review_b.id not in reviews_a

        conn.execute(text(f"SET LOCAL ocr.institution_id = '{tenant_b}'"))
        visible_b = {
            row[0]
            for row in conn.execute(text("SELECT id FROM user_accommodations")).all()
        }
        assert accommodation_b.id in visible_b
        assert accommodation_a.id not in visible_b
        reviews_b = {
            row[0]
            for row in conn.execute(text("SELECT id FROM review_requests")).all()
        }
        assert review_b.id in reviews_b
        assert review_a.id not in reviews_b

        deleted = conn.execute(
            text("DELETE FROM user_accommodations WHERE id = :id"),
            {"id": accommodation_a.id},
        )
        assert deleted.rowcount == 0
        trans.commit()
