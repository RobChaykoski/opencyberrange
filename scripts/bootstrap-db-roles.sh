#!/usr/bin/env bash
# Create or refresh the separate PostgreSQL identities used by the platform.
#
# Usage, from the directory that holds the compose files:
#   OCR_DB_RUNTIME_PASSWORD=... OCR_DB_MIGRATOR_PASSWORD=... \
#   OCR_DB_REPORTING_PASSWORD=... OCR_DB_BACKUP_PASSWORD=... \
#   OCR_DB_AUDIT_PASSWORD=... \
#   bash scripts/bootstrap-db-roles.sh [docker compose file flags]
#
# Production:
#   cd ~/opencyberrange/platform
#   bash ../scripts/bootstrap-db-roles.sh \
#     -f docker-compose.prod.yml -f docker-compose.adopt.yml \
#     -f docker-compose.override.yml
#
# Development:
#   cd ~/opencyberrange
#   bash scripts/bootstrap-db-roles.sh

set -euo pipefail

for name in \
  OCR_DB_MIGRATOR_PASSWORD \
  OCR_DB_RUNTIME_PASSWORD \
  OCR_DB_REPORTING_PASSWORD \
  OCR_DB_BACKUP_PASSWORD \
  OCR_DB_AUDIT_PASSWORD
do
  value="${!name:-}"
  if [ "${#value}" -lt 32 ]; then
    echo "error: $name must be set and at least 32 characters" >&2
    exit 1
  fi
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_FILE="$SCRIPT_DIR/../db/bootstrap-db-roles.sql"
if [ ! -f "$SQL_FILE" ]; then
  echo "error: $SQL_FILE not found" >&2
  exit 1
fi

docker compose "$@" exec -T \
  -e OCR_DB_MIGRATOR_PASSWORD="$OCR_DB_MIGRATOR_PASSWORD" \
  -e OCR_DB_RUNTIME_PASSWORD="$OCR_DB_RUNTIME_PASSWORD" \
  -e OCR_DB_REPORTING_PASSWORD="$OCR_DB_REPORTING_PASSWORD" \
  -e OCR_DB_BACKUP_PASSWORD="$OCR_DB_BACKUP_PASSWORD" \
  -e OCR_DB_AUDIT_PASSWORD="$OCR_DB_AUDIT_PASSWORD" \
  db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1' \
  < "$SQL_FILE"
