"""Career readiness data and GPS scoring helpers.

These tests stay off the database so they run without TEST_DATABASE_URL.
"""

from __future__ import annotations

from app.services.competency_taxonomy import load_taxonomy
from app.services.cyber_gps import _fit_label, _interest_scores, _valid_answers, load_gps
from app.services.role_readiness import (
    _colour,
    _coverage_colour,
    _rating,
    _status,
    load_roles,
    roles_catalogue,
)


def _competency_ids() -> set[str]:
    taxonomy = load_taxonomy()
    return {
        competency["id"]
        for domain in taxonomy.get("domains", [])
        for category in domain.get("categories", [])
        for competency in category.get("competencies", [])
    }


def test_roles_catalogue_has_five_flagship_pathways():
    catalogue = roles_catalogue()
    assert len(catalogue["roles"]) >= 13
    flagship = [role for role in catalogue["roles"] if role["flagship"]]
    assert len(flagship) == 5
    assert {role["id"] for role in flagship} >= {
        "cybersecurity-foundations",
        "soc-analyst",
    }
    assert catalogue["readiness_model"]["components"]


def test_every_critical_competency_exists_in_taxonomy():
    known = _competency_ids()
    missing = [
        (role["id"], competency_id)
        for role in load_roles().get("pathways", [])
        for competency_id in role.get("critical_competencies", [])
        if competency_id not in known
    ]
    assert missing == []


def test_level_requirements_reference_real_domains():
    taxonomy = load_taxonomy()
    domains = {domain["id"] for domain in taxonomy.get("domains", [])}
    bad = [
        (role["id"], domain)
        for role in load_roles().get("pathways", [])
        for domain in role.get("level_requirements", {})
        if domain not in domains
    ]
    assert bad == []


def test_readiness_status_and_colour_thresholds():
    assert _status(None, 60, False) == "no_evidence"
    assert _status(80, 60, True) == "have"
    assert _status(80, 60, False) == "building"
    assert _status(30, 60, False) == "gap"

    assert _colour(None, 60) == "grey"
    assert _colour(60, 60) == "green"
    assert _colour(45, 60) == "amber"
    assert _colour(20, 60) == "red"

    assert _coverage_colour(90) == "green"
    assert _coverage_colour(70) == "amber"
    assert _coverage_colour(30) == "red"


def test_rating_scale_covers_zero_to_one_hundred():
    assert _rating(0)["label"] == "Not Ready"
    assert _rating(100)["label"] == "Highly Prepared"
    assert _rating(85)["label"] == "Career Ready"


def test_gps_answers_are_validated_and_scored():
    valid = _valid_answers(
        {"work": "triage", "environment": "not-a-real-option", "time": "medium"}
    )
    assert valid == {"work": "triage", "time": "medium"}

    scores = _interest_scores(valid)
    assert scores["soc-analyst"] > 0
    assert scores.get("penetration-tester", 0) == 0


def test_gps_has_optional_questions_and_pace_guidance():
    gps = load_gps()
    questions = gps.get("questions", [])
    assert len(questions) >= 4
    assert all(question.get("options") for question in questions)
    assert gps.get("pace")


def test_gps_fit_labels_are_encouraging_not_absolute():
    assert _fit_label(90) == ("Strong fit", "green")
    assert _fit_label(60) == ("Worth exploring", "amber")
    assert _fit_label(20) == ("Stretch direction", "red")
