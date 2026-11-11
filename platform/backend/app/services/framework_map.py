"""Resolve selective framework alignment for each lab."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

from app.config import settings


def _path() -> Path:
    configured = getattr(settings, "CURRICULUM_FRAMEWORKS_PATH", None)
    if configured:
        return Path(configured)
    container = Path("/app/curriculum-frameworks.yaml")
    if container.is_file():
        return container
    try:
        return Path(__file__).resolve().parents[4] / "curriculum-frameworks.yaml"
    except IndexError:
        return container


@lru_cache(maxsize=1)
def load_map() -> dict:
    path = _path()
    if not path.is_file():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


@lru_cache(maxsize=1)
def framework_ids() -> set[str]:
    return {
        str(item.get("id"))
        for item in load_map().get("frameworks", [])
        if item.get("id")
    }


@lru_cache(maxsize=1)
def competency_ids() -> set[str]:
    return {
        str(item.get("id"))
        for item in load_map().get("competencies", [])
        if item.get("id")
    }


def _clean_outcome(value: Optional[str]) -> Optional[str]:
    text = " ".join(str(value or "").split()).strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered.startswith(("submit the correct flag", "capture the flag")):
        return None
    return text


def resolve(
    lab_slug: str,
    chapter_id: Optional[str],
    lab_data: dict,
) -> dict:
    """Resolve one competency, 1–2 framework refs, and one measurable outcome."""
    data = load_map()
    chapter_defaults = data.get("chapter_defaults", {})
    lab_overrides = data.get("lab_overrides", {})

    chapter = chapter_defaults.get(str(chapter_id or ""), {}) or {}
    override = lab_overrides.get(lab_slug, {}) or {}

    primary = (
        lab_data.get("primary_competency")
        or override.get("primary_competency")
        or chapter.get("primary_competency")
    )
    refs = (
        lab_data.get("framework_refs")
        or override.get("framework_refs")
        or chapter.get("framework_refs")
        or []
    )
    if isinstance(refs, str):
        refs = [refs]
    refs = list(dict.fromkeys(str(item) for item in refs if item))[:2]

    outcome = _clean_outcome(lab_data.get("measurable_outcome"))
    if not outcome:
        for item in lab_data.get("learning_outcomes") or []:
            outcome = _clean_outcome(item)
            if outcome:
                break
    if not outcome:
        title = lab_data.get("title") or lab_data.get("name") or lab_slug
        outcome = (
            f"Complete {title} and record one observation, one interpretation, "
            "and a confidence level."
        )

    return {
        "primary_competency": primary,
        "framework_refs": refs,
        "measurable_outcome": outcome,
    }


def validate_resolved(lab_slug: str, resolved: dict) -> list[str]:
    problems = []
    primary = resolved.get("primary_competency")
    refs = resolved.get("framework_refs") or []
    outcome = resolved.get("measurable_outcome")
    if primary not in competency_ids():
        problems.append(f"{lab_slug}: unknown primary competency {primary!r}")
    if not (1 <= len(refs) <= 2):
        problems.append(f"{lab_slug}: expected 1–2 framework refs, got {len(refs)}")
    for ref in refs:
        if ref not in framework_ids():
            problems.append(f"{lab_slug}: unknown framework ref {ref!r}")
    if not outcome or len(str(outcome)) < 15:
        problems.append(f"{lab_slug}: measurable outcome is missing or too short")
    return problems
