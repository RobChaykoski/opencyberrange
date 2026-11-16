"""Central consent middleware: one gate before derived-data services run."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.consent import service
from app.consent.middleware import consent_enforcement, consent_type_for_path

pytestmark = pytest.mark.db


@pytest.fixture(autouse=True)
def _ledger(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "CONSENT_SUPPRESSION_PATH", str(tmp_path / "consent-suppression.jsonl")
    )


def _app():
    app = FastAPI()
    app.middleware("http")(consent_enforcement)

    @app.get("/api/dna/test")
    def dna_test():
        return {"ok": True}

    @app.get("/api/profile/gps/test")
    def gps_test():
        return {"ok": True}

    @app.get("/api/health")
    def health():
        return {"ok": True}

    return TestClient(app)


def test_consent_path_matrix_is_explicit_and_prefix_safe():
    assert consent_type_for_path("/api/dna/v3/evidence") == "cyber_dna"
    assert consent_type_for_path("/api/dna") == "cyber_dna"
    assert consent_type_for_path("/api/profile/skill-dna") == "cyber_dna"
    assert consent_type_for_path("/api/profile/gps") == "cyber_gps"
    assert consent_type_for_path("/api/profile/role-readiness") == "cyber_gps"
    assert consent_type_for_path("/api/profile/portfolio.md") == "portfolio"
    assert consent_type_for_path("/api/profile/snapshots/1") == "portfolio"
    assert consent_type_for_path("/api/coach/chat") == "ai_coach"
    assert consent_type_for_path("/api/research/export") == "research"
    assert consent_type_for_path("/api/consent/") is None
    assert consent_type_for_path("/api/dnaevil") is None
    assert consent_type_for_path("/api/health") is None


def test_middleware_blocks_revoked_feature_before_the_route(
    db_session, test_user, auth_headers
):
    service.revoke(db_session, test_user.id, "cyber_dna")
    client = _app()

    response = client.get("/api/dna/test", headers=auth_headers)

    assert response.status_code == 403
    assert response.headers["x-consent-status"] in {
        "revoked",
        "revocation_in_progress",
    }
    body = response.json()
    assert body["error"] == "ConsentRequired"
    assert body["consent_type"] == "cyber_dna"
    assert "Privacy and consent" in body["detail"]

    # A different domain is unaffected while only DNA is revoked.
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/profile/gps/test", headers=auth_headers).status_code == 200


def test_middleware_allows_regranted_feature(db_session, test_user, auth_headers):
    service.revoke(db_session, test_user.id, "cyber_dna")
    service.grant(db_session, test_user.id, "cyber_dna")

    response = _app().get("/api/dna/test", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_middleware_leaves_authentication_to_the_route(auth_headers):
    client = _app()

    # No token: the route's own auth dependency must produce 401, not the gate.
    assert client.get("/api/dna/test").status_code == 200
    # Malformed token also passes through to the route in this isolated app.
    assert (
        client.get(
            "/api/dna/test", headers={"Authorization": "Bearer not-a-token"}
        ).status_code
        == 200
    )
    # CORS preflight is never blocked by consent.
    assert client.options("/api/dna/test").status_code in {200, 405}

