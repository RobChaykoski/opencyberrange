#!/usr/bin/env python3
"""Generate the measurable outcome contract for every lab.

Every lab produces one entry with:

* skills earned;
* competencies proven, with weights and taxonomy context;
* knowledge domains;
* evidence artifacts;
* a confidence score and basis.

The source is the reviewed competency taxonomy, the per-lab competency
contract, and the lab metadata. This gives Cyber DNA, the workbook, and learner
transcripts one stable data source instead of re-deriving outcomes per view.

Usage:
    python scripts/generate-lab-outcomes.py
    python scripts/generate-lab-outcomes.py --check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "platform/backend/app/data"
LABS = ROOT / "platform/labs"
TAXONOMY = DATA / "competency-taxonomy.yaml"
CONTRACTS = DATA / "competency-contracts.yaml"
OUTPUT = DATA / "lab-outcomes.yaml"

EVIDENCE_LABELS = {
    "flag": "flag",
    "validation_step": "automated validation",
    "analyst_answer": "analyst finding",
    "artifact": "submitted artifact",
}
AXIS_LABELS = {
    "network_systems": "Network systems",
    "web_api": "Web and API",
    "identity_access": "Identity and access",
    "incident_forensics": "Incident and forensics",
    "osint": "OSINT",
    "malware": "Malware analysis",
    "ot_ics": "OT and ICS",
    "ai_security": "AI security",
}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def taxonomy_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for domain in load(TAXONOMY).get("domains", []):
        for category in domain.get("categories", []):
            for competency in category.get("competencies", []):
                index[str(competency["id"])] = {
                    "id": str(competency["id"]),
                    "name": str(competency["name"]),
                    "domain": str(domain["id"]),
                    "domain_label": str(domain.get("label") or domain["id"]),
                    "category": str(category["id"]),
                    "category_label": str(category.get("label") or category["id"]),
                }
    return index


def lab_metadata() -> dict[str, dict]:
    result: dict[str, dict] = {}
    for path in LABS.rglob("lab.yaml"):
        data = load(path)
        result[path.parent.name] = data
    return result


def build() -> dict:
    taxonomy = taxonomy_index()
    contracts = load(CONTRACTS).get("labs") or {}
    labs = lab_metadata()
    entries: dict[str, dict] = {}
    for slug in sorted(contracts):
        contract = contracts[slug]
        lab = labs.get(slug) or {}
        proven = []
        domains: dict[str, dict] = {}
        for weighted in contract.get("competency_ids") or []:
            competency_id = str(weighted.get("id"))
            meta = taxonomy.get(competency_id)
            if meta is None:
                raise SystemExit(f"{slug}: unknown competency {competency_id}")
            proven.append(
                {
                    "id": competency_id,
                    "name": meta["name"],
                    "weight": round(float(weighted.get("weight") or 0), 4),
                    "category": meta["category_label"],
                }
            )
            domains[meta["domain"]] = {
                "id": meta["domain"],
                "label": meta["domain_label"],
            }
        reliability = contract.get("assessment_reliability") or {}
        evidence_types = [str(item.get("type")) for item in contract.get("evidence") or []]
        evidence = [EVIDENCE_LABELS.get(item, item.replace("_", " ")) for item in evidence_types]
        entry = {
            "track": contract.get("track") or "",
            "difficulty": contract.get("difficulty") or "unknown",
            "expected_duration_minutes": contract.get("expected_duration_minutes") or 0,
            "workbook": contract.get("workbook") or "",
            "skills_earned": [
                {
                    "id": item["id"],
                    "name": item["name"],
                    "weight": item["weight"],
                }
                for item in proven
            ],
            "competencies_proven": proven,
            "knowledge_domains": sorted(domains.values(), key=lambda item: item["id"]),
            "practice_axes": [
                AXIS_LABELS.get(str(axis), str(axis)) for axis in lab.get("mapped_skills") or []
            ],
            "evidence_artifacts": evidence,
            "confidence": {
                "score": round(float(reliability.get("score") or 0), 4),
                "level": reliability.get("level") or "low",
                "basis": reliability.get("rationale") or "No reliability rationale recorded.",
            },
            "review_status": contract.get("review_status") or "baseline_derived",
            "reviewed_at": contract.get("reviewed_at"),
        }
        entries[slug] = entry
    missing = sorted(set(labs) - set(entries))
    if missing:
        raise SystemExit(f"labs without a contract: {', '.join(missing[:5])}")
    return {
        "version": "1.0",
        "basis": (
            "Generated from the reviewed competency taxonomy, per-lab competency "
            "contract, and lab metadata. The confidence value is an assessment "
            "reliability signal, not a learner score."
        ),
        "labs": entries,
    }


def render(document: dict) -> str:
    header = (
        "# Generated measurable outcomes for every lab.\n"
        "# Do not edit by hand. Run python scripts/generate-lab-outcomes.py.\n"
        "# Each entry is the workbook/Cyber DNA contract for one lab.\n\n"
    )
    return header + yaml.safe_dump(
        document,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=100,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the file is stale")
    args = parser.parse_args()
    rendered = render(build())
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(
                f"FAIL: {OUTPUT} is stale; run python scripts/generate-lab-outcomes.py",
                file=sys.stderr,
            )
            return 1
        print("PASS: lab outcomes match the competency contracts")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT} ({rendered.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
