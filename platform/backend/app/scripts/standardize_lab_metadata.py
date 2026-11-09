#!/usr/bin/env python3
"""Standardize lab.yaml metadata across the curriculum.

The canonical lab header is:

    title
    category
    difficulty
    estimated_time
    prerequisites
    learning_outcomes
    mapped_skills
    assessment_criteria

The script is idempotent and line-oriented so it can add/update those eight
keys without reformatting the rest of a hand-authored lab. Run it from the
repository root:

    python platform/backend/app/scripts/standardize_lab_metadata.py --check
    python platform/backend/app/scripts/standardize_lab_metadata.py --write

``--check`` exits 1 when any lab is out of date or missing a required field.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict

import yaml

try:
    from app.services.competency_model import AXIS_KEYS
except Exception:  # pragma: no cover - allows running without PYTHONPATH
    AXIS_KEYS = (
        "network_systems",
        "web_api",
        "identity_access",
        "incident_forensics",
        "osint",
        "malware",
        "ot_ics",
        "ai_security",
    )

DEFAULT_LABS_ROOT = os.path.join("platform", "labs")
REQUIRED_KEYS = (
    "title",
    "category",
    "difficulty",
    "estimated_time",
    "prerequisites",
    "learning_outcomes",
    "mapped_skills",
    "assessment_criteria",
)
LEGACY_KEYS = (
    "name",
    "duration_minutes",
    "objectives",
    "learning_objectives",
)
REMOVE_KEYS = set(REQUIRED_KEYS) | set(LEGACY_KEYS)
VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
CATEGORY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

DEFAULT_ASSESSMENT = (
    "Submit the correct flag.",
    "Pass every automated test step in the lab manifest.",
)


def _load_naming():
    try:
        from app.services.lab_naming import parse_lab_slug
        return parse_lab_slug
    except Exception:  # pragma: no cover
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from app.services.lab_naming import parse_lab_slug
        return parse_lab_slug


parse_lab_slug = _load_naming()


def _normalise_outcome(value: str) -> str:
    text = " ".join(str(value).split()).strip()
    text = re.sub(r"^[-*]\s*", "", text)
    text = text.rstrip(".")
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    return text


def _mapped_skills(track: str, level: int, category: str) -> list[str]:
    """Map a lab to the platform's eight competency axes.

    The mapping is deliberately conservative: one to three axes, matching the
    existing competency heuristic but explicit and reviewable in the lab.
    """
    track = (track or "").lower()
    category = (category or "").lower()
    if track == "windows":
        if level <= 1:
            return ["network_systems"]
        if level == 6:
            return ["identity_access", "web_api", "network_systems"]
        return ["identity_access", "network_systems"]
    if track == "linux":
        if level >= 5:
            return ["incident_forensics", "network_systems"]
        if level >= 3:
            return ["identity_access", "network_systems"]
        return ["network_systems", "identity_access"]
    if track == "web":
        return ["web_api"]
    if track == "software-security":
        return ["web_api", "network_systems"]
    if track == "forensics":
        return ["incident_forensics"]
    if track == "osint":
        return ["osint"]
    if track == "malware":
        return ["malware", "incident_forensics"]
    if track == "ot":
        return ["ot_ics"]
    if track == "ai":
        return ["ai_security"]
    if track == "high-school":
        if level >= 12:
            return [
                "web_api",
                "identity_access",
                "network_systems",
                "incident_forensics",
            ]
        if level >= 11:
            return ["incident_forensics", "network_systems"]
        return ["network_systems", "identity_access", "web_api"]
    if track == "network":
        if category == "network-analysis":
            return ["network_systems", "incident_forensics"]
        return ["network_systems"]
    # Unknown tracks still get a valid axis so analytics never drops the lab.
    return ["network_systems"]


def _iter_labs(root: str):
    for dirpath, _dirs, files in os.walk(root):
        if "lab.yaml" in files:
            yield os.path.join(dirpath, "lab.yaml")


def _read_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _build_catalog(root: str):
    catalog = []
    for path in sorted(_iter_labs(root)):
        data = _read_yaml(path)
        slug = os.path.basename(os.path.dirname(path))
        track, level, lab_num = parse_lab_slug(slug)
        if not track or level is None or lab_num is None:
            raise ValueError(f"Cannot parse curriculum position for {path}")
        catalog.append({
            "path": path,
            "slug": slug,
            "track": track,
            "level": level,
            "lab_num": lab_num,
            "data": data,
        })
    return catalog


def _prerequisite_map(catalog):
    groups = defaultdict(lambda: defaultdict(list))
    for item in catalog:
        groups[item["track"]][item["level"]].append(item)
    for levels in groups.values():
        for items in levels.values():
            items.sort(key=lambda i: (i["lab_num"], i["slug"]))

    result = {}
    for _track, levels in groups.items():
        level_numbers = sorted(levels)
        for position, level in enumerate(level_numbers):
            items = levels[level]
            for index, item in enumerate(items):
                if index > 0:
                    result[item["slug"]] = [items[index - 1]["slug"]]
                    continue
                if position == 0:
                    result[item["slug"]] = []
                    continue
                previous_level = level_numbers[position - 1]
                if previous_level == 0:
                    # Level 0 is optional and must not gate the first graded level.
                    result[item["slug"]] = []
                    continue
                result[item["slug"]] = [
                    prev["slug"] for prev in levels[previous_level]
                ]
    return result


def _metadata_for(item, prerequisites):
    data = item["data"]
    title = str(data.get("title") or data.get("name") or item["slug"]).strip()
    category = str(data.get("category") or "general").strip().lower()
    difficulty = str(data.get("difficulty") or "beginner").strip().lower()
    raw_time = data.get("estimated_time", data.get("duration_minutes", 60))
    try:
        estimated_time = int(raw_time)
    except (TypeError, ValueError):
        estimated_time = 60

    outcomes = data.get("learning_objectives") or data.get("objectives") or []
    normalized = []
    seen = set()
    for outcome in outcomes:
        text = _normalise_outcome(outcome)
        if not text or text.lower() in seen:
            continue
        # Flag capture is the assessment, not a learning outcome.
        if re.match(r"^(capture|submit|find|get) the flag\b", text, re.I):
            continue
        seen.add(text.lower())
        normalized.append(text)
    if not normalized:
        normalized = ["Complete the lab scenario and explain the defensive lesson."]

    skills = _mapped_skills(item["track"], item["level"], category)
    criteria = list(DEFAULT_ASSESSMENT)

    return {
        "title": title,
        "category": category,
        "difficulty": difficulty,
        "estimated_time": estimated_time,
        "prerequisites": list(prerequisites),
        "learning_outcomes": normalized,
        "mapped_skills": skills,
        "assessment_criteria": criteria,
    }


def _indent_sequence_lines(dumped: str) -> str:
    """Render nested sequences with the repository's two-space indent."""
    lines = []
    for line in dumped.splitlines():
        if line.startswith("- "):
            lines.append("  " + line)
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def _metadata_block(metadata: dict) -> str:
    dumped = yaml.safe_dump(
        metadata,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=1000,
    )
    return _indent_sequence_lines(dumped)


