"""RangeBox capacity is a stable denominator with live memory/CPU/disk gates."""

from types import SimpleNamespace

import pytest

from app.services.docker_manager import DockerManager, RangeBoxCapacityError

GB = 1024 ** 3


def _manager(monkeypatch, *, total_gb=32, available_gb=28, running=0, cpu_count=64):
    # Bypass DockerManager.__init__ so the test does not need a Docker daemon.
    manager = object.__new__(DockerManager)
    monkeypatch.setattr(
        manager, "_mem_total_bytes", staticmethod(lambda: total_gb * GB)
    )
    monkeypatch.setattr(
        manager, "_mem_available_bytes", staticmethod(lambda: available_gb * GB)
    )
    monkeypatch.setattr(manager, "_count_running_rangeboxes", lambda: running)
    # Keep the host's real CPU/disk out of the fixture.
    monkeypatch.setattr("app.services.docker_manager.os.cpu_count", lambda: cpu_count)
    monkeypatch.setattr(
        "app.services.docker_manager.shutil.disk_usage",
        lambda _path: SimpleNamespace(free=100 * GB),
    )
    # Keep the database out of the fixture; the policy tests cover the setting.
    monkeypatch.setattr(manager, "_rangebox_capacity_percent", lambda: 75)
    monkeypatch.setattr(manager, "_rangebox_stress_max", lambda: 0)
    return manager


def test_capacity_denominator_does_not_grow_as_boxes_start(monkeypatch):
    manager = _manager(monkeypatch, total_gb=32, available_gb=28, running=0)

    initial = manager.MAX_CONCURRENT_RANGEBOXES
    assert initial == 9  # 75% of the 12-box physical ceiling

    for running in (1, 2, 5):
        monkeypatch.setattr(manager, "_count_running_rangeboxes", lambda r=running: r)
        assert manager.MAX_CONCURRENT_RANGEBOXES == initial


def test_capacity_percentage_is_applied_to_the_physical_maximum(monkeypatch):
    manager = _manager(monkeypatch, total_gb=32, available_gb=28, running=0)
    monkeypatch.setattr(manager, "_rangebox_capacity_percent", lambda: 50)

    assert manager.MAX_CONCURRENT_RANGEBOXES == 6


def test_capacity_uses_the_measured_stress_ceiling(monkeypatch):
    manager = _manager(monkeypatch, total_gb=32, available_gb=28, running=0)
    monkeypatch.setattr(manager, "_rangebox_stress_max", lambda: 8)

    assert manager.MAX_CONCURRENT_RANGEBOXES == 6  # 75% of 8, not 12


def test_measured_stress_ceiling_cannot_exceed_the_computed_maximum(monkeypatch):
    manager = _manager(monkeypatch, total_gb=32, available_gb=28, running=0)
    monkeypatch.setattr(manager, "_rangebox_stress_max", lambda: 30)

    assert manager.MAX_CONCURRENT_RANGEBOXES == 9  # clamped to 12, then 75%


def test_capacity_percentage_never_rounds_below_one_box(monkeypatch):
    manager = _manager(monkeypatch, total_gb=10, available_gb=8, running=0)
    monkeypatch.setattr(manager, "_rangebox_capacity_percent", lambda: 10)

    assert manager.MAX_CONCURRENT_RANGEBOXES == 1


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


def test_capacity_uses_cpu_limit_on_small_hosts(monkeypatch):
    manager = _manager(monkeypatch, total_gb=64, available_gb=60, cpu_count=8)
    # (8 vCPU - 2 reserve) / 0.5 CPU per box = 12 physical; 75% leaves 9.
    assert manager.MAX_CONCURRENT_RANGEBOXES == 9


def test_capacity_check_blocks_on_low_disk(monkeypatch):
    manager = _manager(monkeypatch, available_gb=28, running=1)
    monkeypatch.setattr(
        "app.services.docker_manager.shutil.disk_usage",
        lambda _path: SimpleNamespace(free=5 * GB),
    )
    assert manager.has_rangebox_disk_headroom() is False
    with pytest.raises(RangeBoxCapacityError):
        manager._check_rangebox_capacity()


def test_spawn_lock_serializes_concurrent_launches():
    import threading
    import time

    from app.services.docker_manager import rangebox_spawn_lock

    active = 0
    maximum = 0
    guard = threading.Lock()

    def worker():
        nonlocal active, maximum
        with rangebox_spawn_lock():
            with guard:
                active += 1
                maximum = max(maximum, active)
            time.sleep(0.05)
            with guard:
                active -= 1

    threads = [threading.Thread(target=worker) for _ in range(6)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert maximum == 1
