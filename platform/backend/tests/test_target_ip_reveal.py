"""Target IP reveal rules for RangeBox and VPN-only sessions."""
from types import SimpleNamespace

from app.routers.curriculum import should_reveal_target_ips


def _lab(show=False):
    return SimpleNamespace(show_target_ips=show)


def _session(rangebox, subnet="10.100.1.0/24"):
    return SimpleNamespace(rangebox_enabled=rangebox, network_subnet=subnet)


def test_vpn_only_session_reveals_ips():
    assert should_reveal_target_ips(_lab(False), _session(False)) is True


def test_rangebox_session_hides_ips_by_default():
    assert should_reveal_target_ips(_lab(False), _session(True)) is False


def test_lab_opt_in_wins():
    assert should_reveal_target_ips(_lab(True), _session(True)) is True


def test_missing_session_or_subnet_hides_ips():
    assert should_reveal_target_ips(_lab(True), None) is False
    assert should_reveal_target_ips(_lab(True), _session(False, subnet=None)) is False
