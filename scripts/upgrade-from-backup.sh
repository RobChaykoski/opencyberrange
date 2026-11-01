#!/usr/bin/env bash
# Upgrade an OpenCyberRange server from the GitHub backup repository.
#
# The script:
#   1. backs up the database, users, .env, compose files, and certificates
#   2. fast-forwards the checkout from the selected remote/branch
#   3. rebuilds and recreates the backend and frontend
#   4. seeds the curriculum and discovers new labs
#   5. merges the backed-up users into the upgraded database
#   6. verifies the backend and frontend health
#
# Usage:
#   sudo bash scripts/upgrade-from-backup.sh
#   sudo bash scripts/upgrade-from-backup.sh --remote backup --update-users
#   sudo bash scripts/upgrade-from-backup.sh --help
#
# The user export contains password hashes. The backup directory is created
# with mode 700 and should be deleted after a successful upgrade.

set -Eeuo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLATFORM_DIR="$REPO_DIR/platform"
BACKUP_ROOT="${BACKUP_ROOT:-$HOME/opencyberrange-backups}"
REMOTE="${GIT_REMOTE:-backup}"
BRANCH="${GIT_BRANCH:-main}"
DB_USER="${DB_USER:-}"
DB_NAME="${DB_NAME:-}"
RANGEBOX_IMAGE="${RANGEBOX_IMAGE:-opencyberrange/rangebox:lite}"
UBUNTUBOX_IMAGE="${UBUNTUBOX_IMAGE:-opencyberrange/ubuntubox:latest}"
REMNUX_IMAGE="${REMNUX_IMAGE:-opencyberrange/remnuxbox:noble}"
UPDATE_USERS=false
SKIP_USERS=false
SKIP_DISCOVERY=false
SKIP_VERIFY=false
SKIP_RANGEBOX=false
PREBUILD_LABS=true
PREBUILD_PARALLEL="${PREBUILD_PARALLEL:-1}"
CURRENT_STEP="preflight"
BACKUP_DIR=""

usage() {
  cat <<'EOF'
Usage: upgrade-from-backup.sh [options]

Options:
  --remote NAME         Git remote to upgrade from (default: backup, then origin)
  --branch NAME         Git branch to upgrade to (default: main)
  --backup-root DIR     Where to create the timestamped backup
  --db-user USER        PostgreSQL user (default: POSTGRES_USER from platform/.env)
  --db-name NAME        PostgreSQL database (default: POSTGRES_DB from platform/.env)
  --update-users        Overwrite existing users from the backup export
  --skip-users          Do not export or merge users (database backup still runs)
  --skip-discovery      Do not reseed curriculum or discover labs
  --skip-labs           Do not rebuild all lab images (definitions are still refreshed)
  --skip-rangebox       Do not rebuild Kali, Ubuntu, and REMnux RangeBox images
  --skip-verify         Skip the read-only preflight verification
  --prebuild-parallel N Build N lab images concurrently (default: 1)
  -h, --help            Show this help

By default the upgrade refreshes curriculum/lab definitions, rebuilds every lab
image, and rebuilds the Kali, Ubuntu, and REMnux RangeBox images. Lab image
prebuilds can take a long time and need significant disk space; use --skip-labs
or --skip-rangebox for a code-only upgrade.

Environment overrides:
  BACKUP_ROOT, GIT_REMOTE, GIT_BRANCH, DB_USER, DB_NAME, PREBUILD_PARALLEL
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote) REMOTE="${2:?--remote requires a value}"; shift 2 ;;
    --branch) BRANCH="${2:?--branch requires a value}"; shift 2 ;;
    --backup-root) BACKUP_ROOT="${2:?--backup-root requires a value}"; shift 2 ;;
    --db-user) DB_USER="${2:?--db-user requires a value}"; shift 2 ;;
    --db-name) DB_NAME="${2:?--db-name requires a value}"; shift 2 ;;
    --update-users) UPDATE_USERS=true; shift ;;
    --skip-users) SKIP_USERS=true; shift ;;
    --skip-discovery) SKIP_DISCOVERY=true; shift ;;
    --skip-labs) PREBUILD_LABS=false; shift ;;
    --skip-rangebox) SKIP_RANGEBOX=true; shift ;;
    --skip-verify) SKIP_VERIFY=true; shift ;;
    --prebuild-parallel) PREBUILD_PARALLEL="${2:?--prebuild-parallel requires a value}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

