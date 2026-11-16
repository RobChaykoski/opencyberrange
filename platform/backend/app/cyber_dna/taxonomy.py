"""Competency vocabulary owned by the Cyber DNA context.

The YAML is a shared catalogue, not exercise content. This loader deliberately
does not import the exercise models or the exercise-side mapping module, so the
DNA package stays independently testable and extractable.
"""

from __future__ import annotations

from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TAXONOMY_FILE = DATA_DIR / "competency-taxonomy.yaml"
TAXONOMY_VERSION = "1.0"

_cache: dict | None = None
_index: dict | None = None
_domains: list[str] | None = None


def load_taxonomy() -> dict:
    global _cache
    if _cache is None:
        with TAXONOMY_FILE.open("r", encoding="utf-8") as handle:
            _cache = yaml.safe_load(handle) or {}
    return _cache


def competency_index() -> dict[str, dict]:
    """Return competencies keyed by ID with their domain and labels."""
    global _index
    if _index is None:
        index: dict[str, dict] = {}
        for domain in load_taxonomy().get("domains", []):
            for category in domain.get("categories", []):
                for competency in category.get("competencies", []):
                    index[competency["id"]] = {
                        "id": competency["id"],
                        "name": competency["name"],
                        "domain": domain["id"],
                        "domain_label": domain["label"],
                        "category": category["id"],
                        "category_label": category["label"],
                    }
        _index = index
    return _index


def domain_ids() -> list[str]:
    global _domains
    if _domains is None:
        _domains = [domain["id"] for domain in load_taxonomy().get("domains", [])]
    return _domains


def proficiency_scale() -> list[dict]:
    return load_taxonomy().get("proficiency_scale", [])
