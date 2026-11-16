"""Admin-only certification question-bank APIs."""

import uuid

import pytest

from app.auth import get_password_hash
from app.models import User

# Test-only login credential; security-delta: allow credential-like assignment
PASSWORD = "QBank#Pass123"
pytestmark = pytest.mark.db


def _make_user(db_session, role):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"qbank_{role}_{suffix}",
        email=f"qbank_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _headers(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_question_banks_require_admin(client, db_session):
    student = _make_user(db_session, "student")
    headers = _headers(client, student)

    assert client.get("/api/admin/question-banks").status_code == 401
    assert (
        client.get("/api/admin/question-banks", headers=headers).status_code == 403
    )
    assert (
        client.get(
            "/api/admin/question-banks/comptia-network-plus", headers=headers
        ).status_code
        == 403
    )
    assert (
        client.post("/api/admin/question-banks/validate", headers=headers).status_code
        == 403
    )


def test_question_bank_listing_and_detail(client, db_session):
    admin = _make_user(db_session, "admin")
    headers = _headers(client, admin)

    listing = client.get("/api/admin/question-banks", headers=headers)
    assert listing.status_code == 200, listing.text
    body = listing.json()
    assert body["version"]
    assert body["reviewed_at"]
    assert len(body["pathways"]) >= 8
    assert body["validation"]["ok"] is True
    assert body["validation"]["questions"] >= 30

    pathway_id = body["pathways"][0]["id"]
    detail = client.get(
        f"/api/admin/question-banks/{pathway_id}", headers=headers
    )
    assert detail.status_code == 200, detail.text
    detail_body = detail.json()
    assert detail_body["id"] == pathway_id
    assert detail_body["questions"]
    assert "correct" in detail_body["questions"][0]
    assert detail_body["validation"]["ok"] is True

    missing = client.get(
        "/api/admin/question-banks/not-a-pathway", headers=headers
    )
    assert missing.status_code == 404

    validated = client.post("/api/admin/question-banks/validate", headers=headers)
    assert validated.status_code == 200, validated.text
    assert validated.json()["ok"] is True
