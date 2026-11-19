"""Pure unit checks for the pilot readiness formulas."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.services.readiness_dashboard import (
    _band,
    _build_lab_health,
    _case_payload,
    _confidence,
    _login_risk,
    _performance_risk,
    _weighted_available,
)


def test_band_thresholds():
    assert _band(100)[0] == "critical_intervention"
    assert _band(85)[0] == "critical_intervention"
    assert _band(84)[0] == "high_risk"
    assert _band(70)[0] == "high_risk"
    assert _band(50)[0] == "elevated"
    assert _band(30)[0] == "monitor"
    assert _band(29)[0] == "healthy"


def test_weighted_average_renormalises_missing_values():
    value = _weighted_available(
        {"a": 80, "b": None, "c": 40},
        {"a": 0.5, "b": 0.3, "c": 0.2},
    )
    assert value == 68.6


def test_login_risk_bands():
    assert _login_risk(0) == 0
    assert _login_risk(3) == 0
    assert _login_risk(5) == 25
    assert _login_risk(12) == 60
    assert _login_risk(20) == 100


def test_performance_risk_inverts_success_scores():
    risk, provisional = _performance_risk(
        completed=5,
        started=10,
        assigned=10,
        reattempt_rate=50,
        quiz_average=50,
    )
    assert risk == 50.0
    assert provisional is False


def test_confidence_requires_evidence():
    assert _confidence(
        {
            "performance": 1,
            "engagement": 2,
            "progression": 3,
            "competency": 4,
            "behavioural": 5,
            "infrastructure": 6,
        },
        5,
    ) == "high"
    assert _confidence(
        {
            "performance": 1,
            "engagement": 2,
            "progression": 3,
            "competency": None,
            "behavioural": 5,
            "infrastructure": 6,
        },
        5,
    ) == "medium"
    assert _confidence(
        {
            "performance": 1,
            "engagement": None,
            "progression": None,
            "competency": None,
            "behavioural": 5,
            "infrastructure": 6,
        },
        1,
    ) == "low"


def _lab(lab_id: int, name: str):
    return SimpleNamespace(
        id=lab_id,
        name=name,
        slug=f"lab-{lab_id}",
        difficulty="beginner",
        level=SimpleNamespace(
            name="Level 1",
            track=SimpleNamespace(name="Track"),
        ),
    )


def _session(user_id: int, lab_id: int):
    return SimpleNamespace(user_id=user_id, lab_id=lab_id, started_at=None)


def _completion(user_id: int, lab_id: int):
    return SimpleNamespace(
        user_id=user_id,
        lab_id=lab_id,
        hints_used=0,
        time_spent_minutes=30,
    )


def _case_note(*, state: str, follow_up_at: datetime | None):
    return SimpleNamespace(
        id=1,
        state=state,
        owner_id=7,
        priority="high",
        follow_up_at=follow_up_at,
        note="Case note",
        outcome=None,
        created_by_id=2,
        created_at=datetime(2026, 11, 19, 12, tzinfo=timezone.utc),
    )


def test_case_payload_marks_overdue_and_due_soon():
    now = datetime(2026, 11, 19, 12, tzinfo=timezone.utc)
    overdue = _case_payload(
        _case_note(state="open", follow_up_at=now - timedelta(days=1)),
        {7: "Ada Instructor"},
        now,
    )
    assert overdue["is_open"] is True
    assert overdue["owner_name"] == "Ada Instructor"
    assert overdue["overdue"] is True
    assert overdue["due_soon"] is False

    due_soon = _case_payload(
        _case_note(state="open", follow_up_at=now + timedelta(days=2)),
        {7: "Ada Instructor"},
        now,
    )
    assert due_soon["overdue"] is False
    assert due_soon["due_soon"] is True

    closed = _case_payload(
        _case_note(state="closed", follow_up_at=now - timedelta(days=1)),
        {7: "Ada Instructor"},
        now,
    )
    assert closed["is_open"] is False
    assert closed["overdue"] is False


def test_lab_health_distinguishes_no_data_and_degraded():
    labs = [_lab(1, "Healthy lab"), _lab(2, "Degraded lab"), _lab(3, "No data lab")]
    sessions = []
    completions = []
    for user_id in range(5):
        sessions.append(_session(user_id, 1))
        completions.append(_completion(user_id, 1))
        sessions.append(_session(user_id, 2))
    completions.append(_completion(0, 2))
    for user_id in range(2):
        sessions.append(_session(user_id, 3))

    health = _build_lab_health(labs, completions, sessions)
    by_name = {row["name"]: row for row in health["labs"]}

    assert by_name["Healthy lab"]["status"] == "healthy"
    assert by_name["Degraded lab"]["status"] == "degraded"
    assert by_name["No data lab"]["status"] == "no_data"
    assert health["counts"] == {"degraded": 1, "warning": 0, "no_data": 1, "healthy": 1}
