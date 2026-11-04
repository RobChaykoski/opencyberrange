"""Unit tests for SMTP settings and registration email rendering."""
from email import policy
from email.parser import BytesParser

from app.services import mail as mail_service


def test_registration_email_for_approved_user_includes_login_link():
    subject, text_body, html_body = mail_service.render_registration_email(
        username="alice",
        display_name="Alice Example",
        approved=True,
        login_url="https://range.example.com/login",
        support_email="help@example.com",
    )

    assert "ready" in subject.lower()
    assert "alice" in text_body
    assert "https://range.example.com/login" in text_body
    assert "https://range.example.com/login" in html_body
    assert "password" not in text_body.lower()


def test_registration_email_for_pending_user_explains_approval():
    subject, text_body, _ = mail_service.render_registration_email(
        username="bob",
        display_name="Bob",
        approved=False,
        login_url="https://range.example.com/login",
    )

    assert "received" in subject.lower()
    assert "approve" in text_body.lower()
    assert "sign in at https://range.example.com/login" not in text_body


def test_mail_config_requires_enabled_host_and_from_address():
    base = {
        "enabled": True,
        "host": "smtp.example.com",
        "from_email": "no-reply@example.com",
    }
    assert mail_service.is_configured(base) is True
    assert mail_service.is_configured({**base, "enabled": False}) is False
    assert mail_service.is_configured({**base, "host": ""}) is False
    assert mail_service.is_configured({**base, "from_email": "not-an-address"}) is False


class FakeSMTP:
    def __init__(self, host, port, timeout=None, context=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.context = context
        self.started_tls = False
        self.login_args = None
        self.message = None
        FakeSMTP.last = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def ehlo(self):
        return None

    def starttls(self, context=None):
        self.started_tls = True
        self.tls_context = context

    def login(self, username, password):
        self.login_args = (username, password)

    def send_message(self, message):
        self.message = message


def test_send_email_uses_starttls_and_login(monkeypatch):
    config = {
        "enabled": True,
        "host": "smtp.example.com",
        "port": 587,
        "security": "starttls",
        "username": "mailer",
        "password": "secret",
        "from_email": "no-reply@example.com",
        "from_name": "OpenCyberRange",
        "timeout": 10,
    }
    monkeypatch.setattr(mail_service, "mail_config", lambda db, fresh=False: config)
    monkeypatch.setattr(mail_service.smtplib, "SMTP", FakeSMTP)

    sent = mail_service.send_email(
        None,
        to_email="student@example.com",
        subject="Welcome",
        text_body="Hello",
        html_body="<p>Hello</p>",
    )

    assert sent is True
    smtp = FakeSMTP.last
    assert smtp.host == "smtp.example.com"
    assert smtp.port == 587
    assert smtp.started_tls is True
    assert smtp.login_args == ("mailer", "secret")

    parsed = BytesParser(policy=policy.default).parsebytes(smtp.message.as_bytes())
    assert parsed["From"] == "OpenCyberRange <no-reply@example.com>"
    assert parsed["To"] == "student@example.com"
    assert parsed["Subject"] == "Welcome"


def test_send_email_skips_when_mail_disabled(monkeypatch):
    monkeypatch.setattr(
        mail_service,
        "mail_config",
        lambda db, fresh=False: {"enabled": False, "host": "smtp.example.com"},
    )

    assert mail_service.send_email(
        None,
        to_email="student@example.com",
        subject="Welcome",
        text_body="Hello",
    ) is False
