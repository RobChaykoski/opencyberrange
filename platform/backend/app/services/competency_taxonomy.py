"""OpenCyberRange Competency Taxonomy v1.0 loader and evidence mapper.

The taxonomy is the shared vocabulary for workbooks, assessments, pathways,
badges, readiness, capstones, and employer transcripts. This module does three
things:

* loads the taxonomy and the workbook mapping;
* maps a lab or completion to competency IDs;
* turns a learner's completions into per-competency evidence.

Evidence is descriptive. A competency score is a practice-evidence score, not a
grade, a mastery claim, or a hiring prediction.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import yaml
from sqlalchemy.orm import Session, joinedload

from app.models import Lab, LabCompletion, Level, User

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TAXONOMY_FILE = DATA_DIR / "competency-taxonomy.yaml"
MAPPING_FILE = DATA_DIR / "competency-mapping.yaml"

TAXONOMY_VERSION = "1.0"
EVIDENCE_LEVELS = ("no_evidence", "early", "growing", "strong")
EVIDENCE_LABELS = {
    "no_evidence": "No evidence yet",
    "early": "Early evidence",
    "growing": "Growing evidence",
    "strong": "Strong evidence",
}

DOMAIN_CAREER_FAMILIES = {
    "NET": ["defensive", "cloud", "ot"],
    "LIN": ["defensive", "offensive", "cloud"],
    "WIN": ["defensive", "identity", "offensive"],
    "WEB": ["appsec", "offensive"],
    "OSINT": ["intel", "investigative"],
    "FOR": ["investigative", "defensive"],
    "MAL": ["investigative"],
    "TH": ["defensive", "investigative"],
    "IR": ["defensive"],
    "SOC": ["defensive"],
    "CLD": ["cloud", "identity"],
    "OT": ["ot"],
    "AI": ["ai"],
    "PROF": ["leadership", "grc"],
}

PRIMARY_AXIS_TO_DOMAIN = {
    "network_systems": "NET",
    "web_api": "WEB",
    "identity_access": "WIN",
    "incident_forensics": "FOR",
    "osint": "OSINT",
    "malware": "MAL",
    "ot_ics": "OT",
    "ai_security": "AI",
}

_taxonomy_cache: dict | None = None
_mapping_cache: dict | None = None


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_taxonomy() -> dict:
    global _taxonomy_cache
    if _taxonomy_cache is None:
        _taxonomy_cache = _load_yaml(TAXONOMY_FILE)
    return _taxonomy_cache


def load_mapping() -> dict:
    global _mapping_cache
    if _mapping_cache is None:
        _mapping_cache = _load_yaml(MAPPING_FILE)
    return _mapping_cache


def _taxonomy_index() -> tuple[dict, dict, dict]:
    taxonomy = load_taxonomy()
    domains: dict[str, dict] = {}
    categories: dict[str, dict] = {}
    competencies: dict[str, dict] = {}
    for domain in taxonomy.get("domains", []):
        domain_copy = {
            "id": domain["id"],
            "label": domain["label"],
            "description": domain.get("description", ""),
            "categories": [],
        }
        domains[domain["id"]] = domain_copy
        for category in domain.get("categories", []):
            category_copy = {
                "id": category["id"],
                "label": category["label"],
                "domain": domain["id"],
                "competencies": [],
            }
            categories[category["id"]] = category_copy
            domain_copy["categories"].append(category_copy)
            for competency in category.get("competencies", []):
                competency_copy = {
                    "id": competency["id"],
                    "name": competency["name"],
                    "domain": domain["id"],
                    "domain_label": domain["label"],
                    "category": category["id"],
                    "category_label": category["label"],
                }
                competencies[competency["id"]] = competency_copy
                category_copy["competencies"].append(competency_copy)
    return domains, categories, competencies


def _expand_domains(domain_ids: Iterable[str]) -> list[str]:
    _domains, _categories, competencies = _taxonomy_index()
    wanted = set(domain_ids)
    return [
        competency["id"]
        for competency in competencies.values()
        if competency["domain"] in wanted
    ]


def competencies_for_lab(lab: Lab | None) -> list[str]:
    """Return taxonomy IDs for one lab, using chapter, track, category, axis."""
    if lab is None:
        return []
    mapping = load_mapping()
    chapter_id = (getattr(lab, "chapter_id", None) or "").strip()
    if chapter_id and chapter_id in mapping.get("chapters", {}):
        return list(dict.fromkeys(mapping["chapters"][chapter_id]))

    level = getattr(lab, "level", None)
    track = getattr(level, "track", None) if level else None
    track_slug = (getattr(track, "slug", None) or "").strip().lower()
    if track_slug and track_slug in mapping.get("tracks", {}):
        domains = mapping["tracks"][track_slug].get("domains", [])
        expanded = _expand_domains(domains)
        if expanded:
            return expanded

    category = (getattr(lab, "category", None) or "general").strip().lower()
    if category in mapping.get("categories", {}):
        return list(dict.fromkeys(mapping["categories"][category]))

    axis = (getattr(lab, "primary_competency", None) or "").strip().lower()
    domain = PRIMARY_AXIS_TO_DOMAIN.get(axis)
    if domain:
        return _expand_domains([domain])
    return []


def _evidence_level(count: int) -> str:
    if count <= 0:
        return "no_evidence"
    if count < 3:
        return "early"
    if count < 5:
        return "growing"
    return "strong"


def _evidence_score(count: int, clean: int, advanced: int) -> int:
    return max(0, min(100, count * 15 + clean * 5 + advanced * 5))


def build_competency_profile(db: Session, user: User) -> dict:
    """Build a learner's per-competency evidence profile."""
    domains, categories, competencies = _taxonomy_index()
    completions = (
        db.query(LabCompletion)
        .options(
            joinedload(LabCompletion.lab)
            .joinedload(Lab.level)
            .joinedload(Level.track)
        )
        .filter(
            LabCompletion.user_id == user.id,
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        )
        .order_by(LabCompletion.completed_at.asc())
        .all()
    )

    evidence: dict[str, dict] = defaultdict(
        lambda: {
            "count": 0,
            "recent_count": 0,
            "clean": 0,
            "advanced": 0,
            "workbook": 0,
            "capstone": 0,
            "hint_free": 0,
            "first_attempt": 0,
            "minutes": 0,
            "labs": [],
            "latest": None,
        }
    )
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    for row in completions:
        lab = getattr(row, "lab", None)
        lab_name = str(getattr(lab, "name", "") or "").lower()
        lab_slug = str(getattr(lab, "slug", "") or "").lower()
        is_capstone = (
            str(getattr(lab, "category", "") or "").lower() == "assessment"
            or "capstone" in lab_name
            or "capstone" in lab_slug
        )
        completed_at = row.completed_at
        if completed_at is not None and completed_at.tzinfo is None:
            completed_at = completed_at.replace(tzinfo=timezone.utc)
        is_recent = bool(completed_at and completed_at >= cutoff)
        for competency_id in competencies_for_lab(lab):
            bucket = evidence[competency_id]
            bucket["count"] += 1
            if is_recent:
                bucket["recent_count"] += 1
            if (row.hints_used or 0) == 0 and (row.attempts or 1) <= 1:
                bucket["clean"] += 1
            if (row.hints_used or 0) == 0:
                bucket["hint_free"] += 1
            if (row.attempts or 1) <= 1:
                bucket["first_attempt"] += 1
            if str(getattr(lab, "difficulty", "") or "").lower() in {"advanced", "expert"}:
                bucket["advanced"] += 1
            if getattr(lab, "workbook", None):
                bucket["workbook"] += 1
            if is_capstone:
                bucket["capstone"] += 1
            bucket["minutes"] += row.time_spent_minutes or 0
            if lab is not None:
                bucket["labs"].append(lab.name)
            if row.completed_at is not None:
                bucket["latest"] = row.completed_at

    domain_rows = []
    for domain in domains.values():
        category_rows = []
        domain_count = 0
        for category in domain["categories"]:
            competency_rows = []
            category_count = 0
            for competency in category["competencies"]:
                bucket = evidence.get(competency["id"], {})
                count = bucket.get("count", 0)
                level = _evidence_level(count)
                row = {
                    **competency,
                    "evidence_count": count,
                    "recent_count": bucket.get("recent_count", 0),
                    "clean_solves": bucket.get("clean", 0),
                    "advanced_labs": bucket.get("advanced", 0),
                    "workbook_count": bucket.get("workbook", 0),
                    "capstone_count": bucket.get("capstone", 0),
                    "hint_free_count": bucket.get("hint_free", 0),
                    "first_attempt_count": bucket.get("first_attempt", 0),
                    "minutes": bucket.get("minutes", 0),
                    "evidence_level": level,
                    "evidence_label": EVIDENCE_LABELS[level],
                    "score": _evidence_score(
                        count,
                        bucket.get("clean", 0),
                        bucket.get("advanced", 0),
                    ),
                    "latest_evidence_at": (
                        bucket["latest"].isoformat()
                        if bucket.get("latest") is not None
                        else None
                    ),
                    "labs": list(dict.fromkeys(bucket.get("labs", [])))[-5:],
                }
                competency_rows.append(row)
                category_count += count
            category_rows.append(
                {
                    "id": category["id"],
                    "label": category["label"],
                    "evidence_count": category_count,
                    "competencies": competency_rows,
                }
            )
            domain_count += category_count
        domain_rows.append(
            {
                "id": domain["id"],
                "label": domain["label"],
                "description": domain["description"],
                "evidence_count": domain_count,
                "career_families": DOMAIN_CAREER_FAMILIES.get(domain["id"], []),
                "categories": category_rows,
            }
        )

    total_competencies = len(competencies)
    evidenced = sum(1 for row in evidence.values() if row.get("count", 0) > 0)
    return {
        "version": TAXONOMY_VERSION,
        "proficiency_scale": load_taxonomy().get("proficiency_scale", []),
        "domains": domain_rows,
        "summary": {
            "domains": len(domain_rows),
            "competencies": total_competencies,
            "competencies_with_evidence": evidenced,
            "evidence_coverage_pct": (
                round(evidenced / total_competencies * 100, 1)
                if total_competencies
                else 0.0
            ),
        },
        "disclaimer": (
            "Competency evidence is a descriptive practice record. It is not a "
            "grade, a mastery claim, or a prediction of job performance."
        ),
    }


