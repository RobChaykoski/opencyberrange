"""Usage dashboard: attribution, QR scans, aggregates, and privacy."""

import json
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import ActivityEvent, Lab, LabCompletion, User
from app.services import attribution, usage
from app.services.activity import EventTypes

PASSWORD = "Usage#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _make_user(db_session, *, source=None, campaign=None, role="student", created_at=None):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"usage_{suffix}",
        email=f"usage_{suffix}@example.invalid",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        registration_source=source,
        registration_campaign=campaign,
        created_at=created_at or _now(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _make_lab(db_session, name="Usage Lab", category="network"):
    suffix = uuid.uuid4().hex[:8]
    lab = Lab(
        name=f"{name} {suffix}",
        slug=f"usage-lab-{suffix}",
        compose_file="docker-compose.yml",
        category=category,
        difficulty="beginner",
        is_active=True,
    )
    db_session.add(lab)
    db_session.commit()
    db_session.refresh(lab)
    return lab


def _complete(db_session, user, lab, *, completed_at=None, attempts=1, hints=0):
    row = LabCompletion(
        user_id=user.id,
        lab_id=lab.id,
        flag_submitted="TESTFLAG",
        attempts=attempts,
        hints_used=hints,
        time_spent_minutes=20,
        completed_at=completed_at or _now(),
    )
    db_session.add(row)
    db_session.commit()
    return row


def _scan(db_session, source, campaign=None, *, created_at=None):
    row = ActivityEvent(
        event_type=EventTypes.QR_SCANNED,
        target_type="campaign",
        target_label=campaign or source,
        detail=json.dumps({"source": source, "campaign": campaign}),
        created_at=created_at or _now(),
    )
    db_session.add(row)
    db_session.commit()
    return row


def _headers(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_source_and_campaign_normalization():
    assert attribution.normalize_source("Google-Developer-Groups") == "gdg"
    assert attribution.normalize_source("linkedin.com") == "linkedin"
    assert attribution.normalize_source(None) == "direct"
    assert attribution.normalize_source("  Conference 2026 ") == "conference-2026"
    assert attribution.normalize_campaign(" GDG Nov 2026 ") == "gdg-nov-2026"
    assert attribution.normalize_campaign("  ") is None


def test_registration_persists_source_and_campaign(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    response = client.post(
        "/api/auth/register",
        json={
            "username": f"attributed_{suffix}",
            "email": f"attributed_{suffix}@example.invalid",
            "password": PASSWORD,
            "age_band": "18_plus",
            "privacy_acknowledged": True,
            "source": "GDG",
            "campaign": "GDG November 2026",
        },
    )
    assert response.status_code == 200, response.text
    user = db_session.query(User).filter(User.username == f"attributed_{suffix}").first()
    assert user is not None
    assert user.registration_source == "gdg"
    assert user.registration_campaign == "gdg-november-2026"


def test_qr_landing_records_a_scan_and_redirects(client, db_session):
    response = client.get(
        "/api/public/qr/gdg?campaign=gdg-november-2026", follow_redirects=False
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/register?src=gdg&campaign=gdg-november-2026"

    scan = (
        db_session.query(ActivityEvent)
        .filter(ActivityEvent.event_type == EventTypes.QR_SCANNED)
        .order_by(ActivityEvent.id.desc())
        .first()
    )
    assert scan is not None
    detail = json.loads(scan.detail)
    assert detail["source"] == "gdg"
    assert detail["campaign"] == "gdg-november-2026"


def test_public_usage_aggregates_and_suppresses_small_counts(db_session, monkeypatch):
    monkeypatch.setattr(usage, "_minimum_cohort_size", lambda db: 5)
    now = _now()
    source_key = f"usage-test-{uuid.uuid4().hex[:8]}"
    campaign_key = f"campaign-{uuid.uuid4().hex[:8]}"
    gdg_user = _make_user(db_session, source=source_key, created_at=now - timedelta(days=1))
    linkedin_user = _make_user(
        db_session, source="linkedin", created_at=now - timedelta(days=2)
    )
    lab = _make_lab(db_session)
    _complete(db_session, gdg_user, lab, completed_at=now - timedelta(hours=2), attempts=1)
    _complete(
        db_session,
        linkedin_user,
        lab,
        completed_at=now - timedelta(days=1),
        attempts=3,
        hints=1,
    )
    _scan(db_session, source_key, campaign_key)
    _scan(db_session, "linkedin", "linkedin-launch")

    payload = usage.build_usage(db_session, days=30, public=True)

    assert payload["totals"]["registrations"]["value"] >= 2
    assert payload["totals"]["completions"]["value"] >= 2
    source_row = next(item for item in payload["sources"] if item["key"] == source_key)
    assert source_row["registrations"] is None
    assert source_row["registrations_suppressed"] is True
    assert source_row["share"] is None
    assert payload["labs"]["items"]
    assert payload["minimum_cohort_size"] > 0

    serialized = json.dumps(payload)
    assert "usage_" not in serialized
    assert "@example.invalid" not in serialized

    admin_payload = usage.build_usage(db_session, days=30, public=False)
    admin_source = next(
        item for item in admin_payload["sources"] if item["key"] == source_key
    )
    assert admin_source["registrations"] == 1
    assert admin_source["registrations_suppressed"] is False


def test_admin_usage_requires_admin(client, db_session):
    student = _make_user(db_session)
    admin = _make_user(db_session, role="admin")

    assert client.get("/api/usage/admin", headers=_headers(client, student)).status_code == 403
    response = client.get("/api/usage/admin", headers=_headers(client, admin))
    assert response.status_code == 200, response.text
    assert response.json()["public"] is False


def test_qr_png_requires_admin(client, db_session):
    student = _make_user(db_session)
    admin = _make_user(db_session, role="admin")

    assert (
        client.get(
            "/api/usage/admin/qr?source=gdg", headers=_headers(client, student)
        ).status_code
        == 403
    )
    response = client.get(
        "/api/usage/admin/qr?source=gdg&campaign=gdg-november-2026",
        headers=_headers(client, admin),
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG")
