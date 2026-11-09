"""The analytics event and Exercise Health contracts stay explicit."""

from datetime import datetime, timezone

from app.services.analytics_schema import (
    ANALYTICS_SCHEMA_VERSION,
    EXERCISE_HEALTH_FIELDS,
    HEALTH_STATUSES,
    missing_health_fields,
    validate_event,
)


def _event(**overrides):
    event = {
        "event_id": "evt-1",
        "pseudonymous_user_id": "hash-abc",
        "course_id": 1,
        "cohort_id": "CS101-2026F",
        "exercise_id": 42,
        "exercise_version": "1.2.0",
        "mapping_version": "2026.1",
        "occurred_at": datetime.now(timezone.utc),
        "attempt_id": "attempt-1",
        "event_type": "exercise_completed",
        "result": "completed",
        "platform_version": "2.5.3",
        "source": "learner",
        "privacy_classification": "pseudonymous",
    }
    event.update(overrides)
    return event


def test_schema_version_is_declared():
    assert ANALYTICS_SCHEMA_VERSION


def test_complete_event_passes():
    assert validate_event(_event()) == []


def test_event_requires_versions_when_exercise_is_set():
    problems = validate_event(_event(exercise_version=None, mapping_version=None))
    assert "exercise_version is required when exercise_id is set" in problems
    assert "mapping_version is required when exercise_id is set" in problems


def test_event_rejects_unknown_event_type():
    assert any("event_type" in problem for problem in validate_event(_event(event_type="mystery")))


def test_health_status_model_has_four_states():
    assert HEALTH_STATUSES == {"green", "amber", "red", "grey"}


def test_missing_health_fields_lists_gaps():
    payload = {field: None for field in EXERCISE_HEALTH_FIELDS if field != "lab_version"}
    assert missing_health_fields(payload) == ["lab_version"]
