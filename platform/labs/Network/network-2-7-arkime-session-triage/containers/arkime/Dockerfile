# Arkime 6.9.2 on Debian 13. The release .deb is pinned by SHA-256 so the
# lab build fails if the artefact changes. Viewer and offline capture only;
# the seed PCAP is synthetic and no live interface is captured.
FROM debian:13-slim@sha256:8aa5a7bf5a1955bddbe7d74fcdd0b91ab30e74362a8b73af672b0481b35b44a0

ENV DEBIAN_FRONTEND=noninteractive

ARG ARKIME_VERSION=6.9.2
ARG ARKIME_BUILD=6.9.2-1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        iproute2 \
        procps \
        python3 \
        python3-scapy \
    && rm -rf /var/lib/apt/lists/*

RUN arch="$(dpkg --print-architecture)" \
    && case "$arch" in \
        amd64) deb="arkime_${ARKIME_BUILD}.debian13_amd64.deb"; sha="9a4a0f5500d0d2440cf25a763df590be46340fdc60c7d64c34655ff950268b19" ;; \
        arm64) deb="arkime_${ARKIME_BUILD}.debian13_arm64.deb"; sha="5a0dba06b22510c3fcb722daeb86dcb54705ad4bc0eab89932f430ef507279a4" ;; \
        *) echo "unsupported architecture: $arch" >&2; exit 1 ;; \
    esac \
    && curl -fsSL -o "/tmp/${deb}" "https://github.com/arkime/arkime/releases/download/v${ARKIME_VERSION}/${deb}" \
    && echo "${sha}  /tmp/${deb}" | sha256sum -c - \
    && apt-get update \
    && apt-get install -y --no-install-recommends "/tmp/${deb}" \
    && rm -f "/tmp/${deb}" \
    && rm -rf /var/lib/apt/lists/*

COPY config.ini /opt/arkime/etc/config.ini
COPY seed_pcap.py /opt/arkime/seed_pcap.py
COPY entrypoint.sh /entrypoint.sh

RUN chmod 0755 /entrypoint.sh \
    && mkdir -p /opt/arkime/raw /opt/arkime/logs \
    && groupadd --system --gid 10001 arkime \
    && useradd --system --uid 10001 --gid arkime --home-dir /opt/arkime --no-create-home --shell /bin/bash arkime \
    && chown -R arkime:arkime /opt/arkime/raw /opt/arkime/logs

USER arkime

EXPOSE 8005

ENTRYPOINT ["/entrypoint.sh"]
