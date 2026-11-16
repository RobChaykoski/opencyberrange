"""Scoped service identities cannot act as shared administrators."""

from __future__ import annotations

import uuid

import pytest
from fastapi import HTTPException

from app.auth import get_password_hash
from app.models import User
from app.services import service_identities

PASSWORD = "Service#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _admin(db):
    suffix = uuid.uuid4().hex[:8]
    row = User(
        username=f"svc_admin_{suffix}",
        email=f"svc_admin_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=True,
        role="admin",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def test_service_token_uses_explicit_scopes_only(client, db_session):
    admin = _admin(db_session)
    row, token = service_identities.create_credential(
        db_session,
        admin,
        name="scheduler export",
        scopes=["security.events.view"],
        days=30,
    )
    assert token.startswith("ocr_svc_")
    assert row.token_hash != token

    response = client.get(
        "/api/admin/security/events",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text

    # The service can read events but cannot use a permission it was not given.
    forbidden = client.get(
        "/api/admin/security/service-identities",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert forbidden.status_code == 403


def test_service_password_login_is_disabled(client, db_session):
    admin = _admin(db_session)
    row, _token = service_identities.create_credential(
        db_session,
        admin,
        name="no interactive login",
        scopes=["profile.view.self"],
    )
    user = db_session.get(User, row.user_id)
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 401


def test_service_token_can_be_revoked(client, db_session):
    admin = _admin(db_session)
    row, token = service_identities.create_credential(
        db_session,
        admin,
        name="short lived",
        scopes=["security.events.view"],
    )
    assert client.get(
        "/api/admin/security/events",
        headers={"Authorization": f"Bearer {token}"},
    ).status_code == 200
    assert service_identities.revoke_credential(db_session, admin, row.id) is True
    assert client.get(
        "/api/admin/security/events",
        headers={"Authorization": f"Bearer {token}"},
    ).status_code == 401


def test_service_identity_cannot_receive_private_data_scopes(db_session):
    admin = _admin(db_session)
    with pytest.raises(HTTPException) as exc:
        service_identities.create_credential(
            db_session,
            admin,
            name="private probe",
            scopes=["dna.view.private"],
        )
    assert exc.value.status_code == 422
