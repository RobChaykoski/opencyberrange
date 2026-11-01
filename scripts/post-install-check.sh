#!/usr/bin/env bash
# Read-only post-install health check for a running OpenCyberRange deployment.
#
# Runs the runtime-only checks from verify-upgrade.sh: containers, database,
# schema drift, users, labs, RangeBox images, health endpoints, and disk.
# It does not check Git state and does not write to the database.
#
# Usage:
#   bash scripts/post-install-check.sh
#   bash scripts/post-install-check.sh --repo /path/to/deployment
#
# Exit codes: 0 = healthy, 1 = one or more blocking failures.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/verify-upgrade.sh" --runtime-only "$@"
