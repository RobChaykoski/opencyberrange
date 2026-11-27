#!/usr/bin/env python3
"""Aggregate the first-time user test timing sheet.

Usage:
    python scripts/first_time_user_test.py docs/research/first-time-user-test/timing-sheet.csv
    python scripts/first_time_user_test.py <sheet.csv> --json

The sheet is one row per participant. Timestamps are ISO-8601; blank values are
allowed for a phase that does not apply (for example VPN on a browser-only minor
lab). The script never prints a name or email; it groups by persona.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

PHASES = (
    ("register", "start", "register_done"),
    ("approval", "register_done", "approved_login"),
    ("vpn", "approved_login", "vpn_connected"),
    ("lab", "lab_ready_base", "lab_ready"),
    ("flag", "lab_ready", "flag_accepted"),
)


def parse_time(value: str) -> datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def minutes(start: datetime | None, end: datetime | None) -> float | None:
    if start is None or end is None:
        return None
    return round((end - start).total_seconds() / 60.0, 2)


def p90(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(0.9 * len(ordered)) - 1)
    return round(ordered[index], 2)


def aggregate(path: Path) -> dict:
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
    if not rows:
        raise SystemExit("timing sheet is empty")
    by_persona: dict[str, list[dict]] = defaultdict(list)
    phase_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    stuck = Counter()
    errors: list[str] = []

    for index, row in enumerate(rows, start=2):
        persona = (row.get("persona") or "unknown").strip()
        start = parse_time(row.get("start", ""))
        register = parse_time(row.get("register_done", ""))
        approved = parse_time(row.get("approved_login", ""))
        vpn = parse_time(row.get("vpn_connected", ""))
        lab = parse_time(row.get("lab_ready", ""))
        flag = parse_time(row.get("flag_accepted", ""))
        lab_base = vpn or approved
        values = {
            "register": minutes(start, register),
            "approval": minutes(register, approved),
            "vpn": minutes(approved, vpn),
            "lab": minutes(lab_base, lab),
            "flag": minutes(lab, flag),
            "total": minutes(start, flag),
        }
        for phase, value in values.items():
            if value is not None and value < 0:
                errors.append(f"row {index}: {phase} is negative")
            elif value is not None:
                phase_values[persona][phase].append(value)
        by_persona[persona].append(
            {
                "participant_id": (row.get("participant_id") or f"row-{index}").strip(),
                "total": values["total"],
                "assisted": (row.get("assisted") or "").strip().lower() in {"1", "true", "yes", "y"},
                "outcome": (row.get("outcome") or "").strip().lower(),
            }
        )
        for phase in (row.get("stuck_phases") or "").replace(",", ";").split(";"):
            phase = phase.strip()
            if phase:
                stuck[phase] += 1

    summary = {}
    for persona, entries in sorted(by_persona.items()):
        totals = [item["total"] for item in entries if item["total"] is not None]
        summary[persona] = {
            "participants": len(entries),
            "completed": sum(1 for item in entries if item["outcome"].startswith("completed")),
            "assisted": sum(1 for item in entries if item["assisted"]),
            "abandoned": sum(1 for item in entries if item["outcome"] == "abandoned"),
            "technical_failure": sum(1 for item in entries if item["outcome"] == "technical_failure"),
            "median_register": round(statistics.median(phase_values[persona]["register"]), 2)
            if phase_values[persona]["register"]
            else None,
            "median_approval": round(statistics.median(phase_values[persona]["approval"]), 2)
            if phase_values[persona]["approval"]
            else None,
            "median_vpn": round(statistics.median(phase_values[persona]["vpn"]), 2)
            if phase_values[persona]["vpn"]
            else None,
            "median_lab": round(statistics.median(phase_values[persona]["lab"]), 2)
            if phase_values[persona]["lab"]
            else None,
            "median_flag": round(statistics.median(phase_values[persona]["flag"]), 2)
            if phase_values[persona]["flag"]
            else None,
            "median_total": round(statistics.median(totals), 2) if totals else None,
            "p90_total": p90(totals),
            "under_15": sum(1 for value in totals if value < 15),
            "under_15_rate": round(100.0 * sum(1 for value in totals if value < 15) / len(totals), 1)
            if totals
            else None,
        }

    all_totals = [item["total"] for entries in by_persona.values() for item in entries if item["total"] is not None]
    return {
        "rows": len(rows),
        "personas": summary,
        "overall": {
            "participants": len(rows),
            "median_total": round(statistics.median(all_totals), 2) if all_totals else None,
            "p90_total": p90(all_totals),
            "under_15": sum(1 for value in all_totals if value < 15),
            "under_15_rate": round(100.0 * sum(1 for value in all_totals if value < 15) / len(all_totals), 1)
            if all_totals
            else None,
        },
        "stuck_phases": dict(stuck.most_common()),
        "errors": errors,
    }


def render(report: dict) -> str:
    lines = [
        "First-time user test",
        "=" * 40,
        f"participants: {report['rows']}",
        "",
        "| Persona | n | Median register | Median approval | Median VPN | Median lab | Median flag | Median total | p90 | Under 15:00 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for persona, row in report["personas"].items():
        def cell(key, row=row):
            value = row[key]
            return "-" if value is None else f"{value:.1f}"

        lines.append(
            f"| {persona} | {row['participants']} | {cell('median_register')} | "
            f"{cell('median_approval')} | {cell('median_vpn')} | {cell('median_lab')} | "
            f"{cell('median_flag')} | {cell('median_total')} | {cell('p90_total')} | "
            f"{row['under_15']}/{row['participants']} ({row['under_15_rate'] or 0:.1f}%) |"
        )
    overall = report["overall"]
    lines += [
        "",
        (
            f"Overall median: {overall['median_total']} min; p90: {overall['p90_total']} min; "
            f"under 15:00: {overall['under_15']}/{overall['participants']} ({overall['under_15_rate']}%)."
        ),
    ]
    if report["stuck_phases"]:
        lines += ["", "Top stuck phases:"]
        for phase, count in list(report["stuck_phases"].items())[:10]:
            lines.append(f"  {phase}: {count}")
    if report["errors"]:
        lines += ["", "Errors:"] + [f"  {error}" for error in report["errors"]]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.sheet.is_file():
        raise SystemExit(f"no such sheet: {args.sheet}")
    report = aggregate(args.sheet)
    print(json.dumps(report, indent=2) if args.json else render(report))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
