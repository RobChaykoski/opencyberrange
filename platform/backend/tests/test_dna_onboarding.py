"""The first-run DNA flow is for students, not instructors or admins."""

import uuid

from app.auth import get_password_hash
from app.models import User

PASSWORD = "Example-Only-Pass-123"


def _make_user(db_session, role: str) -> User:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"pytest_dna_{role}_{suffix}",
        email=f"pytest_dna_{role}_{suffix}@example.org",
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


def _login(client, user):
    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_student_without_completions_needs_discovery(client, db_session):
    user = _make_user(db_session, "student")
    headers = _login(client, user)

    resp = client.get("/api/auth/settings", headers=headers)

    assert resp.status_code == 200, resp.text
    assert resp.json()["needs_dna_onboarding"] is True


def test_instructor_never_needs_discovery(client, db_session):
    user = _make_user(db_session, "instructor")
    headers = _login(client, user)

    resp = client.get("/api/auth/settings", headers=headers)

    assert resp.status_code == 200, resp.text
    assert resp.json()["needs_dna_onboarding"] is False
