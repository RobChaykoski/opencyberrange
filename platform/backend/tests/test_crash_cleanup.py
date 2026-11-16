"""Crash-recovery cleanup for orphaned lab containers and images.

A kill -9 mid-spawn leaves containers and networks with no matching running
session. The admin cleanup path must remove the orphans while preserving the
containers owned by a live session. Docker is faked here; the live script is
`scripts/verify-crash-cleanup.sh`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models import LabSession, User
from app.services.docker_manager import DockerManager

pytestmark = pytest.mark.db


class _FakeContainer:
    def __init__(self, name, *, age_minutes=60, status="exited"):
        created = datetime.now(timezone.utc) - timedelta(minutes=age_minutes)
        self.name = name
        self.attrs = {
            "Created": created.isoformat().replace("+00:00", "Z"),
            "State": {"Status": status},
        }
        self.removed = False

    def remove(self, force=False):
        self.removed = force


class _FakeContainers:
    def __init__(self, rows):
        self.rows = rows

    def list(self, all=True):
        return self.rows


class _FakeImages:
    def __init__(self):
        self.pruned = 0

    def prune(self, filters=None):
        self.pruned += 1
        return {"ImagesDeleted": [{"Untagged": "repo:tag"}], "SpaceReclaimed": 1024}


class _FakeDocker:
    def __init__(self, containers):
        self.containers = _FakeContainers(containers)
        self.images = _FakeImages()


def _manager(containers):
    manager = DockerManager.__new__(DockerManager)
    manager.client = _FakeDocker(containers)
    return manager


def _user(db):
    suffix = uuid.uuid4().hex[:8]
    row = User(
        username=f"crash_{suffix}",
        email=f"crash_{suffix}@example.org",
        hashed_password="unused",
        is_active=True,
        is_approved=True,
        role="student",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@pytest.fixture
def live_session(db_session, test_lab):
    owner = _user(db_session)
    now = datetime.now(timezone.utc)
    session = LabSession(
        user_id=owner.id,
        lab_id=test_lab.id,
        status="running",
        started_at=now,
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    db_session.commit()
    yield owner, test_lab, session
    db_session.query(LabSession).filter(LabSession.id == session.id).delete()
    db_session.commit()


def test_orphaned_container_is_removed_and_live_session_is_preserved(live_session):
    owner, lab, _session = live_session
    live_name = f"lab_{owner.id}_{lab.slug}-target-1"
    live = _FakeContainer(live_name, age_minutes=120, status="running")
    orphan = _FakeContainer("lab_999999_missing-lab-target-1", age_minutes=120)
    stopped_old = _FakeContainer("lab_888888_old-lab-target-1", age_minutes=90, status="exited")
    too_new = _FakeContainer("lab_777777_new-lab-target-1", age_minutes=2, status="exited")
    platform = _FakeContainer("ocr-backend", age_minutes=600, status="running")

    manager = _manager([live, orphan, stopped_old, too_new, platform])
    removed = manager.cleanup_orphaned_containers()

    assert removed == 2
    assert live.removed is False
    assert too_new.removed is False
    assert platform.removed is False
    assert orphan.removed is True
    assert stopped_old.removed is True


def test_image_prune_reports_reclaimed_space():
    manager = _manager([])
    result = manager.prune_all_images()
    assert result["images_removed"] == 1
    assert result["bytes_freed"] == 1024
    assert manager.client.images.pruned == 1
