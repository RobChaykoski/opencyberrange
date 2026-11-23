"""
Cloudflare dynamic DNS for the platform hostnames.

The settings are stored in ``platform_settings`` and the token is encrypted like
any other secret setting. The updater reads the public IPv4 from Cloudflare's
trace endpoint and updates explicit, zone-scoped A records. It never publishes a
private address and never widens a record list beyond the configured zone.

A firewall's built-in DDNS client is still the better owner of the WAN address.
This service exists for single-host deployments where the platform is the
always-on machine behind the firewall. The ``deploy/cloudflare-ddns`` container
remains the portable option for a separate NPM host.
"""

from __future__ import annotations

import ipaddress
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import quote

import requests
from sqlalchemy.orm import Session

from app.services import settings_service

logger = logging.getLogger(__name__)

CLOUDFLARE_API = "https://api.cloudflare.com/client/v4"
TRACE_URL = "https://cloudflare.com/cdn-cgi/trace"
HTTP_TIMEOUT_SECONDS = 10
MIN_TTL_SECONDS = 60
MAX_TTL_SECONDS = 86400

STATUS_KEYS = (
    "ddns_last_checked_at",
    "ddns_last_ip",
    "ddns_last_result",
    "ddns_last_error",
)


class DDNSError(Exception):
    """A failure that is safe to show to an administrator."""


def _bool(value: Optional[str], default: bool = False) -> bool:
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _int(value: Optional[str], default: int) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def config(db: Session) -> dict:
    """Read the current DDNS configuration. Secrets are decrypted here only."""
    return {
        "enabled": _bool(settings_service.get_setting_fresh(db, "ddns_enabled", "false")),
        "token": (settings_service.get_setting_fresh(db, "ddns_api_token", "") or "").strip(),
        "zone": (settings_service.get_setting_fresh(db, "ddns_zone", "") or "").strip().lower().strip("."),
        "domains": (settings_service.get_setting_fresh(db, "ddns_domains", "") or "").strip(),
        "proxied": _bool(settings_service.get_setting_fresh(db, "ddns_proxied", "false")),
        "ttl": _int(settings_service.get_setting_fresh(db, "ddns_ttl", "120"), 120),
        "interval_minutes": max(
            1,
            _int(settings_service.get_setting_fresh(db, "ddns_interval_minutes", "5"), 5),
        ),
    }


def domains(value: str) -> list[str]:
    """Parse and validate the explicit record list."""
    items = [item.strip().lower().strip(".") for item in re.split(r"[\s,]+", value or "")]
    result: list[str] = []

    for item in items:
        if not item or item in result:
            continue
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+", item):
            raise DDNSError(f"Invalid DNS name: {item}")
        result.append(item)

    if not result:
        raise DDNSError("Set at least one record name.")

    return result


def _require_config(cfg: dict) -> tuple[str, str, list[str]]:
    if not cfg["token"]:
        raise DDNSError("Set a Cloudflare API token first.")
    if not cfg["zone"]:
        raise DDNSError("Set the Cloudflare zone, for example example.edu.")
    names = domains(cfg["domains"])

    for name in names:
        if name != cfg["zone"] and not name.endswith("." + cfg["zone"]):
            raise DDNSError(
                f"{name} is outside the configured zone {cfg['zone']}. "
                "Add the zone explicitly instead of updating another domain."
            )

    return cfg["token"], cfg["zone"], names


def _request(method: str, path: str, token: str, **kwargs) -> dict:
    url = f"{CLOUDFLARE_API}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            timeout=HTTP_TIMEOUT_SECONDS,
            **kwargs,
        )
    except requests.RequestException as exc:
        raise DDNSError(f"Cloudflare request failed: {type(exc).__name__}") from exc

    try:
        payload = response.json()
    except ValueError:
        payload = {}

    if response.status_code >= 400 or not payload.get("success", False):
        messages = payload.get("errors") or []
        detail = "; ".join(
            str(item.get("message", "unknown error")) for item in messages if isinstance(item, dict)
        )
        raise DDNSError(
            f"Cloudflare returned HTTP {response.status_code}"
            + (f": {detail}" if detail else ".")
        )

    return payload


