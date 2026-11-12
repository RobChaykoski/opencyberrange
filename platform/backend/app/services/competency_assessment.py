"""Measurable competency assessment on top of the taxonomy evidence.

Each competency is scored across five weighted dimensions:

* Knowledge (20%) -- quiz or test
* Execution (30%) -- hands-on lab
* Troubleshooting (20%) -- independent challenge
* Documentation (15%) -- workbook submission
* Communication (15%) -- report or briefing

The platform currently measures some dimensions with proxies. A completion is
not an award by itself: a competency is only marked as awarded when the score
clears the threshold and the evidence requirement is met. The API labels
provisional scores so a learner or reviewer can see what is still missing.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml
from sqlalchemy.orm import Session, joinedload

from app.models import ExerciseQuizAttempt, Lab, Level, User
from app.services.competency_taxonomy import (
    build_competency_profile,
    competencies_for_lab,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ASSESSMENT_FILE = DATA_DIR / "competency-assessment.yaml"

DIMENSION_ORDER = ("knowledge", "execution", "troubleshooting", "documentation", "communication")
DIMENSION_LABELS = {
    "knowledge": "Knowledge",
    "execution": "Execution",
    "troubleshooting": "Troubleshooting",
    "documentation": "Documentation",
    "communication": "Communication",
}
DIMENSION_WEIGHTS = {
    "knowledge": 0.20,
    "execution": 0.30,
    "troubleshooting": 0.20,
    "documentation": 0.15,
    "communication": 0.15,
}

_assessment_cache: dict | None = None


def load_assessment() -> dict:
    global _assessment_cache
    if _assessment_cache is None:
        with ASSESSMENT_FILE.open("r", encoding="utf-8") as handle:
            _assessment_cache = yaml.safe_load(handle) or {}
    return _assessment_cache


def assessment_for(competency_id: str) -> dict:
    framework = load_assessment()
    specific = framework.get("competencies", {}).get(competency_id)
    if specific:
        return specific
    return framework.get("generic_rubric", {})


def _level_for(score: float | None) -> dict:
    if score is None:
        return {
            "id": "no_evidence",
            "label": "No evidence yet",
            "badge": None,
            "description": "No assessment evidence yet.",
        }
    for level in load_assessment().get("proficiency_levels", []):
        if level["min"] <= score <= level["max"]:
            return level
    return {
        "id": "awareness",
        "label": "Awareness",
        "badge": None,
        "description": "Can explain concepts.",
    }


def _quiz_scores(db: Session, user_id: int) -> dict[str, list[int]]:
    rows = (
        db.query(ExerciseQuizAttempt)
        .options(
            joinedload(ExerciseQuizAttempt.lab)
            .joinedload(Lab.level)
            .joinedload(Level.track)
        )
        .filter(
            ExerciseQuizAttempt.user_id == user_id,
            ExerciseQuizAttempt.completed_at.isnot(None),
        )
        .all()
    )
    best_by_lab: dict[int, int] = {}
    labs: dict[int, Lab] = {}
    for row in rows:
        if row.lab is None:
            continue
        labs[row.lab_id] = row.lab
        best_by_lab[row.lab_id] = max(best_by_lab.get(row.lab_id, 0), row.score or 0)

    scores: dict[str, list[int]] = defaultdict(list)
    for lab_id, score in best_by_lab.items():
        for competency_id in competencies_for_lab(labs.get(lab_id)):
            scores[competency_id].append(score)
    return scores


def _dimension_scores(row: dict, quiz_scores: list[int]) -> dict:
    count = int(row.get("evidence_count") or 0)
    clean = int(row.get("clean_solves") or 0)
    advanced = int(row.get("advanced_labs") or 0)
    workbook = int(row.get("workbook_count") or 0)
    capstone = int(row.get("capstone_count") or 0)
    first_attempt = int(row.get("first_attempt_count") or 0)

    knowledge = round(sum(quiz_scores) / len(quiz_scores), 1) if quiz_scores else None
    execution = min(100, count * 20 + clean * 10 + advanced * 10) if count else None
    troubleshooting = (
        min(100, round((clean / count) * 100) + min(advanced * 5, 20))
        if count
        else None
    )
    documentation = round((workbook / count) * 100, 1) if count else None
    if capstone:
        communication = 100
    elif count >= 3:
        communication = 50
    else:
        communication = 0 if count else None

    return {
        "knowledge": knowledge,
        "execution": execution,
        "troubleshooting": troubleshooting,
        "documentation": documentation,
        "communication": communication,
        "first_attempt_rate": round((first_attempt / count) * 100, 1) if count else 0.0,
    }


def _weighted_score(dimensions: dict) -> tuple[float | None, float, bool]:
    available_weight = 0.0
    weighted = 0.0
    for key in DIMENSION_ORDER:
        value = dimensions.get(key)
        if value is None:
            continue
        weight = DIMENSION_WEIGHTS[key]
        available_weight += weight
        weighted += weight * value
    if available_weight <= 0:
        return None, 0.0, False
    return round(weighted / available_weight, 1), round(available_weight, 2), available_weight < 0.999


def build_competency_assessment_profile(db: Session, user: User) -> dict:
    """Return the taxonomy profile with per-competency assessment scores."""
    profile = build_competency_profile(db, user)
    quiz_by_competency = _quiz_scores(db, user.id)
    scored = []
    awarded = 0
    provisional = 0

    for domain in profile["domains"]:
        for category in domain["categories"]:
            for competency in category["competencies"]:
                dimensions = _dimension_scores(
                    competency,
                    quiz_by_competency.get(competency["id"], []),
                )
                score, coverage, is_provisional = _weighted_score(dimensions)
                level = _level_for(score)
                evidence_met = bool(
                    (competency.get("workbook_count") or 0) >= 1
                    or (competency.get("capstone_count") or 0) >= 1
                )
                is_awarded = bool(
                    score is not None and score >= 60 and evidence_met
                )
                if is_awarded:
                    awarded += 1
                if is_provisional:
                    provisional += 1
                competency["assessment"] = {
                    "score": score,
                    "coverage_pct": round(coverage * 100, 1),
                    "provisional": is_provisional,
                    "level": level,
                    "evidence_met": evidence_met,
                    "awarded": is_awarded,
                    "dimensions": [
                        {
                            "key": key,
                            "label": DIMENSION_LABELS[key],
                            "weight": DIMENSION_WEIGHTS[key],
                            "score": dimensions.get(key),
                            "available": dimensions.get(key) is not None,
                            "method": assessment_for(competency["id"])
                            .get(key, {})
                            .get("assessment")
                            or load_assessment().get("generic_rubric", {})
                            .get(key, {})
                            .get("assessment"),
                        }
                        for key in DIMENSION_ORDER
                    ],
                    "first_attempt_rate": dimensions["first_attempt_rate"],
                    "rubric": assessment_for(competency["id"]),
                }
                if score is not None:
                    scored.append(score)

    return {
        **profile,
        "summary": {
            **profile["summary"],
            "competencies_assessed": len(scored),
            "competencies_awarded": awarded,
            "competencies_provisional": provisional,
            "average_score": round(sum(scored) / len(scored), 1) if scored else None,
        },
        "assessment_model": {
            "dimensions": load_assessment().get("dimensions", []),
            "proficiency_levels": load_assessment().get("proficiency_levels", []),
            "evidence_requirements": load_assessment().get("evidence_requirements", []),
        },
        "disclaimer": (
            "Assessment scores use the available evidence. Written submissions and "
            "live briefings are future evidence types, so a score can be provisional. "
            "A competency is awarded only when the score threshold and evidence "
            "requirement are both met. This is not a grade or a hiring prediction."
        ),
    }
