#!/usr/bin/env bash
# Collect host OS/package health and place it where the backend can read it.
# Runs as the deploy user; no root and no new mounts are required.
set -euo pipefail

CONTAINER="${BACKEND_CONTAINER:-ocr-backend}"
TARGET="${TARGET_PATH:-/app/backups/host-health.json}"
TMP="$(mktemp)"

python3 - "$TMP" <<'PY'
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

out_path = sys.argv[1]

def run(cmd):
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=60
        ).stdout.strip()
    except Exception:
        return ""

os_release = {}
try:
    with open("/etc/os-release", encoding="utf-8") as handle:
        for line in handle:
            if "=" not in line:
                continue
            key, value = line.rstrip().split("=", 1)
            os_release[key] = value.strip('"')
except OSError:
    pass

upgradable_lines = [
    line for line in run(["apt", "list", "--upgradable"]).splitlines()
    if line.strip() and not line.startswith("Listing...")
]
security = sum(1 for line in upgradable_lines if "-security" in line)

disk = shutil.disk_usage("/")
payload = {
    "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "hostname": run(["hostname"]),
    "os": os_release.get("PRETTY_NAME") or "",
    "version_id": os_release.get("VERSION_ID") or "",
    "kernel": run(["uname", "-r"]),
    "uptime": run(["uptime", "-p"]),
    "upgradable_packages": len(upgradable_lines),
    "security_updates": security,
    "reboot_required": os.path.exists("/var/run/reboot-required")
    or os.path.exists("/run/reboot-required"),
    "disk_total_gb": round(disk.total / (1024 ** 3), 1),
    "disk_free_gb": round(disk.free / (1024 ** 3), 1),
}
with open(out_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
PY

chmod 644 "$TMP"
docker cp "$TMP" "$CONTAINER:$TARGET" >/dev/null
rm -f "$TMP"
echo "host health written to $CONTAINER:$TARGET"

