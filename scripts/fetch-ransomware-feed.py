#!/usr/bin/env python3
"""Build an aggregated ransomware-activity snapshot from RansomLook.

Only two public aggregate endpoints are read:

- ``/api/stats`` - totals for groups, markets, and posts.
- ``/api/hot``   - seven-day totals and per-group post counts.

``/api/recent`` is deliberately not used: its ``post_title`` is the victim
organisation name. This script never reads, stores, or writes victim names,
post links, crypto addresses, or peer addresses.

RansomLook's content is CC BY 4.0; its code is AGPL-3.0 and is not used. See
ADR 0009.

Usage::

    python scripts/fetch-ransomware-feed.py --dry-run
    python scripts/fetch-ransomware-feed.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "platform" / "backend" / "app" / "data" / "ransomware-activity.json"
BASE_URL = "https://www.ransomlook.io"
ATTRIBUTION = (
    "Aggregated counts derived from RansomLook (ransomlook.io), CC BY 4.0. "
    "No victim details are included."
)
STAT_FIELDS = (
    "posts_24h",
    "posts_month",
    "posts_90d",
    "posts_year",
    "posts_total",
    "groups",
    "groups_online",
    "markets",
)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _get(path: str, timeout: float) -> dict:
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        headers={
            "User-Agent": "OpenCyberRange-ransomware-feed/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise SystemExit(f"cannot read {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"{path} did not return a JSON object")
    return payload


def _count(payload: dict, key: str, *, source: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SystemExit(f"{source}.{key} is missing or not a non-negative integer")
    return value


def _groups(hot: dict, maximum: int) -> list[dict]:
    rows = hot.get("rows")
    if not isinstance(rows, list):
        raise SystemExit("/api/hot rows is missing")
    groups = []
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit("/api/hot rows must be objects")
        name = row.get("group")
        if not isinstance(name, str) or not name.strip():
            raise SystemExit("/api/hot row has no group name")
        groups.append({"name": name.strip(), "count": _count(row, "count", source="hot")})
        if len(groups) >= maximum:
            break
    if not groups:
        raise SystemExit("/api/hot returned no groups")
    return groups


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--max-groups", type=int, default=15)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.max_groups < 1:
        parser.error("--max-groups must be at least 1")

    stats = _get("/api/stats", args.timeout)
    hot = _get("/api/hot", args.timeout)

    totals = {field: _count(stats, field, source="stats") for field in STAT_FIELDS}
    totals["window_posts"] = _count(hot, "total_posts", source="hot")
    window_days = _count(hot, "days", source="hot") or 7

    groups = _groups(hot, args.max_groups)
    if sum(row["count"] for row in groups) > totals["window_posts"]:
        raise SystemExit("group counts exceed the reported window total")

    document = {
        "schema_version": 1,
        "mode": "snapshot",
        "generated_at": _now(),
        "window_days": window_days,
        "source": {
            "name": "RansomLook",
            "url": "https://www.ransomlook.io/",
            "licence": "CC BY 4.0",
            "attribution": ATTRIBUTION,
        },
        "method": {
            "aggregation": "group",
            "victim_details": False,
            "links": False,
            "crypto_addresses": False,
        },
        "totals": totals,
        "groups": groups,
        "notes": [
            (
                "Counts are aggregated per group. Victim names, post links, crypto "
                "addresses, and peer addresses are excluded."
            ),
            (
                "Not live attack telemetry. This is a periodic snapshot of publicly "
                "reported ransomware posts."
            ),
        ],
    }

    output = Path(args.output)
    if args.dry_run:
        print(json.dumps(document, indent=2))
        print(f"dry run: would write {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(
        dir=output.parent, prefix=".ransomware-activity-", suffix=".json"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(document, handle, indent=2)
            handle.write("\n")
        os.replace(temp, output)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise
    print(
        f"wrote {output}: {totals['window_posts']} posts in {window_days} days "
        f"across {len(groups)} reported groups"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
