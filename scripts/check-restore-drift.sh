#!/usr/bin/env bash
# Restore the newest backup into a scratch database, migrate it to head, and
# enforce the known Alembic drift budget.
#
# This is a release/manual gate, not a per-commit CI job: it needs a real
# production dump and the database container. The live database is untouched.
#
#   bash scripts/check-restore-drift.sh
#   SCHEMA_DRIFT_BASELINE=48 bash scripts/check-restore-drift.sh
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
DB_CONTAINER="${DB_CONTAINER:-ocr-db}"
BACKEND_CONTAINER="${BACKEND_CONTAINER:-ocr-backend}"
DB_USER="${DB_USER:-labuser}"
DB_NAME="${DB_NAME:-labdb}"
BASELINE="${SCHEMA_DRIFT_BASELINE:-0}"

DUMP="$(ls -t "$BACKUP_DIR"/ocr-backup-*.dump 2>/dev/null | head -1 || true)"
if [ -z "$DUMP" ]; then
    echo "ERROR: no ocr-backup-*.dump in $BACKUP_DIR" >&2
    exit 1
fi

SCRATCH="${DB_NAME}_restore_drift_$(date -u +%H%M%S)"
cleanup() {
    docker exec "$DB_CONTAINER" dropdb -U "$DB_USER" --if-exists "$SCRATCH" \
        >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "drift: restoring $DUMP into $SCRATCH"
docker exec "$DB_CONTAINER" dropdb -U "$DB_USER" --if-exists "$SCRATCH" \
    >/dev/null 2>&1 || true
docker exec "$DB_CONTAINER" createdb -U "$DB_USER" "$SCRATCH"
docker exec -i "$DB_CONTAINER" pg_restore -U "$DB_USER" -d "$SCRATCH" \
    --no-owner < "$DUMP" >/dev/null
echo "drift: restore complete; migrating to head"

DB_PASS="$(docker exec "$DB_CONTAINER" printenv POSTGRES_PASSWORD)"
ENC_PASS="$(printf '%s' "$DB_PASS" | python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip(), safe=""))')"
SCRATCH_URL="postgresql://${DB_USER}:${ENC_PASS}@${DB_CONTAINER}:5432/${SCRATCH}"

COUNT="$(docker exec -e MIGRATOR_DATABASE_URL="$SCRATCH_URL" "$BACKEND_CONTAINER" sh -c '
    alembic -c alembic.ini upgrade head >/tmp/ocr-restore-drift-upgrade.log 2>&1 || {
        cat /tmp/ocr-restore-drift-upgrade.log >&2
        exit 2
    }
    alembic -c alembic.ini check 2>&1 | grep "Detected" | grep -v "sequence named" | wc -l
')"

COUNT="$(printf '%s' "$COUNT" | tr -d '[:space:]')"
echo "drift: ${COUNT} operation(s); baseline ${BASELINE}"
if [ "$COUNT" -gt "$BASELINE" ]; then
    echo "FAILED: schema drift increased beyond the baseline" >&2
    exit 1
fi
echo "PASSED: restore-drift check"
