"""Every lab exposes measurable skills, competencies, domains, evidence, and confidence."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "platform/backend/app/data"
OUTCOMES = DATA / "lab-outcomes.yaml"
TAXONOMY = DATA / "competency-taxonomy.yaml"
LABS = ROOT / "platform/labs"


def _outcomes() -> dict:
    return yaml.safe_load(OUTCOMES.read_text(encoding="utf-8")) or {}


def _taxonomy() -> dict[str, dict]:
    document = yaml.safe_load(TAXONOMY.read_text(encoding="utf-8")) or {}
    result = {}
    for domain in document.get("domains", []):
        for category in domain.get("categories", []):
            for competency in category.get("competencies", []):
                result[str(competency["id"])] = {
                    "domain": str(domain["id"]),
                    "category": str(category["id"]),
                }
    return result


def test_every_lab_has_a_complete_outcome_contract():
    document = _outcomes()
    labs = document.get("labs") or {}
    slugs = {path.parent.name for path in LABS.rglob("lab.yaml")}
    assert set(labs) == slugs
    assert len(labs) == 210
    for slug, entry in labs.items():
        assert entry["track"], slug
        assert entry["difficulty"] in {"beginner", "intermediate", "advanced", "expert", "unknown"}
        assert entry["expected_duration_minutes"] > 0, slug
        assert entry["skills_earned"], slug
        assert entry["competencies_proven"], slug
        assert entry["knowledge_domains"], slug
        assert entry["evidence_artifacts"], slug
        assert set(entry["evidence_artifacts"]) >= {
            "flag",
            "automated validation",
            "analyst finding",
            "submitted artifact",
        }, slug
        confidence = entry["confidence"]
        assert 0 <= confidence["score"] <= 1, slug
        assert confidence["level"] in {"high", "medium", "low"}, slug
        assert confidence["basis"].strip(), slug


def test_competencies_resolve_to_the_taxonomy_and_weights_sum_to_one():
    taxonomy = _taxonomy()
    for slug, entry in (_outcomes().get("labs") or {}).items():
        total = 0.0
        for competency in entry["competencies_proven"]:
            assert competency["id"] in taxonomy, (slug, competency["id"])
            assert competency["name"].strip(), (slug, competency["id"])
            total += float(competency["weight"])
        assert abs(total - 1.0) < 1e-6, (slug, total)


def test_generated_file_is_current():
    result = subprocess.run(
        [sys.executable, "scripts/generate-lab-outcomes.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
