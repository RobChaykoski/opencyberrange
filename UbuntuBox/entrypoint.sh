#!/bin/bash
# UbuntuBox Entrypoint
# Starts: KasmVNC's Xvnc (display + web socket) -> XFCE4 desktop
set -e

RESOLUTION="${RESOLUTION:-1280x800}"
DEPTH="${DEPTH:-24}"
NOVNC_PORT="${NOVNC_PORT:-6080}"
DISPLAY_NUM="${DISPLAY_NUM:-1}"

export DISPLAY=":${DISPLAY_NUM}"
export HOME="/home/student"

echo "[ubuntubox] Starting UbuntuBox..."
echo "[ubuntubox] Resolution: ${RESOLUTION}x${DEPTH}"
echo "[ubuntubox] KasmVNC web port: ${NOVNC_PORT}"

# ── 0. Override shell prompt with platform username if provided ──────
if [ -n "${OCR_USERNAME}" ]; then
    echo "[ubuntubox] Setting prompt username to: ${OCR_USERNAME}"
    # Ubuntu uses bash — override PS1 in .bashrc
    cat >> "${HOME}/.bashrc" << BASHEOF

# OCR: show platform username in prompt
export PS1='\[\033[01;32m\]${OCR_USERNAME}@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
BASHEOF
fi

# ── 1. Start KasmVNC (X server + web socket) ─────────────────────────
echo "[ubuntubox] Starting KasmVNC on display :${DISPLAY_NUM}..."
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
        echo "[ubuntubox] KasmVNC ready."
        break
    fi
    if [ "$i" -eq 20 ]; then
        echo "[ubuntubox] ERROR: KasmVNC failed to start."
        exit 1
    fi
    sleep 0.5
done

# ── 1a. Block Docker gateway IPs to hide host services from nmap ──────
block_gateways() {
    if ! command -v iptables &>/dev/null; then
        echo "[ubuntubox] WARNING: iptables not found, skipping gateway block"
        return 0
    fi
    for iface in $(ip -4 addr show | grep 'inet 10\.' | awk '{print $2}'); do
        gw="$(echo "$iface" | sed 's|\.[0-9]*/.*|.1|')"
        iptables -C OUTPUT -d "$gw" -j DROP 2>/dev/null || \
            iptables -A OUTPUT -d "$gw" -j DROP 2>/dev/null && \
            echo "[ubuntubox] Blocked gateway $gw"
    done
}
block_gateways || echo "[ubuntubox] WARNING: gateway blocking failed (non-fatal)"
# Re-check every 30s in the background for dynamically attached networks
( while true; do sleep 30; block_gateways 2>/dev/null; done ) &

# ── 1b. Ensure XFCE preferred-apps config exists ─────────────────────
mkdir -p "${HOME}/.config/xfce4"
if [ ! -f "${HOME}/.config/xfce4/helpers.rc" ]; then
    cat > "${HOME}/.config/xfce4/helpers.rc" <<'HELPERSRC'
TerminalEmulator=xfce4-terminal
WebBrowser=firefox
FileManager=thunar
HELPERSRC
fi

# ── 2. Start D-Bus session (required by XFCE) ─────────────────────────
eval "$(dbus-launch --sh-syntax)" 2>/dev/null || true

# ── 3. Start XFCE4 desktop ────────────────────────────────────────────
echo "[ubuntubox] Starting XFCE4 desktop..."
startxfce4 &
XFCE_PID=$!

# Wait for desktop to initialize
sleep 3

# ── 4. KasmVNC is already serving the display and WebSocket ──────────
# No password — authentication is handled by FastAPI's WebSocket proxy.
# The KasmVNC port is only reachable inside the Docker network.
echo "[ubuntubox] ✓ UbuntuBox ready. KasmVNC client on port ${NOVNC_PORT}"

cleanup() {
    echo "[ubuntubox] Shutting down..."
    kill "${XFCE_PID}" 2>/dev/null || true
    kill "${XVNC_PID}" 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT

wait "${XVNC_PID}"
