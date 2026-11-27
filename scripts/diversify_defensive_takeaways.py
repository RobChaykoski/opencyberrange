#!/usr/bin/env python3
"""Make shared defensive takeaways lab-specific.

Tracks often reuse one good takeaway across many labs. That is useful advice,
but it hides what the individual lab should verify. This script keeps the shared
guidance and appends one lab-specific evidence sentence. Hand-reviewed labs that
already have a unique takeaway are not touched.

Usage:
    python scripts/diversify_defensive_takeaways.py --check
    python scripts/diversify_defensive_takeaways.py --write
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"
MARKER = "In this lab, apply that to"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def replace_takeaway(path: Path, value: str) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.startswith("defensive_takeaways:"):
            if "|" in line.split(":", 1)[1] or ">" in line.split(":", 1)[1]:
                return False
            lines[index] = f"defensive_takeaways: {json.dumps(value, ensure_ascii=False)}\n"
            path.write_text("".join(lines), encoding="utf-8", newline="\n")
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("choose --check or --write")

    paths = sorted(LABS.rglob("lab.yaml"))
    grouped: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    for path in paths:
        lab = load(path)
        text = str(lab.get("defensive_takeaways") or "").strip()
        if text:
            grouped[text].append((path, lab))

    changed = 0
    skipped = 0
    for text, entries in grouped.items():
        if len(entries) < 2:
            continue
        for path, lab in entries:
            if MARKER in text:
                continue
            title = str(lab.get("title") or path.parent.name).strip().rstrip(".")
            value = f"{text.rstrip()} {MARKER} {title.lower()} and record the evidence before recommending the fix."
            changed += 1
            if args.write and not replace_takeaway(path, value):
                skipped += 1
    print(f"duplicate_labs={changed} written={changed - skipped if args.write else 0} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
