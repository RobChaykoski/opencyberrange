"""Read-only HA status snapshot from the host collector.

The witness/collector writes one JSON file on each app host. This module
validates and sanitises it, adds the local role marker, and applies the
staleness and verdict rules. It never probes a peer, never writes, and never
returns a host path, address, or credential.
"""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_STATUS_PATH = Path("/var/lib/ocr-ha/status.json")
DEFAULT_ROLE_PATH = Path("/etc/ocr-ha/role")
STATUS_PATH_ENV = "OCR_HA_STATUS_PATH"
ROLE_PATH_ENV = "OCR_HA_ROLE_PATH"

STALE_AFTER_SECONDS = 90
WITNESS_SILENT_SECONDS = 300
LAG_WARNING_BYTES = 64 * 1024 * 1024
CACHE_TTL_SECONDS = 15.0

_CACHE_LOCK = threading.Lock()
_CACHE: dict[str, Any] = {"key": None, "expires": 0.0, "value": None}


def _status_path() -> Path:
    return Path(os.environ.get(STATUS_PATH_ENV) or DEFAULT_STATUS_PATH)


def _role_path() -> Path:
    return Path(os.environ.get(ROLE_PATH_ENV) or DEFAULT_ROLE_PATH)


def _read_role() -> str:
    try:
        role = _role_path().read_text(encoding="utf-8").strip().lower()
    except OSError:
        return "unknown"
    return role if role in {"primary", "standby"} else "unknown"


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


