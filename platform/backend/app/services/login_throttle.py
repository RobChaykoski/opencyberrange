"""Shared login-failure throttle.

The login backoff is keyed by (username, client IP). With more than one uvicorn
worker, an in-process counter multiplies the effective limit. Use the configured
Redis/Valkey store when it is available, with a bounded in-process fallback so a
cache outage cannot take authentication down.
"""

from __future__ import annotations

import hashlib
import os
import threading
import time

try:  # The dependency is present in production; the fallback keeps local use safe.
    import redis
except ImportError:  # pragma: no cover - packaging error
    redis = None  # type: ignore[assignment]

MAX_FAILED_ATTEMPTS = 5
WINDOW_SECONDS = 15 * 60
MAX_BACKOFF_SECONDS = 60
REDIS_RETRY_SECONDS = 30
MEMORY_LIMIT = 10_000

_memory: dict[str, tuple[float, int]] = {}
_memory_lock = threading.Lock()
_redis_client = None
_redis_disabled_until = 0.0
_redis_lock = threading.Lock()


def _redis_uri() -> str:
    uri = (os.environ.get("RATELIMIT_STORAGE_URI") or "").strip()
    return uri if uri.startswith(("redis://", "rediss://")) else ""


def _client():
    """Return a live Redis client, or None when the memory fallback is active."""
    global _redis_client, _redis_disabled_until
    uri = _redis_uri()
    if not uri or redis is None:
        return None
    now = time.monotonic()
    with _redis_lock:
        if now < _redis_disabled_until:
            return None
        if _redis_client is not None:
            return _redis_client
        try:
            client = redis.Redis.from_url(
                uri,
                socket_timeout=1.0,
                socket_connect_timeout=1.0,
                decode_responses=True,
            )
            client.ping()
            _redis_client = client
            return client
        except Exception:
            _redis_client = None
            _redis_disabled_until = now + REDIS_RETRY_SECONDS
            return None


def _disable_redis() -> None:
    global _redis_client, _redis_disabled_until
    with _redis_lock:
        _redis_client = None
        _redis_disabled_until = time.monotonic() + REDIS_RETRY_SECONDS


def _key(username: str, ip_address: str | None) -> str:
    material = f"{(username or '').strip().lower()}\0{ip_address or 'unknown'}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return f"ocr:loginfail:{digest}"


def _memory_entry(key: str, now: float) -> tuple[float, int] | None:
    entry = _memory.get(key)
    if entry and now - entry[0] > WINDOW_SECONDS:
        _memory.pop(key, None)
        return None
    return entry


def _backoff(count: int) -> int:
    if count < MAX_FAILED_ATTEMPTS:
        return 0
    return min(MAX_BACKOFF_SECONDS, 2 ** (count - MAX_FAILED_ATTEMPTS))


def record(username: str, ip_address: str | None, now: float | None = None) -> int:
    """Record a failure and return the count inside the window."""
    timestamp = time.time() if now is None else now
    key = _key(username, ip_address)
    client = _client()
    if client is not None:
        try:
            pipe = client.pipeline()
            pipe.zadd(key, {str(timestamp): timestamp})
            pipe.zremrangebyscore(key, 0, timestamp - WINDOW_SECONDS)
            pipe.expire(key, WINDOW_SECONDS + 60)
            pipe.zcard(key)
            return int(pipe.execute()[-1])
        except Exception:
            _disable_redis()
    with _memory_lock:
        entry = _memory_entry(key, timestamp)
        if entry is None:
            entry = (timestamp, 0)
        count = entry[1] + 1
        _memory[key] = (entry[0], count)
        if len(_memory) > MEMORY_LIMIT:
            for stale in [
                item
                for item, value in _memory.items()
                if timestamp - value[0] > WINDOW_SECONDS
            ]:
                _memory.pop(stale, None)
        return count


def retry_after(
    username: str, ip_address: str | None, now: float | None = None
) -> int:
    """Seconds to wait for this key, or 0 when it is within budget."""
    timestamp = time.time() if now is None else now
    key = _key(username, ip_address)
    client = _client()
    if client is not None:
        try:
            pipe = client.pipeline()
            pipe.zremrangebyscore(key, 0, timestamp - WINDOW_SECONDS)
            pipe.zcard(key)
            count = int(pipe.execute()[-1])
            return _backoff(count)
        except Exception:
            _disable_redis()
    with _memory_lock:
        entry = _memory_entry(key, timestamp)
        count = entry[1] if entry else 0
    return _backoff(count)


def clear(username: str, ip_address: str | None) -> None:
    key = _key(username, ip_address)
    client = _client()
    if client is not None:
        try:
            client.delete(key)
            return
        except Exception:
            _disable_redis()
    with _memory_lock:
        _memory.pop(key, None)
