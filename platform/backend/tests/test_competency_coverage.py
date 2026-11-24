"""Competency coverage reports the Release 6 review backlog from data."""

from app.services.competency_coverage import (
    build_review_packet,
    coverage_summary,
    pending_contracts,
    release6_audit,
)


def test_coverage_summary_matches_the_contracts():
    summary = coverage_summary()
    assert summary["total"] == 215
    assert summary["reviewed"] == 25
    assert summary["pending"] == 190
    assert summary["reviewed"] + summary["pending"] == summary["total"]
    assert 0 < summary["coverage_percent"] < 100


def test_release6_audit_has_no_structural_mapping_gaps():
    audit = release6_audit()
    assert audit["labs"]["total"] == 215
    assert audit["labs"]["contracts"] == 215
    assert audit["labs"]["missing_contract"] == []
    assert audit["labs"]["missing_competencies"] == []
    assert audit["labs"]["unknown_competencies"] == []
    assert audit["labs"]["bad_weights"] == []
    assert audit["quiz_pathways"]["total"] == 9
    assert audit["quiz_pathways"]["mapped"] == 9
    assert audit["quiz_pathways"]["unmapped"] == []
    assert audit["exercise_quizzes"]["without_contract"] == []
    assert audit["structural_gaps"] is False
    assert audit["foundation_ready"] is False  # 190 contracts still pending
    assert audit["release_6_ready"] is False


def test_review_packet_names_the_contract_and_the_checklist():
    packet = build_review_packet("ai-1-1-prompt-injection-basics")
    assert "# Contract review: ai-1-1-prompt-injection-basics" in packet
    assert "AI-001" in packet
    assert "Review checklist" in packet
    assert "does not change the contract" in packet


def test_pending_contracts_filter_by_track():
    rows = pending_contracts("AI")
    assert len(rows) == 5
    assert {row["track"] for row in rows} == {"AI"}
    assert all(row["review_status"] != "reviewed" for row in rows)



def test_track_counts_add_up():
    summary = coverage_summary()
    assert sum(item["total"] for item in summary["tracks"]) == summary["total"]
    assert sum(item["pending"] for item in summary["tracks"]) == summary["pending"]


def test_pending_labs_are_limited_and_labelled():
    summary = coverage_summary()
    assert 1 <= len(summary["pending_labs"]) <= 25
    for lab in summary["pending_labs"]:
        assert lab["slug"]
        assert lab["track"]
        assert lab["status"] != "reviewed"
