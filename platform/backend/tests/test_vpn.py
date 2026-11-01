"""WireGuard config and QR smoke tests.

The QR is generated from the same config the download endpoint returns, so this
also verifies that the config path still produces a valid WireGuard document.
"""
import pytest

pytestmark = pytest.mark.db


def test_vpn_config_download(client, auth_headers):
    resp = client.get("/api/labs/vpn-config", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert "[Interface]" in resp.text
    assert "PrivateKey" in resp.text
    assert "[Peer]" in resp.text


def test_vpn_config_qr_is_png(client, auth_headers):
    resp = client.get("/api/labs/vpn-config/qr", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("image/png")
    assert resp.headers.get("cache-control") == "no-store"
    assert resp.content.startswith(b"\x89PNG\r\n\x1a\n")
