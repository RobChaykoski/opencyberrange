#!/usr/bin/env python3
"""Seed feature-test data in a development database only.

Creates multiple instructors, courses, cohorts above and below the suppression
threshold, enrolments, assignments, sessions, completions, flag attempts,
pulse surveys, reactions, course feedback, exercise quizzes, a survey,
consent events, achievements, resets, and a competition.

Safety:
    * Requires ``--dev`` and ``OCR_DEMO_SEED_ALLOWED=1``.
    * Refuses when OCR_ENV/DEPLOYMENT_MODE says production.
    * Every record uses a ``demotest_``/``DEMOTEST-`` prefix.
    * ``--cleanup`` removes only those records.
    * ``DEMO_FEATURE_PASSWORD`` must be supplied; it is never printed or
      written to disk.

Run inside the development backend container:

    docker exec -e OCR_DEMO_SEED_ALLOWED=1 -e PYTHONPATH=/app ocr-backend \
      python -m app.scripts.seed_feature_test_data --dev --yes

Cleanup:

    docker exec -e OCR_DEMO_SEED_ALLOWED=1 -e PYTHONPATH=/app ocr-backend \
      python -m app.scripts.seed_feature_test_data --dev --cleanup --yes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
from datetime import datetime, timedelta, timezone

from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import (
    Achievement,
    ActivityEvent,
    Assignment,
    AssignmentLab,
    Competition,
    CompetitionLab,
    CompetitionParticipant,
    Course,
    CourseCompletionReset,
    CourseEnrollment,
    CourseFeedback,
    CourseLabAssignment,
    ExercisePulseSurvey,
    ExerciseQuizAttempt,
    ExerciseQuizFeedback,
    ExerciseReaction,
    FlagAttempt,
    Lab,
    LabCompletion,
    LabSession,
    Level,
    Survey,
    SurveyAttachment,
    SurveyConsentEvent,
    SurveyResponse,
    Track,
    User,
)

PREFIX = "demotest_"
COURSE_CODE_PREFIX = "DEMOTEST-"
TRACK_SLUG_PREFIX = "demotest-"
LAB_SLUG_PREFIX = "demotest-"
SURVEY_TITLE = "DemoTest course reflection"
COMPETITION_NAME = "DemoTest Practice Sprint"
PASSWORD = os.environ.get("DEMO_FEATURE_PASSWORD", "")
RNG = random.Random(252)

NOW = datetime.now(timezone.utc)

COURSES = (
    {
        "suffix": "A",
        "name": "DemoTest Large Cohort",
        "students": 25,
        "completion": 0.92,
        "hint": 0.20,
        "attempts": (1, 2),
        "learning": (4, 5),
        "difficulty": (2, 4),
        "reset": 0,
    },
    {
        "suffix": "B",
        "name": "DemoTest Threshold Cohort",
        "students": 5,
        "completion": 0.70,
        "hint": 0.50,
        "attempts": (1, 3),
        "learning": (3, 4),
        "difficulty": (3, 4),
        "reset": 1,
    },
    {
        "suffix": "C",
        "name": "DemoTest Small Cohort",
        "students": 3,
        "completion": 0.67,
        "hint": 0.80,
        "attempts": (2, 4),
        "learning": (2, 3),
        "difficulty": (4, 5),
        "reset": 0,
    },
    {
        "suffix": "D",
        "name": "DemoTest No Evidence",
        "students": 0,
        "completion": 0.0,
        "hint": 0.0,
        "attempts": (1, 1),
        "learning": (1, 1),
        "difficulty": (1, 1),
        "reset": 0,
    },
    {
        "suffix": "E",
        "name": "DemoTest Struggling Cohort",
        "students": 12,
        "completion": 0.25,
        "hint": 0.80,
        "attempts": (3, 6),
        "learning": (1, 3),
        "difficulty": (4, 5),
        "reset": 3,
    },
    {
        "suffix": "F",
        "name": "DemoTest Strong Cohort",
        "students": 8,
        "completion": 0.96,
        "hint": 0.10,
        "attempts": (1, 1),
        "learning": (4, 5),
        "difficulty": (2, 3),
        "reset": 0,
    },
)

INSTRUCTORS = (
    {"slug": "instructor_01", "first": "Dana", "last": "Mercer", "org": "DemoTest College"},
    {"slug": "instructor_02", "first": "Ravi", "last": "Shah", "org": "DemoTest Polytechnic"},
    {"slug": "instructor_03", "first": "Mina", "last": "Okafor", "org": "DemoTest University"},
)

SURVEY_QUESTIONS = [
    {"key": "q1", "prompt": "How clear were the lab instructions?", "type": "rating"},
    {"key": "q2", "prompt": "How useful was the exercise for your learning?", "type": "rating"},
    {"key": "q3", "prompt": "What should the instructor change next time?", "type": "text"},
]


def _refuse_production() -> None:
    env = (os.environ.get("OCR_ENV") or os.environ.get("APP_ENV") or "").lower()
    mode = (os.environ.get("DEPLOYMENT_MODE") or "").lower()
    db_url = (os.environ.get("DATABASE_URL") or "").lower()
    if any(token in env for token in ("prod", "production")) or mode in ("production", "prod"):
        raise SystemExit("Refusing to seed: this environment is marked production.")
    if "prod" in db_url or "production" in db_url:
        raise SystemExit("Refusing to seed: DATABASE_URL looks like production.")


def _cleanup(db) -> None:
    users = db.query(User).filter(User.username.like(f"{PREFIX}%")).all()
    user_ids = [user.id for user in users]
    courses = db.query(Course).filter(Course.code.like(f"{COURSE_CODE_PREFIX}%")).all()
    course_ids = [course.id for course in courses]
    labs = db.query(Lab).filter(Lab.slug.like(f"{LAB_SLUG_PREFIX}%")).all()
    lab_ids = [lab.id for lab in labs]

    surveys = db.query(Survey).filter(Survey.title == SURVEY_TITLE).all()
    survey_ids = [survey.id for survey in surveys]
    competitions = db.query(Competition).filter(Competition.name == COMPETITION_NAME).all()
    competition_ids = [competition.id for competition in competitions]
    assignments = db.query(Assignment).filter(Assignment.course_id.in_(course_ids)).all() if course_ids else []
    assignment_ids = [assignment.id for assignment in assignments]

    if survey_ids:
        db.query(SurveyResponse).filter(SurveyResponse.survey_id.in_(survey_ids)).delete(synchronize_session=False)
        db.query(SurveyAttachment).filter(SurveyAttachment.survey_id.in_(survey_ids)).delete(synchronize_session=False)
        db.query(Survey).filter(Survey.id.in_(survey_ids)).delete(synchronize_session=False)
    if competition_ids:
        db.query(CompetitionParticipant).filter(
            CompetitionParticipant.competition_id.in_(competition_ids)
        ).delete(synchronize_session=False)
        db.query(CompetitionLab).filter(
            CompetitionLab.competition_id.in_(competition_ids)
        ).delete(synchronize_session=False)
        db.query(Competition).filter(Competition.id.in_(competition_ids)).delete(synchronize_session=False)
    if assignment_ids:
        db.query(AssignmentLab).filter(AssignmentLab.assignment_id.in_(assignment_ids)).delete(synchronize_session=False)
        db.query(Assignment).filter(Assignment.id.in_(assignment_ids)).delete(synchronize_session=False)
    if user_ids:
        db.query(SurveyConsentEvent).filter(SurveyConsentEvent.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(CourseFeedback).filter(
            (CourseFeedback.author_id.in_(user_ids)) | (CourseFeedback.subject_user_id.in_(user_ids))
        ).delete(synchronize_session=False)
        db.query(ExerciseQuizFeedback).filter(ExerciseQuizFeedback.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(ExerciseQuizAttempt).filter(ExerciseQuizAttempt.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(ExercisePulseSurvey).filter(ExercisePulseSurvey.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(ExerciseReaction).filter(ExerciseReaction.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(CourseCompletionReset).filter(
            (CourseCompletionReset.user_id.in_(user_ids)) | (CourseCompletionReset.reset_by.in_(user_ids))
        ).delete(synchronize_session=False)
        db.query(Achievement).filter(Achievement.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(LabCompletion).filter(LabCompletion.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(FlagAttempt).filter(FlagAttempt.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(LabSession).filter(LabSession.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(ActivityEvent).filter(ActivityEvent.actor_id.in_(user_ids)).delete(synchronize_session=False)
        db.query(CourseEnrollment).filter(CourseEnrollment.user_id.in_(user_ids)).delete(synchronize_session=False)
    if course_ids:
        db.query(CourseLabAssignment).filter(CourseLabAssignment.course_id.in_(course_ids)).delete(synchronize_session=False)
        db.query(CourseEnrollment).filter(CourseEnrollment.course_id.in_(course_ids)).delete(synchronize_session=False)
        db.query(CourseFeedback).filter(CourseFeedback.course_id.in_(course_ids)).delete(synchronize_session=False)
        db.query(Course).filter(Course.id.in_(course_ids)).delete(synchronize_session=False)
    if lab_ids:
        db.query(CourseLabAssignment).filter(CourseLabAssignment.lab_id.in_(lab_ids)).delete(synchronize_session=False)
        db.query(Lab).filter(Lab.id.in_(lab_ids)).delete(synchronize_session=False)
    demo_tracks = db.query(Track).filter(Track.slug.like(f"{TRACK_SLUG_PREFIX}%")).all()
    for track in demo_tracks:
        levels = db.query(Level).filter(Level.track_id == track.id).all()
        for level in levels:
            db.query(Level).filter(Level.id == level.id).delete(synchronize_session=False)
        db.delete(track)
    if users:
        for user in users:
            db.delete(user)
    db.commit()


def _make_user(db, username: str, first: str, last: str, role: str, org: str) -> User:
    user = User(
        username=username,
        email=f"{username}@example.invalid",
        first_name=first,
        last_name=last,
        organization=org,
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role=role,
        is_admin=False,
        survey_opt_in=True,
        survey_opt_in_at=NOW - timedelta(days=30),
        survey_consent_version="2026.1",
        email_consent_version="2026.1",
        email_consent_updated_at=NOW - timedelta(days=30),
    )
    db.add(user)
    db.flush()
    return user


def _make_track(db, slug: str, name: str) -> Track:
    track = Track(name=f"DemoTest {name}", slug=slug, description="DemoTest seed track", is_active=True)
    db.add(track)
    db.flush()
    return track


def _make_lab(db, level: Level, name: str, slug: str, difficulty: str, minutes: int) -> Lab:
    lab = Lab(
        name=name,
        slug=slug,
        description=f"DemoTest synthetic lab: {name}",
        scenario=f"A DemoTest lab for {name.lower()}.",
        scenario_brief=f"DemoTest lab for {name.lower()}.",
        difficulty=difficulty,
        category="general",
        duration_minutes=minutes,
        is_active=True,
        visibility="course",
        level_id=level.id,
        flag_hash=hashlib.sha256(f"OCR{{{slug}}}".encode()).hexdigest(),
        objectives=json.dumps([f"Complete the {name} objective", "Capture the flag"]),
        hints=json.dumps([{"text": "DemoTest hint one.", "unlock_after_minutes": 5}]),
        tools=json.dumps(["terminal"]),
        compose_file="services: {}\n",
        content_version="2.5.2",
    )
    db.add(lab)
    db.flush()
    return lab


def _event(db, event_type: str, actor_id: int, label: str, target: str, days_ago: int):
    db.add(ActivityEvent(
        event_type=event_type,
        actor_id=actor_id,
        target_type="lab",
        target_label=target,
        detail=label,
        created_at=NOW - timedelta(days=days_ago),
    ))


def seed(db) -> None:
    _cleanup(db)

    instructors = []
    for spec in INSTRUCTORS:
        instructors.append(_make_user(
            db,
            f"{PREFIX}{spec['slug']}",
            spec["first"],
            spec["last"],
            "instructor",
            spec["org"],
        ))

    track_specs = (("web", "Web"), ("network", "Network"), ("forensics", "Forensics"))
    tracks = {slug: _make_track(db, f"{TRACK_SLUG_PREFIX}{slug}", name) for slug, name in track_specs}
    levels = {}
    for slug in tracks:
        level = Level(track_id=tracks[slug].id, level_number=1, name=f"DemoTest {slug.title()} Level 1")
        db.add(level)
        db.flush()
        levels[slug] = level

    labs = []
    for index, (slug, name) in enumerate(track_specs):
        for lab_index in range(1, 4):
            lab_slug = f"{LAB_SLUG_PREFIX}{slug}-{lab_index}"
            labs.append(_make_lab(
                db,
                levels[slug],
                f"DemoTest {name} Exercise {lab_index}",
                lab_slug,
                ["beginner", "intermediate", "advanced"][lab_index - 1],
                30 + index * 10 + lab_index * 5,
            ))
    lab_by_track = {
        "web": labs[0:3],
        "network": labs[3:6],
        "forensics": labs[6:9],
    }

    students = []
    for index in range(1, 61):
        students.append(_make_user(
            db,
            f"{PREFIX}student_{index:02d}",
            f"Student{index:02d}",
            "DemoTest",
            "student",
            "DemoTest Academy",
        ))

    created_courses = []
    student_cursor = 0
    for course_index, spec in enumerate(COURSES):
        instructor = instructors[course_index % len(instructors)]
        suffix = spec["suffix"]
        course = Course(
            name=spec["name"],
            code=f"{COURSE_CODE_PREFIX}{suffix}",
            semester="Fall",
            description=f"DemoTest course {suffix} for reporting and suppression testing.",
            invite_code=f"DEMOTEST-{suffix}-2026",
            instructor_id=instructor.id,
            start_date=NOW - timedelta(days=60),
            end_date=NOW + timedelta(days=30),
            is_active=True,
            is_archived=False,
        )
        db.add(course)
        db.flush()
        created_courses.append(course)

        course_labs = lab_by_track["web"] + lab_by_track["network"][:1]
        for lab in course_labs:
            db.add(CourseLabAssignment(course_id=course.id, lab_id=lab.id))
        db.flush()

        # Two assignments per course.
        for assignment_index, assignment_name in enumerate(("Foundation set", "Applied set"), start=1):
            assignment = Assignment(
                course_id=course.id,
                name=f"DemoTest {suffix} {assignment_name}",
                description="DemoTest assignment grouping.",
                due_date=NOW + timedelta(days=14 * assignment_index),
                start_date=NOW - timedelta(days=14),
                sort_order=assignment_index,
            )
            db.add(assignment)
            db.flush()
            for lab in course_labs[(assignment_index - 1) * 2:(assignment_index - 1) * 2 + 2]:
                db.add(AssignmentLab(assignment_id=assignment.id, lab_id=lab.id))

        cohort = students[student_cursor:student_cursor + spec["students"]]
        student_cursor += spec["students"]
        for student_index, student in enumerate(cohort):
            db.add(CourseEnrollment(
                course_id=course.id,
                user_id=student.id,
                enrolled_at=NOW - timedelta(days=45 - student_index % 10),
            ))
            db.flush()

            # Student course check-in / feedback.
            clarity = RNG.randint(2, 5)
            challenge = RNG.randint(2, 5)
            engagement = RNG.randint(2, 5)
            confidence = RNG.randint(1, 5)
            db.add(CourseFeedback(
                course_id=course.id,
                author_id=student.id,
                direction="student_course",
                clarity=clarity,
                challenge=challenge,
                engagement=engagement,
                confidence=confidence,
                comment=(
                    "The walkthrough helped me understand the evidence."
                    if course_index % 2 == 0 else
                    "I needed more time on the enumeration step."
                ),
                is_anonymous=True,
            ))

            # Instructor coaching note for some learners.
            if student_index % 3 == 0:
                db.add(CourseFeedback(
                    course_id=course.id,
                    author_id=instructor.id,
                    subject_user_id=student.id,
                    direction="instructor_student",
                    clarity=RNG.randint(3, 5),
                    challenge=RNG.randint(2, 4),
                    engagement=RNG.randint(3, 5),
                    confidence=RNG.randint(2, 5),
                    comment="Reviewed the learner's evidence and suggested the next exercise.",
                    is_anonymous=False,
                ))

            for lab_index, lab in enumerate(course_labs):
                started = RNG.random() < max(0.05, spec["completion"] + 0.05)
                if not started:
                    continue
                days_ago = 30 - (student_index + lab_index) % 20
                start_at = NOW - timedelta(days=days_ago, hours=2)
                stop_at = start_at + timedelta(minutes=RNG.randint(25, 110))
                session = LabSession(
                    user_id=student.id,
                    lab_id=lab.id,
                    status="stopped",
                    started_at=start_at,
                    expires_at=start_at + timedelta(hours=2),
                    stopped_at=stop_at,
                )
                db.add(session)
                db.flush()
                _event(db, "lab_started", student.id, "DemoTest lab started", lab.name, days_ago)

                completed = RNG.random() < spec["completion"]
                attempts = RNG.randint(*spec["attempts"])
                hints = 1 if RNG.random() < spec["hint"] else 0
                for attempt in range(attempts):
                    db.add(FlagAttempt(
                        user_id=student.id,
                        lab_id=lab.id,
                        flag_submitted="OCR{demotest_attempt}",
                        is_correct=completed and attempt == attempts - 1,
                        attempted_at=start_at + timedelta(minutes=10 + attempt * 3),
                    ))
                if not completed:
                    continue

                completed_at = start_at + timedelta(minutes=RNG.randint(25, 100))
                db.add(LabCompletion(
                    user_id=student.id,
                    lab_id=lab.id,
                    flag_submitted="OCR{demotest_attempt}",
                    attempts=attempts,
                    hints_used=hints,
                    time_spent_minutes=RNG.randint(20, 100),
                    started_at=start_at,
                    completed_at=completed_at,
                ))
                _event(db, "lab_completed", student.id, "DemoTest lab completed", lab.name, days_ago)

                if student.survey_opt_in and RNG.random() < 0.75:
                    db.add(ExercisePulseSurvey(
                        user_id=student.id,
                        lab_id=lab.id,
                        course_id=course.id,
                        difficulty=RNG.randint(*spec["difficulty"]),
                        learning=RNG.randint(*spec["learning"]),
                        unclear=(
                            "The target address changed between steps."
                            if student_index % 4 == 0 else None
                        ),
                        topic_interest=RNG.choice(["api", "logs", "identity", "forensics"]),
                    ))
                db.add(ExerciseReaction(
                    user_id=student.id,
                    lab_id=lab.id,
                    course_id=course.id,
                    reaction="like" if RNG.random() < 0.7 else "dislike",
                ))
                if RNG.random() < 0.45:
                    score = RNG.randint(40, 100)
                    db.add(ExerciseQuizAttempt(
                        user_id=student.id,
                        lab_id=lab.id,
                        course_id=course.id,
                        question_keys=json.dumps(["q1", "q2"]),
                        answers=json.dumps({"q1": 0, "q2": 1}),
                        score=score,
                        correct=max(0, score // 50),
                        total=2,
                        passed=score >= 60,
                        taken_at=completed_at + timedelta(minutes=5),
                        completed_at=completed_at + timedelta(minutes=5),
                    ))
                    db.add(ExerciseQuizFeedback(
                        user_id=student.id,
                        lab_id=lab.id,
                        course_id=course.id,
                        satisfaction=RNG.randint(2, 5),
                        relevance=RNG.randint(2, 5),
                        usefulness=RNG.randint(2, 5),
                        ease_of_use=RNG.randint(2, 5),
                        comment="Useful check on the key concept.",
                    ))

            # Course reset signals.
            if spec["reset"] and student_index < spec["reset"]:
                reset_lab = course_labs[student_index % len(course_labs)]
                db.add(CourseCompletionReset(
                    course_id=course.id,
                    user_id=student.id,
                    lab_id=reset_lab.id,
                    reset_at=NOW - timedelta(days=5),
                    reset_by=instructor.id,
                ))

            db.add(Achievement(
                user_id=student.id,
                course_id=course.id,
                lab_id=course_labs[0].id,
                achievement_type="first_blood",
                awarded_at=NOW - timedelta(days=20),
            ))
            db.add(SurveyConsentEvent(
                user_id=student.id,
                action="opt_in",
                policy_version="2026.1",
                created_at=NOW - timedelta(days=30),
            ))

    # Surveys attached to the large and small cohorts.
    survey = Survey(
        title=SURVEY_TITLE,
        description="DemoTest survey for reporting and consent boundary testing.",
        questions=json.dumps(SURVEY_QUESTIONS),
        created_by=instructors[0].id,
        is_active=True,
    )
    db.add(survey)
    db.flush()
    for course in (created_courses[0], created_courses[2]):
        db.add(SurveyAttachment(survey_id=survey.id, course_id=course.id))
    for student in students[:12]:
        course = created_courses[0]
        db.add(SurveyResponse(
            survey_id=survey.id,
            user_id=student.id,
            course_id=course.id,
            answers=json.dumps({
                "q1": RNG.randint(3, 5),
                "q2": RNG.randint(3, 5),
                "q3": "More time for the final exercise.",
            }),
            submitted_at=NOW - timedelta(days=7),
        ))
    # Small-cohort survey responses must be suppressed in the analyst view.
    for student in students[30:33]:
        course = created_courses[2]
        db.add(SurveyResponse(
            survey_id=survey.id,
            user_id=student.id,
            course_id=course.id,
            answers=json.dumps({
                "q1": RNG.randint(2, 4),
                "q2": RNG.randint(2, 4),
                "q3": "The small cohort made it easy to compare notes.",
            }),
            submitted_at=NOW - timedelta(days=6),
        ))

    # Competition with synthetic labs and opt-in participants.
    competition = Competition(
        name=COMPETITION_NAME,
        description="DemoTest competition for leaderboard and reporting coverage.",
        start_at=NOW - timedelta(days=3),
        end_at=NOW + timedelta(days=4),
        is_active=True,
        created_by=instructors[0].id,
    )
    db.add(competition)
    db.flush()
    for index, lab in enumerate(labs[:3]):
        db.add(CompetitionLab(competition_id=competition.id, lab_id=lab.id, sort_order=index))
    for student in students[:8]:
        db.add(CompetitionParticipant(
            competition_id=competition.id,
            user_id=student.id,
            source="opt_in",
        ))

    db.commit()

    print("DemoTest feature data seeded.")
    print("Accounts use the password supplied in DEMO_FEATURE_PASSWORD.")
    print("Instructors: demotest_instructor_01 .. demotest_instructor_03")
    print("Students:    demotest_student_01 .. demotest_student_60")
    print("Courses:     DEMOTEST-A (25), B (5), C (3), D (0), E (12), F (8)")
    print("Small cohort for suppression: DEMOTEST-C")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="required development guard")
    parser.add_argument("--yes", action="store_true", help="confirm the seed run")
    parser.add_argument("--cleanup", action="store_true", help="remove DemoTest data")
    args = parser.parse_args()

    if not args.dev or os.environ.get("OCR_DEMO_SEED_ALLOWED") != "1":
        raise SystemExit(
            "Development only. Pass --dev and set OCR_DEMO_SEED_ALLOWED=1. "
            "Never run this against production."
        )
    _refuse_production()

    db = SessionLocal()
    try:
        if args.cleanup:
            _cleanup(db)
            print("DemoTest feature data removed.")
            return 0
        if not args.yes:
            raise SystemExit("Refusing without --yes.")
        if not PASSWORD:
            raise SystemExit(
                "Set DEMO_FEATURE_PASSWORD to the password for the demo accounts. "
                "The value is not printed or written to disk."
            )
        seed(db)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
