"""RB-01: admin handlers must not be async when they never await.

An ``async def`` handler that performs synchronous database, Docker, or file
work blocks the event loop for every request on the worker. FastAPI runs a
plain ``def`` handler in the threadpool, which is the correct place for that
work. These handlers are the heavy ones; the list is deliberately small so the
test reads as a contract rather than a snapshot.
"""

from __future__ import annotations

import inspect

import pytest

from app.routers import admin

THREADPOOL_HANDLERS = (
    "reset_user_lab",
    "discover_labs",
    "get_system_metrics",
    "sample_system_metrics",
    "export_activity_log",
    "get_session_logs",
    "activity_calendar",
    "list_backups",
    "download_backup",
    "get_rangebox_capacity",
    "run_rangebox_capacity_test",
    "stress_test_cleanup",
    "get_data_integrity_status",
    "software_integrity_status",
)


@pytest.mark.parametrize("name", THREADPOOL_HANDLERS)
def test_admin_io_handler_runs_in_the_threadpool(name):
    handler = getattr(admin, name)
    assert not inspect.iscoroutinefunction(handler), (
        f"{name} does blocking I/O but is async; make it a plain def or "
        "offload the blocking call"
    )
