"""Admin user APIs expose the fields the users table now displays."""

import uuid

from app.auth import get_password_hash
from app.models import User

PASSWORD = "Admin#Pass123"


def _make_admin(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    admin = User(
        username=f"pytest_admin_{suffix}",
        email=f"pytest_admin_{suffix}@example.org",
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


def test_admin_user_list_includes_last_sign_in(client, db_session, monkeypatch):
    from app.routers import admin as admin_router

    monkeypatch.setattr(admin_router.wireguard_manager, "list_peers", lambda: None)
    admin, headers = _make_admin(client, db_session)

    resp = client.get("/api/admin/users", headers=headers)

    assert resp.status_code == 200, resp.text
    row = next(user for user in resp.json() if user["id"] == admin.id)
    assert row["last_login_at"] is not None
    assert row["role"] == "admin"
    assert row["is_locked"] is False
    assert row["vpn_registered"] is False


def test_admin_user_detail_includes_last_sign_in(client, db_session):
    admin, headers = _make_admin(client, db_session)

    resp = client.get(f"/api/admin/users/{admin.id}/details", headers=headers)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["last_login_at"] is not None
    assert body["role"] == "admin"
