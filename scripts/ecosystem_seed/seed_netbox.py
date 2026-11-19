#!/usr/bin/env python3
"""Seed a fake NetBox asset inventory for OpenCyberRange training capstones.

Run against the dev-only training stack:

    NETBOX_URL=http://127.0.0.1:8083 \
    NETBOX_TOKEN=... \
    python scripts/ecosystem_seed/seed_netbox.py

The script is idempotent: it looks records up by slug or name before creating
them. Every site, device, and prefix is synthetic training data.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("NETBOX_URL", "http://127.0.0.1:8083").rstrip("/")
TOKEN = os.environ.get("NETBOX_TOKEN", "").strip()

if not TOKEN:
    print("NETBOX_TOKEN is required", file=sys.stderr)
    sys.exit(2)


def call(method: str, path: str, payload: dict | None = None) -> dict:
    url = f"{BASE}/api/{path.lstrip('/')}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", f"Token {TOKEN}")
    request.add_header("Accept", "application/json")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        raise RuntimeError(f"{method} {path} -> {error.code}: {body[:400]}") from error


def find(path: str, key: str, value: str) -> dict | None:
    result = call("GET", f"{path}?{key}={urllib.parse.quote(value)}&limit=1")
    results = result.get("results", [])
    return results[0] if results else None


def ensure(path: str, key: str, value: str, payload: dict) -> dict:
    existing = find(path, key, value)
    if existing:
        print(f"keep  {path} {value} -> {existing['id']}")
        return existing
    created = call("POST", path + "/", payload)
    print(f"create {path} {value} -> {created['id']}")
    return created


tenant = ensure("tenancy/tenants", "slug", "training", {
    "name": "Training (synthetic)",
    "slug": "training",
    "description": "Synthetic tenant. Not a real organization.",
})

site = ensure("dcim/sites", "slug", "training-dc", {
    "name": "Training Data Centre",
    "slug": "training-dc",
    "status": "active",
    "tenant": tenant["id"],
    "description": "Synthetic site for capstone asset exercises.",
})

manufacturers = [
    ("Cisco", "cisco"),
    ("Juniper", "juniper"),
    ("Dell", "dell"),
    ("Opengear", "opengear"),
]
manufacturer_ids = {}
for name, slug in manufacturers:
    manufacturer_ids[slug] = ensure("dcim/manufacturers", "slug", slug, {"name": name, "slug": slug})["id"]

device_types = [
    ("Catalyst 9300", "catalyst-9300", "cisco"),
    ("EX4300", "ex4300", "juniper"),
    ("PowerEdge R660", "poweredge-r660", "dell"),
    ("ACM7004", "acm7004", "opengear"),
]
type_ids = {}
for model, slug, manufacturer in device_types:
    type_ids[slug] = ensure("dcim/device-types", "slug", slug, {
        "manufacturer": manufacturer_ids[manufacturer],
        "model": model,
        "slug": slug,
    })["id"]

roles = [
    ("Core Switch", "core-switch", "2196f3"),
    ("Edge Router", "edge-router", "3f51b5"),
    ("Hypervisor", "hypervisor", "4caf50"),
    ("Console Server", "console-server", "ff9800"),
]
role_ids = {}
for name, slug, color in roles:
    role_ids[slug] = ensure("dcim/device-roles", "slug", slug, {
        "name": name,
        "slug": slug,
        "color": color,
        "vm_role": False,
    })["id"]

devices = [
    ("core-sw-01", "catalyst-9300", "core-switch"),
    ("edge-rtr-01", "ex4300", "edge-router"),
    ("hv-01", "poweredge-r660", "hypervisor"),
    ("hv-02", "poweredge-r660", "hypervisor"),
    ("console-01", "acm7004", "console-server"),
]
for name, type_slug, role_slug in devices:
    ensure("dcim/devices", "name", name, {
        "name": name,
        "device_type": type_ids[type_slug],
        "role": role_ids[role_slug],
        "site": site["id"],
        "tenant": tenant["id"],
        "status": "active",
    })

for prefix, description in [
    ("10.10.0.0/16", "Training core network"),
    ("10.20.0.0/16", "Training lab network"),
    ("172.20.0.0/16", "Training endpoint network"),
]:
    ensure("ipam/prefixes", "prefix", prefix, {
        "prefix": prefix,
        "site": site["id"],
        "tenant": tenant["id"],
        "status": "active",
        "description": description,
    })

print("Seeded NetBox training inventory.")
