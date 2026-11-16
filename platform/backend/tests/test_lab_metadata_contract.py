"""Static contract checks for the lab.yaml JSON Schema and validator."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "platform" / "backend" / "lab_metadata.schema.json"
LABS = REPO / "platform" / "labs"
VALIDATOR = REPO / "scripts" / "validate_lab_metadata.py"


def _validator() -> Draft202012Validator:
    return Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))


def _first_lab() -> dict:
    path = sorted(LABS.rglob("lab.yaml"))[0]
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_every_lab_matches_the_contract():
    validator = _validator()
    files = sorted(LABS.rglob("lab.yaml"))
    assert len(files) == 210
    failures = []
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(data), key=lambda item: list(item.path))
        if errors:
            failures.append((path, errors[0].message))
    assert not failures, failures[:5]


def test_unknown_top_level_key_is_rejected():
    lab = _first_lab()
    lab["titel"] = lab["title"]
    errors = list(_validator().iter_errors(lab))
    assert any("Additional properties" in error.message for error in errors)


def test_missing_required_field_is_rejected():
    lab = _first_lab()
    del lab["flag"]
    errors = list(_validator().iter_errors(lab))
    assert any(
        error.validator == "required" and "flag" in error.message for error in errors
    )


def test_invalid_enum_is_rejected():
    lab = _first_lab()
    lab["difficulty"] = "impossible"
    errors = list(_validator().iter_errors(lab))
    assert any("impossible" in error.message for error in errors)


def test_cli_fails_on_a_typo(tmp_path):
    lab = _first_lab()
    lab["titel"] = lab["title"]
    target = tmp_path / "Track" / "lab" / "lab.yaml"
    target.parent.mkdir(parents=True)
    target.write_text(yaml.safe_dump(lab, sort_keys=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--labs-dir",
            str(tmp_path),
            "--schema",
            str(SCHEMA),
            "--quiet",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 1
    assert "Additional properties" in result.stderr
