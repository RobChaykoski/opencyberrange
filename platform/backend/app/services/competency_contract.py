"""Reviewed competency contract loader.

The contract is data, not a runtime score. It states which taxonomy
competencies a lab exercises, how much each contributes, which evidence types
are accepted, and how reliable the assessment is. Assessment code must use the
contract rather than inferring weights from lab text.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONTRACT_FILE = DATA_DIR / "competency-contracts.yaml"
TAXONOMY_FILE = DATA_DIR / "competency-taxonomy.yaml"


@lru_cache(maxsize=1)
def load_contracts() -> dict:
    with CONTRACT_FILE.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


@lru_cache(maxsize=1)
def taxonomy_ids() -> frozenset[str]:
    with TAXONOMY_FILE.open("r", encoding="utf-8") as handle:
        taxonomy = yaml.safe_load(handle) or {}
    ids = set()
    for domain in taxonomy.get("domains", []):
        for category in domain.get("categories", []):
            for competency in category.get("competencies", []):
                ids.add(str(competency["id"]))
    return frozenset(ids)


def contract_for_lab(lab_slug: str) -> dict | None:
    return (load_contracts().get("labs") or {}).get(lab_slug)


def reviewed_contracts() -> dict[str, dict]:
    return {
        slug: contract
        for slug, contract in (load_contracts().get("labs") or {}).items()
        if contract.get("review_status") == "reviewed"
    }


def validate_contracts() -> list[str]:
    problems: list[str] = []
    document = load_contracts()
    labs = document.get("labs") or {}
    if not labs:
        return ["competency contracts are empty"]
    known = taxonomy_ids()
    for slug, contract in labs.items():
        if contract.get("lab_id") != slug:
            problems.append(f"{slug}: lab_id does not match the map key")
        competencies = contract.get("competency_ids") or []
        total = sum(float(item.get("weight") or 0) for item in competencies)
        if abs(total - 1.0) > 1e-6:
            problems.append(f"{slug}: competency weights sum to {total}")
        unknown = {item.get("id") for item in competencies} - known
        if unknown:
            problems.append(f"{slug}: unknown competencies {sorted(unknown)}")
        evidence = contract.get("evidence") or []
        evidence_total = sum(float(item.get("weight") or 0) for item in evidence)
        if abs(evidence_total - 1.0) > 1e-6:
            problems.append(f"{slug}: evidence weights sum to {evidence_total}")
        if {item.get("type") for item in evidence} != {
            "flag",
            "validation_step",
            "analyst_answer",
            "artifact",
        }:
            problems.append(f"{slug}: evidence types are incomplete")
        if contract.get("prohibited_collection") != document.get(
            "prohibited_collection"
        ):
            problems.append(f"{slug}: prohibited collection differs from the policy")
    return problems
