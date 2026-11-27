#!/usr/bin/env python3
"""Run the release test matrix in platform/tester/release-tests.yaml.

Examples:
    python scripts/release_tests.py --list
    python scripts/release_tests.py --automated-only
    python scripts/release_tests.py --automated-only --json release-tests.json
    python scripts/release_tests.py --live --test lab-launch --test docker-isolation

Manual entries are reported, never marked passed by this script. A skip is a
gap: use --strict to fail on a skipped automated test as well as a failed one.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "platform" / "tester" / "release-tests.yaml"


def load_matrix() -> list[dict]:
    data = yaml.safe_load(MATRIX.read_text(encoding="utf-8")) or {}
    return data.get("tests") or []


def missing_requirements(test: dict) -> list[str]:
    return [key for key in test.get("requires") or [] if not os.environ.get(key)]


def run_test(test: dict, live: bool) -> dict:
    test_id = test["id"]
    if test.get("type") == "manual":
        return {"id": test_id, "title": test["title"], "status": "manual", "detail": "evidence required"}
    if test.get("live") and not live:
        return {"id": test_id, "title": test["title"], "status": "skip", "detail": "live test not requested"}
    missing = missing_requirements(test)
    if missing:
        return {
            "id": test_id,
            "title": test["title"],
            "status": "skip",
            "detail": "missing env: " + ", ".join(missing),
        }
    command = list(test.get("command") or [])
    # Run the interpreter that launched this script. A venv's python.exe can
    # be a symlink, and Windows then searches the target's directory for a
    # bare "python", which silently selects a different interpreter.
    if command and command[0] == "python":
        command[0] = sys.executable
    cwd = ROOT / (test.get("cwd") or ".")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=int(test.get("timeout") or 1800),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"id": test_id, "title": test["title"], "status": "fail", "detail": str(exc)}
    detail = (result.stdout or "")[-800:] + (result.stderr or "")[-800:]
    return {
        "id": test_id,
        "title": test["title"],
        "status": "pass" if result.returncode == 0 else "fail",
        "detail": detail.strip(),
        "returncode": result.returncode,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--automated-only", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--strict", action="store_true", help="fail on skipped automated tests")
    parser.add_argument("--test", action="append", default=[], help="test id; repeat as needed")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    tests = load_matrix()
    if args.test:
        wanted = set(args.test)
        tests = [test for test in tests if test["id"] in wanted]
    if args.list:
        for test in tests:
            print(f"{test['id']:24} {test.get('type', 'command'):8} {test['title']}")
        return 0

    results = []
    for test in tests:
        if args.automated_only and test.get("type") == "manual":
            results.append(
                {"id": test["id"], "title": test["title"], "status": "manual", "detail": "evidence required"}
            )
            continue
        print(f"==> {test['id']}: {test['title']}", flush=True)
        result = run_test(test, args.live)
        results.append(result)
        print(f"    {result['status'].upper()}: {result.get('detail', '')[:300]}", flush=True)

    counts = {key: sum(1 for item in results if item["status"] == key) for key in ("pass", "fail", "skip", "manual")}
    payload = {"counts": counts, "results": results}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("\nRelease test summary")
        print("=" * 30)
        for key in ("pass", "fail", "skip", "manual"):
            print(f"  {key:6} {counts[key]}")
        if counts["manual"]:
            print("\nManual evidence required:")
            for item in results:
                if item["status"] == "manual":
                    print(f"  - {item['id']}: {item['title']}")

    if counts["fail"]:
        return 1
    if args.strict and counts["skip"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
