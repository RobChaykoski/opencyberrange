"""TOTP enrollment, login, and /me state tests."""
import base64

import pyotp
import pytest

pytestmark = pytest.mark.db


def test_mfa_enrollment_returns_scannable_qr(client, auth_headers):
    resp = client.post("/api/auth/mfa/enroll", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["secret"]
    assert body["provisioning_uri"].startswith("otpauth://totp/")
    assert body["qr_data_url"].startswith("data:image/png;base64,")

    png = base64.b64decode(body["qr_data_url"].split(",", 1)[1])
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(png) > 100


def test_mfa_login_requires_code_and_me_reports_enabled(
    client, auth_headers, test_user, test_password
):
    enroll = client.post("/api/auth/mfa/enroll", headers=auth_headers)
    assert enroll.status_code == 200, enroll.text
    secret = enroll.json()["secret"]

    code = pyotp.TOTP(secret).now()
    verify = client.post(
        "/api/auth/mfa/verify",
        json={"code": code},
        headers=auth_headers,
    )
    assert verify.status_code == 200, verify.text

    without_code = client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": test_password},
    )
    assert without_code.status_code == 401
    assert without_code.headers.get("x-mfa-required") == "true"

    with_code = client.post(
        "/api/auth/login",
        data={
            "username": test_user.username,
            "password": test_password,
            "totp_code": pyotp.TOTP(secret).now(),
        },
    )
    assert with_code.status_code == 200, with_code.text

    token = with_code.json()["access_token"]
    me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["mfa_enabled"] is True
