"""SMTP mail delivery for platform notifications.

Settings live in ``platform_settings`` so an administrator can configure the
relay from the admin interface. Delivery is best effort: a registration must
never fail because the SMTP relay is down or unconfigured.
"""
from __future__ import annotations

import html
import logging
import re
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, parseaddr
from typing import Optional
from urllib.parse import quote

from sqlalchemy.orm import Session

from app.services import settings_service

logger = logging.getLogger(__name__)

# Built-in defaults for account emails. Administrators can override the subject
# and body in Settings -> Email templates. Blank settings fall back here.
TEMPLATE_DEFAULTS = {
    "registration_received": {
        "subject": "Your {platform_name} registration was received",
        "body": (
            "Hi {display_name},\n\n"
            "Your {platform_name} account has been created.\n\n"
            "Username: {username}\n\n"
            "An administrator must approve your account before you can sign in.\n\n"
            "If you did not create this account, contact {support_email}.\n\n"
            "Powered by OpenCyberRange."
        ),
    },
    "registration_approved": {
        "subject": "Your {platform_name} account is ready",
        "body": (
            "Hi {display_name},\n\n"
            "Your {platform_name} account is ready.\n\n"
            "Username: {username}\n\n"
            "Sign in at {login_url}.\n\n"
            "If you did not create this account, contact {support_email}.\n\n"
            "Powered by OpenCyberRange."
        ),
    },
    "account_approved": {
        "subject": "Your {platform_name} account has been approved",
        "body": (
            "Hi {display_name},\n\n"
            "An administrator has approved your {platform_name} account.\n\n"
            "Username: {username}\n\n"
            "You can sign in at {login_url}.\n\n"
            "Powered by OpenCyberRange."
        ),
    },
    "account_rejected": {
        "subject": "Your {platform_name} account request",
        "body": (
            "Hi {display_name},\n\n"
            "Your {platform_name} account request was not approved.\n\n"
            "If you believe this is a mistake, contact {support_email}.\n\n"
            "Powered by OpenCyberRange."
        ),
    },
    "username_reminder": {
        "subject": "Your {platform_name} username",
        "body": (
            "You asked us to remind you of the username for the {platform_name} "
            "account registered to this email address.\n\n"
            "{usernames}\n\n"
            "Sign in at {login_url}.\n\n"
            "For your security, this message does not include your password. If you "
            "did not ask for this reminder, you can ignore it.\n\n"
            "Powered by OpenCyberRange."
        ),
    },
    "password_reset": {
        "subject": "Reset your {platform_name} password",
        "body": (
            "Hi {display_name},\n\n"
            "We received a request to reset the password for the {platform_name} "
            "account registered to this email address.\n\n"
            "Choose a new password here (valid for {expires_minutes} minutes):\n"
            "{reset_url}\n\n"
            "If you did not ask for this, you can ignore this message. Your password "
            "will not change.\n\n"
            "Powered by OpenCyberRange."
        ),
    },
}

TEMPLATE_SETTING_PREFIX = "mail_template_"
NOTIFICATION_SETTINGS = {
    "registration_received": "notify_registration_received",
    "registration_approved": "notify_registration_approved",
    "account_approved": "notify_account_approved",
    "account_rejected": "notify_account_rejected",
    "username_reminder": "notify_username_reminder",
    "password_reset": "notify_password_reset",
}


def _clean(value) -> str:
    """Strip CR/LF so settings cannot inject extra mail headers."""
    return str(value or "").replace("\r", " ").replace("\n", " ").strip()


