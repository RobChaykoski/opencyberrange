"""Security configuration must reject template secrets at startup."""

import pytest

import app.config as config


def test_placeholder_jwt_secret_is_rejected(monkeypatch):
    monkeypatch.setattr(
        config.settings, "JWT_SECRET", "CHANGE_ME_generate_with_token_hex_32"
    )
    monkeypatch.setattr(config.settings, "SETUP_TOKEN", "")
    with pytest.raises(ValueError, match="JWT_SECRET"):
        config.validate_settings()


def test_placeholder_setup_token_is_rejected(monkeypatch):
    monkeypatch.setattr(
        config.settings, "JWT_SECRET", "a" * 64
    )
    monkeypatch.setattr(
        config.settings, "SETUP_TOKEN", "CHANGE_ME_generate_with_token_hex_32"
    )
    with pytest.raises(ValueError, match="SETUP_TOKEN"):
        config.validate_settings()


def test_random_secrets_are_accepted(monkeypatch):
    monkeypatch.setattr(config.settings, "JWT_SECRET", "a" * 64)
    monkeypatch.setattr(config.settings, "SETUP_TOKEN", "b" * 64)
    config.validate_settings()
