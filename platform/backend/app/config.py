"""
Application configuration
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database - MUST be set via environment variable in production
    DATABASE_URL: str = ""
    # Schema owner / migration identity. Production requires a role that is
    # different from the runtime role, so runtime traffic is subject to RLS.
    MIGRATOR_DATABASE_URL: str = ""
    # Optional least-privilege dump identity. Falls back to the migrator role,
    # then the runtime role. Use a read-only role with BYPASSRLS in production.
    BACKUP_DATABASE_URL: str = ""
    
    # JWT - MUST be set via environment variable (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(64))")
    JWT_SECRET: str = ""
    ENVIRONMENT: str = "development"
    # production | development | test. An explicit deployment mode lets a
    # production-intended host fail closed if ENVIRONMENT is misconfigured.
    OCR_DEPLOYMENT_MODE: str = ""
    # Production must refuse startup when a protected route lacks an
    # authorization dependency. route_audit reads the same variable.
    OCR_AUTHZ_STRICT: bool = False
    SETUP_TOKEN: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "opencyberrange"
    JWT_AUDIENCE: str = "ocr-api"
    JWT_LEEWAY_SECONDS: int = 30
    JWT_EXPIRATION_HOURS: int = 24
    REFRESH_TOKEN_DAYS: int = 30
    SESSION_MAX_PER_USER: int = 10
    # Explicit Argon2id baseline. Memory cost is KiB; time cost is iterations.
    ARGON2_TIME_COST: int = 3
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 4
    ARGON2_HASH_LEN: int = 32
    ARGON2_SALT_LEN: int = 16
    PASSWORD_REHASH_DAYS: int = 365

    # Dedicated key for report manifests. Empty falls back to JWT_SECRET with
    # domain separation. Keep it stable so old reports remain verifiable.
    REPORT_SIGNING_KEY: str = ""
    
    # CORS - set via environment variable to match your domain
    CORS_ORIGINS: str = "https://localhost"
    
    # WireGuard Server — set via environment variable
    WG_SERVER_ENDPOINT: str = ""
    WG_SERVER_PUBLIC_KEY: str = ""
    # This host's address on wg0. Two HA hosts must not both use 10.0.0.1.
    WG_SERVER_ADDRESS: str = "10.0.0.1"

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

    # Wiki origin split. When WIKI_COOKIE_DOMAIN is set (for example
    # ".example.edu"), the wiki session cookie is scoped to the parent domain so
    # a wiki served from a sibling hostname can authenticate its subresources.
    # Leave empty for a same-origin wiki.
    WIKI_COOKIE_DOMAIN: str = ""

    # SSO / OIDC. PUBLIC_BASE_URL must be the stable external origin; the OIDC
    # redirect URI is derived from it, not from the request Host header.
    PUBLIC_BASE_URL: str = ""
    FRONTEND_BASE_URL: str = ""
    SSO_STATE_TTL_SECONDS: int = 600
    # LTI 1.3 login state is as short-lived as the SSO flow.
    LTI_STATE_TTL_SECONDS: int = 600
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
    environment = (settings.ENVIRONMENT or "development").strip().lower()
    production = environment in {"production", "prod"}
    deployment_mode = (settings.OCR_DEPLOYMENT_MODE or "").strip().lower()
    production_mode = deployment_mode in {"production", "prod"}

    if environment not in {"development", "test", "production", "prod"}:
        errors.append(
            "ENVIRONMENT must be development, test, or production; "
            f"got {settings.ENVIRONMENT!r}."
        )
    if deployment_mode and deployment_mode not in {
        "development",
        "test",
        "production",
        "prod",
    }:
        errors.append(
            "OCR_DEPLOYMENT_MODE must be development, test, or production; "
            f"got {settings.OCR_DEPLOYMENT_MODE!r}."
        )
    if production_mode and not production:
        errors.append(
            "OCR_DEPLOYMENT_MODE=production requires ENVIRONMENT=production. "
            "Refusing to start a production-intended host with a non-production "
            "environment."
        )
    if production:
        if not settings.OCR_AUTHZ_STRICT:
            errors.append(
                "OCR_AUTHZ_STRICT=1 is required in production so a protected "
                "route without an authorization dependency stops startup."
            )
        if not settings.WG_ENCRYPTION_KEY:
            errors.append(
                "WG_ENCRYPTION_KEY is required in production; WireGuard private "
                "keys must never be stored unencrypted."
            )

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

    if production:
        if not settings.MIGRATOR_DATABASE_URL:
            errors.append(
                "MIGRATOR_DATABASE_URL must be set in production so schema "
                "changes run as the migrator role, not the runtime role."
            )
        elif settings.MIGRATOR_DATABASE_URL == settings.DATABASE_URL:
            errors.append(
                "MIGRATOR_DATABASE_URL must use a different role from "
                "DATABASE_URL so the runtime identity cannot bypass RLS."
            )
        if (
            settings.BACKUP_DATABASE_URL
            and settings.BACKUP_DATABASE_URL == settings.DATABASE_URL
        ):
            errors.append(
                "BACKUP_DATABASE_URL must not use the runtime role; pg_dump "
                "must run as a role with BYPASSRLS."
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

    # Report manifests need a signing key independent of JWT. A shared key
    # means one compromise forges both sessions and report evidence.
    if not settings.REPORT_SIGNING_KEY:
        message = (
            "REPORT_SIGNING_KEY is not set; report signing falls back to "
            "JWT_SECRET. Set a separate 32+ character key in production."
        )
        (errors if production else warnings).append(message)
    else:
        if len(settings.REPORT_SIGNING_KEY) < 32:
            errors.append("REPORT_SIGNING_KEY must be at least 32 characters.")
        if settings.REPORT_SIGNING_KEY == settings.JWT_SECRET:
            message = (
                "REPORT_SIGNING_KEY must not equal JWT_SECRET; use a separate "
                "key so session and report compromise are independent."
            )
            (errors if production else warnings).append(message)

    # Validate SETUP_TOKEN. First-run setup requires it in every deployment.
    if settings.SETUP_TOKEN and _is_placeholder_secret(settings.SETUP_TOKEN):
        errors.append(
            "SETUP_TOKEN contains a default/placeholder value. "
            "Generate a unique random token before starting the platform."
        )
    if not settings.SETUP_TOKEN:
        warnings.append(
            "SETUP_TOKEN is not set. First-run setup will be blocked until the "
            "operator configures it."
        )
    
    # Validate LABS_HOST_PATH
    if not settings.LABS_HOST_PATH:
        warnings.append(
            "LABS_HOST_PATH not set. Lab spawning will fail. "
            "Set to the absolute host path of the labs/ directory (e.g. /opt/opencyberrange/platform/labs)."
        )

    # Validate WG_ENCRYPTION_KEY. A VPN-enabled deployment must never store a
    # private key in plaintext; production fails closed.
    vpn_configured = bool(
        settings.WG_SERVER_ENDPOINT
        or settings.WG_SERVER_PUBLIC_KEY
        or settings.WG_API_KEY
    )
    if not settings.WG_ENCRYPTION_KEY:
        message = (
            "WG_ENCRYPTION_KEY not set. WireGuard private keys would be stored "
            "unencrypted. Generate with: python3 -c "
            "\"from cryptography.fernet import Fernet; "
            "print(Fernet.generate_key().decode())\""
        )
        (errors if (production or vpn_configured) else warnings).append(message)
    
    # Log warnings
    for warning in warnings:
        logging.warning(f"Security config: {warning}")
    
    # Only raise errors for truly critical issues
    if errors:
        raise ValueError(
            "Security configuration errors:\n" + 
            "\n".join(f"  - {e}" for e in errors)
        )


# Validation runs from the application startup hook (app.main lifespan).
