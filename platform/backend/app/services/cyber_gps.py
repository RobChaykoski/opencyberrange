"""Cybersecurity GPS: optional direction finding from evidence and interest.

The GPS answers "where am I, where could I go, and what should I try next?"
It uses the learner's competency assessment, recent growth, and optional answers.
Answers are used only for the current view and are not stored.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app.models import User
from app.services.competency_assessment import build_competency_assessment_profile
from app.services.role_readiness import build_role_readiness, load_roles

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
GPS_FILE = DATA_DIR / "cyber-gps.yaml"

_gps_cache: dict | None = None


def load_gps() -> dict:
    global _gps_cache
    if _gps_cache is None:
        with GPS_FILE.open("r", encoding="utf-8") as handle:
            _gps_cache = yaml.safe_load(handle) or {}
    return _gps_cache


def _questions_public() -> list[dict]:
    return [
        {
            "id": question["id"],
            "prompt": question["prompt"],
            "help": question.get("help"),
            "optional": True,
            "options": [
                {"id": option["id"], "label": option["label"]}
                for option in question.get("options", [])
            ],
        }
        for question in load_gps().get("questions", [])
    ]


def _valid_answers(answers: dict | None) -> dict[str, str]:
    if not answers:
        return {}
    valid = {}
    for question in load_gps().get("questions", []):
        value = answers.get(question["id"])
        if value and any(option["id"] == value for option in question.get("options", [])):
            valid[question["id"]] = value
    return valid


def _interest_scores(answers: dict[str, str]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for question in load_gps().get("questions", []):
        selected = answers.get(question["id"])
        if not selected:
            continue
        option = next(
            (item for item in question.get("options", []) if item["id"] == selected),
            None,
        )
        if option is None:
            continue
        for role_id, weight in (option.get("weights") or {}).items():
            scores[role_id] = scores.get(role_id, 0.0) + float(weight)
    return scores


def _flatten(profile: dict) -> dict[str, dict]:
    rows = {}
    for domain in profile.get("domains", []):
        for category in domain.get("categories", []):
            for competency in category.get("competencies", []):
                rows[competency["id"]] = competency
    return rows


def _fit_label(score: float) -> tuple[str, str]:
    if score >= 75:
        return "Strong fit", "green"
    if score >= 50:
        return "Worth exploring", "amber"
    return "Stretch direction", "red"


def build_gps(
    db: Session,
    user: User,
    answers: dict | None = None,
    summary: dict | None = None,
) -> dict:
    answers = _valid_answers(answers)
    assessment = build_competency_assessment_profile(db, user)
    competency_by_id = _flatten(assessment)
    roles = load_roles().get("pathways", [])
    role_ids = [
        role["id"]
        for role in roles
        if role.get("flagship")
        or role["id"]
        in {
            "penetration-tester",
            "dfir-analyst",
            "cloud-security-analyst",
            "ai-security-analyst",
        }
    ]
    interest = _interest_scores(answers)
    interest_max = max(interest.values(), default=0.0)

    directions = []
    for role_id in role_ids:
        readiness = build_role_readiness(
            db,
            user,
            role_id,
            summary=summary,
            assessment=assessment,
        )
        role = readiness["role"]
        critical_ids = [
            competency_id
            for competency_id in next(
                (
                    item.get("critical_competencies", [])
                    for item in roles
                    if item["id"] == role_id
                ),
                [],
            )
            if competency_id in competency_by_id
        ]
        recent = sum(
            int(competency_by_id[competency_id].get("recent_count") or 0)
            for competency_id in critical_ids
        )
        growth = (
            min(100.0, (recent / max(1, len(critical_ids))) * 25)
            if critical_ids
            else 0.0
        )
        evidence = float(readiness["readiness"]["score"] or 0)
        role_interest = (
            interest.get(role_id, 0.0) / interest_max * 100
            if interest_max
            else None
        )
        if role_interest is None:
            fit = 0.75 * evidence + 0.25 * growth
        else:
            fit = 0.55 * evidence + 0.25 * role_interest + 0.20 * growth
        fit = round(fit, 1)
        label, colour = _fit_label(fit)
        top_domains = readiness["domains"][:2]
        why = [
            f"{domain['label']} evidence is {domain['score']}% of the pathway target."
            for domain in top_domains
        ]
        if role_interest is not None and role_interest > 0:
            why.append("Your answers point toward this kind of work.")
        if growth > 0:
            why.append(f"You have {recent} recent completion(s) in this pathway.")
        next_lab = (readiness.get("next_workbooks") or [None])[0]
        next_experiment = (
            f"Try {next_lab['name']}."
            if next_lab
            else f"Review the {readiness['capstone'].get('title') or 'capstone'} brief."
        )
        directions.append(
            {
                "role_id": role_id,
                "title": role["title"],
                "family": role.get("family"),
                "flagship": role.get("flagship"),
                "fit_score": fit,
                "fit_label": label,
                "colour": colour,
                "evidence_score": evidence,
                "interest_score": round(role_interest, 1) if role_interest is not None else None,
                "growth_score": round(growth, 1),
                "why": why,
                "next_experiment": next_experiment,
                "readiness_rating": readiness["readiness"]["rating"]["label"],
            }
        )

    directions.sort(key=lambda row: (-row["fit_score"], row["title"]))

    domains = assessment.get("domains", [])
    top_domains = sorted(
        [
            {
                "key": domain["id"],
                "label": domain["label"],
                "score": round(
                    sum(
                        (competency.get("assessment") or {}).get("score") or 0
                        for category in domain["categories"]
                        for competency in category["competencies"]
                    )
                    / max(
                        1,
                        sum(
                            1
                            for category in domain["categories"]
                            for competency in category["competencies"]
                            if (competency.get("assessment") or {}).get("score") is not None
                        ),
                    ),
                    1,
                ),
                "evidence_count": domain["evidence_count"],
                "recent_count": sum(
                    int(competency.get("recent_count") or 0)
                    for category in domain["categories"]
                    for competency in category["competencies"]
                ),
                "colour": "green"
                if domain["evidence_count"] >= 8
                else "amber"
                if domain["evidence_count"] >= 3
                else "red"
                if domain["evidence_count"] > 0
                else "grey",
            }
            for domain in domains
        ],
        key=lambda row: (-row["score"], -row["evidence_count"]),
    )[:4]

    strongest = sorted(
        [
            {
                "id": competency["id"],
                "name": competency["name"],
                "domain": competency["domain_label"],
                "score": (competency.get("assessment") or {}).get("score"),
                "level": (competency.get("assessment") or {}).get("level", {}).get("label"),
            }
            for competency in competency_by_id.values()
            if (competency.get("assessment") or {}).get("score") is not None
        ],
        key=lambda row: (-(row["score"] or 0), row["name"]),
    )[:5]

    time_choice = answers.get("time")
    pace = load_gps().get("pace", {}).get(time_choice) if time_choice else None
    top = directions[0] if directions else None

    return {
        "version": load_gps().get("version"),
        "answers_received": bool(answers),
        "answers_note": (
            "Answers are used for this view only and are not saved. Skip any "
            "question; the evidence-only view still works."
        ),
        "questions": _questions_public(),
        "where_you_are": {
            "top_domains": top_domains,
            "strongest_competencies": strongest,
            "competencies_with_evidence": assessment["summary"].get(
                "competencies_with_evidence", 0
            ),
            "evidence_total": sum(
                int(competency.get("evidence_count") or 0)
                for competency in competency_by_id.values()
            ),
            "recent_total": sum(
                int(competency.get("recent_count") or 0)
                for competency in competency_by_id.values()
            ),
        },
        "growth": {
            "recent_domains": [
                row for row in top_domains if row["recent_count"] > 0
            ],
            "note": (
                "Recent means a completion in the last 30 days. Growth is a "
                "practice signal, not a prediction."
            ),
        },
        "pace": pace,
        "directions": directions[:4],
        "next_step": top["next_experiment"] if top else "Complete one exercise to start the map.",
        "disclaimer": (
            "The GPS is a direction aid. It combines practice evidence, recent "
            "activity, and optional answers. It is not a grade, a ranking, or a "
            "prediction of employment."
        ),
    }
