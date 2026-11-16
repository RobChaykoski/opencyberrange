"""Runtime software-integrity hashing and failure reporting."""

from __future__ import annotations

import json
from pathlib import Path

from app.services import software_integrity


def _lab(root: Path, slug: str = "lab-one") -> Path:
    lab = root / slug
    (lab / "containers" / "evidence" / "app").mkdir(parents=True)
    (lab / "containers" / "evidence" / "data").mkdir(parents=True)
    (lab / "containers" / "evidence" / "logs").mkdir(parents=True)
    (lab / "containers" / "helper").mkdir(parents=True)
    (lab / "lab.yaml").write_text("name: test\n", encoding="utf-8")
    (lab / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
    (lab / "README.md").write_text("reviewed content\n", encoding="utf-8")
    (lab / "containers" / "evidence" / "app" / "runtime.py").write_text(
        "generated\n", encoding="utf-8"
    )
    (lab / "containers" / "evidence" / "data" / "state.db").write_text(
        "generated\n", encoding="utf-8"
    )
    (lab / "containers" / "evidence" / "logs" / "run.log").write_text(
        "generated\n", encoding="utf-8"
    )
    (lab / "containers" / "helper" / "docker-compose.yml").write_text(
        "services: {}\n", encoding="utf-8"
    )
    return lab


def test_content_hash_ignores_runtime_directories(tmp_path):
    lab = _lab(tmp_path)
    before = software_integrity.content_hash(lab)

    (lab / "containers" / "evidence" / "app" / "runtime.py").write_text(
        "changed\n", encoding="utf-8"
    )
    assert software_integrity.content_hash(lab) == before

    (lab / "README.md").write_text("changed\n", encoding="utf-8")
    assert software_integrity.content_hash(lab) != before


def test_verify_uses_lab_yaml_and_ignores_nested_compose(tmp_path, monkeypatch):
    lab = _lab(tmp_path)
    manifest = {
        "release": "test",
        "labs": {"lab-one": software_integrity.content_hash(lab)},
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(software_integrity, "MANIFEST_PATH", manifest_path)

    result = software_integrity.verify(str(tmp_path))

    assert result["ok"] is True
    assert result["extra"] == []
    assert result["checked"] == 1


def test_verify_reports_unreadable_lab_instead_of_raising(tmp_path, monkeypatch):
    _lab(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps({"release": "test", "labs": {"lab-one": "expected"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(software_integrity, "MANIFEST_PATH", manifest_path)

    def denied(_path):
        raise PermissionError("permission denied")

    monkeypatch.setattr(software_integrity, "content_hash", denied)

    result = software_integrity.verify(str(tmp_path))

    assert result["ok"] is False
    assert result["unreadable"][0]["slug"] == "lab-one"
    assert result["missing"] == []


def test_verify_reports_missing_and_extra_labs(tmp_path, monkeypatch):
    lab = _lab(tmp_path, "lab-one")
    _lab(tmp_path, "lab-extra")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "release": "test",
                "labs": {"lab-one": software_integrity.content_hash(lab), "lab-missing": "x"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(software_integrity, "MANIFEST_PATH", manifest_path)

    result = software_integrity.verify(str(tmp_path))

    assert result["ok"] is False
    assert result["missing"] == ["lab-missing"]
    assert result["extra"] == ["lab-extra"]
