"""Shared login-failure throttle: Redis path and memory fallback."""

from __future__ import annotations

import pytest

from app.services import login_throttle


class _FakePipeline:
    def __init__(self, store):
        self.store = store
        self.ops = []

    def zadd(self, key, mapping):
        self.ops.append(("zadd", key, mapping))
        return self

    def zremrangebyscore(self, key, low, high):
        self.ops.append(("zrem", key, low, high))
        return self

    def expire(self, key, _ttl):
        self.ops.append(("expire", key))
        return self

    def zcard(self, key):
        self.ops.append(("zcard", key))
        return self

    def execute(self):
        results = []
        for op in self.ops:
            if op[0] == "zadd":
                _, key, mapping = op
                bucket = self.store.setdefault(key, {})
                bucket.update({str(k): float(v) for k, v in mapping.items()})
                results.append(1)
            elif op[0] == "zrem":
                _, key, low, high = op
                bucket = self.store.get(key, {})
                for item in [k for k, v in bucket.items() if low <= v <= high]:
                    bucket.pop(item, None)
                results.append(0)
            elif op[0] == "expire":
                results.append(True)
            else:
                results.append(len(self.store.get(op[1], {})))
        self.ops = []
        return results


class _FakeRedis:
    def __init__(self):
        self.store = {}

    def pipeline(self):
        return _FakePipeline(self.store)

    def delete(self, key):
        self.store.pop(key, None)
        return 1


@pytest.fixture(autouse=True)
def _isolated_throttle(monkeypatch):
    login_throttle._memory.clear()
    login_throttle._redis_client = None
    login_throttle._redis_disabled_until = 0.0
    monkeypatch.setattr(login_throttle, "_client", lambda: None)
    yield
    login_throttle._memory.clear()


def test_memory_fallback_backoff_and_clear():
    now = 1_000.0
    for index in range(5):
        assert login_throttle.record("Bob", "192.0.2.1", now=now + index) == index + 1
    assert login_throttle.retry_after("bob", "192.0.2.1", now=now + 10) == 1
    assert login_throttle.record("bob", "192.0.2.1", now=now + 20) == 6
    assert login_throttle.retry_after("bob", "192.0.2.1", now=now + 20) == 2
    login_throttle.clear("bob", "192.0.2.1")
    assert login_throttle.retry_after("bob", "192.0.2.1", now=now + 20) == 0


def test_window_expiry_resets_the_count():
    assert login_throttle.record("carol", "192.0.2.2", now=0) == 1
    assert (
        login_throttle.retry_after(
            "carol", "192.0.2.2", now=login_throttle.WINDOW_SECONDS + 1
        )
        == 0
    )
    assert (
        login_throttle.record(
            "carol", "192.0.2.2", now=login_throttle.WINDOW_SECONDS + 2
        )
        == 1
    )


def test_redis_path_uses_a_hashed_key(monkeypatch):
    fake = _FakeRedis()
    monkeypatch.setattr(login_throttle, "_client", lambda: fake)
    now = 2_000.0
    for index in range(5):
        assert login_throttle.record("Dave", "198.51.100.7", now=now + index) == index + 1
    assert login_throttle.retry_after("dave", "198.51.100.7", now=now + 10) == 1
    key = next(iter(fake.store))
    assert key.startswith("ocr:loginfail:")
    assert "dave" not in key.lower()
    assert "198.51.100.7" not in key
    login_throttle.clear("dave", "198.51.100.7")
    assert login_throttle.retry_after("dave", "198.51.100.7", now=now + 10) == 0
