"""Privacy and auditor governance dashboard tests."""

import uuid

import pytest

from app.auth import get_password_hash
from app.models import User

pytestmark = pytest.mark.db

TEST_PASSWORD = "Correct#Horse7Battery"


def _login(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_governance_dashboards_enforce_roles(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    users = {}
    for role in ("privacy_officer", "auditor", "instructor"):
        user = User(
            username=f"governance_{role}_{suffix}",
            email=f"governance_{role}_{suffix}@university.edu",
            hashed_password=get_password_hash(PASSWORD),
            is_active=True,
            is_approved=True,
            role=role,
            institution_id="default",
        )
        db_session.add(user)
        users[role] = user
    db_session.commit()
    for user in users.values():
        db_session.refresh(user)

    try:
        privacy = _login(client, users["privacy_officer"])
        privacy_view = client.get("/api/governance/privacy/dashboard", headers=privacy)
        assert privacy_view.status_code == 200, privacy_view.text
        privacy_body = privacy_view.json()
        assert "learners" in privacy_body
        assert "consent" in privacy_body
        assert "report_access" in privacy_body
        assert privacy_body["suppression_threshold"] >= 0

        auditor = _login(client, users["auditor"])
        auditor_privacy = client.get(
            "/api/governance/privacy/dashboard", headers=auditor
        )
        assert auditor_privacy.status_code == 403

        audit_view = client.get("/api/governance/audit/dashboard", headers=auditor)
        assert audit_view.status_code == 200, audit_view.text
        audit_body = audit_view.json()
        assert "report_exports" in audit_body
        assert "integrity_entries" in audit_body
        assert "report_access" in audit_body

        privacy_audit = client.get(
            "/api/governance/audit/dashboard", headers=privacy
        )
        assert privacy_audit.status_code == 403

        instructor = _login(client, users["instructor"])
        assert client.get(
            "/api/governance/privacy/dashboard", headers=instructor
        ).status_code == 403
        assert client.get(
            "/api/governance/audit/dashboard", headers=instructor
        ).status_code == 403
    finally:
        for user in users.values():
            db_session.delete(user)
        db_session.commit()
