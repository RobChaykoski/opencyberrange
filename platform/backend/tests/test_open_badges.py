"""Open Badges signing and status regression tests."""

from __future__ import annotations

import base64
from types import SimpleNamespace

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.services.open_badges import _b64url, credential_status


def test_ed25519_jwt_round_trip_and_tamper_detection():
    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    token = jwt.encode(
        {
            "iss": "https://range.example.edu",
            "sub": "https://range.example.edu/api/badges/subjects/abc",
            "jti": "credential-1",
            "vc": {"type": ["VerifiableCredential", "OpenBadgeCredential"]},
        },
        private,
        algorithm="EdDSA",
        headers={"kid": "test-key", "typ": "JWT"},
    )
    claims = jwt.decode(
        token,
        public,
        algorithms=["EdDSA"],
        options={"verify_aud": False},
    )
    assert claims["jti"] == "credential-1"
    assert claims["vc"]["type"][-1] == "OpenBadgeCredential"

    header = jwt.get_unverified_header(token)
    assert header["alg"] == "EdDSA"
    assert header["kid"] == "test-key"

    header_part, payload_part, signature_part = token.split(".")
    flipped = ("A" if payload_part[0] != "A" else "B") + payload_part[1:]
    tampered = ".".join((header_part, flipped, signature_part))
    try:
        jwt.decode(tampered, public, algorithms=["EdDSA"], options={"verify_aud": False})
    except jwt.PyJWTError:
        pass
    else:
        raise AssertionError("tampered token verified")


def test_public_key_raw_encoding_is_urlsafe_base64():
    private = Ed25519PrivateKey.generate()
    raw = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    encoded = _b64url(raw)
    assert "=" not in encoded
    assert base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)) == raw


def test_credential_status_values():
    assert credential_status(SimpleNamespace(revoked_at=None)) == "active"
    assert credential_status(SimpleNamespace(revoked_at="now")) == "revoked"
