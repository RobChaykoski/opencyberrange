"""Persisted learner report snapshots: storage, immutability, and scoping."""

from __future__ import annotations

import pytest

from app.services import skill_dna
from app.services.learner_snapshots import get_snapshot

pytestmark = pytest.mark.db


def _export_markdown(client, auth_headers) -> int:
    response = client.get("/api/profile/career-dossier.md", headers=auth_headers)
    assert response.status_code == 200, response.text
    return int(response.headers["X-OCR-Snapshot-ID"])


def test_report_export_is_persisted_with_weights(
    client, db_session, auth_headers, test_user
):
    snapshot_id = _export_markdown(client, auth_headers)

    detail = client.get(
        f"/api/profile/snapshots/{snapshot_id}", headers=auth_headers
    )
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert body["snapshot"]["kind"] == "career_dossier"
    assert body["snapshot"]["schema_version"] == "2026.1"
    assert body["snapshot"]["formula_version"] == skill_dna.FORMULA_VERSION
    weights = body["snapshot"]["weights"]["factor_weights"]["skill_dna"]
    assert weights["cap"] == 99
    assert weights["dimensions"]["builder"]["completed_lab"] == 2.0
    assert body["payload"]["cyber_dna"]["factor_weights"] == weights
    assert body["snapshot"]["content_sha256"] == body["snapshot"]["content_sha256"]


def test_stored_report_survives_a_formula_change(
    client, db_session, auth_headers, test_user, monkeypatch
):
    snapshot_id = _export_markdown(client, auth_headers)

    # A later scoring change must not rewrite the stored report.
    monkeypatch.setattr(skill_dna, "FORMULA_VERSION", "9999.0")

    stored = client.get(
        f"/api/profile/snapshots/{snapshot_id}", headers=auth_headers
    ).json()
    assert stored["payload"]["cyber_dna"]["formula_version"] == "2026.14"

    live = client.get("/api/profile/career-dossier", headers=auth_headers).json()
    assert live["cyber_dna"]["formula_version"] == "9999.0"
    assert live["snapshot"]["snapshot_id"] != snapshot_id


def test_snapshot_listing_filters_and_owner_scope(
    client, db_session, auth_headers, test_user
):
    snapshot_id = _export_markdown(client, auth_headers)

    listing = client.get(
        "/api/profile/snapshots?kind=career_dossier&limit=5",
        headers=auth_headers,
    )
    assert listing.status_code == 200
    ids = [row["snapshot_id"] for row in listing.json()["snapshots"]]
    assert snapshot_id in ids

    other_kind = client.get(
        "/api/profile/snapshots?kind=portfolio", headers=auth_headers
    ).json()["snapshots"]
    assert all(row["kind"] == "portfolio" for row in other_kind)

    assert (
        client.get("/api/profile/snapshots/999999", headers=auth_headers).status_code
        == 404
    )
    assert get_snapshot(db_session, test_user.id + 999, snapshot_id) is None


def test_stored_report_renders_from_the_snapshot(client, auth_headers):
    snapshot_id = _export_markdown(client, auth_headers)

    markdown = client.get(
        f"/api/profile/snapshots/{snapshot_id}/markdown", headers=auth_headers
    )
    assert markdown.status_code == 200
    assert f"Report snapshot `{snapshot_id}`" in markdown.text
    assert markdown.headers["X-OCR-Snapshot-ID"] == str(snapshot_id)

    html = client.get(
        f"/api/profile/snapshots/{snapshot_id}/html", headers=auth_headers
    )
    assert html.status_code == 200
    assert "snapshot-footer" in html.text


def test_repeated_export_dedupes_unchanged_content(client, auth_headers):
    first = _export_markdown(client, auth_headers)
    second = _export_markdown(client, auth_headers)
    assert first == second
