"""Generate the curriculum map, README inventory, and terminology pages.

The YAML manifests are the source of truth:
  curriculum-manifest.yaml
  curriculum-glossary.yaml

Generated outputs:
  Workbook/CURRICULUM.md
  Workbook/TERMINOLOGY.md
  README.md                (the "Included tracks" section)
  Workbook/index.md        (the "Available Tracks" section)
  Manual-Lite/08_Glossary/01_Glossary.md
                           (the "Cross-curriculum terminology" section)
  Each chapter 00_Introduction.md H1, using the display ID.

Run:
  python scripts/generate-curriculum-docs.py
  python scripts/generate-curriculum-docs.py --check
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "curriculum-manifest.yaml"
GLOSSARY = ROOT / "curriculum-glossary.yaml"
WORKBOOK = ROOT / "Workbook"

README = ROOT / "README.md"
INDEX = WORKBOOK / "index.md"
CURRICULUM = WORKBOOK / "CURRICULUM.md"
TERMINOLOGY = WORKBOOK / "TERMINOLOGY.md"
MANUAL_GLOSSARY = ROOT / "Manual-Lite" / "08_Glossary" / "01_Glossary.md"

README_BEGIN = "<!-- BEGIN GENERATED CURRICULUM INVENTORY -->"
README_END = "<!-- END GENERATED CURRICULUM INVENTORY -->"
INDEX_BEGIN = "<!-- BEGIN GENERATED WORKBOOK CURRICULUM -->"
INDEX_END = "<!-- END GENERATED WORKBOOK CURRICULUM -->"
GLOSSARY_BEGIN = "<!-- BEGIN GENERATED CROSS-CURRICULUM TERMS -->"
GLOSSARY_END = "<!-- END GENERATED CROSS-CURRICULUM TERMS -->"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def fmt_duration(minutes: int) -> str:
    minutes = int(minutes or 0)
    if minutes >= 60:
        hours, remainder = divmod(minutes, 60)
        return f"{hours}h {remainder:02d}m"
    return f"{minutes}m"


def chapter_lab_count(directory: str) -> int:
    """Count labs whose workbook path names this chapter directory."""
    count = 0
    for lab_yaml in (ROOT / "platform" / "labs").rglob("lab.yaml"):
        data = yaml.safe_load(lab_yaml.read_text(encoding="utf-8")) or {}
        workbook = str(data.get("workbook") or "")
        if f"/{directory}/" in workbook:
            count += 1
    return count


def track_totals(track: dict) -> tuple[int, int]:
    chapters = track.get("chapters", [])
    return (
        sum(int(c.get("exercises") or 0) for c in chapters),
        sum(int(c.get("estimated_minutes") or 0) for c in chapters),
    )


def ordered_tracks(manifest: dict) -> list[dict]:
    return sorted(
        manifest.get("tracks", []),
        key=lambda track: (
            int(track.get("pathway_order", 999)),
            str(track.get("display_name") or track.get("id") or ""),
        ),
    )


def all_chapters(manifest: dict) -> list[tuple[dict, dict]]:
    return [
        (track, chapter)
        for track in ordered_tracks(manifest)
        for chapter in track.get("chapters", [])
    ]


def render_track_table(manifest: dict, *, include_roles: bool = False) -> str:
    if include_roles:
        lines = [
            "| Track ID | Display name | Audience | Difficulty | Prerequisites | Exercises | Duration | Required environment | Recommended next | Role alignment | Status |",
            "|---|---|---|---|---|---:|---|---|---|---|---|",
        ]
    else:
        lines = [
            "| Track ID | Display name | Audience | Difficulty | Prerequisites | Exercises | Duration | Status |",
            "|---|---|---|---|---|---:|---|---|",
        ]
    for track in ordered_tracks(manifest):
        exercises, minutes = track_totals(track)
        prereqs = ", ".join(track.get("prerequisites") or []) or "None"
        roles = "; ".join(track.get("role_alignment") or []) or "—"
        env = track.get("required_environment") or "—"
        next_id = track.get("recommended_next") or "—"
        base = [
            f"`{track['id']}`",
            track.get("display_name", ""),
            track.get("audience", ""),
            track.get("difficulty", ""),
            prereqs,
            str(exercises),
            fmt_duration(minutes),
        ]
        if include_roles:
            base.extend([env, f"`{next_id}`", roles, track.get("status", "")])
        else:
            base.append(track.get("status", ""))
        lines.append("| " + " | ".join(base) + " |")
    return "\n".join(lines)


def render_pathway(manifest: dict) -> str:
    ids = [c["id"] for _, c in all_chapters(manifest)]
    return " → ".join(f"`{item}`" for item in ids)


def render_readme_inventory(manifest: dict) -> str:
    return "\n".join([
        "The curriculum is generated from `curriculum-manifest.yaml`. The table",
        "below is the learner-facing inventory; the full chapter map, prerequisites,",
        "environments, role alignment, and recommended next steps are in",
        "[`Workbook/CURRICULUM.md`](Workbook/CURRICULUM.md).",
        "",
        "Exercise counts are labs that expose a workbook page. The platform also",
        "contains labs without a workbook page; see `Workbook/COVERAGE.md`.",
        "",
        "Framework alignment is selective and documented in",
        "[`Workbook/FRAMEWORKS.md`](Workbook/FRAMEWORKS.md).",
        "",
        "Regenerate with `python scripts/generate-curriculum-docs.py`; CI can use",
        "`--check` to detect drift.",
        "",
        render_track_table(manifest),
        "",
        "**Total:** "
        f"{sum(track_totals(t)[0] for t in manifest.get('tracks', []))} exercises "
        f"across {len(manifest.get('tracks', []))} tracks and "
        f"{len(all_chapters(manifest))} chapters.",
        "",
        "Recommended pathway:",
        "",
        render_pathway(manifest),
        "",
    ])


def render_index_inventory(manifest: dict) -> str:
    return "\n".join([
        "The workbook curriculum is generated from `curriculum-manifest.yaml`.",
        "Every published chapter has a stable display ID, a physical directory, a",
        "prerequisite chain, an exercise count, an estimated duration, and a",
        "recommended next step.",
        "",
        "Exercise counts are labs that expose a workbook page. The platform also",
        "contains labs without a workbook page; see [Workbook coverage](COVERAGE.md).",
        "",
        "See the [framework alignment](FRAMEWORKS.md) for the selective mapping.",
        "",
        render_track_table(manifest),
        "",
        "**Total:** "
        f"{sum(track_totals(t)[0] for t in manifest.get('tracks', []))} exercises "
        f"across {len(manifest.get('tracks', []))} tracks and "
        f"{len(all_chapters(manifest))} chapters.",
        "",
        f"See the [full curriculum map](CURRICULUM.md) and the "
        "[cross-curriculum terminology](TERMINOLOGY.md).",
        "",
        "Recommended pathway:",
        "",
        render_pathway(manifest),
        "",
    ])


def render_curriculum(manifest: dict, glossary: dict) -> str:
    lines = [
        "# Curriculum Map",
        "",
        "Generated from `curriculum-manifest.yaml`. Do not edit this page by hand.",
        "Directory names are stable; display IDs are the labels used in chapter",
        "titles, navigation, prerequisite blocks, PDFs, analytics, and reports.",
        "",
        "Exercise counts are labs that expose a workbook page. The platform also",
        "contains labs without a workbook page; see [Workbook coverage](COVERAGE.md).",
        "",
        "Framework alignment is selective. See [Framework alignment](FRAMEWORKS.md).",
        "",
        "## Track overview",
        "",
        render_track_table(manifest, include_roles=True),
        "",
        "## Chapter map",
        "",
        "| Chapter | Display name | Directory | Difficulty | Prerequisites | Exercises | Duration | Recommended next | Status |",
        "|---|---|---|---|---|---:|---|---|---|",
    ]
    for track in ordered_tracks(manifest):
        for chapter in track.get("chapters", []):
            prereqs = ", ".join(chapter.get("prerequisites") or []) or "None"
            lines.append(
                f"| `{chapter['id']}` | {chapter.get('display_name', '')} | "
                f"`{chapter.get('directory', '')}` | {chapter.get('difficulty', '')} | "
                f"{prereqs} | {chapter.get('exercises', 0)} | "
                f"{fmt_duration(chapter.get('estimated_minutes', 0))} | "
                f"`{chapter.get('recommended_next') or '—'}` | "
                f"{chapter.get('status', '')} |"
            )
    lines.extend([
        "",
        "## Track details",
        "",
    ])
    for track in ordered_tracks(manifest):
        exercises, minutes = track_totals(track)
        lines.extend([
            f"### {track.get('display_name', track['id'])} (`{track['id']}`)",
            "",
            f"- **Audience:** {track.get('audience', '—')}",
            f"- **Difficulty:** {track.get('difficulty', '—')}",
            f"- **Track prerequisites:** {', '.join(track.get('prerequisites') or []) or 'None'}",
            f"- **Exercises:** {exercises}",
            f"- **Estimated duration:** {fmt_duration(minutes)}",
            f"- **Required environment:** {track.get('required_environment', '—')}",
            f"- **Recommended next track:** `{track.get('recommended_next') or '—'}`",
            f"- **Role alignment:** {', '.join(track.get('role_alignment') or []) or '—'}",
            f"- **Status:** {track.get('status', '—')}",
            "",
            "| Chapter | Directory | Prerequisites | Recommended next |",
            "|---|---|---|---|",
        ])
        for chapter in track.get("chapters", []):
            prereqs = ", ".join(chapter.get("prerequisites") or []) or "None"
            lines.append(
                f"| `{chapter['id']}` — {chapter.get('display_name', '')} | "
                f"`{chapter.get('directory', '')}` | {prereqs} | "
                f"`{chapter.get('recommended_next') or '—'}` |"
            )
        notes = [c for c in track.get("chapters", []) if c.get("notes")]
        if notes:
            lines.append("")
            for chapter in notes:
                lines.append(f"- `{chapter['id']}`: {chapter['notes']}")
        lines.append("")
    lines.extend([
        "## Recommended pathway",
        "",
        render_pathway(manifest),
        "",
        "## Evidence ladder",
        "",
        "| Level | Term | Definition |",
        "|---:|---|---|",
    ])
    for item in glossary.get("evidence_ladder", []):
        lines.append(
            f"| {item.get('level', '')} | **{item.get('name', '')}** | "
            f"{item.get('definition', '')} |"
        )
    lines.extend([
        "",
        "See [Cross-Curriculum Terminology](TERMINOLOGY.md) for the full term list.",
        "",
    ])
    return "\n".join(lines)


def render_terminology(glossary: dict) -> str:
    lines = [
        "# Cross-Curriculum Terminology",
        "",
        "Generated from `curriculum-glossary.yaml`. Do not edit this page by hand.",
        "These definitions take precedence in learner-facing prose, workbook",
        "evidence notes, analytics, assessment reports, and PDF output.",
        "",
        "## Core terms",
        "",
        "| Term | Definition |",
        "|---|---|",
    ]
    for item in glossary.get("terms", []):
        lines.append(f"| **{item['term']}** | {item['definition']} |")
    lines.extend([
        "",
        "## Evidence ladder",
        "",
        "Use these words in this order. Do not skip from an observation to a",
        "finding, impact, or remediation claim.",
        "",
        "| Level | Term | Definition |",
        "|---:|---|---|",
    ])
    for item in glossary.get("evidence_ladder", []):
        lines.append(
            f"| {item.get('level', '')} | **{item.get('name', '')}** | "
            f"{item.get('definition', '')} |"
        )
    lines.extend([
        "",
        "## How to use the ladder",
        "",
        "- **Observed:** quote or show the output.",
        "- **Inferred:** say what you think it means and what would verify it.",
        "- **Validated:** name the approved test and its result.",
        "- **Impacted:** name the affected confidentiality, integrity, availability,",
        "  identity, or process state.",
        "- **Remediated:** name the root-cause change.",
        "- **Verified:** name the regression test that confirms the correction.",
        "",
        "A flag confirms completion. It is not a finding or proof of impact.",
        "",
    ])
    return "\n".join(lines)


def render_glossary_section(glossary: dict) -> str:
    lines = [
        "## Cross-curriculum terminology",
        "",
        "These definitions are generated from `curriculum-glossary.yaml` and take",
        "precedence across every track, workbook, report, and PDF. Track-specific",
        "sections below may add context but must not contradict these meanings.",
        "",
        "| Term | Definition |",
        "|---|---|",
    ]
    for item in glossary.get("terms", []):
        lines.append(f"| **{item['term']}** | {item['definition']} |")
    lines.extend([
        "",
        "### Evidence ladder",
        "",
        "Use this wording in this order.",
        "",
        "| Level | Term | Definition |",
        "|---:|---|---|",
    ])
    for item in glossary.get("evidence_ladder", []):
        lines.append(
            f"| {item.get('level', '')} | **{item.get('name', '')}** | "
            f"{item.get('definition', '')} |"
        )
    return "\n".join(lines)


def replace_marked(text: str, begin: str, end: str, body: str) -> str:
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    replacement = f"{begin}\n{body.rstrip()}\n{end}"
    if not pattern.search(text):
        raise SystemExit(f"missing markers: {begin}")
    return pattern.sub(replacement, text, count=1)


def insert_marked_after(text: str, anchor: str, begin: str, end: str, body: str) -> str:
    if begin in text:
        return replace_marked(text, begin, end, body)
    marker = f"{anchor}\n\n{begin}\n{body.rstrip()}\n{end}\n"
    if anchor not in text:
        raise SystemExit(f"missing anchor: {anchor}")
    return text.replace(anchor, marker, 1)


def insert_marked_before(text: str, anchor: str, begin: str, end: str, body: str) -> str:
    if begin in text:
        return replace_marked(text, begin, end, body)
    if anchor not in text:
        raise SystemExit(f"missing anchor: {anchor}")
    marker = f"{begin}\n{body.rstrip()}\n{end}\n\n{anchor}"
    return text.replace(anchor, marker, 1)


def insert_marked_section(text: str, heading: str, next_heading: str, begin: str, end: str, body: str) -> str:
    if begin in text:
        return replace_marked(text, begin, end, body)
    start = text.find(heading)
    if start == -1:
        raise SystemExit(f"missing heading: {heading}")
    end_at = text.find(next_heading, start + len(heading))
    if end_at == -1:
        raise SystemExit(f"missing next heading after {heading}: {next_heading}")
    section = f"{heading}\n\n{begin}\n{body.rstrip()}\n{end}\n\n"
    return text[:start] + section + text[end_at:]


def chapter_lookup(manifest: dict) -> dict[str, dict]:
    return {
        chapter["id"]: chapter
        for _, chapter in all_chapters(manifest)
        if chapter.get("id")
    }


def render_chapter_position(chapter: dict, lookup: dict[str, dict]) -> str:
    prereqs = chapter.get("prerequisites") or []
    if prereqs:
        prereq_text = ", ".join(
            f"`{item}` — {lookup.get(item, {}).get('display_name', 'Unknown chapter')}"
            for item in prereqs
        )
    else:
        prereq_text = "None"
    next_id = chapter.get("recommended_next")
    next_text = (
        f"`{next_id}` — {lookup.get(next_id, {}).get('display_name', 'Unknown chapter')}"
        if next_id else "—"
    )
    return "\n".join([
        "<!-- BEGIN GENERATED CHAPTER POSITION -->",
        '!!! note "Curriculum position"',
        f"    **Chapter:** `{chapter['id']}` — {chapter.get('display_name', '')}",
        f"    **Prerequisites:** {prereq_text}",
        f"    **Recommended next:** {next_text}",
        "<!-- END GENERATED CHAPTER POSITION -->",
    ])


def update_intro_titles(manifest: dict) -> dict[Path, str]:
    lookup = chapter_lookup(manifest)
    updates: dict[Path, str] = {}
    begin = "<!-- BEGIN GENERATED CHAPTER POSITION -->"
    end = "<!-- END GENERATED CHAPTER POSITION -->"
    for _, chapter in all_chapters(manifest):
        intro = chapter.get("intro")
        if not intro:
            continue
        path = WORKBOOK / intro
        if not path.exists():
            raise SystemExit(f"missing intro page: {path}")
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if not lines or not lines[0].startswith("# "):
            raise SystemExit(f"intro page has no H1: {path}")
        desired = f"# {chapter['id']}: {chapter['display_name']}"
        lines[0] = desired
        block = render_chapter_position(chapter, lookup)
        updated = "\n".join(lines)
        if begin in updated:
            updated = re.sub(
                re.escape(begin) + r".*?" + re.escape(end),
                block,
                updated,
                count=1,
                flags=re.S,
            )
        else:
            updated = updated.replace(f"{desired}\n", f"{desired}\n\n{block}\n", 1)
        updates[path] = updated + ("\n" if text.endswith("\n") else "")
    return updates


def validate_manifest(manifest: dict) -> list[str]:
    problems = []
    seen_ids = set()
    for track in manifest.get("tracks", []):
        if not track.get("id"):
            problems.append("track without id")
        for chapter in track.get("chapters", []):
            cid = chapter.get("id")
            directory = chapter.get("directory")
            if not cid or not directory:
                problems.append(f"{track.get('id')}: chapter missing id or directory")
                continue
            if cid in seen_ids:
                problems.append(f"duplicate chapter id: {cid}")
            seen_ids.add(cid)
            if not (WORKBOOK / directory).is_dir():
                problems.append(f"{cid}: missing directory {directory}")
            actual = chapter_lab_count(directory)
            declared = int(chapter.get("exercises") or 0)
            if actual != declared:
                problems.append(
                    f"{cid}: declared {declared} exercises but lab.yaml has {actual}"
                )
            intro = chapter.get("intro")
            if intro and not (WORKBOOK / intro).is_file():
                problems.append(f"{cid}: missing intro {intro}")
            if not intro and chapter.get("status") == "published":
                notes = str(chapter.get("notes") or "").lower()
                if "no 00_introduction" not in notes:
                    problems.append(f"{cid}: published chapter has no intro page")
    return problems


def main() -> int:
    manifest = load_yaml(MANIFEST)
    glossary = load_yaml(GLOSSARY)
    problems = validate_manifest(manifest)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1

    outputs: dict[Path, str] = {}
    outputs[CURRICULUM] = render_curriculum(manifest, glossary)
    outputs[TERMINOLOGY] = render_terminology(glossary)
    outputs[README] = insert_marked_section(
        README.read_text(encoding="utf-8"),
        "## Included tracks",
        "## Network Foundations stream",
        README_BEGIN,
        README_END,
        render_readme_inventory(manifest),
    )
    outputs[INDEX] = insert_marked_section(
        INDEX.read_text(encoding="utf-8"),
        "## Available Tracks",
        "## How to Use This Workbook",
        INDEX_BEGIN,
        INDEX_END,
        render_index_inventory(manifest),
    )
    outputs[MANUAL_GLOSSARY] = insert_marked_before(
        MANUAL_GLOSSARY.read_text(encoding="utf-8"),
        "## How MISP machine tags work",
        GLOSSARY_BEGIN,
        GLOSSARY_END,
        render_glossary_section(glossary),
    )

    intro_updates = update_intro_titles(manifest)
    outputs.update(intro_updates)

    if "--check" in sys.argv:
        stale = []
        for path, content in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path)
        if stale:
            for path in stale:
                print(f"FAIL: stale generated file: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"PASS: curriculum docs match {MANIFEST.name} and {GLOSSARY.name}")
        return 0

    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    print(
        f"wrote {CURRICULUM.relative_to(ROOT)}, {TERMINOLOGY.relative_to(ROOT)}, "
        f"README inventory, workbook index, glossary terms, and "
        f"{len(intro_updates)} chapter titles"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
