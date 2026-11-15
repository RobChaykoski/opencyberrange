"""Unit tests for the growth-velocity windows.

The service reads rows from the database, but the window maths is pure. These
tests use simple objects so the boundary handling, hint ratio, and difficulty
average stay covered without a database.
"""

from datetime import datetime, timedelta
from types import SimpleNamespace

from app.services.growth_velocity import summarise_completions, confidence_for

NOW = datetime(2026, 11, 15, 12, 0, 0)


def completion(days_ago: int, hints: int = 0, difficulty: str = "beginner"):
    return SimpleNamespace(
        completed_at=NOW - timedelta(days=days_ago),
        hints_used=hints,
        lab_difficulty_snapshot=difficulty,
        lab=None,
    )


def window(days: int) -> tuple[datetime, datetime]:
    end = NOW - timedelta(days=0 if days == 0 else days)
    return end - timedelta(days=30), end


def test_current_window_counts_completions_hints_and_difficulty():
    rows = [
        completion(2, hints=0, difficulty="intermediate"),
        completion(5, hints=2, difficulty="advanced"),
        completion(40, hints=3, difficulty="beginner"),
    ]
    start, end = window(0)
    result = summarise_completions(rows, start, end)

    assert result["completions"] == 2
    assert result["hints_per_completion"] == 1.0
    assert result["avg_difficulty"] == 2.5
    assert result["hint_free"] == 1
    assert result["active_days"] == 2


def test_prior_window_excludes_current_rows():
    rows = [
        completion(2),
        completion(45, hints=4),
        completion(50, hints=2),
    ]
    start = NOW - timedelta(days=60)
    end = NOW - timedelta(days=30)
    result = summarise_completions(rows, start, end)

    assert result["completions"] == 2
    assert result["hints_per_completion"] == 3.0


def test_empty_window_reports_zeroes():
    result = summarise_completions([], *window(0))

    assert result["completions"] == 0
    assert result["hints_per_completion"] == 0.0
    assert result["avg_difficulty"] == 0.0
    assert result["active_days"] == 0
    assert result["active_weeks"] == 0


def test_confidence_gates_percentages_and_career_roles():
    assert confidence_for(0)["level"] == "starting"
    assert confidence_for(2)["percent_ready"] is False
    assert confidence_for(3)["percent_ready"] is True
    assert confidence_for(3)["career_ready"] is False
    assert confidence_for(8)["career_ready"] is True
    assert confidence_for(15)["level"] == "established"
