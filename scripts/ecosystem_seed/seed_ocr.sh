#!/usr/bin/env bash
# Seed the synthetic capstone course into the development OpenCyberRange instance.
#
# Run on the development host, from the repository root:
#   bash scripts/ecosystem_seed/seed_ocr.sh
#
# It refuses to run when the backend reports a production environment.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [ -z "${OCR_BACKEND_CONTAINER:-}" ]; then
  if docker inspect --format '{{.State.Running}}' ocr-backend 2>/dev/null | grep -qx true; then
    OCR_BACKEND_CONTAINER=ocr-backend
  elif docker inspect --format '{{.State.Running}}' ocr-r5-backend 2>/dev/null | grep -qx true; then
    OCR_BACKEND_CONTAINER=ocr-r5-backend
  else
    OCR_BACKEND_CONTAINER=ocr-backend
  fi
fi
# security-delta: allow credential-like assignment (synthetic lab password)
TRAINING_PASSWORD="${TRAINING_PASSWORD:-TrainLab!2026#Student}"

if [ "${OCR_ENV:-dev}" = "production" ] || [ "${OCR_ENV:-}" = "prod" ]; then
  echo "REFUSING: the capstone seed is for the development instance only"
  exit 2
fi

environment="$(docker exec "$OCR_BACKEND_CONTAINER" printenv OCR_ENV 2>/dev/null || true)"
if [ "$environment" = "production" ] || [ "$environment" = "prod" ]; then
  echo "REFUSING: $OCR_BACKEND_CONTAINER reports a production environment"
  exit 2
fi

docker exec -i -w /app -e TRAINING_PASSWORD="$TRAINING_PASSWORD" \
  "$OCR_BACKEND_CONTAINER" python - < "$ROOT/scripts/ecosystem_seed/seed_ocr.py"
