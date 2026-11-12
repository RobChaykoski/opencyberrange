"""Create or refresh the DevFest 2027 Cyber Discovery event.

The event uses the existing competition engine: participants, labs, sponsors,
leaderboard, and certificates. The only extra marker is
``experience_key='devfest-2027'``, which turns on the Cyber Discovery panel and
the discovery certificate award.

Usage:
    python -m app.scripts.seed_devfest_event --preview
    python -m app.scripts.seed_devfest_event --start 2027-11-06T09:00:00Z --end 2027-11-06T16:00:00Z
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models import Competition, CompetitionLab, CompetitionSponsor, Lab, User

EXPERIENCE_KEY = "devfest-2027"
EVENT_NAME = "GDG Windsor DevFest 2027 Cyber Discovery Experience"
EVENT_DESCRIPTION = (
    "A six-hour Cyber Discovery Experience powered by OpenCyberRange and "
    "SWOCTS. Investigate four disciplines, explore four career pathways, and "
    "receive a Cyber DNA snapshot, a Cyber GPS report, and an exclusive "
    "event certificate."
)
LAB_SLUGS = (
    # Morning investigations
    "network-1-1-packet-capture-analysis",
    "forensics-1-1-windows-memory-volatility",
    "osint-1-3-exif-metadata",
    "osint-1-1-public-footprint",
    "ai-1-1-prompt-injection-basics",
    "ai-1-3-indirect-prompt-injection",
    # Afternoon pathway labs
    "high-school-10-1-rangebox-network-basics",
    "high-school-11-1-rangebox-log-detective",
    "ot-1-1-modbus-register-analysis",
)
SPONSORS = (
    ("GDG Windsor", "Community partner and host.", "gold"),
    ("SWOCTS", "Programme and career-discovery partner.", "gold"),
    ("OpenCyberRange", "Platform and curriculum partner.", "gold"),
)


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the DevFest 2027 event")
    parser.add_argument("--start", default="2027-11-06T09:00:00Z")
    parser.add_argument("--end", default="2027-11-06T16:00:00Z")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="End the event one minute ago so certificates can be tested on dev.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    start = _parse(args.start)
    end = _parse(args.end)
    if args.preview:
        end = datetime.now(timezone.utc) - timedelta(minutes=1)
        start = min(start, end - timedelta(hours=6))
    if end <= start:
        print("End time must be after start time.")
        return 1

    db = SessionLocal()
    try:
        admin = (
            db.query(User).filter(User.role == "admin", User.is_active == True).first()
        )
        labs = (
            db.query(Lab)
            .filter(Lab.slug.in_(LAB_SLUGS), Lab.is_active == True)
            .all()
        )
        lab_by_slug = {lab.slug: lab for lab in labs}
        missing = [slug for slug in LAB_SLUGS if slug not in lab_by_slug]
        if missing:
            print("Warning: missing active labs:", ", ".join(missing))
        if not labs:
            print("No event labs found. Aborting.")
            return 1

        competition = (
            db.query(Competition)
            .filter(Competition.experience_key == EXPERIENCE_KEY)
            .first()
        )
        if competition is None:
            competition = (
                db.query(Competition)
                .filter(Competition.name == EVENT_NAME)
                .first()
            )

        action = "updated" if competition else "created"
        if args.dry_run:
            print(
                f"Would have {action} event '{EVENT_NAME}' with "
                f"{len(labs)} labs and {len(SPONSORS)} sponsors."
            )
            return 0

        if competition is None:
            competition = Competition(
                name=EVENT_NAME,
                description=EVENT_DESCRIPTION,
                start_at=start,
                end_at=end,
                created_by=admin.id if admin else None,
                is_active=True,
                experience_key=EXPERIENCE_KEY,
            )
            db.add(competition)
            db.flush()
        else:
            competition.name = EVENT_NAME
            competition.description = EVENT_DESCRIPTION
            competition.start_at = start
            competition.end_at = end
            competition.is_active = True
            competition.experience_key = EXPERIENCE_KEY

        # Replace the lab list and sponsor list so reruns are idempotent.
        db.query(CompetitionLab).filter(
            CompetitionLab.competition_id == competition.id
        ).delete(synchronize_session=False)
        for order, slug in enumerate(LAB_SLUGS):
            lab = lab_by_slug.get(slug)
            if lab is None:
                continue
            db.add(
                CompetitionLab(
                    competition_id=competition.id,
                    lab_id=lab.id,
                    sort_order=order,
                )
            )

        db.query(CompetitionSponsor).filter(
            CompetitionSponsor.competition_id == competition.id
        ).delete(synchronize_session=False)
        for order, (name, description, tier) in enumerate(SPONSORS):
            db.add(
                CompetitionSponsor(
                    competition_id=competition.id,
                    name=name,
                    description=description,
                    tier=tier,
                    sort_order=order,
                )
            )

        db.commit()
        db.refresh(competition)
        print(
            f"Event {action}: id={competition.id} '{competition.name}' "
            f"({start.date()} to {end.date()}) with {len(labs)} labs."
        )
        print(
            "Open /events/{id} to review it. The discovery panel appears when "
            "experience_key is devfest-2027.".format(id=competition.id)
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
