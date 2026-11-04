from __future__ import annotations

import uuid

import pytest

from app.auth import get_password_hash
from app.models import IdentityProvider, User

pytestmark = pytest.mark.db

PASSWORD = "Correct#Horse7Battery"


@pytest.fixture()
def admin_auth(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"idp_admin_{suffix}",
        email=f"idp_admin_{suffix}@university.edu",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    yield headers, user
    db_session.query(IdentityProvider).filter(
        IdentityProvider.name.like("Test %")
    ).delete(synchronize_session=False)
    db_session.query(User).filter(User.id == user.id).delete()
    db_session.commit()


@pytest.fixture()
def student_auth(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"idp_student_{suffix}",
        email=f"idp_student_{suffix}@university.edu",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add(user)
    db_session.commit()
    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    yield {"Authorization": f"Bearer {resp.json()['access_token']}"}
    db_session.query(User).filter(User.id == user.id).delete()
    db_session.commit()


def test_ldap_provider_create_redacts_secret(admin_auth, client):
    headers, _ = admin_auth
    created = client.post(
        "/api/identity/providers",
        json={
            "name": "Test LDAP",
            "kind": "ldap",
            "enabled": True,
            "config": {
                "server_url": "ldaps://ldap.example.edu",
                "base_dn": "ou=people,dc=example,dc=edu",
            },
            "secrets": {"bind_password": "super-secret"},
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["kind"] == "ldap"
    assert body["has_secrets"] is True
    assert body["secret_keys"] == ["bind_password"]
    assert "super-secret" not in created.text

    listed = client.get("/api/identity/providers", headers=headers)
    assert listed.status_code == 200
    assert "super-secret" not in listed.text


def test_oidc_and_saml_validation(admin_auth, client):
    headers, _ = admin_auth
    bad = client.post(
        "/api/identity/providers",
        json={
            "name": "Test OIDC",
            "kind": "oidc",
            "config": {"issuer": "http://not-https", "client_id": "x"},
        },
        headers=headers,
    )
    assert bad.status_code == 400

    good = client.post(
        "/api/identity/providers",
        json={
            "name": "Test OIDC",
            "kind": "oidc",
            "enabled": True,
            "config": {
                "issuer": "https://idp.example.edu",
                "client_id": "ocr-client",
                "scopes": "openid email profile",
            },
            "secrets": {"client_secret": "client-secret"},
        },
        headers=headers,
    )
    assert good.status_code == 201, good.text

    saml = client.post(
        "/api/identity/providers",
        json={
            "name": "Test SAML",
            "kind": "saml",
            "enabled": True,
            "config": {
                "idp_entity_id": "https://idp.example.edu/saml",
                "sso_url": "https://idp.example.edu/sso",
                "sp_entity_id": "https://ocr.example.edu/saml",
                "acs_url": "https://ocr.example.edu/api/identity/saml/acs",
            },
        },
        headers=headers,
    )
    assert saml.status_code == 201, saml.text


def test_default_provider_must_be_enabled_and_is_exclusive(admin_auth, client):
    headers, _ = admin_auth
    first = client.post(
        "/api/identity/providers",
        json={
            "name": "Test LDAP",
            "kind": "ldap",
            "enabled": True,
            "config": {"server_url": "ldap://ldap.example.edu", "base_dn": "dc=example,dc=edu"},
        },
        headers=headers,
    ).json()
    second = client.post(
        "/api/identity/providers",
        json={
            "name": "Test OIDC",
            "kind": "oidc",
            "enabled": True,
            "config": {"issuer": "https://idp.example.edu", "client_id": "ocr"},
        },
        headers=headers,
    ).json()

    made_default = client.post(
        f"/api/identity/providers/{first['id']}/default", headers=headers
    )
    assert made_default.status_code == 200, made_default.text
    assert made_default.json()["is_default"] is True

    switched = client.post(
        f"/api/identity/providers/{second['id']}/default", headers=headers
    )
    assert switched.status_code == 200, switched.text
    listed = client.get("/api/identity/providers", headers=headers).json()["providers"]
    defaults = [row for row in listed if row["is_default"]]
    assert [row["id"] for row in defaults] == [second["id"]]

    disabled = client.patch(
        f"/api/identity/providers/{second['id']}",
        json={"enabled": False},
        headers=headers,
    )
    assert disabled.status_code == 400


def test_identity_provider_requires_admin(student_auth, client):
    resp = client.get("/api/identity/providers", headers=student_auth)
    assert resp.status_code == 403
