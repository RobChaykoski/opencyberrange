"""Momentum and friction contracts for the advanced DNA insights layer."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.models import Lab, LabCompletion, LabSession, Level, Track
from app.services.skill_momentum import MOMENTUM_VERSION, build_momentum


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


def _track(db, name: str, slug: str) -> Track:
    track = Track(
        name=name,
        slug=f"{slug}-{_suffix()}",
        description="skill-momentum-test",
        is_active=True,
        sequential=False,
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


def _lab(
    db,
    track: Track,
    *,
    name: str,
    category: str,
    difficulty: str = "intermediate",
    duration: int = 60,
) -> Lab:
    level = db.query(Level).filter(Level.track_id == track.id).first()
    if level is None:
        level = Level(track_id=track.id, level_number=1, name="Level 1")
        db.add(level)
        db.commit()
        db.refresh(level)
    lab = Lab(
        name=name,
        slug=f"{name.lower().replace(' ', '-')}-{_suffix()}",
        description="Synthetic Momentum lab",
        compose_file="services: {}\n",
        category=category,
        difficulty=difficulty,
        duration_minutes=duration,
        is_active=True,
        visibility="public",
        level_id=level.id,
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab


def _complete(
    db,
    user,
    lab: Lab,
    *,
    hints: int = 0,
    attempts: int = 1,
    minutes: int = 30,
    completed_at: datetime | None = None,
):
    row = LabCompletion(
        user_id=user.id,
        lab_id=lab.id,
        flag_submitted="OCR{momentum_test}",
        attempts=attempts,
        hints_used=hints,
        time_spent_minutes=minutes,
        completed_at=completed_at or datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    return row


def _start(db, user, lab: Lab):
    db.add(
        LabSession(
            user_id=user.id,
            lab_id=lab.id,
            status="stopped",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
    )
    db.commit()


def _cleanup(db, user, tracks: list[Track]):
    user_id = user.id
    db.query(LabSession).filter(LabSession.user_id == user_id).delete(
        synchronize_session=False
    )
    db.query(LabCompletion).filter(LabCompletion.user_id == user_id).delete(
        synchronize_session=False
    )
    track_ids = [track.id for track in tracks]
    if track_ids:
        level_ids = [
            row.id
            for row in db.query(Level).filter(Level.track_id.in_(track_ids)).all()
        ]
        if level_ids:
            db.query(Lab).filter(Lab.level_id.in_(level_ids)).delete(
                synchronize_session=False
            )
        db.query(Level).filter(Level.track_id.in_(track_ids)).delete(
            synchronize_session=False
        )
        db.query(Track).filter(Track.id.in_(track_ids)).delete(
            synchronize_session=False
        )
    db.commit()


def test_empty_momentum_reports_no_evidence(db_session, test_user):
    momentum = build_momentum(db_session, test_user)

    assert momentum["version"] == MOMENTUM_VERSION
    assert momentum["summary"]["completed"] == 0
    assert momentum["summary"]["started"] == 0
    assert all(row["status"] == "no_evidence" for row in momentum["branches"])
    assert momentum["stuck_points"] == []
    assert "first evidence" in momentum["next_move"]


def test_momentum_flags_friction_and_stuck_points(db_session, test_user):
    tracks = []
    try:
        web = _track(db_session, "Web Application Security", "web")
        tracks.append(web)
        hard = _lab(
            db_session,
            web,
            name="Hard Request Smuggling",
            category="web",
            duration=60,
        )
        unfinished = _lab(
            db_session,
            web,
            name="Unfinished Enumeration",
            category="web",
            duration=45,
        )
        _complete(
            db_session,
            test_user,
            hard,
            hints=3,
            attempts=4,
            minutes=140,
        )
        _start(db_session, test_user, unfinished)

        momentum = build_momentum(db_session, test_user)
        tester = next(row for row in momentum["branches"] if row["key"] == "tester")

        assert tester["status"] == "friction"
        assert tester["completed"] == 1
        assert tester["started"] == 2
        assert tester["unfinished"] == 1
        assert tester["hint_rate"] == 100.0
        assert tester["first_attempt_rate"] == 0.0
        assert tester["friction_score"] >= 55
        assert len(momentum["stuck_points"]) == 2
        assert any("Started but not finished" in row["reason"] for row in momentum["stuck_points"])
        assert any("High hint use" in row["reason"] for row in momentum["stuck_points"])
        assert tester["next_lab"]["name"] == "Unfinished Enumeration"
        assert tester["next_lab"]["track_slug"] == web.slug
    finally:
        _cleanup(db_session, test_user, tracks)


def test_momentum_reports_gaining_when_recent_work_is_clean(db_session, test_user):
    tracks = []
    try:
        network = _track(db_session, "Network Security", "network")
        tracks.append(network)
        now = datetime.now(timezone.utc)
        labs = [
            _lab(
                db_session,
                network,
                name=f"Traffic Analysis {index}",
                category="network-analysis",
                duration=60,
            )
            for index in range(4)
        ]
        # Earlier work used hints and retries; recent work is clean.
        _complete(db_session, test_user, labs[0], hints=2, attempts=3, minutes=90, completed_at=now - timedelta(days=4))
        _complete(db_session, test_user, labs[1], hints=2, attempts=2, minutes=90, completed_at=now - timedelta(days=3))
        _complete(db_session, test_user, labs[2], hints=0, attempts=1, minutes=60, completed_at=now - timedelta(days=2))
        _complete(db_session, test_user, labs[3], hints=0, attempts=1, minutes=55, completed_at=now - timedelta(days=1))

        momentum = build_momentum(db_session, test_user)
        defender = next(row for row in momentum["branches"] if row["key"] == "defender")

        assert defender["completed"] == 4
        assert defender["movement"]["delta"] == 100.0
        assert defender["status"] == "gaining"
        assert momentum["gaining"]
    finally:
        _cleanup(db_session, test_user, tracks)
