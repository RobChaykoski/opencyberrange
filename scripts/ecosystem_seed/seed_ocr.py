"""Seed a synthetic capstone course in the development OpenCyberRange instance.

Run inside the dev backend container:

    docker exec -i -e TRAINING_PASSWORD='...' ocr-backend python - < scripts/ecosystem_seed/seed_ocr.py

This is additive and idempotent. It is for the development instance only.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import (
    Course,
    CourseEnrollment,
    CourseLabAssignment,
    CourseStaff,
    ExerciseSet,
    Lab,
    User,
)

# security-delta: allow credential-like assignment (synthetic lab password)
PASSWORD = os.environ.get("TRAINING_PASSWORD", "TrainLab!2026#Student")
COURSE_CODE = "OCR-CAP-COHORT"
INVITE_CODE = "OCRTRAIN26"


def ensure_user(session, username: str, role: str, first: str, last: str) -> User:
    user = session.query(User).filter(User.username == username).first()
    if user is not None:
        if not user.is_approved:
            user.is_approved = True
        if user.role != role:
            user.role = role
        return user
    user = User(
        username=username,
        email=f"{username}@example.invalid",
        first_name=first,
        last_name=last,
        role=role,
        hashed_password=get_password_hash(PASSWORD),
        institution_id="default",
        is_approved=True,
    )
    session.add(user)
    session.flush()
    return user


def main() -> None:
    session = SessionLocal()
    try:
        instructor = ensure_user(session, "instructor01", "instructor", "Morgan", "Instructor")
        mentor = ensure_user(session, "mentor01", "mentor", "Alex", "Mentor")
        assistant = ensure_user(session, "ta01", "teaching_assistant", "Jamie", "Assistant")
        students = [
            ensure_user(session, f"student{i:02d}", "student", "Student", f"Number{i}")
            for i in range(1, 9)
        ]
        ensure_user(session, "privacy01", "privacy_officer", "Pat", "Privacy")
        ensure_user(session, "auditor01", "auditor", "Avery", "Auditor")

        course = session.query(Course).filter(Course.code == COURSE_CODE).first()
        if course is None:
            now = datetime.now(timezone.utc)
            course = Course(
                name="Capstone: Multi-Student Cohort Defence",
                code=COURSE_CODE,
                semester="2026F",
                description=(
                    "Synthetic capstone for the dev training lab. Fake learners, "
                    "fake assets, and fake evidence only."
                ),
                invite_code=INVITE_CODE,
                instructor_id=instructor.id,
                institution_id="default",
                start_date=now,
                end_date=now + timedelta(days=120),
                is_active=True,
                cohort_strict=False,
            )
            session.add(course)
            session.flush()

        for student in students:
            exists = (
                session.query(CourseEnrollment)
                .filter(
                    CourseEnrollment.course_id == course.id,
                    CourseEnrollment.user_id == student.id,
                )
                .first()
            )
            if exists is None:
                session.add(
                    CourseEnrollment(
                        course_id=course.id,
                        user_id=student.id,
                        institution_id="default",
                    )
                )

        for user, staff_role in [
            (mentor, "mentor"),
            (assistant, "teaching_assistant"),
            (instructor, "co_instructor"),
        ]:
            exists = (
                session.query(CourseStaff)
                .filter(
                    CourseStaff.course_id == course.id,
                    CourseStaff.user_id == user.id,
                    CourseStaff.staff_role == staff_role,
                )
                .first()
            )
            if exists is None:
                session.add(
                    CourseStaff(
                        course_id=course.id,
                        user_id=user.id,
                        staff_role=staff_role,
                        created_by_id=instructor.id,
                    )
                )

        if not session.query(ExerciseSet).filter(
            ExerciseSet.course_id == course.id, ExerciseSet.name == "Capstone"
        ).first():
            session.add(
                ExerciseSet(
                    course_id=course.id,
                    name="Capstone",
                    description="Synthetic cohort capstone exercise set.",
                    sort_order=1,
                )
            )

        preferred_slugs = [
            "network-1-4-failed-login-analysis",
            "identity-2-1-identity-lifecycle",
            "network-12-2-firewall-policy-hardening",
        ]
        labs = [
            lab
            for lab in (
                session.query(Lab).filter(Lab.slug == slug).first()
                for slug in preferred_slugs
            )
            if lab is not None
        ]
        if not labs:
            labs = session.query(Lab).limit(3).all()
        session.query(CourseLabAssignment).filter(
            CourseLabAssignment.course_id == course.id
        ).delete()
        for index, lab in enumerate(labs):
            session.add(
                CourseLabAssignment(
                    course_id=course.id,
                    lab_id=lab.id,
                    sort_order=index,
                )
            )

        # A second course that is deliberately not assigned to the mentor or the
        # teaching assistant. It proves cross-course scope denial.
        single = session.query(Course).filter(Course.code == "OCR-CAP-SINGLE").first()
        if single is None:
            now = datetime.now(timezone.utc)
            single = Course(
                name="Capstone: Single-Student Security Operations",
                code="OCR-CAP-SINGLE",
                semester="2026F",
                description=(
                    "Synthetic single-student capstone. Not assigned to the "
                    "cohort mentor or teaching assistant."
                ),
                invite_code="OCRTRAIN26S",
                instructor_id=instructor.id,
                institution_id="default",
                start_date=now,
                end_date=now + timedelta(days=120),
                is_active=True,
                cohort_strict=False,
            )
            session.add(single)
            session.flush()
        for student in students[:4]:
            exists = (
                session.query(CourseEnrollment)
                .filter(
                    CourseEnrollment.course_id == single.id,
                    CourseEnrollment.user_id == student.id,
                )
                .first()
            )
            if exists is None:
                session.add(
                    CourseEnrollment(
                        course_id=single.id,
                        user_id=student.id,
                        institution_id="default",
                    )
                )
        single_lab = (
            session.query(Lab)
            .filter(Lab.slug == "linux-1-1-ssh-service-detection")
            .first()
        )
        session.query(CourseLabAssignment).filter(
            CourseLabAssignment.course_id == single.id
        ).delete()
        if single_lab is not None:
            session.add(
                CourseLabAssignment(
                    course_id=single.id,
                    lab_id=single_lab.id,
                    sort_order=0,
                )
            )

        session.commit()
        print(f"Seeded OCR dev course {course.code} (id={course.id}).")
        print(f"Seeded OCR dev course {single.code} (id={single.id}) without mentor/TA staff.")
        print("Enrolled students:", ", ".join(user.username for user in students))
        print("Staff: mentor01 (mentor), ta01 (teaching_assistant), instructor01 (co_instructor)")
        print("Assigned labs:", ", ".join(lab.slug for lab in labs))
    finally:
        session.close()


if __name__ == "__main__":
    main()
