"""Cyber Discovery event layer: plan, block progress, and certificate serial."""

from __future__ import annotations

from types import SimpleNamespace

from app.services import devfest
from app.services.event_certificates import event_certificate_serial


def test_plan_loads_with_sessions_and_career_stories():
    plan = devfest.load_plan()
    assert plan["event"]["name"].startswith("GDG Windsor DevFest 2027")
    assert len(plan["sessions"]) == 2
    assert plan["career_stories"]["stories"]
    assert plan["privacy"]


def test_plan_for_experience_only_matches_the_devfest_key():
    assert devfest.plan_for_experience("devfest-2027") is not None
    assert devfest.plan_for_experience("something-else") is None


def test_block_progress_marks_completed_labs():
    block = {
        "id": "packet-detective",
        "title": "Packet Detective",
        "scenario": "A capture is the only evidence.",
        "competencies": ["NET-021"],
        "measures": ["Observation"],
        "career_paths": ["soc-analyst"],
        "lab_slugs": ["network-1-1-packet-capture-analysis", "network-1-2-http-traffic-analysis"],
    }
    labs = {
        "network-1-1-packet-capture-analysis": SimpleNamespace(
            name="Suspicious Traffic Analysis"
        ),
        "network-1-2-http-traffic-analysis": SimpleNamespace(
            name="HTTP Traffic Analysis"
        ),
    }
    progress = devfest._block_progress(
        block, labs, {"network-1-1-packet-capture-analysis"}
    )
    assert progress["completed"] is True
    assert progress["completed_labs"] == 1
    assert progress["total_labs"] == 2
    assert progress["labs"][0]["completed"] is True
    assert progress["labs"][1]["completed"] is False


def test_block_progress_ignores_labs_not_in_the_event():
    block = {
        "id": "find-the-person",
        "title": "Find the Person",
        "lab_slugs": ["osint-1-3-exif-metadata", "missing-lab"],
        "competencies": [],
    }
    labs = {"osint-1-3-exif-metadata": SimpleNamespace(name="EXIF Metadata")}
    progress = devfest._block_progress(block, labs, set())
    assert progress["total_labs"] == 1
    assert progress["completed"] is False


def test_discovery_certificate_serial_is_event_scoped():
    serial = event_certificate_serial(42, 7, "discovery")
    assert serial is not None
    assert serial.startswith("DVF-CYBER-2027-")
    assert len(serial.split("-")[-1]) == 5
    assert serial == event_certificate_serial(42, 7, "discovery")


def test_other_event_awards_have_no_devfest_serial():
    assert event_certificate_serial(42, 7, "participation") is None


def test_plan_summary_exposes_the_event_achievement():
    summary = devfest.plan_summary(devfest.load_plan())
    assert summary["achievement"]["type"] == "devfest_2027_discovery"
    assert summary["achievement"]["label"] == "DevFest Cyber Discovery"
    assert summary["outputs"]["learner"]
