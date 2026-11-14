#!/usr/bin/env bash
# Production health check for the platform, workbook origin, disk, backups,
# and TLS certificate. Exits non-zero and alerts on failure.
#
# Optional config file: ~/.ocr-monitor.env
#   ALERT_WEBHOOK_URL=https://hooks.slack.com/services/...   (Slack-compatible)
#   DISK_MIN_GB=10
#   BACKUP_MAX_HOURS=26
set -uo pipefail

STATE_DIR="${STATE_DIR:-$HOME/.local/state/ocr-monitor}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
DISK_MIN_GB="${DISK_MIN_GB:-10}"
BACKUP_MAX_HOURS="${BACKUP_MAX_HOURS:-26}"
CERT_FILE="${CERT_FILE:-$HOME/opencyberrange/platform/certs/selfsigned.crt}"

# shellcheck disable=SC1090
[ -f "$HOME/.ocr-monitor.env" ] && source "$HOME/.ocr-monitor.env"

mkdir -p "$STATE_DIR"
issues=()
now=$(date -u +%s)

check_version() {
  curl -sk --max-time 10 https://127.0.0.1/api/version | grep -q '"version":"5"' \
    || issues+=("api-version")
}

check_health() {
  curl -sf --max-time 10 http://127.0.0.1:8000/health | grep -q '"status":"healthy"' \
    || issues+=("backend-health")
}

check_workbook() {
  local code
  code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 https://127.0.0.1:8443/wiki/ || echo 000)
  [ "$code" = "200" ] || [ "$code" = "302" ] || issues+=("workbook-8443")
}

check_containers() {
  local name status
  for name in ocr-backend ocr-frontend ocr-db ocr-valkey; do
    status=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$name" 2>/dev/null || echo missing)
    [ "$status" = "healthy" ] || [ "$status" = "running" ] || issues+=("container:$name=$status")
  done
}

check_disk() {
  local free_gb
  free_gb=$(df -Pk / | awk 'NR==2 {printf "%d", $4/1024/1024}')
  [ "$free_gb" -ge "$DISK_MIN_GB" ] || issues+=("disk=${free_gb}GB")
}

check_backup() {
  local latest age_h
  latest=$(find "$BACKUP_DIR" -maxdepth 1 -name 'ocr-backup-*.dump' -printf '%T@\n' 2>/dev/null | sort -nr | head -1)
  if [ -z "$latest" ]; then
    issues+=("backup-missing")
    return
  fi
  age_h=$(( (now - ${latest%.*}) / 3600 ))
  [ "$age_h" -le "$BACKUP_MAX_HOURS" ] || issues+=("backup-age=${age_h}h")
}

check_offsite() {
  local latest age_h
  latest=$(ssh -o BatchMode=yes -o ConnectTimeout=6 ocr-offsite \
    "find ~/backups/prod -maxdepth 1 -name 'ocr-backup-*.dump.gpg' -printf '%T@\\n' 2>/dev/null | sort -nr | head -1" 2>/dev/null) || {
    issues+=("offsite-unreachable")
    return
  }
  if [ -z "$latest" ]; then
    issues+=("offsite-backup-missing")
    return
  fi
  age_h=$(( (now - ${latest%.*}) / 3600 ))
  [ "$age_h" -le "$BACKUP_MAX_HOURS" ] || issues+=("offsite-age=${age_h}h")
}

check_cert() {
  [ -f "$CERT_FILE" ] || { issues+=("cert-missing"); return; }
  openssl x509 -checkend 2592000 -noout -in "$CERT_FILE" >/dev/null 2>&1 \
    || issues+=("cert-expires-30d")
}

check_version
check_health
check_workbook
check_containers
check_disk
check_backup
check_offsite
check_cert

if [ ${#issues[@]} -gt 0 ]; then
  msg="OCR production check failed: ${issues[*]}"
  echo "[$(date -u +%FT%TZ)] FAIL $msg"
  if [ -n "${ALERT_WEBHOOK_URL:-}" ]; then
    payload=$(python3 -c 'import json,sys; print(json.dumps({"text": sys.argv[1]}))' "$msg")
    curl -sS --max-time 10 -X POST -H 'Content-Type: application/json' \
      --data "$payload" "$ALERT_WEBHOOK_URL" >/dev/null || true
  fi
  printf '{"ok":false,"checked_at":%s,"issues":%s}\n' "$now" \
    "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "${issues[@]}")" \
    > "$STATE_DIR/status.json"
  exit 1
fi

printf '{"ok":true,"checked_at":%s,"issues":[]}\n' "$now" > "$STATE_DIR/status.json"
echo "[$(date -u +%FT%TZ)] OK"
