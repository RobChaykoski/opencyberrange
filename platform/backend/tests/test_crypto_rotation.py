"""Fernet envelope and rotation behavior."""

from __future__ import annotations

from cryptography.fernet import Fernet

from app import crypto
from app.config import settings
from app.services import settings_service


def _use_keys(monkeypatch, primary: str, previous: str = ""):
    monkeypatch.setattr(settings, "WG_ENCRYPTION_KEY", primary, raising=False)
    monkeypatch.setattr(
        settings, "WG_ENCRYPTION_KEY_PREVIOUS", previous, raising=False
    )
    crypto.reset_cache()


def test_v1_envelope_round_trips(monkeypatch):
    key = Fernet.generate_key().decode()
    _use_keys(monkeypatch, key)

    token = crypto.encrypt_secret("correct horse battery staple")
    assert token.startswith("v1:")
    assert crypto.is_encrypted(token)
    assert crypto.decrypt_secret(token) == "correct horse battery staple"
    assert crypto.needs_reencryption(token) is False


def test_previous_key_decrypts_old_rows(monkeypatch):
    old_key = Fernet.generate_key().decode()
    new_key = Fernet.generate_key().decode()

    _use_keys(monkeypatch, old_key)
    old_token = crypto.encrypt_secret("rotate me")

    _use_keys(monkeypatch, new_key, previous=old_key)
    assert crypto.decrypt_secret(old_token) == "rotate me"
    assert crypto.needs_reencryption(old_token) is True

    new_token = crypto.encrypt_secret("rotate me")
    assert crypto.needs_reencryption(new_token) is False
    assert crypto.decrypt_secret(new_token) == "rotate me"


def test_legacy_bare_token_still_decrypts(monkeypatch):
    key = Fernet.generate_key().decode()
    _use_keys(monkeypatch, key)
    legacy = Fernet(key.encode()).encrypt(b"legacy secret").decode()

    assert crypto.is_encrypted(legacy)
    assert crypto.decrypt_secret(legacy) == "legacy secret"
    assert crypto.needs_reencryption(legacy) is True


def test_malformed_token_raises_value_error(monkeypatch):
    key = Fernet.generate_key().decode()
    _use_keys(monkeypatch, key)

    try:
        crypto.decrypt_secret("v1:not-a-token")
    except ValueError:
        pass
    else:  # pragma: no cover - the assertion is the contract
        raise AssertionError("malformed token should raise ValueError")


def test_aliases_keep_the_wireguard_contract(monkeypatch):
    key = Fernet.generate_key().decode()
    _use_keys(monkeypatch, key)

    token = crypto.encrypt_private_key("wg-private")
    assert crypto.decrypt_private_key(token) == "wg-private"


def test_secret_settings_are_encrypted_at_rest(monkeypatch):
    key = Fernet.generate_key().decode()
    _use_keys(monkeypatch, key)

    ciphertext = settings_service._protect("mail_password", "smtp-secret")
    assert ciphertext.startswith("v1:")
    assert settings_service._reveal("mail_password", ciphertext) == "smtp-secret"
    assert settings_service._protect("mail_host", "smtp.example.com") == "smtp.example.com"
