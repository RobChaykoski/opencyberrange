"""Read-only competency coverage for the admin quality view.

The source of truth is the generated contract file. This service does not score
learners; it reports whether the curriculum model is ready for Release 6.

It also builds the subject-matter review packets. Review is a human decision:
the packet gives a reviewer the current contract, the taxonomy names, the
evidence weights, and a checklist. It does not mark anything reviewed.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml

from app.services.competency_contract import (
    contract_for_lab,
    load_contracts,
    taxonomy_ids,
    taxonomy_names,
)
from app.services.rubrics import load_rubrics

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BANK_FILE = DATA_DIR / "certification-question-banks.yaml"
PLATFORM_DIR = Path(__file__).resolve().parents[3]
LABS_DIR = PLATFORM_DIR / "labs"
WEIGHT_EPSILON = 0.001


def _bank_pathways() -> list[dict]:
    with BANK_FILE.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return list(payload.get("pathways") or [])


def coverage_summary() -> dict:
    contracts = load_contracts().get("labs") or {}
    tracks: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "reviewed": 0, "pending": 0})
    pending: list[dict] = []

    for slug, contract in sorted(contracts.items()):
        if not isinstance(contract, dict):
            continue
        track = str(contract.get("track") or "Unknown")
        status = str(contract.get("review_status") or "unknown")
        reviewed = status == "reviewed"
        tracks[track]["total"] += 1
        tracks[track]["reviewed" if reviewed else "pending"] += 1
        if not reviewed:
            pending.append(
                {
                    "slug": slug,
                    "track": track,
                    "difficulty": contract.get("difficulty"),
                    "status": status,
                }
            )

    total = len(contracts)
    reviewed = sum(1 for contract in contracts.values() if isinstance(contract, dict) and contract.get("review_status") == "reviewed")
    return {
        "total": total,
        "reviewed": reviewed,
        "pending": total - reviewed,
        "coverage_percent": round((reviewed / total) * 100, 1) if total else 0.0,
        "rubrics": len(load_rubrics()),
        "tracks": [
            {"track": track, **counts}
            for track, counts in sorted(tracks.items(), key=lambda item: (-item[1]["pending"], item[0]))
        ],
        "pending_labs": pending[:25],
    }


def _weight_sum(items: list) -> float:
    total = 0.0
    for item in items or []:
        if isinstance(item, dict):
            total += float(item.get("weight") or 0)
    return total


def release6_audit() -> dict:
    """Check every object that must carry a competency mapping for 6.0."""
    contracts = load_contracts().get("labs") or {}
    known = taxonomy_ids()
    lab_slugs = {path.parent.name for path in LABS_DIR.rglob("lab.yaml")}
    quiz_slugs = {path.parent.name for path in LABS_DIR.rglob("quiz.yaml")}

    missing_competencies: list[str] = []
    unknown_competencies: list[str] = []
    bad_weights: list[str] = []
    for slug, contract in sorted(contracts.items()):
        if not isinstance(contract, dict):
            continue
        links = [
            item
            for item in (contract.get("competency_ids") or [])
            if isinstance(item, dict) and item.get("id")
        ]
        ids = [str(item["id"]) for item in links]
        if not ids:
            missing_competencies.append(slug)
        for competency_id in ids:
            if competency_id not in known:
                unknown_competencies.append(f"{slug}:{competency_id}")
        if abs(_weight_sum(links) - 1.0) > WEIGHT_EPSILON:
            bad_weights.append(f"{slug}:competencies={_weight_sum(links):.3f}")
        if abs(_weight_sum(contract.get("evidence") or []) - 1.0) > WEIGHT_EPSILON:
            bad_weights.append(
                f"{slug}:evidence={_weight_sum(contract.get('evidence') or []):.3f}"
            )

    pathways = _bank_pathways()
    quiz_unmapped = [
        str(pathway.get("id"))
        for pathway in pathways
        if not pathway.get("competencies")
    ]
    quiz_unknown: list[str] = []
    for pathway in pathways:
        for competency_id in pathway.get("competencies") or []:
            if str(competency_id) not in known:
                quiz_unknown.append(f"{pathway.get('id')}:{competency_id}")

    labs_without_contract = sorted(lab_slugs - set(contracts))
    quizzes_without_contract = sorted(quiz_slugs - set(contracts))
    reviewed = sum(
        1
        for contract in contracts.values()
        if isinstance(contract, dict) and contract.get("review_status") == "reviewed"
    )
    gaps = (
        bool(missing_competencies)
        or bool(unknown_competencies)
        or bool(bad_weights)
        or bool(quiz_unmapped)
        or bool(quiz_unknown)
        or bool(labs_without_contract)
        or bool(quizzes_without_contract)
    )
    foundation_ready = (
        not gaps
        and len(contracts) > 0
        and reviewed == len(contracts)
        and len(pathways) > 0
        and not quiz_unmapped
    )
    return {
        "labs": {
            "total": len(lab_slugs),
            "contracts": len(contracts),
            "reviewed": reviewed,
            "pending_review": len(contracts) - reviewed,
            "missing_contract": labs_without_contract,
            "missing_competencies": missing_competencies,
            "unknown_competencies": unknown_competencies,
            "bad_weights": bad_weights,
        },
        "quiz_pathways": {
            "total": len(pathways),
            "mapped": len(pathways) - len(quiz_unmapped),
            "unmapped": quiz_unmapped,
            "unknown_competencies": quiz_unknown,
        },
        "exercise_quizzes": {
            "total": len(quiz_slugs),
            "with_contract": len(quiz_slugs) - len(quizzes_without_contract),
            "without_contract": quizzes_without_contract,
        },
        "capstones": {
            "status": "not_implemented",
            "objects": 0,
            "mapped": 0,
        },
        "badges": {
            "status": "derived_from_level_certificates",
            "individually_mapped": False,
            "note": "A badge inherits the competencies of the reviewed labs in its level.",
        },
        "structural_gaps": gaps,
        "foundation_ready": foundation_ready,
        # Capstone objects and per-badge competency lists do not exist yet.
        "release_6_ready": False,
    }


def pending_contracts(track: str | None = None) -> list[dict]:
    contracts = load_contracts().get("labs") or {}
    rows = []
    for slug, contract in sorted(contracts.items()):
        if not isinstance(contract, dict):
            continue
        if contract.get("review_status") == "reviewed":
            continue
        if track and str(contract.get("track") or "").casefold() != track.casefold():
            continue
        rows.append({"slug": slug, **contract})
    rows.sort(key=lambda row: (str(row.get("track")), row["slug"]))
    return rows


def _checklist() -> list[str]:
    return [
        "The competencies match what the exercise actually requires.",
        "The competency weights reflect the relative effort and importance.",
        "The evidence types can be collected by the platform.",
        "The evidence weights sum to 1.0 and include a human-reviewed artifact where needed.",
        "The assessment criteria are observable and not a restatement of the topic.",
        "No prohibited collection is introduced (keystrokes, mouse movement, exhaustive terminal history).",
        "The workbook path resolves to the authored chapter.",
        "Set `review_status: reviewed` and `reviewed_at: YYYY-MM-DD` in `competency-contracts.yaml`.",
        "Regenerate the review queue and coverage docs.",
    ]


def build_review_packet(slug: str) -> str:
    contract = contract_for_lab(slug)
    if contract is None:
        raise KeyError(f"unknown contract: {slug}")
    names = taxonomy_names()
    lines = [
        f"# Contract review: {slug}",
        "",
        f"- Track: **{contract.get('track') or 'Unknown'}**",
        f"- Difficulty: {contract.get('difficulty') or 'unknown'}",
        f"- Expected duration: {contract.get('expected_duration_minutes') or 'unknown'} minutes",
        f"- Review status: `{contract.get('review_status') or 'unknown'}`",
        f"- Reviewed at: {contract.get('reviewed_at') or 'not reviewed'}",
        f"- Workbook: `{contract.get('workbook') or 'missing'}`",
        f"- Test steps: {contract.get('test_steps') or 0}",
        f"- Flag required: {'yes' if contract.get('flag_required') else 'no'}",
        "",
        "## Current competencies",
        "",
        "| ID | Name | Weight |",
        "|---|---|---:|",
    ]
    for link in contract.get("competency_ids") or []:
        competency_id = str(link.get("id"))
        lines.append(
            f"| `{competency_id}` | {names.get(competency_id, 'UNKNOWN')} | {link.get('weight')} |"
        )
    lines += [
        "",
        "## Evidence",
        "",
        "| Type | Weight | Source | Validation |",
        "|---|---:|---|---|",
    ]
    for evidence in contract.get("evidence") or []:
        lines.append(
            f"| {evidence.get('type')} | {evidence.get('weight')} | "
            f"`{evidence.get('source')}` | {evidence.get('validation')} |"
        )
    lines += ["", "## Assessment criteria", ""]
    for criterion in contract.get("assessment_criteria") or []:
        lines.append(f"- {criterion}")
    reliability = contract.get("assessment_reliability") or {}
    lines += [
        "",
        "## Reliability",
        "",
        f"- Level: {reliability.get('level')}",
        f"- Score: {reliability.get('score')}",
        f"- Determinism: {reliability.get('determinism')}",
        f"- Independent validation: {reliability.get('independent_validation')}",
        f"- Rationale: {reliability.get('rationale') or 'none'}",
        "",
        "## Review checklist",
        "",
    ]
    lines += [f"- [ ] {item}" for item in _checklist()]
    lines += [
        "",
        "Review is a human decision. This packet does not change the contract.",
        "",
    ]
    return "\n".join(lines)
