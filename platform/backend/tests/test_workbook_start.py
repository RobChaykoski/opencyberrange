"""Workbook cards open the current exercise, or the first one, per track."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models import Lab, LabCompletion, LabSession, Level, Track

pytestmark = pytest.mark.db


def _make_track(db_session):
    suffix = uuid.uuid4().hex[:8]
    track = Track(
        name=f"Workbook Start {suffix}",
        slug=f"wbstart-{suffix}",
        is_active=True,
    )
    db_session.add(track)
    db_session.flush()
    level = Level(track_id=track.id, level_number=1, name="Start")
    db_session.add(level)
    db_session.flush()
    labs = []
    for index in (1, 2):
        lab = Lab(
            name=f"Start Lab {index}",
            slug=f"wbstart-{suffix}-{index}",
            level_id=level.id,
            sort_order=index,
            is_active=True,
            visibility="public",
            compose_file="services: {}\n",
            workbook=f"wiki/range/wbstart-{suffix}/CH/0{index}/",
        )
        db_session.add(lab)
        labs.append(lab)
    db_session.commit()
    for lab in labs:
        db_session.refresh(lab)
    return track, labs


def _card(client, headers, slug):
    resp = client.get("/api/exercises/workbooks", headers=headers)
    assert resp.status_code == 200, resp.text
    return next(w for w in resp.json()["workbooks"] if w["slug"] == slug)


def test_workbook_card_starts_at_first_then_current_exercise(
    client, db_session, test_user, auth_headers
):
    track, labs = _make_track(db_session)
    try:
        card = _card(client, auth_headers, track.slug)
        assert card["start_url"] == labs[0].workbook.replace("wiki/", "/wiki/")
        assert card["started"] is False

        db_session.add(
            LabCompletion(
                user_id=test_user.id,
                lab_id=labs[0].id,
                flag_submitted="OCR{test}",
                completed_at=datetime.now(timezone.utc),
            )
        )
        db_session.commit()

        card = _card(client, auth_headers, track.slug)
        assert card["start_url"] == labs[1].workbook.replace("wiki/", "/wiki/")
        assert card["started"] is True

        # A running session wins even when the sequential pointer disagrees.
        db_session.add(
            LabSession(
                user_id=test_user.id,
                lab_id=labs[0].id,
                status="running",
                started_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            )
        )
        db_session.commit()

        card = _card(client, auth_headers, track.slug)
        assert card["start_url"] == labs[0].workbook.replace("wiki/", "/wiki/")
    finally:
        db_session.query(LabSession).filter(
            LabSession.user_id == test_user.id,
            LabSession.lab_id.in_([lab.id for lab in labs]),
        ).delete(synchronize_session=False)
        db_session.query(LabCompletion).filter(
            LabCompletion.user_id == test_user.id,
            LabCompletion.lab_id.in_([lab.id for lab in labs]),
        ).delete(synchronize_session=False)
        db_session.query(Lab).filter(Lab.id.in_([lab.id for lab in labs])).delete(
            synchronize_session=False
        )
        db_session.query(Level).filter(Level.track_id == track.id).delete(
            synchronize_session=False
        )
        db_session.query(Track).filter(Track.id == track.id).delete(
            synchronize_session=False
        )
        db_session.commit()
