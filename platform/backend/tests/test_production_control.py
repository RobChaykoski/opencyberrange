"""Production change control: tickets, encryption, revert, and one-way cutover."""

from __future__ import annotations

import json
import uuid

import pytest

from app.auth import get_password_hash
from app.crypto import is_encrypted
from app.models import (
    ProductionCutover,
    SettingsChangeRequest,
    User,
)
from app.services import production_control, settings_service

PASSWORD = "Prod#Control#2026"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _admin(db):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"prod_admin_{suffix}",
        email=f"prod_admin_{suffix}@acme.example",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="admin",
        is_admin=True,
        institution_id="default",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _sample_user(db):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"pytest_sample_{suffix}",
        email=f"pytest_sample_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
        institution_id="default",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _reset(db):
    settings_service.set_setting(db, "deployment_mode", "development")
    settings_service.set_setting(db, "data_collection_mode", "sample")
    settings_service.set_setting(db, "settings_change_ticket_mode", "optional")
    db.query(ProductionCutover).delete()
    db.query(SettingsChangeRequest).delete()
    db.commit()


def test_change_set_encrypts_ticket_and_reason_and_redacts_secrets(db_session):
    _reset(db_session)
    settings_service.seed_defaults(db_session)
    admin = _admin(db_session)
    try:
        change = production_control.apply_change_set(
            db_session,
            admin,
            {
                "analytics_min_cohort_size": "7",
                "mail_password": "SuperSecret#123",
            },
            ticket_number="CHG-2026-0042",
            reason="Approved privacy review for cohort suppression.",
        )
        assert change["ticket_number"] == "CHG-2026-0042"
        assert change["secret_keys"] == ["mail_password"]
        assert change["before"]["mail_password"] == "[secret]"
        assert change["after"]["mail_password"] == "[secret]"

        row = db_session.query(SettingsChangeRequest).filter_by(id=change["id"]).one()
        assert is_encrypted(row.ticket_number)
        assert is_encrypted(row.reason)
        assert "CHG-2026-0042" not in row.ticket_number
        assert "SuperSecret#123" not in row.after_values
        assert "SuperSecret#123" not in row.before_values
        assert json.loads(row.after_values)["mail_password"] == "[secret]"
    finally:
        _reset(db_session)


def test_change_set_reverts_when_values_have_not_drifted(db_session):
    _reset(db_session)
    settings_service.seed_defaults(db_session)
    admin = _admin(db_session)
    try:
        change = production_control.apply_change_set(
            db_session,
            admin,
            {"analytics_min_cohort_size": "9"},
            ticket_number="CHG-REVERT-1",
            reason="Temporary cohort threshold change.",
        )
        assert settings_service.get_setting_fresh(
            db_session, "analytics_min_cohort_size"
        ) == "9"
        reverted = production_control.revert_change_set(
            db_session,
            admin,
            change["id"],
            reason="Restore the reviewed baseline.",
        )
        assert reverted["status"] == "reverted"
        assert settings_service.get_setting_fresh(
            db_session, "analytics_min_cohort_size"
        ) != "9"
    finally:
        _reset(db_session)


def test_change_set_revert_detects_drift(db_session):
    _reset(db_session)
    settings_service.seed_defaults(db_session)
    admin = _admin(db_session)
    try:
        change = production_control.apply_change_set(
            db_session,
            admin,
            {"analytics_min_cohort_size": "8"},
            ticket_number="CHG-DRIFT-1",
            reason="Initial threshold change.",
        )
        settings_service.set_setting(db_session, "analytics_min_cohort_size", "11")
        with pytest.raises(production_control.ProductionControlError) as exc:
            production_control.revert_change_set(
                db_session,
                admin,
                change["id"],
                reason="Attempted revert after drift.",
            )
        assert exc.value.code == "drifted"
    finally:
        _reset(db_session)


