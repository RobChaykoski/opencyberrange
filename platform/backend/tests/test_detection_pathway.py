"""The defensive detection pathway resolves to real, synthetic, testable assets."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "platform/backend/app/data"
PATHWAY = DATA / "detection-pathway.yaml"
DATASETS = DATA / "detection-datasets"
TAXONOMY = DATA / "competency-taxonomy.yaml"
LABS = ROOT / "platform/labs"

PROHIBITED = ["keystrokes", "mouse_movement", "exhaustive_terminal_history"]
REQUIRED_MODULES = [f"DET-{index:02d}" for index in range(1, 9)]


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
    seen = set()
    for module in modules:
        assert module["title"].strip()
        assert module["estimated_minutes"] > 0
        assert module["outcomes"], module["id"]
        assert module["evidence"], module["id"]
        assert sum(item["weight"] for item in module["competencies"]) == 1.0
        for prerequisite in module["prerequisites"]:
            assert prerequisite in seen, (module["id"], prerequisite)
        seen.add(module["id"])


def test_every_competency_exists_in_the_taxonomy():
    taxonomy_ids = _taxonomy_ids()
    for module in _pathway()["modules"]:
        for item in module["competencies"]:
            assert item["id"] in taxonomy_ids, (module["id"], item["id"])


def test_datasets_and_rules_are_present_and_listed():
    readme = (DATASETS / "README.md").read_text(encoding="utf-8")
    files = {path.name for path in DATASETS.iterdir() if path.is_file()}
    assert "opensearch-events.jsonl" in files
    for module in _pathway()["modules"]:
        for dataset in module["datasets"]:
            assert (DATASETS / dataset).is_file(), (module["id"], dataset)
            assert dataset in readme, (module["id"], dataset)
        for rule in module["sigma_rules"]:
            assert (DATASETS / "sigma" / rule).is_file(), (module["id"], rule)
            assert rule in readme, (module["id"], rule)


def test_jsonl_datasets_parse_and_use_documentation_ranges():
    addresses: set[str] = set()
    for path in DATASETS.glob("*.jsonl"):
        lines = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert lines, path.name
        for line in lines:
            event = json.loads(line)
            addresses.update(re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", line))
            assert "password" not in line.lower(), (path.name, "credential material")
            assert "@example.org" not in line and "@gmail.com" not in line
            assert event, path.name
    assert addresses
    for address in addresses:
        assert address.startswith("10.20.0."), address


def test_assets_contain_no_surveillance_signals():
    pathway = _pathway()
    assert pathway["data_policy"]["synthetic_only"] is True
    assert pathway["data_policy"]["real_pii"] is False
    assert pathway["data_policy"]["prohibited_collection"] == PROHIBITED
    for path in DATASETS.rglob("*"):
        if not path.is_file() or path.suffix not in {".jsonl", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for term in PROHIBITED:
            assert term not in text, (path.name, term)


def test_sigma_rules_are_reviewable():
    for path in (DATASETS / "sigma").glob("*.yml"):
        rule = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert rule["title"].strip()
        assert rule["id"].strip()
        assert rule["description"].strip()
        assert rule["logsource"]
        assert rule["detection"]["condition"]
        assert rule["falsepositives"], path.name
        assert rule["level"] in {"low", "medium", "high", "critical"}


def test_kql_queries_are_unique_and_reference_dataset_indexes():
    document = yaml.safe_load(
        (DATASETS / "kql-queries.yaml").read_text(encoding="utf-8")
    )
    queries = document["queries"]
    assert queries
    ids = set()
    indexes = {path.stem for path in DATASETS.glob("*.jsonl")}
    for query in queries:
        assert query["id"] not in ids
        ids.add(query["id"])
        assert query["index"] in indexes, query["id"]
        assert "|" in query["kql"], query["id"]
        assert query["expected"].strip()


def test_every_module_names_a_planned_or_existing_lab():
    existing = _lab_slugs()
    planned: set[str] = set()
    for module in _pathway()["modules"]:
        for slug in module["existing_labs"]:
            assert slug in existing, (module["id"], slug)
        for slug in module["planned_labs"]:
            assert slug not in existing, (module["id"], slug)
            assert slug not in planned, (module["id"], slug)
            planned.add(slug)
