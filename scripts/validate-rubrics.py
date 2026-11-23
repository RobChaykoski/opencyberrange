#!/usr/bin/env python3
"""Validate the versioned rubric registry."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "platform" / "backend"))

from app.services.rubrics import load_rubrics, validate_rubrics


def main() -> int:
    problems = validate_rubrics()
    rubrics = load_rubrics()
    print(f"rubrics: {len(rubrics)} loaded")
    for rubric_id, document in sorted(rubrics.items()):
        print(f"  {rubric_id} v{document.get('version')}: {len(document.get('criteria') or [])} criteria")
    for problem in problems:
        print(f"ERROR: {problem}")
    if problems:
        print(f"FAILED: {len(problems)} error(s)")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
