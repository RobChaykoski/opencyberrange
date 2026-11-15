#!/usr/bin/env bash
# Build the workbook wiki into the compose wiki_data volume.
#
# The builder image is pinned to the same MkDocs/Material versions as the docs
# toolchain. The repository is mounted read-only; only the output volume is
# written. Run this after changing Workbook/, wikis.yaml, or mkdocs-*.yml.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLATFORM_DIR="$REPO_DIR/platform"

ENV_FILE="${WIKI_ENV_FILE:-$PLATFORM_DIR/.env}"
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="$REPO_DIR/.env"
fi
if [ ! -f "$ENV_FILE" ]; then
    echo "error: a platform .env is required (checked $PLATFORM_DIR/.env and $REPO_DIR/.env)" >&2
    exit 1
fi

cd "$PLATFORM_DIR"
COMPOSE=(docker compose --env-file "$ENV_FILE")
if [ -z "${COMPOSE_PROJECT_NAME:-}" ]; then
    COMPOSE_PROJECT_NAME=$(docker inspect ocr-frontend \
        --format '{{index .Config.Labels "com.docker.compose.project"}}' 2>/dev/null || true)
fi
if [ -n "${COMPOSE_PROJECT_NAME:-}" ]; then
    COMPOSE+=(-p "$COMPOSE_PROJECT_NAME")
fi
COMPOSE+=(-f docker-compose.prod.yml)
[ -f docker-compose.adopt.yml ] && COMPOSE+=(-f docker-compose.adopt.yml)
[ -f docker-compose.override.yml ] && COMPOSE+=(-f docker-compose.override.yml)
COMPOSE+=(--profile tools run --rm wiki-builder)

echo "[*] building workbook wiki into the wiki_data volume"
"${COMPOSE[@]}"