def _rewrite(text: str, block: str) -> str:
    lines = text.splitlines(keepends=True)
    kept = []
    insert_at = None
    skipping = False
    for line in lines:
        if skipping:
            if not line.strip() or line[:1].isspace():
                continue
            skipping = False
        match = re.match(r"^([A-Za-z_][\w]*):", line)
        if match and match.group(1) in REMOVE_KEYS:
            if insert_at is None:
                insert_at = len(kept)
            skipping = True
            continue
        kept.append(line)
    if insert_at is None:
        insert_at = 0
    prefix = "".join(kept[:insert_at])
    suffix = "".join(kept[insert_at:])
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    if prefix and not prefix.endswith("\n\n"):
        prefix += "\n"
    if suffix and not suffix.startswith("\n"):
        block += "\n"
    return prefix + block + suffix


def _validate(metadata: dict) -> list[str]:
    errors = []
    if not metadata["title"] or len(metadata["title"]) > 100:
        errors.append("title must be 1-100 characters")
    if not CATEGORY_RE.match(metadata["category"]):
        errors.append("category must be lower-case kebab-case")
    if metadata["difficulty"] not in VALID_DIFFICULTIES:
        errors.append("difficulty must be beginner, intermediate, or advanced")
    if not isinstance(metadata["estimated_time"], int) or metadata["estimated_time"] <= 0:
        errors.append("estimated_time must be a positive integer")
    for key in ("prerequisites", "learning_outcomes", "mapped_skills", "assessment_criteria"):
        value = metadata[key]
        if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
            errors.append(f"{key} must be a list of non-empty strings")
    if not metadata["learning_outcomes"]:
        errors.append("learning_outcomes must not be empty")
    if not metadata["assessment_criteria"]:
        errors.append("assessment_criteria must not be empty")
    unknown = [s for s in metadata["mapped_skills"] if s not in AXIS_KEYS]
    if not metadata["mapped_skills"] or unknown:
        errors.append(
            "mapped_skills must use competency keys: " + ", ".join(AXIS_KEYS)
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=DEFAULT_LABS_ROOT)
    parser.add_argument("--write", action="store_true", help="rewrite lab.yaml files")
    parser.add_argument("--check", action="store_true", help="exit 1 when changes are needed")
    args = parser.parse_args()

    catalog = _build_catalog(args.root)
    prerequisites = _prerequisite_map(catalog)

    changes = 0
    errors = 0
    for item in catalog:
        metadata = _metadata_for(item, prerequisites.get(item["slug"], []))
        for problem in _validate(metadata):
            print(f"INVALID {item['path']}: {problem}")
            errors += 1
        with open(item["path"], encoding="utf-8") as fh:
            original = fh.read()
        updated = _rewrite(original, _metadata_block(metadata))
        if updated != original:
            changes += 1
            if args.write:
                with open(item["path"], "w", encoding="utf-8", newline="") as fh:
                    fh.write(updated)
                print(f"updated {item['path']}")
            elif not args.check:
                print(f"needs update {item['path']}")

    print(
        f"{len(catalog)} lab(s); {changes} file(s) {'updated' if args.write else 'need updating'}; "
        f"{errors} validation error(s)"
    )
    if errors:
        return 1
    if args.check and changes:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
