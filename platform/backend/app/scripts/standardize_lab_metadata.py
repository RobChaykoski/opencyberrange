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
OUTCOME_INTRO = "By completion students will be able to:"
VAGUE_OUTCOME_RE = re.compile(
    r"^(?:understand|learn|know|appreciate|become familiar with|"
    r"gain (?:an )?understanding of)\b",
    re.I,
)
ACTION_OUTCOME_RE = re.compile(
    r"^(?:configure|analyze|analyse|detect|identify|enumerate|explain|"
    r"describe|compare|demonstrate|verify|check|list|inspect|grab|connect|"
    r"access|download|retrieve|extract|exploit|authenticate|write|map|"
    r"reconstruct|document|investigate|correlate|pivot|escalate|assemble|"
    r"recover|decode|filter|monitor|trace|probe|triage|apply|use|perform|"
    r"determine|locate|discover|test|validate|review|summarize)\b",
    re.I,
)
LOW_VALUE_OUTCOME_RE = re.compile(
    r"^(?:verify|check|confirm)\b.*\b(?:port|service)\b.*\b(?:open|running|reachable)\b",
    re.I,
)
CATEGORY_OUTCOMES = {
    "enumeration": (
        "Enumerate the exposed service and its version",
        "Identify accessible resources and misconfigurations",
        "Document the information exposed by the target",
    ),
    "credential-attacks": (
        "Test the target service with valid and invalid credentials",
        "Identify the account or credential weakness that grants access",
        "Document the access obtained and the control that failed",
    ),
    "network-analysis": (
        "Inspect the relevant network traffic for the activity under investigation",
        "Identify the indicators that distinguish the activity from normal traffic",
        "Explain the detection or prevention control that addresses the finding",
    ),
    "web": (
        "Identify the vulnerable web endpoint and input",
        "Exploit the weakness to recover the assessment token",
        "Explain how to remediate the vulnerability",
    ),
    "forensics": (
        "Acquire and inspect the relevant evidence",
        "Reconstruct the activity from the available artefacts",
        "Document findings with supporting evidence",
    ),
    "osint": (
        "Collect publicly available information about the target",
        "Corroborate findings across independent sources",
        "Document the exposure and its privacy impact",
    ),
    "malware": (
        "Triage the suspicious sample or traffic",
        "Identify the malicious capability and supporting infrastructure",
        "Document indicators of compromise",
    ),
    "ai": (
        "Probe the assistant's policy boundary",
        "Demonstrate the policy bypass and its impact",
        "Explain the control that would prevent it",
    ),
    "ot": (
        "Inspect the industrial protocol traffic",
        "Identify the exposed process values",
        "Explain the operational risk",
    ),
    "reconnaissance": (
        "Enumerate the exposed services",
        "Identify service versions and possible weaknesses",
        "Document the attack surface",
    ),
    "authentication": (
        "Authenticate to the target service",
        "Inspect the post-authentication context",
        "Document the information exposed after login",
    ),
    "post-exploitation": (
        "Establish access to the target host",
        "Enumerate the host for sensitive data",
        "Recover the assessment token",
    ),
    "privilege-escalation": (
        "Enumerate local privilege-escalation paths",
        "Exploit the misconfiguration to gain elevated access",
        "Document the root cause",
    ),
    "exploitation": (
        "Identify the exploitable service or input",
        "Exploit the weakness to execute the required action",
        "Explain the remediation",
    ),
    "assessment": (
        "Enumerate the target environment",
        "Exploit the required weakness chain",
        "Document the evidence and final token",
    ),
    "general": (
        "Complete the lab's investigative steps",
        "Identify the key evidence or weakness",
        "Explain the defensive lesson",
    ),
}


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
    text = re.sub(r"^(?:successfully|be able to)\s+", "", text, flags=re.I)
    text = re.sub(r"^understand\s+", "Explain ", text, flags=re.I)
    text = re.sub(r"^learn\s+to\s+", "Demonstrate how to ", text, flags=re.I)
    text = re.sub(r"^learn\s+", "Explain ", text, flags=re.I)
    text = re.sub(r"^know\s+", "Identify ", text, flags=re.I)
    text = re.sub(r"^become familiar with\s+", "Describe ", text, flags=re.I)
    text = re.sub(
        r"^gain (?:an )?understanding of\s+", "Explain ", text, flags=re.I,
    )
    text = re.sub(r"^appreciate\s+", "Explain the importance of ", text, flags=re.I)
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


def _append_unique(outcomes, seen, text):
    text = _normalise_outcome(text)
    if not text:
        return
    low = text.lower()
    if low in seen:
        return
    if re.match(r"^(capture|submit|find|get) the flag\b", text, re.I):
        return
    if LOW_VALUE_OUTCOME_RE.match(text):
        return
    seen.add(low)
    outcomes.append(text)


def _step_outcomes(data):
    """Turn concrete test steps into measurable outcomes when a lab is short."""
    for step in (data.get("test", {}) or {}).get("steps", []) or []:
        name = step.get("name") if isinstance(step, dict) else None
        if not name:
            continue
        text = _normalise_outcome(name)
        if re.search(r"\b(?:flag|ocr\{)", text, re.I):
            continue
        if not ACTION_OUTCOME_RE.match(text):
            continue
        yield text


def _category_outcomes(category):
    return CATEGORY_OUTCOMES.get(
        category, CATEGORY_OUTCOMES["general"],
    )


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

    outcomes = (
        data.get("learning_outcomes")
        or data.get("learning_objectives")
        or data.get("objectives")
        or []
    )
    learning_outcomes = []
    seen = set()
    for outcome in outcomes:
        _append_unique(learning_outcomes, seen, outcome)

    # Short labs get concrete outcomes from their tester steps first, then a
    # category fallback, so every lab ends up with 3-5 measurable statements.
    if len(learning_outcomes) < 3:
        for outcome in _step_outcomes(data):
            _append_unique(learning_outcomes, seen, outcome)
            if len(learning_outcomes) >= 3:
                break
    if len(learning_outcomes) < 3:
        for outcome in _category_outcomes(category):
            _append_unique(learning_outcomes, seen, outcome)
            if len(learning_outcomes) >= 3:
                break
    if len(learning_outcomes) < 3:
        _append_unique(
            learning_outcomes,
            seen,
            "Document the evidence and explain the defensive lesson",
        )
    # Cap the list so the learner-facing brief stays focused.
    learning_outcomes = learning_outcomes[:5]

    skills = _mapped_skills(item["track"], item["level"], category)
    criteria = list(DEFAULT_ASSESSMENT)

    return {
        "title": title,
        "category": category,
        "difficulty": difficulty,
        "estimated_time": estimated_time,
        "prerequisites": list(prerequisites),
        "learning_outcomes": learning_outcomes,
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
    lines = dumped.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("learning_outcomes:"):
            lines.insert(index, f"# {OUTCOME_INTRO}")
            break
    return _indent_sequence_lines("\n".join(lines) + "\n")


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
        if line.strip() == f"# {OUTCOME_INTRO}":
            if insert_at is None:
                insert_at = len(kept)
            continue
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
    elif not 3 <= len(metadata["learning_outcomes"]) <= 5:
        errors.append("learning_outcomes must contain 3 to 5 outcomes")
    for outcome in metadata["learning_outcomes"]:
        if VAGUE_OUTCOME_RE.match(outcome):
            errors.append(f"learning outcome uses a vague verb: {outcome}")
        if len(outcome.split()) < 3:
            errors.append(f"learning outcome is too short to be measurable: {outcome}")
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
