"""Static regression checks for installer and RangeBox hardening."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"


def test_wstunnel_installer_has_no_tmp_fallback_and_verifies_checksum():
    text = (SCRIPTS / "setup-wstunnel.sh").read_text(encoding="utf-8")
    assert "/tmp/wstunnel" not in text
    assert "WSTUNNEL_SHA256_AMD64" in text
    assert "WSTUNNEL_SHA256_ARM64" in text
    assert "sha256sum" in text
    assert "checksum mismatch" in text


def test_rangebox_entrypoint_uses_sudo_for_privileged_network_ops():
    text = (ROOT / "RangeBox" / "entrypoint.sh").read_text(encoding="utf-8")
    assert "sudo -n iptables" in text
    assert "sudo -n dnsmasq" in text
    assert "sudo -n tee /etc/resolv.conf" in text


def test_peer_manager_fails_closed_and_validates_inputs():
    text = (SCRIPTS / "setup-range-server.sh").read_text(encoding="utf-8")
    assert "PEER_MANAGER_API_KEY is not set; refusing to start" in text
    assert "hmac.compare_digest" in text
    assert "Refusing to bind the Peer Manager to 0.0.0.0" in text
    assert "network.subnet_of(client_network)" in text
    assert '"preshared_key": None' in text


def test_lab_isolation_audit_has_no_unsudoed_rangebox_privilege_finding():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "audit-lab-isolation.py"), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "entrypoint-privilege" not in result.stdout
