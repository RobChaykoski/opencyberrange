"""RBAC/PBAC matrix: grants, policy attributes, and endpoint authorization."""

from __future__ import annotations

import uuid

import pytest

from app.auth import get_password_hash
from app.models import User
from app.security import permissions
from app.services import access_matrix, rbac

PASSWORD = "Matrix#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, role="student"):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"matrix_{role}_{suffix}",
        email=f"matrix_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id="default",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _headers(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_matrix_contains_every_role_and_permission(db_session):
    rbac.seed(db_session)
    matrix = access_matrix.build_matrix(db_session, include_timestamp=False)

    role_keys = [role["key"] for role in matrix["roles"]]
    assert set(role_keys) == set(permissions.SEEDED_ROLES)
    assert matrix["summary"]["permissions"] == len(permissions.PERMISSION_CATALOG)

    for row in matrix["permissions"]:
        assert set(row["roles"]) == set(role_keys)
        assert row["granted_to"] == [
            role_key for role_key in role_keys if row["roles"][role_key]
        ]

    assert matrix["summary"]["restricted"] == len(
        permissions.SENSITIVE_PRIVATE_PERMISSIONS
    )
    assert matrix["summary"]["break_glass"] == len(
        permissions.BREAK_GLASS_PERMISSIONS
    )
    assert matrix["policy_rules"]


def test_private_permissions_are_never_role_grants(db_session):
    rbac.seed(db_session)
    matrix = access_matrix.build_matrix(db_session, include_timestamp=False)

    for row in matrix["permissions"]:
        if row["sensitivity"] == "restricted":
            assert row["granted_to"] == [], row["key"]


def test_auditor_receives_read_only_permissions_only(db_session):
    rbac.seed(db_session)
    matrix = access_matrix.build_matrix(db_session, include_timestamp=False)

    auditor = next(role for role in matrix["roles"] if role["key"] == "auditor")
    assert set(auditor["permissions"]) <= permissions.READ_ONLY_PERMISSIONS


def test_matrix_reports_reviewed_tenant_scopes(db_session):
    rbac.seed(db_session)
    matrix = access_matrix.build_matrix(db_session, include_timestamp=False)
    scopes = {role["key"]: role["tenant_scope"] for role in matrix["roles"]}

    assert scopes["admin"] == "global"
    assert scopes["service_account"] == "explicit"
    assert scopes["employer"] == "shared"
    assert scopes["instructor"] == "institution"


def test_matrix_endpoint_requires_security_event_access(client, db_session):
    admin = _user(db_session, "admin")
    student = _user(db_session, "student")

    allowed = client.get(
        "/api/admin/security/rbac/matrix", headers=_headers(client, admin)
    )
    assert allowed.status_code == 200, allowed.text
    body = allowed.json()
    assert body["summary"]["roles"] >= 1
    assert body["permissions"]

    denied = client.get(
        "/api/admin/security/rbac/matrix", headers=_headers(client, student)
    )
    assert denied.status_code == 403
