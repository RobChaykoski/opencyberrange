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


def _oidc_provider(issuer: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        name="OIDC issuer test",
        config=json.dumps({"issuer": issuer, "client_id": "ocr-client"}),
        secrets=None,
    )


def _mock_id_token(monkeypatch, claims: dict) -> None:
    document = {
        "issuer": "https://auth.example.edu/application/o/ocr/",
        "id_token_signing_alg_values_supported": ["RS256"],
    }

    class Key:
        key = object()

    class JWKClient:
        def get_signing_key_from_jwt(self, token):
            return Key()

    monkeypatch.setattr(oidc, "discover", lambda provider: document)
    monkeypatch.setattr(oidc, "_jwk_client", lambda document: JWKClient())
    monkeypatch.setattr(oidc.jwt, "decode", lambda *args, **kwargs: claims)


@pytest.mark.parametrize(
    "configured,claimed",
    [
        ("https://auth.example.edu/application/o/ocr/", "https://auth.example.edu/application/o/ocr/"),
        ("https://auth.example.edu/application/o/ocr", "https://auth.example.edu/application/o/ocr/"),
        ("https://auth.example.edu/application/o/ocr/", "https://auth.example.edu/application/o/ocr"),
    ],
)
def test_oidc_issuer_trailing_slash_is_normalized(monkeypatch, configured, claimed):
    _mock_id_token(monkeypatch, {"iss": claimed, "nonce": "nonce", "sub": "subject"})
    claims = oidc.validate_id_token(
        _oidc_provider(configured), "signed-token", "nonce"
    )
    assert claims["sub"] == "subject"


def test_oidc_issuer_mismatch_is_rejected(monkeypatch):
    _mock_id_token(
        monkeypatch,
        {"iss": "https://evil.example/application/o/ocr/", "nonce": "nonce", "sub": "subject"},
    )
    with pytest.raises(SSOError):
        oidc.validate_id_token(
            _oidc_provider("https://auth.example.edu/application/o/ocr/"),
            "signed-token",
            "nonce",
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
