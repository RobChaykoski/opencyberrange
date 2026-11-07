"""Seed three development profiles for career-discovery demonstrations.

Development/test only. The script creates:

* a learner who is fairly well versed across the range;
* a learner who is just starting;
* a learner who is changing career direction.

It then exports one career dossier per learner (JSON, Markdown, and printable
HTML). Run inside the backend container:

    python -m app.scripts.seed_career_profiles --output-dir /app/data/career_profiles

The script is idempotent for its own demo users, course, and synthetic labs. It
does not change real learner records.
"""
from __future__ import annotations

import argparse
import os
import secrets
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import joinedload

from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import (
    Achievement,
    Course,
    CourseEnrollment,
    CourseLabAssignment,
    ExercisePulseSurvey,
    FlagAttempt,
    Lab,
    LabCompletion,
    LabSession,
    Level,
    Track,
    User,
)
from app.scripts.export_career_profiles import DEMO_USERNAMES, export_career_profiles

DEMO_PASSWORD = os.environ.get("CAREER_DEMO_PASSWORD") or secrets.token_urlsafe(12)
DEMO_COURSE_CODE = "DEMO-CAREER"
DEMO_TRACK_SLUG = "career-demo"
DEMO_LAB_PREFIX = "career-demo-"

PROFILE_SPECS = (
    {
        "username": "demo_career_ready",
        "first_name": "Avery",
        "last_name": "Ready",
        "organization": "Range Academy",
        "headline": "Fairly well versed across offensive, defensive, and investigative work.",
        "lab_plan": [
            ("web", 2),
            ("exploitation", 2),
            ("privilege-escalation", 1),
            ("post-exploitation", 1),
            ("credential-attacks", 1),
            ("network", 1),
            ("network-analysis", 1),
            ("forensics", 1),
            ("osint", 1),
            ("enumeration", 1),
        ],
        "hints": 0,
        "attempts": 1,
        "minutes": (30, 55),
        "achievements": (
            "first_blood",
            "no_hints",
            "perfectionist",
            "learning_hours_15",
        ),
        "survey_learning": (4, 5),
        "survey_difficulty": (2, 3),
        "topics": ("web", "network", "forensics"),
    },
    {
        "username": "demo_career_starting",
        "first_name": "Sam",
        "last_name": "Starter",
        "organization": "Community College",
        "headline": "Just starting: building confidence with a few beginner exercises.",
        "lab_plan": [
            ("general", 1),
            ("network", 1),
            ("osint", 1),
        ],
        "hints": 1,
        "attempts": 2,
        "minutes": (30, 50),
        "achievements": ("first_blood",),
        "survey_learning": (3, 4),
        "survey_difficulty": (2, 4),
        "topics": ("career", "network"),
        "unfinished": 1,
    },
    {
        "username": "demo_career_changer",
        "first_name": "Jordan",
        "last_name": "Changer",
        "organization": "Career changer - healthcare operations",
        "headline": "Changing direction: building evidence in investigation, forensics, and malware-adjacent work.",
        "lab_plan": [
            ("osint", 2),
            ("forensics", 2),
            ("network-analysis", 2),
            ("web", 1),
        ],
        "hints": 1,
        "attempts": 2,
        "minutes": (35, 65),
        "achievements": ("first_blood", "no_hints", "learning_hours_5"),
        "survey_learning": (4, 5),
        "survey_difficulty": (3, 4),
        "topics": ("forensics", "malware", "osint"),
        "unfinished": 1,
    },
)


