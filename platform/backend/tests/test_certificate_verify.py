"""Certificate verification tests."""
import uuid

import pytest

from app.models import Level, Track, User

pytestmark = pytest.mark.db


def test_public_certificate_verification(client, auth_headers, test_user, test_lab, test_flag, db_session):
    suffix = uuid.uuid4().hex[:8]
    track = Track(
        name=f"Verification Test {suffix}",
        slug=f"verify-{suffix}",
        description="Test-only track",
        icon="web",
        color="#0EA5E9",
        sort_order=99,
        is_active=True,
        sequential=False,
    )
    db_session.add(track)
    db_session.flush()

    level = Level(
        track_id=track.id,
        level_number=1,
        name="Verification Level",
        description="Test-only level",
        sort_order=1,
    )
    db_session.add(level)
    db_session.flush()

    test_lab.level_id = level.id
    test_lab.visibility = "public"
    test_lab.is_active = True
    db_session.commit()

    try:
        submit = client.post(
            f"/api/exercises/labs/{test_lab.id}/submit-flag",
            json={"flag": test_flag},
            headers=auth_headers,
        )
        assert submit.status_code == 200, submit.text
        assert submit.json()["correct"] is True

        issued = client.get(
            f"/api/exercises/tracks/{track.slug}/levels/{level.id}/certificate",
            headers=auth_headers,
        )
        assert issued.status_code == 200, issued.text
        certificate = issued.json()
        assert certificate["recipient"]
        assert certificate["certificate_id"].startswith("OCR-")

        pdf = client.get(
            f"/api/exercises/tracks/{track.slug}/levels/{level.id}/certificate.pdf",
            headers=auth_headers,
        )
        assert pdf.status_code == 200, pdf.text
        assert pdf.content.startswith(b"%PDF")
        assert b"/Title" in pdf.content
        assert b"/Author" in pdf.content
        assert b"/Lang" in pdf.content

        verified = client.get(
            f"/api/exercises/verify/certificate/{certificate['certificate_id']}"
        )
        assert verified.status_code == 200, verified.text
        payload = verified.json()
        assert payload["valid"] is True
        assert payload["certificate_id"] == certificate["certificate_id"]
        assert payload["recipient"] == certificate["recipient"]
        assert payload["track_name"] == track.name
        assert payload["level_name"] == level.name
        assert payload["exercises_completed"] == 1
        assert payload["exercises_total"] == 1
        # Verification is public; it must not turn into an account lookup.
        for identifier in ("username", "email", "student_id", "user_id"):
            assert identifier not in payload

        # The holder can opt out of public verification. Their own certificate
        # still renders, but the public verify endpoint stops confirming it and
        # the payload no longer carries a verification URL.
        db_session.query(User).filter(User.id == test_user.id).update(
            {"certificates_public": False}
        )
        db_session.commit()

        withdrawn = client.get(
            f"/api/exercises/verify/certificate/{certificate['certificate_id']}"
        )
        assert withdrawn.status_code == 200
        assert withdrawn.json()["valid"] is False

        private_certificate = client.get(
            f"/api/exercises/tracks/{track.slug}/levels/{level.id}/certificate",
            headers=auth_headers,
        )
        assert private_certificate.status_code == 200, private_certificate.text
        assert private_certificate.json()["public_verification"] is False
        assert private_certificate.json()["verify_url"] is None
        assert private_certificate.json()["qr_code"] is None
    finally:
        db_session.query(type(test_lab)).filter(type(test_lab).id == test_lab.id).update(
            {"level_id": None}
        )
        db_session.query(Level).filter(Level.id == level.id).delete()
        db_session.query(Track).filter(Track.id == track.id).delete()
        db_session.commit()


def test_public_verification_accepts_compound_track_slug(
    client, auth_headers, test_user, test_lab, test_flag, db_session
):
    """high-school-... certificates carry a hyphen in the track prefix."""
    track = Track(
        name="High School Verification Test",
        slug="high-school",
        description="Test-only track",
        icon="brain",
        color="#8B5CF6",
        sort_order=100,
        is_active=True,
        sequential=False,
    )
    db_session.add(track)
    db_session.flush()

    level = Level(
        track_id=track.id,
        level_number=12,
        name="Compound Prefix Level",
        description="Test-only level",
        sort_order=1,
    )
    db_session.add(level)
    db_session.flush()

    test_lab.level_id = level.id
    test_lab.visibility = "public"
    test_lab.is_active = True
    db_session.commit()

    try:
        submit = client.post(
            f"/api/exercises/labs/{test_lab.id}/submit-flag",
            json={"flag": test_flag},
            headers=auth_headers,
        )
        assert submit.status_code == 200, submit.text
        assert submit.json()["correct"] is True

        issued = client.get(
            f"/api/exercises/tracks/{track.slug}/levels/{level.id}/certificate",
            headers=auth_headers,
        )
        assert issued.status_code == 200, issued.text
        certificate = issued.json()
        assert certificate["certificate_id"].startswith("OCR-HIGH-SCH-")

        verified = client.get(
            f"/api/exercises/verify/certificate/{certificate['certificate_id']}"
        )
        assert verified.status_code == 200, verified.text
        assert verified.json()["valid"] is True
        assert verified.json()["certificate_id"] == certificate["certificate_id"]
    finally:
        db_session.query(type(test_lab)).filter(type(test_lab).id == test_lab.id).update(
            {"level_id": None}
        )
        db_session.query(Level).filter(Level.id == level.id).delete()
        db_session.query(Track).filter(Track.id == track.id).delete()
        db_session.commit()
