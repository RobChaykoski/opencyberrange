#!/usr/bin/env bash
# Register the training Moodle as an LTI 1.3 platform and create the tool.
#
# Run on the development host after the Moodle TLS proxy and OCR dev are up:
#   bash scripts/ecosystem_seed/seed_lti.sh
#
# This is dev-only. It never points at production.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MOODLE_CONTAINER="${MOODLE_CONTAINER:-ecosystem-test-moodle-1}"
OCR_CONTAINER="${OCR_CONTAINER:-ocr-backend}"
MOODLE_ISSUER="${MOODLE_ISSUER:-https://moodle.172.16.16.44.sslip.io:9443}"
OCR_PUBLIC_URL="${OCR_PUBLIC_URL:-https://172.16.16.44}"

if [ "${OCR_ENV:-dev}" = "production" ] || [ "${OCR_ENV:-}" = "prod" ]; then
  echo "REFUSING: LTI training seeds are for the development host only"
  exit 2
fi

bash "$ROOT/scripts/ecosystem_seed/trust-training-certs.sh"

output="$(docker exec -e OCR_PUBLIC_URL="$OCR_PUBLIC_URL" "$MOODLE_CONTAINER" php /seed/seed_moodle_lti.php)"
echo "$output"
deployment_id="$(printf '%s\n' "$output" | sed -n 's/.*deployment_id=\([0-9][0-9]*\).*/\1/p' | tail -1)"
if [ -z "$deployment_id" ]; then
  echo "Could not determine the Moodle LTI deployment id"
  exit 1
fi

docker exec -i -w /app \
  -e MOODLE_ISSUER="$MOODLE_ISSUER" \
  -e MOODLE_LTI_DEPLOYMENT_ID="$deployment_id" \
  "$OCR_CONTAINER" python - < "$ROOT/scripts/ecosystem_seed/seed_lti.py"

echo "LTI 1.3 tool and platform registered (deployment $deployment_id)."
