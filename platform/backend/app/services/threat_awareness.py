"""Aggregated threat-awareness snapshots.

The platform deliberately never stores or renders individual threat addresses.
A snapshot contains country-level and category-level counts produced offline by
``scripts/fetch-threat-feed.py``. This module loads and validates that snapshot,
adds derived shares, and refuses anything that looks like an address.

Design rules (see ADR 0008):

* aggregation only - countries and categories, never hosts;
* minimum bucket size so a small country cannot be inferred from a count;
* no runtime egress;
* a labelled sample snapshot ships with the platform.
"""

from __future__ import annotations

import ipaddress
import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_PATH = DATA_DIR / "threat-awareness.json"
ENV_PATH = "THREAT_AWARENESS_SNAPSHOT"

SCHEMA_VERSION = 1
MODES = {"sample", "snapshot"}
MAX_BYTES = 512 * 1024

_HOST_TOKEN = re.compile(r"[0-9A-Fa-f:.]+")
_ISO2 = re.compile(r"^[A-Z]{2}$")

_CACHE_LOCK = threading.Lock()
_CACHE: dict[str, Any] = {"key": None, "value": None}


class ThreatAwarenessError(Exception):
    """The snapshot is missing, unreadable, or breaks the aggregation rules."""

    status_code = 503
    code = "threat_awareness_unavailable"

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
        raise ThreatAwarenessError(f"snapshot is not available: {exc}") from exc
    if stat.st_size > MAX_BYTES:
        raise ThreatAwarenessError("snapshot is larger than the allowed size")
    try:
        with path.open(encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError) as exc:
        raise ThreatAwarenessError(f"snapshot cannot be read: {exc}") from exc
    if not isinstance(document, dict):
        raise ThreatAwarenessError("snapshot must be a JSON object")
    return document


def _require(document: dict[str, Any], key: str, kind: type) -> Any:
    value = document.get(key)
    if not isinstance(value, kind):
        raise ThreatAwarenessError(f"snapshot field {key!r} has the wrong type")
    return value


def _looks_like_address(text: str) -> bool:
    for token in _HOST_TOKEN.findall(text):
        if "." not in token and ":" not in token:
            continue
        try:
            ipaddress.ip_address(token)
        except ValueError:
            continue
        return True
    return False


def _check_no_addresses(value: Any, field: str = "snapshot") -> None:
    if isinstance(value, str):
        if _looks_like_address(value):
            raise ThreatAwarenessError(
                f"{field} contains an address-like value; snapshots must be aggregated"
            )
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _check_no_addresses(key, field)
            _check_no_addresses(item, field)
        return
    if isinstance(value, list):
        for item in value:
            _check_no_addresses(item, field)


def _count(entry: dict[str, Any], field: str) -> int:
    value = entry.get("count")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ThreatAwarenessError(f"{field} count must be a non-negative integer")
    return value


def _rows(
    document: dict[str, Any],
    key: str,
    minimum: int,
    *,
    require_code: bool,
) -> list[dict[str, Any]]:
    rows = document.get(key)
    if not isinstance(rows, list) or not rows:
        raise ThreatAwarenessError(f"snapshot field {key!r} must be a non-empty list")
    seen: set[str] = set()
    cleaned: list[dict[str, Any]] = []
    for entry in rows:
        if not isinstance(entry, dict):
            raise ThreatAwarenessError(f"{key} entries must be objects")
        label = entry.get("label")
        if not isinstance(label, str) or not label.strip():
            raise ThreatAwarenessError(f"{key} entries need a label")
        count = _count(entry, key)
        if count and count < minimum:
            raise ThreatAwarenessError(
                f"{key} bucket below the minimum size of {minimum} was not suppressed"
            )
        row: dict[str, Any] = {"label": label.strip(), "count": count}
        if require_code:
            code = entry.get("code")
            if not isinstance(code, str) or not _ISO2.match(code):
                raise ThreatAwarenessError(
                    f"{key} entries need an ISO 3166-1 alpha-2 code"
                )
            row["code"] = code
            if code in seen:
                raise ThreatAwarenessError(f"duplicate country code {code}")
            seen.add(code)
        else:
            identifier = entry.get("id")
            if not isinstance(identifier, str) or not identifier.strip():
                raise ThreatAwarenessError(f"{key} entries need an id")
            row["id"] = identifier.strip()
            if identifier in seen:
                raise ThreatAwarenessError(f"duplicate {key} id {identifier}")
            seen.add(identifier)
        cleaned.append(row)
    cleaned.sort(key=lambda item: (-item["count"], item["label"]))
    return cleaned


