"""Competency contract review cycles and instructor sign-off."""

from __future__ import annotations

import uuid

import pytest

from app.auth import get_password_hash
from app.models import CompetencyContractReview, User
from app.services.competency_contract import load_contracts

PASSWORD = "ReviewCycle#Pass123"  # Test-only credential; security-delta: allow
LAB = "ai-1-1-prompt-injection-basics"


def _user(db, role: str = "instructor", institution: str = "default") -> User:
    suffix = uuid.uuid4().hex[:10]
    user = User(
        username=f"review_{role}_{suffix}",
        email=f"review_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id=institution,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _headers(client, user: User) -> dict:
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _payload(**overrides) -> dict:
    contract = (load_contracts().get("labs") or {})[LAB]
    payload = {
        "competency_ids": [
            {"id": link["id"], "weight": link["weight"]}
            for link in contract["competency_ids"]
        ],
        "evidence": [
            {
                "type": item["type"],
                "weight": item["weight"],
                "source": item.get("source"),
                "validation": item.get("validation"),
            }
            for item in contract["evidence"]
        ],
        "assessment_reliability": contract.get("assessment_reliability") or {},
        "assessment_criteria": contract.get("assessment_criteria") or [],
        "review_cycle_months": 12,
        "rationale": "Subject-matter review of the exercise, workbook, and evidence contract.",
        "decision": "approved",
        "attestation": True,
    }
    payload.update(overrides)
    return payload


def _cleanup(db, users: list[User]) -> None:
    ids = [user.id for user in users]
    db.query(CompetencyContractReview).filter(
        CompetencyContractReview.reviewer_id.in_(ids)
    ).delete(synchronize_session=False)
    for user in users:
        db.delete(user)
    db.commit()


@pytest.mark.db
def test_queue_starts_with_pending_contracts(client, db_session):
    instructor = _user(db_session)
    try:
        response = client.get(
            "/api/competency-reviews/queue", headers=_headers(client, instructor)
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["total"] == 215
        assert body["counts"]["pending"] >= 190
        assert body["contracts"][0]["status"] == "pending"
    finally:
        _cleanup(db_session, [instructor])


@pytest.mark.db
def test_detail_returns_the_contract_and_hashes(client, db_session):
    instructor = _user(db_session)
    try:
        response = client.get(
            f"/api/competency-reviews/{LAB}", headers=_headers(client, instructor)
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["lab_slug"] == LAB
        assert body["contract"]["track"] == "AI"
        assert body["status"] == "pending"
        assert len(body["lab_hash"]) == 64
        assert len(body["taxonomy_hash"]) == 64
    finally:
        _cleanup(db_session, [instructor])


@pytest.mark.db
def test_sign_creates_a_current_review_with_a_next_date(client, db_session):
    instructor = _user(db_session)
    admin = _user(db_session, "admin")
    try:
        headers = _headers(client, instructor)
        signed = client.post(
            f"/api/competency-reviews/{LAB}/sign",
            json=_payload(),
            headers=headers,
        )
        assert signed.status_code == 200, signed.text
        body = signed.json()
        assert body["status"] == "signed"
        assert body["decision"] == "approved"
        assert body["attestation"] is True
        assert body["next_review_at"]

        detail = client.get(f"/api/competency-reviews/{LAB}", headers=headers).json()
        assert detail["status"] == "current"

        ready = client.get(
            "/api/competency-reviews/export-ready", headers=headers
        ).json()
        assert [row["id"] for row in ready["reviews"]] == [body["id"]]

        forbidden = client.post(
            f"/api/competency-reviews/{body['id']}/exported", headers=headers
        )
        assert forbidden.status_code == 403

        exported = client.post(
            f"/api/competency-reviews/{body['id']}/exported",
            headers=_headers(client, admin),
        )
        assert exported.status_code == 200, exported.text
        assert exported.json()["exported_at"]
    finally:
        _cleanup(db_session, [instructor, admin])


@pytest.mark.db
def test_attestation_is_required_and_changes_can_be_requested(client, db_session):
    instructor = _user(db_session)
    try:
        headers = _headers(client, instructor)
        missing = client.post(
            f"/api/competency-reviews/{LAB}/sign",
            json=_payload(attestation=False),
            headers=headers,
        )
        assert missing.status_code == 400
        assert missing.headers["X-Error-Code"] == "contract_review_attestation_required"

        changed = client.post(
            f"/api/competency-reviews/{LAB}/sign",
            json=_payload(decision="changes_requested", attestation=True),
            headers=headers,
        )
        assert changed.status_code == 200, changed.text
        assert changed.json()["status"] == "changes_requested"
        assert changed.json()["next_review_at"] is None
        detail = client.get(f"/api/competency-reviews/{LAB}", headers=headers).json()
        assert detail["status"] == "changes_requested"
    finally:
        _cleanup(db_session, [instructor])


@pytest.mark.db
def test_weights_must_sum_to_one(client, db_session):
    instructor = _user(db_session)
    try:
        response = client.post(
            f"/api/competency-reviews/{LAB}/sign",
            json=_payload(
                competency_ids=[{"id": "AI-001", "weight": 0.5}], attestation=True
            ),
            headers=_headers(client, instructor),
        )
        assert response.status_code == 400
        assert response.headers["X-Error-Code"] == "contract_review_invalid"
    finally:
        _cleanup(db_session, [instructor])


@pytest.mark.db
def test_mentor_can_view_but_not_sign(client, db_session):
    mentor = _user(db_session, "mentor")
    try:
        headers = _headers(client, mentor)
        assert client.get("/api/competency-reviews/queue", headers=headers).status_code == 200
        response = client.post(
            f"/api/competency-reviews/{LAB}/sign", json=_payload(), headers=headers
        )
        assert response.status_code == 403
        assert response.headers["X-Error-Code"] == "contract_review_forbidden"
    finally:
        _cleanup(db_session, [mentor])


@pytest.mark.db
def test_draft_is_owned_by_its_reviewer(client, db_session):
    first = _user(db_session, "instructor", "default")
    second = _user(db_session, "instructor", "default")
    try:
        first_headers = _headers(client, first)
        response = client.post(
            f"/api/competency-reviews/{LAB}/draft",
            json=_payload(),
            headers=first_headers,
        )
        assert response.status_code == 200, response.text
        response = client.post(
            f"/api/competency-reviews/{LAB}/draft",
            json=_payload(),
            headers=_headers(client, second),
        )
        assert response.status_code == 409
        assert response.headers["X-Error-Code"] == "contract_review_draft_owned"
    finally:
        _cleanup(db_session, [first, second])


@pytest.mark.db
def test_a_review_is_not_current_in_another_tenant(client, db_session):
    first = _user(db_session, "instructor", "tenant-a")
    second = _user(db_session, "instructor", "tenant-b")
    try:
        signed = client.post(
            f"/api/competency-reviews/{LAB}/sign",
            json=_payload(),
            headers=_headers(client, first),
        )
        assert signed.status_code == 200, signed.text
        detail = client.get(
            f"/api/competency-reviews/{LAB}", headers=_headers(client, second)
        ).json()
        assert detail["status"] == "pending"
        assert detail["latest"] is None
    finally:
        _cleanup(db_session, [first, second])


@pytest.mark.db
def test_catalogue_exposes_competencies_and_cycle_lengths(client, db_session):
    instructor = _user(db_session)
    try:
        response = client.get(
            "/api/competency-reviews/catalogue",
            headers=_headers(client, instructor),
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert len(body["competencies"]) >= 200
        assert body["cycle_months"] == [6, 12, 24]
        assert "analyst_answer" in body["evidence_types"]
        assert body["domains"]
    finally:
        _cleanup(db_session, [instructor])

def test_contract_snapshot_hash_is_stable_and_sensitive():
    from app.services.competency_contract_integrity import (
        contract_snapshot,
        snapshot_hash,
    )

    base = {
        "competency_ids": [{"id": "AI-001", "weight": 1.0}],
        "evidence": [
            {
                "type": "flag",
                "weight": 1.0,
                "source": "lab.flag",
                "validation": "exact_match",
            }
        ],
        "assessment_reliability": {"level": "medium", "score": 0.6},
        "assessment_criteria": ["Submit the correct flag."],
        "track": "AI",
    }
    reordered = {
        "track": "AI",
        "assessment_criteria": ["Submit the correct flag."],
        "assessment_reliability": {"score": 0.6, "level": "medium"},
        "evidence": [
            {
                "validation": "exact_match",
                "source": "lab.flag",
                "weight": 1.0,
                "type": "flag",
            }
        ],
        "competency_ids": [{"weight": 1.0, "id": "AI-001"}],
    }
    changed = {
        **base,
        "competency_ids": [{"id": "AI-001", "weight": 0.9}],
    }
    assert set(contract_snapshot(base)) == {
        "competency_ids",
        "evidence",
        "assessment_reliability",
        "assessment_criteria",
    }
    assert snapshot_hash(base) == snapshot_hash(reordered)
    assert snapshot_hash(base) != snapshot_hash(changed)