def public_ipv4() -> str:
    """Read the public IPv4 address and refuse to publish a private one."""
    try:
        response = requests.get(TRACE_URL, timeout=HTTP_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise DDNSError(f"Could not reach the address service: {type(exc).__name__}") from exc

    if response.status_code >= 400:
        raise DDNSError(f"Address service returned HTTP {response.status_code}.")

    match = re.search(r"^ip=(.+)$", response.text, re.MULTILINE)
    if not match:
        raise DDNSError("Address service did not return an IPv4 address.")

    value = match.group(1).strip()
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise DDNSError("Address service returned an invalid address.") from exc

    if address.version != 4 or address.is_private or address.is_loopback or address.is_link_local:
        raise DDNSError("Address service returned a non-public IPv4 address.")

    return str(address)


def _zone_id(token: str, zone: str) -> str:
    payload = _request("GET", f"/zones?name={quote(zone)}&status=active", token)
    zones = payload.get("result") or []

    if not zones:
        raise DDNSError(f"Cloudflare has no active zone named {zone}.")

    return str(zones[0]["id"])


def _records(token: str, zone_id: str, name: str) -> list[dict]:
    payload = _request(
        "GET",
        f"/zones/{zone_id}/dns_records?type=A&name={quote(name)}",
        token,
    )
    return [item for item in payload.get("result") or [] if isinstance(item, dict)]


def status(db: Session) -> dict:
    cfg = config(db)
    return {
        "enabled": cfg["enabled"],
        "zone": cfg["zone"],
        "domains": cfg["domains"],
        "proxied": cfg["proxied"],
        "ttl": cfg["ttl"],
        "interval_minutes": cfg["interval_minutes"],
        "last_checked_at": settings_service.get_setting_fresh(db, "ddns_last_checked_at", ""),
        "last_ip": settings_service.get_setting_fresh(db, "ddns_last_ip", ""),
        "last_result": settings_service.get_setting_fresh(db, "ddns_last_result", ""),
        "last_error": settings_service.get_setting_fresh(db, "ddns_last_error", ""),
    }


def is_due(db: Session, now: Optional[datetime] = None) -> bool:
    cfg = config(db)
    if not cfg["enabled"]:
        return False

    last_value = settings_service.get_setting_fresh(db, "ddns_last_checked_at", "") or ""
    if not last_value:
        return True

    try:
        last = datetime.fromisoformat(last_value.replace("Z", "+00:00"))
    except ValueError:
        return True

    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)

    return (now or datetime.now(timezone.utc)) >= last + timedelta(minutes=cfg["interval_minutes"])


def sync(db: Session, *, dry_run: bool = False) -> dict:
    """Check the public address and reconcile the configured A records.

    ``dry_run`` validates the token, zone, and current records without writing
    DNS. It is the "test" path in the settings panel.
    """
    cfg = config(db)
    token, zone, names = _require_config(cfg)
    address = public_ipv4()
    zone_id = _zone_id(token, zone)
    ttl = max(MIN_TTL_SECONDS, min(MAX_TTL_SECONDS, cfg["ttl"]))

    created = 0
    updated = 0
    current = 0
    actions: list[str] = []
    errors: list[str] = []

    for name in names:
        try:
            records = _records(token, zone_id, name)
            body = {
                "type": "A",
                "name": name,
                "content": address,
                "ttl": ttl,
                "proxied": cfg["proxied"],
            }

            if not records:
                actions.append(f"create {name} -> {address}")
                if not dry_run:
                    _request("POST", f"/zones/{zone_id}/dns_records", token, json=body)
                    created += 1
                continue

            if len(records) > 1:
                raise DDNSError(
                    f"{name} has {len(records)} A records. The updater manages one record; "
                    "remove the extra records or update them manually."
                )

            record = records[0]
            same_address = record.get("content") == address
            same_proxied = bool(record.get("proxied")) == cfg["proxied"]
            same_ttl = cfg["proxied"] or int(record.get("ttl") or 0) == ttl

            if same_address and same_proxied and same_ttl:
                actions.append(f"current {name} = {address}")
                current += 1
                continue

            actions.append(f"update {name} -> {address}")
            if not dry_run:
                _request(
                    "PATCH",
                    f"/zones/{zone_id}/dns_records/{record['id']}",
                    token,
                    json={
                        "content": address,
                        "ttl": ttl,
                        "proxied": cfg["proxied"],
                    },
                )
                updated += 1
        except DDNSError as exc:
            errors.append(f"{name}: {exc}")

    result = {
        "ok": not errors,
        "dry_run": dry_run,
        "ip": address,
        "zone": zone,
        "created": created,
        "updated": updated,
        "current": current,
        "actions": actions,
        "errors": errors,
    }

    summary = (
        f"{created} created, {updated} updated, {current} current"
        if not errors
        else f"{len(errors)} record(s) failed"
    )

    if not dry_run:
        _write_status(db, address, summary, "; ".join(errors))

    if errors:
        logger.warning("Cloudflare DDNS completed with errors: %s", "; ".join(errors))
    else:
        logger.info("Cloudflare DDNS: %s at %s", summary, address)

    return result


def _write_status(db: Session, address: str, result: str, error: str) -> None:
    settings_service.bulk_update_settings(
        db,
        {
            "ddns_last_checked_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "ddns_last_ip": address,
            "ddns_last_result": result,
            "ddns_last_error": error,
        },
    )


def record_failure(db: Session, message: str) -> None:
    """Record a configuration or transport failure without erasing the last IP."""
    settings_service.bulk_update_settings(
        db,
        {
            "ddns_last_checked_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "ddns_last_result": "check failed",
            "ddns_last_error": message,
        },
    )
