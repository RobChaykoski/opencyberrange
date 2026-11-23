#!/usr/bin/env bash
# Register the training Moodle as an LTI 1.3 platform and create the course
# tool plus a pre-linked demo activity.
#
# Run on the development host after Moodle and the OCR backend are up:
#   bash scripts/ecosystem_seed/seed_lti.sh
#
# This is dev-only. It never points at production.
#
# Useful overrides:
#   MOODLE_CONTAINER, OCR_CONTAINER
#   MOODLE_ISSUER, MOODLE_INTERNAL_URL
#   OCR_PUBLIC_URL, OCR_INTERNAL_URL
#   MOODLE_LTI_CLIENT_ID, MOODLE_LTI_COURSE, MOODLE_LTI_LAB_SLUG
#   MOODLE_LTI_ACTIVITY_NAME, MOODLE_LTI_COURSE_TOOL_NAME
#   MOODLE_ALLOW_PRIVATE_LTI_URLS=0 to keep Moodle's cURL SSRF allow-list
#   SKIP_CERT_TRUST=1 to skip the local TLS trust step

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MOODLE_CONTAINER="${MOODLE_CONTAINER:-ecosystem-test-moodle-1}"
if [ -z "${OCR_CONTAINER:-}" ]; then
  if docker inspect --format '{{.State.Running}}' ocr-backend 2>/dev/null | grep -qx true; then
    OCR_CONTAINER=ocr-backend
  elif docker inspect --format '{{.State.Running}}' ocr-r5-backend 2>/dev/null | grep -qx true; then
    OCR_CONTAINER=ocr-r5-backend
  else
    OCR_CONTAINER=ocr-backend
  fi
fi
MOODLE_ISSUER="${MOODLE_ISSUER:?set MOODLE_ISSUER to the Moodle origin}"
MOODLE_INTERNAL_URL="${MOODLE_INTERNAL_URL:-$MOODLE_ISSUER}"
OCR_PUBLIC_URL="${OCR_PUBLIC_URL:?set OCR_PUBLIC_URL to the platform origin}"
OCR_INTERNAL_URL="${OCR_INTERNAL_URL:-$OCR_PUBLIC_URL}"
MOODLE_LTI_CLIENT_ID="${MOODLE_LTI_CLIENT_ID:-ocr-training-client}"
MOODLE_LTI_COURSE="${MOODLE_LTI_COURSE:-OCR-CAP-COHORT}"
MOODLE_LTI_COURSE_TOOL_NAME="${MOODLE_LTI_COURSE_TOOL_NAME:-OpenCyberRange Showcase}"
MOODLE_LTI_ACTIVITY_NAME="${MOODLE_LTI_ACTIVITY_NAME:-Avalon Biotech - Suspicious Traffic Analysis}"
MOODLE_LTI_LAB_SLUG="${MOODLE_LTI_LAB_SLUG:-network-1-1-packet-capture-analysis}"
MOODLE_ALLOW_PRIVATE_LTI_URLS="${MOODLE_ALLOW_PRIVATE_LTI_URLS:-1}"
MOODLE_PLATFORM_NAME="${MOODLE_PLATFORM_NAME:-Training Moodle (Showcase)}"

if [ "${OCR_ENV:-dev}" = "production" ] || [ "${OCR_ENV:-}" = "prod" ]; then
  echo "REFUSING: LTI training seeds are for the development host only"
  exit 2
fi

if [ "${SKIP_CERT_TRUST:-0}" != "1" ] && \
   { [ "${MOODLE_ISSUER#https://}" != "$MOODLE_ISSUER" ] || \
     [ "${OCR_PUBLIC_URL#https://}" != "$OCR_PUBLIC_URL" ]; }; then
  bash "$ROOT/scripts/ecosystem_seed/trust-training-certs.sh"
fi

output="$(docker exec \
  -u "${MOODLE_SEED_USER:-daemon}" \
  -e OCR_PUBLIC_URL="$OCR_PUBLIC_URL" \
  -e OCR_INTERNAL_URL="$OCR_INTERNAL_URL" \
  -e MOODLE_LTI_CLIENT_ID="$MOODLE_LTI_CLIENT_ID" \
  -e MOODLE_LTI_COURSE="$MOODLE_LTI_COURSE" \
  -e MOODLE_LTI_COURSE_TOOL_NAME="$MOODLE_LTI_COURSE_TOOL_NAME" \
  -e MOODLE_LTI_ACTIVITY_NAME="$MOODLE_LTI_ACTIVITY_NAME" \
  -e MOODLE_LTI_LAB_SLUG="$MOODLE_LTI_LAB_SLUG" \
  -e MOODLE_ALLOW_PRIVATE_LTI_URLS="$MOODLE_ALLOW_PRIVATE_LTI_URLS" \
  "$MOODLE_CONTAINER" php /seed/seed_moodle_lti.php)"
printf '%s\n' "$output"

client_id="$(printf '%s\n' "$output" | sed -n 's/^client_id=//p' | tail -1)"
deployment_id="$(printf '%s\n' "$output" | sed -n 's/^deployment_id=//p' | tail -1)"
if [ -z "$deployment_id" ]; then
  echo "Could not determine the Moodle LTI deployment id"
  exit 1
fi
if [ -z "$client_id" ]; then
  echo "Could not determine the Moodle LTI client id"
  exit 1
fi

docker exec -i -w /app \
  -e MOODLE_ISSUER="$MOODLE_ISSUER" \
  -e MOODLE_INTERNAL_URL="$MOODLE_INTERNAL_URL" \
  -e MOODLE_LTI_CLIENT_ID="$client_id" \
  -e MOODLE_LTI_DEPLOYMENT_ID="$deployment_id" \
  -e MOODLE_PLATFORM_NAME="$MOODLE_PLATFORM_NAME" \
  "$OCR_CONTAINER" python - < "$ROOT/scripts/ecosystem_seed/seed_lti.py"

echo "LTI 1.3 course tool and platform registered (deployment $deployment_id)."
echo "Moodle activity: ${MOODLE_ISSUER}/mod/lti/view.php?id=$(printf '%s\n' "$output" | sed -n 's/^cmid=//p' | tail -1)"
