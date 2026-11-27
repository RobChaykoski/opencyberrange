#!/usr/bin/env bash
# Verify a lab's baked flag render contract on a host with Docker.
#
# Builds the target image, runs the same entrypoint override the launcher uses,
# and checks that the flag file contains the session value. It does not start
# the platform, the backend, or a lab network.
#
# Usage (from the repository root, on a host with Docker):
#   bash scripts/verify-flag-render.sh <lab-slug> [<lab-slug> ...]
#
# Example:
#   bash scripts/verify-flag-render.sh linux-1-6-version-vulnerability-identification
#
# Requires bash, docker, and python3 (for `docker compose config`).

set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABS_DIR="${LABS_DIR:-$ROOT/platform/labs}"
DOCKER="${DOCKER:-docker}"

die() {
  echo "ERROR: $*" >&2
  exit 1
}

field() {
  sed -n "s/^$2:[[:space:]]*//p" "$1" | head -n 1 | sed 's/^"//; s/"$//'
}

command_parts() {
  awk '
    /^flag_command:/ { flag = 1; next }
    flag && /^[[:space:]]*-[[:space:]]*/ {
      sub(/^[[:space:]]*-[[:space:]]*/, "")
      print
      next
    }
    flag { exit }
  ' "$1"
}

verify_lab() {
  local slug="$1"
  local lab
  lab="$(find "$LABS_DIR" -type d -name "$slug" | head -n 1)"
  [ -n "$lab" ] || die "lab not found: $slug"

  local yaml="$lab/lab.yaml"
  [ -f "$yaml" ] || die "$slug: missing lab.yaml"

  local path service
  path="$(field "$yaml" flag_path)"
  service="$(field "$yaml" flag_service)"
  [ -n "$path" ] || die "$slug: missing flag_path"
  [ -n "$service" ] || die "$slug: missing flag_service"

  local mode static_flag
  mode="$(field "$yaml" flag_mode)"
  static_flag="$(field "$yaml" flag)"
  [ -n "$mode" ] || mode="write"

  local -a cmd=()
  while IFS= read -r part; do
    [ -n "$part" ] && cmd+=("$part")
  done < <(command_parts "$yaml")
  [ "${#cmd[@]}" -gt 0 ] || die "$slug: missing flag_command"

  local compose="$lab/docker-compose.yml"
  [ -f "$compose" ] || die "$slug: missing docker-compose.yml"

  local context dockerfile
  context="$($DOCKER compose -f "$compose" config --format json | python3 -c '
import json, sys
service = sys.argv[1]
data = json.load(sys.stdin)
build = (data.get("services", {}).get(service) or {}).get("build") or {}
if isinstance(build, str):
    build = {"context": build}
print(build.get("context") or "")
' "$service")"
  dockerfile="$($DOCKER compose -f "$compose" config --format json | python3 -c '
import json, sys
service = sys.argv[1]
data = json.load(sys.stdin)
build = (data.get("services", {}).get(service) or {}).get("build") or {}
if isinstance(build, str):
    build = {"context": build}
print(build.get("dockerfile") or "Dockerfile")
' "$service")"
  [ -n "$context" ] || die "$slug: service $service has no build context"

  case "$context" in
    /*) ;;
    *) context="$(cd "$lab" && cd "$context" && pwd)" ;;
  esac
  case "$dockerfile" in
    /*) ;;
    *) dockerfile="$context/$dockerfile" ;;
  esac
  [ -f "$dockerfile" ] || die "$slug: missing Dockerfile at $dockerfile"

  local tag="ocr-flagverify-${slug//[^a-zA-Z0-9]/-}"
  local name="flagverify-${slug//[^a-zA-Z0-9]/-}"
  local testflag="OCR{verify_${slug//[^a-zA-Z0-9]/_}}"

  local exec_cmd=""
  local part
  for part in "${cmd[@]}"; do
    exec_cmd+=" $(printf '%q' "$part")"
  done

  local parent
  parent="$(dirname "$path")"
  local render_cmd
  if [ "$mode" = "replace" ] && [ -n "$static_flag" ]; then
    render_cmd="sed -i \"s#${static_flag}#\$LAB_FLAG#g\" $(printf '%q' "$path")"
  else
    render_cmd="mkdir -p $(printf '%q' "$parent") && printf '%s\\n' \"\$LAB_FLAG\" > $(printf '%q' "$path")"
  fi

  echo "==> $slug"
  $DOCKER build -q -t "$tag" -f "$dockerfile" "$context" >/dev/null
  $DOCKER rm -f "$name" >/dev/null 2>&1 || true
  $DOCKER run -d --rm --name "$name" --network none \
    -e LAB_FLAG="$testflag" \
    --entrypoint /bin/sh "$tag" \
    -c "$render_cmd; exec$exec_cmd" \
    >/dev/null
  sleep 2

  local got=""
  got="$($DOCKER exec "$name" grep -oF "$testflag" "$path" 2>/dev/null | head -n1 || true)"
  $DOCKER rm -f "$name" >/dev/null 2>&1 || true
  $DOCKER rmi "$tag" >/dev/null 2>&1 || true

  if [ "$got" = "$testflag" ]; then
    echo "PASS $slug"
    return 0
  fi
  echo "FAIL $slug: expected '$testflag', got '$got'" >&2
  return 1
}

[ "$#" -gt 0 ] || die "usage: $0 <lab-slug> [<lab-slug> ...]"

failed=0
for slug in "$@"; do
  verify_lab "$slug" || failed=$((failed + 1))
done

if [ "$failed" -ne 0 ]; then
  echo "$failed lab(s) failed" >&2
  exit 1
fi
echo "All flag-render checks passed"
