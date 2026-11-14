#!/usr/bin/env bash
# Back up the production database, erasure ledger, and platform env.
#
# Run from anywhere. The database dump is a custom-format archive validated
# with pg_restore before it is kept. Old backups matching this script's own
# names are pruned after RETENTION_DAYS; unrelated files are left alone.
#
# Environment overrides:
#   BACKUP_DIR       destination (default ~/backups)
#   RETENTION_DAYS   daily retention (default 14)
#   DB_CONTAINER     default ocr-db
#   BACKEND_CONTAINER default ocr-backend
#   DB_USER/DB_NAME  default labuser/labdb
#   ENV_FILE         default ~/opencyberrange/platform/.env
#
# Off-host destinations (any combination; encrypted by default):
#   BACKUP_REMOTE         rsync target, e.g. ocr-offsite:/path
#   BACKUP_NFS_DIR        path to an already-mounted NFS directory
#   BACKUP_SMB_URL        smb://host/share/dir/ (curl + netrc)
#   BACKUP_RCLONE_REMOTE  rclone remote:path (S3, WebDAV, SFTP, crypt)
#   BACKUP_COPY_CMD       executable receiving each encrypted file path
#   BACKUP_GPG_RECIPIENT  required for encryption (public key)
#   BACKUP_ALLOW_PLAINTEXT=1 explicitly allows unencrypted off-host copies
#   BACKUP_SMB_NETRC      default ~/.ocr-smb-netrc
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
DB_CONTAINER="${DB_CONTAINER:-ocr-db}"
BACKEND_CONTAINER="${BACKEND_CONTAINER:-ocr-backend}"
DB_USER="${DB_USER:-labuser}"
DB_NAME="${DB_NAME:-labdb}"
ENV_FILE="${ENV_FILE:-$HOME/opencyberrange/platform/.env}"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
PREFIX="ocr-backup"

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

DUMP="$BACKUP_DIR/$PREFIX-$STAMP.dump"
PARTIAL="$DUMP.partial"
cleanup() { rm -f "$PARTIAL"; }
trap cleanup EXIT

echo "[$(date -u +%FT%TZ)] dumping $DB_NAME from $DB_CONTAINER"
docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$PARTIAL"
if [ ! -s "$PARTIAL" ]; then
  echo "ERROR: database dump is empty" >&2
  exit 1
fi
OBJECTS=$(docker exec -i "$DB_CONTAINER" pg_restore -l < "$PARTIAL" | wc -l)
if [ "$OBJECTS" -lt 1 ]; then
  echo "ERROR: dump archive failed pg_restore validation" >&2
  exit 1
fi
mv "$PARTIAL" "$DUMP"
chmod 600 "$DUMP"
echo "database: $DUMP ($(du -h "$DUMP" | cut -f1), $OBJECTS objects)"

if docker cp "$BACKEND_CONTAINER:/workbook/erasure-ledger.jsonl" \
     "$BACKUP_DIR/erasure-ledger-$STAMP.jsonl" 2>/dev/null; then
  LEDGER_FILE="$BACKUP_DIR/erasure-ledger-$STAMP.jsonl"
  chmod 600 "$LEDGER_FILE"
  echo "ledger:   $LEDGER_FILE"
else
  LEDGER_FILE=""
  echo "ledger:   not present on this deployment (ok)"
fi

ENV_COPY=""
if [ -f "$ENV_FILE" ]; then
  ENV_COPY="$BACKUP_DIR/platform-env-$STAMP"
  cp "$ENV_FILE" "$ENV_COPY"
  chmod 600 "$ENV_COPY"
  echo "env:      $ENV_COPY"
fi

sha256sum "$DUMP" > "$DUMP.sha256"
chmod 600 "$DUMP.sha256"

DESTINATIONS=0
for var in BACKUP_REMOTE BACKUP_NFS_DIR BACKUP_SMB_URL BACKUP_RCLONE_REMOTE BACKUP_COPY_CMD; do
  [ -n "${!var:-}" ] && DESTINATIONS=1
done

