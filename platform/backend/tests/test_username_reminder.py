"""Forgot-username flow: generic response, mail only to the account address."""
import uuid

import pytest

from app.auth import get_password_hash
from app.models import User
from app.services import mail

pytestmark = pytest.mark.db

PASSWORD = "Correct#Horse7Battery"


@pytest.fixture()
def reminder_user(db_session):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"reminder_{suffix}",
        email=f"reminder_{suffix}@university.edu",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.query(User).filter(User.id == user.id).delete()
    db_session.commit()


def test_forgot_username_emails_only_the_registered_address(
    client, reminder_user, monkeypatch
):
    sent = {}

    def fake_send(**kwargs):
        sent.update(kwargs)
        return True

    monkeypatch.setattr(mail, "send_username_reminder_email", fake_send)

    resp = client.post(
        "/api/auth/forgot-username",
        json={"email": reminder_user.email.upper()},
    )
    assert resp.status_code == 200, resp.text
    assert "If that email is registered" in resp.json()["message"]
    assert sent["to_email"] == reminder_user.email.lower()
    assert sent["usernames"] == [reminder_user.username]


def test_forgot_username_is_generic_for_unknown_address(client, db_schema, monkeypatch):
    called = {"value": False}

    def fake_send(**kwargs):
        called["value"] = True
        return True

    monkeypatch.setattr(mail, "send_username_reminder_email", fake_send)

    resp = client.post(
        "/api/auth/forgot-username",
        json={"email": "nobody-here@university.edu"},
    )
    assert resp.status_code == 200, resp.text
    assert "If that email is registered" in resp.json()["message"]
    assert called["value"] is False


def test_forgot_username_rejects_malformed_email(client, db_schema):
    resp = client.post("/api/auth/forgot-username", json={"email": "not-an-email"})
    assert resp.status_code == 422
