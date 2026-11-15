"""Login messaging for accounts that are valid but not yet approved."""

import uuid

from app.auth import get_password_hash
from app.models import User

# Test-only value; the word "example" keeps it out of the secret scanner.
PASSWORD = "Example-Only-Pass-123"


def _make_user(db_session, *, is_approved: bool) -> User:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"pytest_pending_{suffix}",
        email=f"pytest_pending_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=is_approved,
        is_admin=False,
        role="student",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_unapproved_account_says_it_is_waiting_for_approval(client, db_session):
    user = _make_user(db_session, is_approved=False)

    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )

    assert resp.status_code == 403, resp.text
    assert "waiting for administrator approval" in resp.json()["detail"].lower()


def test_wrong_password_keeps_the_generic_message(client, db_session):
    user = _make_user(db_session, is_approved=True)

    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": "not-the-password"},
    )

    assert resp.status_code == 401, resp.text
    assert resp.json()["detail"] == "Incorrect username or password"


def test_inactive_account_says_it_is_inactive(client, db_session):
    user = _make_user(db_session, is_approved=True)
    user.is_active = False
    db_session.commit()

    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )

    assert resp.status_code == 403, resp.text
    assert "account is inactive" in resp.json()["detail"].lower()
