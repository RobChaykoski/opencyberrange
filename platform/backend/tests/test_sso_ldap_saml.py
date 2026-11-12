"""LDAP and SAML adapters: routing, provisioning, role mapping, and HA state."""

from __future__ import annotations

import base64
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from lxml import etree
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from onelogin.saml2.xml_templates import OneLogin_Saml2_Templates
from onelogin.saml2.xml_utils import OneLogin_Saml2_XML

from app.auth import get_password_hash
from app.models import (
    ExternalIdentity,
    IdentityProvider,
    SsoLoginState,
    SsoLoginTicket,
    SsoSession,
    User,
)
from app.services import ldap_auth, saml_auth
from app.services.external_identity import (
    ExternalUser,
    SSOError,
    role_for,
)

pytestmark = pytest.mark.db

PASSWORD = uuid.uuid4().hex + "Aa1!"
SAML_CERT = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIIBszCCAVmgAwIBAgIUfakecertificateplaceholder000000000000\n"
    "-----END CERTIFICATE-----"
)


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


@pytest.fixture(autouse=True)
def _cleanup_sso(db_session):
    yield
    provider_ids = [
        row.id
        for row in db_session.query(IdentityProvider)
        .filter(IdentityProvider.name.like("SSO Test LDAP %"))
        .all()
    ] + [
        row.id
        for row in db_session.query(IdentityProvider)
        .filter(IdentityProvider.name.like("SSO Test SAML %"))
        .all()
    ]
    user_ids = [
        row.id
        for row in db_session.query(User)
        .filter(User.username.like("sso_test_ldap_%"))
        .all()
    ] + [
        row.id
        for row in db_session.query(User)
        .filter(User.username.like("sso_test_saml_%"))
        .all()
    ]
    if provider_ids or user_ids:
        db_session.query(SsoLoginTicket).filter(
            (SsoLoginTicket.provider_id.in_(provider_ids))
            | (SsoLoginTicket.user_id.in_(user_ids))
        ).delete(synchronize_session=False)
        db_session.query(SsoLoginState).filter(
            SsoLoginState.provider_id.in_(provider_ids)
        ).delete(synchronize_session=False)
        db_session.query(SsoSession).filter(
            (SsoSession.provider_id.in_(provider_ids))
            | (SsoSession.user_id.in_(user_ids))
        ).delete(synchronize_session=False)
        db_session.query(ExternalIdentity).filter(
            (ExternalIdentity.provider_id.in_(provider_ids))
            | (ExternalIdentity.user_id.in_(user_ids))
        ).delete(synchronize_session=False)
        db_session.query(User).filter(User.id.in_(user_ids)).delete(
            synchronize_session=False
        )
        db_session.query(IdentityProvider).filter(
            IdentityProvider.id.in_(provider_ids)
        ).delete(synchronize_session=False)
        db_session.commit()


