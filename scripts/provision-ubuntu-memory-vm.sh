#!/bin/bash
# Build the live-memory target image from a prepared Ubuntu qcow2.
#
# The qcow2 is not committed. See
# platform/labs/Forensics/_ubuntu-memory/README.md for the preparation steps.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="$REPO_DIR/platform/labs/Forensics/_ubuntu-memory"
QCOW="${QCOW:-$REPO_DIR/platform/lab-images/ubuntu-memory/ubuntu-memory.qcow2}"

if [ ! -f "$QCOW" ]; then
    echo "[memory] prepared qcow2 not found: $QCOW" >&2
    echo "[memory] follow the preparation steps in $TARGET_DIR/README.md" >&2
    exit 1
fi

BUILD_DIR=$(mktemp -d)
trap 'rm -rf "$BUILD_DIR"' EXIT
cp "$TARGET_DIR/Dockerfile" "$TARGET_DIR/entrypoint.sh" "$BUILD_DIR/"
cp "$QCOW" "$BUILD_DIR/ubuntu-memory.qcow2"
docker build -t ocr-ubuntu-memory:latest "$BUILD_DIR"

docker image inspect ocr-ubuntu-memory:latest --format '{{.RepoTags}} {{.Size}}'
echo "[ok] live-memory target image ready"
