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

LAB_SLUG = "high-school-12-1-devfest-community-portal"
COMPETITION_NAME = "Windsor-Essex DevFest 2026"
DEFAULT_START = "2026-11-21T09:00:00-05:00"
DEFAULT_END = "2026-11-21T17:00:00-05:00"


def seed_devfest_competition():
    db = SessionLocal()
    try:
        existing = db.query(Competition).filter(
            Competition.name == COMPETITION_NAME
        ).first()
        if existing:
            print(f"Competition already exists: {COMPETITION_NAME} (id={existing.id})")
            return

        lab = db.query(Lab).filter(Lab.slug == LAB_SLUG).first()
        if not lab:
            print(f"Lab not found: {LAB_SLUG}. Run discover_labs.py first.")
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
                "A browser-first, opt-in OSINT challenge for the Windsor-Essex "
                "DevFest community. Explore a fictional conference portal, open "
                "a speaker's slide export, and recover the flag from its metadata."
            ),
            start_at=start_at,
            end_at=end_at,
            is_active=True,
            created_by=owner.id,
        )
        db.add(competition)
        db.flush()
        db.add(CompetitionLab(
            competition_id=competition.id,
            lab_id=lab.id,
            sort_order=0,
        ))
        db.commit()

        print(f"Created competition: {COMPETITION_NAME} (id={competition.id})")
        print(f"Owner: {owner.username}")
        print(f"Lab: {lab.name}")
        print(f"New-user sign-up: /register?competition={competition.id}")
    except Exception as exc:
        db.rollback()
        print(f"Error creating DevFest competition: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_devfest_competition()
