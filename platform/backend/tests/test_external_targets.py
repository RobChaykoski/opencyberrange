"""Live OSINT targets have reviewed offline mirrors and content hashes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/check-external-targets.py"
INVENTORY = ROOT / "platform/backend/app/data/external-targets.yaml"


def test_offline_mirrors_match_recorded_hashes():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--offline"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_every_target_has_a_mirror_and_no_personal_data():
    document = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
    targets = document.get("targets") or []
    assert targets
    for target in targets:
        assert target["pii"] == "none"
        assert target["offline_mirror"]
        assert (ROOT / target["offline_mirror"]).is_file()
        assert len(target["offline_mirror_sha256"]) == 64
        assert target["audience"] in {"adult", "all"}
