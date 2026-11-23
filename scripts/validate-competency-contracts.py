#!/usr/bin/env python3
"""Validate the Release 6 competency contracts before review.

Checks structure and arithmetic only. It cannot decide whether a competency is
the right one for an exercise; that is the subject-matter review.

Usage:
    python scripts/validate-competency-contracts.py
    python scripts/validate-competency-contracts.py --json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "platform/backend/app/data/competency-contracts.yaml"
TAXONOMY = ROOT / "platform/backend/app/data/competency-taxonomy.yaml"
LABS = ROOT / "platform/labs"
WEIGHT_EPSILON = 0.001
REVIEW_STATUSES = {"reviewed", "baseline_derived"}
EVIDENCE_TYPES = {
    "flag",
    "validation_step",
    "analyst_answer",
    "artifact",
    "quiz",
    "workbook",
}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def competency_ids() -> set[str]:
    taxonomy = load_yaml(TAXONOMY)
    result: set[str] = set()
    for domain in taxonomy.get("domains") or []:
        for category in domain.get("categories") or []:
            for competency in category.get("competencies") or []:
                if competency.get("id"):
                    result.add(str(competency["id"]))
    return result


def lab_slugs() -> set[str]:
    return {path.parent.name for path in LABS.rglob("lab.yaml")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    contracts = load_yaml(CONTRACTS).get("labs") or {}
    known_competencies = competency_ids()
    slugs = lab_slugs()
    errors: list[str] = []
    warnings: list[str] = []
    reviewed = 0
    statuses: Counter[str] = Counter()
    evidence_types: Counter[str] = Counter()

    for slug, contract in sorted(contracts.items()):
        if not isinstance(contract, dict):
            errors.append(f"{slug}: contract is not a mapping")
            continue
        if slug not in slugs:
            errors.append(f"{slug}: no lab.yaml with this slug")
        status = str(contract.get("review_status") or "")
        statuses[status or "missing"] += 1
        if status == "reviewed":
            reviewed += 1
        elif status not in REVIEW_STATUSES:
            errors.append(f"{slug}: unknown review_status {status!r}")

        competencies = contract.get("competency_ids") or []
        if not competencies:
            errors.append(f"{slug}: no competency_ids")
        seen: set[str] = set()
        competency_weight = 0.0
        for item in competencies:
            if not isinstance(item, dict) or not item.get("id"):
                errors.append(f"{slug}: malformed competency entry")
                continue
            cid = str(item["id"])
            if cid in seen:
                errors.append(f"{slug}: duplicate competency {cid}")
            seen.add(cid)
            if cid not in known_competencies:
                errors.append(f"{slug}: unknown competency {cid}")
            try:
                competency_weight += float(item.get("weight", 0))
            except (TypeError, ValueError):
                errors.append(f"{slug}: non-numeric competency weight for {cid}")
        if competencies and abs(competency_weight - 1.0) > WEIGHT_EPSILON:
            errors.append(f"{slug}: competency weights sum to {competency_weight:.3f}")

        evidence = contract.get("evidence") or []
        if not evidence:
            errors.append(f"{slug}: no evidence")
        evidence_weight = 0.0
        for item in evidence:
            if not isinstance(item, dict) or not item.get("type"):
                errors.append(f"{slug}: malformed evidence entry")
                continue
            etype = str(item["type"])
            evidence_types[etype] += 1
            if etype not in EVIDENCE_TYPES:
                errors.append(f"{slug}: unknown evidence type {etype}")
            try:
                evidence_weight += float(item.get("weight", 0))
            except (TypeError, ValueError):
                errors.append(f"{slug}: non-numeric evidence weight for {etype}")
        if evidence and abs(evidence_weight - 1.0) > WEIGHT_EPSILON:
            errors.append(f"{slug}: evidence weights sum to {evidence_weight:.3f}")

        if status == "reviewed" and not contract.get("assessment_reliability"):
            warnings.append(f"{slug}: reviewed contract has no assessment_reliability block")

    missing = sorted(slugs - set(contracts))
    for slug in missing:
        errors.append(f"{slug}: lab has no competency contract")

    summary = {
        "contracts": len(contracts),
        "labs": len(slugs),
        "reviewed": reviewed,
        "pending": len(contracts) - reviewed,
        "review_status": dict(sorted(statuses.items())),
        "evidence_types": dict(sorted(evidence_types.items())),
        "errors": len(errors),
        "warnings": len(warnings),
    }

    if args.json:
        print(json.dumps({**summary, "error_details": errors, "warning_details": warnings}, indent=2))
    else:
        print(
            f"competency contracts: {summary['contracts']} contracts, "
            f"{summary['reviewed']} reviewed, {summary['pending']} pending"
        )
        for warning in warnings:
            print(f"WARN: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print(
            "PASS" if not errors else f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)"
        )

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
