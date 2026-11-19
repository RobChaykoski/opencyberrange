"""
Platform settings service - provides cached read/write access to
runtime-configurable settings stored in the platform_settings table.

Settings fall back to config.py (environment) defaults when not
present in the database, so existing .env deployments keep working.
"""

import logging
import os
import time as _time
from typing import Optional, Dict, List

from sqlalchemy.orm import Session

from app.crypto import decrypt_secret, encrypt_secret, is_encrypted
from app.models import PlatformSetting

logger = logging.getLogger(__name__)

# In-memory cache with TTL: populated on first read, invalidated on write.
# The TTL ensures multi-worker deployments see fresh settings within
# _CACHE_TTL_SECONDS even if another worker performed the update.
_cache: Dict[str, str] = {}
_cache_loaded = False
_cache_loaded_at: float = 0.0
_CACHE_TTL_SECONDS = 30  # re-read from DB at most every 30 seconds

# Default settings with metadata.  These are seeded into the DB on
# first startup and serve as documentation for what's configurable.
DEFAULT_SETTINGS = [
    # --- General ---
    {"key": "setup_complete", "value": "false", "category": "general",
     "description": "Set to true after first-run setup wizard completes", "is_secret": False},
    {"key": "certificate_verify_url", "value": "", "category": "general",
     "description": "Base URL used in certificate QR codes for verification (e.g. https://range.example.com). Empty uses the request host.", "is_secret": False},
    {"key": "certificate_design", "value": "classic", "category": "general",
     "description": "Default certificate design: classic, executive, modern, or minimal", "is_secret": False},
    {"key": "export_label_enabled", "value": "true", "category": "exports",
     "description": "Add a data-classification label and handling note to exported PDFs, CSV files, and download responses.", "is_secret": False},
    {"key": "export_classification", "value": "internal", "category": "exports",
     "description": "Default data classification for exported files: public, internal, confidential, or restricted.", "is_secret": False},
    {"key": "export_organisation", "value": "", "category": "exports",
     "description": "Organisation name recorded as the author/owner of exported files. Empty uses SWOCTS Cyber Range.", "is_secret": False},
    {"key": "export_handling_note", "value": "", "category": "exports",
     "description": "Optional handling instruction added to export metadata, for example 'Contains learner records. Share only with authorised staff.'", "is_secret": False},
    {"key": "export_include_timestamp", "value": "true", "category": "exports",
     "description": "Record the generation time in export metadata and response headers.", "is_secret": False},
    {"key": "data_label_enforcement_enabled", "value": "false", "category": "exports",
     "description": "Enforce the data-label policy on downloads. When off, exports are labelled but never denied. When on, role, region, and label ceilings are applied and Restricted exports are blocked by default.", "is_secret": False},
    {"key": "data_label_region", "value": "", "category": "exports",
     "description": "Institution region used by the export policy, for example CA, US, EU, or UK. Empty applies no region-specific rule.", "is_secret": False},
    {"key": "data_label_max_export_rank", "value": "3", "category": "exports",
     "description": "Highest label rank allowed in a download: 0 Public, 1 Internal, 2 Confidential, 3 Restricted. The effective ceiling is the lower of this, the role limit, and any region rule.", "is_secret": False},
    {"key": "data_label_block_restricted_exports", "value": "true", "category": "exports",
     "description": "Block Restricted-classified downloads when enforcement is on. Keep this on unless the institution needs password-hash user exports or database backups through the UI.", "is_secret": False},
    {"key": "data_label_custom_levels", "value": "", "category": "exports",
     "description": "Optional JSON list aligning labels to an organisational scheme: [{\"key\":\"public\",\"label\":\"Public\",\"rank\":0,\"handling\":\"...\",\"exportable\":true}, ...]. Empty uses Public/Internal/Confidential/Restricted.", "is_secret": False},
    {"key": "data_label_region_rules", "value": "", "category": "exports",
     "description": "Optional JSON object of region overrides, for example {\"EU\":{\"max_export_rank\":2,\"block_restricted\":true}}. The region setting selects which rule applies.", "is_secret": False},
    {"key": "data_label_role_max_rank", "value": "", "category": "exports",
     "description": "Optional JSON object of per-role ceilings, for example {\"student\":2,\"instructor\":2,\"admin\":3}. RBAC permissions are checked first; this is an additional institution ceiling.", "is_secret": False},

    # --- Email ---
    {"key": "mail_enabled", "value": "false", "category": "email",
     "description": "Send account and test email through the configured SMTP relay", "is_secret": False},
    {"key": "mail_host", "value": "", "category": "email",
     "description": "SMTP server hostname, for example smtp.example.com", "is_secret": False},
    {"key": "mail_port", "value": "587", "category": "email",
     "description": "SMTP port: 587 for STARTTLS, 465 for SSL/TLS, or 25 for plain SMTP", "is_secret": False},
    {"key": "mail_security", "value": "starttls", "category": "email",
     "description": "SMTP transport security: starttls, ssl, or none", "is_secret": False},
    {"key": "mail_username", "value": "", "category": "email",
     "description": "SMTP username. Leave empty when the relay does not require authentication.", "is_secret": False},
    {"key": "mail_password", "value": "", "category": "email",
     "description": "SMTP password. The admin API returns it masked.", "is_secret": True},
    {"key": "mail_from_email", "value": "", "category": "email",
     "description": "From address for platform email, for example no-reply@example.com", "is_secret": False},
    {"key": "mail_from_name", "value": "SWOCTS Cyber Range", "category": "email",
     "description": "Display name for the From address", "is_secret": False},
    {"key": "mail_public_url", "value": "", "category": "email",
     "description": "Public URL used in email links, for example https://range.example.com. Empty falls back to the certificate URL or request host.", "is_secret": False},
    {"key": "mail_timeout_seconds", "value": "15", "category": "email",
     "description": "SMTP connection timeout in seconds", "is_secret": False},

    # --- Notification preferences ---
    {"key": "notify_registration_received", "value": "true", "category": "notifications",
     "description": "Email a new learner when registration is received and the account is waiting for approval."},
    {"key": "notify_registration_approved", "value": "true", "category": "notifications",
     "description": "Email a new learner when registration is auto-approved and the account is immediately active."},
    {"key": "notify_account_approved", "value": "true", "category": "notifications",
     "description": "Email a learner when an administrator approves a pending account."},
    {"key": "notify_account_rejected", "value": "true", "category": "notifications",
     "description": "Email a learner when an administrator rejects a pending account. The message never includes an internal reason."},
    {"key": "notify_username_reminder", "value": "true", "category": "notifications",
     "description": "Send the self-service username reminder email. Security and service messages may still be sent when other preferences are off."},

    # --- Email templates ---
    {"key": "mail_template_registration_received_subject",
     "value": "Your {platform_name} registration was received", "category": "email-templates",
     "description": "Subject for the pending-registration email. Blank uses the built-in default. Placeholders: {platform_name}, {display_name}, {username}, {email}, {login_url}, {support_email}."},
    {"key": "mail_template_registration_received_body",
     "value": "Hi {display_name},\n\nYour {platform_name} account has been created.\n\nUsername: {username}\n\nAn administrator must approve your account before you can sign in.\n\nIf you did not create this account, contact {support_email}.\n\nPowered by OpenCyberRange.",
     "category": "email-templates",
     "description": "Body for the pending-registration email. Blank uses the built-in default."},
    {"key": "mail_template_registration_approved_subject",
     "value": "Your {platform_name} account is ready", "category": "email-templates",
     "description": "Subject for an auto-approved registration email. Blank uses the built-in default."},
    {"key": "mail_template_registration_approved_body",
     "value": "Hi {display_name},\n\nYour {platform_name} account is ready.\n\nUsername: {username}\n\nSign in at {login_url}.\n\nIf you did not create this account, contact {support_email}.\n\nPowered by OpenCyberRange.",
     "category": "email-templates",
     "description": "Body for an auto-approved registration email. Blank uses the built-in default."},
    {"key": "mail_template_account_approved_subject",
     "value": "Your {platform_name} account has been approved", "category": "email-templates",
     "description": "Subject for the administrator-approval email. Blank uses the built-in default."},
    {"key": "mail_template_account_approved_body",
     "value": "Hi {display_name},\n\nAn administrator has approved your {platform_name} account.\n\nUsername: {username}\n\nYou can sign in at {login_url}.\n\nPowered by OpenCyberRange.",
     "category": "email-templates",
     "description": "Body for the administrator-approval email. Blank uses the built-in default."},
    {"key": "mail_template_account_rejected_subject",
     "value": "Your {platform_name} account request", "category": "email-templates",
     "description": "Subject for the rejection email. Blank uses the built-in default."},
    {"key": "mail_template_account_rejected_body",
     "value": "Hi {display_name},\n\nYour {platform_name} account request was not approved.\n\nIf you believe this is a mistake, contact {support_email}.\n\nPowered by OpenCyberRange.",
     "category": "email-templates",
     "description": "Body for the rejection email. Do not include internal review details. Blank uses the built-in default."},
    {"key": "mail_template_username_reminder_subject",
     "value": "Your {platform_name} username", "category": "email-templates",
     "description": "Subject for the username reminder email. Blank uses the built-in default."},
    {"key": "mail_template_username_reminder_body",
     "value": "You asked us to remind you of the username for the {platform_name} account registered to this email address.\n\n{usernames}\n\nSign in at {login_url}.\n\nFor your security, this message does not include your password. If you did not ask for this reminder, you can ignore it.\n\nPowered by OpenCyberRange.",
     "category": "email-templates",
     "description": "Body for the username reminder email. Placeholder {usernames} is the formatted list. Blank uses the built-in default."},

    # --- Security ---
    {"key": "jwt_expiration_hours", "value": "24", "category": "security",
     "description": "JWT token lifetime in hours"},
    {"key": "max_failed_attempts", "value": "5", "category": "security",
     "description": "Failed login attempts before account lockout"},
    {"key": "lockout_duration_minutes", "value": "30", "category": "security",
     "description": "Account lockout duration in minutes"},
    {"key": "require_approval", "value": "true", "category": "security",
     "description": "Require admin approval for new user registrations"},
    {"key": "sso_enabled", "value": "true", "category": "security",
     "description": "Allow users to sign in through the configured LDAP, OIDC, and SAML providers. When off, the institution sign-in panel is hidden and all SSO endpoints reject new logins. Local password login, including the break-glass administrator, remains available."},
    {"key": "enable_api_docs", "value": "false", "category": "security",
     "description": "Enable Swagger UI (/docs) and ReDoc (/redoc) on the backend API"},
    {"key": "privacy_default_on", "value": "true", "category": "security",
     "description": "Start administrators with privacy mode on when they have no saved preference. Privacy mode masks usernames, emails, display names, and student IDs in admin views."},
    {"key": "analytics_min_cohort_size", "value": "5", "category": "security",
     "description": "Minimum learner cohort for course, exercise, and report analytics. Smaller groups are suppressed to reduce re-identification risk. Set to 0 to disable suppression in a trusted test environment."},
    {"key": "max_privileged_accounts", "value": "1", "category": "security",
     "description": "Maximum instructor and administrator accounts on this install. Set to 0 for unlimited, or raise it to add more instructors and admins. The edition default is 1."},
    {"key": "password_breach_check_enabled", "value": "false", "category": "security",
     "description": "Check new passwords against the Have I Been Pwned Pwned Passwords range API. Only the first five characters of a SHA-1 hash leave the server; the full password is never sent. The check fails open if the API is unreachable, so offline installs continue to work."},
    {"key": "security_event_store_enabled", "value": "true", "category": "security",
     "description": "Write security, audit, and privacy events to the append-only security event store. PostgreSQL row-level security removes UPDATE and DELETE capability.", "is_secret": False},
    {"key": "security_event_http_logging", "value": "true", "category": "security",
     "description": "Capture sensitive HTTP requests that do not have a richer explicit event. Disable only for a high-volume deployment with an external audit pipeline.", "is_secret": False},
    {"key": "security_event_retention_days", "value": "365", "category": "security",
     "description": "Recommended retention for security events. The application role cannot delete events; retention is applied by an operator with an elevated maintenance role under the institution's retention schedule.", "is_secret": False},
    {"key": "deployment_mode", "value": "development", "category": "security",
     "description": "Deployment phase. Development is for sample data and review. Production is a one-way cutover: it requires a ticket, the current password, explicit data-loss and one-way acknowledgements, clears sample/test accounts, and cannot be reversed from the application. Only the cutover workflow can change this value.", "is_secret": False},
    {"key": "data_collection_mode", "value": "sample", "category": "security",
     "description": "Data collection state. Sample data is not production evidence. The production cutover sets this to production and only real learner evidence is collected afterwards. Only the cutover workflow can change this value.", "is_secret": False},
    {"key": "settings_change_ticket_mode", "value": "optional", "category": "security",
     "description": "Ticket requirement for settings changes: off, optional, or required. Production defaults to required after cutover. A required ticket must be listed with the change set and reason; every apply, revert, and cutover is recorded in the security event store and audit log.", "is_secret": False},
    {"key": "tenant_isolation_enabled", "value": "true", "category": "security",
     "description": "Enforce the tenant boundary in the Authorization Service. Non-system roles may only access records whose owner has the same institution_id. Disable only for a single-institution test deployment.", "is_secret": False},
    {"key": "authorization_strict_startup", "value": "false", "category": "security",
     "description": "Refuse to start when a protected API route has no authentication/authorization dependency. Enterprise deployments should enable this after reviewing the startup audit.", "is_secret": False},
    {"key": "break_glass_enabled", "value": "false", "category": "security",
     "description": "Allow time-bound, reasoned emergency access to private data or restricted exports. Every use is a critical security event. Leave off unless the institution has an approved break-glass procedure.", "is_secret": False},
    {"key": "break_glass_require_mfa", "value": "true", "category": "security",
     "description": "Require MFA on the requesting and target accounts before a break-glass grant can be created or used.", "is_secret": False},
    {"key": "break_glass_require_approval", "value": "false", "category": "security",
     "description": "Require a second operator to approve a break-glass request. Enable this for enterprise deployments.", "is_secret": False},
    {"key": "break_glass_max_minutes", "value": "60", "category": "security",
     "description": "Maximum lifetime of a break-glass grant in minutes. Grants cannot be extended; create a new reviewed grant instead.", "is_secret": False},
    {"key": "security_alert_enabled", "value": "true", "category": "security",
     "description": "Run the threshold alert scan over security events. Alerts are written back as security.alert events and shown in the Security console.", "is_secret": False},
    {"key": "security_alert_window_minutes", "value": "15", "category": "security",
     "description": "Rolling window for repeated failed logins, denied requests, and export denials.", "is_secret": False},
    {"key": "security_alert_threshold", "value": "5", "category": "security",
     "description": "Number of matching events in the window before an alert is raised.", "is_secret": False},
    {"key": "refresh_token_days", "value": "30", "category": "security",
     "description": "Lifetime of a login session and its rotating refresh token. Access tokens remain short-lived and are renewed from the refresh token.", "is_secret": False},
    {"key": "reauth_window_minutes", "value": "15", "category": "security",
     "description": "How long a password + MFA reauthentication remains valid for privacy, role, MFA, and export operations. A fresh login starts the window.", "is_secret": False},
    {"key": "mfa_max_failed_attempts", "value": "5", "category": "security",
     "description": "Bad TOTP or recovery-code attempts before the MFA challenge is temporarily locked.", "is_secret": False},
    {"key": "mfa_lockout_minutes", "value": "15", "category": "security",
     "description": "How long the MFA challenge stays locked after too many bad codes.", "is_secret": False},
    {"key": "mfa_recovery_code_ttl_days", "value": "365", "category": "security",
     "description": "Lifetime of a generated MFA recovery-code set. Generating a new set invalidates the previous one.", "is_secret": False},
    {"key": "mfa_recovery_code_count", "value": "10", "category": "security",
     "description": "Number of single-use recovery codes generated at a time.", "is_secret": False},
    {"key": "password_rehash_days", "value": "365", "category": "security",
     "description": "Maximum age of a password hash before a successful login rehashes it with the current Argon2id parameters.", "is_secret": False},
    {"key": "portfolio_share_lifetime_days", "value": "30", "category": "security",
     "description": "Default lifetime for a portfolio share link. The raw token is shown once and only its SHA-256 hash is stored. Learners may revoke a link at any time.", "is_secret": False},

    # --- Wiki origin split ---
    {"key": "wiki_origin", "value": "", "category": "wiki",
     "description": "Optional separate origin for the workbook wiki, for example https://wiki.example.edu. It must point at this same deployment and have a valid TLS certificate. Empty keeps the wiki same-origin."},
    {"key": "wiki_cookie_domain", "value": "", "category": "wiki",
     "description": "Parent-domain scope for the HttpOnly wiki cookie, for example .example.edu. Set this when the wiki runs on a different hostname. Empty keeps the cookie host-only."},
    {"key": "wiki_frame_ancestor", "value": "", "category": "wiki",
     "description": "Optional space-separated list of origins allowed to frame the wiki, for example https://range.example.edu. Empty derives the app origin from FRONTEND_BASE_URL, PUBLIC_BASE_URL, or SERVER_PUBLIC_HOST."},

    # --- Labs ---
    {"key": "default_session_hours", "value": "2", "category": "labs",
     "description": "Default exercise session duration in hours"},
    {"key": "max_session_hours", "value": "8", "category": "labs",
     "description": "Maximum exercise session duration in hours"},
    {"key": "session_accommodation_percent", "value": "100", "category": "labs",
     "description": "Extra time for timed exercises as a percentage of the normal session length. 100 = no change, 150 = 50% extra time. Allowed 100-300."},
    {"key": "container_cpu_limit", "value": "0.5", "category": "labs",
     "description": "Default CPU limit per container (Docker CPUs)"},
    {"key": "container_memory_limit", "value": "512M", "category": "labs",
     "description": "Default memory limit per container"},
    {"key": "rangebox_capacity_percent", "value": "75", "category": "labs",
     "description": "Percentage of the host's computed RangeBox maximum used as the live concurrency cap. The remaining headroom protects the backend, database, SIEM, and interactive VNC. Default 75; allowed range 10-100. An explicit MAX_CONCURRENT_RANGEBOXES environment variable overrides this setting."},
    {"key": "rangebox_stress_max", "value": "0", "category": "labs",
     "description": "Measured Level 4 RangeBox ceiling from the last capacity test. Zero means no measured ceiling has been recorded, so the computed maximum is used."},
    {"key": "rangebox_stress_tested_at", "value": "", "category": "labs",
     "description": "UTC timestamp of the last recorded Level 4 RangeBox ceiling."},
    # --- VPN ---
    {"key": "vpn_enabled", "value": "true", "category": "vpn",
     "description": "Enable WireGuard VPN features"},
    {"key": "vpn_endpoint", "value": "", "category": "vpn",
     "description": "WireGuard server endpoint (host:port)"},
    {"key": "vpn_public_key", "value": "", "category": "vpn",
     "description": "WireGuard server public key"},
    {"key": "vpn_wstunnel_enabled", "value": "false", "category": "vpn",
     "description": "Wrap WireGuard in WebSocket tunnel (for Cloudflare Tunnel deployments)"},
    {"key": "vpn_wstunnel_url", "value": "", "category": "vpn",
     "description": "WebSocket tunnel URL (e.g. wss://vpn.yourdomain.com)"},

    # --- Open Badges ---
    {"key": "open_badge_issuer_name", "value": "SWOCTS Cyber Range", "category": "badges",
     "description": "Issuer name shown in Open Badges 3.0 credentials."},
    {"key": "open_badge_issuer_url", "value": "", "category": "badges",
     "description": "Public issuer URL for Open Badges credentials. Empty uses the platform public URL."},
    {"key": "open_badge_signing_key", "value": "", "category": "badges", "is_secret": True,
     "description": "Ed25519 private key used to sign Open Badges credentials. Generated on first use."},
    {"key": "open_badge_retired_keys", "value": "[]", "category": "badges",
     "description": "Public JWKs retired by key rotation, kept so older credentials still verify."},

    # --- Features ---
    {"key": "advanced_dna_insights_enabled", "value": "false", "category": "features",
     "description": "Show the development-only Momentum and Career Atlas surfaces on learner profiles and career dossiers. Keep this off in production until the review in docs/CAREER-ATLAS-AND-MOMENTUM.md is signed off.", "is_secret": False},
    {"key": "cyber_dna_v3_enabled", "value": "false", "category": "features",
     "description": "Expose the Cyber DNA v3 evidence, behavior, interest, and career-affinity APIs. Evidence is recorded regardless of this gate; the gate controls the learner-facing read surfaces. See docs/CYBER-DNA-V3.md.", "is_secret": False},





]

