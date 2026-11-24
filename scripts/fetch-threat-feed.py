#!/usr/bin/env python3
"""Build an aggregated threat-awareness snapshot from FireHOL netsets.

This runs on an operations host, never in the request path and never in a
browser. It downloads a fixed set of FireHOL netsets, counts entries per feed
and per country, applies a minimum bucket size, and writes a small JSON
document. It never writes an individual address, hostname, or attack path.

Usage::

    python scripts/fetch-threat-feed.py --dry-run
    python scripts/fetch-threat-feed.py --geoip-db /var/lib/GeoIP/GeoLite2-Country.mmdb

Country attribution uses a local MaxMind database when ``maxminddb`` is
installed and ``--geoip-db`` is given. Without it, every entry is counted under
``ZZ`` (unknown) and the snapshot says so. The panel still works; it just cannot
break down by country.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "platform" / "backend" / "app" / "data" / "threat-awareness.json"
BASE_URL = "https://iplists.firehol.org/files"

FEEDS = (
    ("firehol_level1", "Level 1 - high risk", "firehol_level1.netset"),
    ("firehol_level2", "Level 2 - moderate risk", "firehol_level2.netset"),
    ("firehol_level3", "Level 3 - low risk", "firehol_level3.netset"),
    ("abusers_30d", "30-day abusers", "firehol_abusers_30d.netset"),
    ("abusers_24h", "24-hour abusers", "firehol_abusers_1d.netset"),
    ("malicious_web", "Malicious web clients", "firehol_webclient.netset"),
    ("web_server", "Web server threats", "firehol_webserver.netset"),
    ("anonymous", "Anonymous proxies", "firehol_proxies.netset"),
)

ATTRIBUTION = (
    "Aggregated counts derived from the FireHOL iplists project. "
    "Individual addresses are not retained."
)
TERMS = (
    "FireHOL aggregates third-party feeds and each feed keeps its own terms. "
    "Confirm them before enabling a refresh job."
)
UNKNOWN_COUNTRY = ("ZZ", "Unknown or unresolved")
GEOIP_ATTRIBUTION = (
    "IP geolocation by DB-IP (https://db-ip.com), CC BY 4.0."
)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _fetch(url: str, timeout: float) -> list[str]:
    request = urllib.request.Request(
        url, headers={"User-Agent": "OpenCyberRange-threat-feed/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SystemExit(f"cannot fetch {url}: {exc}") from exc
    return raw.decode("utf-8", errors="replace").splitlines()


def _networks(lines: list[str], limit: int) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    networks = []
    for line in lines:
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        try:
            networks.append(ipaddress.ip_network(text, strict=False))
        except ValueError:
            continue
        if len(networks) >= limit:
            break
    return networks


class GeoLookup:
    """Country lookup backed by a local MaxMind database, when available."""

    def __init__(self, path: str | None) -> None:
        self.reader = None
        if not path:
            return
        try:
            import maxminddb  # type: ignore[import-not-found]
        except ImportError:
            raise SystemExit(
                "--geoip-db needs the 'maxminddb' package; "
                "install it on the operations host only"
            ) from None
        self.reader = maxminddb.open_database(path)

    @property
    def active(self) -> bool:
        return self.reader is not None

    def country(
        self, network: ipaddress.IPv4Network | ipaddress.IPv6Network
    ) -> tuple[str, str]:
        if self.reader is None:
            return UNKNOWN_COUNTRY
        address = str(network.network_address)
        try:
            record = self.reader.get(address) or {}
        except (OSError, TypeError, ValueError):  # pragma: no cover
            return UNKNOWN_COUNTRY
        country = record.get("country") or {}
        code = str(country.get("iso_code") or "").upper()
        names = country.get("names") or {}
        label = str(names.get("en") or code or "").strip()
        if len(code) != 2 or not code.isalpha() or code == "ZZ":
            return UNKNOWN_COUNTRY
        return code, label or code

    def close(self) -> None:
        if self.reader is not None:
            self.reader.close()


def _snapshot(
    feeds: list[dict], geo: GeoLookup, minimum: int, window_hours: int
) -> dict:
    category_totals: list[dict] = []
    country_counts: dict[str, dict] = {}
    observed = 0
    suppressed = 0

    for feed in feeds:
        category_totals.append(
            {
                "id": feed["id"],
                "label": feed["label"],
                "count": feed["count"],
            }
        )
        observed += feed["count"]
        for code, entry in feed["countries"].items():
            bucket = country_counts.setdefault(
                code,
                {"code": code, "label": entry["label"], "count": 0},
            )
            bucket["count"] += entry["count"]

    categories = [
        entry for entry in category_totals if entry["count"] >= minimum
    ]
    suppressed += len(category_totals) - len(categories)

    countries = [
        entry for entry in country_counts.values() if entry["count"] >= minimum
    ]
    suppressed += len(country_counts) - len(countries)

    categories.sort(key=lambda entry: (-entry["count"], entry["label"]))
    countries.sort(key=lambda entry: (-entry["count"], entry["label"]))
    reported = sum(entry["count"] for entry in categories)

    return {
        "schema_version": 1,
        "mode": "snapshot",
        "generated_at": _now(),
        "window_hours": window_hours,
        "source": {
            "name": "FireHOL threat intelligence feeds",
            "url": "https://iplists.firehol.org/",
            "attribution": (
                f"{ATTRIBUTION} {GEOIP_ATTRIBUTION}" if geo.active else ATTRIBUTION
            ),
            "terms": TERMS,
        },
        "method": {
            "aggregation": "country",
            "minimum_bucket_size": minimum,
            "individual_addresses": False,
            "geoip": "local-database" if geo.active else "none",
            "attack_paths": "not included",
        },
        "totals": {
            "entries_observed": observed,
            "entries_reported": reported,
            "categories": len(categories),
            "countries": len(countries),
            "buckets_suppressed": suppressed,
        },
        "categories": categories,
        "countries": countries,
        "notes": [
            (
                "Counts are aggregated per country. No individual address, "
                "hostname, or attack path is included."
            ),
            "An entry can appear in more than one feed, so counts overlap.",
            "Not live attack telemetry. This is a periodic feed snapshot.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--minimum-bucket-size", type=int, default=25)
    parser.add_argument("--window-hours", type=int, default=24)
    parser.add_argument("--max-entries-per-feed", type=int, default=250_000)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--geoip-db", default=None)
    parser.add_argument(
        "--require-geoip",
        action="store_true",
        help="Fail instead of writing a snapshot where every entry is unknown",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.minimum_bucket_size < 1:
        parser.error("--minimum-bucket-size must be at least 1")
    if args.window_hours < 1:
        parser.error("--window-hours must be at least 1")

    geo = GeoLookup(args.geoip_db)
    if args.require_geoip and not geo.active:
        raise SystemExit(
            "--require-geoip needs --geoip-db and the maxminddb package"
        )
    feeds = []
    try:
        for identifier, label, filename in FEEDS:
            url = f"{BASE_URL}/{filename}"
            networks = _networks(
                _fetch(url, args.timeout), args.max_entries_per_feed
            )
            countries: dict[str, dict] = {}
            for network in networks:
                code, name = geo.country(network)
                bucket = countries.setdefault(
                    code, {"label": name, "count": 0}
                )
                bucket["count"] += 1
            feeds.append(
                {
                    "id": identifier,
                    "label": label,
                    "count": len(networks),
                    "countries": countries,
                }
            )
    finally:
        geo.close()

    document = _snapshot(
        feeds, geo, args.minimum_bucket_size, args.window_hours
    )

    output = Path(args.output)
    if args.dry_run:
        print(json.dumps(document, indent=2))
        print(f"dry run: would write {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(
        dir=output.parent, prefix=".threat-awareness-", suffix=".json"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(document, handle, indent=2)
            handle.write("\n")
        os.replace(temp, output)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise
    print(
        f"wrote {output}: {document['totals']['entries_reported']} reported "
        f"entries across {document['totals']['countries']} countries"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
