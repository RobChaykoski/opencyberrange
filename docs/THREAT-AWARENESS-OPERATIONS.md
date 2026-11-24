# Threat-awareness operations

Two snapshots feed the panel:

| Section | Source | Snapshot file |
|---|---|---|
| Hostile infrastructure | FireHOL iplists + a local GeoIP database | `platform/backend/app/data/threat-awareness.json` |
| Ransomware activity | RansomLook aggregate endpoints | `platform/backend/app/data/ransomware-activity.json` |

Both are offline files baked into the backend image. A refresh is a normal
release: regenerate the file, verify it, commit it, refresh the supply-chain
lock, sign, and deploy. The panel shows the snapshot timestamp; there is no
runtime egress.

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

## RansomLook

```bash
python scripts/fetch-ransomware-feed.py --max-groups 15
```

Only `/api/stats` and `/api/hot` are read. Victim names, post links, crypto
addresses, and peer addresses are excluded. Attribution: "Aggregated counts
derived from RansomLook (ransomlook.io), CC BY 4.0."

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
| RansomLook | Weekly | The public totals move daily |

Do not schedule a refresh inside the platform. Run it on an operations host,
review the diff, and ship it as a release.

## Attribution

- FireHOL iplists: <https://iplists.firehol.org/>
- DB-IP Lite: <https://db-ip.com>, CC BY 4.0
- RansomLook: <https://www.ransomlook.io/>, CC BY 4.0

See [ADR 0008](decisions/0008-threat-awareness.md) and
[ADR 0009](decisions/0009-intelligence-sources.md).
