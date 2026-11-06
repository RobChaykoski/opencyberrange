"""SMTP mail delivery for platform notifications.

Settings live in ``platform_settings`` so an administrator can configure the
relay from the admin interface. Delivery is best effort: a registration must
never fail because the SMTP relay is down or unconfigured.
"""
from __future__ import annotations

import html
import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, parseaddr
from typing import Optional

from sqlalchemy.orm import Session

from app.services import settings_service

logger = logging.getLogger(__name__)


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
        support_email = getattr(settings, "PRIVACY_CONTACT_EMAIL", "") or ""
        login_url = public_base_url(db, request_base)
        login_url = f"{login_url}/login" if login_url else ""
        subject, text_body, html_body = render_registration_email(
            username=username,
            display_name=display_name,
            approved=approved,
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
        support_email = getattr(settings, "PRIVACY_CONTACT_EMAIL", "") or ""
        login_url = public_base_url(db, request_base)
        login_url = f"{login_url}/login" if login_url else ""
        subject, text_body, html_body = render_username_reminder_email(
            usernames=usernames,
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