def _as_int(value, default: int, minimum: int, maximum: int) -> int:
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def mail_config(db: Session, *, fresh: bool = False) -> dict:
    """Return the effective SMTP configuration from platform settings."""
    get = settings_service.get_setting_fresh if fresh else settings_service.get_setting

    security = (_clean(get(db, "mail_security", "starttls")) or "starttls").lower()
    if security not in {"starttls", "ssl", "none"}:
        security = "starttls"

    default_port = 465 if security == "ssl" else 25 if security == "none" else 587
    from_email = _clean(get(db, "mail_from_email", ""))
    username = _clean(get(db, "mail_username", ""))
    password = str(get(db, "mail_password", "") or "")

    return {
        "enabled": (_clean(get(db, "mail_enabled", "false")) or "false").lower() == "true",
        "host": _clean(get(db, "mail_host", "")),
        "port": _as_int(get(db, "mail_port", default_port), default_port, 1, 65535),
        "security": security,
        "username": username,
        "password": password,
        "from_email": from_email,
        "from_name": _clean(get(db, "mail_from_name", "SWOCTS Cyber Range")) or "SWOCTS Cyber Range",
        "public_url": _clean(get(db, "mail_public_url", "")),
        "timeout": _as_int(get(db, "mail_timeout_seconds", 15), 15, 1, 120),
    }


def is_configured(config: dict) -> bool:
    """True when the relay has enough information to attempt delivery."""
    if not config.get("enabled"):
        return False
    if not config.get("host"):
        return False
    _, address = parseaddr(config.get("from_email", ""))
    return "@" in address


def public_base_url(db: Session, request_base: str = "") -> str:
    """Choose the public origin used in email links."""
    for key in ("mail_public_url", "certificate_verify_url"):
        value = _clean(settings_service.get_setting(db, key, ""))
        if value:
            return value.rstrip("/")

    from app.config import settings

    host = (getattr(settings, "SERVER_PUBLIC_HOST", "") or "").strip().rstrip("/")
    if host and host not in ("localhost", "127.0.0.1", "[::1]"):
        if not host.startswith(("http://", "https://")):
            host = f"https://{host}"
        return host.rstrip("/")

    return (request_base or "").rstrip("/")


def _setting(db: Session | None, key: str, default: str = "") -> str:
    if db is None:
        return default
    try:
        value = settings_service.get_setting(db, key, default)
    except Exception:
        logger.warning("Could not read setting %s; using default", key)
        return default
    return default if value is None or str(value).strip() == "" else str(value)


def _format_placeholders(value: str, context: dict) -> str:
    """Replace {name} placeholders and leave unknown ones visible."""
    def replace(match):
        name = match.group(1)
        return str(context.get(name, match.group(0)))

    return re.sub(r"\{([a-zA-Z0-9_]+)\}", replace, value or "")


def _html_from_text(value: str) -> str:
    escaped = html.escape(value or "")
    escaped = re.sub(
        r"(https?://[^\s<]+)",
        lambda match: f'<a href="{match.group(1)}">{match.group(1)}</a>',
        escaped,
    )
    paragraphs = [
        paragraph.replace("\n", "<br>")
        for paragraph in escaped.split("\n\n")
        if paragraph.strip()
    ]
    body = "".join(f"<p>{paragraph}</p>" for paragraph in paragraphs)
    return (
        "<!doctype html><html><body>"
        f"{body}"
        "<p style=\"margin-top:1.5em;font-size:12px;color:#64748b;\">"
        "Powered by OpenCyberRange.</p>"
        "</body></html>"
    )


def render_template(
    db: Session | None,
    template_key: str,
    **context,
) -> tuple[str, str, str]:
    """Render an account email from settings, falling back to the default.

    The caller passes the display values; unknown placeholders are left visible
    so an administrator can spot a typo in a custom template.
    """
    defaults = TEMPLATE_DEFAULTS.get(template_key)
    if defaults is None:
        raise ValueError(f"unknown mail template: {template_key}")

    platform_name = _setting(db, "mail_from_name", "SWOCTS Cyber Range")
    values = {
        "platform_name": platform_name,
        "display_name": context.get("display_name") or context.get("username") or "there",
        "username": context.get("username", ""),
        "email": context.get("email", ""),
        "login_url": context.get("login_url", ""),
        "support_email": context.get("support_email", ""),
        "usernames": context.get("usernames", ""),
        "reset_url": context.get("reset_url", ""),
        "expires_minutes": str(context.get("expires_minutes", "30")),
    }
    subject_value = _setting(
        db,
        f"{TEMPLATE_SETTING_PREFIX}{template_key}_subject",
        defaults["subject"],
    )
    body_value = _setting(
        db,
        f"{TEMPLATE_SETTING_PREFIX}{template_key}_body",
        defaults["body"],
    )
    subject = _format_placeholders(subject_value, values).strip()
    text_body = _format_placeholders(body_value, values).strip()
    if not subject:
        subject = _format_placeholders(defaults["subject"], values).strip()
    if not text_body:
        text_body = _format_placeholders(defaults["body"], values).strip()
    return subject, text_body, _html_from_text(text_body)


