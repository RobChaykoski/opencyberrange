# Threat-awareness operations

Two snapshots feed the panel:

| Section | Source | Snapshot file |
|---|---|---|
| Hostile infrastructure | FireHOL iplists plus a reviewed set of DShield, Blocklist.de, abuse.ch Feodo Tracker, OffSeq Mirage, and IPsum feeds, with a local GeoIP database | `platform/backend/app/data/threat-awareness.json` |
| Ransomware activity | RansomLook aggregate endpoints | `platform/backend/app/data/ransomware-activity.json` |

Both are offline files baked into the backend image. A refresh is a normal
release: regenerate the file, verify it, commit it, refresh the supply-chain
lock, sign, and deploy. The panel shows the snapshot timestamp; there is no
runtime egress.

The candidate feeds come from the
[threat-intelligence-feeds catalog](https://github.com/kraloveckey/threat-intelligence-feeds)
(MIT metadata; every upstream keeps its own terms). Only the reviewed allowlist
below is fetched.

## FireHOL and GeoIP

The fetch script only writes aggregated country and feed counts. It never
retains an address. Country attribution needs a local MaxMind-format database.

### DB-IP Lite (recommended)

DB-IP Lite is free under **CC BY 4.0** and needs no account:

```bash
curl -sL -o /tmp/dbip-country-lite.mmdb.gz \
  https://download.db-ip.com/free/dbip-country-lite-2026-11.mmdb.gz
gunzip -f /tmp/dbip-country-lite.mmdb.gz
```

Then:

```bash
python scripts/fetch-threat-feed.py \
  --geoip-db /tmp/dbip-country-lite.mmdb \
  --minimum-bucket-size 25 --require-geoip
```

Attribution is written into the snapshot: "IP geolocation by DB-IP
(https://db-ip.com), CC BY 4.0."

### MaxMind GeoLite2

The same command works with a GeoLite2-Country `.mmdb` obtained under a MaxMind
account and licence. Keep the MaxMind attribution with any copy.

### Mirrors and consensus builds

- **WP Statistics DB-IP mirror** (`wp-statistics/DbIP-City-lite`, served through
  jsDelivr): the same DB-IP City Lite data under CC BY 4.0, with no account.
  Acceptable as a fallback when `db-ip.com` is unavailable; keep the DB-IP
  attribution. Prefer the upstream download for provenance.
- **GeoForge** (`ipanalytics/GeoForge`): not adopted. It is a source-available
  Go builder that merges DB-IP Lite, GeoLite2, IP2Location LITE, Sypex Geo,
  operator geofeeds, RIR statistics, and GeoNames into a consensus MMDB. It is
  heavier than a country-only refresh needs, and the licence plus
  `THIRD_PARTY_DATA.md` put conditions on redistributing derived outputs.
  Revisit only if country accuracy becomes a measured problem and those terms
  are cleared.
- **ipgeolocation.io**: a keyed API with rate-limited tiers. Suitable for spot
  checks or a future paid accuracy tier, not for refreshing hundreds of
  thousands of feed entries.

### HackerTarget and other lookup APIs

`https://hackertarget.com/geoip-ip-location-lookup/` is an ad-hoc lookup
service: the free tier is limited to **50 lookups a day** across its IP tools.
Do not use it for a feed refresh; a single FireHOL run has hundreds of
thousands of entries. It is useful for spot-checking one address while
investigating a country bucket.

### A snapshot without GeoIP

Without `--geoip-db`, every entry is counted as `ZZ` (unknown) and the panel
says so. `--require-geoip` turns that into an error instead of writing a
low-value snapshot.

## Curated additional feeds

The builder also reads these reviewed daily or periodic lists. Keep the
allowlist small: the map is awareness material, and every extra feed adds
overlap and licensing review.

| Feed | List | Cadence | Terms |
|---|---|---|---|
| DShield / SANS ISC | FireWALL-E `dshield_30d.netset` | 10 minutes upstream | Public blocklist; attribute DShield/SANS ISC and confirm current terms |
| Blocklist.de | `lists.blocklist.de/lists/all.txt` | 15 minutes upstream | Public fail2ban reports; attribute Blocklist.de and confirm current terms |
| abuse.ch Feodo Tracker | `ipblocklist_aggressive.txt` | 30 minutes upstream | Public C2 blocklist; attribute abuse.ch and confirm current terms |
| OffSeq Mirage | `feeds.offseq.com/mirage-feed/latest/ipv4-7d.txt` | Daily | **CC BY 4.0**; credit "OffSeq Mirage" with a link |
| IPsum | `stamparm/ipsum` level 3 | Daily | **The Unlicense** (public domain) |

The FireWALL-E copy of DShield is normalised to a netset. The other lists are
one entry per line; IPsum appends an occurrence count, so the ingest reads the
first token. A feed returning fewer than `--minimum-bucket-size` entries can
still contribute to country totals but is suppressed from the category list,
which is why DShield uses the 30-day list (54 subnets) rather than the 19-subnet
three-day list.

See [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) for attribution and
the licence note for every source.

## RansomLook

```bash
python scripts/fetch-ransomware-feed.py --max-groups 15
```

Only `/api/stats` and `/api/hot` are read. Victim names, post links, crypto
addresses, and peer addresses are excluded. Attribution: "Aggregated counts
derived from RansomLook (ransomlook.io), CC BY 4.0."

## Threat map UI

The page at `/threat-awareness` (also `/threat-map`) is a first-party bubble
map. It is the primary way a learner explores the snapshot:

- **Markers** are country centroids from Natural Earth 110m data. Marker size
  shows reported entries; the top three have a dashed ring.
- **Filters** limit the view by region and minimum bucket size. The hotspot list
  shows the same rows as a keyboard-friendly alternative to the map.
- **Selection** opens a detail panel with the count, share, rank, and the
  country-attribution caveat. It never shows an address, host, attack path,
  victim, or post link.
- **OpenStreetMap link.** The selected-country panel offers a plain outbound
  link to `openstreetmap.org` at the country centroid. The platform does not
  fetch tiles or call OSM at runtime; opening the link is a deliberate learner
  action and contacts that site.
- **Snapshot, not live.** The page shows the snapshot time and a "not live"
  badge. There is no animated attack traffic and no simulated telemetry.
- **Two-minute challenge.** Three questions use only the aggregate rows:
  compare three countries, estimate the top country's share, and compare
  regions. The score is local to the page and is never sent to the platform.

The map source is generated once:

```text
platform/frontend/src/data/worldMap.js
```

It contains the Natural Earth land outline, country centroids, and region
labels. Natural Earth is public domain. Regenerate it only when the source
changes; do not fetch map data at runtime.

### Privacy and accessibility

- Country-level counts only. The map cannot be filtered down to a small bucket
  because the ingest suppresses buckets below `minimum_bucket_size`.
- No learner, lab, session, prompt, packet, or flow data is used.
- The map has no runtime egress. The snapshot is a local file.
- Keyboard: arrow keys move between countries, Enter or Space selects, Home/End
  jump, and Escape clears. The hotspot list is a complete accessible fallback.
- The tooltip is decorative; the detail panel is the accessible announcement.
- `prefers-reduced-motion` disables the marker and tooltip transitions.

### Tests

- `src/components/__tests__/ThreatMap.test.js` covers markers, selection,
  region filtering, and the empty-filter state.
- `src/components/__tests__/ThreatMapQuiz.test.js` covers the question flow and
  the "nothing is recorded" statement.
- `src/composables/useToolPanel.test.js` covers the allow-listed tool keys.

## Verify before committing

```bash
cd platform/backend
python -c "from app.services import threat_awareness as t; d=t.snapshot(); print(d['mode'], d['totals']['entries_reported'], d['totals']['countries'])"
python -c "from app.services import ransomware_activity as r; d=r.snapshot(); print(d['mode'], d['totals']['window_posts'], len(d['groups']))"
```

Expected: `snapshot` mode, a recent `generated_at`, and no `sample` banner.

## Cadence

| Snapshot | Suggested cadence | Notes |
|---|---|---|
| FireHOL | Weekly or monthly | Re-download the monthly DB-IP file with the feed |
| Curated daily feeds | Weekly snapshot | DShield, Blocklist.de, Feodo, OffSeq, and IPsum move daily or faster |
| RansomLook | Every 1–3 days | The public totals move daily; weekly at minimum |

Do not schedule a refresh inside the platform. Run it on an operations host,
review the diff, and ship it as a release.

## Attribution

- FireHOL iplists: <https://iplists.firehol.org/>
- DB-IP Lite: <https://db-ip.com>, CC BY 4.0
- RansomLook: <https://www.ransomlook.io/>, CC BY 4.0

See [ADR 0008](decisions/0008-threat-awareness.md) and
[ADR 0009](decisions/0009-intelligence-sources.md).
