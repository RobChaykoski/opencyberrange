"""Workbook answer capture and its evidence snapshot."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import pytest

from app.auth import get_password_hash
from app.models import (
    EvidenceRecord,
    ExerciseQuizAttempt,
    FlagAttempt,
    Lab,
    LabCompletion,
    User,
    WorkbookAnswer,
)

PASSWORD = "Workbook#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db

SLUG = "osint-1-3-exif-metadata"


def _user(db, role: str = "student") -> User:
    suffix = hashlib.sha256(f"{role}-{datetime.now(timezone.utc)}".encode()).hexdigest()[:10]
    user = User(
        username=f"workbook_{role}_{suffix}",
        email=f"workbook_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id="default",
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


def _lab(db) -> Lab:
    db.query(WorkbookAnswer).filter(
        WorkbookAnswer.lab_id.in_(db.query(Lab.id).filter(Lab.slug == SLUG))
    ).delete(synchronize_session=False)
    existing = db.query(Lab).filter(Lab.slug == SLUG).first()
    if existing is not None:
        db.query(FlagAttempt).filter(FlagAttempt.lab_id == existing.id).delete(
            synchronize_session=False
        )
        db.query(LabCompletion).filter(LabCompletion.lab_id == existing.id).delete(
            synchronize_session=False
        )
        db.query(ExerciseQuizAttempt).filter(
            ExerciseQuizAttempt.lab_id == existing.id
        ).delete(synchronize_session=False)
        db.delete(existing)
        db.commit()
    lab = Lab(
        name="Workbook Answer Test Lab",
        slug=SLUG,
        description="Synthetic workbook answer test",
        compose_file="services: {}\n",
        is_active=True,
        visibility="public",
        workbook="wiki/range/osint/CH_OSINT01_OSINT_Foundations/03_EXIF_Metadata/",
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab


def _cleanup(db, user: User, lab: Lab) -> None:
    db.query(EvidenceRecord).filter(EvidenceRecord.learner_id == user.id).delete(
        synchronize_session=False
    )
    db.query(WorkbookAnswer).filter(WorkbookAnswer.lab_id == lab.id).delete(
        synchronize_session=False
    )
    db.delete(lab)
    db.delete(user)
    db.commit()


def test_workbook_answer_saves_and_snapshots_evidence(client, db_session):
    user = _user(db_session)
    lab = _lab(db_session)
    headers = _headers(client, user)
    try:
        first = client.put(
            f"/api/workbook-answers/{SLUG}",
            json={"answer": "I found the camera metadata in the UserComment field."},
            headers=headers,
        )
        assert first.status_code == 200, first.text
        body = first.json()
        assert body["created"] is True
        assert body["answer"]["answer_text"].startswith("I found")
        assert body["evidence"]["status"] == "collected"
        assert body["evidence"]["content_text"].startswith("I found")
        evidence_id = body["evidence"]["id"]

        replay = client.put(
            f"/api/workbook-answers/{SLUG}",
            json={"answer": "I found the camera metadata in the UserComment field."},
            headers=headers,
        )
        assert replay.status_code == 200
        assert replay.json()["created"] is False
        assert replay.json()["evidence"]["id"] == evidence_id

        edited = client.put(
            f"/api/workbook-answers/{SLUG}",
            json={"answer": "I found the camera metadata and the GPS coordinates in the file."},
            headers=headers,
        )
        assert edited.status_code == 200
        assert edited.json()["created"] is True
        assert edited.json()["evidence"]["id"] != evidence_id

        current = client.get(
            f"/api/workbook-answers/{SLUG}",
            headers=headers,
        )
        assert current.status_code == 200
        assert "GPS coordinates" in current.json()["answer"]["answer_text"]

        options = client.get("/api/workbook-answers/options", headers=headers)
        assert options.status_code == 200
        assert any(item["slug"] == SLUG for item in options.json()["exercises"])

        admin = _user(db_session, "admin")
        admin_headers = _headers(client, admin)
        detail = client.get(
            f"/api/evidence/{edited.json()['evidence']['id']}",
            headers=admin_headers,
        )
        assert detail.status_code == 200
        assert "GPS coordinates" in detail.json()["evidence"]["content_text"]
    finally:
        _cleanup(db_session, user, lab)


def test_short_workbook_answer_is_rejected(client, db_session):
    user = _user(db_session)
    lab = _lab(db_session)
    headers = _headers(client, user)
    try:
        response = client.put(
            f"/api/workbook-answers/{SLUG}",
            json={"answer": "short"},
            headers=headers,
        )
        assert response.status_code == 422
    finally:
        _cleanup(db_session, user, lab)
