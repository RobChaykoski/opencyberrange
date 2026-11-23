"""Versioned rubric registry for Release 6 evidence review.

A rubric is data. It states the criteria, their weights, and observable level
descriptors. Evidence records keep the rubric id and version they were judged
against; editing a rubric never rewrites an old decision.

The registry is intentionally read-only at runtime. A new rubric version is a
new file, reviewed like any other curriculum change.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "rubrics"
ALLOWED_EVIDENCE_TYPES = {
    "flag",
    "validation_step",
    "workbook",
    "analyst_answer",
    "quiz",
    "artifact",
    "capstone",
    "instructor",
}
REQUIRED_LEVELS = {0, 1, 2, 3}
WEIGHT_EPSILON = 1e-6


@lru_cache(maxsize=1)
def load_rubrics() -> dict[str, dict]:
    rubrics: dict[str, dict] = {}
    if not DATA_DIR.is_dir():
        return rubrics
    for path in sorted(DATA_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as handle:
            document = yaml.safe_load(handle) or {}
        rubric_id = str(document.get("rubric") or "")
        if rubric_id:
            rubrics[rubric_id] = document
    return rubrics


def get_rubric(rubric_id: str, version: str | None = None) -> dict | None:
    document = load_rubrics().get(rubric_id)
    if document is None:
        return None
    if version is not None and str(document.get("version")) != str(version):
        return None
    return document


def rubric_reference(rubric_id: str, version: str | None = None) -> dict | None:
    document = get_rubric(rubric_id, version)
    if document is None:
        return None
    return {
        "rubric": document.get("rubric"),
        "version": str(document.get("version")),
        "title": document.get("title"),
        "evidence_types": list(document.get("evidence_types") or []),
    }


def validate_rubrics() -> list[str]:
    problems: list[str] = []
    seen: set[tuple[str, str]] = set()
    for path in sorted(DATA_DIR.glob("*.yaml")) if DATA_DIR.is_dir() else []:
        with path.open(encoding="utf-8") as handle:
            document = yaml.safe_load(handle) or {}
        label = path.name
        rubric_id = str(document.get("rubric") or "").strip()
        version = str(document.get("version") or "").strip()
        if not rubric_id:
            problems.append(f"{label}: missing rubric id")
            continue
        if not version:
            problems.append(f"{label}: missing version")
        if (rubric_id, version) in seen:
            problems.append(f"{label}: duplicate rubric {rubric_id} version {version}")
        seen.add((rubric_id, version))
        if rubric_id != path.stem:
            problems.append(f"{label}: file name should match the rubric id")

        evidence_types = {str(item) for item in document.get("evidence_types") or []}
        if not evidence_types:
            problems.append(f"{label}: missing evidence_types")
        unknown_types = evidence_types - ALLOWED_EVIDENCE_TYPES
        if unknown_types:
            problems.append(f"{label}: unknown evidence types {sorted(unknown_types)}")

        criteria = document.get("criteria") or []
        if not criteria:
            problems.append(f"{label}: no criteria")
            continue
        total = 0.0
        seen_criteria: set[str] = set()
        for criterion in criteria:
            if not isinstance(criterion, dict):
                problems.append(f"{label}: malformed criterion")
                continue
            criterion_id = str(criterion.get("id") or "").strip()
            if not criterion_id:
                problems.append(f"{label}: criterion missing id")
            elif criterion_id in seen_criteria:
                problems.append(f"{label}: duplicate criterion {criterion_id}")
            seen_criteria.add(criterion_id)
            if not criterion.get("label"):
                problems.append(f"{label}: criterion {criterion_id} missing label")
            try:
                total += float(criterion.get("weight") or 0)
            except (TypeError, ValueError):
                problems.append(f"{label}: criterion {criterion_id} has a non-numeric weight")
            levels = criterion.get("levels") or {}
            numeric_levels = {int(level) for level in levels} if isinstance(levels, dict) else set()
            if numeric_levels != REQUIRED_LEVELS:
                problems.append(f"{label}: criterion {criterion_id} levels must be 0..3")
            if isinstance(levels, dict):
                for level, descriptor in levels.items():
                    if not str(descriptor or "").strip():
                        problems.append(f"{label}: criterion {criterion_id} level {level} is empty")
        if abs(total - 1.0) > WEIGHT_EPSILON:
            problems.append(f"{label}: criteria weights sum to {total}")
    return problems