def build_cohort_competency_summary(
    db: Session,
    learner_ids: list[int],
    minimum: int = 5,
) -> dict:
    """Aggregate competency evidence for a cohort with small-group suppression."""
    domains, _categories, competencies = _taxonomy_index()
    learner_ids = list(dict.fromkeys(learner_ids))
    if not learner_ids:
        return {
            "version": TAXONOMY_VERSION,
            "cohort_size": 0,
            "minimum_cohort_size": minimum,
            "state": "no_evidence",
            "domains": [],
        }

    completions = (
        db.query(LabCompletion)
        .options(
            joinedload(LabCompletion.lab)
            .joinedload(Lab.level)
            .joinedload(Level.track)
        )
        .filter(
            LabCompletion.user_id.in_(learner_ids),
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        )
        .all()
    )

    evidence: dict[str, dict] = defaultdict(
        lambda: {"learners": set(), "count": 0, "clean": 0, "advanced": 0}
    )
    for row in completions:
        lab = getattr(row, "lab", None)
        for competency_id in competencies_for_lab(lab):
            bucket = evidence[competency_id]
            bucket["learners"].add(row.user_id)
            bucket["count"] += 1
            if (row.hints_used or 0) == 0 and (row.attempts or 1) <= 1:
                bucket["clean"] += 1
            if str(getattr(lab, "difficulty", "") or "").lower() in {"advanced", "expert"}:
                bucket["advanced"] += 1

    suppressed = len(learner_ids) < max(1, minimum)
    domain_rows = []
    for domain in domains.values():
        category_rows = []
        for category in domain["categories"]:
            competency_rows = []
            for competency in category["competencies"]:
                bucket = evidence.get(competency["id"], {})
                learner_count = len(bucket.get("learners", set()))
                count = bucket.get("count", 0)
                if suppressed:
                    competency_rows.append(
                        {
                            **competency,
                            "state": "suppressed",
                            "evidence_level": "no_evidence",
                            "evidence_label": "Suppressed",
                        }
                    )
                    continue
                level = _evidence_level(learner_count)
                competency_rows.append(
                    {
                        **competency,
                        "state": "available" if learner_count else "no_evidence",
                        "learners_with_evidence": learner_count,
                        "coverage_pct": round(learner_count / len(learner_ids) * 100, 1),
                        "evidence_count": count,
                        "clean_solves": bucket.get("clean", 0),
                        "advanced_labs": bucket.get("advanced", 0),
                        "evidence_level": level,
                        "evidence_label": EVIDENCE_LABELS[level],
                    }
                )
            category_rows.append(
                {
                    "id": category["id"],
                    "label": category["label"],
                    "competencies": competency_rows,
                }
            )
        domain_rows.append(
            {
                "id": domain["id"],
                "label": domain["label"],
                "description": domain["description"],
                "career_families": DOMAIN_CAREER_FAMILIES.get(domain["id"], []),
                "categories": category_rows,
            }
        )

    return {
        "version": TAXONOMY_VERSION,
        "cohort_size": len(learner_ids),
        "minimum_cohort_size": minimum,
        "state": "suppressed" if suppressed else "available",
        "domains": domain_rows,
        "notes": [
            "Counts only; no learner names or identifiers.",
            "Groups below the minimum cohort size are suppressed.",
            "Competency evidence is descriptive, not a grade or a ranking.",
        ],
    }
