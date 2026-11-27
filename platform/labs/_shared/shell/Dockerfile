FROM alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc

# A tiny browser terminal for command-only labs. This is deliberately much
# lighter than the KasmVNC RangeBox: no X server, no desktop, no VNC.
RUN apk add --no-cache \
        ttyd \
        iputils \
        curl \
        nmap \
        bind-tools

ENV HOME=/tmp
WORKDIR /tmp

EXPOSE 7681

# The credential gates the terminal page; the lab network is already isolated
# per session. The shell runs as root inside this disposable container so ping
# and nmap have the capabilities they need. There is no host mount, no Docker
# socket, and no persistent data.
CMD ["ttyd", "-p", "7681", "-W", "-c", "learner:trailguard", "/bin/sh"]
