"""Career Atlas contracts: unlock states, role ladders, and salary sources."""

from __future__ import annotations

from app.services.career_explorer import (
    CAREER_ATLAS_VERSION,
    SALARY_SOURCES,
    build_career_atlas,
)


def _dna(offensive_evidence=6, defensive_evidence=1, **scores):
    dimensions = []
    for key in ("explorer", "builder", "tester", "defender", "investigator", "leader"):
        dimensions.append(
            {
                "key": key,
                "label": key.title(),
                "class_name": key.title(),
                "tier": "Practitioner",
                "score": scores.get(key, 0),
            }
        )
    affinities = [
        {
            "key": "offensive",
            "label": "Offensive Security / Penetration Testing",
            "evidence_level": "strong" if offensive_evidence >= 6 else "no_evidence",
            "evidence_count": offensive_evidence,
            "recommended": offensive_evidence > 0,
        },
        {
            "key": "defensive",
            "label": "Defensive Security / SOC",
            "evidence_level": "early" if defensive_evidence else "no_evidence",
            "evidence_count": defensive_evidence,
            "recommended": False,
        },
        {
            "key": "investigative",
            "label": "DFIR / Investigation",
            "evidence_level": "no_evidence",
            "evidence_count": 0,
            "recommended": False,
        },
        {
            "key": "leadership",
            "label": "Security Leadership / Education",
            "evidence_level": "no_evidence",
            "evidence_count": 0,
            "recommended": False,
        },
    ]
    return {"dimensions": dimensions, "affinities": affinities}


def test_empty_atlas_keeps_families_visible_and_locked():
    atlas = build_career_atlas(_dna(offensive_evidence=0, defensive_evidence=0))

    assert atlas["version"] == CAREER_ATLAS_VERSION
    assert len(atlas["branches"]) == 6
    assert len(atlas["families"]) == 11
    assert atlas["summary"]["unlocked"] == 0
    assert atlas["summary"]["locked"] == 11
    assert atlas["recommended_family_key"] is None
    assert all(row["unlock_state"] == "locked" for row in atlas["families"])
    assert all(row["roles"] for row in atlas["families"])


def test_atlas_unlocks_offensive_family_and_returns_salary_bands():
    atlas = build_career_atlas(_dna(tester=70, explorer=60))
    offensive = next(row for row in atlas["families"] if row["key"] == "offensive")

    assert offensive["unlock_state"] == "unlocked"
    assert offensive["recommended"] is True
    assert offensive["match_score"] == 86
    assert len(offensive["roles"]) >= 3

    salary = offensive["roles"][0]["salary"]
    assert salary["ca"]["currency"] == "CAD"
    assert salary["us"]["currency"] == "USD"
    assert salary["ca"]["low"] < salary["ca"]["median"] < salary["ca"]["high"]
    assert salary["us"]["low"] < salary["us"]["median"] < salary["us"]["high"]
    assert salary["ca"]["source_label"]
    assert salary["ca"]["as_of"]
    assert salary["us"]["source_label"]
    assert salary["us"]["as_of"]


def test_atlas_sources_are_tagged_and_disclaimed():
    atlas = build_career_atlas(_dna())

    assert set(SALARY_SOURCES) == {"ca_jobbank", "us_bls"}
    assert {source["key"] for source in atlas["sources"]} == {"ca_jobbank", "us_bls"}
    assert "not a job prediction" in atlas["disclaimer"]
    assert "not an offer" in atlas["salary_note"]


def test_atlas_accepts_a_next_lab_map():
    atlas = build_career_atlas(
        _dna(tester=70),
        next_labs={
            "tester": {
                "name": "Request Smuggling",
                "track_slug": "web",
                "difficulty": "intermediate",
            }
        },
    )
    tester = next(row for row in atlas["branches"] if row["key"] == "tester")
    assert tester["next_lab"]["name"] == "Request Smuggling"
    assert tester["next_lab"]["track_slug"] == "web"


def test_atlas_branch_scores_come_from_cyber_dna():
    atlas = build_career_atlas(_dna(defender=44, investigator=51))

    defender = next(row for row in atlas["branches"] if row["key"] == "defender")
    investigator = next(row for row in atlas["branches"] if row["key"] == "investigator")

    assert defender["score"] == 44
    assert investigator["score"] == 51
    assert defender["tier"] == "Practitioner"
