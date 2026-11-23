#!/usr/bin/env python3
"""Discover live hosts with nmap and upsert them into NetBox IPAM.

This is the small, auditable lab option. The production option is NetBox
Discovery + Diode, which uses nmap for host discovery and NAPALM/SNMP for
device modeling.

Safety rules:
- only scan an explicit CIDR (default maximum /24 unless --allow-large)
- never run against a production flag
- dry-run is available and recommended first
- only creates IP addresses and, optionally, the covering prefix
- idempotent: an existing address is kept, not duplicated

Usage:
    NETBOX_URL=http://127.0.0.1:8083 NETBOX_TOKEN=... \
      python scripts/ecosystem_seed/discover_netbox.py --cidr <private-subnet> --dry-run

    # Replay a saved nmap -oX file without scanning
    python scripts/ecosystem_seed/discover_netbox.py --nmap-xml scan.xml --dry-run
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime

BASE = ""
TOKEN = ""


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


def find_one(path: str, query: str) -> dict | None:
    result = call("GET", f"{path}?{query}&limit=1")
    results = result.get("results", [])
    return results[0] if results else None


def ensure_tag(name: str, slug: str) -> int | None:
    existing = find_one("extras/tags", f"slug={urllib.parse.quote(slug)}")
    if existing:
        return existing["id"]
    created = call("POST", "extras/tags/", {
        "name": name,
        "slug": slug,
        "color": "607d8b",
        "description": "Created by the nmap discovery script",
    })
    return created.get("id")


def ensure_prefix(cidr: str, site_slug: str, tenant_slug: str) -> None:
    existing = find_one("ipam/prefixes", f"prefix={urllib.parse.quote(cidr)}")
    if existing:
        print(f"keep  prefix {cidr} -> {existing['id']}")
        return

    site = find_one("dcim/sites", f"slug={urllib.parse.quote(site_slug)}")
    tenant = find_one("tenancy/tenants", f"slug={urllib.parse.quote(tenant_slug)}")
    payload = {
        "prefix": cidr,
        "status": "active",
        "description": "Discovered by nmap",
    }
    if site:
        payload["site"] = site["id"]
    if tenant:
        payload["tenant"] = tenant["id"]

    created = call("POST", "ipam/prefixes/", payload)
    print(f"create prefix {cidr} -> {created['id']}")


def upsert_ip(address: str, tag_id: int | None, dry_run: bool) -> str:
    existing = find_one("ipam/ip-addresses", f"address={urllib.parse.quote(address + '/32')}")

    if existing:
        return "kept"

    if dry_run:
        print(f"would create ip {address}/32")
        return "created"

    payload = {
        "address": f"{address}/32",
        "status": "active",
        "description": f"Discovered by nmap on {datetime.now(UTC).date().isoformat()}",
    }
    if tag_id is not None:
        payload["tags"] = [tag_id]

    try:
        call("POST", "ipam/ip-addresses/", payload)
    except RuntimeError as error:
        # A concurrent run may have created the address between the lookup and
        # the insert. Treat the duplicate as kept rather than failing the batch.
        if "400" in str(error) and "already exists" in str(error).lower():
            return "kept"
        raise

    print(f"create ip {address}/32")
    return "created"


def hosts_from_xml(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    hosts: list[str] = []

    for host in root.findall(".//host"):
        status = host.find("status")
        if status is None or status.get("state") != "up":
            continue

        for address in host.findall("address"):
            if address.get("addrtype") in {"ipv4", "ipv6"}:
                hosts.append(address.get("addr", ""))

    return sorted({host for host in hosts if host})


def scan(cidr: str) -> str:
    command = [
        "nmap", "-sn", "-n", "--max-retries", "1", "--host-timeout", "10s",
        "-oX", "-", cidr,
    ]
    print("run   " + " ".join(command))
    completed = subprocess.run(command, capture_output=True, text=True, timeout=900)

    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "nmap failed")

    return completed.stdout


def main() -> int:
    global BASE, TOKEN

    if os.environ.get("OCR_ENV", "dev").lower() in {"production", "prod"}:
        print("REFUSING: discovery must not run against the production flag", file=sys.stderr)
        return 2

    parser = argparse.ArgumentParser()
    parser.add_argument("--cidr", help="IPv4/IPv6 CIDR to scan, e.g. <private-subnet>")
    parser.add_argument("--nmap-xml", help="Replay a saved nmap -oX file instead of scanning")
    parser.add_argument("--site", default="training-dc", help="NetBox site slug for the prefix")
    parser.add_argument("--tenant", default="training", help="NetBox tenant slug for the prefix")
    parser.add_argument("--tag", default="nmap-discovered", help="Tag applied to created IPs")
    parser.add_argument("--create-prefix", action="store_true", help="Create the CIDR prefix if missing")
    parser.add_argument("--allow-large", action="store_true", help="Allow prefixes larger than /24")
    parser.add_argument("--max-hosts", type=int, default=256)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.cidr and not args.nmap_xml:
        parser.error("--cidr or --nmap-xml is required")

    if args.cidr:
        network = ipaddress.ip_network(args.cidr, strict=False)
        if network.prefixlen < 24 and not args.allow_large:
            parser.error("refusing a prefix larger than /24 without --allow-large")
        cidr = str(network)
    else:
        cidr = ""

    BASE = os.environ.get("NETBOX_URL", "http://127.0.0.1:8083").rstrip("/")
    TOKEN = os.environ.get("NETBOX_TOKEN", "").strip()

    if not TOKEN:
        print("NETBOX_TOKEN is required", file=sys.stderr)
        return 2

    xml_text = open(args.nmap_xml, encoding="utf-8").read() if args.nmap_xml else scan(cidr)
    hosts = hosts_from_xml(xml_text)[: args.max_hosts]

    if not hosts:
        print(json.dumps({"schema": "opendiscovery.netbox-discovery/v1", "discovered": 0}))
        return 0

    tag_id = None if args.dry_run else ensure_tag("nmap-discovered", args.tag)

    if args.dry_run:
        print(f"would ensure tag {args.tag}")

    if args.create_prefix and cidr:
        if args.dry_run:
            print(f"would ensure prefix {cidr}")
        else:
            ensure_prefix(cidr, args.site, args.tenant)

    created = kept = 0
    for host in hosts:
        result = upsert_ip(host, tag_id, args.dry_run)
        created += result == "created"
        kept += result == "kept"

    print(json.dumps({
        "schema": "opendiscovery.netbox-discovery/v1",
        "cidr": cidr or None,
        "discovered": len(hosts),
        "created": created,
        "kept": kept,
        "dryRun": args.dry_run,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