def _secret_keys() -> set[str]:
    return {
        item["key"] for item in DEFAULT_SETTINGS if item.get("is_secret")
    }


_SECRET_KEYS = _secret_keys()


def _is_secret(key: str, row: PlatformSetting | None = None) -> bool:
    if row is not None:
        return bool(row.is_secret)
    return key in _SECRET_KEYS


def _protect(key: str, value: str, row: PlatformSetting | None = None) -> str:
    """Encrypt a secret setting on write; leave plaintext and masks alone."""
    if not value or not _is_secret(key, row) or is_encrypted(value):
        return value
    return encrypt_secret(value)


def _reveal(key: str, value: str | None, row: PlatformSetting | None = None) -> str | None:
    """Decrypt a stored secret for the service that needs the real value."""
    if not value or not _is_secret(key, row) or not is_encrypted(value):
        return value
    try:
        return decrypt_secret(value)
    except ValueError:
        logger.warning("Could not decrypt secret setting %s", key)
        return value


def _load_cache(db: Session) -> None:
    """Load all settings into memory cache."""
    global _cache, _cache_loaded, _cache_loaded_at
    rows = db.query(PlatformSetting).all()
    _cache = {row.key: row.value for row in rows}
    _cache_loaded = True
    _cache_loaded_at = _time.monotonic()


