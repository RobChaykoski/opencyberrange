"""Seed Cyber DNA v3 development fixtures. Development/test only.

The script:

* creates a synthetic student (``dna_fixture_ready``) with a rich completion
  history copied from ``dummyadmin``;
* grants ``cyber_dna`` consent to the fixture and to ``demo_career_ready`` (a
  below-gate case) with an explicit admin audit reason;
* optionally purges DNA evidence for every learner without granted consent;
* backfills evidence through the consent-aware adapter.

The password for the fixture account comes from ``DNA_FIXTURE_PASSWORD``. If it
is unset, a random unusable password is stored and never printed.

Run inside the development backend:

    docker exec -w /app -e PYTHONPATH=/app ocr-backend \
      python -m app.scripts.seed_dna_fixtures --purge-non-consenting
"""

from __future__ import annotations

import argparse
import os
import secrets
from datetime import datetime, timezone

from sqlalchemy import func

from app.auth import get_password_hash
from app.consent.service import grant
from app.cyber_dna.models import DnaEvidenceRecord
from app.cyber_dna.service import erase_learner
from app.database import SessionLocal
from app.models import LabCompletion, User
from app.services.dna_events import backfill_completions, consent_allows_processing

FIXTURE_USERNAME = "dna_fixture_ready"
SOURCE_USERNAME = "dummyadmin"
BELOW_GATE_USERNAME = "demo_career_ready"
FIXTURE_REASON = "development DNA fixture (synthetic account)"


def ensure_fixture_user(db) -> tuple[User, bool]:
    user = db.query(User).filter(User.username == FIXTURE_USERNAME).first()
    if user is not None:
        return user, False
    password = os.environ.get("DNA_FIXTURE_PASSWORD") or secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    user = User(
        username=FIXTURE_USERNAME,
        email="dna_fixture_ready@example.invalid",
        hashed_password=get_password_hash(password),
        role="student",
        is_active=True,
        is_approved=True,
        is_minor=False,
        age_band="18_plus",
        first_name="Fixture",
        last_name="Ready",
        organization="Development fixture",
        privacy_acknowledged_at=now,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, True


def copy_completions(db, source: User, target: User) -> int:
    existing = (
        db.query(func.count(LabCompletion.id))
        .filter(LabCompletion.user_id == target.id)
        .scalar()
        or 0
    )
    if existing:
        return 0
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    seen: set[int] = set()
    copied = 0
    for row in db.query(LabCompletion).filter(LabCompletion.user_id == source.id).all():
        if row.lab_id in seen:
            continue
        seen.add(row.lab_id)
        db.add(
            LabCompletion(
                user_id=target.id,
                lab_id=row.lab_id,
                attempts=row.attempts or 1,
                hints_used=row.hints_used or 0,
                time_spent_minutes=row.time_spent_minutes,
                flag_submitted=row.flag_submitted or "FIXTURE",
                completed_at=row.completed_at or now,
            )
        )
        copied += 1
    db.commit()
    return copied


def purge_non_consenting(db) -> int:
    learner_ids = [
        row[0]
        for row in db.query(LabCompletion.user_id).distinct().all()
        if row[0] is not None
    ]
    evidence_ids = {
        row[0] for row in db.query(DnaEvidenceRecord.learner_id).distinct()
    }
    deleted = 0
    for learner_id in sorted(evidence_ids | set(learner_ids)):
        if consent_allows_processing(db, learner_id):
            continue
        rows = erase_learner(db, learner_id)
        db.commit()
        deleted += rows
    return deleted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--purge-non-consenting",
        action="store_true",
        help="Delete DNA rows for learners without granted consent",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        source = db.query(User).filter(User.username == SOURCE_USERNAME).first()
        if source is None:
            raise SystemExit(f"source user {SOURCE_USERNAME} not found")

        fixture, created = ensure_fixture_user(db)
        grant(
            db,
            fixture.id,
            "cyber_dna",
            actor="admin",
            reason=FIXTURE_REASON,
        )

        below = db.query(User).filter(User.username == BELOW_GATE_USERNAME).first()
        if below is not None:
            grant(
                db,
                below.id,
                "cyber_dna",
                actor="admin",
                reason=FIXTURE_REASON,
            )

        copied = copy_completions(db, source, fixture)
        purged = purge_non_consenting(db) if args.purge_non_consenting else 0
        stats = backfill_completions(db)

        print(
            f"fixture={'created' if created else 'existing'} "
            f"copied_completions={copied} purged_rows={purged} "
            f"completions={stats['completions']} "
            f"evidence_rows={stats['evidence_rows']} "
            f"blocked={stats['blocked']} learners={stats['learners']}"
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
