#!/usr/bin/env bash
# ==============================================================================
# OpenCyberRange in-place production update
# ==============================================================================
#
# For deployments where the repository contains the deployable platform tree:
#
#   ~/opencyberrange/platform/docker-compose.prod.yml
#   ~/opencyberrange/platform/docker-compose.adopt.yml      (optional)
#   ~/opencyberrange/platform/docker-compose.override.yml   (optional)
#
# This is the current production layout. It does not use sudo: the deploy user
# must own the checkout and be in the docker group. The existing
# ocr-platform.service drop-in owns boot ordering.
#
# The older scripts/deploy-updates.sh targets a split layout with a root
# docker-compose.yml and deployed backend/frontend directories. It will fail
# here. Use this script instead.
#
# Usage:
#   bash scripts/deploy-inplace.sh --dry-run
#   bash scripts/deploy-inplace.sh
#   bash scripts/deploy-inplace.sh --tag v5.36.0
#   bash scripts/deploy-inplace.sh --skip-wiki --skip-backup
#
# ==============================================================================

set -Eeuo pipefail

REPO_DIR="${OCR_REPO_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PLATFORM_DIR="${OCR_PLATFORM_DIR:-$REPO_DIR/platform}"
RELEASE_GPG_FINGERPRINT="${RELEASE_GPG_FINGERPRINT:-68A817762C831475F00DB54E775050A4C4921814}"
DEPLOY_VERIFY_URL="${DEPLOY_VERIFY_URL:-https://localhost}"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-opencyberrange}"

TAG=""
DRY_RUN=0
SKIP_WIKI=0
SKIP_BACKUP=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tag) TAG="${2:-}"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        --skip-wiki) SKIP_WIKI=1; shift ;;
        --skip-backup) SKIP_BACKUP=1; shift ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done

