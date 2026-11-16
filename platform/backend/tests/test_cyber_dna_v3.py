"""Cyber DNA v3: event ingestion, gates, snapshots, and owner APIs."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.cyber_dna.events import ActivityCompleted
from app.cyber_dna.models import DnaEvidenceRecord, DnaSnapshot
from app.cyber_dna.service import (
    AFFINITY_VERSION,
    BEHAVIOR_VERSION,
    affinity_gate,
    build_affinity,
    build_behavior,
    build_interest,
    competency_scores,
    erase_learner,
    ingest_activity,
)
from app.models import PlatformSetting

pytestmark = pytest.mark.db


def _event(learner_id, activity_id, category, competencies, **overrides):
    return ActivityCompleted(
        event_id=f"event:{uuid.uuid4().hex}",
        learner_id=learner_id,
        activity_id=activity_id,
        activity_category=category,
        competency_weights={item: 1 / len(competencies) for item in competencies},
        **overrides,
    )


def test_ingestion_is_idempotent_and_scores_competencies(db_session, test_user):
    try:
        event = _event(
            test_user.id,
            "lab-1",
            "network",
            ["NET-001", "NET-011"],
            difficulty="intermediate",
            attempts=1,
            hints_used=0,
            duration_minutes=30,
        )
        assert ingest_activity(db_session, event) == 2
        assert ingest_activity(db_session, event) == 0
        assert (
            db_session.query(DnaEvidenceRecord)
            .filter(DnaEvidenceRecord.learner_id == test_user.id)
            .count()
            == 2
        )
        scores = competency_scores(db_session, test_user.id)
        assert {item["competency_id"] for item in scores} == {"NET-001", "NET-011"}
        assert all(0 <= item["score"] <= 99 for item in scores)
    finally:
        erase_learner(db_session, test_user.id)
        db_session.commit()


def test_behavior_and_interest_use_events_only(db_session, test_user):
    try:
        for index, category in enumerate(
            ("network", "network", "malware", "malware", "forensics", "forensics")
        ):
            competencies = {
                "network": ["NET-001", "NET-011"],
                "malware": ["MAL-001", "MAL-002"],
                "forensics": ["FOR-001", "FOR-002"],
            }[category]
            ingest_activity(
                db_session,
                _event(
                    test_user.id,
                    f"lab-{index}",
                    category,
                    competencies,
                    attempts=1 + index % 2,
                    hints_used=0,
                    duration_minutes=20 + index * 5,
                ),
            )

        behavior = build_behavior(db_session, test_user.id)
        assert behavior["version"] == BEHAVIOR_VERSION
        assert behavior["signals"]["persistence"]["sample_size"] == 6
        assert behavior["signals"]["independence"]["value"] is not None
        assert behavior["signals"]["investigation"]["kind"] == "proxy"

        interest = build_interest(db_session, test_user.id)
        assert interest["available"] is True
        assert set(interest["vector"]) == {"network", "malware", "forensics"}

        gate = affinity_gate(db_session, test_user.id)
        assert gate["available"] is False
        assert gate["labs"]["have"] == 6

        affinity = build_affinity(db_session, test_user.id)
        assert affinity["available"] is False
        assert affinity["pathways"] == []
        assert affinity["gate"]["labs"]["need"] == 30
    finally:
        erase_learner(db_session, test_user.id)
        db_session.commit()


def test_affinity_stays_hidden_until_all_three_gates_are_met(db_session, test_user):
    try:
        for index in range(30):
            ingest_activity(
                db_session,
                _event(
                    test_user.id,
                    f"lab-{index}",
                    ("network", "malware", "forensics")[index % 3],
                    ["NET-001", "NET-011", "MAL-001", "FOR-001"],
                    attempts=1,
                    hints_used=0,
                    duration_minutes=30,
                ),
            )

        gate = affinity_gate(db_session, test_user.id)
        assert gate == {
            "available": True,
            "labs": {"have": 30, "need": 30},
            "domains": {"have": 3, "need": 3},
            "observations": {"have": 120, "need": 100},
        }
        affinity = build_affinity(db_session, test_user.id)
        assert affinity["available"] is True
        assert affinity["version"] == AFFINITY_VERSION
        assert affinity["pathways"]
        assert all(item["affinity"] is not None for item in affinity["pathways"])
    finally:
        erase_learner(db_session, test_user.id)
        db_session.commit()


def test_erasure_removes_evidence_and_snapshots(db_session, test_user):
    event = _event(test_user.id, "lab-erase", "network", ["NET-001"])
    ingest_activity(db_session, event)
    assert (
        db_session.query(DnaEvidenceRecord)
        .filter(DnaEvidenceRecord.learner_id == test_user.id)
        .count()
        == 1
    )
    assert erase_learner(db_session, test_user.id) == 1
    db_session.commit()
    assert (
        db_session.query(DnaEvidenceRecord)
        .filter(DnaEvidenceRecord.learner_id == test_user.id)
        .count()
        == 0
    )
    assert (
        db_session.query(DnaSnapshot)
        .filter(DnaSnapshot.learner_id == test_user.id)
        .count()
        == 0
    )


def test_api_gate_and_snapshots(db_session, client, auth_headers, test_user):
    setting = (
        db_session.query(PlatformSetting)
        .filter(PlatformSetting.key == "cyber_dna_v3_enabled")
        .first()
    )
    created = setting is None
    if setting is None:
        setting = PlatformSetting(
            key="cyber_dna_v3_enabled",
            value="false",
            category="features",
            description="test",
            is_secret=False,
        )
        db_session.add(setting)
    setting.value = "false"
    db_session.commit()
    try:
        ingest_activity(
            db_session,
            _event(
                test_user.id,
                "lab-api",
                "network",
                ["NET-001"],
                occurred_at=datetime.now(timezone.utc).replace(tzinfo=None),
            ),
        )
        for path in (
            "/api/dna/v3/evidence",
            "/api/dna/v3/behavior",
            "/api/dna/v3/interest",
            "/api/dna/v3/affinity",
            "/api/dna/v3/dna",
        ):
            assert client.get(path, headers=auth_headers).status_code == 404

        setting.value = "true"
        db_session.commit()

        response = client.get("/api/dna/v3/behavior", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["version"] == BEHAVIOR_VERSION

        dna = client.get("/api/dna/v3/dna", headers=auth_headers)
        assert dna.status_code == 200
        assert dna.json()["affinity"]["available"] is False

        snapshot = client.post(
            "/api/dna/v3/snapshots?kind=behavior_profile",
            headers=auth_headers,
        )
        assert snapshot.status_code == 200, snapshot.text
        snapshot_id = snapshot.json()["snapshot"]["snapshot_id"]
        assert snapshot.json()["snapshot"]["kind"] == "behavior_profile"

        listing = client.get(
            "/api/dna/v3/snapshots?kind=behavior_profile", headers=auth_headers
        )
        assert listing.status_code == 200
        assert any(
            row["snapshot_id"] == snapshot_id for row in listing.json()["snapshots"]
        )
        detail = client.get(
            f"/api/dna/v3/snapshots/{snapshot_id}", headers=auth_headers
        )
        assert detail.status_code == 200
        assert detail.json()["payload"]["version"] == BEHAVIOR_VERSION
    finally:
        erase_learner(db_session, test_user.id)
        if created:
            db_session.delete(setting)
        else:
            setting.value = "false"
        db_session.commit()
