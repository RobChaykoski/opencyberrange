"""Resolve exercises targeted at a learner's course cohorts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import (
    Course,
    CourseCohort,
    CourseCohortMember,
    CourseEnrollment,
    CourseRequirement,
    ExerciseSet,
    ExerciseSetItem,
)


def cohort_lab_ids(
    db: Session,
    user_id: int,
    course_id: Optional[int] = None,
    *,
    required_only: bool = True,
) -> set[int]:
    """Labs in exercise sets required for a cohort the learner belongs to."""
    now = datetime.now(timezone.utc)
    query = (
        db.query(ExerciseSetItem.lab_id)
        .join(ExerciseSet, ExerciseSet.id == ExerciseSetItem.set_id)
        .join(CourseRequirement, CourseRequirement.set_id == ExerciseSet.id)
        .join(CourseCohort, CourseCohort.id == CourseRequirement.cohort_id)
        .join(CourseCohortMember, CourseCohortMember.cohort_id == CourseCohort.id)
        .join(Course, Course.id == CourseCohort.course_id)
        .join(
            CourseEnrollment,
            (CourseEnrollment.course_id == Course.id)
            & (CourseEnrollment.user_id == CourseCohortMember.user_id),
        )
        .filter(
            CourseCohortMember.user_id == user_id,
            Course.is_active.is_(True),
            Course.end_date >= now,
        )
    )
    if course_id is not None:
        query = query.filter(Course.id == course_id)
    if required_only:
        query = query.filter(ExerciseSetItem.required.is_(True))
    return {row[0] for row in query.distinct().all()}


def has_cohort_requirements(db: Session, course_id: int) -> bool:
    """True when at least one cohort has an exercise-set requirement."""
    return (
        db.query(CourseRequirement.id)
        .filter(CourseRequirement.course_id == course_id)
        .first()
        is not None
    )


def strict_cohort_lab_ids(
    db: Session, user_id: int, course_id: int
) -> set[int] | None:
    """Return the visible lab IDs for a strict course, or None to keep all."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None or not course.cohort_strict:
        return None
    if not has_cohort_requirements(db, course_id):
        return None
    return cohort_lab_ids(db, user_id, course_id, required_only=False)


def visible_course_lab_ids(
    db: Session, user_id: int, course_id: int, assigned_lab_ids: set[int]
) -> set[int]:
    """Intersect a course's assigned labs with strict cohort visibility."""
    strict = strict_cohort_lab_ids(db, user_id, course_id)
    return assigned_lab_ids if strict is None else assigned_lab_ids & strict


def sync_default_cohort(db: Session, course: Course) -> int:
    """Add enrolled learners who have no cohort to the course default cohort."""
    default = (
        db.query(CourseCohort)
        .filter(
            CourseCohort.course_id == course.id,
            CourseCohort.is_default.is_(True),
        )
        .first()
    )
    if default is None:
        return 0
    enrolled_ids = {
        row[0]
        for row in db.query(CourseEnrollment.user_id)
        .filter(CourseEnrollment.course_id == course.id)
        .all()
    }
    member_ids = {
        row[0]
        for row in db.query(CourseCohortMember.user_id)
        .join(CourseCohort, CourseCohort.id == CourseCohortMember.cohort_id)
        .filter(CourseCohort.course_id == course.id)
        .all()
    }
    added = 0
    for user_id in sorted(enrolled_ids - member_ids):
        db.add(CourseCohortMember(cohort_id=default.id, user_id=user_id))
        added += 1
    if added:
        db.commit()
    return added

