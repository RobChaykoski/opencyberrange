"""Backfill achievement awards for completions earned before a rules change.

Run after upgrading when an achievement rule changed (for example, enabling
global awards for standalone labs and competitions). The check is idempotent:
an award that already exists is skipped, so it is safe to run more than once.

Usage:
    docker compose --env-file .env -f docker-compose.prod.yml exec -T backend \
      python /app/app/scripts/backfill_achievements.py
"""
from collections import defaultdict

from app.database import SessionLocal
from app.models import LabCompletion
from app.services.achievements import check_achievements


def main() -> None:
    db = SessionLocal()
    try:
        rows = db.query(LabCompletion.user_id, LabCompletion.lab_id).filter(
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        ).all()

        by_user = defaultdict(list)
        for user_id, lab_id in rows:
            by_user[user_id].append(lab_id)

        checked = 0
        for user_id, lab_ids in by_user.items():
            for lab_id in lab_ids:
                check_achievements(db, user_id, lab_id)
                checked += 1

        print(
            f"Backfill complete: checked {checked} completions "
            f"for {len(by_user)} users"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
