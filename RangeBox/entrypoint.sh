#!/bin/bash
# RangeBox Entrypoint
# Starts: KasmVNC's Xvnc (virtual display + web socket) -> XFCE4 desktop
#
# Privileged network hygiene (gateway DROP rules, dnsmasq, /etc/resolv.conf)
# runs through `sudo -n` because the image's final USER is `kali`. The image
# grants kali NOPASSWD sudo, so this is hygiene inside the student's own box,
# not a security boundary; the host DOCKER-USER policy is the real boundary.
set -e

RESOLUTION="${RESOLUTION:-1280x800}"
DEPTH="${DEPTH:-24}"
VNC_PORT="${VNC_PORT:-5900}"
NOVNC_PORT="${NOVNC_PORT:-6080}"
DISPLAY_NUM="${DISPLAY_NUM:-1}"

export DISPLAY=":${DISPLAY_NUM}"
export HOME="/home/kali"

echo "[rangebox] Starting RangeBox..."
echo "[rangebox] Resolution: ${RESOLUTION}x${DEPTH}"
echo "[rangebox] KasmVNC web port: ${NOVNC_PORT}"

# ── 1. Start KasmVNC (X server + web socket) ──────────────────────────
# KasmVNC replaces Xvfb + x11vnc + websockify: one process owns the display
# and serves the KasmVNC client/WebSocket on NOVNC_PORT.
echo "[rangebox] Starting KasmVNC on display :${DISPLAY_NUM}..."
mkdir -p "${HOME}/.vnc"
Xvnc "${DISPLAY}" \
    -geometry "${RESOLUTION}" \
    -depth "${DEPTH}" \
    -SecurityTypes None \
    -DisableBasicAuth \
    -websocketPort "${NOVNC_PORT}" \
    -sslOnly 0 \
    -interface 0.0.0.0 \
    -AlwaysShared \
    -publicIP 127.0.0.1 \
    -httpd /usr/share/kasmvnc/www &
XVNC_PID=$!

# Wait for the X server to be ready
for i in $(seq 1 20); do
    if xdpyinfo -display "${DISPLAY}" >/dev/null 2>&1; then
        echo "[rangebox] KasmVNC ready."
        break
    fi
    if [ "$i" -eq 20 ]; then
        echo "[rangebox] ERROR: KasmVNC failed to start."
        exit 1
    fi
    sleep 0.5
done

# ── 1a. Block Docker gateway IPs to hide host services from nmap ──────
# Containers have NET_ADMIN; drop outbound to every .1 gateway on 10.x
# subnets.  A background loop re-applies when new interfaces appear
# (e.g. when the platform bridges us to a lab network after boot).
#
# This is hygiene, not a security boundary: the image grants kali NOPASSWD
# sudo, so a student can flush these rules inside their own box. The real
# boundary is the host DOCKER-USER policy in docker_manager.py. This layer
# only keeps casual nmap scans from seeing the frontend, Peer Manager, or DB.
block_gateways() {
    if ! command -v iptables &>/dev/null; then
        echo "[rangebox] WARNING: iptables not found, skipping gateway block"
        return 0
    fi
    local applied=0
    for iface in $(ip -4 addr show | grep 'inet 10\.' | awk '{print $2}'); do
        # OCR lab bridges put the gateway at .254 (docker_manager.py), not .1.
        # Blocking only .1 left the real gateway open, so the attack box could
        # reach the platform frontend and the Peer Manager on <subnet>.254.
        # Drop both the Docker-default .1 and the OCR .254.
        net="$(echo "$iface" | sed 's|\.[0-9]*/.*||')"
        for last in 1 254; do
            gw="${net}.${last}"
            if sudo -n iptables -C OUTPUT -d "$gw" -j DROP 2>/dev/null; then
                applied=$((applied + 1))
            elif sudo -n iptables -A OUTPUT -d "$gw" -j DROP 2>/dev/null; then
                applied=$((applied + 1))
                echo "[rangebox] Blocked gateway $gw"
            fi
        done
    done
    if [ "$applied" -eq 0 ]; then
        echo "[rangebox] WARNING: no gateway DROP rules applied; check sudo/iptables permissions"
    fi
}
block_gateways || echo "[rangebox] WARNING: gateway blocking failed (non-fatal)"

