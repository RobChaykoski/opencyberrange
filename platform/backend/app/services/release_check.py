"""Compare this installation with the latest published GitHub release.

The check is deliberately small and offline-safe:

* the result is cached for 15 minutes so a dashboard refresh cannot exhaust the
  unauthenticated GitHub API limit;
* a network failure returns the last good result with ``stale: true``;
* a first-run failure returns ``unknown`` instead of failing the admin page;
* only public release metadata is returned, never a token or repository secret.

Set ``GITHUB_TOKEN`` (or ``GH_TOKEN``) to raise the GitHub API rate limit. The
token is read from the environment and is never included in the response.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

from app.version import APP_VERSION

REPOSITORY = os.environ.get(
    "OCR_RELEASE_REPOSITORY", "RobChaykoski/opencyberrange"
).strip()
CACHE_TTL_SECONDS = int(os.environ.get("OCR_RELEASE_CHECK_TTL", "900") or "900")
TIMEOUT_SECONDS = float(os.environ.get("OCR_RELEASE_CHECK_TIMEOUT", "4") or "4")
USER_AGENT = "OpenCyberRange-release-check/1.0"

_VERSION_RE = re.compile(r"^v?(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:[-+].*)?$")
_lock = threading.Lock()
_cache: dict[str, Any] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _version_key(value: str) -> tuple[int, int, int] | None:
    match = _VERSION_RE.match(str(value or "").strip())
    if not match:
        return None
    return tuple(int(part or 0) for part in match.groups())  # type: ignore[return-value]


def _normalise(value: str) -> str:
    key = _version_key(value)
    return ".".join(str(part) for part in key) if key else str(value or "").strip()


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch(url: str) -> Any:
    request = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _latest_from_github() -> dict[str, Any]:
    releases: list[dict[str, Any]] = []
    tags: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        releases = _fetch(
            f"https://api.github.com/repos/{REPOSITORY}/releases?per_page=30"
        )
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        errors.append(f"releases: {exc}")
    try:
        tags = _fetch(f"https://api.github.com/repos/{REPOSITORY}/tags?per_page=100")
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        errors.append(f"tags: {exc}")
    if not releases and not tags:
        raise RuntimeError("; ".join(errors) or "GitHub returned no release data")

    candidates: list[dict[str, Any]] = []
    release_by_tag = {
        str(item.get("tag_name") or ""): item
        for item in releases
        if item.get("tag_name")
    }
    for item in [*releases, *tags]:
        tag = str(item.get("tag_name") or item.get("name") or "").strip()
        key = _version_key(tag)
        if not key:
            continue
        release = release_by_tag.get(tag) or {}
        candidates.append(
            {
                "tag": tag,
                "version": _normalise(tag),
                "key": key,
                "release_url": release.get("html_url")
                or f"https://github.com/{REPOSITORY}/releases/tag/{tag}",
                "release_name": release.get("name") or tag,
                "published_at": release.get("published_at")
                or release.get("created_at"),
                "body": (release.get("body") or "").strip()[:600],
                "prerelease": bool(release.get("prerelease")),
                "draft": bool(release.get("draft")),
            }
        )
    if not candidates:
        raise RuntimeError("no semantic version tag was found")
    stable = [item for item in candidates if not item["prerelease"] and not item["draft"]]
    return max(stable or candidates, key=lambda item: item["key"])


def _upgrade_path(latest: str) -> dict[str, Any]:
    tag = f"v{latest}" if not latest.startswith("v") else latest
    return {
        "summary": (
            "Back up, check out the signed release tag, rebuild the backend and "
            "frontend, apply migrations, and verify the deployment."
        ),
        "runbook": "docs/DEPLOYMENT-RUNBOOK.md",
        "readiness": "docs/RELEASE-5-PRODUCTION-READINESS.md",
        "releases": "docs/RELEASES.md",
        "commands": [
            "bash scripts/backup-production.sh",
            f"git fetch origin --tags && git checkout {tag}",
            "cd platform && docker compose -f docker-compose.prod.yml -f docker-compose.adopt.yml -f docker-compose.override.yml build backend frontend",
            "cd platform && docker compose -f docker-compose.prod.yml -f docker-compose.adopt.yml -f docker-compose.override.yml up -d backend frontend",
            "docker exec ocr-backend alembic -c alembic.ini upgrade head",
            "bash scripts/monitor-deployment.sh",
        ],
        "rollback": (
            "Restore the pre-deploy database dump and the retained previous image "
            "tags; see the readiness rollback section."
        ),
        "note": (
            "Production cutover remains a separate, password-confirmed change. "
            "This indicator never deploys anything by itself."
        ),
    }


def _result(
    *,
    installed: str,
    latest: str | None,
    latest_tag: str | None,
    release_url: str | None,
    release_name: str | None,
    published_at: str | None,
    body: str,
    status: str,
    cached: bool,
    stale: bool,
    message: str,
) -> dict[str, Any]:
    upgrade = _upgrade_path(latest) if latest else None
    return {
        "installed": installed,
        "installed_normalised": _normalise(installed),
        "latest": latest,
        "latest_tag": latest_tag,
        "latest_normalised": _normalise(latest) if latest else None,
        "status": status,
        "release_url": release_url,
        "release_name": release_name,
        "published_at": published_at,
        "release_notes": body,
        "checked_at": _now(),
        "cached": cached,
        "stale": stale,
        "message": message,
        "upgrade": upgrade,
    }


def get_status(force: bool = False) -> dict[str, Any]:
    """Return the cached release status, refreshing from GitHub when due."""
    installed = APP_VERSION
    with _lock:
        cached = dict(_cache) if _cache else {}
    now = time.time()
    if not force and cached.get("fetched_at") and now - cached["fetched_at"] < CACHE_TTL_SECONDS:
        result = dict(cached["result"])
        result["cached"] = True
        return result

    try:
        latest = _latest_from_github()
        installed_key = _version_key(installed) or (0, 0, 0)
        latest_key = latest["key"]
        if latest_key > installed_key:
            status = "behind"
            message = (
                f"This installation is on {_normalise(installed)}; the latest "
                f"published GitHub release is {latest['tag']}."
            )
        elif latest_key < installed_key:
            status = "ahead"
            message = (
                f"This installation is on {_normalise(installed)}, ahead of the "
                f"latest published GitHub release {latest['tag']}."
            )
        else:
            status = "current"
            message = (
                f"This installation matches the latest published GitHub "
                f"release {latest['tag']}."
            )
        result = _result(
            installed=installed,
            latest=latest["version"],
            latest_tag=latest["tag"],
            release_url=latest["release_url"],
            release_name=latest["release_name"],
            published_at=latest["published_at"],
            body=latest["body"],
            status=status,
            cached=False,
            stale=False,
            message=message,
        )
        with _lock:
            _cache.clear()
            _cache.update({"fetched_at": now, "result": result})
        return result
    except Exception as exc:  # noqa: BLE001 - a status check must not break the admin page
        message = f"Could not check the latest GitHub release: {exc}"
        if cached.get("result"):
            result = dict(cached["result"])
            result.update(
                {
                    "cached": True,
                    "stale": True,
                    "checked_at": _now(),
                    "message": message + " Showing the last successful check.",
                }
            )
            return result
        return _result(
            installed=installed,
            latest=None,
            latest_tag=None,
            release_url=None,
            release_name=None,
            published_at=None,
            body="",
            status="unknown",
            cached=False,
            stale=False,
            message=message,
        )
