#!/usr/bin/env bash
# Run OpenCyberRange database integrity checks from the Docker host.
#
# The checks are read-only against the platform database. They write JSON
# evidence under OCR_INTEGRITY_EVIDENCE_DIR (default /var/lib/ocr-integrity)
# and keep only the last OCR_INTEGRITY_RETENTION_DAYS days.
#
# What runs:
#   * data-quality audit (critical gate)
#   * append-only ledger chain and attribution check
#   * table checksum and database fingerprint
#   * on OCR_INTEGRITY_MANIFEST_DAY (ISO weekday, default Sunday): a signed
#     HMAC-SHA256 checksum manifest
#
# Usage:
#   sudo bash scripts/db-integrity-check.sh
#   sudo OCR_PLATFORM_DIR=/opt/opencyberrange bash scripts/db-integrity-check.sh
#
# Requirements: docker, flock, readlink, date, find.

set -euo pipefail

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PLATFORM_DIR="${OCR_PLATFORM_DIR:-$(cd "$SCRIPT_DIR/.." && pwd)}"
CONTAINER="${OCR_BACKEND_CONTAINER:-ocr-backend}"
EVIDENCE_DIR="${OCR_INTEGRITY_EVIDENCE_DIR:-/var/lib/ocr-integrity}"
RETENTION_DAYS="${OCR_INTEGRITY_RETENTION_DAYS:-90}"
MANIFEST_DAY="${OCR_INTEGRITY_MANIFEST_DAY:-7}"   # ISO weekday: 7 = Sunday
LOCK_FILE="${OCR_INTEGRITY_LOCK:-/run/ocr-db-integrity.lock}"
HOST="$(hostname -s 2>/dev/null || hostname)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$EVIDENCE_DIR/$HOST-$STAMP"
CHECK_SCRIPT="$PLATFORM_DIR/scripts/database_integrity.py"

log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*"; }
fail() { log "ERROR: $*" >&2; exit 1; }

[ -r "$CHECK_SCRIPT" ] || fail "database_integrity.py not found at $CHECK_SCRIPT"
command -v docker >/dev/null 2>&1 || fail "docker is required"
command -v flock >/dev/null 2>&1 || fail "flock is required"

# Optional key and deployment overrides. Keep this file root-only (0600).
if [ -r /etc/opencyberrange/integrity.env ]; then
  set -a
  # shellcheck disable=SC1091
  . /etc/opencyberrange/integrity.env
  set +a
fi

mkdir -p "$EVIDENCE_DIR"
chmod 700 "$EVIDENCE_DIR"

exec 9>"$LOCK_FILE" 2>/dev/null || exec 9>"/tmp/ocr-db-integrity.lock"
if ! flock -n 9; then
  log "Another integrity check is running; exiting."
  exit 0
fi

if [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null || echo false)" != "true" ]; then
  fail "container $CONTAINER is not running"
fi

run_check() {
  local name="$1"
  shift
  if docker exec -i "$CONTAINER" python - "$@" < "$CHECK_SCRIPT" > "$OUT.$name.json"; then
    log "$name: ok"
    return 0
  fi
  log "$name: FAILED (see $OUT.$name.json and the container log)" >&2
  return 1
}

rc=0
run_check quality --json --quality || rc=1
run_check ledger --json --ledger || rc=1
run_check checksum --checksum || rc=1

if [ "$(date -u +%u)" = "$MANIFEST_DAY" ]; then
  if [ -z "${DB_INTEGRITY_KEY:-}" ]; then
    log "manifest: skipped (DB_INTEGRITY_KEY is not set)" >&2
  elif docker exec -i -e DB_INTEGRITY_KEY "$CONTAINER" python - \
      --write-manifest /tmp/db-manifest.json \
      < "$CHECK_SCRIPT" > "$OUT.manifest-write.json"; then
    docker cp "$CONTAINER:/tmp/db-manifest.json" "$OUT.manifest.json"
    docker exec "$CONTAINER" rm -f /tmp/db-manifest.json
    log "manifest: signed and copied to $OUT.manifest.json"
  else
    log "manifest: FAILED" >&2
    rc=1
  fi
fi

find "$EVIDENCE_DIR" -type f -mtime "+$RETENTION_DAYS" -delete

log "Evidence: $OUT.*.json (exit $rc)"
exit "$rc"
