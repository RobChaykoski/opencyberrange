"""Admin curriculum APIs: track/level CRUD, ordering, and cascade behavior."""

import uuid

import pytest

from app.auth import get_password_hash
from app.models import Lab, User

# Test-only login credential; security-delta: allow credential-like assignment
PASSWORD = "Curriculum#Pass123"
pytestmark = pytest.mark.db


def _make_user(db_session, role="admin"):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"curriculum_{role}_{suffix}",
        email=f"curriculum_{role}_{suffix}@example.org",
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


def _track_payload(suffix):
    return {
        "name": f"Curriculum Track {suffix}",
        "slug": f"curriculum-{suffix}",
        "description": "Track used by the curriculum admin tests",
        "icon": "web",
        "color": "#3b82f6",
    }


def _create_track(client, headers, suffix):
    response = client.post(
        "/api/admin/curriculum/tracks",
        json=_track_payload(suffix),
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_curriculum_admin_requires_admin(client, db_session):
    student = _make_user(db_session, "student")
    headers = _headers(client, student)

    unauthenticated = client.get("/api/admin/curriculum/tracks")
    assert unauthenticated.status_code == 401

    denied = client.get("/api/admin/curriculum/tracks", headers=headers)
    assert denied.status_code == 403

    denied_write = client.post(
        "/api/admin/curriculum/tracks",
        json=_track_payload(uuid.uuid4().hex[:8]),
        headers=headers,
    )
    assert denied_write.status_code == 403


def test_track_and_level_lifecycle(client, db_session):
    admin = _make_user(db_session)
    headers = _headers(client, admin)
    suffix = uuid.uuid4().hex[:8]
    track_id = _create_track(client, headers, suffix)

    duplicate = client.post(
        "/api/admin/curriculum/tracks",
        json=_track_payload(suffix),
        headers=headers,
    )
    assert duplicate.status_code == 400
    assert "already exists" in duplicate.json()["detail"]

    created_level = client.post(
        f"/api/admin/curriculum/tracks/{track_id}/levels",
        json={"name": "Foundations", "description": "First level"},
        headers=headers,
    )
    assert created_level.status_code == 200, created_level.text
    level_id = created_level.json()["id"]
    assert created_level.json()["level_number"] == 1

    second_level = client.post(
        f"/api/admin/curriculum/tracks/{track_id}/levels",
        json={"name": "Applied", "description": "Second level"},
        headers=headers,
    )
    assert second_level.status_code == 200, second_level.text
    second_level_id = second_level.json()["id"]
    assert second_level.json()["level_number"] == 2

    lab = Lab(
        name=f"Curriculum Lab {suffix}",
        slug=f"curriculum-lab-{suffix}",
        description="Assigned to the first level",
        compose_file="services: {}\n",
        is_active=True,
        visibility="public",
        level_id=level_id,
        duration_minutes=30,
        difficulty="beginner",
    )
    db_session.add(lab)
    db_session.commit()
    db_session.refresh(lab)

    listing = client.get("/api/admin/curriculum/tracks", headers=headers)
    assert listing.status_code == 200, listing.text
    row = next(item for item in listing.json() if item["id"] == track_id)
    assert row["level_count"] == 2
    assert row["lab_count"] == 1
    first = next(level for level in row["levels"] if level["id"] == level_id)
    assert first["lab_count"] == 1

    updated = client.put(
        f"/api/admin/curriculum/tracks/{track_id}",
        json={"name": "Renamed Track", "is_active": False},
        headers=headers,
    )
    assert updated.status_code == 200, updated.text

    renamed_level = client.put(
        f"/api/admin/curriculum/levels/{level_id}",
        json={"name": "Renamed Level", "description": "Updated"},
        headers=headers,
    )
    assert renamed_level.status_code == 200, renamed_level.text

    reordered = client.put(
        f"/api/admin/curriculum/tracks/{track_id}/levels/reorder",
        json={"ordered_ids": [second_level_id, level_id]},
        headers=headers,
    )
    assert reordered.status_code == 200, reordered.text

    listing = client.get("/api/admin/curriculum/tracks", headers=headers).json()
    row = next(item for item in listing if item["id"] == track_id)
    assert row["name"] == "Renamed Track"
    assert row["is_active"] is False
    ordered = sorted(row["levels"], key=lambda level: level["level_number"])
    assert [level["id"] for level in ordered] == [second_level_id, level_id]
    assert [level["level_number"] for level in ordered] == [1, 2]

    blocked = client.delete(
        f"/api/admin/curriculum/levels/{level_id}", headers=headers
    )
    assert blocked.status_code == 400
    assert "assigned labs" in blocked.json()["detail"]

    deleted_level = client.delete(
        f"/api/admin/curriculum/levels/{second_level_id}", headers=headers
    )
    assert deleted_level.status_code == 200, deleted_level.text

    deleted_track = client.delete(
        f"/api/admin/curriculum/tracks/{track_id}", headers=headers
    )
    assert deleted_track.status_code == 200, deleted_track.text
    assert "1 levels deleted" in deleted_track.json()["message"]

    details = client.get(f"/api/admin/labs/{lab.id}/details", headers=headers)
    assert details.status_code == 200, details.text
    assert details.json()["level_id"] is None


def test_level_reorder_handles_swaps_and_partial_lists(client, db_session):
    admin = _make_user(db_session)
    headers = _headers(client, admin)
    track_id = _create_track(client, headers, uuid.uuid4().hex[:8])

    level_ids = []
    for name in ("One", "Two", "Three"):
        created = client.post(
            f"/api/admin/curriculum/tracks/{track_id}/levels",
            json={"name": name},
            headers=headers,
        )
        assert created.status_code == 200, created.text
        level_ids.append(created.json()["id"])

    reordered = client.put(
        f"/api/admin/curriculum/tracks/{track_id}/levels/reorder",
        json={"ordered_ids": [level_ids[2], level_ids[0]]},
        headers=headers,
    )
    assert reordered.status_code == 200, reordered.text

    listing = client.get("/api/admin/curriculum/tracks", headers=headers).json()
    row = next(item for item in listing if item["id"] == track_id)
    ordered = sorted(row["levels"], key=lambda level: level["level_number"])
    assert [level["id"] for level in ordered] == [
        level_ids[2],
        level_ids[0],
        level_ids[1],
    ]
    assert [level["level_number"] for level in ordered] == [1, 2, 3]


def test_track_reorder_and_missing_ids(client, db_session):
    admin = _make_user(db_session)
    headers = _headers(client, admin)
    suffix = uuid.uuid4().hex[:8]
    first_id = _create_track(client, headers, f"{suffix}a")
    second_id = _create_track(client, headers, f"{suffix}b")

    reordered = client.put(
        "/api/admin/curriculum/tracks/reorder",
        json={"ordered_ids": [second_id, first_id]},
        headers=headers,
    )
    assert reordered.status_code == 200, reordered.text

    listing = client.get("/api/admin/curriculum/tracks", headers=headers).json()
    ids = [row["id"] for row in listing]
    assert ids.index(second_id) < ids.index(first_id)

    missing_update = client.put(
        "/api/admin/curriculum/tracks/99999999",
        json={"name": "Missing Track"},
        headers=headers,
    )
    assert missing_update.status_code == 404

    missing_level = client.put(
        "/api/admin/curriculum/levels/99999999",
        json={"name": "Missing Level"},
        headers=headers,
    )
    assert missing_level.status_code == 404

    missing_delete = client.delete(
        "/api/admin/curriculum/levels/99999999", headers=headers
    )
    assert missing_delete.status_code == 404

    unknown_level = client.put(
        f"/api/admin/curriculum/tracks/{first_id}/levels/reorder",
        json={"ordered_ids": [99999999]},
        headers=headers,
    )
    assert unknown_level.status_code == 200

def test_admin_labs_include_review_status(client, db_session, test_lab):
    """The exercises table can show contract review state without a second call."""
    admin = _make_user(db_session)
    headers = _headers(client, admin)
    response = client.get("/api/admin/labs", headers=headers)
    assert response.status_code == 200, response.text
    row = next(item for item in response.json() if item["id"] == test_lab.id)
    assert row["review_status"] in {
        "reviewed",
        "pathway_implementation",
        "baseline_derived",
        "pending",
        "unmapped",
    }
    assert "content_version" in row
    assert isinstance(row["has_flag"], bool)
