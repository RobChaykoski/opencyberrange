"""RangeBox capacity is a stable denominator with a live memory gate."""

import pytest

from app.services.docker_manager import DockerManager, RangeBoxCapacityError

GB = 1024 ** 3


def _manager(monkeypatch, *, total_gb=32, available_gb=28, running=0):
    # Bypass DockerManager.__init__ so the test does not need a Docker daemon.
    manager = object.__new__(DockerManager)
    monkeypatch.setattr(
        manager, "_mem_total_bytes", staticmethod(lambda: total_gb * GB)
    )
    monkeypatch.setattr(
        manager, "_mem_available_bytes", staticmethod(lambda: available_gb * GB)
    )
    monkeypatch.setattr(manager, "_count_running_rangeboxes", lambda: running)
    return manager


def test_capacity_denominator_does_not_grow_as_boxes_start(monkeypatch):
    manager = _manager(monkeypatch, total_gb=32, available_gb=28, running=0)

    initial = manager.MAX_CONCURRENT_RANGEBOXES
    assert initial == 12  # (32 GB - 8 GB reserve) / 2 GB per box

    for running in (1, 2, 5):
        monkeypatch.setattr(manager, "_count_running_rangeboxes", lambda r=running: r)
        assert manager.MAX_CONCURRENT_RANGEBOXES == initial


def test_capacity_respects_explicit_override(monkeypatch):
    manager = _manager(monkeypatch)
    monkeypatch.setattr(manager, "_RANGEBOX_MAX_OVERRIDE", "3")

    assert manager.MAX_CONCURRENT_RANGEBOXES == 3


def test_memory_headroom_is_a_separate_live_check(monkeypatch):
    manager = _manager(monkeypatch, available_gb=9, running=0)
    assert manager.has_rangebox_memory_headroom() is False

    monkeypatch.setattr(
        manager, "_mem_available_bytes", staticmethod(lambda: 10 * GB)
    )
    assert manager.has_rangebox_memory_headroom() is True


def test_capacity_check_blocks_at_cap_and_on_memory_pressure(monkeypatch):
    at_cap = _manager(monkeypatch, available_gb=28, running=12)
    with pytest.raises(RangeBoxCapacityError):
        at_cap._check_rangebox_capacity()

    low_memory = _manager(monkeypatch, available_gb=9, running=1)
    with pytest.raises(RangeBoxCapacityError):
        low_memory._check_rangebox_capacity()
