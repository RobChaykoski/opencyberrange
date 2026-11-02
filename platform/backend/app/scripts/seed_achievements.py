#!/usr/bin/env python3
"""Seed the default learning-path achievements.

Custom achievements are global definitions: once seeded, every course can
award them. Awards are still course-scoped, so a student earns the badge once
per course in which they reach the threshold.

The script is idempotent. It creates a definition only when no achievement
with the same name already exists, which means an operator can edit or
deactivate a seeded badge without the next deployment overwriting it.

Usage (inside Docker):
  docker compose exec backend python /app/app/scripts/seed_achievements.py
"""

import sys

sys.path.insert(0, "/app")

from app.database import SessionLocal
from app.models import CustomAchievement


# A learning ladder, not a leaderboard. The names are playful; the thresholds
# reward curiosity, practice, and understanding rather than speed or "elite"
# knowledge.
DEFAULT_ACHIEVEMENTS = [
    {
        "name": "Hello, World",
        "description": "Complete your first exercise. Every journey starts with one command.",
        "icon": "👋",
        "trigger": "labs_completed",
        "threshold": 1,
    },
    {
        "name": "Curious by Default",
        "description": "Complete 3 exercises. Curiosity is the core hacker skill.",
        "icon": "🔎",
        "trigger": "labs_completed",
        "threshold": 3,
    },
    {
        "name": "Terminal Tourist",
        "description": "Complete 5 exercises. You are finding your way around the command line.",
        "icon": "🧭",
        "trigger": "labs_completed",
        "threshold": 5,
    },
    {
        "name": "Packet Whisperer",
        "description": "Complete 8 exercises. You are starting to hear what the network is saying.",
        "icon": "📡",
        "trigger": "labs_completed",
        "threshold": 8,
    },
    {
        "name": "Shell We Dance?",
        "description": "Complete 10 exercises. The shell is becoming a familiar dance partner.",
        "icon": "🐚",
        "trigger": "labs_completed",
        "threshold": 10,
    },
    {
        "name": "Root of the Problem",
        "description": "Complete 15 exercises. You are learning to find causes, not just symptoms.",
        "icon": "🌱",
        "trigger": "labs_completed",
        "threshold": 15,
    },
    {
        "name": "Lab Rat",
        "description": "Complete 20 exercises. Comfortable in the lab, curious about everything.",
        "icon": "🐭",
        "trigger": "labs_completed",
        "threshold": 20,
    },
    {
        "name": "The Long Game",
        "description": "Complete 25 exercises. Skill is built one deliberate repetition at a time.",
        "icon": "🏔️",
        "trigger": "labs_completed",
        "threshold": 25,
    },
    {
        "name": "Lone Wolf",
        "description": "Complete 3 exercises without using hints. Your notes are enough.",
        "icon": "🐺",
        "trigger": "no_hint_labs",
        "threshold": 3,
    },
    {
        "name": "RTFM",
        "description": "Complete 5 exercises without using hints. The manual is a superpower.",
        "icon": "📚",
        "trigger": "no_hint_labs",
        "threshold": 5,
    },
    {
        "name": "Hacker Ethos",
        "description": "Complete 8 exercises without using hints. Learn it, understand it, then make it yours.",
        "icon": "🧠",
        "trigger": "no_hint_labs",
        "threshold": 8,
    },
    {
        "name": "Always Be Learning",
        "description": "Complete 10 exercises without using hints. The best tool is a curious mind.",
        "icon": "🧑‍🎓",
        "trigger": "no_hint_labs",
        "threshold": 10,
    },
    {
        "name": "First Try, No Cry",
        "description": "Complete 3 exercises on the first flag attempt. Read twice, submit once.",
        "icon": "🎯",
        "trigger": "perfect_labs",
        "threshold": 3,
    },
    {
        "name": "One-Shot Wonder",
        "description": "Complete 5 exercises on the first flag attempt. Careful work looks like luck.",
        "icon": "⚡",
        "trigger": "perfect_labs",
        "threshold": 5,
    },
    {
        "name": "No Guesswork",
        "description": "Complete 8 exercises on the first flag attempt. Evidence beats guessing.",
        "icon": "🔬",
        "trigger": "perfect_labs",
        "threshold": 8,
    },
    {
        "name": "Signal in the Noise",
        "description": "Complete your first OSINT exercise. The public surface is bigger than it looks.",
        "icon": "🔎",
        "trigger": "osint_labs_completed",
        "threshold": 1,
    },
    {
        "name": "Digital Footprint",
        "description": "Complete 2 OSINT exercises. Follow the trail, not the noise.",
        "icon": "👣",
        "trigger": "osint_labs_completed",
        "threshold": 2,
    },
    {
        "name": "Metadata Miner",
        "description": "Complete 3 OSINT exercises. You are reading between the pixels.",
        "icon": "🔬",
        "trigger": "osint_labs_completed",
        "threshold": 3,
    },
    {
        "name": "Open Source Operative",
        "description": "Complete every OSINT exercise assigned to the course. The whole picture, from public sources.",
        "icon": "🌐",
        "trigger": "osint_track_completed",
        "threshold": 1,
    },
    {
        "name": "Clean Footprint",
        "description": "Complete 3 OSINT exercises without using hints. Your notes were enough.",
        "icon": "🧭",
        "trigger": "osint_no_hint_labs",
        "threshold": 3,
    },
    {
        "name": "First-Pass Analyst",
        "description": "Complete 3 OSINT exercises on the first flag attempt. Evidence beats guessing.",
        "icon": "🛰️",
        "trigger": "osint_perfect_labs",
        "threshold": 3,
    },
    {
        "name": "DevFest Ghost",
        "description": "Complete all three DevFest starter challenges without hints. You were never really here.",
        "icon": "\U0001F47B",
        "trigger": "devfest_no_hint_labs",
        "threshold": 3,
    },
    {
        "name": "Range Cartographer",
        "description": "Complete at least one exercise in every active track. You have mapped the whole range.",
        "icon": "\U0001F5FA\uFE0F",
        "trigger": "all_tracks_completed",
        "threshold": 1,
    },
    {
        "name": "Phoenix",
        "description": "Complete an exercise after five or more flag attempts. Persistence is a security skill.",
        "icon": "\U0001F525",
        "trigger": "comeback_labs",
        "threshold": 1,
    },
    {
        "name": "Night Shift",
        "description": "Complete an exercise between 00:00 and 05:00. The quiet hours are productive.",
        "icon": "\U0001F319",
        "trigger": "night_labs",
        "threshold": 1,
    },
]


def seed_achievements():
    """Create any missing default achievements.

    Existing rows are left untouched so operator edits survive a re-seed.
    """
    db = SessionLocal()
    try:
        created = []
        skipped = []

        for definition in DEFAULT_ACHIEVEMENTS:
            existing = db.query(CustomAchievement).filter(
                CustomAchievement.name == definition["name"]
            ).first()
            if existing:
                skipped.append(definition["name"])
                continue

            db.add(CustomAchievement(**definition))
            created.append(definition["name"])

        db.commit()

        print(f"Default achievements: {len(created)} created, {len(skipped)} already present")
        for name in created:
            print(f"  + {name}")
        if skipped:
            print("  (existing definitions were left unchanged)")
    except Exception as exc:
        db.rollback()
        print(f"Error seeding achievements: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_achievements()
