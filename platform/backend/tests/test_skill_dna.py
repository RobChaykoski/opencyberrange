"""Skill DNA scores, titles, and profile API contracts."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.models import (
    Achievement,
    Competition,
    CompetitionParticipant,
    Course,
    CourseEnrollment,
    Lab,
    LabCompletion,
    LabSession,
    Level,
    Track,
)
from app.services.skill_dna import (
    build_skill_dna,
    skill_branch_for_lab,
    skill_branch_mix,
)
from app.services.titles import equip_title


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


@pytest.fixture(autouse=True)
def _cleanup_skill_dna(db_session, test_user):
    """Remove the graph this module creates before the shared user teardown."""
    yield
    user_id = test_user.id
    db_session.query(Achievement).filter(Achievement.user_id == user_id).delete(
        synchronize_session=False
    )
    db_session.query(LabSession).filter(LabSession.user_id == user_id).delete(
        synchronize_session=False
    )
    db_session.query(CompetitionParticipant).filter(
        CompetitionParticipant.user_id == user_id
    ).delete(synchronize_session=False)
    db_session.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == user_id
    ).delete(synchronize_session=False)
    db_session.query(Course).filter(Course.instructor_id == user_id).delete(
        synchronize_session=False
    )
    db_session.query(LabCompletion).filter(LabCompletion.user_id == user_id).delete(
        synchronize_session=False
    )

    track_ids = [
        row.id
        for row in db_session.query(Track).filter(Track.description == "skill-dna-test").all()
    ]
    if track_ids:
        level_ids = [
            row.id for row in db_session.query(Level).filter(Level.track_id.in_(track_ids)).all()
        ]
        if level_ids:
            db_session.query(Lab).filter(Lab.level_id.in_(level_ids)).delete(
                synchronize_session=False
            )
        db_session.query(Level).filter(Level.track_id.in_(track_ids)).delete(
            synchronize_session=False
        )
        db_session.query(Track).filter(Track.id.in_(track_ids)).delete(
            synchronize_session=False
        )

    db_session.query(Competition).filter(Competition.name == "Skill DNA Cup").delete(
        synchronize_session=False
    )
    db_session.commit()


def _track(db, name: str, slug: str) -> Track:
    track = Track(
        name=name,
        slug=f"{slug}-{_suffix()}",
        description="skill-dna-test",
        is_active=True,
        sequential=False,
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


def _lab(db, track: Track, *, name: str, category: str, difficulty: str = "intermediate") -> Lab:
    level = db.query(Level).filter(Level.track_id == track.id).first()
    if level is None:
        level = Level(track_id=track.id, level_number=1, name="Level 1")
        db.add(level)
        db.commit()
        db.refresh(level)
    lab = Lab(
        name=name,
        slug=f"{name.lower().replace(' ', '-')}-{_suffix()}",
        description="Synthetic Skill DNA lab",
        compose_file="services: {}\n",
        category=category,
        difficulty=difficulty,
        is_active=True,
        visibility="public",
        level_id=level.id,
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab


def _complete(db, user, lab: Lab, *, hints: int = 0, attempts: int = 1, minutes: int = 30):
    row = LabCompletion(
        user_id=user.id,
        lab_id=lab.id,
        flag_submitted="OCR{skill_dna_test}",
        attempts=attempts,
        hints_used=hints,
        time_spent_minutes=minutes,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    return row


def _seed_activity(db, user):
    forensics = _track(db, "Digital Forensics", "forensics")
    osint = _track(db, "OSINT", "osint")
    web = _track(db, "Web Application Security", "web")
    network = _track(db, "Network Security", "network")

    forensics_lab = _lab(
        db,
        forensics,
        name="Memory Analysis",
        category="forensics",
        difficulty="advanced",
    )
    osint_lab = _lab(db, osint, name="Open Source Trail", category="osint")
    web_lab = _lab(db, web, name="Request Smuggling", category="web")
    network_lab = _lab(db, network, name="Traffic Triage", category="network-analysis")

    _complete(db, user, forensics_lab, hints=0, attempts=1, minutes=45)
    _complete(db, user, osint_lab, hints=0, attempts=1, minutes=25)
    _complete(db, user, web_lab, hints=1, attempts=2, minutes=35)
    _complete(db, user, network_lab, hints=0, attempts=1, minutes=40)

    # An opened but unfinished lab counts toward exploration.
    unfinished = _lab(db, osint, name="Unfinished Trail", category="osint")
    db.add(
        LabSession(
            user_id=user.id,
            lab_id=unfinished.id,
            status="stopped",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
    )
    db.commit()

    for achievement_type in ("first_blood", "no_hints", "perfectionist"):
        db.add(
            Achievement(
                user_id=user.id,
                achievement_type=achievement_type,
                awarded_at=datetime.now(timezone.utc),
            )
        )
    db.commit()

    competition = Competition(
        name="Skill DNA Cup",
        start_at=datetime.now(timezone.utc) - timedelta(days=1),
        end_at=datetime.now(timezone.utc) + timedelta(days=1),
        is_active=True,
    )
    db.add(competition)
    db.commit()
    db.refresh(competition)
    db.add(CompetitionParticipant(competition_id=competition.id, user_id=user.id))

    course = Course(
        name="Skill DNA Course",
        code="DNA101",
        semester="2026F",
        invite_code=f"DNA-{_suffix()}",
        instructor_id=user.id,
        start_date=datetime.now(timezone.utc) - timedelta(days=1),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
        is_active=True,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    db.add(CourseEnrollment(course_id=course.id, user_id=user.id))
    db.commit()


def test_empty_profile_starts_at_recruit(db_session, test_user):
    dna = build_skill_dna(db_session, test_user)

    assert dna["class"]["label"] == "Recruit"
    assert dna["overall"] == 0
    assert all(row["score"] == 0 for row in dna["dimensions"])
    assert dna["titles"]["equipped"]["label"] == "Recruit"
    assert dna["titles"]["titles"][0]["unlocked"] is True


def test_skill_dna_scores_and_class(db_session, test_user):
    _seed_activity(db_session, test_user)

    dna = build_skill_dna(db_session, test_user)
    scores = {row["key"]: row["score"] for row in dna["dimensions"]}

    assert dna["formula_version"] == "2026.12"
    assert scores["explorer"] > 0
    assert scores["builder"] > 0
    assert scores["tester"] > 0
    assert scores["defender"] > 0
    assert scores["investigator"] > 0
    assert scores["leader"] > 0
    assert dna["class"]["key"] in {"explorer", "builder", "tester", "defender", "investigator", "leader"}
    assert dna["class"]["class_name"] in {"Pathfinder", "Artificer", "Assessor", "Warden", "Seeker", "Commander"}
    assert dna["overall"] > 0
    assert all(0 <= score <= 100 for score in scores.values())
    for row in dna["dimensions"]:
        assert row["tier"] != "Unranked"
        assert row["evidence"]
        assert row["next_step"]
        assert row["certification_key"]

    affinities = {row["key"]: row for row in dna["affinities"]}
    assert set(affinities) == {"offensive", "defensive", "investigative", "leadership"}
    assert any(row["recommended"] for row in dna["affinities"])
    assert all(
        row["evidence_level"] in {"no_evidence", "early", "growing", "strong"}
        for row in dna["affinities"]
    )


def test_offensive_affinity_recognises_pentest_practice(db_session, test_user):
    web = _track(db_session, "Web Application Security", "web")
    for index, category in enumerate(
        [
            "reconnaissance",
            "exploitation",
            "privilege-escalation",
            "post-exploitation",
            "credential-attacks",
        ]
    ):
        lab = _lab(
            db_session,
            web,
            name=f"Offensive Practice {index}",
            category=category,
        )
        _complete(db_session, test_user, lab, hints=0, attempts=1, minutes=30)

    dna = build_skill_dna(db_session, test_user)
    offensive = next(
        row for row in dna["affinities"] if row["key"] == "offensive"
    )

    assert offensive["evidence_level"] in {"growing", "strong"}
    assert offensive["recommended"] is True
    assert "core offensive labs" in offensive["evidence"]
    assert "Penetration tester" in offensive["roles"]
    assert offensive["next_step"]


def test_titles_unlock_and_equip(db_session, test_user):
    _seed_activity(db_session, test_user)

    dna = build_skill_dna(db_session, test_user)
    titles = {row["key"]: row for row in dna["titles"]["titles"]}

    assert titles["first_blood"]["unlocked"] is True
    assert titles["self_reliant"]["unlocked"] is True
    assert titles["perfectionist"]["unlocked"] is True
    assert titles["champion"]["unlocked"] is False

    equip_title(db_session, test_user, "first_blood")
    dna = build_skill_dna(db_session, test_user)
    assert dna["titles"]["equipped"]["key"] == "first_blood"
    assert dna["titles"]["equipped"]["label"] == "First Blood"

    equip_title(db_session, test_user, None)
    dna = build_skill_dna(db_session, test_user)
    assert dna["titles"]["equipped"]["key"] == "class"

    with pytest.raises(ValueError):
        equip_title(db_session, test_user, "champion")


def test_profile_summary_includes_skill_dna(client, auth_headers, db_session, test_user):
    _seed_activity(db_session, test_user)

    resp = client.get("/api/profile/summary", headers=auth_headers)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["skill_dna"]["overall"] > 0
    assert len(body["skill_dna"]["dimensions"]) == 6
    assert len(body["skill_dna"]["affinities"]) == 4
    assert body["skill_dna"]["titles"]["titles"]
    assert body["user"]["equipped_title"]["key"] in {"class", "first_blood"}


def test_career_dossier_api_and_exports(client, auth_headers, db_session, test_user):
    _seed_activity(db_session, test_user)

    resp = client.get("/api/profile/career-dossier", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["identity"]["username"] == test_user.username
    assert len(body["cyber_dna"]["affinities"]) == 4
    assert body["learning"]["completed_exercises"] >= 1
    assert body["recommended_next_steps"]
    assert any(
        "hackthebox" in resource["url"].lower()
        for resource in body["external_resources"]
    )

    markdown = client.get("/api/profile/career-dossier.md", headers=auth_headers)
    assert markdown.status_code == 200, markdown.text
    assert "Career profile:" in markdown.text
    assert markdown.headers["cache-control"] == "no-store"

    html = client.get("/api/profile/career-dossier.html", headers=auth_headers)
    assert html.status_code == 200, html.text
    assert "text/html" in html.headers["content-type"]
    assert "Practice affinities" in html.text
    assert html.headers["cache-control"] == "no-store"


def test_title_api_equips_and_rejects_locked(client, auth_headers, db_session, test_user):
    _seed_activity(db_session, test_user)

    ok = client.put(
        "/api/profile/title",
        headers=auth_headers,
        json={"title": "first_blood"},
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["equipped_title"] == "first_blood"

    locked = client.put(
        "/api/profile/title",
        headers=auth_headers,
        json={"title": "champion"},
    )
    assert locked.status_code == 400

    cleared = client.put(
        "/api/profile/title",
        headers=auth_headers,
        json={"title": None},
    )
    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["equipped_title"] is None


def test_skill_branch_mapping_and_mix():
    counter = {"id": 0}

    def lab(category, difficulty="beginner", track="web"):
        counter["id"] += 1
        return SimpleNamespace(
            id=counter["id"],
            category=category,
            difficulty=difficulty,
            level=SimpleNamespace(track=SimpleNamespace(slug=track)),
        )

    assert skill_branch_for_lab(lab("reconnaissance")) == "explorer"
    assert skill_branch_for_lab(lab("web")) == "tester"
    assert skill_branch_for_lab(lab("assessment")) == "tester"
    assert skill_branch_for_lab(lab("forensics")) == "investigator"
    assert skill_branch_for_lab(lab("network-analysis")) == "defender"
    assert skill_branch_for_lab(lab("ot")) == "defender"
    assert skill_branch_for_lab(lab("web", difficulty="advanced")) == "tester"
    assert skill_branch_for_lab(lab("forensics", difficulty="advanced")) == "leader"

    labs = [
        lab("reconnaissance"),
        lab("web"),
        lab("forensics"),
        lab("network-analysis"),
        lab("web", difficulty="advanced"),
    ]
    completions = [
        SimpleNamespace(lab=labs[1]),
        SimpleNamespace(lab=labs[1]),
        SimpleNamespace(lab=labs[2]),
    ]
    mix = skill_branch_mix(labs, completions)
    by_key = {row["key"]: row for row in mix["dimensions"]}

    assert mix["assigned_total"] == 5
    assert mix["completed_total"] == 2
    assert mix["completion_pct"] == 40.0
    assert by_key["tester"]["assigned"] == 2
    assert by_key["tester"]["completed"] == 1
    assert by_key["builder"]["assigned"] == 0
    assert by_key["investigator"]["completed"] == 1
    assert by_key["explorer"]["assigned_pct"] == 20.0
