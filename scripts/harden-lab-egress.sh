#!/usr/bin/env bash
# Harden lab egress: every lab network may reach its own and other lab
# subnets (Docker bridge isolation still blocks cross-lab containers) plus the
# shared target networks, but not the host, platform containers, internet, or
# cloud metadata. Idempotent; intended for the production host.
#
# Modes:
#   (default)   apply the rules
#   --dry-run   print the rule script without running it
#   --audit     report missing or unexpected rules without changing anything
set -euo pipefail

IMAGE="${IMAGE:-opencyberrange/rangebox:lite}"
MGMT_PORTS="${QEMU_MGMT_PORTS:-5700,5900,7100,8006,8004}"
SOURCES=(
  10.50.0.0/16
  10.100.0.0/14
  10.104.0.0/13
  10.112.0.0/12
  10.128.0.0/9
)

MODE=apply
NO_FAIL=0
case "${1:-}" in
  --dry-run) MODE=dry ;;
  --audit) MODE=audit ;;
  --audit-no-fail) MODE=audit; NO_FAIL=1 ;;
  "") ;;
  *) echo "usage: $0 [--dry-run|--audit] [--no-fail]" >&2; exit 2 ;;
esac
if [ "${2:-}" = "--no-fail" ]; then
  NO_FAIL=1
fi

mapfile -t network_ids < <(docker network ls --format '{{.ID}}')

# The rules below are IPv4-only. If any Docker network has IPv6 enabled, the
# containment model has a hole; stop rather than apply a partial policy.
v6_networks=$(for id in "${network_ids[@]}"; do
  docker network inspect "$id" --format '{{.Name}} {{.EnableIPv6}}' 2>/dev/null || true
done | awk '$2 == "true" {print $1}')
if [ -n "$v6_networks" ]; then
  cat >&2 <<EOF
ERROR: Docker network(s) have IPv6 enabled:
$(printf '  %s\n' $v6_networks)
Disable IPv6 on those networks (or add equivalent ip6tables rules) before
relying on lab egress containment.
EOF
  exit 1
fi

if [[ "$IMAGE" != *"@sha256:"* ]]; then
  echo "WARN: $IMAGE is not pinned by digest; a mutable tag can run arbitrary code as root." >&2
  if [ "${HARDEN_STRICT:-0}" = "1" ]; then
    echo "ERROR: HARDEN_STRICT=1 requires a digest-pinned IMAGE." >&2
    exit 1
  fi
fi

rules_file=$(mktemp)
trap 'rm -f "$rules_file"' EXIT
gateways=()
for id in "${network_ids[@]}"; do
  while read -r subnet gateway; do
    [ -n "$subnet" ] || continue
    if [[ "$subnet" =~ ^10\.(50|1[0-9]{2}|2[0-5][0-9])\. ]]; then
      [ -n "$gateway" ] && gateways+=("$gateway")
    fi
  done < <(docker network inspect "$id" --format '{{range .IPAM.Config}}{{.Subnet}} {{.Gateway}}{{"\n"}}{{end}}' 2>/dev/null || true)
done

# Deduplicate gateways.
if [ ${#gateways[@]} -gt 0 ]; then
  mapfile -t gateways < <(printf '%s\n' "${gateways[@]}" | sort -u)
fi

# Expected rules, one `iptables -C` argument list per entry.
expected=()
for src in "${SOURCES[@]}"; do
  expected+=("OCR-LAB-INPUT -s $src -j DROP")
done
for src in "${SOURCES[@]}"; do
  expected+=("DOCKER-USER -s $src -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")
  for gw in "${gateways[@]}"; do
    expected+=("DOCKER-USER -s $src -d $gw -j DROP")
  done
  expected+=("DOCKER-USER -s $src -d 172.30.0.0/16 -p tcp -m multiport --dports $MGMT_PORTS -j DROP")
  expected+=("DOCKER-USER -s $src -d 172.30.0.0/16 -j ACCEPT")
  expected+=("DOCKER-USER -s $src -d 10.150.0.0/24 -j ACCEPT")
  for dst in "${SOURCES[@]}"; do
    expected+=("DOCKER-USER -s $src -d $dst -j ACCEPT")
  done
  expected+=("DOCKER-USER -s $src -d 172.16.0.0/12 -j DROP")
  expected+=("DOCKER-USER -s $src -d 169.254.0.0/16 -j DROP")
  expected+=("DOCKER-USER -s $src -j DROP")
done

# Host-local traffic (SSH and any other listener) never reaches DOCKER-USER,
# so the INPUT drop lives in a dedicated chain.
if [ "$MODE" = "audit" ]; then
  {
    echo 'REQUIRED_CHAIN="OCR-LAB-INPUT"'
    echo 'iptables -C INPUT -j OCR-LAB-INPUT 2>/dev/null || echo "MISSING INPUT -j OCR-LAB-INPUT"'
    for spec in "${expected[@]}"; do
      echo "iptables -C $spec 2>/dev/null || echo \"MISSING $spec\""
    done
    echo 'iptables -S OCR-LAB-INPUT 2>/dev/null | sed -n "s/^-A /RULE:/p"'
    echo 'exit 0'
  } > "$rules_file"
else
  {
    echo "iptables -N OCR-LAB-INPUT 2>/dev/null || true"
    echo "iptables -C INPUT -j OCR-LAB-INPUT 2>/dev/null || iptables -I INPUT 1 -j OCR-LAB-INPUT"
    for spec in "${expected[@]}"; do
      echo "iptables -C $spec 2>/dev/null || iptables -A $spec"
    done
  } > "$rules_file"
fi

if [ "$MODE" = "dry" ]; then
  cat "$rules_file"
  exit 0
fi

if [ "$MODE" = "audit" ]; then
  output=$(docker run --rm -i --privileged --net=host --user 0 \
    --entrypoint sh "$IMAGE" -s < "$rules_file")
  missing=$(printf '%s\n' "$output" | sed -n 's/^MISSING /  /p')
  unexpected=""
  while IFS= read -r line; do
    case "$line" in
      RULE:*) ;;
      *) continue ;;
    esac
    src=$(printf '%s\n' "$line" | sed -n 's/.*-s \([^ ]*\).*/\1/p')
    [ -n "$src" ] || continue
    listed=0
    for expected_src in "${SOURCES[@]}"; do
      [ "$src" = "$expected_src" ] && listed=1 && break
    done
    [ "$listed" = 1 ] || unexpected+="  ${line#RULE:}"$'\n'
  done <<< "$output"

  if [ -z "$missing" ] && [ -z "$unexpected" ]; then
    echo "OK: egress containment matches the expected policy (${#expected[@]} rules)"
    exit 0
  fi

  echo "DRIFT: egress containment differs from the expected policy" >&2
  if [ -n "$missing" ]; then
    echo "Missing rules:" >&2
    printf '%s\n' "$missing" >&2
  fi
  if [ -n "$unexpected" ]; then
    echo "Unexpected OCR-LAB-INPUT sources:" >&2
    printf '%s' "$unexpected" >&2
  fi
  [ "$NO_FAIL" = "1" ] && exit 0
  exit 1
fi

docker run --rm -i --privileged --net=host --user 0 \
  --entrypoint sh "$IMAGE" -s < "$rules_file"

echo "Applied egress rules for ${#SOURCES[@]} lab range(s), ${#gateways[@]} gateway(s)"
