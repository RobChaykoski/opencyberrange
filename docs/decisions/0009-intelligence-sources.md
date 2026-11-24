# ADR 0009: External threat-intelligence sources

Status: **accepted**
Date: 24 November 2026

## Context

Three public sources were proposed for the Threat Awareness surface:

1. `Cybersight-Security/Global-Threat-Map` - an interactive map of FireHOL
   address feeds.
2. `RansomLook` (`ransomlook.io`) - a ransomware group, post, and leak tracker.
3. `Violations Watch` (`violationswatch.org`) - an OSINT log of alleged
   international humanitarian and human-rights law violations.

They have different licences, data classes, and risk profiles. A single
"add a feed" habit would put the platform's licence, privacy, and safeguarding
rules at risk.

## Decision

### 1. Global Threat Map: rejected

GPL-3.0 code cannot be combined with the PolyForm Noncommercial platform
licence. The project also renders individual IP addresses and simulated attack
paths, and calls a third-party geolocation API from the browser. See ADR 0008.

### 2. RansomLook: aggregate data only

RansomLook's **content** is CC BY 4.0; its **code** is AGPL-3.0. The platform
therefore uses the public API as a data source and never vendors the code.

Only two endpoints are allowed:

- `/api/stats` - aggregate totals (groups, posts, markets).
- `/api/hot` - seven-day totals and per-group post counts.

The snapshot contains group names and counts. It must never contain:

- victim organisation names or post titles;
- post links, onion addresses, or magnet links;
- cryptocurrency addresses or transactions;
- torrent peer IPs or ASNs;
- ransom-note text or screenshots.

`/api/recent` is explicitly excluded because its `post_title` is the victim
name. The fetch script aggregates from the allow-listed endpoints only, and the
service builds its response from known fields, so an unexpected snapshot field
cannot reach the UI.

Attribution: "Aggregated counts derived from RansomLook (ransomlook.io), CC BY
4.0." and a link to the source.

### 3. Violations Watch: rejected

Violations Watch is human-rights OSINT, not cyber telemetry. Integrating it
into a cyber range would:

- place unverified allegations against named state and non-state actors inside
  a product that learners may read as endorsed findings;
- carry defamation and political-risk exposure the institution has not
  accepted;
- introduce incidents involving children into a technical training surface,
  which is a safeguarding concern even though victim names are withheld;
- mix two unrelated data-governance regimes.

It is not ingested, embedded, or linked from the product UI. An instructor may
reference it in an ethics or OSINT discussion outside the platform, with its own
"unverified leads" caveat.

## Consequences

- The Threat Awareness panel gains a ransomware section sourced from aggregate
  RansomLook endpoints, with no victim data.
- The source register lives in `THIRD_PARTY_NOTICES.md` and this ADR.
- Any new source needs: licence check, data classification, an explicit
  allow-list of fields, aggregation rules, and an owner before code is written.
- The snapshot remains offline and signed, so an isolated range works without
  third-party calls.
