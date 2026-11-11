#!/bin/bash
# ==============================================================================
# OpenCyberRange - Fix the WireGuard client-pool route on an existing host
# ==============================================================================
#
# Peers added with `wg set` after wg-quick brought the interface up do not get
# a system route. Return traffic then follows the host's default route instead
# of the tunnel, so the VPN handshakes but lab targets are unreachable.
#
# Run this on an existing deployment after upgrading to the installer that
# writes the route in PostUp/PostDown:
#
#   sudo bash scripts/fix-wireguard-client-route.sh
#
# It is idempotent: it adds the runtime route, backs up wg0.conf, and inserts
# the route into PostUp/PostDown if it is not already present.
# ==============================================================================

set -euo pipefail

WG_INTERFACE="${WG_INTERFACE:-wg0}"
WG_CLIENT_CIDR="${WG_CLIENT_CIDR:-10.255.0.0/16}"
WG_CONF="${WG_CONF:-/etc/wireguard/${WG_INTERFACE}.conf}"

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: run as root (sudo bash $0)" >&2
    exit 1
fi

if ! ip link show "$WG_INTERFACE" >/dev/null 2>&1; then
    echo "ERROR: WireGuard interface ${WG_INTERFACE} not found" >&2
    exit 1
fi

# 1. Make the current process traffic work immediately.
ip route replace "$WG_CLIENT_CIDR" dev "$WG_INTERFACE"
echo "[ok] runtime route: ${WG_CLIENT_CIDR} dev ${WG_INTERFACE}"

# 2. Persist it for the next wg-quick start.
if [ ! -f "$WG_CONF" ]; then
    echo "[warn] ${WG_CONF} not found; runtime route only" >&2
    exit 0
fi

backup="${WG_CONF}.bak-$(date +%Y%m%d%H%M%S)"
cp -a "$WG_CONF" "$backup"
echo "[ok] backup: ${backup}"

if ! grep -q "ip route replace ${WG_CLIENT_CIDR}" "$WG_CONF"; then
    sed -i -E "s#^PostUp[[:space:]]*= #PostUp = ip route replace ${WG_CLIENT_CIDR} dev %i; #" "$WG_CONF"
    echo "[ok] added PostUp route"
else
    echo "[ok] PostUp route already present"
fi

if ! grep -q "ip route del ${WG_CLIENT_CIDR}" "$WG_CONF"; then
    sed -i -E "s#^PostDown[[:space:]]*= #PostDown = ip route del ${WG_CLIENT_CIDR} dev %i 2>/dev/null || true; #" "$WG_CONF"
    echo "[ok] added PostDown route"
else
    echo "[ok] PostDown route already present"
fi

echo "[ok] persisted route in ${WG_CONF}"
