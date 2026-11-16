"""Portfolio share expiry, revocation, single-use, consent, and audit."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.auth import get_password_hash
from app.models import PlatformSetting, SecurityEvent, User
from app.services import portfolio_shares

PASSWORD = "Share#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


@pytest.fixture(autouse=True)
def _suppression_ledger(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "CONSENT_SUPPRESSION_PATH", str(tmp_path / "consent-suppression.jsonl")
    )


def _user(db):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"share_{suffix}",
        email=f"share_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _grant_sharing(db, user):
    from app.consent import service as consent_service

    if consent_service.blocked_status(db, user.id, "portfolio_sharing"):
        consent_service.grant(db, user.id, "portfolio_sharing", actor="self")


def _set(db, key, value):
    row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if row is None:
        row = PlatformSetting(
            key=key,
            value=str(value),
            category="security",
            description="test",
            is_secret=False,
        )
        db.add(row)
    else:
        row.value = str(value)
    db.commit()


def test_share_requires_live_sharing_consent(db_session):
    user = _user(db_session)
    with pytest.raises(HTTPException) as exc:
        portfolio_shares.create_share(db_session, user)
    assert exc.value.status_code == 403


def test_single_use_share_is_consumed_once(db_session):
    user = _user(db_session)
    _grant_sharing(db_session, user)
    row, token = portfolio_shares.create_share(
        db_session, user, label="Employer", single_use=True
    )
    assert row.single_use is True
    assert token
    # Only the hash is persisted.
    assert row.token_hash != token
    assert len(row.token_hash) == 64

    first = portfolio_shares.resolve_share(db_session, token, ip_address="203.0.113.9")
    assert first is not None
    second = portfolio_shares.resolve_share(db_session, token)
    assert second is None

    used = (
        db_session.query(SecurityEvent)
        .filter(SecurityEvent.event_type == "portfolio.share_used")
        .order_by(SecurityEvent.id.desc())
        .first()
    )
    assert used is not None


def test_revocation_and_expiry_disable_a_share(db_session):
    user = _user(db_session)
    _grant_sharing(db_session, user)
    row, token = portfolio_shares.create_share(db_session, user)
    assert portfolio_shares.resolve_share(db_session, token) is not None

    assert portfolio_shares.revoke_share(db_session, user, row.id) is True
    assert portfolio_shares.resolve_share(db_session, token) is None

    other, other_token = portfolio_shares.create_share(db_session, user)
    other.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        seconds=1
    )
    db_session.commit()
    assert portfolio_shares.resolve_share(db_session, other_token) is None


def test_revoking_sharing_consent_disables_existing_links(db_session):
    user = _user(db_session)
    _grant_sharing(db_session, user)
    row, token = portfolio_shares.create_share(db_session, user)
    assert portfolio_shares.resolve_share(db_session, token) is not None

    from app.consent import service as consent_service

    consent_service.revoke(db_session, user.id, "portfolio_sharing", reason="test")
    assert portfolio_shares.resolve_share(db_session, token) is None


def test_share_lifetime_is_capped_by_setting(db_session):
    user = _user(db_session)
    _grant_sharing(db_session, user)
    _set(db_session, "portfolio_share_lifetime_days", "30")
    row, _token = portfolio_shares.create_share(db_session, user)
    delta = row.expires_at - datetime.now(timezone.utc).replace(tzinfo=None)
    assert timedelta(days=29) < delta <= timedelta(days=30, seconds=5)
