"""Simulate a student completing every lab and quiz.

Usage (in container):
  python /app/app/scripts/simulate_student.py <username>
"""
import os
import sys
import yaml
import glob
sys.path.insert(0, "/app")

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://labuser:labpass@db:5432/labdb")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine(DATABASE_URL, connect_args={"application_name": "ocr-app-cli"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.models import User, Lab, LabCompletion, FlagAttempt, LevelQuiz, QuizAttempt, CourseEnrollment
from app.services.achievements import check_achievements
from datetime import datetime, timezone

LABS_ROOT = "/labs"

def load_flags():
    flags = {}
    for path in glob.glob(os.path.join(LABS_ROOT, "**", "lab.yaml"), recursive=True):
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except Exception:
            continue
        if not data or "flag" not in data:
            continue
        # derive slug from directory name
        slug = os.path.basename(os.path.dirname(path))
        flags[slug] = data["flag"]
    return flags

def main():
    if len(sys.argv) < 2:
        print("Usage: simulate_student.py <username>")
        sys.exit(1)
    username = sys.argv[1]
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User {username} not found")
            sys.exit(1)
        user.is_approved = True
        user.is_active = True
        db.commit()

        flags = load_flags()
        print(f"Loaded {len(flags)} flags from lab.yaml")

        labs = db.query(Lab).all()
        completed = 0
        for lab in labs:
            flag = flags.get(lab.slug)
            if not flag:
                print(f"  ! no flag for {lab.slug}")
                continue
            # skip if already completed
            existing = db.query(LabCompletion).filter(
                LabCompletion.user_id == user.id,
                LabCompletion.lab_id == lab.id,
                LabCompletion.flag_submitted.isnot(None),
                LabCompletion.flag_submitted != "",
            ).first()
            if existing:
                completed += 1
                continue
            now = datetime.now(timezone.utc)
            lc = LabCompletion(
                user_id=user.id,
                lab_id=lab.id,
                flag_submitted=flag[:50],
                completed_at=now,
                hints_used=0,
                attempts=1,
            )
            db.add(lc)
            db.add(FlagAttempt(user_id=user.id, lab_id=lab.id, flag_submitted=flag[:50], is_correct=True, attempted_at=now))
            db.commit()
            completed += 1

        print(f"Completed {completed}/{len(labs)} labs")

        # Run achievement checks for each course the user is enrolled in
        enrollments = db.query(CourseEnrollment).filter(CourseEnrollment.user_id == user.id).all()
        for e in enrollments:
            try:
                check_achievements(db, user.id, e.course_id)
                print(f"  achievements checked for course {e.course_id}")
            except Exception as ex:
                print(f"  achievement check failed: {ex}")

        # Also check achievements for all courses (in case not enrolled) - skip, needs enrollment

        # Take all quizzes with perfect score
        quizzes = db.query(LevelQuiz).all()
        for q in quizzes:
            existing = db.query(QuizAttempt).filter(
                QuizAttempt.user_id == user.id,
                QuizAttempt.quiz_id == q.id,
                QuizAttempt.passed == True,
            ).first()
            if existing:
                continue
            # build answers = all correct
            questions = sorted(q.questions, key=lambda x: x.sort_order)
            answers = [qq.correct_index for qq in questions]
            attempt = QuizAttempt(
                user_id=user.id,
                quiz_id=q.id,
                score=100,
                total=len(questions),
                correct=len(questions),
                passed=True,
                answers=__import__("json").dumps(answers),
                taken_at=datetime.now(timezone.utc),
            )
            db.add(attempt)
            db.commit()
        print(f"Took {len(quizzes)} quizzes (perfect scores)")

        print("Done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
