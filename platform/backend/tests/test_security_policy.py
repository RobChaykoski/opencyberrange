"""Policy checks for self, scoped, shared, and read-only access."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import Course, User
from app.security.permissions import (
    PERMISSION_CATALOG,
    ROLE_PERMISSIONS,
    SENSITIVE_PRIVATE_PERMISSIONS,
)
from app.security.policy import authorize

# Test-only login credential; security-delta: allow credential-like assignment
PASSWORD = "Policy#Pass123"
pytestmark = pytest.mark.db


def _user(db_session, role):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"policy_{role}_{suffix}",
        email=f"policy_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _course(db_session, instructor):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    course = Course(
        name=f"Policy Course {suffix}",
        code=f"PO{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"PO-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


def test_catalog_and_role_grants_are_consistent():
    for role, permissions in ROLE_PERMISSIONS.items():
        unknown = permissions - set(PERMISSION_CATALOG)
        assert not unknown, (role, unknown)
    assert not (ROLE_PERMISSIONS["admin"] & SENSITIVE_PRIVATE_PERMISSIONS)


def test_self_permissions_do_not_cross_learners(db_session):
    from app.consent import service as consent_service

    student = _user(db_session, "student")
    other = _user(db_session, "student")
    consent_service.grant(db_session, student.id, "cyber_dna")

    own = authorize(
        db_session,
        student,
        "dna.view.self",
        resource_user_id=student.id,
    )
    assert own.allowed is True

    cross = authorize(
        db_session,
        student,
        "dna.view.self",
        resource_user_id=other.id,
    )
    assert cross.allowed is False


def test_unknown_permission_and_unprovisioned_role_deny(db_session):
    student = _user(db_session, "student")
    assert authorize(db_session, student, "made.up.permission").allowed is False

    unknown_role = _user(db_session, "guest")
    assert (
        authorize(db_session, unknown_role, "profile.view.self", resource_user_id=unknown_role.id).allowed
        is False
    )


def test_instructor_scope_requires_the_assigned_course(db_session):
    owner = _user(db_session, "instructor")
    outsider = _user(db_session, "instructor")
    course = _course(db_session, owner)

    allowed = authorize(
        db_session,
        owner,
        "student.progress.view",
        course_id=course.id,
    )
    assert allowed.allowed is True

    denied = authorize(
        db_session,
        outsider,
        "student.progress.view",
        course_id=course.id,
    )
    assert denied.allowed is False
    assert "not assigned" in denied.reason

    unscoped = authorize(db_session, owner, "student.progress.view")
    assert unscoped.allowed is False

    missing = authorize(
        db_session, owner, "student.progress.view", course_id=99999999
    )
    assert missing.allowed is False


def test_auditor_is_read_only(db_session):
    auditor = _user(db_session, "auditor")
    assert (
        authorize(db_session, auditor, "privacy.audit.view").allowed is True
    )
    denied = authorize(db_session, auditor, "privacy.revocation.execute")
    assert denied.allowed is False
    assert "read-only" in denied.reason


def test_shared_permissions_require_an_explicit_share(db_session):
    employer = _user(db_session, "employer")
    assert (
        authorize(db_session, employer, "portfolio.view.shared", shared=True).allowed
        is True
    )
    assert (
        authorize(db_session, employer, "portfolio.view.shared").allowed is False
    )
    assert (
        authorize(db_session, employer, "consent.manage.self").allowed is False
    )


def test_admin_cannot_read_sensitive_private_data_by_default(db_session):
    admin = _user(db_session, "admin")
    learner = _user(db_session, "student")
    assert (
        authorize(
            db_session,
            admin,
            "coach.transcript.view",
            resource_user_id=learner.id,
        ).allowed
        is False
    )
    assert (
        authorize(
            db_session,
            admin,
            "coach.transcript.view",
            resource_user_id=admin.id,
        ).allowed
        is False
    )


def test_privacy_officer_can_execute_revocations(db_session):
    officer = _user(db_session, "privacy_officer")
    assert (
        authorize(db_session, officer, "privacy.revocation.execute").allowed
        is True
    )
    assert authorize(db_session, officer, "deletion.approve").allowed is True
    assert authorize(db_session, officer, "platform.admin").allowed is False
