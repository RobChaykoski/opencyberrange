"""Course cohorts, exercise sets, requirements, and coverage."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import (
    Course,
    CourseCohort,
    CourseCohortMember,
    CourseEnrollment,
    CourseRequirement,
    ExerciseSet,
    ExerciseSetItem,
    Lab,
    LabCompletion,
    User,
)
from app.services.activity import EventTypes, log_activity

router = APIRouter()

RULE_TYPES = {"complete_all", "complete_percent", "complete_count"}


def _course_or_403(db: Session, course_id: int, user: User) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if user.role != "admin" and course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to plan this course")
    return course


def _cohort(db: Session, course_id: int, cohort_id: int) -> CourseCohort:
    row = (
        db.query(CourseCohort)
        .filter(CourseCohort.id == cohort_id, CourseCohort.course_id == course_id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Cohort not found")
    return row


def _set(db: Session, course_id: int, set_id: int) -> ExerciseSet:
    row = (
        db.query(ExerciseSet)
        .filter(ExerciseSet.id == set_id, ExerciseSet.course_id == course_id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Exercise set not found")
    return row


def _require_rule(rule_type: str, threshold: Optional[int]) -> None:
    if rule_type not in RULE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported requirement rule")
    if rule_type == "complete_all":
        return
    if threshold is None or threshold < 1:
        raise HTTPException(status_code=400, detail="A positive threshold is required")
    if rule_type == "complete_percent" and threshold > 100:
        raise HTTPException(status_code=400, detail="Percent threshold is 1–100")


def _member_ids(db: Session, cohort_id: int) -> list[int]:
    return [
        row.user_id
        for row in db.query(CourseCohortMember.user_id)
        .filter(CourseCohortMember.cohort_id == cohort_id)
        .all()
    ]


class CohortCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(None, max_length=500)


class CohortUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = Field(None, max_length=500)


class MembersRequest(BaseModel):
    user_ids: list[int]


class SetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(None, max_length=500)
    sort_order: int = 0


class SetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = Field(None, max_length=500)
    sort_order: int | None = None


class SetItem(BaseModel):
    lab_id: int
    required: bool = True
    sort_order: int = 0


class SetItemsRequest(BaseModel):
    items: list[SetItem]


class RequirementCreate(BaseModel):
    cohort_id: int
    set_id: int
    rule_type: str = "complete_all"
    threshold: int | None = None
    due_at: str | None = None
    note: str | None = Field(None, max_length=500)

    @field_validator("rule_type")
    @classmethod
    def valid_rule(cls, value: str) -> str:
        if value not in RULE_TYPES:
            raise ValueError("unsupported rule type")
        return value


class RequirementUpdate(BaseModel):
    cohort_id: int | None = None
    set_id: int | None = None
    rule_type: str | None = None
    threshold: int | None = None
    due_at: str | None = None
    note: str | None = Field(None, max_length=500)


def _parse_due(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid due date") from exc
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def _set_payload(db: Session, row: ExerciseSet) -> dict:
    items = (
        db.query(ExerciseSetItem, Lab)
        .join(Lab, Lab.id == ExerciseSetItem.lab_id)
        .filter(ExerciseSetItem.set_id == row.id)
        .order_by(ExerciseSetItem.sort_order, ExerciseSetItem.id)
        .all()
    )
    return {
        "id": row.id,
        "name": row.name,
        "description": row.description,
        "sort_order": row.sort_order,
        "items": [
            {
                "id": item.id,
                "lab_id": item.lab_id,
                "lab_name": lab.name,
                "required": bool(item.required),
                "sort_order": item.sort_order,
            }
            for item, lab in items
        ],
    }


def _cohort_payload(db: Session, row: CourseCohort) -> dict:
    members = (
        db.query(User)
        .join(CourseCohortMember, CourseCohortMember.user_id == User.id)
        .filter(CourseCohortMember.cohort_id == row.id)
        .order_by(func.lower(User.username))
        .all()
    )
    return {
        "id": row.id,
        "name": row.name,
        "description": row.description,
        "members": [
            {"id": member.id, "username": member.username, "role": member.role}
            for member in members
        ],
    }


def _requirement_payload(row: CourseRequirement) -> dict:
    return {
        "id": row.id,
        "cohort_id": row.cohort_id,
        "set_id": row.set_id,
        "rule_type": row.rule_type,
        "threshold": row.threshold,
        "due_at": row.due_at.isoformat() if row.due_at else None,
        "note": row.note,
    }


def _coverage(db: Session, course: Course) -> list[dict]:
    cohorts = {
        row.id: row
        for row in db.query(CourseCohort)
        .filter(CourseCohort.course_id == course.id)
        .all()
    }
    sets = {
        row.id: row
        for row in db.query(ExerciseSet)
        .filter(ExerciseSet.course_id == course.id)
        .all()
    }
    requirements = (
        db.query(CourseRequirement)
        .filter(CourseRequirement.course_id == course.id)
        .order_by(CourseRequirement.id)
        .all()
    )
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    result = []
    for requirement in requirements:
        cohort = cohorts.get(requirement.cohort_id)
        exercise_set = sets.get(requirement.set_id)
        if cohort is None or exercise_set is None:
            continue
        items = (
            db.query(ExerciseSetItem)
            .filter(ExerciseSetItem.set_id == exercise_set.id)
            .all()
        )
        lab_ids = [item.lab_id for item in items if item.required]
        total_items = len(lab_ids)
        if requirement.rule_type == "complete_percent":
            needed = max(1, round(total_items * (requirement.threshold or 0) / 100))
        elif requirement.rule_type == "complete_count":
            needed = min(total_items, requirement.threshold or 0)
        else:
            needed = total_items

        members = (
            db.query(User)
            .join(CourseCohortMember, CourseCohortMember.user_id == User.id)
            .filter(CourseCohortMember.cohort_id == cohort.id)
            .order_by(func.lower(User.username))
            .all()
        )
        completed_by_user: dict[int, int] = {}
        if members and lab_ids:
            for user_id, count in (
                db.query(LabCompletion.user_id, func.count(func.distinct(LabCompletion.lab_id)))
                .filter(
                    LabCompletion.user_id.in_([member.id for member in members]),
                    LabCompletion.lab_id.in_(lab_ids),
                )
                .group_by(LabCompletion.user_id)
                .all()
            ):
                completed_by_user[user_id] = int(count)

        students = []
        met = 0
        for member in members:
            done = completed_by_user.get(member.id, 0)
            passed = done >= needed if needed else False
            met += 1 if passed else 0
            students.append(
                {
                    "id": member.id,
                    "username": member.username,
                    "completed": done,
                    "required": needed,
                    "met": passed,
                }
            )
        overdue = bool(requirement.due_at and requirement.due_at < now and met < len(members))
        result.append(
            {
                **_requirement_payload(requirement),
                "cohort_name": cohort.name,
                "set_name": exercise_set.name,
                "total_items": total_items,
                "learners": len(members),
                "met": met,
                "missing": len(members) - met,
                "overdue": overdue,
                "students": students,
            }
        )
    return result


@router.get("/courses/{course_id}/planning")
def get_planning(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = _course_or_403(db, course_id, current_user)
    cohorts = (
        db.query(CourseCohort)
        .filter(CourseCohort.course_id == course.id)
        .order_by(func.lower(CourseCohort.name))
        .all()
    )
    sets = (
        db.query(ExerciseSet)
        .filter(ExerciseSet.course_id == course.id)
        .order_by(ExerciseSet.sort_order, func.lower(ExerciseSet.name))
        .all()
    )
    requirements = (
        db.query(CourseRequirement)
        .filter(CourseRequirement.course_id == course.id)
        .order_by(CourseRequirement.id)
        .all()
    )
    return {
        "cohorts": [_cohort_payload(db, row) for row in cohorts],
        "exercise_sets": [_set_payload(db, row) for row in sets],
        "requirements": [_requirement_payload(row) for row in requirements],
        "coverage": _coverage(db, course),
    }


@router.post("/courses/{course_id}/cohorts", status_code=201)
def create_cohort(
    course_id: int,
    payload: CohortCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = _course_or_403(db, course_id, current_user)
    duplicate = (
        db.query(CourseCohort)
        .filter(
            CourseCohort.course_id == course.id,
            func.lower(CourseCohort.name) == payload.name.strip().lower(),
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="A cohort with that name exists")
    row = CourseCohort(
        course_id=course.id,
        name=payload.name.strip(),
        description=(payload.description or "").strip() or None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    log_activity(
        db,
        EventTypes.COHORT_CREATED,
        actor_id=current_user.id,
        target_type="course",
        target_id=course.id,
        target_label=course.name,
        detail={"cohort_id": row.id, "name": row.name},
    )
    return _cohort_payload(db, row)


@router.patch("/courses/{course_id}/cohorts/{cohort_id}")
def update_cohort(
    course_id: int,
    cohort_id: int,
    payload: CohortUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _course_or_403(db, course_id, current_user)
    row = _cohort(db, course_id, cohort_id)
    if payload.name is not None:
        row.name = payload.name.strip()
    if payload.description is not None:
        row.description = payload.description.strip() or None
    db.commit()
    return _cohort_payload(db, row)


@router.delete("/courses/{course_id}/cohorts/{cohort_id}")
def delete_cohort(
    course_id: int,
    cohort_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _course_or_403(db, course_id, current_user)
    row = _cohort(db, course_id, cohort_id)
    db.delete(row)
    db.commit()
    return {"ok": True}


@router.put("/courses/{course_id}/cohorts/{cohort_id}/members")
def set_cohort_members(
    course_id: int,
    cohort_id: int,
    payload: MembersRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = _course_or_403(db, course_id, current_user)
    cohort = _cohort(db, course_id, cohort_id)
    enrolled = {
        row.user_id
        for row in db.query(CourseEnrollment.user_id)
        .filter(CourseEnrollment.course_id == course.id)
        .all()
    }
    requested = set(payload.user_ids)
    if not requested.issubset(enrolled):
        raise HTTPException(
            status_code=400, detail="Cohort members must be enrolled in the course"
        )
    db.query(CourseCohortMember).filter(
        CourseCohortMember.cohort_id == cohort.id
    ).delete(synchronize_session=False)
    for user_id in sorted(requested):
        db.add(CourseCohortMember(cohort_id=cohort.id, user_id=user_id))
    db.commit()
    return _cohort_payload(db, cohort)


@router.post("/courses/{course_id}/exercise-sets", status_code=201)
def create_set(
    course_id: int,
    payload: SetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = _course_or_403(db, course_id, current_user)
    duplicate = (
        db.query(ExerciseSet)
        .filter(
            ExerciseSet.course_id == course.id,
            func.lower(ExerciseSet.name) == payload.name.strip().lower(),
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="An exercise set with that name exists")
    row = ExerciseSet(
        course_id=course.id,
        name=payload.name.strip(),
        description=(payload.description or "").strip() or None,
        sort_order=payload.sort_order,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _set_payload(db, row)


@router.patch("/courses/{course_id}/exercise-sets/{set_id}")
def update_set(
    course_id: int,
    set_id: int,
    payload: SetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _course_or_403(db, course_id, current_user)
    row = _set(db, course_id, set_id)
    if payload.name is not None:
        row.name = payload.name.strip()
    if payload.description is not None:
        row.description = payload.description.strip() or None
    if payload.sort_order is not None:
        row.sort_order = payload.sort_order
    db.commit()
    return _set_payload(db, row)


@router.delete("/courses/{course_id}/exercise-sets/{set_id}")
def delete_set(
    course_id: int,
    set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _course_or_403(db, course_id, current_user)
    row = _set(db, course_id, set_id)
    db.delete(row)
    db.commit()
    return {"ok": True}


@router.put("/courses/{course_id}/exercise-sets/{set_id}/items")
def set_items(
    course_id: int,
    set_id: int,
    payload: SetItemsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _course_or_403(db, course_id, current_user)
    row = _set(db, course_id, set_id)
    lab_ids = [item.lab_id for item in payload.items]
    if lab_ids:
        found = {
            lab.id for lab in db.query(Lab.id).filter(Lab.id.in_(lab_ids)).all()
        }
        missing = set(lab_ids) - found
        if missing:
            raise HTTPException(
                status_code=400, detail=f"Unknown exercise IDs: {sorted(missing)}"
            )
    db.query(ExerciseSetItem).filter(ExerciseSetItem.set_id == row.id).delete(
        synchronize_session=False
    )
    for index, item in enumerate(payload.items):
        db.add(
            ExerciseSetItem(
                set_id=row.id,
                lab_id=item.lab_id,
                required=item.required,
                sort_order=item.sort_order or index,
            )
        )
    db.commit()
    return _set_payload(db, row)


@router.post("/courses/{course_id}/requirements", status_code=201)
def create_requirement(
    course_id: int,
    payload: RequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = _course_or_403(db, course_id, current_user)
    _cohort(db, course.id, payload.cohort_id)
    _set(db, course.id, payload.set_id)
    _require_rule(payload.rule_type, payload.threshold)
    row = CourseRequirement(
        course_id=course.id,
        cohort_id=payload.cohort_id,
        set_id=payload.set_id,
        rule_type=payload.rule_type,
        threshold=payload.threshold,
        due_at=_parse_due(payload.due_at),
        note=(payload.note or "").strip() or None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _requirement_payload(row)


@router.patch("/courses/{course_id}/requirements/{requirement_id}")
def update_requirement(
    course_id: int,
    requirement_id: int,
    payload: RequirementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _course_or_403(db, course_id, current_user)
    row = (
        db.query(CourseRequirement)
        .filter(
            CourseRequirement.id == requirement_id,
            CourseRequirement.course_id == course_id,
        )
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    if payload.cohort_id is not None:
        _cohort(db, course_id, payload.cohort_id)
        row.cohort_id = payload.cohort_id
    if payload.set_id is not None:
        _set(db, course_id, payload.set_id)
        row.set_id = payload.set_id
    if payload.rule_type is not None:
        _require_rule(payload.rule_type, payload.threshold)
        row.rule_type = payload.rule_type
    if payload.threshold is not None:
        row.threshold = payload.threshold
    if payload.due_at is not None:
        row.due_at = _parse_due(payload.due_at)
    if payload.note is not None:
        row.note = payload.note.strip() or None
    _require_rule(row.rule_type, row.threshold)
    db.commit()
    return _requirement_payload(row)


@router.delete("/courses/{course_id}/requirements/{requirement_id}")
def delete_requirement(
    course_id: int,
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _course_or_403(db, course_id, current_user)
    row = (
        db.query(CourseRequirement)
        .filter(
            CourseRequirement.id == requirement_id,
            CourseRequirement.course_id == course_id,
        )
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    db.delete(row)
    db.commit()
    return {"ok": True}


@router.get("/courses/{course_id}/planning/coverage")
def get_coverage(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = _course_or_403(db, course_id, current_user)
    return {"coverage": _coverage(db, course)}
