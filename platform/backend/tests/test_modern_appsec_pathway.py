"""The modern application-security pathway covers API, identity, and platform gaps."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "platform/backend/app/data"
PATHWAY = DATA / "modern-appsec-pathway.yaml"
TAXONOMY = DATA / "competency-taxonomy.yaml"
LABS = ROOT / "platform/labs"
DOC = ROOT / "docs/MODERN-APP-SECURITY-PATHWAY.md"
SLUG_RE = re.compile(r"^[a-z]+(?:-[a-z]+)*-(?:\d+-\d+|midterm-\d+|final-\d+)-[a-z0-9-]+$")


def _pathway() -> dict:
    return yaml.safe_load(PATHWAY.read_text(encoding="utf-8")) or {}


def _taxonomy_ids() -> set[str]:
    taxonomy = yaml.safe_load(TAXONOMY.read_text(encoding="utf-8")) or {}
    return {
        competency["id"]
        for domain in taxonomy["domains"]
        for category in domain.get("categories", [])
        for competency in category.get("competencies", [])
    }


def test_pathway_is_a_complete_ordered_progression():
    modules = _pathway()["modules"]
    assert [module["id"] for module in modules] == [
        f"MAS-{index:02d}" for index in range(1, 11)
    ]
    seen = set()
    for module in modules:
        assert module["title"].strip()
        assert module["estimated_minutes"] > 0
        assert module["outcomes"]
        assert module["evidence"]
        assert module["fix"].strip()
        assert module["safety"].strip()
        assert module["attack"]
        assert abs(sum(item["weight"] for item in module["competencies"]) - 1.0) < 1e-6
        for prerequisite in module["prerequisites"]:
            assert prerequisite in seen, (module["id"], prerequisite)
        seen.add(module["id"])


def test_competencies_and_labs_resolve():
    taxonomy = _taxonomy_ids()
    existing = {path.parent.name for path in LABS.rglob("lab.yaml")}
    planned: set[str] = set()
    for module in _pathway()["modules"]:
        for item in module["competencies"]:
            assert item["id"] in taxonomy, (module["id"], item["id"])
        for slug in module["existing_labs"]:
            assert slug in existing, (module["id"], slug)
        for slug in module["planned_labs"]:
            assert SLUG_RE.match(slug), (module["id"], slug)
            assert slug not in existing, (module["id"], slug)
            assert slug not in planned, slug
            planned.add(slug)


def test_required_modern_appsec_topics_are_covered():
    text = " ".join(
        f"{module['title']} {' '.join(module['outcomes'])}"
        for module in _pathway()["modules"]
    ).lower()
    for topic in (
        "api",
        "graphql",
        "jwt",
        "oauth",
        "devsecops",
        "container",
        "kubernetes",
        "supply chain",
    ):
        assert topic in text, topic


def test_documentation_names_every_module_and_required_topic():
    doc = DOC.read_text(encoding="utf-8")
    for module in _pathway()["modules"]:
        assert module["id"] in doc, module["id"]
    for topic in ("GraphQL", "JWT", "OAuth", "DevSecOps", "Kubernetes"):
        assert topic in doc, topic
