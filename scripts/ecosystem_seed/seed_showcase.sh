#!/usr/bin/env bash
# One-command seed for the local Moodle LTI 1.3 showcase.
#
#   bash scripts/ecosystem_seed/seed_showcase.sh
#
# The training stack and OpenCyberRange backend must already be running.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="${PYTHON:-python3}"

exec "$PYTHON" "$ROOT/scripts/ecosystem_seed/seed_showcase.py" "$@"
