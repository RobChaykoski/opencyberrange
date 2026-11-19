#!/usr/bin/env bash
# Seed the dev-only training ecosystem with fake data.
#
#   bash scripts/ecosystem_seed/seed_all.sh
#
# Every record created here is synthetic. Never point this at production.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT/deploy/ecosystem-test"

if [ "${OCR_ENV:-dev}" = "production" ] || [ "${OCR_ENV:-}" = "prod" ]; then
  echo "REFUSING: the training stack must not run against production"
  exit 2
fi

set -a
# shellcheck disable=SC1091
. ./.env
set +a

PYTHON="${PYTHON:-python3}"

echo "== Moodle =="
docker compose exec -T -e TRAINING_PASSWORD="${TRAINING_PASSWORD:-TrainLab!2026#Student}" \
  moodle php /seed/seed_moodle.php

if docker compose --profile assets ps --services --filter status=running | grep -qx netbox; then
  echo "== NetBox =="
  # security-delta: allow possible secret (lab-only token minted inside the container)
  netbox_api_value="$(docker compose exec -T netbox /opt/netbox/netbox/manage.py shell --no-imports \
    -c "from users.models import Token, User; u=User.objects.get(username='admin'); t=Token.objects.create(version=1, user=u); print('NETBOX_TOKEN_VALUE='+t.token)" \
    2>/dev/null | sed -n 's/^NETBOX_TOKEN_VALUE=//p' | tr -d '\r' | tail -n1)"
  if [ -z "$netbox_api_value" ]; then
    echo "could not create a NetBox API token; create one in the NetBox UI and re-run"
    echo "  NETBOX_TOKEN=<token> $PYTHON scripts/ecosystem_seed/seed_netbox.py"
  else
    NETBOX_URL="${NETBOX_URL:-http://${NETBOX_BIND:-127.0.0.1}:${NETBOX_PORT:-8083}}" NETBOX_TOKEN="$netbox_api_value" \
      "$PYTHON" "$ROOT/scripts/ecosystem_seed/seed_netbox.py"
  fi
else
  echo "SKIP: NetBox is not running"
fi

echo "== Ralph =="
if docker compose --profile assets ps --services --filter status=running | grep -qx ralph; then
  echo "Ralph is running. Create the first admin in the web UI, then load fake assets."
  echo "  http://${RALPH_BIND:-127.0.0.1}:${RALPH_PORT:-8084}/"
else
  echo "SKIP: Ralph is not running"
fi

echo "== Fleet =="
if docker compose --profile endpoint ps --services --filter status=running | grep -qx fleet; then
  echo "Fleet is running. Complete first-run setup and enrol fake hosts only."
  echo "  http://${FLEET_BIND:-127.0.0.1}:${FLEET_PORT:-8082}/"
else
  echo "SKIP: Fleet is not running"
fi

echo "== Authentik =="
if docker compose --profile sso ps --services --filter status=running | grep -qx authentik-server; then
  # security-delta: allow exec (seeds the local Authentik training file)
  docker compose exec -T -e TRAINING_PASSWORD="${TRAINING_PASSWORD:-TrainLab!2026#Student}" authentik-server ak shell -c "exec(open('/seed/seed_authentik.py').read())" < /dev/null 2>&1 | grep -E 'Seeded|Groups:|Users:|Error|Traceback' || true
  echo "Authentik training groups and users seeded."
else
  echo "SKIP: Authentik is not running"
fi

echo "Seeding complete."
