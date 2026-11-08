"""Unicode and attack-payload validation for account inputs."""

import uuid

import pytest

from app.auth import get_password_hash
from app.models import User
from app.routers.auth import RegisterRequest
from app.services.input_safety import (
    normalize_identifier,
    normalize_text,
)

PASSWORD = "Correct#Horse7Battery"


def _register_payload(**overrides):
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"unicode_{suffix}",
        "email": f"unicode_{suffix}@example.org",
        "password": PASSWORD,
        "send_registration_email": False,
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    "value",
    [
        "漢字の名前",
        "Zoë",
        "محمد",
        "नमस्ते",
        "Emoji 🙂",
        "Renée O'Brien",
    ],
)
def test_display_names_allow_legitimate_unicode(value):
    assert normalize_text(value, field="name") == value


@pytest.mark.parametrize(
    "value,reason",
    [
        ("bad\x00name", "null"),
        ("bad\x07name", "control"),
        ("bad\u202ename", "bidirectional"),
        ("bad\u200bname", "invisible"),
        ("bad\ufeffname", "invisible"),
        ("bad\ud800name", "control"),
        ("bad\ufdd0name", "noncharacter"),
        ("line\nbreak", "line break"),
    ],
)
def test_dangerous_characters_are_rejected(value, reason):
    with pytest.raises(ValueError):
        normalize_text(value, field="name")


def test_multiline_text_allows_newlines_but_not_crlf_injection():
    assert normalize_text("one\ntwo", allow_newlines=True) == "one\ntwo"
    with pytest.raises(ValueError):
        normalize_text("one\r\ntwo", allow_newlines=False)


def test_fullwidth_text_is_normalised():
    assert normalize_text("ＡＤＭＩＮ", field="name") == "ADMIN"


def test_identifiers_reject_non_ascii_and_homoglyphs():
    with pytest.raises(ValueError):
        normalize_identifier("аdmin", field="username")  # Cyrillic а
    with pytest.raises(ValueError):
        normalize_identifier("管理者", field="username")
    assert normalize_identifier("admin_1", field="username") == "admin_1"


def test_register_schema_accepts_kanji_name():
    request = RegisterRequest(**_register_payload(first_name="漢字"))
    assert request.first_name == "漢字"


def test_register_schema_rejects_bidi_name():
    with pytest.raises(ValueError):
        RegisterRequest(**_register_payload(first_name="bad\u202ename"))


def test_register_schema_rejects_homoglyph_username():
    with pytest.raises(ValueError):
        RegisterRequest(**_register_payload(username="аdmin"))


def test_registration_stores_sql_payload_as_literal_text(client, db_session):
    payload = _register_payload(first_name="' OR 1=1 --")
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200, response.text
    user = db_session.query(User).filter(User.username == payload["username"]).first()
    assert user is not None
    assert user.first_name == "' OR 1=1 --"


def test_registration_rejects_bidi_name(client):
    response = client.post(
        "/api/auth/register",
        json=_register_payload(first_name="bad\u202ename"),
    )
    assert response.status_code == 422


def test_login_rejects_homoglyph_username(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"real_{suffix}",
        email=f"real_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": f"reаl_{suffix}", "password": PASSWORD},  # Cyrillic а
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_pending_account_uses_generic_error(client, db_session):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"pending_{suffix}",
        email=f"pending_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=False,
        role="student",
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