log() { printf '\n[*] %s\n' "$*"; }
warn() { printf '[!] %s\n' "$*" >&2; }
fail() { printf '[x] %s\n' "$*" >&2; exit 1; }

on_error() {
  local code=$?
  printf '\n[x] Upgrade failed during: %s\n' "$CURRENT_STEP" >&2
  if [[ -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ]]; then
    printf '[x] Backup is at: %s\n' "$BACKUP_DIR" >&2
    printf '[x] Restore instructions are in: %s/README.txt\n' "$BACKUP_DIR" >&2
  fi
  exit "$code"
}
trap on_error ERR

env_value() {
  local key="$1" file="$2"
  [[ -f "$file" ]] || return 0
  grep -E "^${key}=" "$file" | tail -1 | cut -d= -f2- \
    | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//"
}

docker_path() {
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$1"
  else
    printf '%s' "$1"
  fi
}

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------

log "Preflight checks"
command -v docker >/dev/null 2>&1 || fail "docker is not installed"
docker compose version >/dev/null 2>&1 || fail "docker compose v2 is not available"
command -v git >/dev/null 2>&1 || fail "git is not installed"
git -C "$REPO_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  || fail "not a git checkout: $REPO_DIR"
[[ -f "$PLATFORM_DIR/.env" ]] || fail "missing $PLATFORM_DIR/.env"

if [[ -z "$DB_USER" ]]; then
  DB_USER="$(env_value POSTGRES_USER "$PLATFORM_DIR/.env")"
  DB_USER="${DB_USER:-labuser}"
fi
if [[ -z "$DB_NAME" ]]; then
  DB_NAME="$(env_value POSTGRES_DB "$PLATFORM_DIR/.env")"
  DB_NAME="${DB_NAME:-labdb}"
fi

if ! git -C "$REPO_DIR" remote get-url "$REMOTE" >/dev/null 2>&1; then
  if [[ "$REMOTE" == "backup" ]] && git -C "$REPO_DIR" remote get-url origin >/dev/null 2>&1; then
    warn "remote 'backup' not found; using 'origin'"
    REMOTE=origin
  else
    fail "git remote '$REMOTE' does not exist"
  fi
fi

if [[ -n "$(git -C "$REPO_DIR" status --porcelain --untracked-files=no)" ]]; then
  fail "the checkout has uncommitted changes; commit or stash them before upgrading"
fi

COMPOSE=()
if [[ -f "$PLATFORM_DIR/docker-compose.yml" ]]; then
  COMPOSE=(docker compose -f "$(docker_path "$PLATFORM_DIR/docker-compose.yml")")
elif [[ -f "$PLATFORM_DIR/docker-compose.prod.yml" ]]; then
  COMPOSE=(docker compose -f "$(docker_path "$PLATFORM_DIR/docker-compose.prod.yml")")
else
  fail "no docker-compose.yml or docker-compose.prod.yml in $PLATFORM_DIR"
fi
if [[ -f "$PLATFORM_DIR/docker-compose.override.yml" ]]; then
  COMPOSE+=(-f "$(docker_path "$PLATFORM_DIR/docker-compose.override.yml")")
fi
compose() { "${COMPOSE[@]}" "$@"; }
# Git Bash rewrites absolute container paths such as /tmp/x into Windows paths
# before Docker sees them. Disable that conversion for exec/cp arguments.
compose_in() { MSYS_NO_PATHCONV=1 "${COMPOSE[@]}" "$@"; }
COMPOSE_DISPLAY="$(printf '%q ' "${COMPOSE[@]}")"

