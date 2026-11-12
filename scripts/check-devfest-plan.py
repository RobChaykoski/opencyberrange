"""Validate the DevFest Cyber Discovery plan against the curriculum data.

Checks that every competency and career path named in the plan exists in the
taxonomy and roles files, that ids are unique, and that the privacy and
certificate sections are present.

Usage:
    python scripts/check-devfest-plan.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "platform" / "backend" / "app" / "data"
PLAN = DATA / "devfest-2027.yaml"
TAXONOMY = DATA / "competency-taxonomy.yaml"
ROLES = DATA / "curriculum-roles.yaml"


def _competency_ids() -> set[str]:
    data = yaml.safe_load(TAXONOMY.read_text(encoding="utf-8")) or {}
    return {
        competency["id"]
        for domain in data.get("domains", [])
        for category in domain.get("categories", [])
        for competency in category.get("competencies", [])
    }


def _role_ids() -> set[str]:
    data = yaml.safe_load(ROLES.read_text(encoding="utf-8")) or {}
    return {role["id"] for role in data.get("pathways", [])}


def validate() -> list[str]:
    problems: list[str] = []
    if not PLAN.exists():
        return [f"{PLAN} is missing"]
    plan = yaml.safe_load(PLAN.read_text(encoding="utf-8")) or {}
    competencies = _competency_ids()
    roles = _role_ids()

    event = plan.get("event") or {}
    for field in ("name", "tagline", "duration_hours", "certificate"):
        if not event.get(field):
            problems.append(f"event.{field} is missing")
    certificate = event.get("certificate") or {}
    if not certificate.get("id_prefix"):
        problems.append("event.certificate.id_prefix is missing")

    seen: set[str] = set()
    for session in plan.get("sessions", []):
        for exercise in session.get("exercises", []):
            exercise_id = exercise.get("id")
            if exercise_id in seen:
                problems.append(f"duplicate exercise id {exercise_id}")
            seen.add(exercise_id)
            for competency in exercise.get("competencies", []):
                if competency not in competencies:
                    problems.append(f"{exercise_id}: unknown competency {competency}")
            for path in exercise.get("career_paths", []):
                if path not in roles:
                    problems.append(f"{exercise_id}: unknown career path {path}")
        for pathway in session.get("pathways", []):
            if pathway.get("id") not in roles:
                problems.append(f"unknown pathway {pathway.get('id')}")
            for competency in pathway.get("competencies", []):
                if competency not in competencies:
                    problems.append(f"{pathway.get('id')}: unknown competency {competency}")

    for concept in plan.get("top_concepts", []):
        for competency in concept.get("competencies", []):
            if competency not in competencies:
                problems.append(f"{concept.get('id')}: unknown competency {competency}")

    if not plan.get("privacy"):
        problems.append("privacy rules are missing")
    if not plan.get("outputs", {}).get("learner"):
        problems.append("learner outputs are missing")
    return problems


def main() -> int:
    problems = validate()
    print("DevFest plan check")
    print("=" * 40)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        print(f"FAIL ({len(problems)} problem(s))")
        return 1
    print("PASS: competencies, career paths, and required sections are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
