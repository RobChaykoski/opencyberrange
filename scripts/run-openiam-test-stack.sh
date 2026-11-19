#!/usr/bin/env bash
# Start the official OpenIAM test stack on a dedicated dev lab host.
#
# OpenIAM deploys as Docker Swarm stacks. This wrapper refuses to initialise
# Swarm automatically because doing so on the shared dev host would change the
# host's Docker mode. Run it only on a host set aside for the identity lab.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$ROOT/deploy/ecosystem-test/openiam"

if [ "${OCR_ENV:-dev}" = "production" ] || [ "${OCR_ENV:-}" = "prod" ]; then
  echo "REFUSING: OpenIAM test stack is for a dev lab host only"
  exit 2
fi

if [ ! -d "$TARGET" ]; then
  bash "$ROOT/scripts/fetch-openiam-test-stack.sh"
fi

state="$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || echo unknown)"
if [ "$state" != "active" ]; then
  cat <<EOF
OpenIAM runs as Docker Swarm stacks; Swarm is not active on this host.

On a dedicated dev lab host only:
  docker swarm init
  cd "$TARGET"
  export OPENIAM_RPROXY_HTTP=1
  ./generate.cert.sh
  ./setup.sh
  ./startup.sh

Then load fake identities and one fake access-review campaign.
Do not initialise Swarm on the shared OpenCyberRange dev host.
EOF
  exit 1
fi

cd "$TARGET"
export OPENIAM_RPROXY_HTTP="${OPENIAM_RPROXY_HTTP:-1}"

if [ ! -f vault.crt ]; then
  echo "Vault certificates are missing. Run ./generate.cert.sh once, then retry."
  exit 1
fi

./setup.sh
./startup.sh
echo "OpenIAM test stack started. Use fake identities and campaigns only."
