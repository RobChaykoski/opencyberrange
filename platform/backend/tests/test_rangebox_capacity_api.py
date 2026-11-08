"""Admin RangeBox capacity policy API."""

import uuid

from app.auth import get_password_hash
from app.models import User

PASSWORD = "Admin#Pass123"


def _make_admin(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    admin = User(
        username=f"capacity_admin_{suffix}",
        email=f"capacity_admin_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=True,
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    resp = client.post(
        "/api/auth/login",
        data={"username": admin.username, "password": PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return admin, {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_capacity_endpoint_reports_the_percentage_policy(
    client, db_session, monkeypatch
):
    from app.routers import admin as admin_router
    from app.services import rangebox_capacity

    _admin, headers = _make_admin(client, db_session)
    monkeypatch.setattr(
        admin_router.docker_manager, "_computed_rangebox_max", lambda: 27
    )
    monkeypatch.setattr(
        admin_router.docker_manager, "_count_running_rangeboxes", lambda: 3
    )
    monkeypatch.setattr(
        admin_router.docker_manager, "has_rangebox_memory_headroom", lambda: True
    )
    monkeypatch.setattr(
        admin_router.docker_manager, "has_rangebox_disk_headroom", lambda: True
    )
    monkeypatch.setattr(
        admin_router.docker_manager, "_rangebox_capacity_percent", lambda: 75
    )
    monkeypatch.setattr(
        admin_router.docker_manager, "_rangebox_stress_max", lambda: 24
    )
    monkeypatch.setattr(
        rangebox_capacity, "get_capacity_percent", lambda db=None: 75
    )
    monkeypatch.setattr(
        rangebox_capacity, "get_capacity_policy", lambda db=None: (75, 24)
    )

    resp = client.get("/api/admin/rangebox-capacity", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["computed_max"] == 27
    assert body["stress_max"] == 24
    assert body["percent"] == 75
    assert body["effective_max"] == 18
    assert body["running"] == 3
    assert body["available"] is True


def test_capacity_percentage_rejects_values_outside_the_range(
    client, db_session
):
    _admin, headers = _make_admin(client, db_session)

    resp = client.put(
        "/api/settings/",
        json={"settings": {"rangebox_capacity_percent": "5"}},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "between 10 and 100" in resp.json()["detail"]


def test_capacity_percentage_accepts_a_valid_value(client, db_session):
    _admin, headers = _make_admin(client, db_session)

    resp = client.put(
        "/api/settings/",
        json={"settings": {"rangebox_capacity_percent": "60"}},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["count"] == 1
