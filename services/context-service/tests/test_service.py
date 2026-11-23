from pathlib import Path

import pytest
from app.main import Settings, create_app
from fastapi.testclient import TestClient

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/metadata.json"
HEADERS = {"X-Context-Token": "test-token"}


@pytest.fixture()
def client():
    settings = Settings(
        metadata_mode="fixture",
        metadata_file=str(FIXTURE),
        opa_url=None,
        service_token="test-token",
        fail_closed=True,
    )
    return TestClient(create_app(settings))


def payload(resource_id, role="student", action="export"):
    return {
        "subject": {"id": "user-1", "role": role, "groups": []},
        "resource": {"id": resource_id, "type": "dataset"},
        "action": action,
    }


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["policy_mode"] == "fixture"


def test_missing_token_is_rejected(client):
    assert client.post("/decide", json=payload("dataset:public-demo")).status_code == 401


def test_context_returns_metadata(client):
    response = client.post(
        "/context", json=payload("dataset:lumenpay-audit"), headers=HEADERS
    )
    assert response.status_code == 200
    body = response.json()
    assert body["resource"]["classification"] == "restricted"
    assert body["metadata_hash"]


def test_public_resource_is_allowed(client):
    response = client.post(
        "/decide", json=payload("dataset:public-demo", action="read"), headers=HEADERS
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "allow"


def test_student_cannot_export_restricted(client):
    response = client.post(
        "/decide", json=payload("dataset:lumenpay-audit"), headers=HEADERS
    )
    body = response.json()
    assert body["decision"] == "deny"
    assert body["allow"] is False


def test_training_pii_is_masked_for_students(client):
    response = client.post(
        "/decide", json=payload("dataset:training-pii", action="read"), headers=HEADERS
    )
    body = response.json()
    assert body["decision"] == "mask"
    assert body["allow"] is True
    assert "mask:pii" in body["obligations"]


@pytest.mark.parametrize("action", ["export", "external_share"])
def test_pipeda_pii_export_requires_approval(client, action):
    response = client.post(
        "/decide",
        json=payload("reports:instructor:all", role="instructor", action=action),
        headers=HEADERS,
    )
    body = response.json()
    assert body["decision"] == "require_approval"
    assert body["allow"] is False


def test_unknown_metadata_is_denied(client):
    response = client.post(
        "/decide", json=payload("dataset:does-not-exist"), headers=HEADERS
    )
    body = response.json()
    assert body["decision"] == "deny"


def scan_payload(text, role="instructor", action="publish", source="repo:public-docs"):
    return {
        "source": source,
        "text": text,
        "subject": {"id": "user-1", "role": role, "groups": []},
        "action": action,
    }


def test_scan_redacts_flags_infrastructure_and_secrets(client):
    text = (
        "host 10.20.30.40 flag OCR{secret_flag} "
        "client_secret=SuperSecretValue123456"
    )
    response = client.post(
        "/scan", json={"source": "test-document", "text": text}, headers=HEADERS
    )
    body = response.json()

    assert response.status_code == 200
    assert body["classification"] == "restricted"
    assert body["contains_infrastructure_metadata"] is True
    assert body["contains_assessment_answer_key"] is True
    assert body["contains_secrets"] is True
    assert "OCR{secret_flag}" not in body["redacted_text"]
    assert "10.20.30.40" not in body["redacted_text"]
    assert "SuperSecretValue123456" not in body["redacted_text"]


def test_scan_ignores_placeholders_and_documentation_ranges(client):
    response = client.post(
        "/scan",
        json={
            "source": "test-document",
            "text": "OCR{...} OCR{REPLACE_ME} 203.0.113.10",
        },
        headers=HEADERS,
    )
    body = response.json()

    assert body["classification"] == "internal"
    assert body["publication_safe"] is True
    assert body["findings"] == []


def test_answer_key_publication_is_denied(client):
    response = client.post(
        "/scan-and-decide",
        json=scan_payload("OCR{secret_flag}", action="publish"),
        headers=HEADERS,
    )
    body = response.json()

    assert body["decision"] == "deny"
    assert body["scan"]["contains_assessment_answer_key"] is True
    assert "block:assessment-answer-key" in body["obligations"]


def test_infrastructure_metadata_export_requires_approval(client):
    response = client.post(
        "/scan-and-decide",
        json=scan_payload("host 10.20.30.40", action="export"),
        headers=HEADERS,
    )
    body = response.json()

    assert body["decision"] == "require_approval"
    assert "approval:infrastructure-metadata" in body["obligations"]


def test_clean_document_can_be_published(client):
    response = client.post(
        "/scan-and-decide",
        json=scan_payload("Internal runbook with no sensitive values."),
        headers=HEADERS,
    )
    body = response.json()

    assert body["decision"] == "allow"
    assert body["scan"]["publication_safe"] is True
