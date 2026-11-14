#!/usr/bin/env bash
# Harden lab egress: every lab network may reach its own and other lab
# subnets (Docker bridge isolation still blocks cross-lab containers) plus the
# shared target networks, but not the host, platform containers, internet, or
# cloud metadata. Idempotent; intended for the production host.
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

mapfile -t network_ids < <(docker network ls --format '{{.ID}}')
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

{
  # Host-local traffic (SSH and any other listener on the host) never reaches
  # DOCKER-USER, so drop it in a dedicated INPUT chain.
  echo "iptables -N OCR-LAB-INPUT 2>/dev/null || true"
  echo "iptables -C INPUT -j OCR-LAB-INPUT 2>/dev/null || iptables -I INPUT 1 -j OCR-LAB-INPUT"
  for src in "${SOURCES[@]}"; do
    echo "iptables -C OCR-LAB-INPUT -s $src -j DROP 2>/dev/null || iptables -A OCR-LAB-INPUT -s $src -j DROP"
  done

  for src in "${SOURCES[@]}"; do
    echo "iptables -C DOCKER-USER -s $src -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || iptables -A DOCKER-USER -s $src -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT"
    for gw in "${gateways[@]}"; do
      echo "iptables -C DOCKER-USER -s $src -d $gw -j DROP 2>/dev/null || iptables -A DOCKER-USER -s $src -d $gw -j DROP"
    done
    echo "iptables -C DOCKER-USER -s $src -d 172.30.0.0/16 -p tcp -m multiport --dports $MGMT_PORTS -j DROP 2>/dev/null || iptables -A DOCKER-USER -s $src -d 172.30.0.0/16 -p tcp -m multiport --dports $MGMT_PORTS -j DROP"
    echo "iptables -C DOCKER-USER -s $src -d 172.30.0.0/16 -j ACCEPT 2>/dev/null || iptables -A DOCKER-USER -s $src -d 172.30.0.0/16 -j ACCEPT"
    echo "iptables -C DOCKER-USER -s $src -d 10.150.0.0/24 -j ACCEPT 2>/dev/null || iptables -A DOCKER-USER -s $src -d 10.150.0.0/24 -j ACCEPT"
    for dst in "${SOURCES[@]}"; do
      echo "iptables -C DOCKER-USER -s $src -d $dst -j ACCEPT 2>/dev/null || iptables -A DOCKER-USER -s $src -d $dst -j ACCEPT"
    done
    echo "iptables -C DOCKER-USER -s $src -d 172.16.0.0/12 -j DROP 2>/dev/null || iptables -A DOCKER-USER -s $src -d 172.16.0.0/12 -j DROP"
    echo "iptables -C DOCKER-USER -s $src -d 169.254.0.0/16 -j DROP 2>/dev/null || iptables -A DOCKER-USER -s $src -d 169.254.0.0/16 -j DROP"
    echo "iptables -C DOCKER-USER -s $src -j DROP 2>/dev/null || iptables -A DOCKER-USER -s $src -j DROP"
  done
} | docker run --rm -i --privileged --net=host --user 0 \
      --entrypoint sh "$IMAGE" -s

echo "Applied egress rules for ${#SOURCES[@]} lab range(s), ${#gateways[@]} gateway(s)"
