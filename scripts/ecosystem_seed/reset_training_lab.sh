#!/usr/bin/env bash
# Reset the dev-only training lab to a clean, seeded state.
#
# Run on the development host:
#   bash scripts/ecosystem_seed/reset_training_lab.sh --yes
#
# This deletes the training Docker volumes. It never touches production.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT/deploy/ecosystem-test"

if [ "${OCR_ENV:-dev}" = "production" ] || [ "${OCR_ENV:-}" = "prod" ]; then
  echo "REFUSING: the training lab reset is for the development host only"
  exit 2
fi

if [ "${1:-}" != "--yes" ]; then
  echo "This deletes all training-lab volumes (Moodle, Authentik, NetBox, Ralph, Fleet)."
  echo "Re-run with --yes to continue."
  exit 1
fi

docker compose --profile sso --profile assets --profile endpoint --profile tls down -v
docker compose up -d
docker compose --profile sso --profile assets --profile endpoint --profile tls up -d

# Fleet needs a clean database initialisation after a volume reset.
docker compose --profile endpoint run --rm -T --entrypoint /bin/sh fleet \
  -c 'fleet prepare db' < /dev/null

bash "$ROOT/scripts/ecosystem_seed/seed_all.sh"

if docker ps --format '{{.Names}}' | grep -qx ocr-backend; then
  bash "$ROOT/scripts/ecosystem_seed/seed_ocr.sh"
  bash "$ROOT/scripts/ecosystem_seed/seed_lti.sh"
else
  echo "SKIP: OCR dev backend is not running; skipped the OCR and LTI seeds"
fi

echo "Training lab reset and seeded. Use fake data only."
