"""Aggregated ransomware activity snapshots.

The platform uses RansomLook's public aggregate endpoints as a data source, not
its AGPL-3.0 code. A snapshot contains totals and per-group post counts only.
Victim names, post links, crypto addresses, and peer addresses are never read,
stored, or returned.

See ADR 0009.
"""

from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_PATH = DATA_DIR / "ransomware-activity.json"
ENV_PATH = "RANSOMWARE_ACTIVITY_SNAPSHOT"

SCHEMA_VERSION = 1
MODES = {"sample", "snapshot"}
MAX_BYTES = 256 * 1024
GROUP_NAME = re.compile(r"^[a-z0-9][a-z0-9 ._&()$'\-]{0,79}$")
FORBIDDEN = ("http", "www.", "@", "://", "magnet:", "onion")

TOTAL_FIELDS = (
    "posts_24h",
    "posts_month",
    "posts_90d",
    "posts_year",
    "posts_total",
    "groups",
    "groups_online",
    "markets",
    "window_posts",
)

_CACHE_LOCK = threading.Lock()
_CACHE: dict[str, Any] = {"key": None, "value": None}


class RansomwareActivityError(Exception):
    """The snapshot is missing, unreadable, or breaks the aggregation rules."""

    status_code = 503
    code = "ransomware_activity_unavailable"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _snapshot_path() -> Path:
    override = os.environ.get(ENV_PATH)
    return Path(override) if override else DEFAULT_PATH


def _read_json(path: Path) -> dict[str, Any]:
    try:
        stat = path.stat()
    except OSError as exc:
        raise RansomwareActivityError(f"snapshot is not available: {exc}") from exc
    if stat.st_size > MAX_BYTES:
        raise RansomwareActivityError("snapshot is larger than the allowed size")
    try:
        with path.open(encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError) as exc:
        raise RansomwareActivityError(f"snapshot cannot be read: {exc}") from exc
    if not isinstance(document, dict):
        raise RansomwareActivityError("snapshot must be a JSON object")
    return document


def _text(value: Any, field: str, *, required: bool = True) -> str:
    if value is None and not required:
        return ""
    if not isinstance(value, str) or (required and not value.strip()):
        raise RansomwareActivityError(f"snapshot field {field!r} is invalid")
    return value.strip()


def _count(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RansomwareActivityError(f"snapshot field {field!r} must be a non-negative integer")
    return value


def _parse_time(value: Any) -> str:
    if not isinstance(value, str):
        raise RansomwareActivityError("snapshot generated_at must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RansomwareActivityError("snapshot generated_at is not ISO 8601") from exc
    if parsed.tzinfo is None:
        raise RansomwareActivityError("snapshot generated_at needs a timezone")
    return value


def _groups(document: dict[str, Any], window_posts: int) -> list[dict[str, Any]]:
    rows = document.get("groups")
    if not isinstance(rows, list) or not rows:
        raise RansomwareActivityError("snapshot groups must be a non-empty list")
    seen: set[str] = set()
    cleaned: list[dict[str, Any]] = []
    for entry in rows:
        if not isinstance(entry, dict):
            raise RansomwareActivityError("group entries must be objects")
        name = _text(entry.get("name"), "groups.name")
        if not GROUP_NAME.match(name):
            raise RansomwareActivityError(f"group name is not allowed: {name!r}")
        lowered = name.lower()
        if any(token in lowered for token in FORBIDDEN):
            raise RansomwareActivityError(f"group name contains a forbidden token: {name!r}")
        if lowered in seen:
            raise RansomwareActivityError(f"duplicate group name {name!r}")
        seen.add(lowered)
        count = _count(entry.get("count"), "groups.count")
        cleaned.append({"name": name, "count": count})
    cleaned.sort(key=lambda item: (-item["count"], item["name"]))
    if sum(row["count"] for row in cleaned) > window_posts:
        raise RansomwareActivityError("group counts exceed the reported window total")
    for row in cleaned:
        row["share"] = round(row["count"] / window_posts, 4) if window_posts else 0.0
    return cleaned


def _validate(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("schema_version") != SCHEMA_VERSION:
        raise RansomwareActivityError("unsupported snapshot schema")
    mode = document.get("mode")
    if mode not in MODES:
        raise RansomwareActivityError("snapshot mode must be 'sample' or 'snapshot'")

    generated_at = _parse_time(document.get("generated_at"))
    window_days = document.get("window_days")
    if isinstance(window_days, bool) or not isinstance(window_days, int) or window_days < 1:
        raise RansomwareActivityError("snapshot window_days must be a positive integer")

    source = document.get("source")
    if not isinstance(source, dict):
        raise RansomwareActivityError("snapshot source is required")
    name = _text(source.get("name"), "source.name")
    url = _text(source.get("url"), "source.url")
    licence = _text(source.get("licence"), "source.licence")
    attribution = _text(source.get("attribution"), "source.attribution")

    method = document.get("method")
    if not isinstance(method, dict):
        raise RansomwareActivityError("snapshot method is required")
    for flag in ("victim_details", "links", "crypto_addresses"):
        if method.get(flag) is not False:
            raise RansomwareActivityError(
                f"snapshot method.{flag} must be false; only aggregates are allowed"
            )

    raw_totals = document.get("totals")
    if not isinstance(raw_totals, dict):
        raise RansomwareActivityError("snapshot totals are required")
    totals = {
        field: _count(raw_totals.get(field), f"totals.{field}")
        for field in TOTAL_FIELDS
    }

    groups = _groups(document, totals["window_posts"])

    notes = document.get("notes", [])
    if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
        raise RansomwareActivityError("snapshot notes must be a list of strings")

    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "sample": mode == "sample",
        "generated_at": generated_at,
        "window_days": window_days,
        "source": {
            "name": name,
            "url": url,
            "licence": licence,
            "attribution": attribution,
        },
        "method": {
            "aggregation": "group",
            "victim_details": False,
            "links": False,
            "crypto_addresses": False,
        },
        "totals": totals,
        "groups": groups,
        "notes": [note.strip() for note in notes if note.strip()],
    }


def snapshot(path: Path | None = None) -> dict[str, Any]:
    """Return the validated snapshot, cached until the file changes."""

    target = path or _snapshot_path()
    try:
        stat = target.stat()
        cache_key = f"{target}:{stat.st_mtime_ns}:{stat.st_size}"
    except OSError as exc:
        raise RansomwareActivityError(
            "ransomware-activity snapshot is not installed"
        ) from exc

    with _CACHE_LOCK:
        if _CACHE["key"] == cache_key and _CACHE["value"] is not None:
            return _CACHE["value"]

    value = _validate(_read_json(target))

    with _CACHE_LOCK:
        _CACHE["key"] = cache_key
        _CACHE["value"] = value
    return value


def reset_cache() -> None:
    """Clear the module cache (tests and an explicit snapshot refresh)."""

    with _CACHE_LOCK:
        _CACHE["key"] = None
        _CACHE["value"] = None
