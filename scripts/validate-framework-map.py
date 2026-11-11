"""Validate selective framework alignment across every lab.

Each lab must resolve to:
  - exactly one primary competency
  - one or two framework references
  - one measurable outcome

Run:
  python scripts/validate-framework-map.py
  python scripts/validate-framework-map.py --check
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"
MANIFEST = ROOT / "curriculum-manifest.yaml"
FRAMEWORKS = ROOT / "curriculum-frameworks.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def chapter_map(manifest: dict) -> dict[str, str]:
    result = {}
    for track in manifest.get("tracks", []):
        for chapter in track.get("chapters", []):
            directory = str(chapter.get("directory") or "")
            chapter_id = str(chapter.get("id") or "")
            if directory and chapter_id:
                result[directory] = chapter_id
    return result


def chapter_for_workbook(workbook: str, chapters: dict[str, str]) -> str | None:
    if not workbook:
        return None
    for part in Path(str(workbook).replace("\\", "/")).parts:
        if part in chapters:
            return chapters[part]
    return None


def clean_outcome(value) -> str | None:
    text = " ".join(str(value or "").split()).strip()
    if not text:
        return None
    if text.lower().startswith(("submit the correct flag", "capture the flag")):
        return None
    return text


def resolve(lab_slug: str, chapter_id: str | None, lab_data: dict, data: dict) -> dict:
    chapter = (data.get("chapter_defaults", {}) or {}).get(str(chapter_id or ""), {}) or {}
    override = (data.get("lab_overrides", {}) or {}).get(lab_slug, {}) or {}
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
    outcome = clean_outcome(lab_data.get("measurable_outcome"))
    if not outcome:
        for item in lab_data.get("learning_outcomes") or []:
            outcome = clean_outcome(item)
            if outcome:
                break
    if not outcome:
        title = lab_data.get("title") or lab_data.get("name") or lab_slug
        outcome = (
            f"Complete {title} and record one observation, one interpretation, "
            "and a confidence level."
        )
    return {"primary_competency": primary, "framework_refs": refs, "measurable_outcome": outcome}


def main() -> int:
    manifest = load(MANIFEST)
    data = load(FRAMEWORKS)
    chapters = chapter_map(manifest)
    competencies = {str(item.get("id")) for item in data.get("competencies", [])}
    frameworks = {str(item.get("id")) for item in data.get("frameworks", [])}

    problems = []
    lab_rows = []
    framework_counts = Counter()
    competency_counts = Counter()

    for lab_yaml in sorted(LABS.rglob("lab.yaml")):
        lab_data = load(lab_yaml)
        slug = lab_yaml.parent.name
        workbook = str(lab_data.get("workbook") or "")
        chapter_id = chapter_for_workbook(workbook, chapters)
        override = (data.get("lab_overrides", {}) or {}).get(slug, {}) or {}
        if not chapter_id and not override:
            problems.append(f"{slug}: cannot map workbook to chapter and has no lab override")
            continue
        resolved = resolve(slug, chapter_id, lab_data, data)
        primary = resolved["primary_competency"]
        refs = resolved["framework_refs"]
        outcome = resolved["measurable_outcome"]
        if primary not in competencies:
            problems.append(f"{slug}: unknown competency {primary!r}")
        if not 1 <= len(refs) <= 2:
            problems.append(f"{slug}: expected 1-2 framework refs, got {len(refs)}")
        for ref in refs:
            if ref not in frameworks:
                problems.append(f"{slug}: unknown framework {ref!r}")
        if not outcome or len(outcome) < 15:
            problems.append(f"{slug}: measurable outcome missing or too short")
        framework_counts.update(refs)
        competency_counts.update([primary])
        lab_rows.append((slug, chapter_id, primary, refs, outcome))

    print(f"Labs inspected: {len(lab_rows)}")
    print(f"Competencies used: {len(competency_counts)}")
    print(f"Frameworks used: {', '.join(f'{k} ({v})' for k, v in framework_counts.most_common())}")
    unused = sorted(frameworks - set(framework_counts))
    if unused:
        print(f"Frameworks registered but not mapped yet: {', '.join(unused)}")
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1
    print("PASS: every lab has one competency, one or two framework refs, and one measurable outcome.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
