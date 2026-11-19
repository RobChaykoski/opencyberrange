#!/usr/bin/env bash
# Trust the dev-only TLS certificates between Moodle and OpenCyberRange.
#
# Run on the development host after recreating either container. This is a
# runtime-only trust change; the CAs are not installed in the images.

set -euo pipefail

OCR_CONTAINER="${OCR_CONTAINER:-ocr-backend}"
MOODLE_CONTAINER="${MOODLE_CONTAINER:-ecosystem-test-moodle-1}"
CADDY_CONTAINER="${CADDY_CONTAINER:-ecosystem-test-moodle-proxy-1}"
OCR_HOST="${OCR_HOST:-172.16.16.44}"

if [ "${OCR_ENV:-dev}" = "production" ] || [ "${OCR_ENV:-}" = "prod" ]; then
  echo "REFUSING: the training trust store is for the development host only"
  exit 2
fi

openssl s_client -connect 127.0.0.1:443 -servername "$OCR_HOST" </dev/null 2>/dev/null \
  | openssl x509 -outform PEM > /tmp/ocr-dev.crt
docker cp /tmp/ocr-dev.crt "$MOODLE_CONTAINER:/usr/local/share/ca-certificates/ocr-dev.crt"
docker exec -u root "$MOODLE_CONTAINER" update-ca-certificates

docker exec "$CADDY_CONTAINER" cat /data/caddy/pki/authorities/local/root.crt \
  > /tmp/training-caddy.crt
docker cp /tmp/training-caddy.crt "$OCR_CONTAINER:/usr/local/share/ca-certificates/training-caddy.crt"
docker exec -u root "$OCR_CONTAINER" update-ca-certificates

echo "Trusted the OCR dev certificate in Moodle and the Caddy CA in OCR."
