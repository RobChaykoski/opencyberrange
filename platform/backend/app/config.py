"""
Application configuration
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database - MUST be set via environment variable in production
    DATABASE_URL: str = ""
    
    # JWT - MUST be set via environment variable (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(64))")
    JWT_SECRET: str = ""
    SETUP_TOKEN: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Dedicated key for report manifests. Empty falls back to JWT_SECRET with
    # domain separation. Keep it stable so old reports remain verifiable.
    REPORT_SIGNING_KEY: str = ""
    
    # CORS - set via environment variable to match your domain
    CORS_ORIGINS: str = "https://localhost"
    
    # WireGuard Server — set via environment variable
    WG_SERVER_ENDPOINT: str = ""
    WG_SERVER_PUBLIC_KEY: str = ""

    # Peer Manager API (local WireGuard peer management)
    # NOTE: Use host.docker.internal when backend runs in a Docker container
    WG_API_URL: str = "http://host.docker.internal:5000"
    WG_API_KEY: str = ""
    
    # WireGuard key encryption - MUST be set (generate with: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    WG_ENCRYPTION_KEY: str = ""
    # Comma-separated old keys, used only for decryption during rotation.
    WG_ENCRYPTION_KEY_PREVIOUS: str = ""
    
    # Network bases
    WG_NETWORK_BASE: str = "10.100"
    # VPN client pool. A 2-octet base is a /16 (~62k peers); a 3-octet base
    # (e.g. "10.0.0") would cap the pool at one /24 (~245). Keep it /16 so the
    # peer count is never the constraint. The server + client configs use a
    # matching /16 mask (setup-vpn.sh, wireguard_manager.py).
    WG_CLIENT_BASE: str = "10.255"
    
    # Labs host path — absolute path on the HOST to the labs/ directory.
    # The backend needs this to mount lab volumes when spawning containers.
    # MUST be set via LABS_HOST_PATH in .env (e.g. /opt/opencyberrange/platform/labs)
    LABS_HOST_PATH: str = ""

    # Server public hostname (for general use)
    SERVER_PUBLIC_HOST: str = "localhost"

    # SSO / OIDC. PUBLIC_BASE_URL must be the stable external origin; the OIDC
    # redirect URI is derived from it, not from the request Host header.
    PUBLIC_BASE_URL: str = ""
    FRONTEND_BASE_URL: str = ""
    SSO_STATE_TTL_SECONDS: int = 600
    SSO_TICKET_TTL_SECONDS: int = 120
    SSO_HTTP_TIMEOUT_SECONDS: int = 10
    SSO_DISCOVERY_CACHE_SECONDS: int = 300
    # Local development only. Production issuers must be https://.
    SSO_ALLOW_INSECURE_HTTP: bool = False

    # Contact shown in the survey privacy statement and other privacy notices.
    PRIVACY_CONTACT_EMAIL: str = "privacy@swocts.com"
    
    class Config:
        env_file = ".env"


settings = Settings()


_PLACEHOLDER_SECRET_MARKERS = (
    "change_me",
    "change-me",
    "change-in-production",
    "your-super-secret",
    "placeholder",
    "example",
)


def _is_placeholder_secret(value: str) -> bool:
    """True when a secret still contains an obvious template marker."""
    lowered = str(value or "").strip().lower()
    return any(marker in lowered for marker in _PLACEHOLDER_SECRET_MARKERS)


def validate_settings():
    """
    Validate critical security settings on startup.
    Raises ValueError if required settings are missing or insecure.
    """
    import logging
    errors = []
    warnings = []
    
    # Validate DATABASE_URL
    if not settings.DATABASE_URL:
        errors.append(
            "DATABASE_URL must be set via environment variable. "
            "Example: postgresql://user:password@host:5432/dbname"
        )
    elif "labpass" in settings.DATABASE_URL:
        # Soft warning for development - change before production
        warnings.append(
            "DATABASE_URL contains default password. Change before production deployment."
        )
    
    # Validate JWT_SECRET
    if not settings.JWT_SECRET:
        errors.append(
            "JWT_SECRET must be set via environment variable. "
            "Generate with: python3 -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )
    elif len(settings.JWT_SECRET) < 32:
        errors.append(
            "JWT_SECRET must be at least 32 characters for security."
        )
    elif _is_placeholder_secret(settings.JWT_SECRET):
        errors.append(
            "JWT_SECRET contains a default/placeholder value. "
            "Generate a unique random secret before starting the platform."
        )

    # Validate SETUP_TOKEN when the operator chose to gate first-run setup.
    if settings.SETUP_TOKEN and _is_placeholder_secret(settings.SETUP_TOKEN):
        errors.append(
            "SETUP_TOKEN contains a default/placeholder value. "
            "Generate a unique random token before starting the platform."
        )
    
    # Validate LABS_HOST_PATH
    if not settings.LABS_HOST_PATH:
        warnings.append(
            "LABS_HOST_PATH not set. Lab spawning will fail. "
            "Set to the absolute host path of the labs/ directory (e.g. /opt/opencyberrange/platform/labs)."
        )

    # Validate WG_ENCRYPTION_KEY (only if VPN features are used)
    if not settings.WG_ENCRYPTION_KEY:
        warnings.append(
            "WG_ENCRYPTION_KEY not set. WireGuard private keys will not be encrypted. "
            "Generate with: python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    
    # Log warnings
    for warning in warnings:
        logging.warning(f"Security config: {warning}")
    
    # Only raise errors for truly critical issues
    if errors:
        raise ValueError(
            "Security configuration errors:\n" + 
            "\n".join(f"  - {e}" for e in errors)
        )


# Validate settings on import
validate_settings()