def _parse_time(value: Any) -> str:
    if not isinstance(value, str):
        raise ThreatAwarenessError("snapshot generated_at must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ThreatAwarenessError("snapshot generated_at is not ISO 8601") from exc
    if parsed.tzinfo is None:
        raise ThreatAwarenessError("snapshot generated_at needs a timezone")
    return value


def _validate(document: dict[str, Any]) -> dict[str, Any]:
    version = document.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ThreatAwarenessError(
            f"unsupported snapshot schema {version!r}; expected {SCHEMA_VERSION}"
        )
    mode = document.get("mode")
    if mode not in MODES:
        raise ThreatAwarenessError("snapshot mode must be 'sample' or 'snapshot'")

    generated_at = _parse_time(document.get("generated_at"))

    window = document.get("window_hours", 24)
    if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
        raise ThreatAwarenessError("snapshot window_hours must be a positive integer")

    source = _require(document, "source", dict)
    for key in ("name", "url", "attribution"):
        if not isinstance(source.get(key), str) or not source[key].strip():
            raise ThreatAwarenessError(f"snapshot source.{key} is required")

    method = _require(document, "method", dict)
    minimum = method.get("minimum_bucket_size", 25)
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
        raise ThreatAwarenessError("snapshot method.minimum_bucket_size is invalid")
    if method.get("individual_addresses") is not False:
        raise ThreatAwarenessError(
            "snapshot method.individual_addresses must be false"
        )

    totals = _require(document, "totals", dict)
    observed = totals.get("entries_observed")
    if isinstance(observed, bool) or not isinstance(observed, int) or observed < 0:
        raise ThreatAwarenessError("snapshot totals.entries_observed is invalid")
    reported = totals.get("entries_reported")
    if isinstance(reported, bool) or not isinstance(reported, int) or reported < 0:
        raise ThreatAwarenessError("snapshot totals.entries_reported is invalid")
    if reported > observed:
        raise ThreatAwarenessError(
            "snapshot reports more entries than were observed"
        )

    categories = _rows(document, "categories", minimum, require_code=False)
    countries = _rows(document, "countries", minimum, require_code=True)

    notes = document.get("notes", [])
    if not isinstance(notes, list) or not all(isinstance(n, str) for n in notes):
        raise ThreatAwarenessError("snapshot notes must be a list of strings")

    _check_no_addresses(document)

    def share(count: int) -> float:
        return round(count / reported, 4) if reported else 0.0

    for row in categories:
        row["share"] = share(row["count"])
    for row in countries:
        row["share"] = share(row["count"])

    reported_categories = sum(row["count"] for row in categories)
    reported_countries = sum(row["count"] for row in countries)
    coverage = round(reported / observed, 4) if observed else 0.0

    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "sample": mode == "sample",
        "generated_at": generated_at,
        "window_hours": window,
        "source": {
            "name": source["name"].strip(),
            "url": source["url"].strip(),
            "attribution": source["attribution"].strip(),
            "terms": str(source.get("terms") or "").strip(),
        },
        "method": {
            "aggregation": str(method.get("aggregation") or "country"),
            "minimum_bucket_size": minimum,
            "individual_addresses": False,
            "geoip": str(method.get("geoip") or "unknown"),
            "attack_paths": str(method.get("attack_paths") or "not included"),
        },
        "totals": {
            "entries_observed": observed,
            "entries_reported": reported,
            "coverage": coverage,
            "categories": len(categories),
            "countries": len(countries),
            "category_entries": reported_categories,
            "country_entries": reported_countries,
            "buckets_suppressed": int(totals.get("buckets_suppressed") or 0),
        },
        "categories": categories,
        "countries": countries,
        "notes": [note.strip() for note in notes if note.strip()],
    }


def snapshot(path: Path | None = None) -> dict[str, Any]:
    """Return the validated snapshot, cached until the file changes."""

    target = path or _snapshot_path()
    try:
        stat = target.stat()
        cache_key = f"{target}:{stat.st_mtime_ns}:{stat.st_size}"
    except OSError as exc:
        raise ThreatAwarenessError(
            "threat-awareness snapshot is not installed"
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
