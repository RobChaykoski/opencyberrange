"""Event certificate tests.

Covers participation, placement and trophy-challenge certificates, PDF output,
public verification, certificate opt-out, and the eligibility boundaries
(ended event, approved participant).
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import (
    Achievement,
    Competition,
    CompetitionParticipant,
    CompetitionSponsor,
    User,
)

pytestmark = pytest.mark.db

TEST_PASSWORD = "Correct#Horse7Battery"

TINY_PNG = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


def _ended_event(db, user, *, badges=(), sponsor=True):
    now = datetime.now(timezone.utc)
    competition = Competition(
        name=f"Event Certificate {uuid.uuid4().hex[:8]}",
        description="Test-only ended event",
        start_at=now - timedelta(hours=2),
        end_at=now - timedelta(hours=1),
        is_active=True,
        is_archived=False,
    )
    db.add(competition)
    db.flush()
    db.add(
        CompetitionParticipant(
            competition_id=competition.id,
            user_id=user.id,
            source="opt_in",
        )
    )
    if sponsor:
        db.add(
            CompetitionSponsor(
                competition_id=competition.id,
                name="Northstar Bank",
                tier="gold",
                sort_order=0,
                logo_data=TINY_PNG,
            )
        )
    for code in badges:
        db.add(
            Achievement(
                user_id=user.id,
                course_id=None,
                lab_id=None,
                achievement_type=f"comp_{competition.id}_{code}",
            )
        )
    db.commit()
    return competition


def _cleanup(db, competition_id, user_id):
    db.query(Achievement).filter(
        Achievement.user_id == user_id,
        Achievement.achievement_type.like(f"comp_{competition_id}_%"),
    ).delete(synchronize_session=False)
    db.query(CompetitionParticipant).filter(
        CompetitionParticipant.competition_id == competition_id
    ).delete(synchronize_session=False)
    db.query(CompetitionSponsor).filter(
        CompetitionSponsor.competition_id == competition_id
    ).delete(synchronize_session=False)
    db.query(Competition).filter(Competition.id == competition_id).delete(
        synchronize_session=False
    )
    db.commit()


def test_event_participation_placement_and_trophy_certificates(
    client, db_session, auth_headers, test_user
):
    competition = _ended_event(db_session, test_user, badges=("ch", "fb", "cs", "pr"))
    try:
        listed = client.get(
            f"/api/competitions/{competition.id}/certificates",
            headers=auth_headers,
        )
        assert listed.status_code == 200, listed.text
        awards = {row["award"] for row in listed.json()["certificates"]}
        assert awards == {
            "participation",
            "first",
            "first_blood",
            "clean_sweep",
            "perfect",
        }

        participation = client.get(
            f"/api/competitions/{competition.id}/certificate/participation",
            headers=auth_headers,
        )
        assert participation.status_code == 200, participation.text
        certificate = participation.json()
        assert certificate["kind"] == "event"
        assert certificate["award"] == "participation"
        assert certificate["recipient"] == test_user.display_name
        assert certificate["event_name"] == competition.name
        assert certificate["sponsors"][0]["name"] == "Northstar Bank"
        assert certificate["certificate_id"].startswith("OCR-EVT-")
        assert certificate["public_verification"] is True
        assert certificate["verify_url"].endswith(
            f"/verify/certificate/{certificate['certificate_id']}"
        )
        assert certificate["qr_code"].startswith("data:image/png;base64,")

        placement = client.get(
            f"/api/competitions/{competition.id}/certificate/first",
            headers=auth_headers,
        )
        assert placement.status_code == 200, placement.text
        assert placement.json()["award"] == "first"
        assert placement.json()["title"] == "Certificate of Achievement"

        trophy = client.get(
            f"/api/competitions/{competition.id}/certificate/first_blood",
            headers=auth_headers,
        )
        assert trophy.status_code == 200, trophy.text
        assert trophy.json()["title"] == "Trophy Challenge Certificate"

        # An award the participant did not earn is not downloadable.
        missing = client.get(
            f"/api/competitions/{competition.id}/certificate/second",
            headers=auth_headers,
        )
        assert missing.status_code == 404, missing.text

        pdf = client.get(
            f"/api/competitions/{competition.id}/certificate/participation",
            params={"format": "pdf"},
            headers=auth_headers,
        )
        assert pdf.status_code == 200, pdf.text
        assert pdf.content.startswith(b"%PDF")
        assert pdf.headers["content-type"] == "application/pdf"

        verified = client.get(
            f"/api/exercises/verify/certificate/{certificate['certificate_id']}"
        )
        assert verified.status_code == 200, verified.text
        payload = verified.json()
        assert payload["valid"] is True
        assert payload["kind"] == "event"
        assert payload["award"] == "participation"
        assert payload["event_name"] == competition.name
        assert payload["recipient"] == certificate["recipient"]
        # Public verification must not turn into an account or score lookup.
        for identifier in (
            "username",
            "email",
            "student_id",
            "user_id",
            "score",
            "solved_count",
        ):
            assert identifier not in payload

        # A tampered digest must not verify.
        tampered = certificate["certificate_id"][:-1] + (
            "0" if certificate["certificate_id"][-1] != "0" else "1"
        )
        rejected = client.get(f"/api/exercises/verify/certificate/{tampered}")
        assert rejected.status_code == 200
        assert rejected.json()["valid"] is False

        # Opting out of public certificates stops public verification but the
        # holder can still render their own certificate.
        test_user.certificates_public = False
        db_session.commit()

        withdrawn = client.get(
            f"/api/exercises/verify/certificate/{certificate['certificate_id']}"
        )
        assert withdrawn.status_code == 200
        assert withdrawn.json()["valid"] is False

        private = client.get(
            f"/api/competitions/{competition.id}/certificate/participation",
            headers=auth_headers,
        )
        assert private.status_code == 200, private.text
        assert private.json()["public_verification"] is False
        assert private.json()["verify_url"] is None
        assert private.json()["qr_code"] is None
    finally:
        test_user.certificates_public = True
        db_session.commit()
        _cleanup(db_session, competition.id, test_user.id)


def test_event_certificates_require_an_ended_event(
    client, db_session, auth_headers, test_user
):
    now = datetime.now(timezone.utc)
    competition = Competition(
        name=f"Live Event {uuid.uuid4().hex[:8]}",
        start_at=now - timedelta(minutes=30),
        end_at=now + timedelta(minutes=30),
        is_active=True,
    )
    db_session.add(competition)
    db_session.flush()
    db_session.add(
        CompetitionParticipant(
            competition_id=competition.id,
            user_id=test_user.id,
            source="opt_in",
        )
    )
    db_session.commit()
    try:
        listed = client.get(
            f"/api/competitions/{competition.id}/certificates",
            headers=auth_headers,
        )
        assert listed.status_code == 409, listed.text
        assert "after the event ends" in listed.json()["detail"]

        download = client.get(
            f"/api/competitions/{competition.id}/certificate/participation",
            headers=auth_headers,
        )
        assert download.status_code == 409, download.text
    finally:
        _cleanup(db_session, competition.id, test_user.id)


def test_event_certificates_require_participation(
    client, db_session, test_user
):
    """A non-participant cannot request a certificate for an ended event."""
    suffix = uuid.uuid4().hex[:8]
    outsider = User(
        username=f"event_outsider_{suffix}",
        email=f"event_outsider_{suffix}@example.invalid",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add(outsider)
    db_session.commit()
    db_session.refresh(outsider)

    now = datetime.now(timezone.utc)
    competition = Competition(
        name=f"Outsider Event {suffix}",
        start_at=now - timedelta(hours=2),
        end_at=now - timedelta(hours=1),
        is_active=True,
    )
    db_session.add(competition)
    db_session.flush()
    # test_user participates; outsider does not.
    db_session.add(
        CompetitionParticipant(
            competition_id=competition.id,
            user_id=test_user.id,
            source="opt_in",
        )
    )
    db_session.commit()

    try:
        login = client.post(
            "/api/auth/login",
            data={"username": outsider.username, "password": TEST_PASSWORD},
        )
        assert login.status_code == 200, login.text
        outsider_headers = {
            "Authorization": f"Bearer {login.json()['access_token']}"
        }

        denied = client.get(
            f"/api/competitions/{competition.id}/certificates",
            headers=outsider_headers,
        )
        assert denied.status_code == 403, denied.text
        assert "Join the event" in denied.json()["detail"]
    finally:
        db_session.query(User).filter(User.id == outsider.id).delete()
        db_session.commit()
        _cleanup(db_session, competition.id, test_user.id)
