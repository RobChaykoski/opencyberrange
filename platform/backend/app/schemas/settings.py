"""Pydantic schemas for settings."""

from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)

from app.schemas.common import SafeTextModel


class SettingsBulkUpdate(BaseModel):
    settings: dict  # {"key": "value", ...}
    ticket_number: Optional[str] = Field(None, max_length=80)
    reason: Optional[str] = Field(None, max_length=2000)


class SettingsChangeRevert(BaseModel):
    reason: str = Field(..., min_length=5, max_length=2000)


class ProductionCutoverRequest(BaseModel):
    ticket_number: str = Field(..., min_length=2, max_length=80)
    password: str = Field(..., min_length=1, max_length=200)
    confirmation: str = Field(..., max_length=40)
    acknowledge_data_loss: bool
    acknowledge_one_way: bool
    reason: str = Field(..., min_length=5, max_length=2000)


class MailTestRequest(BaseModel):
    """Optional recipient for an admin-triggered SMTP test."""
    to: Optional[EmailStr] = None


class CustomAchievementCreate(SafeTextModel):
    """Admin-defined achievement definition."""
    name: str = Field(..., min_length=2, max_length=80)
    description: str | None = Field(None, max_length=500)
    icon: str = Field("\U0001F3C5", max_length=16)
    trigger: str = Field("labs_completed", max_length=30)
    threshold: int = Field(1, ge=1, le=10000)
    group_key: str = Field("custom", max_length=30)
    tier: str = Field("bronze", max_length=20)
    difficulty: str = Field("standard", max_length=20)
    is_active: bool = True

    __safe_text_fields__ = {"name": "short", "description": "multiline"}


class CustomAchievementUpdate(SafeTextModel):
    name: str | None = Field(None, min_length=2, max_length=80)
    description: str | None = Field(None, max_length=500)
    icon: str | None = Field(None, max_length=16)
    trigger: str | None = Field(None, max_length=30)
    threshold: int | None = Field(None, ge=1, le=10000)
    group_key: str | None = Field(None, max_length=30)
    tier: str | None = Field(None, max_length=20)
    difficulty: str | None = Field(None, max_length=20)
    is_active: bool | None = None

    __safe_text_fields__ = {"name": "short", "description": "multiline"}
