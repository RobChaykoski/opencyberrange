#!/usr/bin/env python3
"""Lab freshness gate and report.

The metadata schema already records ``reviewed_at``, ``review_status``, and
difficulty evidence. This script makes those fields operational:

* a lab is stale when ``reviewed_at`` is older than the policy window or the
  review status says stale/archived/expired;
* a missing or invalid review date is a failure, not a silent pass;
* provisional difficulty evidence older than two quarters is a warning;
* a provisional lab with at least five observations is a promotion candidate.

Usage:
    python scripts/check-lab-freshness.py
    python scripts/check-lab-freshness.py --write docs/LAB-FRESHNESS.md
    python scripts/check-lab-freshness.py --json lab-freshness.json
    python scripts/check-lab-freshness.py --today 2026-11-23
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
LABS = ROOT / "platform" / "labs"
STALE_STATUS = ("stale", "archived", "expired", "retired")


def _load(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001 - malformed metadata is a finding below
        return {}


def _reviewed(value) -> date | None:
    try:
        return date.fromisoformat(str(value).strip())
    except (TypeError, ValueError):
        return None


def _track(path: Path) -> str:
    try:
        return path.relative_to(LABS).parts[0]
    except (ValueError, IndexError):
        return "Unknown"


def collect(today: date, max_age_days: int, provisional_max_days: int) -> list[dict]:
    rows = []
    for path in sorted(LABS.rglob("lab.yaml")):
        data = _load(path)
        reviewed = _reviewed(data.get("reviewed_at"))
        status = str(data.get("review_status") or "").strip()
        age_days = (today - reviewed).days if reviewed else None
        status_stale = any(token in status.lower() for token in STALE_STATUS)
        stale = reviewed is None or age_days > max_age_days or status_stale
        quality = str(data.get("difficulty_evidence_quality") or "").strip()
        sample = data.get("difficulty_evidence_sample")
        try:
            sample_value = int(sample or 0)
        except (TypeError, ValueError):
            sample_value = 0
        provisional_old = (
            quality == "provisional"
            and reviewed is not None
            and age_days is not None
            and age_days > provisional_max_days
        )
        rows.append(
            {
                "slug": path.parent.name,
                "track": _track(path),
                "path": path.relative_to(ROOT).as_posix(),
                "title": str(data.get("title") or path.parent.name),
                "reviewed_at": reviewed.isoformat() if reviewed else "",
                "age_days": age_days,
                "review_status": status,
                "stale": stale,
                "stale_reason": (
                    "missing or invalid reviewed_at"
                    if reviewed is None
                    else "review status is stale"
                    if status_stale
                    else f"reviewed {age_days} days ago"
                    if age_days > max_age_days
                    else ""
                ),
                "difficulty_quality": quality,
                "difficulty_sample": sample_value,
                "provisional_old": provisional_old,
                "promotion_candidate": quality == "provisional" and sample_value >= 5,
            }
        )
    return rows


def render(rows: list[dict], today: date, max_age_days: int, provisional_max_days: int) -> str:
    by_track = defaultdict(lambda: {"labs": 0, "stale": 0, "provisional": 0, "old": 0})
    for row in rows:
        bucket = by_track[row["track"]]
        bucket["labs"] += 1
        bucket["stale"] += 1 if row["stale"] else 0
        bucket["provisional"] += 1 if row["difficulty_quality"] == "provisional" else 0
        bucket["old"] += 1 if row["provisional_old"] else 0

    stale = [row for row in rows if row["stale"]]
    promotion = [row for row in rows if row["promotion_candidate"]]
    oldest = sorted(
        (row for row in rows if row["age_days"] is not None),
        key=lambda row: row["age_days"],
        reverse=True,
    )[:10]

    lines = [
        "# Lab freshness",
        "",
        f"Generated: **{today.isoformat()}**. Policy: review every "
        f"**{max_age_days} days**; provisional difficulty evidence is flagged "
        f"after **{provisional_max_days} days**.",
        "",
        f"- Labs: **{len(rows)}**",
        f"- Stale or missing review: **{len(stale)}**",
        f"- Provisional difficulty evidence: **{sum(1 for row in rows if row['difficulty_quality'] == 'provisional')}**",
        f"- Promotion candidates (5+ observations): **{len(promotion)}**",
        "",
        "## By track",
        "",
        "| Track | Labs | Stale | Provisional | Provisional over 2 quarters |",
        "|---|---:|---:|---:|---:|",
    ]
    for track in sorted(by_track):
        bucket = by_track[track]
        lines.append(
            f"| {track} | {bucket['labs']} | {bucket['stale']} | "
            f"{bucket['provisional']} | {bucket['old']} |"
        )

    lines.extend(["", "## Stale or missing review", ""])
    if stale:
        lines.extend(
            [
                "| Lab | Track | Reviewed | Reason |",
                "|---|---|---|---|",
            ]
        )
        for row in stale:
            lines.append(
                f"| `{row['slug']}` | {row['track']} | "
                f"{row['reviewed_at'] or 'missing'} | {row['stale_reason']} |"
            )
    else:
        lines.append("None. Every lab has a review date inside the policy window.")

    lines.extend(["", "## Oldest reviews", ""])
    lines.extend(["| Lab | Track | Reviewed | Age (days) |", "|---|---|---|---:|"])
    for row in oldest:
        lines.append(
            f"| `{row['slug']}` | {row['track']} | {row['reviewed_at']} | {row['age_days']} |"
        )

    lines.extend(["", "## Difficulty promotion candidates", ""])
    if promotion:
        lines.extend(
            [
                "Provisional evidence with at least five observations. Re-review the "
                "lab, then change `difficulty_evidence_quality` to `observed` and "
                "record the new evidence date.",
                "",
                "| Lab | Sample | Reviewed |",
                "|---|---:|---|",
            ]
        )
        for row in promotion:
            lines.append(
                f"| `{row['slug']}` | {row['difficulty_sample']} | {row['reviewed_at']} |"
            )
    else:
        lines.append("None yet.")

    lines.extend(
        [
            "",
            "## How to clear a finding",
            "",
            "1. Run the lab canary or a live walkthrough.",
            "2. Update the content, links, ATT&CK mapping, and tool list if needed.",
            "3. Change `reviewed_at` and `review_status` in the same pull request as the content.",
            "4. Re-run `python scripts/check-lab-freshness.py`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--today", help="Override today's date (YYYY-MM-DD)")
    parser.add_argument("--max-age-days", type=int, default=365)
    parser.add_argument("--provisional-max-days", type=int, default=180)
    parser.add_argument("--json", type=Path, help="Write the machine-readable report")
    parser.add_argument("--write", type=Path, help="Write a Markdown report")
    args = parser.parse_args()

    today = date.fromisoformat(args.today) if args.today else date.today()
    rows = collect(today, args.max_age_days, args.provisional_max_days)
    stale = [row for row in rows if row["stale"]]
    promotion = [row for row in rows if row["promotion_candidate"]]

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(
                {
                    "generated": today.isoformat(),
                    "max_age_days": args.max_age_days,
                    "provisional_max_days": args.provisional_max_days,
                    "labs": rows,
                    "stale": stale,
                    "promotion_candidates": promotion,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(
            render(rows, today, args.max_age_days, args.provisional_max_days),
            encoding="utf-8",
        )

    print(
        f"lab freshness: {len(rows)} labs, {len(stale)} stale or missing review, "
        f"{len(promotion)} difficulty promotion candidate(s)"
    )
    for row in stale[:20]:
        print(f"  STALE {row['slug']}: {row['stale_reason']}")
    if len(stale) > 20:
        print(f"  ... {len(stale) - 20} more")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
