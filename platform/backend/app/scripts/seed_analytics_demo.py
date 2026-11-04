"""Seed a realistic multi-course analytics demo.

Run only in a development or test environment:
    python -m app.scripts.seed_analytics_demo

The script is idempotent for its own demo accounts, courses, labs, and survey.
It deliberately leaves shared track records in place.
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone

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
    Survey,
    SurveyAttachment,
    SurveyResponse,
    Track,
    User,
)

DEMO_PASSWORD = "Demo#Pass123"
DEMO_COURSES = ("DEMO-WEB", "DEMO-OSINT", "DEMO-ADV")
DEMO_LAB_PREFIX = "demo-analytics-"
DEMO_SURVEY_TITLE = "Demo course reflection"

DOMAINS = {
    "web": ("Web Security", ["Web exploitation", "Access control", "Secure coding", "API security"]),
    "osint": ("OSINT", ["Search operators", "Domain intelligence", "Image verification", "Public records"]),
    "forensics": ("Digital Forensics", ["Memory analysis", "Disk artefacts", "Network evidence", "Timeline building"]),
    "malware": ("Malware Analysis", ["Static triage", "Behaviour analysis", "Packing", "Indicators"]),
    "ot": ("OT / ICS", ["Modbus", "PLC discovery", "Network segmentation", "HMI review"]),
    "ai": ("AI Security", ["Prompt injection", "Data leakage", "Model abuse", "Guardrails"]),
}

COURSE_SPECS = [
    {
        "code": "DEMO-WEB",
        "name": "Demo Web and Software Security",
        "semester": "Fall",
        "domains": ["web", "web"],
        "students": 9,
        "start_rate": 0.95,
        "complete_rate": 0.9,
        "hint_rate": 0.25,
        "heavy_attempt_rate": 0.15,
        "learning": (4, 5),
        "difficulty": (2, 4),
    },
    {
        "code": "DEMO-OSINT",
        "name": "Demo OSINT and Forensics",
        "semester": "Fall",
        "domains": ["osint", "forensics"],
        "students": 8,
        "start_rate": 0.8,
        "complete_rate": 0.62,
        "hint_rate": 0.5,
        "heavy_attempt_rate": 0.35,
        "learning": (3, 4),
        "difficulty": (3, 4),
    },
    {
        "code": "DEMO-ADV",
        "name": "Demo Malware, OT, and AI",
        "semester": "Winter",
        "domains": ["malware", "ot", "ai"],
        "students": 7,
        "start_rate": 0.65,
        "complete_rate": 0.28,
        "hint_rate": 0.75,
        "heavy_attempt_rate": 0.7,
        "learning": (1, 3),
        "difficulty": (4, 5),
    },
]


def _cleanup(db):
    demo_users = db.query(User).filter(
        (User.username == "demo_instructor")
        | (User.username.like("demo_student_%"))
    ).all()
    user_ids = [user.id for user in demo_users]
    courses = db.query(Course).filter(Course.code.in_(DEMO_COURSES)).all()
    course_ids = [course.id for course in courses]
    labs = db.query(Lab).filter(Lab.slug.like(f"{DEMO_LAB_PREFIX}%")).all()
    lab_ids = [lab.id for lab in labs]

    if user_ids:
        db.query(ExercisePulseSurvey).filter(
            ExercisePulseSurvey.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(SurveyResponse).filter(
            SurveyResponse.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(Achievement).filter(
            Achievement.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(LabCompletion).filter(
            LabCompletion.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(LabSession).filter(
            LabSession.user_id.in_(user_ids)
        ).delete(synchronize_session=False)
        db.query(CourseEnrollment).filter(
            CourseEnrollment.user_id.in_(user_ids)
        ).delete(synchronize_session=False)

    surveys = db.query(Survey).filter(Survey.title == DEMO_SURVEY_TITLE).all()
    for survey in surveys:
        db.query(SurveyResponse).filter(
            SurveyResponse.survey_id == survey.id
        ).delete(synchronize_session=False)
        db.query(SurveyAttachment).filter(
            SurveyAttachment.survey_id == survey.id
        ).delete(synchronize_session=False)
        db.delete(survey)

    if course_ids:
        db.query(CourseLabAssignment).filter(
            CourseLabAssignment.course_id.in_(course_ids)
        ).delete(synchronize_session=False)
        db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id.in_(course_ids)
        ).delete(synchronize_session=False)
        for course in courses:
            db.delete(course)
    if lab_ids:
        db.query(CourseLabAssignment).filter(
            CourseLabAssignment.lab_id.in_(lab_ids)
        ).delete(synchronize_session=False)
        for lab in labs:
            db.delete(lab)
    if demo_users:
        for user in demo_users:
            db.delete(user)
    db.commit()


def _track_for(db, slug):
    track = db.query(Track).filter(Track.slug == slug).first()
    if track:
        return track
    track = Track(
        name=DOMAINS[slug][0],
        slug=slug,
        description="Demo analytics track",
        is_active=True,
    )
    db.add(track)
    db.flush()
    return track


def seed():
    db = SessionLocal()
    try:
        _cleanup(db)
        rng = random.Random(42)
        now = datetime.now(timezone.utc)

        instructor = User(
            username="demo_instructor",
            email="demo_instructor@example.invalid",
            hashed_password=get_password_hash(DEMO_PASSWORD),
            is_active=True,
            is_approved=True,
            role="instructor",
            first_name="Demo",
            last_name="Instructor",
        )
        db.add(instructor)
        db.flush()

        students = []
        for index in range(1, 13):
            student = User(
                username=f"demo_student_{index:02d}",
                email=f"demo_student_{index:02d}@example.invalid",
                hashed_password=get_password_hash(DEMO_PASSWORD),
                is_active=True,
                is_approved=True,
                role="student",
                first_name=f"Demo{index}",
                last_name="Learner",
                survey_opt_in=index <= 9,
            )
            db.add(student)
            students.append(student)
        db.flush()

        level_cache = {}
        lab_cache = {}
        for slug, (_, topics) in DOMAINS.items():
            track = _track_for(db, slug)
            level = Level(
                track_id=track.id,
                level_number=1,
                name="Demo Analytics Level",
                description="Seeded analytics data",
            )
            db.add(level)
            db.flush()
            level_cache[slug] = level
            lab_cache[slug] = []
            for index, topic in enumerate(topics, 1):
                lab = Lab(
                    name=f"{topic} Demo",
                    slug=f"{DEMO_LAB_PREFIX}{slug}-{index}",
                    description=f"Demo exercise for {topic}",
                    compose_file="services: {}\n",
                    is_active=True,
                    visibility="public",
                    level_id=level.id,
                    duration_minutes=45 + index * 5,
                    difficulty="medium",
                )
                db.add(lab)
                db.flush()
                lab_cache[slug].append(lab)

        created_courses = []
        for spec in COURSE_SPECS:
            course = Course(
                name=spec["name"],
                code=spec["code"],
                semester=spec["semester"],
                description="Seeded V2 analytics demo course",
                invite_code=f"{spec['code']}-2026",
                instructor_id=instructor.id,
                start_date=now - timedelta(days=35),
                end_date=now + timedelta(days=35),
                is_active=True,
            )
            db.add(course)
            db.flush()
            created_courses.append(course)
            course_labs = []
            for slug in dict.fromkeys(spec["domains"]):
                course_labs.extend(lab_cache[slug])
            for order, lab in enumerate(course_labs):
                db.add(CourseLabAssignment(
                    course_id=course.id, lab_id=lab.id, sort_order=order,
                ))

            cohort = students[: spec["students"]]
            for student in cohort:
                db.add(CourseEnrollment(
                    course_id=course.id,
                    user_id=student.id,
                    enrolled_at=now - timedelta(days=30),
                ))
                for lab in course_labs:
                    if rng.random() > spec["start_rate"]:
                        continue
                    started = now - timedelta(days=rng.randint(2, 28), hours=rng.randint(0, 10))
                    db.add(LabSession(
                        user_id=student.id,
                        lab_id=lab.id,
                        status="stopped",
                        started_at=started,
                        expires_at=started + timedelta(hours=2),
                        stopped_at=started + timedelta(hours=1),
                    ))
                    db.add(FlagAttempt(
                        user_id=student.id,
                        lab_id=lab.id,
                        flag_submitted="demo",
                        is_correct=False,
                        attempted_at=started + timedelta(minutes=rng.randint(4, 25)),
                    ))
                    if rng.random() > spec["complete_rate"]:
                        continue
                    attempts = rng.randint(1, 6) if rng.random() < spec["heavy_attempt_rate"] else rng.randint(1, 3)
                    hints = rng.randint(1, 3) if rng.random() < spec["hint_rate"] else 0
                    duration = max(5, lab.duration_minutes + rng.randint(-20, 70))
                    completed = started + timedelta(minutes=duration + rng.randint(0, 20))
                    db.add(LabCompletion(
                        user_id=student.id,
                        lab_id=lab.id,
                        flag_submitted="OCR{demo}",
                        completed_at=completed,
                        attempts=attempts,
                        hints_used=hints,
                        time_spent_minutes=duration,
                        started_at=started,
                    ))
                    if student.survey_opt_in:
                        db.add(ExercisePulseSurvey(
                            user_id=student.id,
                            lab_id=lab.id,
                            course_id=course.id,
                            difficulty=rng.randint(*spec["difficulty"]),
                            learning=rng.randint(*spec["learning"]),
                            unclear=(
                                "The first hint could be more specific."
                                if rng.random() < 0.18 else None
                            ),
                            topic_interest=rng.choice(spec["domains"]),
                        ))
                    if rng.random() < 0.3:
                        db.add(Achievement(
                            user_id=student.id,
                            course_id=course.id,
                            lab_id=lab.id,
                            achievement_type="first_blood" if rng.random() < 0.5 else "no_hints",
                        ))

        # A custom survey attached to the demo web course, answered by opted-in learners.
        survey = Survey(
            title=DEMO_SURVEY_TITLE,
            description="Help us improve the next cohort.",
            questions=json.dumps([
                {"prompt": "How useful was the course?", "type": "scale", "options": []},
                {"prompt": "Would you recommend it?", "type": "choice", "options": ["Yes", "No", "Maybe"]},
                {"prompt": "What should change?", "type": "text", "options": []},
            ]),
            created_by=instructor.id,
            is_active=True,
        )
        db.add(survey)
        db.flush()
        db.add(SurveyAttachment(survey_id=survey.id, course_id=created_courses[0].id))
        for student in students[:5]:
            if not student.survey_opt_in:
                continue
            db.add(SurveyResponse(
                survey_id=survey.id,
                user_id=student.id,
                course_id=created_courses[0].id,
                answers=json.dumps({
                    "0": rng.randint(3, 5),
                    "1": rng.choice(["Yes", "Yes", "Maybe"]),
                    "2": rng.choice([
                        "More worked examples.",
                        "A clearer final hint.",
                        "More time on the capstone.",
                    ]),
                }),
            ))

        db.commit()
        print("Demo analytics data seeded.")
        print(f"Instructor: demo_instructor / {DEMO_PASSWORD}")
        print(f"Students:   demo_student_01 .. demo_student_12 / {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