if [ "$DESTINATIONS" = 1 ]; then
  if [ -z "${BACKUP_GPG_RECIPIENT:-}" ] && [ "${BACKUP_ALLOW_PLAINTEXT:-0}" != "1" ]; then
    echo "ERROR: off-host backups require BACKUP_GPG_RECIPIENT (or an explicit BACKUP_ALLOW_PLAINTEXT=1)" >&2
    exit 1
  fi

  files=("$DUMP.sha256")
  encrypted=()
  if [ -n "${BACKUP_GPG_RECIPIENT:-}" ]; then
    command -v gpg >/dev/null || { echo "ERROR: gpg not found for backup encryption" >&2; exit 1; }
    sensitive=("$DUMP")
    [ -n "$LEDGER_FILE" ] && sensitive+=("$LEDGER_FILE")
    [ -n "$ENV_COPY" ] && sensitive+=("$ENV_COPY")
    for src in "${sensitive[@]}"; do
      gpg --batch --yes --trust-model always \
        --recipient "$BACKUP_GPG_RECIPIENT" \
        --output "$src.gpg" --encrypt "$src"
      files+=("$src.gpg")
      encrypted+=("$src.gpg")
    done
    sha256sum "$DUMP.gpg" > "$DUMP.gpg.sha256"
    files+=("$DUMP.gpg.sha256")
    encrypted+=("$DUMP.gpg.sha256")
    echo "encrypt:  ${#encrypted[@]} file(s) for $BACKUP_GPG_RECIPIENT"
  else
    files=("$DUMP" "$DUMP.sha256")
    [ -n "$LEDGER_FILE" ] && files+=("$LEDGER_FILE")
    [ -n "$ENV_COPY" ] && files+=("$ENV_COPY")
    echo "WARNING: BACKUP_ALLOW_PLAINTEXT=1, off-host copies are not encrypted"
  fi

  if [ -n "${BACKUP_REMOTE:-}" ]; then
    echo "remote:   syncing to $BACKUP_REMOTE"
    rsync -a "${files[@]}" "${BACKUP_REMOTE%/}/"
  fi

  if [ -n "${BACKUP_NFS_DIR:-}" ]; then
    [ -d "$BACKUP_NFS_DIR" ] || { echo "ERROR: BACKUP_NFS_DIR is not a mounted directory: $BACKUP_NFS_DIR" >&2; exit 1; }
    cp -p "${files[@]}" "${BACKUP_NFS_DIR%/}/"
    echo "nfs:      copied encrypted set to $BACKUP_NFS_DIR"
  fi

  if [ -n "${BACKUP_SMB_URL:-}" ]; then
    if [ ${#encrypted[@]} -eq 0 ]; then
      echo "ERROR: BACKUP_SMB_URL requires BACKUP_GPG_RECIPIENT" >&2
      exit 1
    fi
    netrc="${BACKUP_SMB_NETRC:-$HOME/.ocr-smb-netrc}"
    [ -f "$netrc" ] || { echo "ERROR: missing SMB credentials file $netrc" >&2; exit 1; }
    for f in "$DUMP.sha256" "${encrypted[@]}"; do
      curl -sS --fail --max-time 300 --netrc-file "$netrc" \
        -T "$f" "${BACKUP_SMB_URL%/}/$(basename "$f")"
    done
    echo "smb:      uploaded encrypted set to $BACKUP_SMB_URL"
  fi

  if [ -n "${BACKUP_RCLONE_REMOTE:-}" ]; then
    command -v rclone >/dev/null || { echo "ERROR: rclone not found for BACKUP_RCLONE_REMOTE" >&2; exit 1; }
    for f in "${files[@]}"; do
      rclone copyto "$f" "${BACKUP_RCLONE_REMOTE%/}/$(basename "$f")"
    done
    echo "rclone:   uploaded to $BACKUP_RCLONE_REMOTE"
  fi

  if [ -n "${BACKUP_COPY_CMD:-}" ]; then
    for f in "${files[@]}"; do
      "$BACKUP_COPY_CMD" "$f"
    done
    echo "command:  handed the encrypted set to BACKUP_COPY_CMD"
  fi

  if [ ${#encrypted[@]} -gt 0 ]; then
    rm -f "${encrypted[@]}"
  fi
fi

find "$BACKUP_DIR" -maxdepth 1 -type f \
  \( -name "$PREFIX-*.dump" -o -name "$PREFIX-*.dump.sha256" \
     -o -name "erasure-ledger-*.jsonl" -o -name "platform-env-*" \) \
  -mtime +"$RETENTION_DAYS" -print -delete

echo "[$(date -u +%FT%TZ)] backup complete"
