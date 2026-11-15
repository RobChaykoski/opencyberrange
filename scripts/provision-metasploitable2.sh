#!/bin/bash
# Prepare the Metasploitable 2 qcow2 and build the lab target image.
#
# Metasploitable 2 is a Rapid7 training VM. It is downloaded here, not stored
# in the repository. Check Rapid7's distribution terms before redistributing
# the image or shipping it inside a published container.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="$REPO_DIR/platform/labs/Metasploit/_target"
VM_DIR="${VM_DIR:-$REPO_DIR/platform/lab-images/metasploitable2}"
ZIP="$VM_DIR/metasploitable-linux-2.0.0.zip"
VMDK="$VM_DIR/Metasploitable2-Linux/Metasploitable.vmdk"
QCOW="$VM_DIR/metasploitable2.qcow2"
URL="https://sourceforge.net/projects/metasploitable/files/Metasploitable2/metasploitable-linux-2.0.0.zip/download"
EXPECTED_SHA256="2ae8788e95273eee87bd379a250d86ec52f286fa7fe84773a3a8f6524085a1ff"

mkdir -p "$VM_DIR"

if [ ! -f "$QCOW" ]; then
    if [ ! -f "$ZIP" ]; then
        echo "[prepare] downloading Metasploitable 2"
        curl -L --fail --retry 3 --retry-delay 5 -o "$ZIP" "$URL"
    fi

    actual_sha256=$(sha256sum "$ZIP" | awk '{print $1}')
    if [ "$actual_sha256" != "$EXPECTED_SHA256" ]; then
        echo "[prepare] SHA-256 mismatch for $ZIP" >&2
        echo "  expected: $EXPECTED_SHA256" >&2
        echo "  actual:   $actual_sha256" >&2
        exit 1
    fi

    if [ ! -f "$VMDK" ]; then
        echo "[prepare] extracting $ZIP"
        python3 -m zipfile -e "$ZIP" "$VM_DIR"
    fi

    echo "[prepare] converting VMDK to qcow2"
    qemu-img convert -O qcow2 "$VMDK" "$QCOW"
fi

echo "[build] building ocr-metasploitable2:latest"
BUILD_DIR=$(mktemp -d)
trap 'rm -rf "$BUILD_DIR"' EXIT
cp "$TARGET_DIR/Dockerfile" "$TARGET_DIR/entrypoint.sh" "$BUILD_DIR/"
cp "$QCOW" "$BUILD_DIR/metasploitable2.qcow2"
docker build -t ocr-metasploitable2:latest "$BUILD_DIR"

docker image inspect ocr-metasploitable2:latest \
    --format '{{.RepoTags}} {{.Size}} bytes'
echo "[ok] target image ready"