def test_production_forces_a_ticket_even_when_mode_is_optional(db_session):
    _reset(db_session)
    settings_service.seed_defaults(db_session)
    admin = _admin(db_session)
    try:
        settings_service.set_setting(db_session, "deployment_mode", "production")
        settings_service.set_setting(
            db_session, "settings_change_ticket_mode", "optional"
        )
        with pytest.raises(production_control.ProductionControlError) as exc:
            production_control.apply_change_set(
                db_session,
                admin,
                {"analytics_min_cohort_size": "6"},
                ticket_number=None,
                reason="Production change without a ticket.",
            )
        assert exc.value.code == "ticket_required"

        change = production_control.apply_change_set(
            db_session,
            admin,
            {"analytics_min_cohort_size": "6"},
            ticket_number="CHG-PROD-OPTIONAL-1",
            reason="Production change with a reviewed ticket.",
        )
        assert change["ticket_number"] == "CHG-PROD-OPTIONAL-1"
    finally:
        _reset(db_session)


def test_required_ticket_and_protected_phase_keys(db_session):
    _reset(db_session)
    settings_service.seed_defaults(db_session)
    admin = _admin(db_session)
    try:
        settings_service.set_setting(
            db_session, "settings_change_ticket_mode", "required"
        )
        with pytest.raises(production_control.ProductionControlError) as exc:
            production_control.apply_change_set(
                db_session,
                admin,
                {"analytics_min_cohort_size": "6"},
                ticket_number=None,
                reason="No ticket supplied.",
            )
        assert exc.value.code == "ticket_required"

        with pytest.raises(production_control.ProductionControlError) as exc:
            production_control.apply_change_set(
                db_session,
                admin,
                {"deployment_mode": "production"},
                ticket_number="CHG-PHASE-1",
                reason="Attempt to skip the cutover.",
            )
        assert exc.value.code == "phase_locked"
    finally:
        _reset(db_session)


def test_cutover_rejects_wrong_password_before_any_change(db_session):
    _reset(db_session)
    settings_service.seed_defaults(db_session)
    admin = _admin(db_session)
    try:
        with pytest.raises(production_control.ProductionControlError) as exc:
            production_control.cutover_to_production(
                db_session,
                admin,
                ticket_number="CHG-BAD-PASS",
                password="Wrong#Password9",  # security-delta: allow credential-like assignment
                confirmation="GO PRODUCTION",
                acknowledge_data_loss=True,
                acknowledge_one_way=True,
                reason="Verify the cutover password gate.",
            )
        assert exc.value.code == "password_invalid"
        assert production_control.deployment_mode(db_session) == "development"
        assert db_session.query(ProductionCutover).count() == 0
    finally:
        _reset(db_session)


def test_one_way_cutover_clears_sample_accounts_and_encrypts_evidence(
    db_session, monkeypatch
):
    _reset(db_session)
    settings_service.seed_defaults(db_session)
    admin = _admin(db_session)
    sample = _sample_user(db_session)
    monkeypatch.setattr(
        production_control,
        "_sample_users",
        lambda db: [sample],
    )
    try:
        result = production_control.cutover_to_production(
            db_session,
            admin,
            ticket_number="CHG-CUTOVER-1",
            password=PASSWORD,
            confirmation="GO PRODUCTION",
            acknowledge_data_loss=True,
            acknowledge_one_way=True,
            reason="Approved production readiness review.",
        )
        assert result["production_locked"] is True
        assert result["summary"]["users_cleared"] == 1
        assert production_control.deployment_mode(db_session) == "production"
        assert production_control.data_collection_mode(db_session) == "production"
        assert production_control.ticket_mode(db_session) == "required"
        assert db_session.query(User).filter(User.id == sample.id).first() is None

        row = db_session.query(ProductionCutover).one()
        assert is_encrypted(row.ticket_number)
        assert "CHG-CUTOVER-1" not in row.ticket_number
        assert "pytest_sample" not in row.sample_data_summary
        assert result["evidence_hash"] == row.evidence_hash

        with pytest.raises(production_control.ProductionControlError) as exc:
            production_control.cutover_to_production(
                db_session,
                admin,
                ticket_number="CHG-CUTOVER-2",
                password=PASSWORD,
                confirmation="GO PRODUCTION",
                acknowledge_data_loss=True,
                acknowledge_one_way=True,
                reason="Attempt a second cutover.",
            )
        assert exc.value.code == "already_production"
    finally:
        _reset(db_session)
