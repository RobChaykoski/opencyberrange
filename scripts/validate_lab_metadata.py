#!/usr/bin/env python3
"""Validate every platform/labs/**/lab.yaml against the canonical schema.

The schema is deliberately strict at the top level and on the nested structures
the loader consumes. Unknown keys fail, so a typo in a lab header is caught in
CI instead of silently producing an incomplete lab.

Usage:
    python scripts/validate_lab_metadata.py
    python scripts/validate_lab_metadata.py --labs-dir platform/labs
    python scripts/validate_lab_metadata.py --schema platform/backend/lab_metadata.schema.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - CI installs requirements-dev
    print(
        "error: jsonschema is required. Install platform/backend/requirements-dev.txt.",
        file=sys.stderr,
    )
    raise SystemExit(2)


def _path_label(error) -> str:
    parts = [str(part) for part in error.path]
    return "/".join(parts) if parts else "<root>"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--labs-dir",
        default="platform/labs",
        help="Directory containing track/lab directories (default: platform/labs)",
    )
    parser.add_argument(
        "--schema",
        default="platform/backend/lab_metadata.schema.json",
        help="Path to the JSON Schema (default: platform/backend/lab_metadata.schema.json)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print failures and the final summary",
    )
    args = parser.parse_args()

    schema_path = Path(args.schema)
    labs_dir = Path(args.labs_dir)
    if not schema_path.is_file():
        print(f"error: schema not found: {schema_path}", file=sys.stderr)
        return 2
    if not labs_dir.is_dir():
        print(f"error: labs directory not found: {labs_dir}", file=sys.stderr)
        return 2

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    files = sorted(labs_dir.rglob("lab.yaml"))
    if not files:
        print(f"error: no lab.yaml files under {labs_dir}", file=sys.stderr)
        return 2

    failed_files = 0
    errors_total = 0
    for path in files:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            failed_files += 1
            errors_total += 1
            mark = getattr(exc, "problem_mark", None)
            location = f" line {mark.line + 1}" if mark is not None else ""
            print(f"FAIL: {path}{location}: YAML parse error: {exc}", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            failed_files += 1
            errors_total += 1
            print(f"FAIL: {path}: top level must be a mapping", file=sys.stderr)
            continue
        errors = sorted(validator.iter_errors(data), key=lambda item: list(item.path))
        if errors:
            failed_files += 1
            errors_total += len(errors)
            for error in errors:
                print(
                    f"FAIL: {path}: {_path_label(error)}: {error.message}",
                    file=sys.stderr,
                )
        elif not args.quiet:
            print(f"OK:   {path}")

    if errors_total:
        print(
            f"FAILED: {errors_total} error(s) across {failed_files} of {len(files)} "
            "lab.yaml file(s)",
            file=sys.stderr,
        )
        return 1
    print(f"OK: {len(files)} lab.yaml file(s) validated against {schema_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
