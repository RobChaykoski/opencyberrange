"""Authorization Service: RBAC tables, tenant, consent, break-glass, owner."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.auth import get_password_hash
from app.consent import service as consent_service
from app.models import (
    Course,
    PlatformSetting,
    RbacUserRole,
    SecurityEvent,
    User,
)
from app.security.permissions import (
    BREAK_GLASS_PERMISSIONS,
    ROLE_PERMISSIONS,
    SENSITIVE_PRIVATE_PERMISSIONS,
    validate_catalog,
)
from app.security.policy import authorize
from app.services import authorization, rbac

PASSWORD = "Authz#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db

DEFAULTS = {
    "tenant_isolation_enabled": "true",
    "break_glass_enabled": "false",
    "break_glass_require_mfa": "true",
    "break_glass_require_approval": "false",
    "break_glass_max_minutes": "60",
}


def _set(db, **values):
    for key, value in values.items():
        row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
        if row is None:
            row = PlatformSetting(
                key=key,
                value=str(value),
                category="security",
                description="test",
                is_secret=False,
            )
            db.add(row)
        else:
            row.value = str(value)
    db.commit()


@pytest.fixture(autouse=True)
def _suppression_ledger(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "CONSENT_SUPPRESSION_PATH", str(tmp_path / "consent-suppression.jsonl")
    )


@pytest.fixture(autouse=True)
def _reset_security_settings(db_session):
    _set(db_session, **DEFAULTS)
    yield
    _set(db_session, **DEFAULTS)


def _user(db, role="student", institution="default", mfa=False):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"authz_{role}_{suffix}",
        email=f"authz_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id=institution,
        mfa_enabled=mfa,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _course(db, instructor):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    row = Course(
        name=f"Authz Course {suffix}",
        code=f"AZ{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"AZ-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def test_permission_catalog_is_reviewed_and_private_data_is_not_granted():
    assert validate_catalog() == []
    from app.scripts.review_permissions import issues

    assert issues() == []
    assert not (ROLE_PERMISSIONS["admin"] & SENSITIVE_PRIVATE_PERMISSIONS)
    assert BREAK_GLASS_PERMISSIONS
    # Faculty get competency/achievement views, never private affinity or
    # recommendation signals.
    faculty = (
        ROLE_PERMISSIONS["instructor"]
        | ROLE_PERMISSIONS["teaching_assistant"]
        | ROLE_PERMISSIONS["mentor"]
    )
    assert "career_affinity.view.self" not in faculty
    assert "recommendation.view.self" not in faculty
    assert "dna.view.private" not in faculty


def test_rbac_seed_is_idempotent_and_admin_edits_survive_reseed(db_session):
    first = rbac.seed(db_session)
    second = rbac.seed(db_session)
    assert second["permissions"] == 0
    assert second["roles"] == 0
    assert second["grants"] == 0
    assert first["permissions"] >= 0

    original = rbac.role_permissions(db_session, "student")
    changed = sorted(original - {"lab.view"})
    rbac.set_role_permissions(db_session, None, "student", changed)
    assert "lab.view" not in rbac.role_permissions(db_session, "student")
    rbac.seed(db_session)
    assert "lab.view" not in rbac.role_permissions(db_session, "student")
    rbac.set_role_permissions(db_session, None, "student", sorted(original))


def test_private_permissions_cannot_be_granted_through_the_rbac_editor(db_session):
    rbac.seed(db_session)
    with pytest.raises(ValueError, match="private permissions"):
        rbac.set_role_permissions(
            db_session, None, "instructor", ["dna.view.private"]
        )


def test_extra_roles_are_effective_until_expiry(db_session):
    rbac.seed(db_session)
    student = _user(db_session, "student")
    assert "audit.view" not in rbac.effective_permissions(db_session, student)
    rbac.grant_user_role(
        db_session,
        None,
        student,
        "auditor",
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1),
    )
    assert "audit.view" in rbac.effective_permissions(db_session, student)
    row = (
        db_session.query(RbacUserRole)
        .filter(RbacUserRole.user_id == student.id)
        .one()
    )
    row.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
    db_session.commit()
    assert "audit.view" not in rbac.effective_permissions(db_session, student)


def test_tenant_boundary_denies_cross_institution_access(db_session):
    rbac.seed(db_session)
    instructor_a = _user(db_session, "instructor", institution="tenant-a")
    learner_a = _user(db_session, "student", institution="tenant-a")
    learner_b = _user(db_session, "student", institution="tenant-b")
    admin = _user(db_session, "admin", institution="platform")

    assert authorize(
        db_session,
        instructor_a,
        "student.progress.view",
        resource_user_id=learner_a.id,
        course_id=_course(db_session, instructor_a).id,
    ).allowed
    denied = authorize(
        db_session,
        instructor_a,
        "student.progress.view",
        resource_user_id=learner_b.id,
        course_id=_course(db_session, instructor_a).id,
    )
    assert denied.allowed is False
    assert "Cross-institution" in denied.reason
    # The system administrator is the only cross-tenant role.
    assert authorize(
        db_session,
        admin,
        "student.progress.view",
        resource_user_id=learner_b.id,
    ).allowed


def test_revoked_dna_consent_blocks_even_a_break_glass_attempt(db_session):
    rbac.seed(db_session)
    learner = _user(db_session, "student")
    admin = _user(db_session, "admin", mfa=True)
    from app.consent import service as consent_service

    consent_service.revoke(db_session, learner.id, "cyber_dna", reason="test")
    _set(db_session, break_glass_enabled="true")
    grant = authorization.create_break_glass(
        db_session,
        admin,
        permission="dna.view.private",
        reason="incident investigation",
        scope_user_id=learner.id,
    )
    assert grant.status == "active"
    decision = authorize(
        db_session, admin, "dna.view.private", resource_user_id=learner.id
    )
    assert decision.allowed is False
    assert "consent" in decision.reason.lower()


def test_break_glass_is_disabled_by_default_and_requires_mfa(db_session):
    rbac.seed(db_session)
    learner = _user(db_session, "student")
    admin_no_mfa = _user(db_session, "admin", mfa=False)
    denied = authorize(
        db_session, admin_no_mfa, "dna.view.private", resource_user_id=learner.id
    )
    assert denied.allowed is False

    with pytest.raises(HTTPException) as exc:
        authorization.create_break_glass(
            db_session,
            admin_no_mfa,
            permission="dna.view.private",
            reason="incident investigation",
            scope_user_id=learner.id,
        )
    assert exc.value.status_code == 403

    _set(db_session, break_glass_enabled="true")
    with pytest.raises(HTTPException) as exc:
        authorization.create_break_glass(
            db_session,
            admin_no_mfa,
            permission="dna.view.private",
            reason="incident investigation",
            scope_user_id=learner.id,
        )
    assert "MFA" in exc.value.detail


def test_break_glass_grant_allows_private_access_then_revoke_denies(db_session):
    rbac.seed(db_session)
    learner = _user(db_session, "student")
    admin = _user(db_session, "admin", mfa=True)
    consent_service.grant(db_session, learner.id, "cyber_dna")
    _set(db_session, break_glass_enabled="true")

    grant = authorization.create_break_glass(
        db_session,
        admin,
        permission="dna.view.private",
        reason="incident investigation",
        reference="INC-42",
        scope_user_id=learner.id,
    )
    decision = authorize(
        db_session,
        admin,
        "dna.view.private",
        resource_user_id=learner.id,
    )
    assert decision.allowed is True
    assert decision.source == "break_glass"
    assert decision.break_glass_id == grant.id

    used = (
        db_session.query(SecurityEvent)
        .filter(SecurityEvent.event_type == "break_glass.used")
        .order_by(SecurityEvent.id.desc())
        .first()
    )
    assert used is not None
    assert used.severity == "critical"
    db_session.refresh(grant)
    assert grant.use_count == 1

    authorization.revoke_break_glass(db_session, admin, grant.id, reason="closed")
    again = authorize(
        db_session, admin, "dna.view.private", resource_user_id=learner.id
    )
    assert again.allowed is False


def test_break_glass_approval_flow_keeps_grant_pending_until_approved(db_session):
    rbac.seed(db_session)
    learner = _user(db_session, "student")
    requester = _user(db_session, "privacy_officer", mfa=True)
    approver = _user(db_session, "admin", mfa=True)
    consent_service.grant(db_session, learner.id, "cyber_dna")
    _set(db_session, break_glass_enabled="true", break_glass_require_approval="true")

    grant = authorization.create_break_glass(
        db_session,
        requester,
        permission="dna.view.private",
        reason="regulatory response",
        scope_user_id=learner.id,
    )
    assert grant.status == "pending"
    assert authorize(
        db_session, requester, "dna.view.private", resource_user_id=learner.id
    ).allowed is False

    authorization.approve_break_glass(db_session, approver, grant.id, note="approved")
    assert authorize(
        db_session, requester, "dna.view.private", resource_user_id=learner.id
    ).allowed is True


def test_expired_break_glass_grants_are_closed_with_an_event(db_session):
    from datetime import datetime, timezone

    rbac.seed(db_session)
    learner = _user(db_session, "student")
    admin = _user(db_session, "admin", mfa=True)
    _set(db_session, break_glass_enabled="true")
    grant = authorization.create_break_glass(
        db_session,
        admin,
        permission="dna.view.private",
        reason="expiry test",
        scope_user_id=learner.id,
    )
    grant.expires_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db_session.commit()
    assert authorization.expire_stale_grants(db_session) >= 1
    db_session.refresh(grant)
    assert grant.status == "expired"
    event = (
        db_session.query(SecurityEvent)
        .filter(SecurityEvent.event_type == "break_glass.expired")
        .order_by(SecurityEvent.id.desc())
        .first()
    )
    assert event is not None


def test_owner_helper_returns_404_for_a_foreign_record(db_session):
    owner = _user(db_session, "student")
    outsider = _user(db_session, "student")
    authorization.require_owner(db_session, owner, owner.id, resource="snapshot")
    with pytest.raises(HTTPException) as exc:
        authorization.require_owner(
            db_session, outsider, owner.id, resource="snapshot"
        )
    assert exc.value.status_code == 404


def test_tenant_helper_rejects_a_foreign_tenant(db_session):
    actor = _user(db_session, "institution_admin", institution="tenant-a")
    authorization.require_tenant(actor, "tenant-a")
    with pytest.raises(HTTPException) as exc:
        authorization.require_tenant(actor, "tenant-b")
    assert exc.value.status_code == 404
