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
