"""Competency coverage reports the Release 6 review backlog from data."""

from app.services.competency_coverage import coverage_summary


def test_coverage_summary_matches_the_contracts():
    summary = coverage_summary()
    assert summary["total"] == 214
    assert summary["reviewed"] == 25
    assert summary["pending"] == 189
    assert summary["reviewed"] + summary["pending"] == summary["total"]
    assert 0 < summary["coverage_percent"] < 100


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
