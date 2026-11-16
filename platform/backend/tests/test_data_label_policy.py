"""Data-label policy: custom schemes, RBAC, region/role ceilings, middleware."""

from __future__ import annotations

import json
import uuid
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

from app.auth import get_password_hash
from app.main import export_label_headers
from app.models import PlatformSetting, User
from app.security.policy import authorize
from app.services import data_labels, export_labels

# Test-only login credential; security-delta: allow credential-like assignment
PASSWORD = "Label#Pass123"
pytestmark = pytest.mark.db

SETTING_DEFAULTS = {
    "export_label_enabled": "true",
    "export_classification": "internal",
    "export_organisation": "",
    "export_handling_note": "",
    "export_include_timestamp": "true",
    "data_label_enforcement_enabled": "false",
    "data_label_region": "",
    "data_label_max_export_rank": "3",
    "data_label_block_restricted_exports": "true",
    "data_label_custom_levels": "",
    "data_label_region_rules": "",
    "data_label_role_max_rank": "",
}


def _set(db_session, **values):
    for key, value in values.items():
        row = (
            db_session.query(PlatformSetting)
            .filter(PlatformSetting.key == key)
            .first()
        )
        if row is None:
            row = PlatformSetting(
                key=key,
                value=str(value),
                category="exports",
                description="test",
                is_secret=False,
            )
            db_session.add(row)
        else:
            row.value = str(value)
    db_session.commit()


@pytest.fixture(autouse=True)
def _reset_settings(db_session):
    yield
    _set(db_session, **SETTING_DEFAULTS)


def _user(db_session, role="student"):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"labels_{role}_{suffix}",
        email=f"labels_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _headers(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_path_classification_covers_public_and_restricted_exports():
    assert export_labels.classification_for_path("/api/auth/export") == "confidential"
    assert (
        export_labels.classification_for_path("/api/admin/activity/export")
        == "confidential"
    )
    assert (
        export_labels.classification_for_path("/api/admin/system/backups/1")
        == "restricted"
    )
    assert (
        export_labels.classification_for_path("/api/admin/users/export")
        == "restricted"
    )
    assert (
        export_labels.classification_for_path("/api/exercises/verify/certificate/abc")
        == "public"
    )
    assert export_labels.classification_for_path("/api/health") is None


def test_enforcement_off_labels_but_never_denies(db_session):
    _set(db_session, data_label_enforcement_enabled="false")
    decision = data_labels.evaluate_export(
        db_session, SimpleNamespace(id=1, role="student"), "/api/admin/system/backups/1"
    )
    assert decision.allowed is True
    assert decision.enforced is False
    assert decision.policy == "advisory"


def test_student_can_export_confidential_self_data_but_not_restricted(db_session):
    _set(db_session, data_label_enforcement_enabled="true")
    student = SimpleNamespace(id=1, role="student")

    self_export = data_labels.evaluate_export(
        db_session, student, "/api/auth/export"
    )
    assert self_export.allowed is True
    assert self_export.classification_key == "confidential"
    assert self_export.policy == "enforced"

    restricted = data_labels.evaluate_export(
        db_session, student, "/api/admin/system/backups/1"
    )
    assert restricted.allowed is False
    assert restricted.policy == "denied"


def test_admin_restricted_export_is_blocked_by_default_and_can_be_allowed(db_session):
    _set(db_session, data_label_enforcement_enabled="true")
    admin = SimpleNamespace(id=1, role="admin")

    blocked = data_labels.evaluate_export(
        db_session, admin, "/api/admin/system/backups/1"
    )
    assert blocked.allowed is False

    _set(db_session, data_label_block_restricted_exports="false")
    allowed = data_labels.evaluate_export(
        db_session, admin, "/api/admin/system/backups/1"
    )
    assert allowed.allowed is True
    assert allowed.classification_key == "restricted"


def test_region_rule_caps_exports_even_for_admin(db_session):
    _set(
        db_session,
        data_label_enforcement_enabled="true",
        data_label_region="EU",
        data_label_region_rules=json.dumps(
            {"EU": {"max_export_rank": 1, "block_restricted": True}}
        ),
    )
    decision = data_labels.evaluate_export(
        db_session, SimpleNamespace(id=1, role="admin"), "/api/auth/export"
    )
    assert decision.allowed is False
    assert "ceiling" in decision.reason


