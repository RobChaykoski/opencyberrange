"""Policy tests for removing stale lab networks during a spawn."""
from app.services.docker_manager import _is_stale_user_lab_network


def test_stale_lab_network_is_removed():
    assert _is_stale_user_lab_network("lab_7_old-lab", 7, set()) is True


def test_active_lab_network_is_preserved():
    active = {"lab_7_new-lab"}
    assert _is_stale_user_lab_network("lab_7_new-lab", 7, active) is False


def test_other_users_network_is_preserved():
    assert _is_stale_user_lab_network("lab_8_old-lab", 7, set()) is False


def test_similar_prefix_without_separator_is_preserved():
    assert _is_stale_user_lab_network("lab_70_old-lab", 7, set()) is False