def _cleanup(db):
    users = db.query(User).filter(User.username.in_(DEMO_USERNAMES)).all()
    user_ids = [user.id for user in users]
    course = db.query(Course).filter(Course.code == DEMO_COURSE_CODE).first()
    course_id = course.id if course else None

    if user_ids:
        db.query(ExercisePulseSurvey).filter(
            ExercisePulseSurvey.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(Achievement).filter(
            Achievement.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(LabCompletion).filter(
            LabCompletion.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(FlagAttempt).filter(
            FlagAttempt.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(LabSession).filter(
            LabSession.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(CourseEnrollment).filter(
            CourseEnrollment.user_id.in_(user_ids)
        ).delete(synchronize_session=False)

    if course_id:
        db.query(CourseLabAssignment).filter(
            CourseLabAssignment.course_id == course_id
        ).delete(synchronize_session=False)
        db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course_id
        ).delete(synchronize_session=False)
        db.delete(course)

    labs = db.query(Lab).filter(Lab.slug.like(f"{DEMO_LAB_PREFIX}%")).all()
    if labs:
        lab_ids = [lab.id for lab in labs]
        db.query(CourseLabAssignment).filter(
            CourseLabAssignment.lab_id.in_(lab_ids)
        ).delete(synchronize_session=False)
        for lab in labs:
            db.delete(lab)
        db.flush()

    levels = db.query(Level).filter(Level.description == "Career demo data").all()
    for level in levels:
        if db.query(Lab).filter(Lab.level_id == level.id).count() == 0:
            db.delete(level)
    tracks = db.query(Track).filter(Track.slug == DEMO_TRACK_SLUG).all()
    for track in tracks:
        if db.query(Level).filter(Level.track_id == track.id).count() == 0:
            db.delete(track)
    for user in users:
        db.delete(user)
    db.commit()


def _instructor(db) -> User:
    user = (
        db.query(User)
        .filter(User.role.in_(("admin", "instructor")), User.is_active == True)  # noqa: E712
        .order_by(User.id.asc())
        .first()
    )
    if user:
        return user
    user = User(
        username="career_coach",
        email="career_coach@example.invalid",
        hashed_password=get_password_hash(DEMO_PASSWORD),
        is_active=True,
        is_approved=True,
        role="instructor",
        first_name="Career",
        last_name="Coach",
        organization="SWOCTS Cyber Range",
    )
    db.add(user)
    db.flush()
    return user


def _demo_level(db) -> Level:
    track = db.query(Track).filter(Track.slug == DEMO_TRACK_SLUG).first()
    if track is None:
        track = Track(
            name="Career Discovery",
            slug=DEMO_TRACK_SLUG,
            description="Synthetic labs for the career demo profiles",
            is_active=True,
            sequential=False,
        )
        db.add(track)
        db.flush()
    level = (
        db.query(Level)
        .filter(
            Level.track_id == track.id,
            Level.description == "Career demo data",
        )
        .first()
    )
    if level is None:
        level = Level(
            track_id=track.id,
            level_number=1,
            name="Career Discovery Lab",
            description="Career demo data",
        )
        db.add(level)
        db.flush()
    return level


def _synthetic_lab(db, category: str, index: int, difficulty: str) -> Lab:
    level = _demo_level(db)
    lab = Lab(
        name=f"Career demo: {category.replace('-', ' ').title()} {index}",
        slug=f"{DEMO_LAB_PREFIX}{category}-{index}",
        description=f"Synthetic {category} exercise for the career-discovery demo",
        compose_file="services: {}\n",
        category=category,
        difficulty=difficulty,
        duration_minutes=45,
        is_active=True,
        visibility="public",
        level_id=level.id,
    )
    db.add(lab)
    db.flush()
    return lab


def _pick_labs(db) -> dict[str, list[Lab]]:
    rows = (
        db.query(Lab)
        .options(joinedload(Lab.level).joinedload(Level.track))
        .filter(Lab.is_active == True)  # noqa: E712
        .all()
    )
    by_category = defaultdict(list)
    for lab in rows:
        by_category[(lab.category or "general").strip().lower()].append(lab)

    pool = defaultdict(list)
    synthetic_index = defaultdict(int)
    for spec in PROFILE_SPECS:
        for category, count in spec["lab_plan"]:
            available = by_category.get(category, [])
            for lab in available:
                if lab not in pool[category] and len(pool[category]) < count:
                    pool[category].append(lab)
            while len(pool[category]) < count:
                synthetic_index[category] += 1
                difficulty = (
                    "advanced"
                    if synthetic_index[category] >= 3
                    else "intermediate"
                )
                pool[category].append(
                    _synthetic_lab(
                        db,
                        category,
                        synthetic_index[category],
                        difficulty,
                    )
                )
    return pool


def _profile_labs(pool: dict[str, list[Lab]], spec: dict) -> list[Lab]:
    labs = []
    for category, count in spec["lab_plan"]:
        labs.extend(pool[category][:count])
    return list(dict.fromkeys(labs))


def _activity(db, user: User, course: Course, spec: dict, labs: list[Lab]):
    now = datetime.now(timezone.utc)
    learned_min, learned_max = spec["survey_learning"]
    difficulty_min, difficulty_max = spec["survey_difficulty"]

    for index, lab in enumerate(labs):
        completed_at = now - timedelta(
            days=55 - index * 3,
            hours=(index * 5) % 8,
        )
        minutes = spec["minutes"][0] + (index * 3) % (
            spec["minutes"][1] - spec["minutes"][0] + 1
        )
        started_at = completed_at - timedelta(minutes=minutes + 5)
        attempts = spec["attempts"] + (1 if index % 5 == 0 else 0)
        hints = spec["hints"] + (1 if index % 4 == 0 else 0)

        db.add(LabSession(
            user_id=user.id,
            lab_id=lab.id,
            status="stopped",
            started_at=started_at,
            expires_at=started_at + timedelta(hours=2),
            stopped_at=completed_at,
        ))
        db.add(FlagAttempt(
            user_id=user.id,
            lab_id=lab.id,
            flag_submitted="career-demo",
            is_correct=attempts == 1,
            attempted_at=started_at + timedelta(minutes=10),
        ))
        db.add(LabCompletion(
            user_id=user.id,
            lab_id=lab.id,
            flag_submitted="OCR{career_demo}",
            completed_at=completed_at,
            attempts=attempts,
            hints_used=hints,
            time_spent_minutes=minutes,
            started_at=started_at,
        ))

        if index % 2 == 0:
            db.add(ExercisePulseSurvey(
                user_id=user.id,
                lab_id=lab.id,
                course_id=course.id,
                difficulty=difficulty_min + (index % (difficulty_max - difficulty_min + 1)),
                learning=learned_min + (index % (learned_max - learned_min + 1)),
                unclear=(
                    "The first hint could name the tool to inspect."
                    if index % 5 == 0 else None
                ),
                topic_interest=spec["topics"][index % len(spec["topics"])],
            ))

    for index in range(spec.get("unfinished", 0)):
        lab = labs[index % len(labs)]
        started_at = now - timedelta(days=2 + index)
        db.add(LabSession(
            user_id=user.id,
            lab_id=lab.id,
            status="stopped",
            started_at=started_at,
            expires_at=started_at + timedelta(hours=2),
            stopped_at=started_at + timedelta(minutes=35),
        ))

    for achievement_type in spec["achievements"]:
        db.add(Achievement(
            user_id=user.id,
            course_id=course.id,
            achievement_type=achievement_type,
            awarded_at=now - timedelta(days=10),
        ))


def seed(output_dir: str):
    db = SessionLocal()
    try:
        _cleanup(db)
        now = datetime.now(timezone.utc)
        instructor = _instructor(db)
        pool = _pick_labs(db)

        course = Course(
            name="Career Discovery Lab",
            code=DEMO_COURSE_CODE,
            semester="Self-paced",
            description=(
                "Development-only course for career-discovery profiles. "
                "Use it to show Cyber DNA, learning evidence, and career conversations."
            ),
            invite_code="CAREER-DEMO",
            instructor_id=instructor.id,
            start_date=now - timedelta(days=70),
            end_date=now + timedelta(days=90),
            is_active=True,
        )
        db.add(course)
        db.flush()

        all_labs = []
        for spec in PROFILE_SPECS:
            labs = _profile_labs(pool, spec)
            all_labs.extend(labs)
        for order, lab in enumerate(dict.fromkeys(all_labs)):
            db.add(CourseLabAssignment(
                course_id=course.id,
                lab_id=lab.id,
                sort_order=order,
            ))

        created = []
        for spec in PROFILE_SPECS:
            user = User(
                username=spec["username"],
                email=f"{spec['username']}@example.invalid",
                hashed_password=get_password_hash(DEMO_PASSWORD),
                is_active=True,
                is_approved=True,
                role="student",
                first_name=spec["first_name"],
                last_name=spec["last_name"],
                organization=spec["organization"],
                survey_opt_in=True,
            )
            db.add(user)
            db.flush()
            db.add(CourseEnrollment(
                course_id=course.id,
                user_id=user.id,
                enrolled_at=now - timedelta(days=65),
            ))
            _activity(db, user, course, spec, _profile_labs(pool, spec))
            created.append(user)

        db.commit()
        print("Career demo profiles seeded.")
        credential_path = Path(output_dir).parent / "career_demo_credentials.txt"
        credential_path.parent.mkdir(parents=True, exist_ok=True)
        credential_path.write_text(
            "Development-only career demo credentials\n"
            + "\n".join(f"{user.username} / {DEMO_PASSWORD}" for user in created)
            + "\n",
            encoding="utf-8",
        )
        os.chmod(credential_path, 0o600)
        print(f"Demo credentials written to {credential_path} (mode 0600).")

        written = export_career_profiles(db, output_dir)
        print("Career dossiers exported:")
        for path in written:
            print(f"  {path}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default=os.environ.get("CAREER_EXPORT_DIR", "data/career_profiles"),
        help="Directory for JSON, Markdown, and HTML dossiers.",
    )
    args = parser.parse_args()
    seed(args.output_dir)


if __name__ == "__main__":
    main()
