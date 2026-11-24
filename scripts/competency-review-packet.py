#!/usr/bin/env python3
"""Generate subject-matter review packets for baseline competency contracts.

A packet is a review aid, not a review. It prints the current contract, the
taxonomy names, the evidence weights, and a checklist. The reviewer edits the
contract and sets `review_status: reviewed`.

Usage:
    python scripts/competency-review-packet.py --summary
    python scripts/competency-review-packet.py --track Network --limit 1
    python scripts/competency-review-packet.py --track AI --out /tmp/ocr-review
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "platform" / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.competency_coverage import (
    build_review_packet,
    coverage_summary,
    pending_contracts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate contract review packets")
    parser.add_argument("--track", help="Only this track (case-insensitive)")
    parser.add_argument("--limit", type=int, default=0, help="Maximum packets (0 = all)")
    parser.add_argument("--out", help="Write one Markdown file per lab to this directory")
    parser.add_argument("--summary", action="store_true", help="Print track progress")
    args = parser.parse_args()

    if args.summary:
        summary = coverage_summary()
        print(
            f"Contracts: {summary['total']} total, {summary['reviewed']} reviewed, "
            f"{summary['pending']} pending ({summary['coverage_percent']}%)"
        )
        for track in summary["tracks"]:
            print(
                f"  {track['track']:<18} total {track['total']:>3}  "
                f"reviewed {track['reviewed']:>3}  pending {track['pending']:>3}"
            )
        return 0

    rows = pending_contracts(args.track)
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("No pending contracts match the filter.")
        return 0

    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        for row in rows:
            (out / f"{row['slug']}.md").write_text(
                build_review_packet(row["slug"]), encoding="utf-8"
            )
        print(f"Wrote {len(rows)} review packet(s) to {out}")
        return 0

    for index, row in enumerate(rows):
        if index:
            print("\n---\n")
        print(build_review_packet(row["slug"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