def test_custom_levels_align_to_an_institutional_scheme(db_session):
    levels = [
        {"key": "public", "label": "Public", "rank": 0},
        {
            "key": "official",
            "label": "Official",
            "rank": 1,
            "handling": "Official use only.",
        },
        {
            "key": "protected",
            "label": "Protected",
            "rank": 2,
            "handling": "Protected personal information.",
        },
        {
            "key": "sealed",
            "label": "Sealed",
            "rank": 3,
            "handling": "Sealed records.",
            "exportable": False,
        },
    ]
    _set(
        db_session,
        export_classification="official",
        data_label_custom_levels=json.dumps(levels),
        data_label_enforcement_enabled="true",
    )
    student = SimpleNamespace(id=1, role="student")

    self_export = data_labels.evaluate_export(
        db_session, student, "/api/auth/export"
    )
    assert self_export.classification_key == "protected"
    assert self_export.classification == "Protected"
    assert self_export.allowed is True

    sealed = data_labels.evaluate_export(
        db_session, student, "/api/admin/system/backups/1"
    )
    # The path's restricted rank maps to the sealed level; it is explicitly
    # non-exportable, so the institution's own label wins.
    assert sealed.classification_key == "sealed"
    assert sealed.allowed is False
    assert "non-exportable" in sealed.reason


def test_invalid_custom_levels_fall_back_with_a_warning(db_session):
    _set(db_session, data_label_custom_levels="{not-json")
    summary = data_labels.policy_summary(db_session)
    assert summary["levels"]
    assert summary["warnings"]
    assert any("not valid JSON" in warning for warning in summary["warnings"])


def test_rbac_export_permissions_follow_the_classification_rank():
    assert authorize(
        None, SimpleNamespace(id=1, role="student"), "export.confidential"
    ).allowed
    assert not authorize(
        None, SimpleNamespace(id=1, role="student"), "export.restricted"
    ).allowed
    assert authorize(
        None, SimpleNamespace(id=1, role="auditor"), "export.internal"
    ).allowed
    assert not authorize(
        None, SimpleNamespace(id=1, role="auditor"), "export.confidential"
    ).allowed
    assert authorize(
        None, SimpleNamespace(id=1, role="admin"), "export.restricted"
    ).allowed


def test_export_middleware_denies_restricted_and_labels_allowed(
    db_session, test_user, auth_headers
):
    _set(db_session, data_label_enforcement_enabled="true")

    app = FastAPI()
    app.middleware("http")(export_label_headers)

    @app.get("/api/auth/export/demo")
    def allowed_export():
        return Response(
            "a,b\n1,2\n",
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="demo.csv"'},
        )

    @app.get("/api/admin/system/backups/demo")
    def restricted_export():
        return Response(
            "backup",
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="backup.csv"'},
        )

    client = TestClient(app)

    allowed = client.get("/api/auth/export/demo", headers=auth_headers)
    assert allowed.status_code == 200, allowed.text
    assert allowed.headers["x-data-classification"] == "Confidential"
    assert allowed.headers["x-data-policy"] == "enforced"

    denied = client.get("/api/admin/system/backups/demo", headers=auth_headers)
    assert denied.status_code == 403, denied.text
    assert denied.json()["error"] == "DataLabelExportDenied"
    assert denied.headers["x-data-policy"] == "denied"


def test_admin_policy_endpoint_previews_a_decision(client, db_session):
    admin = _user(db_session, "admin")
    student = _user(db_session, "student")
    _set(db_session, data_label_enforcement_enabled="true")

    response = client.get(
        "/api/admin/data-labels/policy?role=student&path=/api/auth/export",
        headers=_headers(client, admin),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["enforcement"] is True
    assert body["levels"]
    assert body["label_permissions"]["confidential"] == "export.confidential"
    assert body["sample_decision"]["allowed"] is True

    denied = client.get(
        "/api/admin/data-labels/policy",
        headers=_headers(client, student),
    )
    assert denied.status_code == 403
