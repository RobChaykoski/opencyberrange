#!/usr/bin/env python3
"""Select a deterministic weekly canary slice of lab manifests.

The full lab harness is too expensive to run every week. Divide the sorted lab
list into five buckets and choose one bucket by ISO week. Every lab is exercised
once every five weeks, and the same week always selects the same labs.

Usage:
    python scripts/select-lab-canary.py --space
    python scripts/select-lab-canary.py --json canary.json
    python scripts/select-lab-canary.py --week 47
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFESTS = ROOT / "platform" / "tester" / "manifests"
BUCKETS = 5


def lab_ids() -> list[str]:
    ids = []
    for path in sorted(MANIFESTS.glob("*.yaml")):
        ids.append(path.stem)
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", type=int, help="ISO week number (default: current week)")
    parser.add_argument("--space", action="store_true", help="Print space-separated slugs")
    parser.add_argument("--json", type=Path, help="Write a JSON selection")
    args = parser.parse_args()

    ids = lab_ids()
    if not ids:
        raise SystemExit("No manifests found. Run scripts/generate-lab-manifests.py first.")

    week = args.week if args.week is not None else date.today().isocalendar().week
    bucket = (week - 1) % BUCKETS
    selected = ids[bucket::BUCKETS]

    payload = {
        "week": week,
        "bucket": bucket,
        "buckets": BUCKETS,
        "total_labs": len(ids),
        "selected_count": len(selected),
        "labs": selected,
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.space:
        print(" ".join(selected))
    else:
        print(
            f"canary week {week}: bucket {bucket + 1}/{BUCKETS}, "
            f"{len(selected)} of {len(ids)} labs"
        )
        for slug in selected:
            print(slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
