# OpenCyberRange RemnuxBox — Browser-Based REMnux Analysis Desktop
# Architecture: Xvfb + XFCE4 + x11vnc + websockify/noVNC
#
# REMnux is a Linux distribution for malware analysis and reverse engineering.
# The official image is built for CLI use (SSH + GUI-over-SSH tunnel), so this
# layers the same browser-desktop stack as UbuntuBox on top of it. Students
# then reach the REMnux toolkit from the platform's noVNC viewer like any other
# RangeBox image.
#
# Size warning: the base image is ~6 GB compressed and ~14 GB on disk. Build it
# during provisioning (or pull it ahead of time) rather than at first launch.
#
# Build:
#   docker build -t opencyberrange/remnuxbox:noble RemnuxBox/
#
# Run (standalone test):
#   docker run --rm -p 6080:6080 --shm-size=256m opencyberrange/remnuxbox:noble
#   Open http://localhost:6080/vnc.html
#
# The platform resolves the "remnux" shorthand to REMNUX_IMAGE; override that
# env var to point at a different build or registry.

FROM remnux/remnux-distro:noble

# The distro image is built for CLI use; everything below is our desktop layer.
USER root

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    LANG=en_US.UTF-8 \
    MOZ_DISABLE_CONTENT_SANDBOX=1

# ── Layer 1: Desktop environment + VNC stack ────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11-utils \
    xfce4 \
    xfce4-terminal \
    xfce4-taskmanager \
    dbus-x11 \
    x11vnc \
    novnc \
    websockify \
    fonts-liberation \
    fonts-dejavu-core \
    supervisor \
    sudo \
    locales \
    curl wget ca-certificates \
    && sed -i 's/# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && locale-gen \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 2: Browser (Mozilla APT repo; noble's firefox is a snap stub) ──
RUN install -d -m 0755 /etc/apt/keyrings && \
    wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg \
         -O /etc/apt/keyrings/packages.mozilla.org.asc && \
    echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" \
         > /etc/apt/sources.list.d/mozilla.list && \
    printf 'Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000\n' \
         > /etc/apt/preferences.d/mozilla && \
    apt-get update && apt-get install -y firefox \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 2b: Image analysis & steganography extras ─────────────────────
# REMnux already carries a deep forensics toolkit; these packages cover the
# OSINT track's metadata and LSB workflows in the browser desktop.
RUN apt-get update && apt-get install -y --no-install-recommends \
    binwalk foremost libimage-exiftool-perl pngcheck steghide \
    imagemagick ruby ruby-dev zlib1g-dev python3-pil \
    && gem install --no-document zsteg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Layer 3: Desktop account ────────────────────────────────────────────
# The distro ships a "remnux" user whose home holds the toolchain, so keep it
# as the desktop account: PATH, virtualenvs and tool config behave exactly as
# in the upstream image. Only sudo is added.
RUN id -u remnux >/dev/null 2>&1 || useradd -m -s /bin/bash remnux
RUN usermod -aG sudo remnux
RUN printf 'remnux ALL=(ALL) NOPASSWD:ALL\n' > /etc/sudoers.d/90-remnux \
    && chmod 0440 /etc/sudoers.d/90-remnux

COPY supervisord.conf /etc/supervisor/conf.d/remnuxbox.conf
COPY entrypoint.sh /entrypoint.sh
# Normalize CRLF from Windows checkouts; a CR in the shebang makes the
# container fail with "exec /entrypoint.sh: no such file or directory".
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# XFCE preferred applications
RUN mkdir -p /home/remnux/.config/xfce4 && \
    echo "TerminalEmulator=xfce4-terminal" > /home/remnux/.config/xfce4/helpers.rc && \
    echo "WebBrowser=firefox"             >> /home/remnux/.config/xfce4/helpers.rc && \
    echo "FileManager=thunar"             >> /home/remnux/.config/xfce4/helpers.rc && \
    chown -R remnux:remnux /home/remnux

EXPOSE 6080

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD curl -sf http://localhost:6080/vnc.html || exit 1

USER remnux
WORKDIR /home/remnux

ENTRYPOINT ["/entrypoint.sh"]
