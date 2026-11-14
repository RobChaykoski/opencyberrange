"""Regression tests for SSO hardening: redirects, algorithms, and LDAP transport."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.services import ldap_auth, oidc
from app.services.external_identity import SSOError
from app.services.sso_flow import sanitize_return_to
from app.crypto import encrypt_secret
from app.routers.identity import _export_provider


@pytest.mark.parametrize(
    "value",
    ["/dashboard", "/courses/1?tab=reviews", "/exercises/windows?labId=141&tab=workbook"],
)
def test_return_to_accepts_site_paths(value):
    assert sanitize_return_to(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "https://evil.example",
        "//evil.example",
        "/\\evil.example",
        "/\t/evil.example",
        "/\r\n/evil.example",
        "javascript:alert(1)",
    ],
)
def test_return_to_rejects_offsite_and_control_characters(value):
    assert sanitize_return_to(value) == "/dashboard"


def test_oidc_algorithms_keep_asymmetric_only():
    document = {
        "id_token_signing_alg_values_supported": [
            "RS256",
            "ES256",
            "HS256",
            "none",
        ]
    }
    assert oidc.allowed_id_token_algorithms(document) == ["RS256", "ES256"]


def test_oidc_algorithms_default_to_rs256():
    assert oidc.allowed_id_token_algorithms({}) == ["RS256"]


def test_oidc_algorithms_fail_closed_without_asymmetric_support():
    with pytest.raises(SSOError):
        oidc.allowed_id_token_algorithms(
            {"id_token_signing_alg_values_supported": ["HS256", "none"]}
        )


def _ldap_provider(config: dict) -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        name="LDAP hardening test",
        config=json.dumps(config),
        secrets=None,
    )


def test_ldap_plaintext_is_rejected_by_default():
    provider = _ldap_provider({"server_url": "ldap://directory.example.edu"})
    with pytest.raises(SSOError):
        ldap_auth._connection(provider)


def test_ldap_plaintext_opt_in_does_not_trip_the_guard(monkeypatch):
    calls = {}

    class FakeConnection:
        closed = False

        def __init__(self, *args, **kwargs):
            calls.update(kwargs)

        def open(self):
            calls["opened"] = True

        def unbind(self):
            pass

    monkeypatch.setattr(ldap_auth, "Connection", FakeConnection)
    provider = _ldap_provider(
        {
            "server_url": "ldap://directory.example.edu",
            "allow_plaintext": True,
        }
    )
    ldap_auth._connection(provider)
    assert calls["auto_referrals"] is False
    assert calls["opened"] is True


def test_provider_export_never_includes_secret_values():
    row = SimpleNamespace(
        name="Campus OIDC",
        kind="oidc",
        enabled=True,
        is_default=False,
        config=json.dumps({"issuer": "https://idp.example.edu", "client_id": "ocr"}),
        secrets=encrypt_secret(json.dumps({"client_secret": "super-secret-value"})),
    )
    exported = _export_provider(row)
    serialized = json.dumps(exported)
    assert "super-secret-value" not in serialized
    assert "secrets" not in exported
    assert exported["secret_keys"] == ["client_secret"]
    assert exported["has_secrets"] is True
