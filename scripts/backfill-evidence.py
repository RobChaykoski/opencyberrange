#!/usr/bin/env python3
"""Backfill Cyber DNA evidence from existing lab completions.

Run inside the backend image:

    docker exec -w /app ocr-backend python /app/scripts/backfill-evidence.py --dry-run
    docker exec -w /app ocr-backend python /app/scripts/backfill-evidence.py

This is an exercise-side adapter: it reads completions and emits the same
``ActivityCompleted`` events the live completion path emits. Cyber DNA itself
never reads exercise tables. Consent is checked per learner, so a completion
that predates a revocation never recreates evidence.
"""

from __future__ import annotations

import argparse
import sys

from app.database import SessionLocal
from app.services.dna_events import backfill_completions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Count without writing")
    parser.add_argument("--user-id", type=int, default=None, help="One learner only")
    parser.add_argument("--limit", type=int, default=None, help="Stop after N completions")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        stats = backfill_completions(
            db,
            dry_run=args.dry_run,
            user_id=args.user_id,
            limit=args.limit,
        )
    finally:
        db.close()

    mode = "DRY RUN" if args.dry_run else "WROTE"
    print(
        f"{mode}: {stats['completions']} completion(s), "
        f"{stats['evidence_rows']} evidence row(s), "
        f"{stats['no_mapping']} without a mapping, "
        f"{stats['blocked']} blocked by consent, "
        f"{stats['learners']} consenting learner(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
