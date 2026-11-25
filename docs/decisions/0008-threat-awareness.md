# ADR 0008: Threat awareness data and the Global Threat Map

Status: **accepted**
Date: 24 November 2026

## Context

Instructors asked for a global threat-map view: a visual that shows where
hostile infrastructure is concentrated and why country-level threat intelligence
matters. A third-party project, `Cybersight-Security/Global-Threat-Map`, was
proposed as a drop-in.

It is technically attractive (single-page D3 map, FireHOL feeds) but it cannot
be integrated into this platform:

1. **Licence.** The project is GPL-3.0. OpenCyberRange is distributed under the
   PolyForm Noncommercial License 1.0.0. Vendoring the code, or serving it as
   part of the product, would make the combined work GPL-3.0 and contradict the
   platform licence.
2. **Privacy and accuracy.** It renders individual real IP addresses and calls
   `ip-api.com` from the learner's browser. The free endpoint is HTTP-only,
   rate-limited, and not licensed for commercial use. Individual IP attribution
   is frequently wrong (shared hosting, CDNs, Tor exits, stale feed entries) and
   publishing it in a teaching product is a defamation and data-protection risk.
3. **Misrepresentation.** The animated attack paths are simulated. In an
   educational product, simulated telemetry shown without a hard boundary reads
   as observed attacks.
4. **Operational fragility.** A cron-driven fetcher rewrites a JSON snapshot with
   no schema, no validation, no aggregation, and no offline path.

## Geolocation

Country attribution uses a **local MaxMind-format database**, never a lookup API
in the request path and never a browser call. DB-IP Lite (CC BY 4.0, no account)
is the default recommendation; a licensed MaxMind GeoLite2 database works with
the same flag. HackerTarget and similar services are limited to ad-hoc spot
checks (50 lookups a day on the free tier) and are not used for bulk refresh.

The snapshot records the DB-IP attribution when it is used. Without a database,
entries are counted as unknown and the panel says so.

## Decision

Do not vendor, embed, or iframe the Global Threat Map. Do not copy its assets.

Build a first-party **Threat Awareness** panel instead, with these rules:

- **Server-side or offline ingest only.** `scripts/fetch-threat-feed.py` runs on
  an operations host, never in the browser and never in the request path.
- **Aggregate, do not publish.** Only country-level and category-level counts
  are stored. No individual address, hostname, or attack path enters the
  snapshot, the API, or the UI.
- **Suppress small buckets.** The ingest enforces a minimum bucket size
  (default 25) so a country or category cannot be inferred down to a handful of
  hosts.
- **No runtime egress.** The platform reads a signed snapshot file, so the panel
  works on an isolated range and needs no third-party call.
- **Label honestly.** The UI states the snapshot time and whether the data is a
  sample or a live refresh. It never claims to show live attacks.
- **Keep the licence clean.** First-party code only; feed attribution lives in
  `THIRD_PARTY_NOTICES.md`.

An outbound hyperlink to the public Global Threat Map is permitted, because a
plain link is not a derivative work. It is not enabled by default.

## Consequences

- The panel ships with a labelled **sample** snapshot; a real refresh is an
  explicit operations action.
- Country attribution depends on a local GeoIP database. Without one, the ingest
  reports unknown-country entries rather than guessing.
- Feed terms remain the operator's responsibility. FireHOL aggregates upstream
  lists with their own conditions; the ingest records the attribution it used.
- The panel maps to `TH-010 Threat Intelligence Correlation` and `SOC-004
  Threat Intelligence Usage` for competency evidence, but it is awareness
  material, not a lab and not learner evidence on its own.

## Implementation note (24 November 2026)

The panel is now a first-party bubble map. It uses Natural Earth 110m land and
country centroids (public domain) and the same aggregated snapshot. It filters
by region and bucket size, lists hotspots, and offers a local three-question
challenge. It deliberately does **not** animate attack paths, simulate traffic,
or expose an address, host, learner, lab, prompt, packet, or flow. See
`docs/THREAT-AWARENESS-OPERATIONS.md` for the UI contract and tests.
