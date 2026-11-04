"""Smoke test for the unauthenticated health endpoint.

The endpoint runs a real SELECT 1 against the database and reports
readiness, so this test is meaningful only when TEST_DATABASE_URL points
at a reachable database (the CI job and the verify phase both provide one).
"""

import os

import pytest

from app.version import APP_VERSION, RELEASE_NAME


def test_version_endpoint_reports_build_identity(client):
    resp = client.get("/api/version")
    assert resp.status_code == 200
    assert resp.json() == {"version": APP_VERSION, "release": RELEASE_NAME}


@pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="health probe needs a reachable database",
)
def test_health_reports_db_up(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["database"] == "up"
