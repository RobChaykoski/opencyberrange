"""Password breach checks: k-anonymity, fail-open, and endpoint wiring."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.models import PlatformSetting
from app.services import password_breach

pytestmark = pytest.mark.db


def _set_setting(db_session, value: str) -> None:
    row = (
        db_session.query(PlatformSetting)
        .filter(PlatformSetting.key == "password_breach_check_enabled")
        .first()
    )
    if row is None:
        row = PlatformSetting(
            key="password_breach_check_enabled",
            value=value,
            category="security",
            description="test",
            is_secret=False,
        )
        db_session.add(row)
    else:
        row.value = value
    db_session.commit()


def test_sha1_prefix_is_the_only_value_sent_to_the_range_api(monkeypatch):
    captured = {}

    def fake_fetch(prefix):
        captured["prefix"] = prefix
        return "00112233445566778899AABBCCDDEEFF0011:7\r\n"

    monkeypatch.setattr(password_breach, "_fetch_range", fake_fetch)
    import asyncio

    count = asyncio.run(password_breach.breach_count("Correct#Horse7Battery"))

    digest = password_breach.password_sha1("Correct#Horse7Battery")
    assert captured["prefix"] == digest[:5]
    assert len(captured["prefix"]) == 5
    assert digest[5:] not in captured["prefix"]
    assert count == 0


def test_parse_range_response_matches_the_suffix_case_insensitively():
    suffix = "1E4C9B93F3F0682250B6CF8331B7EE68FD8"
    text = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:1\r\n" f"{suffix.lower()}:42\r\n"

    assert password_breach.parse_range_response(text, suffix) == 42
    assert password_breach.parse_range_response(text, "NOTTHERE") == 0
    assert password_breach.parse_range_response("malformed", suffix) == 0


def test_range_failure_returns_none(monkeypatch):
    monkeypatch.setattr(password_breach, "_fetch_range", lambda prefix: None)
    import asyncio

    assert asyncio.run(password_breach.breach_count("Correct#Horse7Battery")) is None


def test_breach_check_is_disabled_by_default(db_session, monkeypatch):
    _set_setting(db_session, "false")

    async def should_not_run(password):
        raise AssertionError("breach API must not be called when disabled")

    monkeypatch.setattr(password_breach, "breach_count", should_not_run)
    import asyncio

    assert (
        asyncio.run(
            password_breach.enforce_password_breach_check(
                db_session, "Correct#Horse7Battery"
            )
        )
        is None
    )


def test_breach_check_rejects_a_listed_password(db_session, monkeypatch):
    _set_setting(db_session, "true")

    async def listed(password):
        return 3

    monkeypatch.setattr(password_breach, "breach_count", listed)
    import asyncio

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            password_breach.enforce_password_breach_check(
                db_session, "Correct#Horse7Battery"
            )
        )
    assert exc.value.status_code == 400
    assert "known data breach" in exc.value.detail


def test_breach_check_fails_open_when_the_api_is_unavailable(
    db_session, monkeypatch
):
    _set_setting(db_session, "true")

    async def unavailable(password):
        return None

    monkeypatch.setattr(password_breach, "breach_count", unavailable)
    import asyncio

    assert (
        asyncio.run(
            password_breach.enforce_password_breach_check(
                db_session, "Correct#Horse7Battery"
            )
        )
        is None
    )


def test_change_password_returns_400_for_a_breached_password(
    client, db_session, auth_headers, test_password, monkeypatch
):
    _set_setting(db_session, "true")
    new_password = "New#Strong9Pass"
    suffix = password_breach.password_sha1(new_password)[5:]
    monkeypatch.setattr(
        password_breach,
        "_fetch_range",
        lambda prefix: f"{suffix}:19\r\n",
    )

    rejected = client.post(
        "/api/auth/change-password",
        json={
            "current_password": test_password,
            "new_password": new_password,
            "confirm_password": new_password,
        },
        headers=auth_headers,
    )

    assert rejected.status_code == 400, rejected.text
    assert "known data breach" in rejected.json()["detail"]

    # Disabling the check restores the normal policy-only path.
    _set_setting(db_session, "false")
    accepted = client.post(
        "/api/auth/change-password",
        json={
            "current_password": test_password,
            "new_password": new_password,
            "confirm_password": new_password,
        },
        headers=auth_headers,
    )
    assert accepted.status_code == 200, accepted.text
