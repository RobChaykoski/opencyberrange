#!/usr/bin/env python3
"""Instructor lab-friction report.

Ranks the catalogue by completion rate, failed-flag attempts per solve, and hint
use. This is the first instructor-pack report: it turns existing session,
completion, and flag-attempt rows into a short list of labs that need attention.

Examples:
    python scripts/lab_friction_report.py
    python scripts/lab_friction_report.py --course-id 7 --limit 25
    python scripts/lab_friction_report.py --json
    python scripts/lab_friction_report.py --csv lab-friction.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "platform" / "backend"
sys.path.insert(0, str(BACKEND))

from app.config import settings
from sqlalchemy import create_engine, text

QUERY = """
WITH cohort AS (
    SELECT user_id
    FROM course_enrollments
    WHERE course_id = :course_id
),
sessions AS (
    SELECT s.lab_id, COUNT(*) AS starts
    FROM lab_sessions s
    WHERE (:course_id IS NULL OR s.user_id IN (SELECT user_id FROM cohort))
    GROUP BY s.lab_id
),
completions AS (
    SELECT c.lab_id,
           COUNT(*) AS completions,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY c.time_spent_minutes) AS median_minutes
    FROM lab_completions c
    WHERE c.flag_submitted IS NOT NULL
      AND c.flag_submitted <> ''
      AND (:course_id IS NULL OR c.user_id IN (SELECT user_id FROM cohort))
    GROUP BY c.lab_id
),
attempts AS (
    SELECT a.lab_id,
           COUNT(*) FILTER (
               WHERE a.is_correct = false
                 AND a.flag_submitted NOT LIKE 'HINT%%'
           ) AS failed_attempts,
           COUNT(*) FILTER (WHERE a.flag_submitted LIKE 'HINT%%') AS hint_uses
    FROM flag_attempts a
    WHERE (:course_id IS NULL OR a.user_id IN (SELECT user_id FROM cohort))
    GROUP BY a.lab_id
)
SELECT l.id,
       l.name,
       l.slug,
       l.difficulty,
       l.category,
       COALESCE(s.starts, 0) AS starts,
       COALESCE(c.completions, 0) AS completions,
       COALESCE(a.failed_attempts, 0) AS failed_attempts,
       COALESCE(a.hint_uses, 0) AS hint_uses,
       ROUND(c.median_minutes::numeric, 1) AS median_minutes,
       CASE
           WHEN COALESCE(s.starts, 0) > 0
           THEN ROUND(100.0 * COALESCE(c.completions, 0) / s.starts, 1)
           ELSE NULL
       END AS completion_rate,
       CASE
           WHEN COALESCE(c.completions, 0) > 0
           THEN ROUND(1.0 * COALESCE(a.failed_attempts, 0) / c.completions, 2)
           ELSE NULL
       END AS failed_per_completion,
       CASE
           WHEN COALESCE(c.completions, 0) > 0
           THEN ROUND(1.0 * COALESCE(a.hint_uses, 0) / c.completions, 2)
           ELSE NULL
       END AS hints_per_completion
FROM labs l
LEFT JOIN sessions s ON s.lab_id = l.id
LEFT JOIN completions c ON c.lab_id = l.id
LEFT JOIN attempts a ON a.lab_id = l.id
WHERE l.is_active = true
  AND COALESCE(s.starts, 0) >= :min_starts
ORDER BY completion_rate ASC NULLS LAST,
         failed_per_completion DESC NULLS LAST,
         l.name
LIMIT :limit
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--course-id", type=int, default=None)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--min-starts", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--db-url", default=None)
    args = parser.parse_args()

    url = args.db_url or os.environ.get("DATABASE_URL") or settings.DATABASE_URL
    engine = create_engine(url, pool_pre_ping=True)
    with engine.connect() as conn:
        rows = [
            dict(row._mapping)
            for row in conn.execute(
                text(QUERY),
                {
                    "course_id": args.course_id,
                    "limit": args.limit,
                    "min_starts": args.min_starts,
                },
            )
        ]

    if args.json:
        print(json.dumps(rows, indent=2, default=str))
    else:
        header = (
            f"{'completion':>10} {'failed/solve':>12} {'hints/solve':>11} "
            f"{'starts':>7} {'solves':>7}  lab"
        )
        print(header)
        print("-" * len(header))
        for row in rows:
            completion = "-" if row["completion_rate"] is None else f"{row['completion_rate']:.1f}%"
            failed = "-" if row["failed_per_completion"] is None else f"{row['failed_per_completion']:.2f}"
            hints = "-" if row["hints_per_completion"] is None else f"{row['hints_per_completion']:.2f}"
            print(
                f"{completion:>10} {failed:>12} {hints:>11} "
                f"{row['starts']:>7} {row['completions']:>7}  {row['name']}"
            )

    if args.csv:
        columns = [
            "id",
            "name",
            "slug",
            "difficulty",
            "category",
            "starts",
            "completions",
            "completion_rate",
            "failed_attempts",
            "failed_per_completion",
            "hint_uses",
            "hints_per_completion",
            "median_minutes",
        ]
        with args.csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {args.csv} ({len(rows)} rows)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
