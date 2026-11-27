#!/usr/bin/env python3
"""Audit flag exposure in the public tree.

The platform rotates flags per session for the labs that declare a flag render
contract. The remaining labs use a static value, and some of those values are
written into public files (lab source, tester manifests, workbook walkthroughs).

This script distinguishes three things:

* the static flag declarations in `platform/labs/**` (expected, but the value is
  public while the lab is not rotating);
* template and demo values (`OCR{token1_token2}`, `OCR{demo}`, ...);
* leaked answers: a public file outside the lab tree that repeats a static lab
  flag. Those are the immediate integrity problem.

Usage:
    python scripts/audit_flag_exposure.py
    python scripts/audit_flag_exposure.py --json
    python scripts/audit_flag_exposure.py --fail-on-leaks
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FLAG_RE = re.compile(r"OCR\{[^}\n]{1,120}\}")
REAL_RE = re.compile(r"^OCR\{[a-z0-9][a-z0-9_\-]{3,}\}$")
TEMPLATE_MARKERS = (
    "<",
    "...",
    "your",
    "flag_here",
    "example",
    "sample",
    "xxx",
    "todo",
    "redacted",
    "replace_me",
    "token",
    "demo",
    "deco",
    "d3c0y",
    "not_the",
    "session_flag",
    "pytest",
    "smoke",
    "test",
)
# Public OSINT markers are meant to be discoverable on the open web; they are
# not graded lab answers, even when a matching lab flag exists.
INTENTIONAL_PUBLIC_MARKERS = {"platform/backend/app/data/external-targets.yaml"}
AREAS = (
    "platform/labs",
    "platform/tester",
    "Workbook",
    "docs",
    "platform/backend",
    "Manual-Lite",
)
SUFFIXES = {".yaml", ".yml", ".md", ".py", ".sh", ".json", ".txt", ".js", ".vue", ".conf"}


def _is_real(value: str) -> bool:
    if not REAL_RE.match(value):
        return False
    lowered = value.lower()
    if any(marker in lowered for marker in TEMPLATE_MARKERS):
        return False
    return not any(
        ch in value for ch in ("'", '"', "$", "(", ")", "+", ";", " ", "|", "&", "%")
    )


def _labs() -> dict[str, dict]:
    labs: dict[str, dict] = {}
    for lab_yaml in (ROOT / "platform/labs").rglob("lab.yaml"):
        slug = lab_yaml.parent.name
        data = {}
        try:
            data = yaml.safe_load(lab_yaml.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            pass
        # Baked labs declare an explicit render contract.
        rotating = any(
            data.get(key)
            for key in ("flag_path", "flag_service", "flag_command", "flag_owner")
        )
        # Environment-driven labs rotate when a FLAG/*_FLAG compose value
        # matches the lab flag; the launcher substitutes a session value.
        flag_value = str(data.get("flag") or "").strip()
        if not rotating and flag_value:
            compose = lab_yaml.parent / "docker-compose.yml"
            if compose.is_file():
                try:
                    compose_data = yaml.safe_load(compose.read_text(encoding="utf-8")) or {}
                except (OSError, yaml.YAMLError):
                    compose_data = {}
                for service in (compose_data.get("services") or {}).values():
                    if not isinstance(service, dict):
                        continue
                    environment = service.get("environment")
                    entries = []
                    if isinstance(environment, dict):
                        entries = [(str(k), str(v)) for k, v in environment.items()]
                    elif isinstance(environment, list):
                        entries = [
                            tuple(str(item).split("=", 1))
                            for item in environment
                            if isinstance(item, str) and "=" in item
                        ]
                    for key, value in entries:
                        if (
                            key.upper() == "FLAG"
                            or key.upper().endswith("_FLAG")
                        ) and value == flag_value:
                            rotating = True
        labs[slug] = {"rotating": bool(rotating), "path": lab_yaml.parent}
    return labs


def _area_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    for area in AREAS:
        if rel.startswith(area + "/"):
            return area
    return "other"


def _lab_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if len(rel.parts) >= 3 and rel.parts[0] == "platform" and rel.parts[1] == "labs":
        return rel.parts[3] if len(rel.parts) > 4 else ""
    return ""


def scan() -> dict:
    labs = _labs()
    static_flags: dict[str, set[str]] = defaultdict(set)
    occurrences = defaultdict(lambda: {"files": 0, "values": 0, "static_labs": set()})
    rows: list[dict] = []
    seen_files: set[Path] = set()

    for area in AREAS:
        base = ROOT / area
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            lab = _lab_for(path)
            for value in FLAG_RE.findall(text):
                occurrences[area]["values"] += 1
                if path not in seen_files:
                    occurrences[area]["files"] += 1
                    seen_files.add(path)
                if not _is_real(value):
                    continue
                rows.append(
                    {
                        "file": path.relative_to(ROOT).as_posix(),
                        "area": area,
                        "flag": value,
                        "lab": lab,
                        "rotating": labs.get(lab, {}).get("rotating") if lab else None,
                    }
                )
                if lab and not labs.get(lab, {}).get("rotating"):
                    static_flags[lab].add(value)
                    occurrences[area]["static_labs"].add(lab)

    static_values = set().union(*static_flags.values()) if static_flags else set()
    leaks = [
        row
        for row in rows
        if row["area"] != "platform/labs"
        and row["flag"] in static_values
        and row["file"] not in INTENTIONAL_PUBLIC_MARKERS
    ]
    return {
        "areas": {
            area: {
                "files": data["files"],
                "values": data["values"],
                "static_labs": sorted(data["static_labs"]),
            }
            for area, data in occurrences.items()
        },
        "static_labs": {lab: sorted(values) for lab, values in static_flags.items()},
        "rows": rows,
        "leaks": leaks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the full finding list")
    parser.add_argument(
        "--fail-on-leaks",
        action="store_true",
        help="exit non-zero when a public file repeats a static lab flag",
    )
    args = parser.parse_args()
    result = scan()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Flag exposure audit")
        print("=" * 40)
        for area, data in result["areas"].items():
            print(
                f"{area}: {data['values']} value(s), {data['files']} file(s), "
                f"{len(data['static_labs'])} static lab(s)"
            )
        print(f"\nstatic labs declaring a public flag value: {len(result['static_labs'])}")
        print(f"leaked answers outside the lab tree: {len(result['leaks'])}")
        for row in result["leaks"][:20]:
            print(f"   {row['file']}: {row['flag']}")
    if args.fail_on_leaks and result["leaks"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
