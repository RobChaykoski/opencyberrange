#!/usr/bin/env python3
"""Report pinned backend versions against the latest PyPI release.

This is a currency report, not an audit. It never fails the build by default;
`--fail-on-outdated` is available for a deliberate dependency wave.
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
VERSIONS = ROOT / "versions.yaml"
PYPI = "https://pypi.org/pypi/{package}/json"
CORE = (
    ("fastapi", "fastapi"),
    ("sqlalchemy", "sqlalchemy"),
    ("pydantic", "pydantic"),
    ("pydantic-settings", "pydantic-settings"),
    ("uvicorn", "uvicorn"),
    ("cryptography", "cryptography"),
    ("alembic", "alembic"),
    ("psycopg", "psycopg"),
    ("redis", "redis"),
)


def _pins() -> dict:
    with VERSIONS.open(encoding="utf-8") as handle:
        document = yaml.safe_load(handle) or {}
    return document.get("backend") or {}


def _latest(package: str) -> str:
    request = urllib.request.Request(
        PYPI.format(package=package),
        headers={"User-Agent": "OpenCyberRange-dependency-currency/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return str((payload.get("info") or {}).get("version") or "unknown")
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--fail-on-outdated",
        action="store_true",
        help="Exit 1 when a core pin is older than the latest release",
    )
    args = parser.parse_args()
    pins = _pins()
    rows = []
    outdated = 0
    for key, package in CORE:
        current = str(pins.get(key) or "unset")
        latest = _latest(package)
        is_outdated = latest not in {"unknown", current}
        if is_outdated:
            outdated += 1
        rows.append(
            {
                "package": package,
                "current": current,
                "latest": latest,
                "outdated": is_outdated,
            }
        )
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(f"{'package':22} {'current':12} {'latest':12} status")
        for row in rows:
            status = "update" if row["outdated"] else "current"
            print(
                f"{row['package']:22} {row['current']:12} "
                f"{row['latest']:12} {status}"
            )
        print(f"\n{outdated} core package(s) behind.")
    if args.fail_on_outdated and outdated:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
