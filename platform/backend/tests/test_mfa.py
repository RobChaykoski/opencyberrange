"""TOTP enrollment QR smoke test."""
import base64

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
