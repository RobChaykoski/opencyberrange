#!/usr/bin/env bash
# Validate the dev-only training ecosystem stack.
#
# Run from the repository root on the DEV host only:
#   bash scripts/validate-ecosystem-test.sh
#
# This script never talks to production. It only calls 127.0.0.1 ports declared
# in deploy/ecosystem-test/.env.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/deploy/ecosystem-test"

if [ "${OCR_ENV:-dev}" = "production" ] || [ "${OCR_ENV:-}" = "prod" ]; then
  echo "REFUSING: the training stack must not run against production"
  exit 2
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "created deploy/ecosystem-test/.env from .env.example; replace the lab passwords"
fi

set -a
# shellcheck disable=SC1091
. ./.env
set +a

MOODLE_PORT="${MOODLE_PORT:-8091}"
AUTHENTIK_PORT="${AUTHENTIK_PORT:-9000}"
NETBOX_PORT="${NETBOX_PORT:-8083}"
RALPH_PORT="${RALPH_PORT:-8084}"
FLEET_PORT="${FLEET_PORT:-8082}"
MOODLE_HOST="${MOODLE_BIND:-127.0.0.1}"
AUTHENTIK_HOST="${AUTHENTIK_BIND:-127.0.0.1}"
NETBOX_HOST="${NETBOX_BIND:-127.0.0.1}"
RALPH_HOST="${RALPH_BIND:-127.0.0.1}"
FLEET_HOST="${FLEET_BIND:-127.0.0.1}"

failures=0
skips=0

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; failures=$((failures + 1)); }
skip() { echo "SKIP: $1"; skips=$((skips + 1)); }

http_code() {
  local code
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$1" 2>/dev/null)" || true
  [ -n "$code" ] || code="000"
  printf '%s' "$code"
}

expect_http() {
  local label="$1" url="$2" expected="$3"
  local code
  code="$(http_code "$url")"
  if [ "$code" = "$expected" ]; then
    pass "$label ($code)"
  else
    fail "$label (expected $expected, got $code)"
  fi
}

running() {
  docker compose "$@" ps --services --filter status=running 2>/dev/null
}

echo "== Containers =="
docker compose ps

echo "== Moodle =="
moodle_ok=0
for _ in $(seq 1 30); do
  if [ "$(http_code "http://${MOODLE_HOST}:${MOODLE_PORT}/login/index.php")" = "200" ]; then
    moodle_ok=1
    break
  fi
  sleep 2
done
if [ "$moodle_ok" -eq 1 ]; then
  pass "Moodle login page"
else
  fail "Moodle login page"
fi
moodle_db_root_password="${MOODLE_DB_ROOT_PASSWORD:-change-this-root-password}"
if docker compose exec -T moodle-db /opt/bitnami/mariadb/bin/mariadb-admin -h 127.0.0.1 -uroot -p"${moodle_db_root_password}" ping >/dev/null 2>&1; then
  pass "Moodle database"
else
  fail "Moodle database"
fi

echo "== Authentik (sso profile) =="
if running --profile sso | grep -qx authentik-server; then
  live_code="$(http_code "http://${AUTHENTIK_HOST}:${AUTHENTIK_PORT}/-/health/live/")"
  case "$live_code" in
    200|204) pass "Authentik liveness ($live_code)" ;;
    *) fail "Authentik liveness (got $live_code)" ;;
  esac
  ready_code="$(http_code "http://${AUTHENTIK_HOST}:${AUTHENTIK_PORT}/-/health/ready/")"
  case "$ready_code" in
    200|204) pass "Authentik readiness ($ready_code)" ;;
    *) fail "Authentik readiness (got $ready_code)" ;;
  esac
else
  skip "Authentik profile is not running"
fi

echo "== NetBox (assets profile) =="
if running --profile assets | grep -qx netbox; then
  expect_http "NetBox login" "http://${NETBOX_HOST}:${NETBOX_PORT}/login/" "200"
  api_code="$(http_code "http://${NETBOX_HOST}:${NETBOX_PORT}/api/status/")"
  if [ "$api_code" = "200" ] || [ "$api_code" = "403" ]; then
    pass "NetBox API reachable ($api_code)"
  else
    fail "NetBox API reachable (got $api_code)"
  fi
else
  skip "NetBox is not running"
fi

echo "== Ralph (assets profile) =="
if running --profile assets | grep -qx ralph; then
  code="$(http_code "http://${RALPH_HOST}:${RALPH_PORT}/")"
  if [ "$code" = "200" ] || [ "$code" = "302" ]; then
    pass "Ralph responds ($code)"
  else
    fail "Ralph responds (got $code)"
  fi
else
  skip "Ralph is not running"
fi

echo "== Fleet (endpoint profile) =="
if running --profile endpoint | grep -qx fleet; then
  code="$(http_code "http://${FLEET_HOST}:${FLEET_PORT}/")"
  if [ "$code" = "200" ] || [ "$code" = "302" ] || [ "$code" = "307" ]; then
    pass "Fleet responds ($code)"
  else
    fail "Fleet responds (got $code)"
  fi
  if curl -fsS --max-time 10 "http://${FLEET_HOST}:${FLEET_PORT}/api/v1/fleet/version" >/dev/null 2>&1; then
    pass "Fleet version API"
  else
    skip "Fleet version API needs an API token"
  fi
else
  skip "Fleet is not running"
fi

echo "== Results =="
echo "failures: $failures, skipped: $skips"
if [ "$failures" -ne 0 ]; then
  echo "VALIDATION FAILED"
  exit 1
fi
echo "VALIDATION PASSED"
