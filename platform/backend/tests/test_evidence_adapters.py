"""Deterministic evidence adapters for flags and knowledge checks."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.models import EvidenceRecord, EvidenceReview, FlagAttempt, Lab, LabCompletion
from app.services.evidence_adapters import (
    record_flag_evidence,
    record_quiz_evidence,
)

pytestmark = pytest.mark.db


def _lab(slug: str) -> SimpleNamespace:
    return SimpleNamespace(slug=slug)


def test_flag_adapter_creates_accepted_evidence(db_session, test_user):
    completion = SimpleNamespace(
        completed_at=datetime.now(timezone.utc),
        competency_model_version="2026.14",
    )

    record = record_flag_evidence(
        db_session,
        test_user,
        _lab("osint-1-3-exif-metadata"),
        completion,
    )

    assert record is not None
    assert record.status == "accepted"
    assert record.source_type == "flag"
    assert record.rubric_id == "automatic-check"
    assert record.rubric_version == "1.0"
    assert record.source_id == "osint-1-3-exif-metadata"
    assert record.competencies
    assert record.reviews
    assert record.reviews[0].decision == "accepted"
    assert record.reviews[0].reviewer_id is None
    assert record.reviews[0].weighted_score == 1.0

    again = record_flag_evidence(
        db_session,
        test_user,
        _lab("osint-1-3-exif-metadata"),
        completion,
    )
    assert again.id == record.id
    assert (
        db_session.query(EvidenceReview)
        .filter(EvidenceReview.evidence_id == record.id)
        .count()
        == 1
    )


def test_quiz_adapter_records_only_a_pass(db_session, test_user):
    passed = SimpleNamespace(
        passed=True,
        score=90,
        correct=3,
        total=3,
        completed_at=datetime.now(timezone.utc),
    )
    record = record_quiz_evidence(
        db_session,
        test_user,
        _lab("osint-1-3-exif-metadata"),
        passed,
    )
    assert record is not None
    assert record.status == "accepted"
    assert record.source_type == "quiz"
    assert record.confidence == "high"
    assert "90%" in (record.confidence_reason or "")

    failed = SimpleNamespace(
        passed=False,
        score=50,
        correct=1,
        total=2,
        completed_at=datetime.now(timezone.utc),
    )
    assert (
        record_quiz_evidence(
            db_session,
            test_user,
            _lab("osint-1-3-exif-metadata"),
            failed,
        )
        is None
    )


def test_adapter_is_a_noop_without_a_competency_contract(db_session, test_user):
    completion = SimpleNamespace(
        completed_at=datetime.now(timezone.utc),
        competency_model_version="2026.14",
    )
    assert (
        record_flag_evidence(
            db_session,
            test_user,
            _lab("not-a-real-lab-contract"),
            completion,
        )
        is None
    )


def test_correct_flag_endpoint_schedules_evidence(
    client, db_session, test_user, test_flag, auth_headers
):
    slug = "osint-1-3-exif-metadata"
    db_session.query(FlagAttempt).filter(
        FlagAttempt.lab_id.in_(
            db_session.query(Lab.id).filter(Lab.slug == slug).scalar_subquery()
        )
    ).delete(synchronize_session=False)
    previous = db_session.query(Lab).filter(Lab.slug == slug).first()
    if previous is not None:
        db_session.query(LabCompletion).filter(LabCompletion.lab_id == previous.id).delete(
            synchronize_session=False
        )
        db_session.delete(previous)
        db_session.commit()

    lab = Lab(
        name="Evidence Adapter Flag Lab",
        slug=slug,
        description="Synthetic flag adapter test",
        compose_file="services: {}\n",
        is_active=True,
        visibility="public",
        flag_hash=hashlib.sha256(test_flag.encode()).hexdigest(),
    )
    db_session.add(lab)
    db_session.commit()
    db_session.refresh(lab)
    try:
        response = client.post(
            f"/api/exercises/labs/{lab.id}/submit-flag",
            json={"flag": test_flag},
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        assert response.json()["correct"] is True

        records = (
            db_session.query(EvidenceRecord)
            .filter(
                EvidenceRecord.learner_id == test_user.id,
                EvidenceRecord.source_type == "flag",
                EvidenceRecord.source_id == slug,
            )
            .all()
        )
        assert len(records) == 1
        assert records[0].status == "accepted"
        assert records[0].reviews[0].decision == "accepted"
    finally:
        db_session.query(FlagAttempt).filter(FlagAttempt.lab_id == lab.id).delete(
            synchronize_session=False
        )
        db_session.query(LabCompletion).filter(
            LabCompletion.lab_id == lab.id
        ).delete(synchronize_session=False)
        db_session.delete(lab)
        db_session.commit()


def test_adapter_evidence_is_scoped_to_the_learner(db_session, test_user):
    completion = SimpleNamespace(
        completed_at=datetime.now(timezone.utc),
        competency_model_version="2026.14",
    )
    record = record_flag_evidence(
        db_session,
        test_user,
        _lab("osint-1-3-exif-metadata"),
        completion,
    )
    assert record is not None
    assert record.institution_id == (test_user.institution_id or "default")
    assert (
        db_session.query(EvidenceRecord)
        .filter(
            EvidenceRecord.id == record.id,
            EvidenceRecord.learner_id == test_user.id,
        )
        .count()
        == 1
    )
