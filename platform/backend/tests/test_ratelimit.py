"""Rate limiter construction must survive a Redis outage."""

from app.ratelimit import create_limiter, rate_limit_storage_uri


def test_default_storage_is_process_memory(monkeypatch):
    monkeypatch.delenv("RATELIMIT_STORAGE_URI", raising=False)

    assert rate_limit_storage_uri() == "memory://"


def test_configured_storage_uri_is_used(monkeypatch):
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://redis:6379/0")

    assert rate_limit_storage_uri() == "redis://redis:6379/0"


def test_limiter_swallows_storage_errors(monkeypatch):
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://redis:6379/0")

    limiter = create_limiter()

    assert limiter._swallow_errors is True
    assert limiter._in_memory_fallback_enabled is True
    assert limiter._storage_uri == "redis://redis:6379/0"
