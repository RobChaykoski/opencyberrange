"""Optional module status API exposed to the sidebar."""

import uuid

import pytest

from app.auth import get_password_hash
from app.models import User

# Test-only login credential; security-delta: allow credential-like assignment
PASSWORD = "Modules#Pass123"
pytestmark = pytest.mark.db


def _make_user(db_session):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"modules_student_{suffix}",
        email=f"modules_student_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
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


def test_modules_requires_authentication(client):
    assert client.get("/api/modules/").status_code == 401


def test_modules_status_shape_and_dev_tool_gate(client, db_session, monkeypatch):
    user = _make_user(db_session)
    headers = _headers(client, user)

    monkeypatch.setenv("OCR_DEV_TOOLS", "1")
    enabled = client.get("/api/modules/", headers=headers)
    assert enabled.status_code == 200, enabled.text
    body = enabled.json()
    assert body["dev_tools"] is True
    assert isinstance(body["modules"], dict)
    for module in body["modules"].values():
        assert isinstance(module["enabled"], bool)
        assert module["label"]
        assert module["description"]
    assert isinstance(body["exercise_tester"], bool)
    assert isinstance(body["stress_tester"], bool)
    assert isinstance(body["exercise_authoring"], bool)

    monkeypatch.setenv("OCR_DEV_TOOLS", "0")
    disabled = client.get("/api/modules/", headers=headers)
    assert disabled.status_code == 200, disabled.text
    body = disabled.json()
    assert body["dev_tools"] is False
    assert body["exercise_tester"] is False
    assert body["stress_tester"] is False
    assert body["exercise_authoring"] is False