if [[ "$SKIP_USERS" == false && ! -f "$REPO_DIR/scripts/user_transfer.py" ]]; then
  fail "scripts/user_transfer.py is missing; copy it to the server or use --skip-users"
fi

log "Repository: $REPO_DIR"
log "Remote:     $REMOTE/$BRANCH"
log "Database:   $DB_USER@$DB_NAME"

if [[ "$SKIP_VERIFY" == false ]]; then
  CURRENT_STEP="preflight verification"
  log "Running read-only preflight verification"
  bash "$REPO_DIR/scripts/verify-upgrade.sh" \
    --remote "$REMOTE" \
    --branch "$BRANCH" \
    --db-user "$DB_USER" \
    --db-name "$DB_NAME" \
    --backup-root "$BACKUP_ROOT"
fi

# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

CURRENT_STEP="backup"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$BACKUP_ROOT/ocr-$TIMESTAMP"
log "Creating backup at $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR" 2>/dev/null || true

cp "$PLATFORM_DIR/.env" "$BACKUP_DIR/.env"
for f in docker-compose.yml docker-compose.prod.yml docker-compose.override.yml; do
  [[ -f "$PLATFORM_DIR/$f" ]] && cp "$PLATFORM_DIR/$f" "$BACKUP_DIR/$f"
done
[[ -d "$PLATFORM_DIR/certs" ]] && cp -R "$PLATFORM_DIR/certs" "$BACKUP_DIR/certs"

log "Starting database and backend for the backup"
compose up -d db backend >/dev/null

log "Dumping the database"
compose_in exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$BACKUP_DIR/database.dump"
[[ -s "$BACKUP_DIR/database.dump" ]] || fail "database dump is empty"

if [[ "$SKIP_USERS" == false ]]; then
  log "Exporting users"
  compose_in cp "$(docker_path "$REPO_DIR/scripts/user_transfer.py")" backend:/tmp/user_transfer.py >/dev/null
  compose_in exec -T backend python /tmp/user_transfer.py export -o /tmp/users-export.json
  compose_in cp backend:/tmp/users-export.json "$(docker_path "$BACKUP_DIR/users-export.json")" >/dev/null
  compose_in exec -T backend rm -f /tmp/user_transfer.py /tmp/users-export.json
  chmod 600 "$BACKUP_DIR/users-export.json" 2>/dev/null || true
fi

cat > "$BACKUP_DIR/README.txt" <<EOF
OpenCyberRange backup: $BACKUP_DIR

Files:
  database.dump       PostgreSQL custom-format dump
  users-export.json   Portable user export (password hashes; sensitive)
  .env                Platform environment
  docker-compose*     Compose configuration
  certs/              TLS certificates, if present

Full database restore (destructive):
  ${COMPOSE_DISPLAY}stop backend frontend
  cat "$BACKUP_DIR/database.dump" | ${COMPOSE_DISPLAY}exec -T db pg_restore -U $DB_USER -d $DB_NAME --clean --if-exists
  ${COMPOSE_DISPLAY}up -d backend frontend

User merge only:
  ${COMPOSE_DISPLAY}cp "$(docker_path "$BACKUP_DIR/users-export.json")" backend:/tmp/users-export.json
  ${COMPOSE_DISPLAY}exec -T backend python /tmp/user_transfer.py import /tmp/users-export.json --dry-run
  ${COMPOSE_DISPLAY}exec -T backend python /tmp/user_transfer.py import /tmp/users-export.json

The user export contains password hashes and personal data. Delete this backup
directory after the upgrade has been verified and retained elsewhere if needed.
EOF
log "Backup complete: $BACKUP_DIR"

# ---------------------------------------------------------------------------
# Pull and deploy
# ---------------------------------------------------------------------------

