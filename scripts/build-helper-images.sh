#!/usr/bin/env bash
# Build the pinned helper image used by the backend's Docker network helpers.
#
# The image contains iproute2, iptables, and bridge-utils so helper containers
# never install packages at runtime. The base is digest-pinned in the Dockerfile.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${OCR_NETPROBE_IMAGE:-ocr-lab/netprobe:1.0}"

if ! command -v docker >/dev/null 2>&1; then
    echo "error: docker is not installed or not on PATH" >&2
    exit 1
fi

echo "building helper image ${IMAGE}"
docker build --pull=false -t "$IMAGE" "$ROOT/platform/netprobe"
echo "helper image ready: ${IMAGE}"