def notification_enabled(db: Session, template_key: str) -> bool:
    key = NOTIFICATION_SETTINGS.get(template_key)
    if not key:
        return False
    return _setting(db, key, "true").strip().lower() == "true"


def render_registration_email(
    *,
    username: str,
    display_name: str = "",
    approved: bool,
    login_url: str = "",
    support_email: str = "",
) -> tuple[str, str, str]:
    """Build the subject, plain text, and HTML for a registration email."""
    name = _clean(display_name) or username
    safe_name = html.escape(name)
    safe_username = html.escape(username)
    safe_login = html.escape(login_url, quote=True)
    safe_support = html.escape(support_email)

    if approved:
        subject = "Your SWOCTS Cyber Range account is ready"
        action_text = (
            f"You can sign in at {login_url}" if login_url else "You can now sign in."
        )
    else:
        subject = "Your SWOCTS Cyber Range registration was received"
        action_text = (
            "An administrator must approve your account before you can sign in."
        )

    text_body = "\n".join(
        [
            f"Hi {name},",
            "",
            "Your SWOCTS Cyber Range account has been created.",
            "",
            f"Username: {username}",
            "",
            action_text,
            "",
            (
                f"If you did not create this account, contact {support_email}."
                if support_email
                else "If you did not create this account, contact your administrator."
            ),
            "",
            "Powered by OpenCyberRange.",
        ]
    )

    action_html = (
        f'<p><a href="{safe_login}">Sign in to SWOCTS Cyber Range</a></p>'
        if approved and safe_login
        else f"<p>{html.escape(action_text)}</p>"
    )
    support_html = (
        f"<p>If you did not create this account, contact "
        f"<a href=\"mailto:{safe_support}\">{safe_support}</a>.</p>"
        if safe_support
        else "<p>If you did not create this account, contact your administrator.</p>"
    )
    html_body = (
        "<!doctype html><html><body>"
        f"<p>Hi {safe_name},</p>"
        "<p>Your SWOCTS Cyber Range account has been created.</p>"
        f"<p><strong>Username:</strong> {safe_username}</p>"
        f"{action_html}"
        f"{support_html}"
        "<p style=\"margin-top:1.5em;font-size:12px;color:#64748b;\">"
        "Powered by OpenCyberRange.</p>"
        "</body></html>"
    )
    return subject, text_body, html_body


