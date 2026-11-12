"""Role readiness from the competency taxonomy and assessment model.

The learner states a target role. The engine answers six questions:

* what skills they already have;
* which workbooks or labs to complete next;
* their current readiness score;
* which capstone to attempt;
* which certifications align;
* what evidence they can show an employer.

Readiness is a curriculum coverage estimate, not a prediction of employment.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy.orm import Session, joinedload

from app.models import Lab, Level, User
from app.services.competency_assessment import build_competency_assessment_profile
from app.services.competency_taxonomy import DOMAIN_CAREER_FAMILIES, competencies_for_lab

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ROLES_FILE = DATA_DIR / "curriculum-roles.yaml"

DIFFICULTY_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}
DEFAULT_THRESHOLD = 80
DEFAULT_FLOOR = 70

_roles_cache: dict | None = None


def load_roles() -> dict:
    global _roles_cache
    if _roles_cache is None:
        with ROLES_FILE.open("r", encoding="utf-8") as handle:
            _roles_cache = yaml.safe_load(handle) or {}
    return _roles_cache


def roles_catalogue() -> dict:
    data = load_roles()
    return {
        "version": data.get("version"),
        "readiness_model": data.get("readiness_model", {}),
        "level_targets": data.get("level_targets", {}),
        "roles": [
            {
                "id": role["id"],
                "title": role["title"],
                "family": role.get("family"),
                "flagship": bool(role.get("flagship")),
                "aliases": role.get("aliases", []),
                "summary": role.get("summary"),
                "level_requirements": role.get("level_requirements", {}),
                "capstone": {
                    "title": (role.get("capstone") or {}).get("title"),
                    "description": (role.get("capstone") or {}).get("description"),
                },
                "certifications": role.get("certifications", {}),
            }
            for role in data.get("pathways", [])
        ],
    }


def _role(role_id: str) -> dict | None:
    return next(
        (role for role in load_roles().get("pathways", []) if role["id"] == role_id),
        None,
    )


def _flatten_competencies(profile: dict) -> dict[str, dict]:
    rows = {}
    for domain in profile.get("domains", []):
        for category in domain.get("categories", []):
            for competency in category.get("competencies", []):
                rows[competency["id"]] = competency
    return rows


def _target_for(role: dict, domain: str) -> tuple[str, int]:
    level = role.get("level_requirements", {}).get(domain, "Silver")
    target = load_roles().get("level_targets", {}).get(level, 60)
    return level, int(target)


def _status(score, target: int, awarded: bool) -> str:
    if score is None:
        return "no_evidence"
    if score >= target and awarded:
        return "have"
    if score >= target * 0.6:
        return "building"
    return "gap"


def _colour(score, target: int) -> str:
    if score is None:
        return "grey"
    if score >= target:
        return "green"
    if score >= target * 0.7:
        return "amber"
    return "red"


def _coverage_colour(pct: float) -> str:
    if pct >= 85:
        return "green"
    if pct >= 60:
        return "amber"
    return "red"


def _domain_rows(role: dict, critical: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for row in critical:
        grouped.setdefault(row["domain"], []).append(row)
    rows = []
    for domain, items in grouped.items():
        level, target = _target_for(role, domain)
        coverage = sum(item["coverage"] for item in items) / len(items) if items else 0
        rows.append(
            {
                "domain": domain,
                "label": items[0]["domain_label"] if items else domain,
                "target_level": level,
                "target_score": target,
                "score": round(coverage * 100, 1),
                "colour": _coverage_colour(coverage * 100),
                "competencies": len(items),
                "have": sum(1 for item in items if item["status"] == "have"),
                "building": sum(1 for item in items if item["status"] == "building"),
                "gap": sum(1 for item in items if item["status"] in {"gap", "no_evidence"}),
                "career_families": DOMAIN_CAREER_FAMILIES.get(domain, []),
            }
        )
    rows.sort(key=lambda row: (row["score"], row["domain"]))
    return rows


def _average_dimension(critical: list[dict], key: str) -> float | None:
    values = [
        item["dimensions"].get(key)
        for item in critical
        if item["dimensions"].get(key) is not None
    ]
    if not values:
        return None
    return round(sum(values) / len(values), 1)


def _capstone_completed(role: dict, summary: dict | None) -> bool:
    completions = (summary or {}).get("completions") or []
    capstone = role.get("capstone") or {}
    track = str(capstone.get("track") or "").lower()
    for item in completions:
        text = " ".join(
            str(item.get(field) or "")
            for field in ("lab_name", "lab_slug", "category", "workbook")
        ).lower()
        if track and str(item.get("track_slug") or "").lower() != track:
            continue
        if "capstone" in text or "assessment" in text or "final" in text:
            return True
    return False


def _next_labs(
    db: Session,
    role: dict,
    gap_ids: set[str],
    completed_ids: set[int],
    competency_scores: dict[str, float | None],
    competency_names: dict[str, str],
) -> list[dict]:
    labs = (
        db.query(Lab)
        .options(joinedload(Lab.level).joinedload(Level.track))
        .filter(Lab.is_active == True, Lab.visibility == "public")
        .all()
    )
    tracks = {str(track).lower() for track in role.get("tracks", [])}
    categories = {str(category).lower() for category in role.get("categories", [])}
    rows = []
    for lab in labs:
        if lab.id in completed_ids or not getattr(lab, "workbook", None):
            continue
        level = getattr(lab, "level", None)
        track = getattr(level, "track", None) if level else None
        track_slug = str(getattr(track, "slug", "") or "").lower()
        category = str(getattr(lab, "category", "") or "").lower()
        if tracks and track_slug not in tracks and category not in categories:
            continue
        lab_competencies = set(competencies_for_lab(lab))
        matched = lab_competencies & gap_ids
        if not matched:
            continue
        scored = [
            competency_scores.get(competency_id)
            for competency_id in lab_competencies
            if competency_scores.get(competency_id) is not None
        ]
        average = round(sum(scored) / len(scored), 1) if scored else None
        if average is None:
            lab_status, lab_label, lab_colour = "no_evidence", "No evidence yet", "grey"
        elif average >= 75:
            lab_status, lab_label, lab_colour = "ready", "Ready", "green"
        elif average >= 60:
            lab_status, lab_label, lab_colour = "nearly", "Nearly ready", "amber"
        else:
            lab_status, lab_label, lab_colour = "build_first", "Build first", "red"
        rows.append(
            {
                "name": lab.name,
                "slug": lab.slug,
                "track": track.name if track else "Uncategorised",
                "track_slug": track_slug,
                "difficulty": lab.difficulty,
                "workbook": lab.workbook,
                "competencies": sorted(matched),
                "competency_names": [
                    competency_names.get(competency_id, competency_id)
                    for competency_id in sorted(matched)
                ],
                "readiness": {
                    "score": average,
                    "status": lab_status,
                    "label": lab_label,
                    "colour": lab_colour,
                    "reason": (
                        "Your evidence in "
                        + ", ".join(
                            competency_names.get(competency_id, competency_id)
                            for competency_id in sorted(matched)[:2]
                        )
                        + " is the starting point."
                    ),
                },
                "_rank": (
                    DIFFICULTY_RANK.get(str(lab.difficulty or "").lower(), 9),
                    lab.sort_order or 0,
                    lab.id,
                ),
            }
        )
    rows.sort(key=lambda row: row["_rank"])
    for row in rows:
        row.pop("_rank", None)
    return rows[:5]


def _capstone_lab(db: Session, role: dict, completed_ids: set[int]) -> dict | None:
    capstone = role.get("capstone") or {}
    track_slug = str(capstone.get("track") or "").lower()
    labs = (
        db.query(Lab)
        .options(joinedload(Lab.level).joinedload(Level.track))
        .filter(Lab.is_active == True, Lab.visibility == "public")
        .all()
    )
    candidates = []
    for lab in labs:
        level = getattr(lab, "level", None)
        track = getattr(level, "track", None) if level else None
        lab_track = str(getattr(track, "slug", "") or "").lower()
        if track_slug and lab_track != track_slug:
            continue
        text = f"{lab.name} {lab.slug} {lab.workbook or ''} {lab.category or ''}".lower()
        if "capstone" not in text and "assessment" not in text and "final" not in text:
            continue
        candidates.append(
            (
                lab.id in completed_ids,
                DIFFICULTY_RANK.get(str(lab.difficulty or "").lower(), 9),
                lab.sort_order or 0,
                lab,
            )
        )
    if not candidates:
        return None
    candidates.sort(key=lambda row: (row[0], row[1], row[2]))
    _done, _difficulty, _order, lab = candidates[0]
    level = getattr(lab, "level", None)
    track = getattr(level, "track", None) if level else None
    return {
        "name": lab.name,
        "slug": lab.slug,
        "track": track.name if track else None,
        "track_slug": str(getattr(track, "slug", "") or ""),
        "difficulty": lab.difficulty,
        "workbook": lab.workbook,
        "completed": lab.id in completed_ids,
    }


def _rating(score: float) -> dict:
    for row in load_roles().get("readiness_model", {}).get("rating_scale", []):
        if row["min"] <= score <= row["max"]:
            return row
    return {
        "min": 0,
        "max": 100,
        "label": "Not Ready",
        "description": "Build the foundations and start the pathway workbooks.",
    }


def build_role_readiness(
    db: Session,
    user: User,
    role_id: str,
    summary: dict | None = None,
    assessment: dict | None = None,
) -> dict:
    role = _role(role_id)
    if role is None:
        raise ValueError("Unknown role")

    profile = assessment or build_competency_assessment_profile(db, user)
    competencies = _flatten_competencies(profile)
    critical = []
    for competency_id in role.get("critical_competencies", []):
        competency = competencies.get(competency_id)
        if competency is None:
            continue
        assessment = competency.get("assessment") or {}
        domain = competency["domain"]
        level, target = _target_for(role, domain)
        score = assessment.get("score")
        coverage = min((score or 0) / target, 1.0) if score is not None else 0.0
        dimensions = {
            dimension["key"]: dimension.get("score")
            for dimension in assessment.get("dimensions", [])
        }
        critical.append(
            {
                "id": competency["id"],
                "name": competency["name"],
                "domain": domain,
                "domain_label": competency["domain_label"],
                "category": competency["category"],
                "category_label": competency["category_label"],
                "target_level": level,
                "target_score": target,
                "score": score,
                "coverage": coverage,
                "level": assessment.get("level", {}),
                "evidence_count": competency.get("evidence_count", 0),
                "workbook_count": competency.get("workbook_count", 0),
                "capstone_count": competency.get("capstone_count", 0),
                "clean_solves": competency.get("clean_solves", 0),
                "awarded": bool(assessment.get("awarded")),
                "provisional": bool(assessment.get("provisional")),
                "status": _status(score, target, bool(assessment.get("awarded"))),
                "colour": _colour(score, target),
                "dimensions": dimensions,
            }
        )

    domain_rows = _domain_rows(role, critical)
    gap_ids = {row["id"] for row in critical if row["status"] in {"gap", "no_evidence"}}
    completed_ids = {
        int(item["lab_id"])
        for item in ((summary or {}).get("completions") or [])
        if item.get("lab_id") is not None
    }

    components = {
        "workbook": _average_dimension(critical, "documentation"),
        "lab_assessment": _average_dimension(critical, "execution"),
        "independent": _average_dimension(critical, "troubleshooting"),
        "scenario": _average_dimension(critical, "communication"),
    }
    capstone_done = _capstone_completed(role, summary)
    components["capstone"] = 100.0 if capstone_done else 0.0
    weights = load_roles().get("readiness_model", {}).get("components", {})
    weighted = 0.0
    provisional = []
    for key, weight in weights.items():
        value = components.get(key)
        if value is None:
            provisional.append(key)
            continue
        weighted += float(weight) * value
    readiness_score = round(weighted, 1)
    rating = _rating(readiness_score)
    threshold = int(role.get("career_ready_threshold", DEFAULT_THRESHOLD))
    floor = int(role.get("domain_floor", DEFAULT_FLOOR))
    career_ready = (
        readiness_score >= threshold
        and all(row["score"] >= floor for row in domain_rows)
    )

    competency_scores = {
        competency_id: (competency.get("assessment") or {}).get("score")
        for competency_id, competency in competencies.items()
    }
    competency_names = {
        competency_id: competency["name"]
        for competency_id, competency in competencies.items()
    }
    next_labs = _next_labs(
        db,
        role,
        gap_ids,
        completed_ids,
        competency_scores,
        competency_names,
    )
    capstone_lab = _capstone_lab(db, role, completed_ids)
    capstone_meta = role.get("capstone") or {}

    have = [row for row in critical if row["status"] == "have"]
    building = [row for row in critical if row["status"] == "building"]
    gaps = [row for row in critical if row["status"] in {"gap", "no_evidence"}]

    if next_labs:
        first = next_labs[0]
        next_action = (
            f"Complete {first['name']} to strengthen "
            f"{', '.join(first['competencies'][:2])}."
        )
    elif capstone_lab and not capstone_lab["completed"]:
        next_action = f"Attempt the {capstone_meta.get('title') or capstone_lab['name']} capstone."
    elif career_ready:
        next_action = "Download the professional portfolio and review the evidence with a mentor."
    else:
        next_action = "Complete one more role-relevant exercise and record the evidence."

    pipeline = [
        {
            "key": "skills_earned",
            "label": "Skills Earned",
            "value": len(have) + len(building),
            "detail": f"{len(have)} at target · {len(building)} building",
            "state": "complete" if have else "in_progress",
            "colour": "green" if have else "amber",
        },
        {
            "key": "evidence_collected",
            "label": "Evidence Collected",
            "value": sum(row["evidence_count"] for row in critical),
            "detail": "completions mapped to critical competencies",
            "state": "complete" if any(row["workbook_count"] for row in critical) else "in_progress",
            "colour": "green" if any(row["workbook_count"] for row in critical) else "amber",
        },
        {
            "key": "competencies_validated",
            "label": "Competencies Validated",
            "value": sum(1 for row in critical if row["awarded"]),
            "detail": f"{len(critical)} critical competencies",
            "state": "complete" if critical and all(row["awarded"] for row in critical) else "in_progress",
            "colour": "green" if critical and all(row["awarded"] for row in critical) else "amber",
        },
        {
            "key": "career_readiness",
            "label": "Career Readiness",
            "value": readiness_score,
            "detail": rating["label"],
            "state": "complete" if career_ready else "in_progress",
            "colour": "green" if career_ready else "amber",
        },
        {
            "key": "employment_outcomes",
            "label": "Employment Outcomes",
            "value": "Portfolio ready" if career_ready else "Not tracked",
            "detail": "The platform does not track employment outcomes; the transcript is the shareable evidence.",
            "state": "complete" if career_ready else "in_progress",
            "colour": "green" if career_ready else "grey",
        },
    ]

    return {
        "role": {
            "id": role["id"],
            "title": role["title"],
            "family": role.get("family"),
            "flagship": bool(role.get("flagship")),
            "summary": role.get("summary"),
            "aliases": role.get("aliases", []),
            "level_requirements": role.get("level_requirements", {}),
        },
        "readiness": {
            "score": readiness_score,
            "rating": rating,
            "career_ready": career_ready,
            "threshold": threshold,
            "domain_floor": floor,
            "components": components,
            "provisional_components": provisional,
            "weights": weights,
            "component_sources": {
                "workbook": "Documentation evidence from workbook submissions",
                "lab_assessment": "Execution evidence from hands-on labs",
                "independent": "Troubleshooting evidence from independent work",
                "scenario": "Communication evidence from reports and briefings",
                "capstone": "Completed capstone evidence",
            },
        },
        "domains": domain_rows,
        "skills_have": have,
        "skills_building": building,
        "skills_gap": gaps,
        "next_workbooks": next_labs,
        "capstone": {
            **capstone_meta,
            "lab": capstone_lab,
            "completed": capstone_done,
        },
        "certifications": role.get("certifications", {}),
        "evidence": {
            "completed_role_labs": len(
                [
                    item
                    for item in ((summary or {}).get("completions") or [])
                    if str(item.get("track_slug") or "").lower()
                    in {str(track).lower() for track in role.get("tracks", [])}
                ]
            ),
            "clean_solves": sum(row.get("clean_solves", 0) for row in critical),
            "capstones_completed": 1 if capstone_done else 0,
            "certificates": len((summary or {}).get("certificates") or []),
            "work_samples": [
                {
                    "name": item.get("lab_name"),
                    "track": item.get("track_name"),
                    "difficulty": item.get("difficulty"),
                    "completed_at": item.get("completed_at"),
                }
                for item in ((summary or {}).get("completions") or [])[:3]
            ],
        },
        "pipeline": pipeline,
        "next_action": next_action,
        "disclaimer": (
            "Readiness is a curriculum coverage estimate from the available "
            "evidence. It is not a grade, a hiring decision, or a prediction of "
            "employment. The platform does not track employment outcomes."
        ),
    }
