"""Exercise tester hardening: flag redaction and identity scoping.

RB-03 (plaintext flag disclosure) and RB-04 (timeout injection) regressions.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import HTTPException

from app.auth import get_password_hash
from app.models import User
from app.routers.exercise_tester import (
    EXEC_TIMEOUT,
    EXEC_TIMEOUT_MAX,
    TESTER_USER_ID,
    _coerce_timeout,
    _ev,
    _redact_flags,
    _resolve_test_identity,
)

PASSWORD = "Tester#Pass123"  # security-delta: allow credential-like assignment


def _make_user(db_session, role: str, institution_id: str):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"tester-{role}-{suffix}",
        email=f"tester-{role}-{suffix}@example.test",
        hashed_password=get_password_hash(PASSWORD),
        role=role,
        institution_id=institution_id,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_step_timeout_is_never_shell_text():
    assert _coerce_timeout("5; rm -rf /") == EXEC_TIMEOUT
    assert _coerce_timeout(10**9) == EXEC_TIMEOUT_MAX
    assert _coerce_timeout(0) == 1
    assert _coerce_timeout("42") == 42


def test_flags_are_redacted_from_events():
    assert _redact_flags("flag=OCR{abc123}") == "flag=OCR{redacted}"
    event = _ev({"type": "line", "message": "Extracted flag: OCR{abc123}"})
    assert "abc123" not in event
    assert "OCR{redacted}" in event


@pytest.mark.db
def test_instructor_cannot_choose_another_user(db_session):
    instructor = _make_user(db_session, "instructor", "acme")
    other = _make_user(db_session, "student", "acme")

    with pytest.raises(HTTPException) as excinfo:
        _resolve_test_identity(db_session, instructor, other.id)
    assert excinfo.value.status_code == 403


@pytest.mark.db
def test_instructor_cannot_choose_a_user_in_another_institution(db_session):
    instructor = _make_user(db_session, "instructor", "acme")
    outsider = _make_user(db_session, "student", "other-institution")

    with pytest.raises(HTTPException) as excinfo:
        _resolve_test_identity(db_session, instructor, outsider.id)
    assert excinfo.value.status_code == 403


@pytest.mark.db
def test_default_identity_falls_back_to_caller(db_session):
    instructor = _make_user(db_session, "instructor", "acme")

    # A missing harness account (or one owned by another institution) must not
    # borrow an arbitrary administrator's session.
    resolved = _resolve_test_identity(db_session, instructor, None)
    assert resolved.id == instructor.id


@pytest.mark.db
def test_platform_admin_may_test_as_another_user(db_session):
    admin = _make_user(db_session, "admin", "default")
    student = _make_user(db_session, "student", "default")

    resolved = _resolve_test_identity(db_session, admin, student.id)
    assert resolved.id == student.id


@pytest.mark.db
def test_harness_account_is_preferred_when_available(db_session):
    harness = db_session.query(User).filter(User.id == TESTER_USER_ID).first()
    if harness is None:
        pytest.skip("install has no dedicated tester user")

    caller = _make_user(db_session, "admin", harness.institution_id)
    resolved = _resolve_test_identity(db_session, caller, None)
    assert resolved.id == harness.id