def render_username_reminder_email(
    *,
    usernames: list[str],
    login_url: str = "",
    support_email: str = "",
) -> tuple[str, str, str]:
    """Build a username reminder that never contains a password.

    The recipient is already the address on file, so this is a service
    message rather than a marketing email. If several accounts share the
    address (legacy data), list each username once.
    """
    clean_usernames = sorted({_clean(value) for value in usernames if _clean(value)})
    subject = "Your SWOCTS Cyber Range username"
    safe_login = html.escape(login_url, quote=True)
    safe_support = html.escape(support_email)

    username_lines = "\n".join(f"- {name}" for name in clean_usernames)
    if len(clean_usernames) == 1:
        username_lines = f"Username: {clean_usernames[0]}"

    text_body = "\n".join([
        "You asked us to remind you of the username for the SWOCTS Cyber Range",
        "account registered to this email address.",
        "",
        username_lines,
        "",
        (
            f"Sign in at {login_url}"
            if login_url
            else "Open the platform and sign in with this username."
        ),
        "",
        "For your security, this message does not include your password. If you",
        "did not ask for this reminder, you can ignore it.",
        (
            f"Questions? Contact {support_email}."
            if support_email
            else "Questions? Contact your instructor or administrator."
        ),
        "",
        "Powered by OpenCyberRange.",
    ])

    username_html = "".join(
        f"<li><strong>{html.escape(name)}</strong></li>" for name in clean_usernames
    )
    html_body = (
        "<!doctype html><html><body>"
        "<p>You asked us to remind you of the username for the SWOCTS Cyber Range "
        "account registered to this email address.</p>"
        f"<ul>{username_html}</ul>"
        + (
            f'<p><a href="{safe_login}">Sign in to SWOCTS Cyber Range</a></p>'
            if safe_login
            else "<p>Open the platform and sign in with this username.</p>"
        )
        + "<p>For your security, this message does not include your password. "
        "If you did not ask for this reminder, you can ignore it.</p>"
        + (
            f'<p>Questions? Contact <a href="mailto:{safe_support}">{safe_support}</a>.</p>'
            if safe_support
            else "<p>Questions? Contact your instructor or administrator.</p>"
        )
        + "<p style=\"margin-top:1.5em;font-size:12px;color:#64748b;\">"
        "Powered by OpenCyberRange.</p>"
        + "</body></html>"
    )
    return subject, text_body, html_body


def send_email(
    db: Session,
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: Optional[str] = None,
    raise_on_error: bool = False,
    fresh_settings: bool = False,
) -> bool:
    """Send one message. Returns False when mail is disabled or delivery fails."""
    config = mail_config(db, fresh=fresh_settings)
    if not is_configured(config):
        logger.debug("Mail delivery skipped: SMTP is disabled or not configured")
        return False

    to_address = _clean(to_email)
    if "@" not in parseaddr(to_address)[1]:
        logger.warning("Mail delivery skipped: invalid recipient address")
        return False

    message = EmailMessage()
    message["Subject"] = _clean(subject)
    message["From"] = formataddr((config["from_name"], config["from_email"]))
    message["To"] = to_address
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")

    try:
        if config["security"] == "ssl":
            server = smtplib.SMTP_SSL(
                config["host"],
                config["port"],
                timeout=config["timeout"],
                context=ssl.create_default_context(),
            )
        else:
            server = smtplib.SMTP(
                config["host"],
                config["port"],
                timeout=config["timeout"],
            )

        with server:
            server.ehlo()
            if config["security"] == "starttls":
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
            if config["username"]:
                server.login(config["username"], config["password"])
            server.send_message(message)

        logger.info("Sent email to %s", to_address)
        return True
    except Exception as exc:
        logger.warning("Email delivery to %s failed: %s", to_address, exc)
        if raise_on_error:
            raise
        return False


def send_registration_email(
    *,
    user_id: int,
    email: str,
    username: str,
    display_name: str = "",
    approved: bool = False,
    request_base: str = "",
) -> bool:
    """Background-task entry point for a new registration.

    Opens its own database session because the request session is closed once
    the response has been sent.
    """
    from app.database import SessionLocal
    from app.config import settings

    db = None
    try:
        db = SessionLocal()
        template_key = "registration_approved" if approved else "registration_received"
        if not notification_enabled(db, template_key):
            logger.debug("Registration email skipped by notification preference")
            return False
        support_email = getattr(settings, "PRIVACY_CONTACT_EMAIL", "") or ""
        login_url = public_base_url(db, request_base)
        login_url = f"{login_url}/login" if login_url else ""
        subject, text_body, html_body = render_template(
            db,
            template_key,
            email=email,
            username=username,
            display_name=display_name,
            login_url=login_url,
            support_email=support_email,
        )
        return send_email(
            db,
            to_email=email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            fresh_settings=True,
        )
    except Exception as exc:
        logger.warning("Registration email for %s failed: %s", username, exc)
        return False
    finally:
        if db is not None:
            db.close()


