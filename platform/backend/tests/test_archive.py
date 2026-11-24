"""The Living Archive observes verified contribution; it is not a survey."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from app.auth import get_password_hash
from app.models import ImpactContribution, User

PASSWORD = "Archive#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role: str = "student") -> User:
    suffix = uuid.uuid4().hex[:10]
    user = User(
        username=f"archive_{role}_{suffix}",
        email=f"archive_{role}_{suffix}@example.org",
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


def _add(db, user, *, dimension, kind, days_ago=0, reach=5):
    now = datetime(2026, 6, 1)
    occurred = now - timedelta(days=days_ago)
    row = ImpactContribution(
        institution_id="default",
        user_id=user.id,
        dimension=dimension,
        kind=kind,
        title=f"{dimension} {kind}",
        base_points=30,
        reach_count=reach,
        quality_rating=4.0,
        validation_level="instructor",
        originality="original",
        status="verified",
        occurred_at=occurred,
        verified_at=occurred,
        last_used_at=occurred,
    )
    db.add(row)
    db.commit()
    return row


def _cleanup(db, user: User) -> None:
    db.query(ImpactContribution).filter(
        ImpactContribution.user_id == user.id
    ).delete(synchronize_session=False)
    db.delete(user)
    db.commit()


def test_empty_archive_says_undetermined(client, db_session):
    learner = _user(db_session)
    try:
        response = client.get(
            "/api/archive/me", headers=_headers(client, learner)
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["status"] == "undetermined"
        assert body["tradition"] is None
        assert body["observed"]["contributions"] == 0
        assert "observing" in " ".join(body["notes"]).lower()
        assert "%" not in response.text
    finally:
        _cleanup(db_session, learner)


def test_one_narrow_kind_is_not_a_tradition(client, db_session):
    learner = _user(db_session)
    try:
        for _ in range(5):
            _add(db_session, learner, dimension="build", kind="lab")
        body = client.get(
            "/api/archive/me", headers=_headers(client, learner)
        ).json()
        assert body["status"] == "undetermined"
        assert body["tradition"] is None
        assert body["observed"]["kinds"] == 1
    finally:
        _cleanup(db_session, learner)


def test_three_builds_across_two_kinds_emerge_as_creation(client, db_session):
    learner = _user(db_session)
    try:
        _add(db_session, learner, dimension="build", kind="lab", reach=100)
        _add(db_session, learner, dimension="build", kind="tool", reach=40)
        _add(db_session, learner, dimension="build", kind="workbook", reach=20)
        body = client.get(
            "/api/archive/me", headers=_headers(client, learner)
        ).json()
        assert body["status"] == "emerging"
        assert body["tradition"]["title"] == "Creation"
        assert body["tradition"]["archetype"] == "The Builders"
        assert body["observed"]["contributions"] == 3
        assert body["observed"]["kinds"] == 3
        assert any("built something" in note for note in body["notes"])
        assert "%" not in str(body)
    finally:
        _cleanup(db_session, learner)


def test_a_tie_stays_undetermined(client, db_session):
    learner = _user(db_session)
    try:
        _add(db_session, learner, dimension="build", kind="lab")
        _add(db_session, learner, dimension="build", kind="tool")
        _add(db_session, learner, dimension="build", kind="workbook")
        _add(db_session, learner, dimension="protect", kind="assessment")
        _add(db_session, learner, dimension="protect", kind="remediation")
        _add(db_session, learner, dimension="protect", kind="mfa_rollout")
        body = client.get(
            "/api/archive/me", headers=_headers(client, learner)
        ).json()
        assert body["status"] == "undetermined"
        assert body["tradition"] is None
    finally:
        _cleanup(db_session, learner)


def test_long_broad_record_is_recognized(client, db_session):
    learner = _user(db_session)
    try:
        for kind in ("lab", "tool", "workbook", "integration"):
            _add(
                db_session,
                learner,
                dimension="build",
                kind=kind,
                days_ago=200,
                reach=50,
            )
        _add(db_session, learner, dimension="build", kind="lab", days_ago=100)
        _add(db_session, learner, dimension="build", kind="tool", days_ago=10)
        body = client.get(
            "/api/archive/me", headers=_headers(client, learner)
        ).json()
        assert body["status"] == "recognized"
        assert body["tradition"]["title"] == "Creation"
        assert body["observed"]["days"] >= 180
    finally:
        _cleanup(db_session, learner)


def test_archive_requires_authentication(client):
    assert client.get("/api/archive/me").status_code == 401
