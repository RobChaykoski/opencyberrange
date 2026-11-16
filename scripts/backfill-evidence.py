#!/usr/bin/env python3
"""Backfill Cyber DNA evidence from existing lab completions.

Run inside the backend image:

    docker exec -w /app ocr-backend python /app/scripts/backfill-evidence.py --dry-run
    docker exec -w /app ocr-backend python /app/scripts/backfill-evidence.py

This is an exercise-side adapter: it reads completions and emits the same
``ActivityCompleted`` events the live completion path emits. Cyber DNA itself
never reads exercise tables.
"""

from __future__ import annotations

import argparse
import sys

from app.cyber_dna.service import ingest_activity
from app.database import SessionLocal
from app.models import LabCompletion
from app.services.dna_events import build_completion_event
from sqlalchemy.orm import joinedload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Count without writing")
    parser.add_argument("--user-id", type=int, default=None, help="One learner only")
    parser.add_argument("--limit", type=int, default=None, help="Stop after N completions")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        query = (
            db.query(LabCompletion)
            .options(joinedload(LabCompletion.lab))
            .filter(
                LabCompletion.flag_submitted.isnot(None),
                LabCompletion.flag_submitted != "",
            )
            .order_by(LabCompletion.completed_at.asc())
        )
        if args.user_id:
            query = query.filter(LabCompletion.user_id == args.user_id)
        if args.limit:
            query = query.limit(args.limit)

        completions_seen = 0
        rows_written = 0
        no_mapping = 0
        for completion in query.all():
            completions_seen += 1
            event = build_completion_event(
                db, completion.user_id, completion, completion.lab
            )
            if event is None:
                no_mapping += 1
                continue
            if args.dry_run:
                rows_written += len(event.competency_weights)
            else:
                rows_written += ingest_activity(db, event)

        mode = "DRY RUN" if args.dry_run else "WROTE"
        print(
            f"{mode}: {completions_seen} completion(s), "
            f"{rows_written} evidence row(s), {no_mapping} without a mapping"
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