def send_account_status_email(
    *,
    user_id: int,
    email: str,
    username: str,
    display_name: str = "",
    approved: bool = True,
    request_base: str = "",
) -> bool:
    """Send the administrator approval or rejection notice.

    Opens its own database session because the request session is closed once
    the response has been sent.
    """
    from app.database import SessionLocal
    from app.config import settings

    db = None
    try:
        db = SessionLocal()
        template_key = "account_approved" if approved else "account_rejected"
        if not notification_enabled(db, template_key):
            logger.debug("Account status email skipped by notification preference")
            return False
        support_email = getattr(settings, "PRIVACY_CONTACT_EMAIL", "") or ""
        login_url = public_base_url(db, request_base)
        login_url = f"{login_url}/login" if login_url else ""
        subject, text_body, html_body = render_template(
            db,
            template_key,
            email=email,
            username=username,
            display_name=display_name,
            login_url=login_url,
            support_email=support_email,
        )
        return send_email(
            db,
            to_email=email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            fresh_settings=True,
        )
    except Exception as exc:
        logger.warning("Account status email for %s failed: %s", username, exc)
        return False
    finally:
        if db is not None:
            db.close()


def send_username_reminder_email(
    *,
    to_email: str,
    usernames: list[str],
    request_base: str = "",
) -> bool:
    """Background-task entry point for a username reminder.

    The caller has already matched the address to an account. Delivery stays
    best effort so an unavailable relay never changes the generic response.
    """
    from app.database import SessionLocal
    from app.config import settings

    db = None
    try:
        db = SessionLocal()
        if not notification_enabled(db, "username_reminder"):
            logger.debug("Username reminder skipped by notification preference")
            return False
        support_email = getattr(settings, "PRIVACY_CONTACT_EMAIL", "") or ""
        login_url = public_base_url(db, request_base)
        login_url = f"{login_url}/login" if login_url else ""
        clean_usernames = sorted({_clean(value) for value in usernames if _clean(value)})
        if len(clean_usernames) == 1:
            usernames_value = f"Username: {clean_usernames[0]}"
        else:
            usernames_value = "\n".join(f"- {name}" for name in clean_usernames)
        subject, text_body, html_body = render_template(
            db,
            "username_reminder",
            to_email=to_email,
            usernames=usernames_value,
            login_url=login_url,
            support_email=support_email,
        )
        return send_email(
            db,
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            fresh_settings=True,
        )
    except Exception as exc:
        logger.warning("Username reminder for %s failed: %s", to_email, exc)
        return False
    finally:
        if db is not None:
            db.close()


def send_password_reset_email(
    *,
    to_email: str,
    token: str,
    username: str = "",
    display_name: str = "",
    request_base: str = "",
    expires_minutes: int = 30,
) -> bool:
    """Background-task entry point for a self-service password reset link.

    The caller has already matched the address to an eligible local account.
    Delivery stays best effort so an unavailable relay never changes the
    generic response, and the token is never logged.
    """
    from app.database import SessionLocal
    from app.config import settings

    db = None
    try:
        db = SessionLocal()
        if not notification_enabled(db, "password_reset"):
            logger.debug("Password reset email skipped by notification preference")
            return False
        support_email = getattr(settings, "PRIVACY_CONTACT_EMAIL", "") or ""
        base = public_base_url(db, request_base)
        reset_url = (
            f"{base}/reset-password?token={quote(token, safe='')}" if base else ""
        )
        if not reset_url:
            logger.warning("Password reset email skipped: no public URL configured")
            return False
        subject, text_body, html_body = render_template(
            db,
            "password_reset",
            to_email=to_email,
            username=username,
            display_name=display_name,
            reset_url=reset_url,
            expires_minutes=expires_minutes,
            support_email=support_email,
        )
        return send_email(
            db,
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            fresh_settings=True,
        )
    except Exception as exc:
        logger.warning("Password reset email for %s failed: %s", to_email, exc)
        return False
    finally:
        if db is not None:
            db.close()
