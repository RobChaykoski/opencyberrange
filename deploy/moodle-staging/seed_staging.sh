#!/usr/bin/env bash
# Seed fake demo users/courses into the staging Moodle and apply hardening.
#
#   cd deploy/moodle-staging
#   bash seed_staging.sh
#
# This requires TRAINING_PASSWORD in .env. It refuses the training default and
# the production OpenCyberRange hostname.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"
set -a
# shellcheck disable=SC1091
. ./.env
set +a

if [ "${MOODLE_SITE_URL:-}" = "" ]; then
  echo "REFUSING: MOODLE_SITE_URL is not set"
  exit 2
fi
if printf '%s' "$MOODLE_SITE_URL" | grep -q 'ctfd.swocts.com'; then
  echo "REFUSING: this is the production OpenCyberRange host, not staging"
  exit 2
fi
if [ "${TRAINING_PASSWORD:-}" = "" ]; then
  echo "REFUSING: set a demo-only TRAINING_PASSWORD in .env"
  exit 2
fi
if [ "$TRAINING_PASSWORD" = "TrainLab!2026#Student" ]; then
  echo "REFUSING: do not use the training-lab default password on a public staging site"
  exit 2
fi

echo "== Fake Moodle demo data =="
docker compose exec -T -u daemon \
  -e TRAINING_PASSWORD="$TRAINING_PASSWORD" \
  -e TRAINING_RESET_PASSWORDS=1 \
  moodle php /seed/seed_moodle.php

echo "== Hardening =="
docker compose exec -T -u daemon moodle php /harden.php

echo
echo "Staging Moodle seeded with fake data and hardened."
echo "Do not add production SSO, production tokens, or real learner records."
