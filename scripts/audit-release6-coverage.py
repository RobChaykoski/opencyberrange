#!/usr/bin/env python3
"""Audit Release 6 object coverage.

This is a report, not a review. It checks the objects that must carry a
competency mapping for Release 6.0:

* every lab has a contract and a non-empty competency link;
* every competency id exists in the taxonomy;
* competency and evidence weights sum to 1.0;
* every certification quiz pathway has a competency mapping;
* every exercise quiz belongs to a lab with a contract;
* capstones and badges are reported honestly rather than treated as mapped.

Usage:
    python scripts/audit-release6-coverage.py
    python scripts/audit-release6-coverage.py --json
    python scripts/audit-release6-coverage.py --fail-on-gaps
    python scripts/audit-release6-coverage.py --require-reviewed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "platform" / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.competency_coverage import release6_audit


def print_report(audit: dict) -> None:
    labs = audit["labs"]
    quizzes = audit["quiz_pathways"]
    exercises = audit["exercise_quizzes"]
    print("Release 6 coverage audit")
    print("=" * 40)
    print(
        f"Labs: {labs['total']} total, {labs['contracts']} contracts, "
        f"{labs['reviewed']} reviewed, {labs['pending_review']} pending review"
    )
    print(
        f"  missing contract: {len(labs['missing_contract'])}  "
        f"missing competencies: {len(labs['missing_competencies'])}  "
        f"unknown competencies: {len(labs['unknown_competencies'])}  "
        f"bad weights: {len(labs['bad_weights'])}"
    )
    print(
        f"Quiz pathways: {quizzes['total']} total, {quizzes['mapped']} mapped, "
        f"{len(quizzes['unmapped'])} unmapped, "
        f"{len(quizzes['unknown_competencies'])} unknown competency ids"
    )
    print(
        f"Exercise quizzes: {exercises['total']} total, "
        f"{exercises['with_contract']} with a lab contract, "
        f"{len(exercises['without_contract'])} without"
    )
    print(
        f"Capstones: {audit['capstones']['status']} "
        f"({audit['capstones']['objects']} objects)"
    )
    print(f"Badges: {audit['badges']['status']}")
    if audit["release_6_ready"]:
        print("Result: READY for Release 6 object coverage")
    else:
        pending = labs["pending_review"]
        if audit["structural_gaps"]:
            print(f"Result: NOT READY - structural gaps; {pending} contracts pending review")
        else:
            print(
                f"Result: NOT READY - {pending} contracts pending review, "
                "no structural gaps; capstones are not implemented and badges "
                "are derived"
            )
    if audit["foundation_ready"]:
        print("Foundation (6.0): READY")
    else:
        print("Foundation (6.0): NOT READY")
    for key in ("missing_contract", "missing_competencies", "unknown_competencies", "bad_weights"):
        for item in labs[key][:10]:
            print(f"  lab {key}: {item}")
    for item in quizzes["unmapped"][:10]:
        print(f"  quiz pathway unmapped: {item}")
    for item in quizzes["unknown_competencies"][:10]:
        print(f"  quiz unknown competency: {item}")
    for item in exercises["without_contract"][:10]:
        print(f"  exercise quiz without a contract: {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Release 6 coverage")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    parser.add_argument(
        "--fail-on-gaps",
        action="store_true",
        help="Exit 1 when a structural mapping gap exists",
    )
    parser.add_argument(
        "--require-reviewed",
        action="store_true",
        help="Exit 1 while any competency contract is still baseline-derived",
    )
    args = parser.parse_args()
    audit = release6_audit()
    if args.json:
        print(json.dumps(audit, indent=2))
    else:
        print_report(audit)
    if args.fail_on_gaps and audit["structural_gaps"]:
        return 1
    if args.require_reviewed and audit["labs"]["pending_review"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