def _admin(client, db_session) -> dict:
    suffix = _suffix()
    user = User(
        username=f"sso_test_ldap_admin_{suffix}",
        email=f"sso_test_ldap_admin_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=True,
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _create_provider(client, headers, *, kind: str, name: str, config: dict, secrets: dict | None = None):
    payload = {
        "name": name,
        "kind": kind,
        "enabled": True,
        "is_default": False,
        "config": config,
    }
    if secrets:
        payload["secrets"] = secrets
    resp = client.post("/api/identity/providers", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _ldap_provider(client, headers, *, name: str | None = None, config: dict | None = None):
    suffix = _suffix()
    return _create_provider(
        client,
        headers,
        kind="ldap",
        name=name or f"SSO Test LDAP {suffix}",
        config={
            "server_url": "ldaps://ldap.example.edu",
            "base_dn": "ou=people,dc=example,dc=edu",
            "bind_dn": "cn=svc-ocr,ou=services,dc=example,dc=edu",
            "user_search_filter": "(uid={username})",
            "email_attribute": "mail",
            "username_attribute": "uid",
            "group_attribute": "memberOf",
            "instructor_group": "instructors",
            **(config or {}),
        },
        secrets={"bind_password": "service-secret"},
    )


def _saml_provider(client, headers, *, config: dict | None = None):
    suffix = _suffix()
    return _create_provider(
        client,
        headers,
        kind="saml",
        name=f"SSO Test SAML {suffix}",
        config={
            "idp_entity_id": "https://idp.example.edu/metadata",
            "sp_entity_id": "https://ocr.example.edu/saml/metadata",
            "sso_url": "https://idp.example.edu/sso",
            "idp_x509_cert": SAML_CERT,
            "email_attribute": "email",
            "username_attribute": "uid",
            "group_attribute": "groups",
            "instructor_group": "instructors",
            **(config or {}),
        },
    )


def _identity(**overrides) -> ExternalUser:
    suffix = _suffix()
    values = {
        "subject": f"uid=ldap_{suffix},ou=people,dc=example,dc=edu",
        "email": f"sso_test_ldap_{suffix}@example.org",
        "username_hint": f"sso_test_ldap_{suffix}",
        "first_name": "L Dana",
        "last_name": "Student",
        "name": "L Dana Student",
        "groups": [],
    }
    values.update(overrides)
    return ExternalUser(**values)


def _saml_identity(**overrides) -> ExternalUser:
    suffix = _suffix()
    values = {
        "subject": f"saml-subject-{suffix}",
        "email": f"sso_test_saml_{suffix}@example.org",
        "username_hint": f"sso_test_saml_{suffix}",
        "first_name": "Sam",
        "last_name": "Learner",
        "name": "Sam Learner",
        "groups": [],
    }
    values.update(overrides)
    return ExternalUser(**values)


def _make_keypair():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "idp.example.edu")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ).decode()
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()
    return key_pem, cert_pem


