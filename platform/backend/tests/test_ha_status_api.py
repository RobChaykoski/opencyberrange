"""The HA status endpoint is admin-only and reads the host snapshot."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from app.auth import get_password_hash
from app.models import User
from app.services import ha_status

# Test-only fixture credential; never used outside the pytest database.
# security-delta: allow credential-like assignment
PASSWORD = "Admin#Pass123"


def _make_admin(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    admin = User(
        username=f"pytest_ha_admin_{suffix}",
        email=f"pytest_ha_admin_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=True,
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    response = client.post(
        "/api/auth/login",
        data={"username": admin.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return admin, {"Authorization": f"Bearer {response.json()['access_token']}"}


def _write_snapshot(tmp_path, monkeypatch):
    checked_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    role_path = tmp_path / "role"
    role_path.write_text("standby", encoding="utf-8")
    status_path = tmp_path / "status.json"
    status_path.write_text(
        json.dumps(
            {
                "checked_at": checked_at,
                "preferred": "prod",
                "replication": {
                    "state": "streaming",
                    "lag_bytes": 0,
                    "last_replay": "0/1",
                },
                "redis": {"master": "up", "sentinels": "2/2"},
                "witness": {
                    "last_contact": checked_at,
                    "prod": "up",
                    "dev": "up",
                },
                "last_failover": None,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("OCR_HA_STATUS_PATH", str(status_path))
    monkeypatch.setenv("OCR_HA_ROLE_PATH", str(role_path))
    ha_status.reset_cache()


def test_student_cannot_read_ha_status(client, auth_headers):
    response = client.get("/api/admin/system/ha", headers=auth_headers)

    assert response.status_code == 403


def test_admin_without_a_snapshot_gets_available_false(
    client, db_session, tmp_path, monkeypatch
):
    monkeypatch.setenv("OCR_HA_STATUS_PATH", str(tmp_path / "missing.json"))
    monkeypatch.setenv("OCR_HA_ROLE_PATH", str(tmp_path / "missing-role"))
    ha_status.reset_cache()
    _, headers = _make_admin(client, db_session)

    response = client.get("/api/admin/system/ha", headers=headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["available"] is False
    assert body["verdict"] == "unknown"


def test_admin_reads_the_sanitised_snapshot(
    client, db_session, tmp_path, monkeypatch
):
    _write_snapshot(tmp_path, monkeypatch)
    _, headers = _make_admin(client, db_session)

    response = client.get("/api/admin/system/ha", headers=headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["available"] is True
    assert body["verdict"] == "ok"
    assert body["role"] == "standby"
    assert body["preferred"] == "prod"
    assert "path" not in body
