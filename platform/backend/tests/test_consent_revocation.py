"""Consent revocation: gates, atomic purges, suppression, restore protection."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.consent import hooks, service, suppression
from app.consent.models import (
    ConsentAudit,
    ConsentJob,
    ConsentRevocation,
    ConsentState,
)
from app.cyber_dna.models import DnaEvidenceRecord, DnaSnapshot
from app.cyber_dna.service import build_behavior, ingest_activity, record_snapshot
from app.models import (
    Achievement,
    LabCompletion,
    LearnerSnapshot,
    PlatformSetting,
    User,
)
from app.services.dna_events import backfill_completions, emit_completion_event

# Test-only login credential; security-delta: allow credential-like assignment
PASSWORD = "Consent#Pass123"
pytestmark = pytest.mark.db


@pytest.fixture(autouse=True)
def _suppression_ledger(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "CONSENT_SUPPRESSION_PATH", str(tmp_path / "consent-suppression.jsonl")
    )


def _set_feature(db_session, key: str, value: str) -> None:
    row = (
        db_session.query(PlatformSetting)
        .filter(PlatformSetting.key == key)
        .first()
    )
    if row is None:
        row = PlatformSetting(
            key=key,
            value=value,
            category="features",
            description="consent test",
            is_secret=False,
        )
        db_session.add(row)
    else:
        row.value = value
    db_session.commit()


def _make_user(db_session, role="admin"):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"consent_{role}_{suffix}",
        email=f"consent_{role}_{suffix}@example.org",
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


def _headers(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _event(learner_id, activity_id="lab-consent"):
    from app.cyber_dna.events import ActivityCompleted
    from datetime import datetime, timezone

    return ActivityCompleted(
        event_id=f"event:{uuid.uuid4().hex}",
        learner_id=learner_id,
        activity_id=activity_id,
        activity_category="network",
        competency_weights={"NET-001": 1.0},
        difficulty="beginner",
        occurred_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )


def _seed_derived(db_session, user_id: int, lab_id: int) -> None:
    ingest_activity(db_session, _event(user_id))
    record_snapshot(
        db_session, user_id, "behavior_profile", build_behavior(db_session, user_id)
    )
    db_session.add(
        LearnerSnapshot(
            user_id=user_id,
            kind="portfolio",
            schema_version="2026.1",
            formula_version="test",
            weights=json.dumps({"test": 1}),
            payload=json.dumps({"test": True}),
            content_sha256=hashlib.sha256(str(user_id).encode()).hexdigest(),
        )
    )
    db_session.add(
        Achievement(
            user_id=user_id,
            lab_id=lab_id,
            achievement_type="lab_complete",
        )
    )
    if (
        db_session.query(LabCompletion)
        .filter(
            LabCompletion.user_id == user_id,
            LabCompletion.lab_id == lab_id,
        )
        .first()
        is None
    ):
        db_session.add(
            LabCompletion(
                user_id=user_id,
                lab_id=lab_id,
                attempts=1,
                hints_used=0,
                time_spent_minutes=10,
                flag_submitted="TESTFLAG",
            )
        )
    db_session.commit()


def _counts(db_session, user_id: int) -> dict:
    db_session.expire_all()
    return {
        "evidence": db_session.query(DnaEvidenceRecord)
        .filter(DnaEvidenceRecord.learner_id == user_id)
        .count(),
        "snapshots": db_session.query(DnaSnapshot)
        .filter(DnaSnapshot.learner_id == user_id)
        .count(),
        "learner_snapshots": db_session.query(LearnerSnapshot)
        .filter(LearnerSnapshot.user_id == user_id)
        .count(),
        "completions": db_session.query(LabCompletion)
        .filter(LabCompletion.user_id == user_id)
        .count(),
        "achievements": db_session.query(Achievement)
        .filter(Achievement.user_id == user_id)
        .count(),
    }


def test_revoke_blocks_immediately_then_purges_atomically(
    client, db_session, auth_headers, test_user, test_lab
):
    _set_feature(db_session, "cyber_dna_v3_enabled", "true")
    _seed_derived(db_session, test_user.id, test_lab.id)
    assert _counts(db_session, test_user.id)["evidence"] > 0

    assert client.get("/api/dna/v3/evidence", headers=auth_headers).status_code == 200

    response = client.post(
        "/api/consent/cyber_dna/revoke",
        json={"reason": "learner request"},
        headers=auth_headers,
    )
    assert response.status_code == 202, response.text
    body = response.json()
    assert body["state"]["granted"] is False
    assert body["state"]["revocation_in_progress"] is True
    assert body["revocation"]["status"] == "pending"
    assert body["revocation"]["suppression_recorded"] is True

    blocked = client.get("/api/dna/v3/evidence", headers=auth_headers)
    assert blocked.status_code == 403
    assert blocked.headers["x-consent-status"] in {"revoked", "revocation_in_progress"}

    # The exercise-side adapter stops processing before the purge runs.
    completion = (
        db_session.query(LabCompletion)
        .filter(LabCompletion.user_id == test_user.id)
        .first()
    )
    from app.models import Lab

    lab = db_session.query(Lab).filter(Lab.id == completion.lab_id).first()
    assert emit_completion_event(db_session, test_user.id, completion, lab) == 0

    # Destructive work is queued, not done inline.
    before = _counts(db_session, test_user.id)
    assert before["evidence"] > 0
    assert before["learner_snapshots"] > 0

    result = service.run_due_jobs(db_session)
    assert result["purges"] >= 1

    after = _counts(db_session, test_user.id)
    assert after["evidence"] == 0
    assert after["snapshots"] == 0
    assert after["learner_snapshots"] == 0

    # The backfill adapter applies the same consent gate. The surviving
    # completion must not recreate evidence after the purge.
    backfill = backfill_completions(db_session, user_id=test_user.id)
    assert backfill["evidence_rows"] == 0
    assert backfill["blocked"] >= 1
    assert _counts(db_session, test_user.id)["evidence"] == 0
    # Educational records survive.
    assert after["completions"] >= 1
    assert after["achievements"] >= 1

    db_session.expire_all()
    revocation = (
        db_session.query(ConsentRevocation)
        .filter(ConsentRevocation.user_id == test_user.id)
        .one()
    )
    assert revocation.status == "complete"
    assert revocation.verified_at is not None
    audit = (
        db_session.query(ConsentAudit)
        .filter(ConsentAudit.audit_id == revocation.audit_id)
        .one()
    )
    assert audit.verified is True
    assert "cyber_dna:evidence" in json.loads(audit.jobs_completed)
    slots = json.loads(audit.verification_slots)
    assert "immediate" in slots
    assert {"24h", "7d"}.issubset(
        {
            job.slot
            for job in db_session.query(ConsentJob)
            .filter(ConsentJob.revocation_id == revocation.id)
            .all()
        }
    )


def test_verification_repeats_at_24_hours_and_7_days(
    client, db_session, auth_headers, test_user, test_lab
):
    _set_feature(db_session, "cyber_dna_v3_enabled", "true")
    _seed_derived(db_session, test_user.id, test_lab.id)
    response = client.post(
        "/api/consent/cyber_dna/revoke", headers=auth_headers
    )
    assert response.status_code == 202, response.text
    revocation_id = response.json()["revocation"]["id"]
    service.run_due_jobs(db_session)

    db_session.expire_all()
    revocation = (
        db_session.query(ConsentRevocation)
        .filter(ConsentRevocation.id == revocation_id)
        .one()
    )
    assert revocation.status == "complete"

    future = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=25)
    service.run_due_jobs(db_session, now=future)
    db_session.expire_all()
    audit = (
        db_session.query(ConsentAudit)
        .filter(ConsentAudit.audit_id == revocation.audit_id)
        .one()
    )
    assert "24h" in json.loads(audit.verification_slots)

    week = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=8)
    service.run_due_jobs(db_session, now=week)
    db_session.expire_all()
    audit = (
        db_session.query(ConsentAudit)
        .filter(ConsentAudit.audit_id == revocation.audit_id)
        .one()
    )
    assert "7d" in json.loads(audit.verification_slots)


def test_mid_purge_failure_rolls_back_every_target(
    client, db_session, auth_headers, test_user, test_lab, monkeypatch
):
    _set_feature(db_session, "cyber_dna_v3_enabled", "true")
    _seed_derived(db_session, test_user.id, test_lab.id)
    response = client.post(
        "/api/consent/cyber_dna/revoke", headers=auth_headers
    )
    revocation_id = response.json()["revocation"]["id"]

    original = hooks.PURGE_HOOKS[("reports", "learner_snapshots")]

    def explode(db, user_id):
        raise RuntimeError("simulated database failure")

    monkeypatch.setitem(
        hooks.PURGE_HOOKS,
        ("reports", "learner_snapshots"),
        (explode, original[1]),
    )
    service.run_due_jobs(db_session)

    # The whole purge transaction rolled back: DNA evidence is still present.
    after_failure = _counts(db_session, test_user.id)
    assert after_failure["evidence"] > 0
    assert after_failure["learner_snapshots"] > 0
    db_session.expire_all()
    failed = (
        db_session.query(ConsentRevocation)
        .filter(ConsentRevocation.id == revocation_id)
        .one()
    )
    assert failed.status == "failed"

    monkeypatch.setitem(
        hooks.PURGE_HOOKS, ("reports", "learner_snapshots"), original
    )
    service.run_due_jobs(
        db_session,
        now=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=5),
        limit=50,
    )
    after_retry = _counts(db_session, test_user.id)
    assert after_retry["evidence"] == 0
    assert after_retry["learner_snapshots"] == 0


def test_suppression_ledger_failure_aborts_the_transaction(
    db_session, test_user, test_lab, monkeypatch
):
    _seed_derived(db_session, test_user.id, test_lab.id)

    def unavailable(*args, **kwargs):
        raise RuntimeError("ledger unavailable")

    monkeypatch.setattr(service.suppression, "append_suppression", unavailable)
    with pytest.raises(RuntimeError):
        service.revoke(db_session, test_user.id, "cyber_dna")

    assert (
        db_session.query(ConsentRevocation)
        .filter(ConsentRevocation.user_id == test_user.id)
        .count()
        == 0
    )
    assert _counts(db_session, test_user.id)["evidence"] > 0


def test_suppression_blocks_replay_and_restore_sweep(
    client, db_session, auth_headers, test_user, test_lab
):
    _set_feature(db_session, "cyber_dna_v3_enabled", "true")
    _seed_derived(db_session, test_user.id, test_lab.id)
    response = client.post(
        "/api/consent/cyber_dna/revoke", headers=auth_headers
    )
    assert response.status_code == 202, response.text
    service.run_due_jobs(db_session)

    # At-least-once event replay is ignored by the exercise adapter.
    completion = (
        db_session.query(LabCompletion)
        .filter(LabCompletion.user_id == test_user.id)
        .first()
    )
    from app.models import Lab

    lab = db_session.query(Lab).filter(Lab.id == completion.lab_id).first()
    assert emit_completion_event(db_session, test_user.id, completion, lab) == 0

    # Simulate a restore that brings back derived rows and a granted state.
    ingest_activity(db_session, _event(test_user.id, "restored-lab"))
    db_session.add(
        LearnerSnapshot(
            user_id=test_user.id,
            kind="portfolio",
            schema_version="2026.1",
            formula_version="test",
            weights="{}",
            payload="{}",
            content_sha256=hashlib.sha256(b"restored").hexdigest(),
        )
    )
    state = (
        db_session.query(ConsentState)
        .filter(
            ConsentState.user_id == test_user.id,
            ConsentState.consent_type == "cyber_dna",
        )
        .one()
    )
    state.granted = True
    db_session.commit()
    assert _counts(db_session, test_user.id)["evidence"] > 0

    sweep = service.enforce_suppressions(db_session)
    assert sweep["purged"] >= 1, sweep
    after = _counts(db_session, test_user.id)
    assert after["evidence"] == 0
    assert after["learner_snapshots"] == 0
    db_session.expire_all()
    state = (
        db_session.query(ConsentState)
        .filter(
            ConsentState.user_id == test_user.id,
            ConsentState.consent_type == "cyber_dna",
        )
        .one()
    )
    assert state.granted is False
    assert suppression.is_suppressed(test_user.id, "cyber_dna")


def test_regrant_allows_new_activity_without_restoring_old_data(
    client, db_session, auth_headers, test_user, test_lab
):
    _set_feature(db_session, "cyber_dna_v3_enabled", "true")
    _seed_derived(db_session, test_user.id, test_lab.id)
    client.post("/api/consent/cyber_dna/revoke", headers=auth_headers)
    service.run_due_jobs(db_session)
    assert _counts(db_session, test_user.id)["evidence"] == 0

    granted = client.post(
        "/api/consent/cyber_dna/grant", headers=auth_headers
    )
    assert granted.status_code == 200, granted.text
    assert granted.json()["state"]["granted"] is True
    assert not suppression.is_suppressed(test_user.id, "cyber_dna")

    completion = (
        db_session.query(LabCompletion)
        .filter(LabCompletion.user_id == test_user.id)
        .first()
    )
    from app.models import Lab

    lab = db_session.query(Lab).filter(Lab.id == completion.lab_id).first()
    lab.primary_competency = "network_systems"
    db_session.commit()
    assert emit_completion_event(db_session, test_user.id, completion, lab) > 0
    after = _counts(db_session, test_user.id)
    assert after["evidence"] >= 1
    assert after["snapshots"] == 0


def test_optional_profiling_defaults_are_opt_in(db_session, test_user):
    for consent_type in ("cyber_dna", "cyber_gps", "portfolio"):
        state = service.state_for(db_session, test_user.id, consent_type)
        assert state["default_granted"] is False
        assert state["granted"] is False
        assert service.blocked_status(db_session, test_user.id, consent_type) == "revoked"


def test_gps_and_portfolio_gates_preserve_course_progress(
    client, db_session, auth_headers, test_user, test_lab
):
    _set_feature(db_session, "advanced_dna_insights_enabled", "true")
    _seed_derived(db_session, test_user.id, test_lab.id)

    assert client.post("/api/profile/gps", headers=auth_headers).status_code == 200
    assert client.get("/api/profile/portfolio", headers=auth_headers).status_code == 200

    gps = client.post("/api/consent/cyber_gps/revoke", headers=auth_headers)
    assert gps.status_code == 202, gps.text
    assert client.post("/api/profile/gps", headers=auth_headers).status_code == 403

    portfolio = client.post(
        "/api/consent/portfolio/revoke", headers=auth_headers
    )
    assert portfolio.status_code == 202, portfolio.text
    assert client.get("/api/profile/portfolio", headers=auth_headers).status_code == 403

    service.run_due_jobs(db_session)
    after = _counts(db_session, test_user.id)
    assert after["completions"] >= 1
    assert after["learner_snapshots"] == 0

    dashboard = client.get("/api/consent/", headers=auth_headers)
    assert dashboard.status_code == 200, dashboard.text
    body = dashboard.json()
    assert body["consents"]["cyber_gps"]["granted"] is False
    assert body["remaining_records"]["completed_exercises"] >= 1


def test_revoke_is_idempotent_and_version_conflicts_are_rejected(
    client, db_session, auth_headers, test_user
):
    first = client.post("/api/consent/cyber_dna/revoke", headers=auth_headers)
    assert first.status_code == 202, first.text
    first_id = first.json()["revocation"]["id"]

    second = client.post("/api/consent/cyber_dna/revoke", headers=auth_headers)
    assert second.status_code == 202, second.text
    assert second.json()["revocation"]["id"] == first_id
    assert (
        db_session.query(ConsentRevocation)
        .filter(ConsentRevocation.user_id == test_user.id)
        .count()
        == 1
    )

    client.post("/api/consent/cyber_dna/grant", headers=auth_headers)
    conflict = client.post(
        "/api/consent/cyber_dna/revoke",
        json={"version": 1},
        headers=auth_headers,
    )
    assert conflict.status_code == 409


def test_admin_policy_allows_read_only_auditor_and_privacy_officer(
    client, db_session, auth_headers
):
    auditor = _make_user(db_session, "auditor")
    officer = _make_user(db_session, "privacy_officer")
    auditor_headers = _headers(client, auditor)
    officer_headers = _headers(client, officer)

    assert (
        client.get("/api/consent/admin/metrics", headers=auditor_headers).status_code
        == 200
    )
    run_denied = client.post(
        "/api/consent/admin/run-jobs", headers=auditor_headers
    )
    assert run_denied.status_code == 403
    assert run_denied.headers["x-policy-permission"] == "privacy.revocation.execute"

    assert (
        client.post("/api/consent/admin/run-jobs", headers=officer_headers).status_code
        == 200
    )

    assert (
        client.get("/api/consent/admin/metrics", headers=auth_headers).status_code
        == 403
    )


def test_export_contains_consent_proof_but_no_derived_payload(
    client, db_session, auth_headers, test_user, test_lab
):
    _seed_derived(db_session, test_user.id, test_lab.id)
    client.post("/api/consent/cyber_dna/revoke", headers=auth_headers)
    service.run_due_jobs(db_session)

    export = client.get("/api/auth/export", headers=auth_headers)
    assert export.status_code == 200, export.text
    body = export.json()
    assert body["consent"]["consents"]["cyber_dna"]["granted"] is False
    assert any(
        row["action"] == "revoke" and row["consent_type"] == "cyber_dna"
        for row in body["consent"]["history"]
    )
    assert "cyber_dna" not in body
    assert "dna_evidence_records" not in json.dumps(body)


def test_every_privacy_table_has_a_cleanup_and_verification_hook():
    hooks.assert_privacy_targets_registered()
    for table, key in hooks.PRIVACY_TABLES.items():
        assert key in hooks.PURGE_HOOKS, table
