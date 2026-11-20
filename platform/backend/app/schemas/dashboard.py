"""Pydantic schemas for dashboard."""

from datetime import datetime
from typing import List, Optional

from pydantic import (
    BaseModel,
)



class DashboardStatsResponse(BaseModel):
    active_sessions: int = 0
    submission_rate: int = 0
    pending_approvals: int = 0
    course_activity: int = 0


class ActivityEventResponse(BaseModel):
    id: int
    event_type: str
    event_label: str = ""
    actor_id: Optional[int] = None
    actor_username: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    target_label: Optional[str] = None
    detail: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PulseDataPoint(BaseModel):
    hour: str
    concurrent_labs: int = 0
    flags_submitted: int = 0


class PulseResponse(BaseModel):
    data: List[PulseDataPoint] = []


class StudentDashboardResponse(BaseModel):
    next_objective: Optional[dict] = None
    next_quiz: Optional[dict] = None
    progress_percent: int = 0
    total_labs: int = 0
    completed_labs: int = 0
    vpn_status: Optional[dict] = None
    scoreboard_rank: Optional[int] = None
    course_name: Optional[str] = None