def _invalidate_cache() -> None:
    global _cache, _cache_loaded, _cache_loaded_at
    _cache = {}
    _cache_loaded = False
    _cache_loaded_at = 0.0


def invalidate_cache() -> None:
    """Public invalidation hook for change-control writes."""
    _invalidate_cache()


def _is_cache_stale() -> bool:
    """Return True if cache needs refreshing (expired TTL or never loaded)."""
    if not _cache_loaded:
        return True
    return (_time.monotonic() - _cache_loaded_at) > _CACHE_TTL_SECONDS


def get_setting(db: Session, key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a single setting value (cached with TTL)."""
    if _is_cache_stale():
        _load_cache(db)
    return _reveal(key, _cache.get(key, default))


def get_setting_fresh(db: Session, key: str, default: Optional[str] = None) -> Optional[str]:
    """Read a setting straight from the database, skipping the cache.

    The cache is per worker and only the worker that handled a write clears it,
    so every other worker can serve a stale value until the TTL expires. That is
    fine for a value that merely tunes behaviour, and wrong for one that gates
    access: an admin who switches something off would keep granting it for up to
    the TTL on most workers. Use this for those checks. The cost is one indexed
    single-row lookup.
    """
    row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if row is None:
        return default
    return _reveal(key, row.value, row)


def get_settings_by_category(db: Session, category: str) -> List[dict]:
    """Return all settings in a category as list of dicts."""
    rows = db.query(PlatformSetting).filter(
        PlatformSetting.category == category
    ).order_by(PlatformSetting.key).all()
    return [
        {
            "key": r.key,
            "value": r.value if not r.is_secret else "••••••••",
            "category": r.category,
            "description": r.description,
            "is_secret": r.is_secret,
        }
        for r in rows
    ]


def get_all_settings(db: Session) -> List[dict]:
    """Return all settings grouped by category."""
    rows = db.query(PlatformSetting).order_by(
        PlatformSetting.category, PlatformSetting.key
    ).all()
    return [
        {
            "key": r.key,
            "value": r.value if not r.is_secret else "••••••••",
            "category": r.category,
            "description": r.description,
            "is_secret": r.is_secret,
        }
        for r in rows
    ]


def set_setting(db: Session, key: str, value: str) -> PlatformSetting:
    """Create or update a setting."""
    row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if row:
        row.value = _protect(key, value, row)
    else:
        row = PlatformSetting(key=key, value=_protect(key, value))
        db.add(row)
    db.commit()
    db.refresh(row)
    _invalidate_cache()
    return row


def bulk_update_settings(db: Session, updates: Dict[str, str]) -> int:
    """Update multiple settings at once. Returns count of updated rows."""
    count = 0
    for key, value in updates.items():
        row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
        if row:
            row.value = _protect(key, value, row)
            count += 1
        else:
            db.add(PlatformSetting(key=key, value=_protect(key, value)))
            count += 1
    db.commit()
    _invalidate_cache()
    return count


def _default_certificate_verify_url() -> str:
    """Derive the certificate verify base URL for a first-run install.

    The admin can override it in Settings; seeding a sensible value removes
    the trap where an empty setting made QR codes point at the API origin.
    """
    from app.config import settings

    host = (getattr(settings, "SERVER_PUBLIC_HOST", "") or "").strip().rstrip("/")
    if not host:
        return ""
    # The config default is "localhost"; a bare localhost is not a public
    # origin, so leave the setting empty and let the request host decide.
    if host in ("localhost", "127.0.0.1", "[::1]"):
        return ""
    if host.startswith(("http://", "https://")):
        return host
    scheme = "http" if host.startswith(("localhost", "127.0.0.1", "[::1]")) else "https"
    return f"{scheme}://{host}"


def seed_defaults(db: Session) -> int:
    """Insert default settings that don't already exist. Returns count of new rows."""
    created = 0
    resynced = 0
    for defn in DEFAULT_SETTINGS:
        existing = db.query(PlatformSetting).filter(
            PlatformSetting.key == defn["key"]
        ).first()
        if not existing:
            value = defn["value"]
            if defn["key"] == "certificate_verify_url" and not value:
                value = _default_certificate_verify_url()
            db.add(PlatformSetting(
                key=defn["key"],
                value=value,
                category=defn.get("category", "general"),
                description=defn.get("description"),
                is_secret=defn.get("is_secret", False),
            ))
            created += 1
        else:
            # A setting's description and category are documentation owned by
            # the code, not admin data, so keep them in step with DEFAULT_SETTINGS
            # on every start. Without this an existing row keeps whatever text it
            # was first seeded with and the help an admin reads drifts from what
            # the setting actually does. The value is never touched: that is the
            # admin's.
            desc = defn.get("description")
            cat = defn.get("category", "general")
            if existing.description != desc or existing.category != cat:
                existing.description = desc
                existing.category = cat
                resynced += 1

    # Branding migration: replace only the old seeded default, never a name an
    # administrator has customised.
    old_from_name = db.query(PlatformSetting).filter(
        PlatformSetting.key == "mail_from_name",
        PlatformSetting.value == "OpenCyberRange",
    ).first()
    if old_from_name is not None:
        old_from_name.value = "SWOCTS Cyber Range"
        resynced += 1

    if created or resynced:
        db.commit()
        _invalidate_cache()
        if created:
            logger.info(f"Seeded {created} default platform settings")
        if resynced:
            logger.info(f"Resynced descriptions for {resynced} platform settings")

    # Populate empty VPN settings from environment variables so the
    # admin UI shows the values that were auto-detected during install.
    _ENV_TO_SETTING = {
        "vpn_endpoint": "WG_SERVER_ENDPOINT",
        "vpn_public_key": "WG_SERVER_PUBLIC_KEY",
    }
    updated = 0
    for setting_key, env_var in _ENV_TO_SETTING.items():
        env_val = os.environ.get(env_var, "")
        if not env_val:
            continue
        row = db.query(PlatformSetting).filter(
            PlatformSetting.key == setting_key
        ).first()
        if row and not row.value:
            row.value = env_val
            updated += 1
    if updated:
        db.commit()
        _invalidate_cache()
        logger.info(f"Populated {updated} VPN settings from environment")

    return created
