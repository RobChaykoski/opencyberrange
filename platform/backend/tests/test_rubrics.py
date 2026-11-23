"""The rubric registry is versioned data and validates before use."""

from app.services.rubrics import (
    get_rubric,
    load_rubrics,
    rubric_reference,
    validate_rubrics,
)


def test_rubric_registry_loads():
    rubrics = load_rubrics()
    assert {"blue-team-timeline", "vulnerability-report", "capstone-brief"} <= set(rubrics)


def test_rubric_versions_are_addressable():
    assert get_rubric("blue-team-timeline", "1.0") is not None
    assert get_rubric("blue-team-timeline", "9.9") is None
    assert get_rubric("missing") is None


def test_rubric_weights_sum_to_one():
    for document in load_rubrics().values():
        total = sum(float(item["weight"]) for item in document["criteria"])
        assert abs(total - 1.0) < 1e-6, document["rubric"]


def test_rubric_reference_is_safe_for_evidence():
    reference = rubric_reference("vulnerability-report", "1.0")
    assert reference is not None
    assert reference["rubric"] == "vulnerability-report"
    assert reference["version"] == "1.0"
    assert "artifact" in reference["evidence_types"]


def test_registry_validates():
    assert validate_rubrics() == []
