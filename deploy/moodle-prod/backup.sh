#!/usr/bin/env bash
# Back up the production pilot Moodle database and data directory.
#
#   cd ~/moodle-prod
#   bash backup.sh
#
# Keep the default 14-day retention; override RETENTION_DAYS if the pilot needs
# a longer record. Back up before every schema/config change and before the
# event.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"
set -a
# shellcheck disable=SC1091
. ./.env
set +a

RETENTION_DAYS="${RETENTION_DAYS:-14}"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
OUT="backups"
mkdir -p "$OUT"
chmod 700 "$OUT"

DB_FILE="$OUT/moodle-db-$STAMP.sql.gz"
DATA_FILE="$OUT/moodledata-$STAMP.tar.gz"

echo "[$(date -u +%FT%TZ)] dumping moodle database"
docker compose exec -T -e MYSQL_PWD="$MOODLE_DB_ROOT_PASSWORD" \
  moodle-db /opt/bitnami/mariadb/bin/mariadb-dump \
  -uroot --single-transaction --routines --triggers bitnami_moodle \
  | gzip -9 > "$DB_FILE"

echo "[$(date -u +%FT%TZ)] archiving moodledata"
docker compose exec -T moodle \
  tar -czf - -C /bitnami \
  --exclude='moodledata/cache/*' \
  --exclude='moodledata/localcache/*' \
  --exclude='moodledata/temp/*' \
  --exclude='moodledata/sessions/*' \
  moodledata > "$DATA_FILE"

chmod 600 "$DB_FILE" "$DATA_FILE"
find "$OUT" -type f -name 'moodle-db-*.sql.gz' -mtime +"$RETENTION_DAYS" -delete
find "$OUT" -type f -name 'moodledata-*.tar.gz' -mtime +"$RETENTION_DAYS" -delete

echo "[$(date -u +%FT%TZ)] backup complete"
ls -lh "$DB_FILE" "$DATA_FILE"