log() { printf '\n\033[1;34m==>\033[0m %s\n' "$*"; }
fail() { printf '\n\033[1;31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

[[ -d "$REPO_DIR/.git" ]] || fail "Not a git checkout: $REPO_DIR"
[[ -f "$PLATFORM_DIR/docker-compose.prod.yml" ]] || fail "Missing $PLATFORM_DIR/docker-compose.prod.yml"
command -v docker >/dev/null 2>&1 || fail "docker is not installed"
docker compose version >/dev/null 2>&1 || fail "docker compose is not available"
command -v gpg >/dev/null 2>&1 || fail "gpg is required"
command -v python3 >/dev/null 2>&1 || fail "python3 is required"

if [[ -n "$(git -C "$REPO_DIR" status --porcelain --untracked-files=no)" ]]; then
    fail "Tracked files are modified. Commit, stash, or discard them before deploying."
fi

if [[ -z "$TAG" ]]; then
    TAG="$(git -C "$REPO_DIR" tag --list 'v*' --sort=-v:refname | head -n 1)"
fi
[[ -n "$TAG" ]] || fail "No release tag found. Pass --tag."

log "Release $TAG"
if [[ "$DRY_RUN" == "1" ]]; then
    log "Dry run: no checkout, pull, build, or restart"
fi

if [[ "$DRY_RUN" == "0" ]]; then
    log "Fetching tags"
    git -C "$REPO_DIR" fetch --tags origin
fi

log "Verifying the signed release tag"
KEY_HOME="$(mktemp -d)"
trap 'rm -rf "$KEY_HOME"' EXIT
GNUPGHOME="$KEY_HOME" gpg --batch --import "$REPO_DIR/docs/release-signing-key.asc" >/dev/null 2>&1
FINGERPRINT="$(GNUPGHOME="$KEY_HOME" gpg --with-colons --list-keys | awk -F: '/^fpr:/ {print $10; exit}')"
[[ "${FINGERPRINT^^}" == "${RELEASE_GPG_FINGERPRINT^^}" ]] || fail "Release key fingerprint mismatch: ${FINGERPRINT:-none}"
GNUPGHOME="$KEY_HOME" git -C "$REPO_DIR" verify-tag "$TAG" >/dev/null 2>&1 || fail "Tag $TAG is not signed by $RELEASE_GPG_FINGERPRINT"

if [[ "$DRY_RUN" == "0" ]]; then
    log "Checking out $TAG"
    git -C "$REPO_DIR" checkout --detach "$TAG"
fi

# The backend runs as UID 10001 and reads the mounted lab tree directly. Lab
# builds can leave root-owned files behind, so use the Docker group to restore
# read/traverse permissions before the integrity check runs.
if [[ "$DRY_RUN" == "0" ]]; then
    log "Making platform/labs readable by the backend user"
    if command -v docker >/dev/null 2>&1; then
        docker run --rm -v "$REPO_DIR/platform/labs:/labs" alpine:3.20 \
            chmod -R a+rX /labs >/dev/null 2>&1 || \
            chmod -R a+rX "$REPO_DIR/platform/labs" 2>/dev/null || true
    else
        chmod -R a+rX "$REPO_DIR/platform/labs" 2>/dev/null || true
    fi
fi

log "Verifying the supply-chain lock"
(cd "$REPO_DIR" && python3 scripts/supply_chain.py --check \
    --signature supply-chain.lock.json.asc \
    --gpg-public-key docs/release-signing-key.asc \
    --gpg-fingerprint "$RELEASE_GPG_FINGERPRINT")

if [[ "$DRY_RUN" == "1" ]]; then
    log "Would tag rollback images pre-$TAG"
    log "Would back up the database"
    log "Would build and recreate backend and frontend from $PLATFORM_DIR"
    [[ "$SKIP_WIKI" == "1" ]] || log "Would rebuild the wiki volume"
    exit 0
fi

if [[ "$SKIP_BACKUP" == "0" && -x "$REPO_DIR/scripts/backup-production.sh" ]]; then
    log "Backing up the database"
    bash "$REPO_DIR/scripts/backup-production.sh"
fi

if [[ -x "$REPO_DIR/scripts/tag-release-images.sh" ]]; then
    log "Tagging rollback images pre-$TAG"
    bash "$REPO_DIR/scripts/tag-release-images.sh" "pre-$TAG"
fi

COMPOSE=(docker compose \
    --env-file "$PLATFORM_DIR/.env" \
    -f "$PLATFORM_DIR/docker-compose.prod.yml" \
    --project-name "$PROJECT_NAME")
[[ -f "$PLATFORM_DIR/docker-compose.adopt.yml" ]] && COMPOSE+=(-f "$PLATFORM_DIR/docker-compose.adopt.yml")
[[ -f "$PLATFORM_DIR/docker-compose.override.yml" ]] && COMPOSE+=(-f "$PLATFORM_DIR/docker-compose.override.yml")

log "Building backend"
"${COMPOSE[@]}" build backend

log "Building frontend"
"${COMPOSE[@]}" build frontend

log "Recreating backend and frontend"
"${COMPOSE[@]}" up -d backend frontend

if [[ "$SKIP_WIKI" == "0" ]]; then
    log "Rebuilding the wiki volume"
    "${COMPOSE[@]}" --profile tools run --rm wiki-builder
fi

log "Verifying $DEPLOY_VERIFY_URL"
for _ in $(seq 1 30); do
    if curl -fsSk "$DEPLOY_VERIFY_URL/api/version" >/tmp/ocr-deploy-version.json 2>/dev/null; then
        break
    fi
    sleep 2
done

VERSION="$(python3 -c 'import json,sys; print(json.load(open("/tmp/ocr-deploy-version.json"))["version"])' 2>/dev/null || true)"
[[ -n "$VERSION" ]] || fail "Version endpoint did not respond"
EXPECTED="${TAG#v}"
[[ "$VERSION" == "$EXPECTED" ]] || fail "Deployed $VERSION but expected $EXPECTED"

docker exec ocr-frontend nginx -t >/dev/null 2>&1 || fail "nginx configuration test failed"
docker ps --format '{{.Names}}' | grep -qx 'ocr-backend' || fail "ocr-backend is not running"
docker ps --format '{{.Names}}' | grep -qx 'ocr-frontend' || fail "ocr-frontend is not running"

log "Deployment complete: $VERSION"
log "Rollback: retag pre-$TAG images to latest and run: ${COMPOSE[*]} up -d --force-recreate backend frontend"
