#!/usr/bin/env python3
"""Add the two safest missing workbook sections.

A workbook should end with a defensive takeaway and a flag-submission section.
This script appends only those two sections when they are missing; it never
rewrites existing prose. The lab contract supplies the takeaway text.

Usage:
    python scripts/normalize_workbook_sections.py --check
    python scripts/normalize_workbook_sections.py --write
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"
WORKBOOK = ROOT / "Workbook"

REMEDIATION_NEEDLES = (
    "defensive takeaway",
    "defensive takeaways",
    "the fixes",
    "key takeaways",
    "defensive controls",
)


def workbook_page(lab: dict) -> Path | None:
    value = str(lab.get("workbook") or "").strip()
    if not value:
        return None
    parts = [part for part in value.replace("\\", "/").split("/") if part]
    chapter = next((part for part in parts if part.startswith("CH_")), "")
    page = parts[-1] if parts else ""
    candidates = []
    if chapter and page:
        candidates.append(WORKBOOK / chapter / f"{page}.md")
    if page:
        candidates.extend(WORKBOOK.rglob(f"{page}.md"))
    return next((path for path in candidates if path.is_file()), None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("choose --check or --write")

    changed = 0
    missing_remediation = 0
    for path in sorted(LABS.rglob("lab.yaml")):
        lab = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        page = workbook_page(lab)
        if page is None:
            continue
        text = page.read_text(encoding="utf-8", errors="ignore")
        headings = " ".join(
            line[3:].strip().lower()
            for line in text.splitlines()
            if line.startswith("## ")
        )
        additions = []
        if not any(needle in headings for needle in REMEDIATION_NEEDLES):
            missing_remediation += 1
            takeaway = str(lab.get("defensive_takeaways") or "").strip()
            if takeaway:
                additions.append(f"## Defensive Takeaway\n\n{takeaway}\n")
        if not additions:
            continue
        changed += 1
        if args.write:
            page.write_text(
                text.rstrip() + "\n\n" + "\n".join(additions),
                encoding="utf-8",
                newline="\n",
            )
    print(
        f"pages_changed={changed} missing_remediation={missing_remediation} "
        f"written={args.write}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
