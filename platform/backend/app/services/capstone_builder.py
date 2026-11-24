"""Deterministic capstone planning.

The planner turns a role profile into a reviewable capstone plan. It does not
grade, generate prose, or publish anything. It selects labs from the reviewed
competency contracts, groups the covered competencies into objectives, maps the
evidence, and returns a validation gate.

The plan is a proposal. An instructor edits and approves it.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from app.services.competency_contract import load_contracts, taxonomy_names

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ROLES_FILE = DATA_DIR / "curriculum-roles.yaml"
TAXONOMY_FILE = DATA_DIR / "competency-taxonomy.yaml"
LABS_DIR = Path(__file__).resolve().parents[3] / "labs"

TARGET_COVERAGE = 90.0
WORKLOAD_TOLERANCE = 0.10
DIFFICULTY_ORDER = {"beginner": 0, "starter": 0, "intermediate": 1, "advanced": 2}

TRACK_ALIASES = {
    "high-school": "high school",
    "netfor": "network",
    "winpt": "windows",
    "linpt": "linux",
    "forensics": "forensics",
    "identity": "identity",
    "osint": "osint",
    "ai": "ai",
    "malware": "malware",
    "ot": "ot",
    "webpt": "web",
    "software-security": "software security",
}

ASSESSMENTS = [
    {
        "type": "formative",
        "title": "Evidence table and working notes",
        "weight": 0.30,
        "rubric": "analyst-answer",
        "evidence_type": "analyst_answer",
        "description": "Source, time, hash, and relevance for the evidence used in the lab sequence.",
    },
    {
        "type": "summative",
        "title": "Integrated investigation package",
        "weight": 0.50,
        "rubric": "capstone-brief",
        "evidence_type": "artifact",
        "description": "Timeline, finding, movement or impact map, remediation plan, and executive brief.",
    },
    {
        "type": "defence",
        "title": "Briefing and defence",
        "weight": 0.20,
        "rubric": "capstone-brief",
        "evidence_type": "artifact",
        "description": "A ten-minute briefing followed by questions on the evidence and the decisions.",
    },
]


class CapstoneError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@lru_cache(maxsize=1)
def _load_roles() -> dict:
    with ROLES_FILE.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


@lru_cache(maxsize=1)
def _taxonomy_domains() -> dict[str, str]:
    with TAXONOMY_FILE.open(encoding="utf-8") as handle:
        taxonomy = yaml.safe_load(handle) or {}
    domains: dict[str, str] = {}
    for domain in taxonomy.get("domains", []):
        for category in domain.get("categories", []):
            for competency in category.get("competencies", []):
                domains[str(competency["id"])] = str(domain.get("id") or "")
    return domains


@lru_cache(maxsize=1)
def _taxonomy_domain_names() -> dict[str, str]:
    with TAXONOMY_FILE.open(encoding="utf-8") as handle:
        taxonomy = yaml.safe_load(handle) or {}
    names: dict[str, str] = {}
    for domain in taxonomy.get("domains", []):
        domain_id = str(domain.get("id") or "")
        names[domain_id] = str(domain.get("name") or domain_id)
    return names


@lru_cache(maxsize=None)
def _lab_meta(slug: str) -> dict:
    for path in LABS_DIR.rglob("lab.yaml"):
        if path.parent.name != slug:
            continue
        with path.open(encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
        return {
            "title": payload.get("title") or slug,
            "description": payload.get("description") or "",
        }
    return {"title": slug, "description": ""}


def profiles() -> list[dict]:
    rows = []
    for profile in _load_roles().get("pathways") or []:
        critical = [str(item) for item in profile.get("critical_competencies") or []]
        rows.append(
            {
                "id": profile.get("id"),
                "title": profile.get("title"),
                "summary": profile.get("summary"),
                "tracks": profile.get("tracks") or [],
                "critical_competency_count": len(critical),
                "capstone": profile.get("capstone") or {},
                "career_ready_threshold": profile.get("career_ready_threshold"),
            }
        )
    return sorted(rows, key=lambda row: str(row["id"]))


def _profile(profile_id: str) -> dict:
    for profile in _load_roles().get("pathways") or []:
        if str(profile.get("id")) == str(profile_id):
            return profile
    raise CapstoneError(
        "capstone_profile_unknown",
        "The role profile is not in the curriculum catalogue.",
        404,
    )


def _hours(contract: dict) -> float:
    return max(int(contract.get("expected_duration_minutes") or 60), 15) / 60.0


def _reviewed(contract: dict) -> bool:
    return contract.get("review_status") == "reviewed"


def _reliability(contract: dict) -> float:
    value = (contract.get("assessment_reliability") or {}).get("score")
    try:
        return max(0.0, min(float(value), 1.0))
    except (TypeError, ValueError):
        return 0.5


def _candidates(profile: dict, contracts: dict) -> list[dict]:
    critical = {str(item) for item in profile.get("critical_competencies") or []}
    tracks = {
        TRACK_ALIASES.get(str(item).casefold(), str(item).casefold())
        for item in profile.get("tracks") or []
    }
    rows = []
    for slug, contract in contracts.items():
        if not isinstance(contract, dict):
            continue
        contract_track = str(contract.get("track") or "").casefold()
        if tracks and contract_track not in tracks:
            continue
        competencies = {
            str(item.get("id"))
            for item in contract.get("competency_ids") or []
            if isinstance(item, dict) and item.get("id")
        }
        overlap = competencies & critical
        if not overlap:
            continue
        hours = _hours(contract)
        quality = 1.0 if _reviewed(contract) else 0.6
        score = (len(overlap) * quality * (0.5 + _reliability(contract))) / hours
        rows.append(
            {
                "slug": slug,
                "contract": contract,
                "competencies": competencies,
                "overlap": overlap,
                "hours": hours,
                "reviewed": _reviewed(contract),
                "score": score,
            }
        )
    rows.sort(
        key=lambda row: (
            -row["score"],
            -len(row["overlap"]),
            row["hours"],
            row["slug"],
        )
    )
    return rows


def select_labs(
    candidates: list[dict],
    critical: set[str],
    duration_hours: float,
    max_labs: int,
) -> dict:
    """Greedy weighted set cover within the workload budget."""
    remaining = set(critical)
    selected: list[dict] = []
    budget = max(duration_hours, 1.0) * 60.0
    used = 0.0
    while remaining and len(selected) < max_labs:
        best = None
        best_key = None
        for row in candidates:
            if row["slug"] in {item["slug"] for item in selected}:
                continue
            gain = len(row["overlap"] & remaining)
            if gain == 0:
                continue
            fits = used + row["hours"] * 60.0 <= budget * (1 + WORKLOAD_TOLERANCE)
            key = (fits, gain * (0.5 + _reliability(row["contract"])), -row["hours"], row["score"])
            if best is None or key > best_key:
                best = row
                best_key = key
        if best is None:
            break
        if used + best["hours"] * 60.0 > budget * (1 + WORKLOAD_TOLERANCE):
            break
        selected.append(best)
        used += best["hours"] * 60.0
        remaining -= best["overlap"]
    return {
        "selected": selected,
        "uncovered": sorted(remaining),
        "workload_hours": round(used / 60.0, 1),
    }


def _topological_order(selected: list[dict], contracts: dict) -> list[dict]:
    by_slug = {row["slug"]: row for row in selected}
    ordered: list[dict] = []
    visiting: set[str] = set()

    def visit(row: dict) -> None:
        if row["slug"] in {item["slug"] for item in ordered} or row["slug"] in visiting:
            return
        visiting.add(row["slug"])
        for prerequisite in row["contract"].get("prerequisites") or []:
            parent = by_slug.get(str(prerequisite))
            if parent:
                visit(parent)
        visiting.discard(row["slug"])
        ordered.append(row)

    for row in sorted(
        selected,
        key=lambda item: (
            DIFFICULTY_ORDER.get(str(item["contract"].get("difficulty")), 1),
            item["slug"],
        ),
    ):
        visit(row)
    return ordered


def _objective_rows(covered: dict[str, set[str]], evidence_types: list[str]) -> list[dict]:
    names = taxonomy_names()
    domains = _taxonomy_domains()
    domain_names = _taxonomy_domain_names()
    grouped: dict[str, list[str]] = {}
    for competency_id in covered:
        grouped.setdefault(domains.get(competency_id, "OTHER"), []).append(competency_id)
    ranked = sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))[:6]
    rows = []
    for index, (domain_id, competency_ids) in enumerate(ranked, start=1):
        competency_ids = sorted(competency_ids)
        labels = [names.get(item, item) for item in competency_ids[:3]]
        rows.append(
            {
                "number": index,
                "statement": (
                    f"Given the selected lab evidence, demonstrate "
                    f"{domain_names.get(domain_id, domain_id)} by producing a reviewed "
                    f"artifact that applies {', '.join(labels)} and explains the decision."
                ),
                "competencies": [
                    {"id": item, "name": names.get(item, item)}
                    for item in competency_ids
                ],
                "evidence_types": evidence_types or ["artifact", "analyst_answer"],
            }
        )
    return rows


def build_plan(payload: dict) -> dict:
    profile = _profile(str(payload.get("profile_id") or ""))
    duration_hours = float(payload.get("duration_hours") or 40)
    max_labs = int(payload.get("max_labs") or 10)
    contracts = load_contracts().get("labs") or {}
    critical = {str(item) for item in profile.get("critical_competencies") or []}
    waived = {
        str(item)
        for item in payload.get("waived_competencies") or []
        if str(item) in critical
    }
    waiver_reason = str(payload.get("waiver_reason") or "").strip()
    assume_entry_level = bool(payload.get("assume_entry_level", True))
    candidates = _candidates(profile, contracts)
    if not candidates:
        raise CapstoneError(
            "capstone_no_candidates",
            "No reviewed lab contracts match this profile's tracks.",
            409,
        )
    selection = select_labs(candidates, critical, duration_hours, max_labs)
    selected = _topological_order(selection["selected"], contracts)

    covered_ids = set().union(*(row["overlap"] for row in selected)) if selected else set()
    covered: dict[str, set[str]] = {}
    evidence_types: set[str] = set()
    for row in selected:
        for competency_id in row["overlap"]:
            covered[competency_id] = covered.get(competency_id, set()) | {row["slug"]}
        for evidence in row["contract"].get("evidence") or []:
            if isinstance(evidence, dict) and evidence.get("type"):
                evidence_types.add(str(evidence["type"]))
    objectives = _objective_rows(covered, sorted(evidence_types))
    labs = []
    prerequisite_gaps = []
    for order, row in enumerate(selected, start=1):
        missing = [
            str(item)
            for item in row["contract"].get("prerequisites") or []
            if str(item) not in {selected_row["slug"] for selected_row in selected}
        ]
        prerequisite_gaps.extend(
            {"lab": row["slug"], "missing_prerequisite": item} for item in missing
        )
        meta = _lab_meta(row["slug"])
        labs.append(
            {
                "order": order,
                "slug": row["slug"],
                "title": meta["title"],
                "track": row["contract"].get("track"),
                "difficulty": row["contract"].get("difficulty"),
                "hours": row["hours"],
                "reviewed": row["reviewed"],
                "competencies": sorted(row["overlap"]),
                "prerequisites": row["contract"].get("prerequisites") or [],
            }
        )

    deliverables = []
    for index, deliverable in enumerate(
        (profile.get("capstone") or {}).get("deliverables") or [], start=1
    ):
        deliverables.append(
            {
                "number": index,
                "title": str(deliverable),
                "evidence_type": "artifact",
                "reviewer": "Instructor",
                "description": "Reviewed artifact with the capstone rubric.",
            }
        )
    if not deliverables:
        deliverables = [
            {
                "number": 1,
                "title": "Integrated capstone package",
                "evidence_type": "artifact",
                "reviewer": "Instructor",
                "description": "Reviewed artifact with the capstone rubric.",
            }
        ]

    evidence_map = []
    for competency_id in sorted(covered_ids):
        evidence_map.append(
            {
                "competency_id": competency_id,
                "name": taxonomy_names().get(competency_id, competency_id),
                "labs": sorted(covered.get(competency_id, set())),
                "evidence_types": sorted(evidence_types) or ["artifact"],
            }
        )

    weights_total = round(sum(item["weight"] for item in ASSESSMENTS), 2)
    covered_or_waived = covered_ids | waived
    coverage = (
        round(len(covered_or_waived) / len(critical) * 100, 1) if critical else 0.0
    )
    workload = selection["workload_hours"]
    variance = round((workload - duration_hours) / duration_hours * 100, 1) if duration_hours else 0.0
    gaps = []
    for competency_id in selection["uncovered"]:
        alternatives = [
            {
                "slug": row["slug"],
                "title": _lab_meta(row["slug"])["title"],
                "hours": row["hours"],
                "reviewed": row["reviewed"],
            }
            for row in candidates
            if competency_id in row["competencies"]
        ][:3]
        gaps.append(
            {
                "competency_id": competency_id,
                "name": taxonomy_names().get(competency_id, competency_id),
                "alternatives": alternatives,
            }
        )
    recommended_duration = round(workload / 0.8, 1) if workload else 0.0
    validation = {
        "coverage_percent": coverage,
        "target_coverage_percent": TARGET_COVERAGE,
        "coverage_pass": coverage >= TARGET_COVERAGE,
        "workload_hours": workload,
        "target_hours": duration_hours,
        "variance_percent": variance,
        "workload_pass": abs(variance) <= WORKLOAD_TOLERANCE * 100,
        "workload_note": (
            "Selected lab time is below the requested duration; add labs or lower the request."
            if variance < -WORKLOAD_TOLERANCE * 100
            else "Selected lab time is above the requested duration; remove a lab or raise the request."
            if variance > WORKLOAD_TOLERANCE * 100
            else "Selected lab time is within the workload tolerance."
        ),
        "recommended_duration_hours": recommended_duration,
        "waived_competencies": sorted(waived),
        "waiver_reason": waiver_reason or None,
        "waiver_valid": not waived or bool(waiver_reason),
        "assessment_weights_total": weights_total,
        "weights_pass": abs(weights_total - 1.0) < 0.001,
        "prerequisites_satisfied": not prerequisite_gaps or assume_entry_level,
        "assume_entry_level": assume_entry_level,
        "prerequisite_gaps": prerequisite_gaps,
        "prerequisite_assumed": prerequisite_gaps if assume_entry_level else [],
        "objective_coverage": all(
            objective["competencies"] and objective["evidence_types"]
            for objective in objectives
        ),
        "publishable": False,
        "gaps": gaps,
    }
    validation["publishable"] = all(
        [
            validation["coverage_pass"],
            validation["workload_pass"],
            validation["weights_pass"],
            validation["prerequisites_satisfied"],
            validation["objective_coverage"],
            validation["waiver_valid"],
        ]
    )

    return {
        "profile": {
            "id": profile.get("id"),
            "title": profile.get("title"),
            "summary": profile.get("summary"),
            "capstone": profile.get("capstone") or {},
            "career_ready_threshold": profile.get("career_ready_threshold"),
        },
        "request": {
            "duration_hours": duration_hours,
            "max_labs": max_labs,
        },
        "objectives": objectives,
        "labs": labs,
        "assessments": ASSESSMENTS,
        "deliverables": deliverables,
        "evidence_map": evidence_map,
        "validation": validation,
        "notes": [
            "This is a proposal. An instructor edits and approves it.",
            "The planner uses reviewed contracts first and never grades a learner.",
            "A plan is not published until the validation gate passes and an instructor approves it.",
        ],
    }
