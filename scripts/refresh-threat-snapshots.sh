#!/usr/bin/env bash
# Refresh the threat-awareness snapshots on an operations host.
#
# The platform never fetches these feeds at runtime. This helper downloads the
# current DB-IP Lite country database, regenerates both snapshots into a review
# directory, validates them through the backend services, and prints a diff.
# It does not commit, refresh the supply-chain lock, sign, or deploy.
#
# Usage:
#   scripts/refresh-threat-snapshots.sh
#   scripts/refresh-threat-snapshots.sh --output /var/tmp/ocr-threat-review
#   scripts/refresh-threat-snapshots.sh --apply
#   scripts/refresh-threat-snapshots.sh --geoip-db /path/to/dbip.mmdb
#
# Weekly cron example (still review and release through a signed tag):
#   17 3 * * 1 cd /path/to/opencyberrange && \
#     scripts/refresh-threat-snapshots.sh --output /var/tmp/ocr-threat-review \
#     >> /var/log/ocr-threat-refresh.log 2>&1

set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MONTH="${THREAT_GEOIP_MONTH:-$(date -u +%Y-%m)}"
GEOIP_DIR="${THREAT_GEOIP_DIR:-${TMPDIR:-/tmp}/ocr-geoip}"
GEOIP_DB="${THREAT_GEOIP_DB:-}"
OUT_DIR=""
APPLY=0

usage() {
    sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
}

while (($#)); do
    case "$1" in
        --apply) APPLY=1; shift ;;
        --output) OUT_DIR="${2:?--output needs a directory}"; shift 2 ;;
        --geoip-db) GEOIP_DB="${2:?--geoip-db needs a file}"; shift 2 ;;
        --month) MONTH="${2:?--month needs YYYY-MM}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    esac
done

if [[ -z "$GEOIP_DB" ]]; then
    GEOIP_DB="${GEOIP_DIR}/dbip-country-lite-${MONTH}.mmdb"
fi

if [[ -z "$OUT_DIR" ]]; then
    OUT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ocr-threat-refresh.XXXXXX")"
fi
mkdir -p "$OUT_DIR"

if [[ ! -f "$GEOIP_DB" ]]; then
    echo "Downloading DB-IP Lite ${MONTH}"
    mkdir -p "$(dirname "$GEOIP_DB")"
    tmp_gz="${GEOIP_DB}.gz"
    curl -fsSL --retry 3 -o "$tmp_gz" \
        "https://download.db-ip.com/free/dbip-country-lite-${MONTH}.mmdb.gz"
    python3 - "$tmp_gz" "$GEOIP_DB" <<'PY'
import gzip
import shutil
import sys

with gzip.open(sys.argv[1], "rb") as src, open(sys.argv[2], "wb") as dst:
    shutil.copyfileobj(src, dst)
PY
    rm -f "$tmp_gz"
fi

echo "Generating hostile-infrastructure snapshot"
python3 "$ROOT/scripts/fetch-threat-feed.py" \
    --output "$OUT_DIR/threat-awareness.json" \
    --geoip-db "$GEOIP_DB" \
    --minimum-bucket-size 25 \
    --require-geoip

echo "Generating ransomware snapshot"
python3 "$ROOT/scripts/fetch-ransomware-feed.py" \
    --output "$OUT_DIR/ransomware-activity.json" \
    --max-groups 15

echo "Validating snapshots"
(
    cd "$ROOT/platform/backend"
    THREAT_AWARENESS_SNAPSHOT="$OUT_DIR/threat-awareness.json" \
    RANSOMWARE_ACTIVITY_SNAPSHOT="$OUT_DIR/ransomware-activity.json" \
    python3 - <<'PY'
from app.services import ransomware_activity, threat_awareness

threat = threat_awareness.snapshot()
ransom = ransomware_activity.snapshot()
print(
    "threat:",
    threat["mode"],
    threat["generated_at"],
    f"{threat['totals']['entries_reported']} entries",
    f"{threat['totals']['countries']} countries",
    f"{len(threat['categories'])} categories",
)
print(
    "ransom:",
    ransom["mode"],
    ransom["generated_at"],
    f"{ransom['totals']['window_posts']} posts",
    f"{len(ransom['groups'])} groups",
)
PY
)

for name in threat-awareness.json ransomware-activity.json; do
    repo_file="$ROOT/platform/backend/app/data/${name}"
    out_file="$OUT_DIR/${name}"
    if cmp -s "$repo_file" "$out_file"; then
        echo "${name}: unchanged"
    else
        echo "${name}: changed"
        diff -u "$repo_file" "$out_file" | sed -n '1,60p' || true
    fi
done

if [[ "$APPLY" == "1" ]]; then
    cp "$OUT_DIR/threat-awareness.json" \
        "$ROOT/platform/backend/app/data/threat-awareness.json"
    cp "$OUT_DIR/ransomware-activity.json" \
        "$ROOT/platform/backend/app/data/ransomware-activity.json"
    chmod 0644 \
        "$ROOT/platform/backend/app/data/threat-awareness.json" \
        "$ROOT/platform/backend/app/data/ransomware-activity.json"
    echo "Applied to platform/backend/app/data."
    echo "Refresh the supply-chain lock, sign, and release through a signed tag."
else
    echo "Review the generated files in ${OUT_DIR}."
    echo "Rerun with --apply to copy them into the tree."
fi
