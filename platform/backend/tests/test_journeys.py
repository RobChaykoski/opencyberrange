"""Learner journey catalogue and selection."""

from __future__ import annotations

import pytest

from app.models import LearnerJourney

pytestmark = pytest.mark.db


def test_catalogue_and_journey_selection(client, db_session, auth_headers, test_user):
    try:
        catalogue = client.get("/api/journeys", headers=auth_headers)
        assert catalogue.status_code == 200, catalogue.text
        body = catalogue.json()
        assert len(body["journeys"]) >= 10
        assert len(body["traditions"]) == 8
        tradition_titles = {item["title"] for item in body["traditions"]}
        assert tradition_titles == {
            "Protection",
            "Creation",
            "Discovery",
            "Stewardship",
            "Illumination",
            "Connection",
            "Service",
            "Judgment",
        }
        assert all(item["tradition"] in tradition_titles for item in body["journeys"])
        assert body["selected"] is None
        ids = {item["id"] for item in body["journeys"]}
        assert "defend-communities" in ids
        assert "secure-democracy" in ids

        chosen = client.put(
            "/api/journeys/mine",
            json={"journey_id": "defend-communities"},
            headers=auth_headers,
        )
        assert chosen.status_code == 200, chosen.text
        assert chosen.json()["journey"]["journey_id"] == "defend-communities"
        assert chosen.json()["journey"]["journey"]["identity"] == "The Defender"

        mine = client.get("/api/journeys/mine", headers=auth_headers)
        assert mine.status_code == 200
        assert mine.json()["journey"]["journey_id"] == "defend-communities"

        switched = client.put(
            "/api/journeys/mine",
            json={"journey_id": "hunt-adversaries"},
            headers=auth_headers,
        )
        assert switched.status_code == 200
        primary = (
            db_session.query(LearnerJourney)
            .filter(
                LearnerJourney.user_id == test_user.id,
                LearnerJourney.is_primary == True,
            )
            .all()
        )
        assert len(primary) == 1
        assert primary[0].journey_id == "hunt-adversaries"
    finally:
        db_session.query(LearnerJourney).filter(
            LearnerJourney.user_id == test_user.id
        ).delete(synchronize_session=False)
        db_session.commit()


def test_unknown_journey_is_rejected(client, auth_headers):
    response = client.put(
        "/api/journeys/mine",
        json={"journey_id": "not-a-journey"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.headers["X-Error-Code"] == "journey_invalid"


def test_journey_requires_authentication(client):
    assert client.get("/api/journeys").status_code == 401
