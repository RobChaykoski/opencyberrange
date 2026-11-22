#!/usr/bin/env bash
# Tag the images used by running platform containers before a rebuild.
#
# Docker replaces the image behind a tag during `docker compose build`, and the
# old image can then be garbage-collected under the containerd image store even
# while its container is running. Tag the images first so a rollback target
# survives the build.
#
# Usage:
#   bash scripts/tag-release-images.sh <suffix> [container...]
#
# Examples:
#   bash scripts/tag-release-images.sh pre-5.31.0
#   bash scripts/tag-release-images.sh pre-5.31.0 ocr-backend ocr-frontend
#
# The suffix becomes the tag on the image reference recorded in each
# container's configuration:
#   opencyberrange-backend   -> opencyberrange-backend:pre-5.31.0
#   ocr-backend:latest       -> ocr-backend:pre-5.31.0
#
# A localhost:5000/name reference keeps its registry port; only a trailing tag
# is stripped. Set FORCE=1 to overwrite an existing tag that points at a
# different image.

set -euo pipefail

SUFFIX="${1:-}"
if [[ -z "$SUFFIX" ]]; then
    echo "usage: $0 <tag-suffix> [container...]" >&2
    exit 2
fi
shift || true
CONTAINERS=("$@")
if [[ ${#CONTAINERS[@]} -eq 0 ]]; then
    CONTAINERS=(ocr-backend ocr-frontend)
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "error: docker is not installed or not on PATH" >&2
    exit 1
fi

status=0
for container in "${CONTAINERS[@]}"; do
    if ! docker inspect "$container" >/dev/null 2>&1; then
        echo "error: container $container does not exist" >&2
        status=1
        continue
    fi

    image_ref=$(docker inspect --format '{{.Config.Image}}' "$container")
    image_id=$(docker inspect --format '{{.Image}}' "$container")

    if ! docker image inspect "$image_id" >/dev/null 2>&1; then
        echo "error: $container uses $image_id, which is not in the local image store." >&2
        echo "       The rollback image cannot be tagged. Rebuild the deployed commit" >&2
        echo "       instead, and tag the running images before the next deploy." >&2
        status=1
        continue
    fi

    reference="${image_ref%%@*}"
    leaf="${reference##*/}"
    if [[ "$leaf" == *:* ]]; then
        repository="${reference%:*}"
    else
        repository="$reference"
    fi
    target="${repository}:${SUFFIX}"

    if existing=$(docker image inspect --format '{{.Id}}' "$target" 2>/dev/null); then
        if [[ "$existing" == "$image_id" ]]; then
            echo "ok: $target already points at $image_id"
            continue
        fi
        if [[ "${FORCE:-0}" != "1" ]]; then
            echo "error: $target already points at $existing; set FORCE=1 to replace it" >&2
            status=1
            continue
        fi
    fi

    docker tag "$image_id" "$target"
    echo "tagged: $target -> $image_id (from $container)"
done

exit "$status"
