"""Versioned analytics event and Exercise Health contracts.

The documents in ``docs/ANALYTICS-EVENT-SCHEMA.md`` and
``docs/ANALYTICS-GOVERNANCE.md`` are the human-readable contract. This module
keeps the machine-readable field names, required values, and privacy
classifications in one place so future event writers, exports, and tests cannot
drift from the documentation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

ANALYTICS_SCHEMA_VERSION = "2.5.3"

# The minimum event envelope. Every analytics event must carry these fields.
MINIMUM_EVENT_FIELDS: dict[str, dict[str, Any]] = {
    "event_id": {
        "type": "string",
        "required": True,
        "privacy": "pseudonymous",
        "description": "Stable UUID for the event; used for idempotency and audit.",
    },
    "pseudonymous_user_id": {
        "type": "string",
        "required": True,
        "privacy": "pseudonymous",
        "description": "Keyed hash of the learner ID; never the raw user ID in exports.",
    },
    "course_id": {
        "type": "integer|null",
        "required": False,
        "privacy": "confidential",
        "description": "Course context, or null for standalone practice.",
    },
    "cohort_id": {
        "type": "string|null",
        "required": False,
        "privacy": "confidential",
        "description": "Cohort grouping such as course code plus term.",
    },
    "exercise_id": {
        "type": "integer|null",
        "required": False,
        "privacy": "internal",
        "description": "Lab/exercise identifier, or null for non-exercise events.",
    },
    "exercise_version": {
        "type": "string|null",
        "required": False,
        "privacy": "internal",
        "description": "Content version of the lab; essential for comparing revisions.",
    },
    "mapping_version": {
        "type": "string|null",
        "required": False,
        "privacy": "internal",
        "description": "Track and competency mapping version used at event time.",
    },
    "occurred_at": {
        "type": "datetime",
        "required": True,
        "privacy": "confidential",
        "description": "UTC timestamp of the learner action.",
    },
    "attempt_id": {
        "type": "string|null",
        "required": False,
        "privacy": "pseudonymous",
        "description": "Groups events from one exercise attempt.",
    },
    "event_type": {
        "type": "string",
        "required": True,
        "privacy": "internal",
        "description": "One of EVENT_TYPES.",
    },
    "result": {
        "type": "string|null",
        "required": False,
        "privacy": "confidential",
        "description": "Outcome value such as completed, failed, abandoned, or passed.",
    },
    "platform_version": {
        "type": "string",
        "required": True,
        "privacy": "internal",
        "description": "Platform release that produced the event.",
    },
    "source": {
        "type": "string",
        "required": True,
        "privacy": "internal",
        "description": "learner, instructor, or system.",
    },
    "privacy_classification": {
        "type": "string",
        "required": True,
        "privacy": "internal",
        "description": "One of PRIVACY_CLASSIFICATIONS.",
    },
}

EVENT_TYPES = {
    "exercise_started",
    "exercise_completed",
    "exercise_abandoned",
    "flag_attempted",
    "hint_requested",
    "workbook_opened",
    "quiz_attempted",
    "pulse_submitted",
    "feedback_submitted",
    "certificate_issued",
    "transcript_requested",
}

RESULT_VALUES = {
    "started",
    "completed",
    "abandoned",
    "correct",
    "incorrect",
    "passed",
    "failed",
    "opened",
    "submitted",
    "issued",
    "requested",
}

SOURCES = {"learner", "instructor", "system"}

PRIVACY_CLASSIFICATIONS = {
    "pseudonymous",
    "confidential",
    "restricted",
    "aggregate",
    "internal",
}

HEALTH_STATUSES = {"green", "amber", "red", "grey"}

EXERCISE_HEALTH_FIELDS = (
    "assigned_learners",
    "started_learners",
    "completed_learners",
    "median_active_time_minutes",
    "active_time_iqr",
    "first_attempt_success_rate",
    "median_attempts",
    "hint_use_rate",
    "median_time_to_first_hint_minutes",
    "reset_rate",
    "technical_failure_rate",
    "abandonment_point",
    "difficulty_rating",
    "instruction_clarity",
    "learning_value_rating",
    "free_text_themes",
    "lab_version",
    "sample_size",
    "health_status",
    "component_status",
)

HEALTH_STATUS_MEANING = {
    "green": "Technically reliable, clear, appropriate difficulty, strong learning value.",
    "amber": "Mixed evidence, strained experience, or a component near its threshold.",
    "red": "Technical failures, unclear instructions, severe abandonment, or low learning value.",
    "grey": "Insufficient evidence; no judgement is made.",
}


def validate_event(event: dict) -> list[str]:
    """Return a list of contract violations for one analytics event."""
    problems: list[str] = []
    for field, spec in MINIMUM_EVENT_FIELDS.items():
        if spec["required"] and event.get(field) in (None, ""):
            problems.append(f"{field} is required")
    if event.get("event_type") and event["event_type"] not in EVENT_TYPES:
        problems.append(f"event_type must be one of {sorted(EVENT_TYPES)}")
    if event.get("result") and event["result"] not in RESULT_VALUES:
        problems.append(f"result must be one of {sorted(RESULT_VALUES)}")
    if event.get("source") and event["source"] not in SOURCES:
        problems.append(f"source must be one of {sorted(SOURCES)}")
    classification = event.get("privacy_classification")
    if classification and classification not in PRIVACY_CLASSIFICATIONS:
        problems.append(
            f"privacy_classification must be one of {sorted(PRIVACY_CLASSIFICATIONS)}"
        )
    occurred_at = event.get("occurred_at")
    if occurred_at is not None and not isinstance(occurred_at, datetime):
        problems.append("occurred_at must be a datetime")
    for field in ("exercise_version", "mapping_version"):
        if event.get(field) in (None, "") and event.get("exercise_id") is not None:
            # Versioning is required when an exercise is in scope. A missing
            # version contaminates the revision comparison the field exists for.
            problems.append(f"{field} is required when exercise_id is set")
    return problems


def missing_health_fields(payload: dict) -> list[str]:
    """Return Exercise Health fields absent from an API response."""
    return [field for field in EXERCISE_HEALTH_FIELDS if field not in payload]
