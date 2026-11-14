#!/usr/bin/env bash
# Restore the newest backup into a scratch database and compare row counts.
#
# The live database is never modified. The scratch database is dropped on exit.
# Use this after installing or changing the backup timer, and before a release
# that includes a migration.
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
DB_CONTAINER="${DB_CONTAINER:-ocr-db}"
DB_USER="${DB_USER:-labuser}"
DB_NAME="${DB_NAME:-labdb}"
TABLES="${TABLES:-users labs courses course_enrollments lab_completions achievements review_requests activity_events}"

DUMP="$(ls -t "$BACKUP_DIR"/ocr-backup-*.dump 2>/dev/null | head -1 || true)"
if [ -z "$DUMP" ]; then
  echo "ERROR: no ocr-backup-*.dump in $BACKUP_DIR" >&2
  exit 1
fi
echo "drill: restoring $DUMP"

SCRATCH="${DB_NAME}_restore_drill_$(date -u +%H%M%S)"
cleanup() { docker exec "$DB_CONTAINER" dropdb -U "$DB_USER" --if-exists "$SCRATCH" >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker exec "$DB_CONTAINER" createdb -U "$DB_USER" "$SCRATCH"
docker exec -i "$DB_CONTAINER" pg_restore -U "$DB_USER" -d "$SCRATCH" --no-owner < "$DUMP" >/dev/null
echo "drill: restore complete, comparing counts"

failed=0
for table in $TABLES; do
  live=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -tAc "select count(*) from $table")
  restored=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$SCRATCH" -tAc "select count(*) from $table")
  if [ "$live" = "$restored" ]; then
    printf '  %-22s %8s ok\n' "$table" "$live"
  else
    printf '  %-22s live=%s restored=%s MISMATCH\n' "$table" "$live" "$restored"
    failed=1
  fi
done
if [ "$failed" -ne 0 ]; then
  echo "DRILL FAILED" >&2
  exit 1
fi
echo "DRILL PASSED"
