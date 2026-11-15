"""Regression checks for the security-review hardening."""

import inspect
import re

import pytest
from starlette.requests import Request

from app.auth import (
    get_current_active_user,
    get_current_admin_user,
    get_current_instructor_user,
    get_current_user,
)
from app.routers.labs import _client_ip
from app.services.db_integrity import LEDGER_TABLES
from app.services.docker_manager import DockerManager, validate_lab_compose
from app.services.erasure import _OPTIONAL_USER_REFERENCES


def test_client_ip_uses_uvicorn_sanitised_address():
    request = Request(
        {
            "type": "http",
            "client": ("203.0.113.9", 12345),
            "headers": [(b"x-forwarded-for", b"198.51.100.7, 203.0.113.9")],
        }
    )

    assert _client_ip(request) == "203.0.113.9"


def test_auth_dependencies_run_in_the_threadpool():
    for dependency in (
        get_current_user,
        get_current_active_user,
        get_current_admin_user,
        get_current_instructor_user,
    ):
        assert not inspect.iscoroutinefunction(dependency), dependency.__name__


@pytest.mark.parametrize(
    "service",
    [
        {"privileged": True},
        {"network_mode": "host"},
        {"pid": "host"},
        {"volumes": ["/var/run/docker.sock:/var/run/docker.sock"]},
        {"volumes": ["../../etc:/etc"]},
        {"devices": ["/dev/sda:/dev/sda"]},
        {"cap_add": ["SYS_ADMIN"]},
    ],
)
def test_compose_guard_rejects_host_escape_features(service):
    with pytest.raises(ValueError):
        validate_lab_compose({"services": {"target": service}}, "test-lab")


def test_compose_guard_allows_lab_relative_binds_and_net_admin():
    validate_lab_compose(
        {
            "services": {
                "target": {
                    "volumes": ["./containers/target/config:/config:ro"],
                    "cap_add": ["NET_ADMIN", "NET_RAW"],
                }
            }
        },
        "test-lab",
    )


def test_sql_identifier_lists_are_fixed_constants():
    identifier = re.compile(r"^[a-z][a-z0-9_]*$")
    for table, column, action in _OPTIONAL_USER_REFERENCES:
        assert identifier.fullmatch(table), table
        assert identifier.fullmatch(column), column
        assert action in {"delete", "null"}, action
    for table in LEDGER_TABLES:
        assert identifier.fullmatch(table), table


def test_lab_services_get_default_process_and_capability_limits():
    assert DockerManager.LAB_PIDS_LIMIT <= 1024
    assert "SYS_ADMIN" in DockerManager.LAB_DEFAULT_CAP_DROP
    assert "SYS_PTRACE" in DockerManager.LAB_DEFAULT_CAP_DROP
    assert "SETUID" not in DockerManager.LAB_DEFAULT_CAP_DROP
    assert "SETGID" not in DockerManager.LAB_DEFAULT_CAP_DROP