def _age_seconds(value: datetime | None, now: datetime) -> int | None:
    if value is None:
        return None
    return max(0, int((now - value).total_seconds()))


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _count(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _replication(document: dict[str, Any]) -> dict[str, Any]:
    raw = _mapping(document.get("replication"))
    return {
        "state": _text(raw.get("state")),
        "lag_bytes": _count(raw.get("lag_bytes")),
        "last_replay": _text(raw.get("last_replay")),
    }


def _redis(document: dict[str, Any]) -> dict[str, Any]:
    raw = _mapping(document.get("redis"))
    return {
        "master": _text(raw.get("master")),
        "sentinels": _text(raw.get("sentinels")),
    }


def _witness(document: dict[str, Any]) -> dict[str, Any]:
    raw = _mapping(document.get("witness"))
    return {
        "last_contact": _text(raw.get("last_contact")),
        "prod": _text(raw.get("prod")),
        "dev": _text(raw.get("dev")),
    }


def _last_failover(document: dict[str, Any]) -> dict[str, Any] | None:
    raw = document.get("last_failover")
    if not isinstance(raw, dict):
        return None
    return {
        "at": _text(raw.get("at")),
        "from": _text(raw.get("from")),
        "to": _text(raw.get("to")),
        "verified": raw.get("verified") if isinstance(raw.get("verified"), bool) else None,
    }


def _unknown(role: str, detail: str, *, available: bool) -> dict[str, Any]:
    return {
        "available": available,
        "checked_at": None,
        "age_seconds": None,
        "stale": True,
        "role": role,
        "preferred": None,
        "replication": None,
        "redis": None,
        "witness": None,
        "last_failover": None,
        "verdict": "unknown",
        "detail": detail,
    }


def _verdict(
    *,
    replication: dict[str, Any],
    witness: dict[str, Any],
    last_failover: dict[str, Any] | None,
    stale: bool,
    now: datetime,
) -> str:
    if stale:
        return "unknown"

    state = replication.get("state")
    if state and state not in {"streaming", "primary"}:
        return "error"

    lag = replication.get("lag_bytes")
    if isinstance(lag, int) and lag > LAG_WARNING_BYTES:
        return "warning"

    last_contact = _parse_time(witness.get("last_contact"))
    contact_age = _age_seconds(last_contact, now)
    if contact_age is not None and contact_age > WITNESS_SILENT_SECONDS:
        return "warning"
    if any(witness.get(node) not in (None, "up") for node in ("prod", "dev")):
        return "warning"

    if last_failover and last_failover.get("verified") is False:
        return "warning"

    return "ok"


def _build(document: dict[str, Any], role: str) -> dict[str, Any]:
    now = datetime.now(UTC)
    checked_at = _parse_time(document.get("checked_at"))
    age = _age_seconds(checked_at, now)
    stale = age is None or age > STALE_AFTER_SECONDS

    replication = _replication(document)
    redis = _redis(document)
    witness = _witness(document)
    last_failover = _last_failover(document)
    preferred = _text(document.get("preferred"))
    if preferred not in {"prod", "dev"}:
        preferred = None

    verdict = _verdict(
        replication=replication,
        witness=witness,
        last_failover=last_failover,
        stale=stale,
        now=now,
    )

    if stale:
        detail = (
            "HA status is stale; the last snapshot is too old to trust."
            if checked_at is not None
            else "The HA status snapshot has no valid timestamp."
        )
    elif verdict == "error":
        detail = "The standby is not receiving WAL; failover would lose data."
    elif verdict == "warning":
        detail = "HA needs attention; review replication and witness state."
    else:
        detail = "HA status is current."

    return {
        "available": True,
        "checked_at": checked_at.isoformat().replace("+00:00", "Z")
        if checked_at
        else None,
        "age_seconds": age,
        "stale": stale,
        "role": role,
        "preferred": preferred,
        "replication": replication,
        "redis": redis,
        "witness": witness,
        "last_failover": last_failover,
        "verdict": verdict,
        "detail": detail,
    }


def snapshot() -> dict[str, Any]:
    """Return the sanitised HA snapshot, cached for 15 seconds.

    A missing file means HA is not configured on this host; the admin card is
    hidden. A malformed file is reported as ``unknown`` rather than a 500.
    """

    target = _status_path()
    role = _read_role()
    try:
        stat = target.stat()
        key = (str(target), stat.st_mtime_ns, stat.st_size)
    except OSError:
        key = (str(target), "missing")
        with _CACHE_LOCK:
            if _CACHE["key"] == key and _CACHE["expires"] > time.monotonic():
                return _CACHE["value"]
        value = _unknown(role, "HA is not configured on this host.", available=False)
        with _CACHE_LOCK:
            _CACHE.update(
                {
                    "key": key,
                    "expires": time.monotonic() + CACHE_TTL_SECONDS,
                    "value": value,
                }
            )
        return value

    now = time.monotonic()
    with _CACHE_LOCK:
        if _CACHE["key"] == key and _CACHE["expires"] > now:
            return _CACHE["value"]

    try:
        document = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        value = _unknown(role, "The HA status snapshot is unreadable.", available=True)
    else:
        if isinstance(document, dict):
            value = _build(document, role)
        else:
            value = _unknown(
                role, "The HA status snapshot is not a JSON object.", available=True
            )

    with _CACHE_LOCK:
        _CACHE.update({"key": key, "expires": now + CACHE_TTL_SECONDS, "value": value})
    return value


def attention_items() -> list[dict[str, str]]:
    """Entries for the admin needs-attention summary, empty without HA."""

    snap = snapshot()
    if not snap.get("available"):
        return []

    if snap.get("stale"):
        age = snap.get("age_seconds")
        detail = (
            f"HA status is {age} seconds old; it is too stale to trust."
            if isinstance(age, int)
            else "The HA status snapshot has no usable timestamp."
        )
        return [{"name": "HA status", "status": "warning", "detail": detail}]

    items: list[dict[str, str]] = []
    replication = snap.get("replication") or {}
    state = replication.get("state")
    lag = replication.get("lag_bytes")
    if state and state not in {"streaming", "primary"}:
        items.append(
            {
                "name": "HA replication",
                "status": "error",
                "detail": "The standby is not receiving WAL; failover would lose data.",
            }
        )
    elif isinstance(lag, int) and lag > LAG_WARNING_BYTES:
        items.append(
            {
                "name": "HA replication",
                "status": "warning",
                "detail": f"Replication lag is {lag // (1024 * 1024)} MB; do not promote yet.",
            }
        )

    witness = snap.get("witness") or {}
    last_contact = _parse_time(witness.get("last_contact"))
    contact_age = _age_seconds(last_contact, datetime.now(UTC))
    if contact_age is not None and contact_age > WITNESS_SILENT_SECONDS:
        items.append(
            {
                "name": "HA witness",
                "status": "warning",
                "detail": "No witness contact for five minutes; HA decisions need a third opinion.",
            }
        )
    elif any(witness.get(node) not in (None, "up") for node in ("prod", "dev")):
        items.append(
            {
                "name": "HA witness",
                "status": "warning",
                "detail": "The witness reports a node down; treat the peer state carefully.",
            }
        )

    return items


def reset_cache() -> None:
    """Clear the module cache (tests and an explicit refresh)."""

    with _CACHE_LOCK:
        _CACHE.update({"key": None, "expires": 0.0, "value": None})
