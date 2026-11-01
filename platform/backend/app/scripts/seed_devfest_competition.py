#!/usr/bin/env python3
"""Create the Windsor-Essex DevFest 2026 special competition.

Idempotent: if a competition with the same name already exists, nothing is
created. Run inside the backend container after the high-school lab has been
discovered:

    docker compose exec backend python /app/app/scripts/seed_devfest_competition.py

Override the window with DEVFEST_START / DEVFEST_END if the event schedule
changes. Dates use ISO 8601 with an explicit offset.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, "/app")

from app.database import SessionLocal
from app.models import Competition, CompetitionLab, Lab, User

LAB_SLUGS = (
    "high-school-12-1-devfest-community-portal",
    "software-security-1-1-hidden-export-route",
    "software-security-2-1-diagnostics-command-injection",
)
COMPETITION_NAME = "Windsor-Essex DevFest 2026"
DEFAULT_START = "2026-11-21T09:00:00-05:00"
DEFAULT_END = "2026-11-21T17:00:00-05:00"


def seed_devfest_competition():
    db = SessionLocal()
    try:
        labs = []
        for slug in LAB_SLUGS:
            lab = db.query(Lab).filter(Lab.slug == slug).first()
            if lab:
                labs.append(lab)
            else:
                print(f"Lab not found, skipping: {slug}. Run discover_labs.py first.")

        if not labs:
            print("No DevFest labs found; run discover_labs.py first.")
            return

        existing = db.query(Competition).filter(
            Competition.name == COMPETITION_NAME
        ).first()
        if existing:
            existing_ids = {
                row.lab_id for row in db.query(CompetitionLab).filter(
                    CompetitionLab.competition_id == existing.id
                ).all()
            }
            added = 0
            for order, lab in enumerate(labs):
                if lab.id not in existing_ids:
                    db.add(CompetitionLab(
                        competition_id=existing.id,
                        lab_id=lab.id,
                        sort_order=order,
                    ))
                    added += 1
            if added:
                db.commit()
            print(
                f"Competition already exists: {COMPETITION_NAME} "
                f"(id={existing.id}); added {added} lab(s)"
            )
            return

        owner = db.query(User).filter(
            User.role.in_(("admin", "instructor")),
            User.is_active == True,
        ).order_by(User.id).first()
        if not owner:
            print("No active admin or instructor found to own the competition.")
            return

        start_at = datetime.fromisoformat(
            os.environ.get("DEVFEST_START", DEFAULT_START)
        )
        end_at = datetime.fromisoformat(
            os.environ.get("DEVFEST_END", DEFAULT_END)
        )

        competition = Competition(
            name=COMPETITION_NAME,
            description=(
                "Three browser-first, opt-in starter challenges for the "
                "Windsor-Essex DevFest community: a metadata OSINT exercise, a "
                "source-review exercise, and a command-injection exercise. No "
                "terminal or VPN is required."
            ),
            start_at=start_at,
            end_at=end_at,
            is_active=True,
            created_by=owner.id,
        )
        db.add(competition)
        db.flush()
        for order, lab in enumerate(labs):
            db.add(CompetitionLab(
                competition_id=competition.id,
                lab_id=lab.id,
                sort_order=order,
            ))
        db.commit()

        print(f"Created competition: {COMPETITION_NAME} (id={competition.id})")
        print(f"Owner: {owner.username}")
        print("Labs:")
        for lab in labs:
            print(f"  - {lab.name} ({lab.slug})")
        print(f"New-user sign-up: /register?competition={competition.id}")
    except Exception as exc:
        db.rollback()
        print(f"Error creating DevFest competition: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_devfest_competition()
