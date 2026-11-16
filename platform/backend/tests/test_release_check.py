"""Release comparison: version parsing, caching, and offline fallback."""

from __future__ import annotations

import app.services.release_check as release_check


def _clear_cache():
    release_check._cache.clear()


def test_version_keys_are_semantic_and_normalised():
    assert release_check._version_key("v5.16.0") == (5, 16, 0)
    assert release_check._version_key("5") == (5, 0, 0)
    assert release_check._version_key("2.5.5") == (2, 5, 5)
    assert release_check._version_key("not-a-version") is None
    assert release_check._normalise("v5.16.0") == "5.16.0"


def test_latest_uses_the_highest_stable_release_or_tag(monkeypatch):
    releases = [
        {"tag_name": "v2.5.5", "html_url": "https://example.test/v2.5.5", "name": "Old"},
        {"tag_name": "v5.16.0", "html_url": "https://example.test/v5.16.0", "name": "New"},
    ]
    tags = [{"name": "v5.15.0"}, {"name": "v5.16.0"}, {"name": "not-a-version"}]
    monkeypatch.setattr(
        release_check,
        "_fetch",
        lambda url: releases if "releases" in url else tags,
    )
    latest = release_check._latest_from_github()
    assert latest["tag"] == "v5.16.0"
    assert latest["version"] == "5.16.0"
    assert latest["release_url"] == "https://example.test/v5.16.0"


def test_status_reports_behind_and_builds_an_upgrade_path(monkeypatch):
    _clear_cache()
    monkeypatch.setattr(release_check, "APP_VERSION", "5")
    monkeypatch.setattr(
        release_check,
        "_latest_from_github",
        lambda: {
            "tag": "v5.16.0",
            "version": "5.16.0",
            "key": (5, 16, 0),
            "release_url": "https://example.test/v5.16.0",
            "release_name": "Release 5.16",
            "published_at": "2026-11-01T00:00:00Z",
            "body": "Notes",
        },
    )
    status = release_check.get_status()
    assert status["status"] == "behind"
    assert status["installed_normalised"] == "5.0.0"
    assert status["latest_normalised"] == "5.16.0"
    assert status["upgrade"]["runbook"] == "docs/DEPLOYMENT-RUNBOOK.md"
    assert any("git fetch" in command for command in status["upgrade"]["commands"])
    assert status["cached"] is False


def test_status_uses_cache_without_calling_github_twice(monkeypatch):
    _clear_cache()
    monkeypatch.setattr(release_check, "APP_VERSION", "5")
    calls = {"count": 0}

    def latest():
        calls["count"] += 1
        return {
            "tag": "v5.16.0",
            "version": "5.16.0",
            "key": (5, 16, 0),
            "release_url": "https://example.test/v5.16.0",
            "release_name": "Release 5.16",
            "published_at": None,
            "body": "",
        }

    monkeypatch.setattr(release_check, "_latest_from_github", latest)
    first = release_check.get_status()
    second = release_check.get_status()
    assert calls["count"] == 1
    assert first["status"] == "behind"
    assert second["cached"] is True


def test_status_falls_back_to_unknown_when_github_is_unreachable(monkeypatch):
    _clear_cache()

    def fail():
        raise RuntimeError("offline")

    monkeypatch.setattr(release_check, "_latest_from_github", fail)
    status = release_check.get_status(force=True)
    assert status["status"] == "unknown"
    assert status["latest"] is None
    assert "offline" in status["message"]


def test_status_returns_stale_cache_after_a_later_failure(monkeypatch):
    _clear_cache()
    monkeypatch.setattr(release_check, "APP_VERSION", "5")
    monkeypatch.setattr(
        release_check,
        "_latest_from_github",
        lambda: {
            "tag": "v5.16.0",
            "version": "5.16.0",
            "key": (5, 16, 0),
            "release_url": "https://example.test/v5.16.0",
            "release_name": "Release 5.16",
            "published_at": None,
            "body": "",
        },
    )
    release_check.get_status()

    def fail():
        raise RuntimeError("offline")

    monkeypatch.setattr(release_check, "_latest_from_github", fail)
    status = release_check.get_status(force=True)
    assert status["status"] == "behind"
    assert status["cached"] is True
    assert status["stale"] is True
