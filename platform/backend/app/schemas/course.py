"""Pydantic schemas for course."""

import re
import unicodedata
from datetime import datetime
from typing import List, Optional

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from app.schemas.common import SafeTextModel


class CourseCreate(SafeTextModel):
    name: str = Field(..., min_length=3, max_length=150)
    code: str = Field(..., min_length=2, max_length=20)
    semester: str = Field(..., min_length=3, max_length=20)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    instructor_id: Optional[int] = None
    wiki_theme_color: Optional[str] = None

    __safe_text_fields__ = {
        "name": "short",
        "code": "short",
        "semester": "short",
        "description": "multiline",
    }


class CourseUpdate(SafeTextModel):
    name: Optional[str] = Field(None, min_length=3, max_length=150)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    semester: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None
    instructor_id: Optional[int] = None
    wiki_theme_color: Optional[str] = None

    __safe_text_fields__ = {
        "name": "short",
        "code": "short",
        "semester": "short",
        "description": "multiline",
    }


class CourseResponse(BaseModel):
    id: int
    name: str
    code: str
    semester: str
    description: Optional[str] = None
    invite_code: str
    instructor_id: int
    instructor_name: Optional[str] = None
    start_date: datetime
    end_date: datetime
    is_active: bool
    is_archived: bool = False
    wiki_slug: Optional[str] = None
    wiki_theme_color: Optional[str] = "blue"
    created_at: Optional[datetime] = None
    student_count: int = 0
    lab_count: int = 0

    class Config:
        from_attributes = True


class CourseJoinRequest(BaseModel):
    # Allow surrounding whitespace and full-width input to be normalised before
    # the 6-20 character check, so a pasted code is not rejected for formatting.
    invite_code: str = Field(..., min_length=1, max_length=64)

    @field_validator("invite_code")
    @classmethod
    def normalize_invite_code(cls, v: str) -> str:
        value = unicodedata.normalize("NFKC", v)
        value = re.sub(r"\s+", "", value)
        if not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", value):
            raise ValueError(
                "Invite code must be 6-20 letters, numbers, hyphens, or underscores"
            )
        return value


class ExerciseQuizFeedbackInput(SafeTextModel):
    """Optional post-quiz ratings that feed course experience metrics."""

    satisfaction: Optional[int] = Field(None, ge=1, le=5)
    relevance: Optional[int] = Field(None, ge=1, le=5)
    usefulness: Optional[int] = Field(None, ge=1, le=5)
    ease_of_use: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)

    __safe_text_fields__ = {"comment": "multiline"}


class ExerciseQuizSubmitRequest(BaseModel):
    answers: dict = Field(default_factory=dict)
    feedback: Optional[ExerciseQuizFeedbackInput] = None


class CourseFeedbackRequest(SafeTextModel):
    """Student course check-in or instructor coaching note.

    Ratings are 1-5. Students send no ``subject_user_id``; instructors must
    send the enrolled student they are coaching.
    """
    clarity: Optional[int] = Field(None, ge=1, le=5)
    challenge: Optional[int] = Field(None, ge=1, le=5)
    engagement: Optional[int] = Field(None, ge=1, le=5)
    confidence: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)
    subject_user_id: Optional[int] = None

    __safe_text_fields__ = {"comment": "multiline"}


class CourseLabAssignRequest(BaseModel):
    lab_ids: List[int]


class CourseLabBulkRemoveRequest(BaseModel):
    lab_ids: List[int]


class CourseLabReorderRequest(BaseModel):
    lab_order: List[dict]


class AssignmentReorderRequest(BaseModel):
    assignment_order: List[dict]


class CourseLabUpdateRequest(SafeTextModel):
    display_name: Optional[str] = Field(None, max_length=255)

    __safe_text_fields__ = {"display_name": "short"}


class BulkEnrollRequest(BaseModel):
    user_ids: List[int]


class MinorConsentRequest(BaseModel):
    reference: str = Field(..., min_length=3, max_length=200)


class ScoreboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    student_id: Optional[str] = None
    total_score: int
    labs_completed: int
    achievements: List[str] = []
    lab_scores: dict = {}


class ScoreboardResponse(BaseModel):
    course: dict
    labs: List[dict]
    scoreboard: List[ScoreboardEntry]


class AchievementResponse(BaseModel):
    id: int
    user_id: int
    username: str
    achievement_type: str
    lab_id: Optional[int] = None
    lab_name: Optional[str] = None
    awarded_at: datetime

    class Config:
        from_attributes = True


class AssignmentCreate(SafeTextModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    locked: Optional[bool] = False

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class AssignmentUpdate(SafeTextModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    locked: Optional[bool] = None

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class AssignmentLabsRequest(BaseModel):
    lab_ids: List[int]
