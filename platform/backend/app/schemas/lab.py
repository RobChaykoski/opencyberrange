"""Pydantic schemas for lab."""

import re
from datetime import datetime
from typing import List, Optional

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from app.schemas.common import SafeTextModel


class LabResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    difficulty: str
    category: str
    duration_minutes: int
    is_active: Optional[bool] = True
    level_id: Optional[int] = None
    sort_order: int
    chapter_id: Optional[str] = None
    chapter_name: Optional[str] = None
    primary_competency: Optional[str] = None
    framework_refs: List[str] = Field(default_factory=list, validation_alias="framework_refs_list")
    measurable_outcome: Optional[str] = None
    
    class Config:
        from_attributes = True


class UpdateLabRequest(SafeTextModel):
    name: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    is_course_exclusive: Optional[bool] = None  # Deprecated — use visibility
    is_course_available: Optional[bool] = None  # Deprecated — use visibility
    visibility: Optional[str] = None  # draft | course | pending_public | public
    level_id: Optional[int] = None  # Send explicit null to clear (uncategorize); omit key to leave unchanged
    prerequisites: Optional[str] = None
    mapped_skills: Optional[str] = None
    assessment_criteria: Optional[str] = None
    mitre_attack: Optional[str] = None

    __safe_text_fields__ = {
        "name": "short",
        "description": "multiline",
        "difficulty": "short",
        "category": "short",
        "prerequisites": "multiline",
        "mapped_skills": "multiline",
        "assessment_criteria": "multiline",
        "mitre_attack": "multiline",
    }

    @field_validator('visibility')
    @classmethod
    def visibility_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ('draft', 'course', 'pending_public', 'public'):
            raise ValueError('Visibility must be draft, course, pending_public, or public')
        return v


class TargetInfo(BaseModel):
    name: str
    ip: str
    ports: List[int] = []


class LabSessionResponse(BaseModel):
    id: int
    lab_id: int
    lab_name: str
    lab_slug: str
    network_subnet: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    targets: List[TargetInfo] = []
    
    class Config:
        from_attributes = True


class VPNStatusResponse(BaseModel):
    has_config: bool
    vpn_registered: Optional[bool] = False
    client_ip: Optional[str] = None


class LabCreate(SafeTextModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    scenario: Optional[str] = None
    difficulty: str = "beginner"
    category: str = "general"
    duration_minutes: int = 60
    level_id: Optional[int] = None
    compose_file: str = ""
    objectives: Optional[str] = None
    prerequisites: Optional[str] = None
    mapped_skills: Optional[str] = None
    assessment_criteria: Optional[str] = None
    mitre_attack: Optional[str] = None
    hints: Optional[str] = None
    tools: Optional[str] = None
    hostnames: Optional[str] = None
    flag: Optional[str] = None
    visibility: Optional[str] = None
    lab_yaml: Optional[str] = None

    __safe_text_fields__ = {
        "name": "short",
        "description": "multiline",
        "scenario": "multiline",
        "objectives": "multiline",
        "hints": "multiline",
        "tools": "multiline",
        "hostnames": "multiline",
        "difficulty": "short",
        "category": "short",
    }
    @field_validator('slug')
    @classmethod
    def slug_valid(cls, v: str) -> str:
        if not re.match(r'^[a-z][a-z0-9-]*$', v):
            raise ValueError('Slug must start with lowercase letter and contain only lowercase letters, numbers, and hyphens')
        return v


class TrackCreate(SafeTextModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = "web"
    color: Optional[str] = "#3b82f6"

    __safe_text_fields__ = {"name": "short", "description": "multiline"}

    @field_validator('slug')
    @classmethod
    def slug_valid(cls, v: str) -> str:
        if not re.match(r'^[a-z][a-z0-9-]*$', v):
            raise ValueError('Slug must start with lowercase letter and contain only lowercase letters, numbers, and hyphens')
        return v


class TrackUpdate(SafeTextModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class LevelCreate(SafeTextModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class LevelUpdate(SafeTextModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class ReorderRequest(BaseModel):
    ordered_ids: List[int]
