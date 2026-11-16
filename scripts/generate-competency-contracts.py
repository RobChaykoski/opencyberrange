#!/usr/bin/env python3
"""Generate the per-lab competency contract and its review report.

The reviewed taxonomy and mapping live in
``platform/backend/app/data/competency-taxonomy.yaml`` and
``competency-mapping.yaml``. Curated entries for the highest-use labs live in
``competency-contract-overrides.yaml``. Everything else gets a deterministic
baseline derived from the lab's workbook chapter, category, and mapped skills.

Run after changing a lab, the mapping, or a curated override:

    python scripts/generate-competency-contracts.py
    python scripts/generate-competency-contracts.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "platform/backend/app/data"
LABS = ROOT / "platform/labs"
TAXONOMY = DATA / "competency-taxonomy.yaml"
MAPPING = DATA / "competency-mapping.yaml"
OVERRIDES = DATA / "competency-contract-overrides.yaml"
OUTPUT = DATA / "competency-contracts.yaml"
REPORT = ROOT / "docs/COMPETENCY-CONTRACTS.md"

DEFAULT_EVIDENCE = {
    "flag": 0.35,
    "validation_step": 0.35,
    "analyst_answer": 0.20,
    "artifact": 0.10,
}
PROHIBITED = ["keystrokes", "mouse_movement", "exhaustive_terminal_history"]
AXIS_TO_DOMAIN = {
    "network_systems": "NET",
    "web_api": "WEB",
    "identity_access": "WIN",
    "incident_forensics": "FOR",
    "osint": "OSINT",
    "malware": "MAL",
    "ot_ics": "OT",
    "ai_security": "AI",
}
WEIGHT_SETS = {
    1: [1.0],
    2: [0.6, 0.4],
    3: [0.4, 0.35, 0.25],
    4: [0.4, 0.3, 0.2, 0.1],
}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def taxonomy_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for domain in load(TAXONOMY).get("domains", []):
        for category in domain.get("categories", []):
            for competency in category.get("competencies", []):
                index[competency["id"]] = {
                    "id": competency["id"],
                    "name": competency["name"],
                    "domain": domain["id"],
                    "category": category["id"],
                }
    return index


def chapter_id(workbook: str | None) -> str | None:
    match = re.search(r"CH[_-]([A-Za-z0-9]+)[_/]", str(workbook or ""))
    return match.group(1).upper() if match else None


def baseline_competencies(lab: dict, mapping: dict, taxonomy: dict) -> list[str]:
    chapter = chapter_id(lab.get("workbook"))
    chapters = mapping.get("chapters") or {}
    if chapter and chapter in chapters:
        return list(dict.fromkeys(chapters[chapter]))

    category = str(lab.get("category") or "").strip().lower()
    categories = mapping.get("categories") or {}
    if category in categories:
        return list(dict.fromkeys(categories[category]))

    domains = {
        AXIS_TO_DOMAIN[axis]
        for axis in (lab.get("mapped_skills") or [])
        if axis in AXIS_TO_DOMAIN
    }
    if domains:
        ids = [
            competency_id
            for competency_id, meta in taxonomy.items()
            if meta["domain"] in domains
        ]
        return ids

    return ["PROF-001"]


def weighted_ids(ids: list[str]) -> list[dict]:
    unique = list(dict.fromkeys(ids))[:4]
    if not unique:
        unique = ["PROF-001"]
    weights = WEIGHT_SETS.get(len(unique), WEIGHT_SETS[4])
    return [
        {"id": competency_id, "weight": weight}
        for competency_id, weight in zip(unique, weights)
    ]


def contract_for(lab: dict, slug: str, track: str, mapping: dict, taxonomy: dict, override: dict) -> dict:
    competencies = override.get("competency_ids") or weighted_ids(
        baseline_competencies(lab, mapping, taxonomy)
    )
    evidence_weights = {**DEFAULT_EVIDENCE, **(override.get("evidence_weights") or {})}
    reliability = override.get("assessment_reliability") or {
        "level": "medium",
        "score": 0.65,
        "evidence_completeness": "medium",
        "determinism": "deterministic",
        "independent_validation": "pending",
        "rationale": (
            "Baseline contract derived from the reviewed competency mapping. "
            "The evidence types and weights are explicit; live harness evidence "
            "and analyst-answer moderation are required before marking reviewed."
        ),
    }
    criteria = lab.get("assessment_criteria") or [
        "Submit the correct flag.",
        "Pass every automated solve step.",
        "Record one analyst observation and one defensive implication.",
        "Submit the requested scan, report, or screenshot artifact.",
    ]
    return {
        "lab_id": slug,
        "track": track,
        "difficulty": lab.get("difficulty") or "unknown",
        "expected_duration_minutes": int(lab.get("estimated_time") or 60),
        "prerequisites": list(lab.get("prerequisites") or []),
        "workbook": lab.get("workbook") or "",
        "competency_ids": competencies,
        "evidence": [
            {
                "type": "flag",
                "weight": evidence_weights["flag"],
                "source": "lab.flag",
                "validation": "exact_match",
            },
            {
                "type": "validation_step",
                "weight": evidence_weights["validation_step"],
                "source": f"platform/tester/manifests/{slug}.yaml",
                "validation": "all_steps_pass",
            },
            {
                "type": "analyst_answer",
                "weight": evidence_weights["analyst_answer"],
                "source": "workbook.analysis_questions",
                "validation": "rubric",
            },
            {
                "type": "artifact",
                "weight": evidence_weights["artifact"],
                "source": "submitted_artifact",
                "validation": "rubric",
            },
        ],
        "prohibited_collection": list(PROHIBITED),
        "assessment_reliability": reliability,
        "assessment_criteria": criteria,
        "test_steps": len((lab.get("test") or {}).get("steps") or []),
        "flag_required": bool(lab.get("flag")),
        "content_version": lab.get("content_version") or "",
        "usage_rank": override.get("usage_rank"),
        "usage_completions": override.get("usage_completions"),
        "usage_source": (
            override.get("usage_source")
            or (
                "Production lab_completions, queried 2026-11-16"
                if override.get("usage_rank")
                else None
            )
        ),
        "review_status": override.get("review_status") or "baseline_derived",
        "reviewed_at": override.get("reviewed_at"),
    }


def build() -> dict:
    mapping = load(MAPPING)
    taxonomy = taxonomy_index()
    overrides = (load(OVERRIDES).get("labs") or {}) if OVERRIDES.is_file() else {}
    labs: dict[str, dict] = {}
    for lab_yaml in sorted(LABS.rglob("lab.yaml")):
        lab = load(lab_yaml)
        slug = lab_yaml.parent.name
        track = lab_yaml.parent.parent.name
        labs[slug] = contract_for(
            lab,
            slug,
            track,
            mapping,
            taxonomy,
            overrides.get(slug) or {},
        )
    return {
        "version": "1.0",
        "basis": (
            "Generated from the reviewed competency taxonomy, competency mapping, "
            "and curated high-use overrides. Evidence is limited to flags, solve "
            "validation, analyst answers, and submitted artifacts."
        ),
        "prohibited_collection": list(PROHIBITED),
        "labs": dict(sorted(labs.items())),
    }


def _validate(document: dict, taxonomy: dict) -> list[str]:
    errors: list[str] = []
    labs = document.get("labs") or {}
    for slug, contract in labs.items():
        competencies = contract.get("competency_ids") or []
        total = sum(float(item.get("weight") or 0) for item in competencies)
        if not competencies:
            errors.append(f"{slug}: no competency IDs")
        if abs(total - 1.0) > 1e-6:
            errors.append(f"{slug}: competency weights sum to {total}")
        for item in competencies:
            if item.get("id") not in taxonomy:
                errors.append(f"{slug}: unknown competency {item.get('id')}")
        evidence = contract.get("evidence") or []
        evidence_total = sum(float(item.get("weight") or 0) for item in evidence)
        if abs(evidence_total - 1.0) > 1e-6:
            errors.append(f"{slug}: evidence weights sum to {evidence_total}")
        allowed = {"flag", "validation_step", "analyst_answer", "artifact"}
        if {item.get("type") for item in evidence} != allowed:
            errors.append(f"{slug}: evidence types must be {sorted(allowed)}")
        if contract.get("prohibited_collection") != PROHIBITED:
            errors.append(f"{slug}: prohibited_collection must match the policy")
    return errors


def render_report(document: dict) -> str:
    labs = document["labs"]
    reviewed = [slug for slug, contract in labs.items() if contract["review_status"] == "reviewed"]
    reviewed.sort(
        key=lambda slug: (
            labs[slug].get("usage_rank") is None,
            labs[slug].get("usage_rank") or 999,
        )
    )
    baseline = [slug for slug, contract in labs.items() if contract["review_status"] != "reviewed"]
    lines = [
        "# Competency contracts",
        "",
        "<!-- Generated by scripts/generate-competency-contracts.py. Do not edit by hand. -->",
        "",
        "Source of truth: `platform/backend/app/data/competency-contracts.yaml`,",
        "generated from the competency taxonomy, workbook mapping, lab metadata, and",
        "the curated high-use overrides.",
        "",
        "## Collection policy",
        "",
        "A contract uses only:",
        "",
        "- the lab flag, compared exactly;",
        "- automated solve/validation steps from the lab manifest;",
        "- analyst answers from the workbook;",
        "- submitted artifacts (scan output, report, screenshot, or evidence file).",
        "",
        "It does **not** collect keystrokes, mouse movement, or exhaustive terminal",
        "history. Those signals are prohibited for every lab.",
        "",
        "## Coverage",
        "",
        f"- Labs: **{len(labs)}**",
        f"- Reviewed: **{len(reviewed)}**",
        f"- Baseline derived, awaiting review: **{len(baseline)}**",
        "",
        "## Highest-use reviewed labs",
        "",
        "Ranked by recorded completions in the production database on 2026-11-16.",
        "",
        "| Rank | Completions | Lab | Track | Difficulty | Minutes | Competencies (weight) | Reliability |",
        "|---:|---:|---|---|---|---:|---|---|",
    ]
    for slug in reviewed:
        contract = labs[slug]
        competencies = ", ".join(
            f"`{item['id']}` {item['weight']:.2f}" for item in contract["competency_ids"]
        )
        reliability = contract["assessment_reliability"]
        lines.append(
            "| {} | {} | `{}` | {} | {} | {} | {} | {} ({:.2f}) |".format(
                contract.get("usage_rank") or "-",
                contract.get("usage_completions") or "-",
                slug,
                contract["track"],
                contract["difficulty"],
                contract["expected_duration_minutes"],
                competencies,
                reliability["level"],
                reliability["score"],
            )
        )
    lines.extend(
        [
            "",
            "## Review queue",
            "",
            "The remaining baseline contracts already carry explicit competency IDs,",
            "weights, evidence weights, prerequisites, duration, and reliability",
            "fields. Mark one reviewed after a subject-matter review and a live",
            "three-run harness result:",
            "",
            "```bash",
            "python scripts/lab_harness.py --lab <lab-id> --runs 3 --rebuild",
            "python scripts/generate-competency-contracts.py",
            "```",
            "",
            "A reviewed contract should change `review_status` to `reviewed`, set",
            "`reviewed_at`, and replace the baseline reliability rationale with the",
            "actual evidence and harness result.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    document = build()
    errors = _validate(document, taxonomy_index())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    rendered = yaml.safe_dump(
        document, sort_keys=False, default_flow_style=False, width=1000
    )
    report = render_report(document)

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        current_report = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
        if current != rendered:
            print(f"stale competency contracts: {OUTPUT.relative_to(ROOT)}", file=sys.stderr)
            return 1
        if current_report != report:
            print(f"stale competency report: {REPORT.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"competency contracts are current ({len(document['labs'])} labs)")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
    REPORT.write_text(report, encoding="utf-8", newline="\n")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)} and {REPORT.relative_to(ROOT)} "
        f"({len(document['labs'])} labs)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
