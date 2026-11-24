#!/usr/bin/env bash
# Exercise the ocr-labd status/stop path against a disposable container.
#
# Run on a host with Docker access, from the repository root:
#
#   bash scripts/check-labd-harness.sh
#   bash scripts/check-labd-harness.sh --keep
#
# The script creates ocr-lab-harness, starts the agent with --enable-stop, and
# removes both in a trap. It never touches a real lab container.
set -euo pipefail

ROOT="${LABD_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
IMAGE="${LABD_IMAGE:-alpine}"
CONTAINER="ocr-lab-harness"
PORT="${LABD_PORT:-18099}"
AUDIT="$(mktemp -t ocr-labd-harness.XXXXXX.jsonl)"
LOG="$(mktemp -t ocr-labd-harness.XXXXXX.log)"
TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
AGENT_PID=""
KEEP=0

for arg in "$@"; do
    case "$arg" in
        --keep) KEEP=1 ;;
        *) echo "unknown argument: $arg" >&2; exit 2 ;;
    esac
done

cleanup() {
    if [ -n "$AGENT_PID" ]; then
        kill "$AGENT_PID" 2>/dev/null || true
        wait "$AGENT_PID" 2>/dev/null || true
    fi
    if [ "$KEEP" -eq 0 ]; then
        docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
        rm -f "$AUDIT" "$LOG"
    else
        echo "kept: $CONTAINER, $AUDIT, $LOG"
    fi
}
trap cleanup EXIT

require() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "ERROR: $1 is not installed" >&2
        exit 1
    }
}

code() {
    curl -s -o /dev/null -w '%{http_code}' "$@"
}

body() {
    curl -s "$@"
}

require docker
require python3
require curl

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    echo "pulling $IMAGE"
    docker pull "$IMAGE" >/dev/null
fi

docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER" --rm "$IMAGE" sleep 300 >/dev/null

echo "starting ocr-labd on 127.0.0.1:$PORT"
OCR_LABD_TOKEN="$TOKEN" python3 "$ROOT/platform/labd/ocr_labd.py" \
    --host 127.0.0.1 --port "$PORT" --enable-stop --audit-log "$AUDIT" \
    >"$LOG" 2>&1 &
AGENT_PID=$!

ready=0
for _ in $(seq 1 20); do
    if [ "$(code "http://127.0.0.1:$PORT/health")" = "200" ]; then
        ready=1
        break
    fi
    sleep 0.25
done
if [ "$ready" -ne 1 ]; then
    echo "FAILED: agent did not start" >&2
    cat "$LOG" >&2 || true
    exit 1
fi

fail() {
    echo "FAILED: $1" >&2
    exit 1
}

[ "$(code "http://127.0.0.1:$PORT/v1/status/harness")" = "401" ] \
    || fail "status without a token was not rejected"
[ "$(code -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:$PORT/v1/status/harness")" = "200" ] \
    || fail "status did not return 200"

status_body="$(body -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:$PORT/v1/status/harness")"
printf '%s' "$status_body" | grep -q '"running": true' \
    || fail "status did not report a running container"

caps="$(body -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:$PORT/v1/capabilities")"
printf '%s' "$caps" | grep -q '"stop"' \
    || fail "capabilities did not report stop"

stop_body="$(body -X POST -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"lab_id":"harness"}' \
    "http://127.0.0.1:$PORT/v1/stop")"
printf '%s' "$stop_body" | grep -q '"stopped": true' \
    || fail "stop did not succeed"

sleep 1
[ "$(code -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:$PORT/v1/status/harness")" = "404" ] \
    || fail "the stopped container was still reported"

[ "$(code -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:$PORT/v1/status/Bad_ID")" = "400" ] \
    || fail "an invalid lab id was not rejected"
[ "$(code -X POST -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"lab_id":"missing"}' \
    "http://127.0.0.1:$PORT/v1/stop")" = "404" ] \
    || fail "stopping a missing container was not rejected"

[ -s "$AUDIT" ] || fail "the audit log is empty"

echo "PASSED: ocr-labd status/stop harness"