def _signed_response(
    provider,
    request_id: str,
    email: str,
    groups: list[str],
    key_pem: str,
    cert_pem: str,
    *,
    sign: bool = True,
) -> dict:
    acs = saml_auth.resolved_acs_url(provider)
    now = datetime.now(timezone.utc)
    issue = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    not_before = (now - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    not_after = (now + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")

    attributes = OneLogin_Saml2_Templates.ATTRIBUTE % ("email", email)
    for group in groups:
        attributes += OneLogin_Saml2_Templates.ATTRIBUTE % ("groups", group)
    xml = OneLogin_Saml2_Templates.RESPONSE % {
        "id": "_response_id",
        "in_response_to": request_id,
        "issue_instant": issue,
        "destination": acs,
        "entity_id": "https://idp.example.edu/metadata",
        "status": "urn:oasis:names:tc:SAML:2.0:status:Success",
        "assertion_id": "_assertion_id",
        "requester": "https://ocr.example.edu/saml/metadata",
        "name_id_policy": OneLogin_Saml2_Constants.NAMEID_EMAIL_ADDRESS,
        "name_id": email,
        "cm": "urn:oasis:names:tc:SAML:2.0:cm:bearer",
        "not_after": not_after,
        "not_before": not_before,
        "session_index": "session-e2e",
        "authn_context": (
            "<saml:AuthnContext>"
            "<saml:AuthnContextClassRef>"
            "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport"
            "</saml:AuthnContextClassRef>"
            "</saml:AuthnContext>"
        ),
        "attributes": attributes,
    }
    root = OneLogin_Saml2_XML.to_etree(xml)
    if sign:
        assertion = OneLogin_Saml2_XML.query(root, "//saml:Assertion")[0]
        signed = OneLogin_Saml2_XML.to_etree(
            OneLogin_Saml2_Utils.add_sign(
                etree.tostring(assertion), key_pem, cert_pem
            )
        )
        assertion.getparent().replace(assertion, signed)
    return {
        "SAMLResponse": base64.b64encode(etree.tostring(root)).decode(),
        "RelayState": "relay",
    }


# ---------------------------------------------------------------- role mapping


def test_role_mapping_never_grants_admin():
    assert role_for({"default_role": "student"}, []) == "student"
    assert role_for({"default_role": "instructor"}, []) == "instructor"
    assert role_for({"default_role": "admin"}, []) == "student"
    assert (
        role_for(
            {"default_role": "student", "instructor_group": "instructors"},
            ["CN=Instructors,OU=Groups,DC=example,DC=edu"],
        )
        == "instructor"
    )
    assert (
        role_for(
            {"default_role": "student", "instructor_group": "faculty"},
            ["CN=Instructors,OU=Groups,DC=example,DC=edu"],
        )
        == "student"
    )


# ----------------------------------------------------------------------- LDAP


def test_provider_list_includes_ldap_and_saml(client, db_session):
    headers = _admin(client, db_session)
    ldap = _ldap_provider(client, headers)
    saml = _saml_provider(client, headers)

    listed = client.get("/api/auth/sso/providers")
    assert listed.status_code == 200, listed.text
    rows = {row["id"]: row for row in listed.json()["providers"]}
    assert rows[ldap["id"]]["kind"] == "ldap"
    assert rows[ldap["id"]]["login_path"] is None
    assert rows[saml["id"]]["kind"] == "saml"
    assert rows[saml["id"]]["login_path"].endswith(f"/saml/{saml['id']}/login")
    assert "service-secret" not in listed.text


def test_ldap_login_provisions_and_exchanges_ticket(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _ldap_provider(client, headers)
    identity = _identity()
    monkeypatch.setattr(ldap_auth, "authenticate", lambda *args, **kwargs: identity)

    login = client.post(
        f"/api/auth/sso/ldap/{provider['id']}/login",
        json={"username": "ldap.student", "password": "secret", "return_to": "/profile"},
    )
    assert login.status_code == 200, login.text
    body = login.json()
    assert body["return_to"] == "/profile"
    assert "ticket" in body

    exchanged = client.post("/api/auth/sso/exchange", json={"ticket": body["ticket"]})
    assert exchanged.status_code == 200, exchanged.text
    assert exchanged.json()["user"]["email"] == identity.email
    assert exchanged.json()["user"]["role"] == "student"

    user = db_session.query(User).filter(User.email == identity.email).first()
    assert user is not None
    assert user.password_login_disabled is True
    assert user.is_admin is False
    link = (
        db_session.query(ExternalIdentity)
        .filter(
            ExternalIdentity.provider_id == provider["id"],
            ExternalIdentity.subject == identity.subject,
        )
        .first()
    )
    assert link is not None and link.user_id == user.id

    replay = client.post("/api/auth/sso/exchange", json={"ticket": body["ticket"]})
    assert replay.status_code == 400


def test_ldap_invalid_credentials_returns_generic_401(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _ldap_provider(client, headers)

    def _fail(*args, **kwargs):
        raise SSOError("Invalid username or password.", code="invalid_credentials")

    monkeypatch.setattr(ldap_auth, "authenticate", _fail)
    resp = client.post(
        f"/api/auth/sso/ldap/{provider['id']}/login",
        json={"username": "user", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid username or password."


def test_ldap_outage_returns_503(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _ldap_provider(client, headers)

    def _down(*args, **kwargs):
        raise SSOError("Could not connect to the LDAP server.", code="unavailable")

    monkeypatch.setattr(ldap_auth, "authenticate", _down)
    resp = client.post(
        f"/api/auth/sso/ldap/{provider['id']}/login",
        json={"username": "user", "password": "secret"},
    )
    assert resp.status_code == 503


def test_ldap_instructor_group_grants_instructor(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _ldap_provider(client, headers)
    identity = _identity(
        groups=["CN=Instructors,OU=Groups,DC=example,DC=edu"],
    )
    monkeypatch.setattr(ldap_auth, "authenticate", lambda *args, **kwargs: identity)

    login = client.post(
        f"/api/auth/sso/ldap/{provider['id']}/login",
        json={"username": "teacher", "password": "secret"},
    )
    assert login.status_code == 200, login.text
    exchanged = client.post(
        "/api/auth/sso/exchange", json={"ticket": login.json()["ticket"]}
    )
    assert exchanged.status_code == 200, exchanged.text
    assert exchanged.json()["user"]["role"] == "instructor"


def test_ldap_role_follows_directory_group_changes(client, db_session, monkeypatch):
    """A directory group change applies on the next login, not only at signup."""
    headers = _admin(client, db_session)
    provider = _ldap_provider(client, headers)
    suffix = _suffix()
    base = {
        "subject": f"uid=ldap_role_{suffix},ou=people,dc=example,dc=edu",
        "email": f"sso_role_{suffix}@example.org",
        "username_hint": f"sso_role_{suffix}",
        "first_name": "Role",
        "last_name": "Test",
        "name": "Role Test",
    }

    def login_and_role():
        login = client.post(
            f"/api/auth/sso/ldap/{provider['id']}/login",
            json={"username": "role-test", "password": "secret"},
        )
        assert login.status_code == 200, login.text
        exchanged = client.post(
            "/api/auth/sso/exchange", json={"ticket": login.json()["ticket"]}
        )
        assert exchanged.status_code == 200, exchanged.text
        return exchanged.json()["user"]["role"]

    monkeypatch.setattr(
        ldap_auth,
        "authenticate",
        lambda *args, **kwargs: ExternalUser(groups=[], **base),
    )
    assert login_and_role() == "student"

    monkeypatch.setattr(
        ldap_auth,
        "authenticate",
        lambda *args, **kwargs: ExternalUser(
            groups=["cn=instructors,ou=groups,dc=example,dc=edu"],
            **base,
        ),
    )
    assert login_and_role() == "instructor"


def test_ldap_links_existing_student_but_never_admin(
    client, db_session, monkeypatch
):
    headers = _admin(client, db_session)
    provider = _ldap_provider(client, headers)
    suffix = _suffix()
    student = User(
        username=f"sso_test_ldap_link_{suffix}",
        email=f"sso_test_ldap_link_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    admin = User(
        username=f"sso_test_ldap_admin_link_{suffix}",
        email=f"sso_test_ldap_admin_link_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="admin",
        is_admin=True,
    )
    db_session.add_all([student, admin])
    db_session.commit()
    db_session.refresh(student)
    db_session.refresh(admin)

    monkeypatch.setattr(
        ldap_auth,
        "authenticate",
        lambda *args, **kwargs: _identity(email=student.email),
    )
    linked = client.post(
        f"/api/auth/sso/ldap/{provider['id']}/login",
        json={"username": "linked", "password": "secret"},
    )
    assert linked.status_code == 200, linked.text
    assert (
        db_session.query(ExternalIdentity)
        .filter(
            ExternalIdentity.provider_id == provider["id"],
            ExternalIdentity.user_id == student.id,
        )
        .count()
        == 1
    )
    assert db_session.query(User).filter(User.email == student.email).count() == 1

    monkeypatch.setattr(
        ldap_auth,
        "authenticate",
        lambda *args, **kwargs: _identity(email=admin.email),
    )
    blocked = client.post(
        f"/api/auth/sso/ldap/{provider['id']}/login",
        json={"username": "admin", "password": "secret"},
    )
    assert blocked.status_code == 400
    assert (
        db_session.query(ExternalIdentity)
        .filter(ExternalIdentity.user_id == admin.id)
        .count()
        == 0
    )


def test_ldap_provider_test_endpoint(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _ldap_provider(client, headers)
    monkeypatch.setattr(
        ldap_auth,
        "test_provider",
        lambda row: {"message": "LDAP bind OK", "base_dn": "ou=people"},
    )
    resp = client.post(
        f"/api/identity/providers/{provider['id']}/test", headers=headers
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["ok"] is True
    assert resp.json()["message"] == "LDAP bind OK"


# ----------------------------------------------------------------------- SAML


def test_saml_provider_requires_idp_certificate(client, db_session):
    headers = _admin(client, db_session)
    suffix = _suffix()
    resp = client.post(
        "/api/identity/providers",
        json={
            "name": f"SSO Test SAML {suffix}",
            "kind": "saml",
            "enabled": True,
            "config": {
                "idp_entity_id": "https://idp.example.edu/metadata",
                "sp_entity_id": "https://ocr.example.edu/saml/metadata",
                "sso_url": "https://idp.example.edu/sso",
            },
        },
        headers=headers,
    )
    assert resp.status_code == 400
    assert "idp_x509_cert" in resp.text


def test_saml_processes_real_signed_assertion(client, db_session, monkeypatch):
    monkeypatch.setattr(
        saml_auth, "public_base_url", lambda: "https://ocr.example.edu"
    )
    headers = _admin(client, db_session)
    key_pem, cert_pem = _make_keypair()
    created = _saml_provider(
        client, headers, config={"idp_x509_cert": cert_pem}
    )
    provider = (
        db_session.query(IdentityProvider)
        .filter(IdentityProvider.id == created["id"])
        .first()
    )
    request_id = "ONELOGIN_real_request"
    post = _signed_response(
        provider,
        request_id,
        "saml.real@example.org",
        ["CN=Instructors,OU=Groups,DC=example,DC=edu"],
        key_pem,
        cert_pem,
    )
    identity, session = saml_auth.process_response(provider, post, request_id)
    assert identity.email == "saml.real@example.org"
    assert identity.subject == "saml.real@example.org"
    assert identity.groups == ["CN=Instructors,OU=Groups,DC=example,DC=edu"]
    assert session["session_index"] == "session-e2e"


def test_saml_acs_router_accepts_real_signed_assertion(
    client, db_session, monkeypatch
):
    monkeypatch.setattr(
        saml_auth, "public_base_url", lambda: "https://ocr.example.edu"
    )
    headers = _admin(client, db_session)
    key_pem, cert_pem = _make_keypair()
    created = _saml_provider(
        client, headers, config={"idp_x509_cert": cert_pem}
    )
    provider = (
        db_session.query(IdentityProvider)
        .filter(IdentityProvider.id == created["id"])
        .first()
    )
    request_id = "ONELOGIN_router_request"
    monkeypatch.setattr(
        saml_auth,
        "start_login",
        lambda row, relay: ("https://idp.example.edu/sso?SAMLRequest=fake", request_id),
    )
    started = client.get(
        f"/api/auth/sso/saml/{provider.id}/login?return_to=/profile",
        follow_redirects=False,
    )
    assert started.status_code == 302, started.text

    state_row = (
        db_session.query(SsoLoginState)
        .filter(SsoLoginState.provider_id == provider.id)
        .order_by(SsoLoginState.id.desc())
        .first()
    )
    post = _signed_response(
        provider,
        request_id,
        "saml.router@example.org",
        ["CN=Instructors,OU=Groups,DC=example,DC=edu"],
        key_pem,
        cert_pem,
    )
    post["RelayState"] = state_row.state
    acs = client.post(
        f"/api/auth/sso/saml/{provider.id}/acs",
        data=post,
        follow_redirects=False,
    )
    assert acs.status_code == 302, acs.text
    ticket = parse_qs(urlparse(acs.headers["location"]).query)["ticket"][0]
    exchanged = client.post("/api/auth/sso/exchange", json={"ticket": ticket})
    assert exchanged.status_code == 200, exchanged.text
    assert exchanged.json()["user"]["email"] == "saml.router@example.org"
    assert exchanged.json()["user"]["role"] == "instructor"


def test_saml_rejects_unsigned_assertion(client, db_session, monkeypatch):
    monkeypatch.setattr(
        saml_auth, "public_base_url", lambda: "https://ocr.example.edu"
    )
    headers = _admin(client, db_session)
    key_pem, cert_pem = _make_keypair()
    created = _saml_provider(
        client, headers, config={"idp_x509_cert": cert_pem}
    )
    provider = (
        db_session.query(IdentityProvider)
        .filter(IdentityProvider.id == created["id"])
        .first()
    )
    request_id = "ONELOGIN_unsigned_request"
    post = _signed_response(
        provider,
        request_id,
        "saml.unsigned@example.org",
        [],
        key_pem,
        cert_pem,
        sign=False,
    )
    with pytest.raises(SSOError):
        saml_auth.process_response(provider, post, request_id)


def test_saml_login_and_acs_provision(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _saml_provider(client, headers)
    identity = _saml_identity()

    monkeypatch.setattr(
        saml_auth,
        "start_login",
        lambda row, relay: ("https://idp.example.edu/sso?SAMLRequest=fake", "request-123"),
    )
    started = client.get(
        f"/api/auth/sso/saml/{provider['id']}/login?return_to=/profile",
        follow_redirects=False,
    )
    assert started.status_code == 302, started.text
    assert started.headers["location"].startswith("https://idp.example.edu/sso")

    state_row = (
        db_session.query(SsoLoginState)
        .filter(SsoLoginState.provider_id == provider["id"])
        .order_by(SsoLoginState.id.desc())
        .first()
    )
    assert state_row is not None
    assert state_row.nonce == "request-123"
    assert state_row.return_to == "/profile"

    monkeypatch.setattr(
        saml_auth,
        "process_response",
        lambda row, data, request_id: (identity, {"session_index": "sess-1"}),
    )
    acs = client.post(
        f"/api/auth/sso/saml/{provider['id']}/acs",
        data={"RelayState": state_row.state, "SAMLResponse": "fake"},
        follow_redirects=False,
    )
    assert acs.status_code == 302, acs.text
    location = acs.headers["location"]
    query = parse_qs(urlparse(location).query)
    assert query["return_to"] == ["/profile"]
    ticket = query["ticket"][0]

    exchanged = client.post("/api/auth/sso/exchange", json={"ticket": ticket})
    assert exchanged.status_code == 200, exchanged.text
    assert exchanged.json()["user"]["email"] == identity.email
    assert exchanged.json()["user"]["role"] == "student"

    user = db_session.query(User).filter(User.email == identity.email).first()
    assert user is not None
    assert user.password_login_disabled is True
    link = (
        db_session.query(ExternalIdentity)
        .filter(
            ExternalIdentity.provider_id == provider["id"],
            ExternalIdentity.subject == identity.subject,
        )
        .first()
    )
    assert link is not None and link.user_id == user.id

    replay = client.post(
        f"/api/auth/sso/saml/{provider['id']}/acs",
        data={"RelayState": state_row.state, "SAMLResponse": "fake"},
        follow_redirects=False,
    )
    assert replay.status_code == 302
    assert "error=sso_failed" in replay.headers["location"]


def test_saml_acs_can_run_on_a_second_replica(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _saml_provider(client, headers)
    identity = _saml_identity()

    monkeypatch.setattr(
        saml_auth,
        "start_login",
        lambda row, relay: ("https://idp.example.edu/sso?SAMLRequest=fake", "request-abc"),
    )
    started = client.get(
        f"/api/auth/sso/saml/{provider['id']}/login",
        follow_redirects=False,
    )
    assert started.status_code == 302

    state_row = (
        db_session.query(SsoLoginState)
        .filter(SsoLoginState.provider_id == provider["id"])
        .order_by(SsoLoginState.id.desc())
        .first()
    )
    monkeypatch.setattr(
        saml_auth,
        "process_response",
        lambda row, data, request_id: (identity, {"session_index": "sess-2"}),
    )

    from app.main import app
    from fastapi.testclient import TestClient

    second = TestClient(app)
    acs = second.post(
        f"/api/auth/sso/saml/{provider['id']}/acs",
        data={"RelayState": state_row.state, "SAMLResponse": "fake"},
        follow_redirects=False,
    )
    assert acs.status_code == 302, acs.text
    ticket = parse_qs(urlparse(acs.headers["location"]).query)["ticket"][0]
    exchanged = second.post("/api/auth/sso/exchange", json={"ticket": ticket})
    assert exchanged.status_code == 200, exchanged.text


def test_saml_pending_approval_returns_error(client, db_session, monkeypatch):
    headers = _admin(client, db_session)
    provider = _saml_provider(client, headers, config={"auto_approve": False})
    identity = _saml_identity()

    monkeypatch.setattr(
        saml_auth,
        "start_login",
        lambda row, relay: ("https://idp.example.edu/sso?SAMLRequest=fake", "request-pending"),
    )
    client.get(
        f"/api/auth/sso/saml/{provider['id']}/login",
        follow_redirects=False,
    )
    state_row = (
        db_session.query(SsoLoginState)
        .filter(SsoLoginState.provider_id == provider["id"])
        .order_by(SsoLoginState.id.desc())
        .first()
    )
    monkeypatch.setattr(
        saml_auth,
        "process_response",
        lambda row, data, request_id: (identity, {"session_index": "sess-3"}),
    )
    acs = client.post(
        f"/api/auth/sso/saml/{provider['id']}/acs",
        data={"RelayState": state_row.state, "SAMLResponse": "fake"},
        follow_redirects=False,
    )
    assert acs.status_code == 302
    assert "error=pending_approval" in acs.headers["location"]
    user = db_session.query(User).filter(User.email == identity.email).first()
    assert user is not None and user.is_approved is False


def test_saml_requires_relay_state(client, db_session):
    headers = _admin(client, db_session)
    provider = _saml_provider(client, headers)
    acs = client.post(
        f"/api/auth/sso/saml/{provider['id']}/acs",
        data={"SAMLResponse": "fake"},
        follow_redirects=False,
    )
    assert acs.status_code == 302
    assert "error=invalid_request" in acs.headers["location"]