# ── 1b. Start dnsmasq for clean reverse DNS ──────────────────────────
# Docker's embedded DNS (127.0.0.11) returns compose container names
# on PTR queries, leaking exercise slugs into nmap output. dnsmasq
# reads /etc/hosts and serves proper PTR records so reverse lookups
# return friendly names like plc1.masa.local.
_reload_dnsmasq() {
    [ -f /tmp/dnsmasq.pid ] && sudo -n kill -HUP "$(cat /tmp/dnsmasq.pid)" 2>/dev/null
}
if command -v dnsmasq &>/dev/null; then
    DOCKER_DNS="127.0.0.11"
    cat > /tmp/dnsmasq.conf <<DNSCONF
listen-address=127.0.0.1
bind-interfaces
no-resolv
server=${DOCKER_DNS}
expand-hosts
no-negcache
# Do not forward reverse lookups of private (RFC1918) addresses upstream. Without
# this, PTR queries for lab targets were forwarded to Docker's embedded DNS,
# which answered with the compose container name and leaked the exercise slug
# into nmap output. bogus-priv answers those with NXDOMAIN instead, so reverse
# lookups of lab hosts return nothing rather than the slug.
bogus-priv
DNSCONF
    sudo -n dnsmasq -C /tmp/dnsmasq.conf --pid-file=/tmp/dnsmasq.pid 2>/dev/null && {
        echo "nameserver 127.0.0.1" | sudo -n tee /etc/resolv.conf >/dev/null
        echo "[rangebox] dnsmasq started, reverse DNS will use /etc/hosts"
    } || echo "[rangebox] WARNING: dnsmasq failed to start (non-fatal)"
fi

# Re-check gateways and reload dnsmasq every 30s for dynamically attached networks
( while true; do sleep 30; block_gateways 2>/dev/null; _reload_dnsmasq; done ) &

# ── 1c. Ensure XFCE preferred-apps config exists ─────────────────────
# Without this, exo-open --launch TerminalEmulator may open the browser.
mkdir -p "${HOME}/.config/xfce4"
if [ ! -f "${HOME}/.config/xfce4/helpers.rc" ]; then
    cat > "${HOME}/.config/xfce4/helpers.rc" <<'HELPERSRC'
TerminalEmulator=xfce4-terminal
WebBrowser=firefox-esr
FileManager=thunar
HELPERSRC
fi

# ── 2. Start D-Bus session (required by XFCE) ─────────────────────────
eval "$(dbus-launch --sh-syntax)" 2>/dev/null || true

# ── 3. Start XFCE4 desktop ────────────────────────────────────────────
echo "[rangebox] Starting XFCE4 desktop..."
startxfce4 &
XFCE_PID=$!

# Wait for desktop to initialize
sleep 3

# xfdesktop can start before its per-monitor backdrop property exists, leaving
# a black root window. Set every last-image property to the branded wallpaper.
WALLPAPER="/usr/share/backgrounds/ocr-wallpaper.png"
if [ -f "${WALLPAPER}" ] && command -v xfconf-query >/dev/null 2>&1; then
    xfconf-query -c xfce4-desktop -l 2>/dev/null \
        | grep -E 'last-image$' \
        | while read -r prop; do
            xfconf-query -c xfce4-desktop -p "${prop}" -s "${WALLPAPER}" 2>/dev/null || true
        done
fi

# ── 4. KasmVNC is already serving the display and WebSocket ───────────
# No password — authentication is handled by FastAPI's WebSocket proxy.
# The KasmVNC port is only reachable inside the Docker network.
echo "[rangebox] ✓ RangeBox ready. KasmVNC client on port ${NOVNC_PORT}"

# Trap signals for graceful shutdown
cleanup() {
    echo "[rangebox] Shutting down..."
    kill "${XFCE_PID}" 2>/dev/null || true
    kill "${XVNC_PID}" 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT

# Keep the container alive while KasmVNC runs. If Xvnc exits, stop.
wait "${XVNC_PID}"
