"""Generate the selective framework-alignment page.

Source of truth: curriculum-frameworks.yaml
Run:
  python scripts/generate-framework-docs.py
  python scripts/generate-framework-docs.py --check
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORKS = ROOT / "curriculum-frameworks.yaml"
MANIFEST = ROOT / "curriculum-manifest.yaml"
OUT = ROOT / "Workbook" / "FRAMEWORKS.md"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def chapters(manifest: dict) -> list[dict]:
    rows = []
    for track in manifest.get("tracks", []):
        for chapter in track.get("chapters", []):
            item = dict(chapter)
            item["track_name"] = track.get("display_name")
            rows.append(item)
    return rows


def framework_label(fid: str, frameworks: dict) -> str:
    item = frameworks.get(fid, {})
    return item.get("name", fid)


def main() -> int:
    data = load(FRAMEWORKS)
    manifest = load(MANIFEST)
    frameworks = {str(item.get("id")): item for item in data.get("frameworks", [])}
    competencies = {str(item.get("id")): item for item in data.get("competencies", [])}
    defaults = data.get("chapter_defaults", {}) or {}
    overrides = data.get("lab_overrides", {}) or {}

    used = set()
    for chapter in chapters(manifest):
        config = defaults.get(chapter["id"], {}) or {}
        used.update(config.get("framework_refs") or [])
    for config in overrides.values():
        used.update((config or {}).get("framework_refs") or [])

    lines = [
        "# Framework Alignment",
        "",
        "Generated from `curriculum-frameworks.yaml`. Do not edit this page by hand.",
        "",
        "Framework mapping is **selective**. Each exercise resolves to:",
        "",
        "- **one primary competency**;",
        "- **one or two framework references** that actually govern the work;",
        "- **one measurable outcome**.",
        "",
        "An explicit value in a lab's `lab.yaml` overrides the chapter default. "
        "Lab-level overrides are listed below.",
        "",
        "## Framework registry",
        "",
        "| ID | Framework | Version | Purpose | Used? |",
        "|---|---|---|---|---|",
    ]
    for fid, item in frameworks.items():
        lines.append(
            f"| `{fid}` | {item.get('name', '')} | {item.get('version', '')} | "
            f"{item.get('purpose', '')} | {'Yes' if fid in used else 'Not yet'} |"
        )

    lines.extend([
        "",
        "Frameworks registered but not mapped yet are shown as **Not yet**. They "
        "remain in the registry so future SBOM or supply-chain exercises can use "
        "them without inventing a local variant.",
        "",
        "## Primary competencies",
        "",
        "| ID | Competency | Description |",
        "|---|---|---|",
    ])
    for cid, item in competencies.items():
        lines.append(f"| `{cid}` | {item.get('name', '')} | {item.get('description', '')} |")

    lines.extend([
        "",
        "## Chapter alignment",
        "",
        "| Chapter | Display name | Track | Primary competency | Framework references |",
        "|---|---|---|---|---|",
    ])
    for chapter in chapters(manifest):
        config = defaults.get(chapter["id"], {}) or {}
        primary = config.get("primary_competency") or "—"
        refs = ", ".join(
            f"`{ref}` ({framework_label(ref, frameworks)})"
            for ref in (config.get("framework_refs") or [])
        ) or "—"
        lines.append(
            f"| `{chapter['id']}` | {chapter.get('display_name', '')} | "
            f"{chapter.get('track_name', '')} | `{primary}` | {refs} |"
        )

    lines.extend([
        "",
        "## Lab-level overrides",
        "",
        "| Lab slug | Primary competency | Framework references |",
        "|---|---|---|",
    ])
    if overrides:
        for slug, config in overrides.items():
            config = config or {}
            refs = ", ".join(
                f"`{ref}` ({framework_label(ref, frameworks)})"
                for ref in (config.get("framework_refs") or [])
            ) or "Inherits chapter default"
            lines.append(
                f"| `{slug}` | `{config.get('primary_competency') or '—'}` | {refs} |"
            )
    else:
        lines.append("| — | — | — |")

    lines.extend([
        "",
        "## Measurable outcomes",
        "",
        "Each lab uses its explicit `measurable_outcome` when present. Otherwise it "
        "uses the first learning outcome that is not a flag-submission statement. "
        "If neither exists, the generator supplies one observation/interpretation/"
        "confidence sentence. The validation script rejects a missing or too-short "
        "outcome.",
        "",
        "## Validation",
        "",
        "```bash",
        "python scripts/validate-framework-map.py",
        "```",
        "",
        "The validator checks every lab for exactly one known competency, one or two "
        "known framework references, and one measurable outcome.",
        "",
    ])
    content = "\n".join(lines) + "\n"

    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != content:
            print(f"FAIL: {OUT.relative_to(ROOT)} is stale; run the generator", file=sys.stderr)
            return 1
        print(f"PASS: {OUT.relative_to(ROOT)} matches {FRAMEWORKS.name}")
        return 0

    OUT.write_text(content, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
