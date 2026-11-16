"""Grades 9-12 labs are offline, fictional, and free of live targets."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/check-minor-safe.py"
BACKEND = ROOT / "platform/backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

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


def test_minor_safe_defaults_and_high_school_wiki_scope():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: offline, fictional, no live targets, and High School wiki scope" in result.stdout
