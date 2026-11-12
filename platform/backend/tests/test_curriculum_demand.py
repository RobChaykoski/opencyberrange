"""Curriculum-demand synthesis: topic demand, friction, and suppression."""

from __future__ import annotations

from app.services.curriculum_demand import build_curriculum_demand

DISCLAIMER_KEY = "disclaimer"


def _call(**overrides):
    payload = {
        "courses": [
            {
                "id": 1,
                "code": "CYB-101",
                "name": "Intro",
                "cohort_state": "available",
                "suppression": {},
            }
        ],
        "topics": [{"key": "osint", "label": "OSINT", "count": 12}],
        "exercises": [
            {
                "lab_id": 1,
                "lab_name": "OSINT basics",
                "track_name": "OSINT",
                "slug": "osint-1",
                "chapter_label": "OSINT foundations",
                "completion_rate": 30,
                "abandonment_rate": 55,
                "hint_pressure_rate": 70,
                "technical_failure_rate": 0,
                "median_attempts": 2,
                "sample_size": 8,
                "course": {"code": "CYB-101"},
            }
        ],
        "competency": {
            "state": "available",
            "cohort_size": 20,
            "domains": [
                {
                    "id": "OSINT",
                    "label": "OSINT",
                    "categories": [
                        {
                            "competencies": [
                                {
                                    "id": "OSINT-001",
                                    "name": "Collection",
                                    "state": "available",
                                    "coverage_pct": 10,
                                },
                                {
                                    "id": "OSINT-002",
                                    "name": "Verification",
                                    "state": "available",
                                    "coverage_pct": 25,
                                },
                            ]
                        }
                    ],
                }
            ],
        },
        "minimum": 5,
        "generated_at": "2026-11-11T00:00:00+00:00",
    }
    payload.update(overrides)
    return build_curriculum_demand(**payload)


def test_suppressed_courses_return_no_recommendations():
    result = _call(
        courses=[
            {
                "id": 1,
                "code": "SMALL",
                "name": "Small cohort",
                "cohort_state": "suppressed",
                "suppression": {"minimum_cohort_size": 5},
            }
        ]
    )

    assert result["state"] == "suppressed"
    assert result["recommendations"] == []
    assert result["courses_reporting"] == 0
    assert result[DISCLAIMER_KEY]


def test_topic_demand_compares_requests_with_supply():
    result = _call()
    topic = next(
        row for row in result["recommendations"] if row["kind"] == "topic_demand"
    )

    assert topic["area"] == "OSINT"
    assert topic["signal"] == 12
    assert topic["supply"] == 1
    assert topic["priority"] == "high"


def test_exercise_friction_is_flagged_with_sample_size():
    result = _call()
    friction = next(
        row for row in result["recommendations"] if row["kind"] == "exercise_friction"
    )

    assert friction["id"] == "friction-1"
    assert "n=8" in friction["rationale"]
    assert friction["priority"] in {"high", "medium"}


def test_competency_gap_requires_cohort_above_minimum():
    result = _call()
    gap = next(
        row for row in result["recommendations"] if row["kind"] == "competency_gap"
    )
    assert gap["area"] == "OSINT"
    assert "Collection" in gap["rationale"]

    suppressed = _call(
        competency={
            "state": "available",
            "cohort_size": 3,
            "domains": [
                {
                    "id": "OSINT",
                    "label": "OSINT",
                    "categories": [
                        {
                            "competencies": [
                                {
                                    "id": "OSINT-001",
                                    "name": "Collection",
                                    "state": "available",
                                    "coverage_pct": 10,
                                }
                            ]
                        }
                    ],
                }
            ],
        }
    )
    assert not any(
        row["kind"] == "competency_gap"
        for row in suppressed["recommendations"]
    )


def test_summary_counts_match_recommendations():
    result = _call()
    summary = result["summary"]
    kinds = [row["kind"] for row in result["recommendations"]]

    assert summary["topic_demand"] == kinds.count("topic_demand")
    assert summary["exercise_friction"] == kinds.count("exercise_friction")
    assert summary["competency_gap"] == kinds.count("competency_gap")
    assert summary["high"] + summary["medium"] + summary["low"] == len(kinds)
