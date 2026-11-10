"""The About inventory mixes release artefacts with live runtime values."""

import uuid

import pytest

from app.auth import get_password_hash
from app.models import User
from app.version import APP_VERSION

PASSWORD = "About#Pass123"
pytestmark = pytest.mark.db


def _user(db_session) -> User:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"about_{suffix}",
        email=f"about_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _headers(client, user: User) -> dict:
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_about_reports_live_build_and_runtime(client, db_session):
    response = client.get("/api/about", headers=_headers(client, _user(db_session)))

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["version"] == APP_VERSION
    assert data["platform"]["version"] == APP_VERSION
    assert data["build"]["version"] == APP_VERSION
    assert data["runtime"]["python"]
    assert "schema_revision" in data["runtime"]
    assert "labs" in data["content"]
    assert data["integrity"]["status"] in {
        "ok",
        "warning",
        "error",
        "unavailable",
    }
