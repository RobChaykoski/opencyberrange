"""Portable user export/import through the admin API."""

import uuid

from app.auth import get_password_hash, verify_password
from app.models import User

PASSWORD = "Admin#Pass123"
IMPORT_PASSWORD = "Imported#Pass9"


def _make_admin(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    admin = User(
        username=f"pytest_transfer_admin_{suffix}",
        email=f"pytest_transfer_admin_{suffix}@example.org",
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


def _payload(*users):
    return {
        "format": "opencyberrange-users",
        "version": 1,
        "users": list(users),
    }


def test_export_returns_portable_fields(client, db_session):
    admin, headers = _make_admin(client, db_session)

    resp = client.get(
        "/api/admin/users/export?reason=pytest-migration", headers=headers
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["format"] == "opencyberrange-users"
    assert body["version"] == 1
    assert body["reason"] == "pytest-migration"
    assert body["exported_by"] == admin.username
    assert body["user_count"] == len(body["users"])
    exported = next(user for user in body["users"] if user["username"] == admin.username)
    assert exported["email"] == admin.email
    assert exported["password_hash"].startswith(("$argon2", "$2"))
    assert "totp_secret" not in exported
    assert "mfa_recovery_codes" not in exported
    assert "vpn_registered" not in exported


def test_export_requires_a_reason(client, db_session):
    _, headers = _make_admin(client, db_session)

    missing = client.get("/api/admin/users/export", headers=headers)
    assert missing.status_code == 422

    blank = client.get("/api/admin/users/export?reason=+++++", headers=headers)
    assert blank.status_code == 400
    assert "reason" in blank.json()["detail"].lower()


def test_import_preview_does_not_write_then_import_logs_in(client, db_session):
    admin, headers = _make_admin(client, db_session)
    suffix = uuid.uuid4().hex[:10]
    username = f"pytest_transfer_{suffix}"
    email = f"{username}@university.edu"
    payload = _payload({
        "username": username,
        "email": email,
        "password_hash": get_password_hash(IMPORT_PASSWORD),
        "first_name": "Imported",
        "last_name": "Student",
        "role": "student",
        "is_admin": False,
        "is_active": True,
        "is_approved": True,
    })

    preview = client.post(
        "/api/admin/users/import",
        json={"payload": payload, "dry_run": True},
        headers=headers,
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["created"] == 1
    assert preview.json()["dry_run"] is True
    db_session.expire_all()
    assert db_session.query(User).filter(User.username == username).first() is None

    imported = client.post(
        "/api/admin/users/import",
        json={"payload": payload, "dry_run": False},
        headers=headers,
    )
    assert imported.status_code == 200, imported.text
    assert imported.json()["created"] == 1

    db_session.expire_all()
    created = db_session.query(User).filter(User.username == username).one()
    assert created.first_name == "Imported"
    assert verify_password(IMPORT_PASSWORD, created.hashed_password)

    login = client.post(
        "/api/auth/login",
        data={"username": username, "password": IMPORT_PASSWORD},
    )
    assert login.status_code == 200, login.text

    db_session.query(User).filter(User.id == created.id).delete()
    db_session.commit()


def test_import_update_refreshes_existing_profile(client, db_session, test_user):
    _, headers = _make_admin(client, db_session)
    payload = _payload({
        "username": test_user.username,
        "email": test_user.email,
        "password_hash": test_user.hashed_password,
        "first_name": "Updated",
        "last_name": "Name",
        "role": "student",
        "is_admin": False,
        "is_active": True,
        "is_approved": True,
    })

    skipped = client.post(
        "/api/admin/users/import",
        json={"payload": payload},
        headers=headers,
    )
    assert skipped.status_code == 200, skipped.text
    assert skipped.json()["skipped"] == 1

    updated = client.post(
        "/api/admin/users/import",
        json={"payload": payload, "update": True},
        headers=headers,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["updated"] == 1

    db_session.expire_all()
    refreshed = db_session.query(User).filter(User.id == test_user.id).one()
    assert refreshed.first_name == "Updated"
    assert refreshed.last_name == "Name"


def test_import_never_overwrites_signed_in_admin(client, db_session):
    admin, headers = _make_admin(client, db_session)
    payload = _payload({
        "username": admin.username,
        "email": admin.email,
        "password_hash": get_password_hash("Hacked#Pass9"),
        "first_name": "Overwritten",
        "role": "student",
        "is_admin": False,
        "is_active": True,
        "is_approved": True,
    })

    resp = client.post(
        "/api/admin/users/import",
        json={"payload": payload, "update": True},
        headers=headers,
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["skipped"] == 1
    assert resp.json()["updated"] == 0
    assert any("protected" in warning for warning in resp.json()["warnings"])

    db_session.expire_all()
    refreshed = db_session.query(User).filter(User.id == admin.id).one()
    assert refreshed.first_name != "Overwritten"
    assert refreshed.role == "admin"
    assert verify_password(PASSWORD, refreshed.hashed_password)


def test_import_never_overwrites_another_admin(client, db_session):
    _, headers = _make_admin(client, db_session)
    suffix = uuid.uuid4().hex[:8]
    other = User(
        username=f"pytest_other_admin_{suffix}",
        email=f"pytest_other_admin_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=True,
        role="admin",
        first_name="Original",
    )
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)

    payload = _payload({
        "username": other.username,
        "email": other.email,
        "password_hash": get_password_hash("Hacked#Pass9"),
        "first_name": "Overwritten",
        "role": "student",
        "is_admin": False,
        "is_active": True,
        "is_approved": True,
    })

    resp = client.post(
        "/api/admin/users/import",
        json={"payload": payload, "update": True},
        headers=headers,
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["skipped"] == 1
    db_session.expire_all()
    refreshed = db_session.query(User).filter(User.id == other.id).one()
    assert refreshed.first_name == "Original"
    assert refreshed.role == "admin"
    assert verify_password(PASSWORD, refreshed.hashed_password)

    db_session.query(User).filter(User.id == other.id).delete()
    db_session.commit()


def test_import_rejects_unknown_format(client, db_session):
    _, headers = _make_admin(client, db_session)

    resp = client.post(
        "/api/admin/users/import",
        json={"payload": {"format": "something-else", "users": []}},
        headers=headers,
    )

    assert resp.status_code == 400
    assert "unrecognised export format" in resp.json()["detail"]


def test_upload_snapshot_can_be_staged_without_restoring(
    client, db_session, tmp_path, monkeypatch
):
    _, headers = _make_admin(client, db_session)
    monkeypatch.setenv("OCR_BACKUP_DIR", str(tmp_path))

    resp = client.post(
        "/api/admin/system/restore/upload",
        files={"file": ("another-system.sql", b"SELECT 1;\n", "application/sql")},
        data={"restore_now": "false"},
        headers=headers,
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["restored"] is False
    assert body["size_bytes"] > 0
    assert (tmp_path / body["filename"]).exists()


def test_upload_snapshot_rejects_non_sql_files(client, db_session, tmp_path, monkeypatch):
    _, headers = _make_admin(client, db_session)
    monkeypatch.setenv("OCR_BACKUP_DIR", str(tmp_path))

    resp = client.post(
        "/api/admin/system/restore/upload",
        files={"file": ("another-system.dump", b"PGDMP", "application/octet-stream")},
        data={"restore_now": "false"},
        headers=headers,
    )

    assert resp.status_code == 400
    assert ".sql" in resp.json()["detail"]