CURRENT_STEP="git fetch/merge"
OLD_COMMIT="$(git -C "$REPO_DIR" rev-parse HEAD)"
log "Fetching $REMOTE/$BRANCH"
git -C "$REPO_DIR" fetch "$REMOTE" "$BRANCH"
log "Fast-forwarding to $REMOTE/$BRANCH"
git -C "$REPO_DIR" merge --ff-only "$REMOTE/$BRANCH"
NEW_COMMIT="$(git -C "$REPO_DIR" rev-parse HEAD)"

CURRENT_STEP="docker build/recreate"
log "Rebuilding and recreating database, backend, and frontend"
compose up -d --build db backend frontend

CURRENT_STEP="backend health"
log "Waiting for the backend health endpoint"
READY=false
for _ in $(seq 1 60); do
  if compose_in exec -T backend curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    READY=true
    break
  fi
  sleep 2
done
[[ "$READY" == true ]] || fail "backend did not become healthy"

if [[ "$SKIP_DISCOVERY" == false ]]; then
  CURRENT_STEP="curriculum/discovery"
  log "Seeding curriculum and discovering labs"
  compose_in exec -T backend python -m app.scripts.seed_curriculum
  compose_in exec -T backend python /app/app/scripts/discover_labs.py
fi

if [[ "$PREBUILD_LABS" == true ]]; then
  CURRENT_STEP="lab image prebuild"
  log "Rebuilding all lab images (cached layers are reused where possible)"
  bash "$REPO_DIR/scripts/prebuild-labs.sh" --parallel "$PREBUILD_PARALLEL"
fi

if [[ "$SKIP_RANGEBOX" == false ]]; then
  CURRENT_STEP="rangebox images"
  log "Rebuilding RangeBox images: Kali, Ubuntu, and REMnux"
  docker build --pull -t "$RANGEBOX_IMAGE" "$REPO_DIR/RangeBox"
  docker build --pull -t "$UBUNTUBOX_IMAGE" "$REPO_DIR/UbuntuBox"
  docker build --pull -t "$REMNUX_IMAGE" "$REPO_DIR/RemnuxBox"
fi

if [[ "$SKIP_USERS" == false ]]; then
  CURRENT_STEP="user merge"
  log "Merging users from the backup (existing users are preserved by default)"
  compose_in cp "$(docker_path "$REPO_DIR/scripts/user_transfer.py")" backend:/tmp/user_transfer.py >/dev/null
  compose_in cp "$(docker_path "$BACKUP_DIR/users-export.json")" backend:/tmp/users-export.json >/dev/null
  if [[ "$UPDATE_USERS" == true ]]; then
    compose_in exec -T backend python /tmp/user_transfer.py import /tmp/users-export.json --update
  else
    compose_in exec -T backend python /tmp/user_transfer.py import /tmp/users-export.json
  fi
  compose_in exec -T backend rm -f /tmp/user_transfer.py /tmp/users-export.json
fi

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

CURRENT_STEP="verification"
log "Container status"
compose ps

log "Backend health"
compose_in exec -T backend curl -fsS http://localhost:8000/health
printf '\n'

log "User count"
compose_in exec -T db psql -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT count(*) FROM users;"

LAB_STATUS="rebuilt"
[[ "$PREBUILD_LABS" == true ]] || LAB_STATUS="skipped (--skip-labs)"
RANGEBOX_STATUS="rebuilt"
[[ "$SKIP_RANGEBOX" == false ]] || RANGEBOX_STATUS="skipped (--skip-rangebox)"

cat <<EOF

[✓] Upgrade complete
    Previous commit: $OLD_COMMIT
    Current commit:  $NEW_COMMIT
    Backup:          $BACKUP_DIR
    Lab images:      $LAB_STATUS
    RangeBox images: $RANGEBOX_STATUS

Next steps:
  - Log in and verify a migrated account and the exercise catalogue.
  - Verify the frontend over HTTPS.
  - Delete the backup directory after confirming the upgrade, or move it to
    secure storage. It contains password hashes and personal data.
EOF
