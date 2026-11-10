"""WireGuard config and QR smoke tests.

The QR is generated from the same config the download endpoint returns, so this
also verifies that the config path still produces a valid WireGuard document.
"""
import re

import pytest

pytestmark = pytest.mark.db


def test_vpn_config_download(client, auth_headers):
    resp = client.get("/api/labs/vpn-config", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert "[Interface]" in resp.text
    assert "PrivateKey" in resp.text
    assert "[Peer]" in resp.text
    # The client only claims its own /32 address and routes its own /24.
    assert re.search(r"Address = \d+\.\d+\.\d+\.\d+/32", resp.text)
    assert re.search(r"AllowedIPs = \d+\.\d+\.\d+\.0/24", resp.text)
    assert "10.128.0.0/9" not in resp.text
    assert "10.100.0.0/14" not in resp.text


def test_vpn_client_is_not_in_the_old_home_overlap_pool():
    from app.routers.labs import get_vpn_client_ip

    assert get_vpn_client_ip(6, "10.255").startswith("10.255.")


def test_vpn_allowed_ips_is_the_students_own_lab_subnet():
    from app.routers.labs import get_subnet_id, vpn_allowed_ips

    second, third = get_subnet_id(6)
    assert vpn_allowed_ips(6) == f"10.{second}.{third}.0/24"


def test_vpn_config_qr_is_png(client, auth_headers):
    resp = client.get("/api/labs/vpn-config/qr", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("image/png")
    assert resp.headers.get("cache-control") == "no-store"
    assert resp.content.startswith(b"\x89PNG\r\n\x1a\n")
