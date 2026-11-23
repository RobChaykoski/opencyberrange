"""The DFIR pathway resolves to reviewed evidence and requires a report."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "platform/backend/app/data"
PATHWAY = DATA / "dfir-pathway.yaml"
DATASETS = DATA / "dfir-datasets"
TAXONOMY = DATA / "competency-taxonomy.yaml"
LABS = ROOT / "platform/labs"

REQUIRED_MODULES = [f"DFIR-{index:02d}" for index in range(1, 14)]
REPORT_SECTIONS = [
    "Short finding",
    "Evidence and custody",
    "Method",
    "Findings",
    "Timeline",
    "Response recommendations",
    "Lessons learned",
    "Reviewer sign-off",
]


def _pathway() -> dict:
    return yaml.safe_load(PATHWAY.read_text(encoding="utf-8"))


def _taxonomy_ids() -> set[str]:
    taxonomy = yaml.safe_load(TAXONOMY.read_text(encoding="utf-8"))
    return {
        competency["id"]
        for domain in taxonomy["domains"]
        for category in domain.get("categories", [])
        for competency in category.get("competencies", [])
    }


def _lab_slugs() -> set[str]:
    return {path.parent.name for path in LABS.rglob("lab.yaml") if path.is_file()}


def test_pathway_is_a_complete_ordered_progression():
    pathway = _pathway()
    modules = pathway["modules"]
    assert [module["id"] for module in modules] == REQUIRED_MODULES
    seen: set[str] = set()
    for module in modules:
        assert module["title"].strip()
        assert module["estimated_minutes"] > 0
        assert module["outcomes"]
        assert module["evidence"]
        assert module["report_required"] is True
        assert module["analyst_finding_required"] is True
        assert "analyst_report" in module["evidence"]
        assert (
            "evidence_artifact" in module["evidence"]
            or "hashed_acquisition_record" in module["evidence"]
            or "timeline" in module["evidence"]
        )
        assert abs(sum(item["weight"] for item in module["competencies"]) - 1.0) < 1e-9
        for prerequisite in module["prerequisites"]:
            assert prerequisite in seen, (module["id"], prerequisite)
        seen.add(module["id"])


def test_assessment_policy_requires_more_than_a_flag():
    pathway = _pathway()
    policy = pathway["assessment_policy"]
    assert policy["report_or_artifact_required"] is True
    assert policy["short_finding_required"] is True
    assert policy["flag_alone_is_not_completion"] is True
    assert "analyst_report" in policy["evidence_examples"]
    assert "evidence_artifact" in policy["evidence_examples"]


def test_every_competency_exists_in_the_taxonomy():
    taxonomy_ids = _taxonomy_ids()
    for module in _pathway()["modules"]:
        for item in module["competencies"]:
            assert item["id"] in taxonomy_ids, (module["id"], item["id"])


def test_datasets_are_present_and_listed():
    readme = (DATASETS / "README.md").read_text(encoding="utf-8")
    for module in _pathway()["modules"]:
        for dataset in module["datasets"]:
            path = DATASETS / dataset
            assert path.is_file(), (module["id"], dataset)
            assert dataset in readme, (module["id"], dataset)
    assert (DATASETS / "report-template.md").is_file()


def test_evidence_files_parse_and_are_synthetic():
    for path in DATASETS.glob("*.jsonl"):
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert lines, path.name
        for line in lines:
            assert json.loads(line), path.name
    for path in DATASETS.glob("*.json"):
        assert json.loads(path.read_text(encoding="utf-8")), path.name
    for path in DATASETS.glob("*.yaml"):
        assert yaml.safe_load(path.read_text(encoding="utf-8")), path.name
    for path in DATASETS.glob("*"):
        if not path.is_file() or path.suffix not in {".jsonl", ".json", ".yaml", ".md"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        assert "@gmail.com" not in text
        assert "@yahoo.com" not in text
        assert "@outlook.com" not in text
        assert "555-" not in text


def test_report_template_has_the_required_sections():
    template = (DATASETS / "report-template.md").read_text(encoding="utf-8")
    for section in REPORT_SECTIONS:
        assert section in template, section
    assert "SHA-256" in template
    assert "Confidence" in template
    assert "Alternative explanation" in template


def test_module_labs_exist_or_are_explicitly_planned():
    existing = _lab_slugs()
    planned: set[str] = set()
    for module in _pathway()["modules"]:
        for slug in module["existing_labs"]:
            assert slug in existing, (module["id"], slug)
        for slug in module["planned_labs"]:
            assert slug not in existing, (module["id"], slug)
            assert slug not in planned, (module["id"], slug)
            planned.add(slug)
