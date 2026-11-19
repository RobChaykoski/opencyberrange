#!/usr/bin/env bash
# Fetch the official OpenIAM compose stack for the dev-only training lab.
#
# It is intentionally not embedded in this repository: OpenIAM publishes its
# own multi-service compose deployment. Keep it on the dev host and load only
# fake identities and campaigns.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$ROOT/deploy/ecosystem-test/openiam"

if [ -d "$TARGET/.git" ]; then
  echo "OpenIAM test stack already present at $TARGET"
  exit 0
fi

mkdir -p "$TARGET"
git clone --depth 1 https://bitbucket.org/openiam/openiam-docker-compose.git "$TARGET"
echo "OpenIAM test stack fetched to $TARGET"
echo "Read its README, keep it on the dev host, and use fake data only."
