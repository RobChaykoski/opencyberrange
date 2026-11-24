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


def _production(monkeypatch):
    monkeypatch.setattr(config.settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(config.settings, "OCR_DEPLOYMENT_MODE", "production")
    monkeypatch.setattr(config.settings, "OCR_AUTHZ_STRICT", True)
    monkeypatch.setattr(
        config.settings,
        "DATABASE_URL",
        "postgresql://ocr_runtime:runtime@db:5432/ocr",
    )
    monkeypatch.setattr(
        config.settings,
        "MIGRATOR_DATABASE_URL",
        "postgresql://ocr_migrator:migrator@db:5432/ocr",
    )
    monkeypatch.setattr(config.settings, "JWT_SECRET", "a" * 64)
    monkeypatch.setattr(config.settings, "REPORT_SIGNING_KEY", "b" * 64)
    monkeypatch.setattr(config.settings, "SETUP_TOKEN", "c" * 64)
    monkeypatch.setattr(
        config.settings,
        "WG_ENCRYPTION_KEY",
        "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
    )


def test_production_requires_strict_authorization(monkeypatch):
    _production(monkeypatch)
    monkeypatch.setattr(config.settings, "OCR_AUTHZ_STRICT", False)
    with pytest.raises(ValueError, match="OCR_AUTHZ_STRICT"):
        config.validate_settings()


def test_production_deployment_mode_requires_production_environment(monkeypatch):
    _production(monkeypatch)
    monkeypatch.setattr(config.settings, "ENVIRONMENT", "development")
    with pytest.raises(ValueError, match="OCR_DEPLOYMENT_MODE=production"):
        config.validate_settings()


def test_production_requires_wireguard_key_encryption(monkeypatch):
    _production(monkeypatch)
    monkeypatch.setattr(config.settings, "WG_ENCRYPTION_KEY", "")
    with pytest.raises(ValueError, match="WG_ENCRYPTION_KEY"):
        config.validate_settings()


def test_valid_production_configuration_is_accepted(monkeypatch):
    _production(monkeypatch)
    config.validate_settings()

def test_malformed_wireguard_key_is_rejected(monkeypatch):
    _production(monkeypatch)
    monkeypatch.setattr(config.settings, "WG_ENCRYPTION_KEY", "not-a-fernet-key")
    with pytest.raises(ValueError, match="Fernet"):
        config.validate_settings()


def test_malformed_previous_wireguard_key_is_rejected(monkeypatch):
    _production(monkeypatch)
    monkeypatch.setattr(
        config.settings, "WG_ENCRYPTION_KEY_PREVIOUS", "not-a-fernet-key"
    )
    with pytest.raises(ValueError, match="WG_ENCRYPTION_KEY_PREVIOUS"):
        config.validate_settings()
