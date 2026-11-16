"""Grades 9-12 labs are offline, fictional, and free of live targets."""

from __future__ import annotations

import subprocess
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/check-minor-safe.py"
BACKEND = ROOT / "platform/backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.models import Lab  # noqa: E402
from app.routers.curriculum import _is_lab_visible  # noqa: E402


def test_under_18_learner_does_not_see_osint_labs():
    lab = SimpleNamespace(
        category="osint",
        visibility="public",
        is_active=True,
        created_by=None,
        id=1,
    )
    minor = SimpleNamespace(role="student", is_minor=True, id=7)
    adult = SimpleNamespace(role="student", is_minor=False, id=8)
    assert _is_lab_visible(lab, minor, set()) is False
    assert _is_lab_visible(lab, adult, set()) is True


def test_minor_does_not_enumerate_or_spawn_osint_labs(
    client, test_user, test_password, db_session
):
    suffix = uuid.uuid4().hex[:8]
    lab = Lab(
        name=f"OSINT test {suffix}",
        slug=f"osint-2-2-test-{suffix}",
        description="Test-only OSINT lab",
        scenario="fictional",
        difficulty="beginner",
        category="osint",
        compose_file="services: {}",
        visibility="public",
        is_active=True,
    )
    db_session.add(lab)
    db_session.commit()
    db_session.refresh(lab)
    try:
        test_user.is_minor = True
        db_session.commit()
        login = client.post(
            "/api/auth/login",
            data={"username": test_user.username, "password": test_password},
        )
        assert login.status_code == 200, login.text
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        visible = client.get("/api/labs/", headers=headers).json()["labs"]
        assert lab.slug not in {item["slug"] for item in visible}
        spawn = client.post(f"/api/labs/spawn/{lab.slug}", headers=headers)
        assert spawn.status_code == 404

        test_user.is_minor = False
        db_session.commit()
        visible = client.get("/api/labs/", headers=headers).json()["labs"]
        assert lab.slug in {item["slug"] for item in visible}
    finally:
        db_session.delete(lab)
        db_session.commit()


def test_minor_safe_defaults_and_high_school_wiki_scope():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: offline, fictional, no live targets, and High School wiki scope" in result.stdout
