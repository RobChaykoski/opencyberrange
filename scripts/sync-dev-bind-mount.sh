#!/usr/bin/env bash
# Sync a pulled development checkout into the runtime tree.
#
# The development backend is bind-mounted from ~/opencyberrange/backend, while
# the frontend is baked into its image. Run this after `git pull` so source, the
# runtime integrity manifest, and lab permissions are current before the
# containers restart.
#
#   bash scripts/sync-dev-bind-mount.sh [repo-dir]

set -euo pipefail

REPO_DIR="${1:-$HOME/opencyberrange}"
cd "$REPO_DIR"

if [ ! -d platform/backend ] || [ ! -d backend ]; then
  echo "error: $REPO_DIR does not look like a development checkout" >&2
  exit 1
fi

echo "syncing backend source"
rsync -a \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache/' \
  --exclude='backups/' \
  --exclude='app/data/about/' \
  platform/backend/ backend/
rm -f backend/app/models.py backend/app/schemas.py

echo "syncing frontend source"
rsync -a \
  --exclude='node_modules/' \
  --exclude='dist/' \
  --exclude='wiki/' \
  platform/frontend/ frontend/

# Git may recreate modified lab files with the host umask (often 660). The
# backend runs as a different UID and must be able to read every lab.
echo "making lab content readable"
chmod -R a+rX platform/labs 2>/dev/null || true

echo "rebuilding frontend image"
docker compose build frontend

echo "restarting backend and frontend"
# A bind-mount source change does not alter the Compose config, so plain
# `up -d` leaves the old process running with cached imports. Recreate the
# two application containers; the database and proxy stay up.
docker compose up -d --force-recreate backend frontend
echo "development bind mount is current"
