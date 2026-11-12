# Public WebSocket relay (wstunnel server).
#
# The implant connects here with a WebSocket upgrade.  The relay forwards the
# tunnel to the tasking server on the protected segment, so the lab network
# only ever sees the relay half of the conversation.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# Keep this version and the two checksums in step with scripts/setup-wstunnel.sh
# so the lab teaches the same binary the platform ships.
ARG WSTUNNEL_VERSION=10.5.2
ARG WSTUNNEL_SHA256_AMD64=7687e4354e91e856beb8d1d3bbf86f990f4cf752be639ad6d1f21b57c8191cf8
ARG WSTUNNEL_SHA256_ARM64=ce6438391db8a83e22f204ae6cdcc87f96451409b90e76858997bb1a9cd85088

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl ca-certificates; \
    rm -rf /var/lib/apt/lists/*; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
        amd64) sha="${WSTUNNEL_SHA256_AMD64}" ;; \
        arm64) sha="${WSTUNNEL_SHA256_ARM64}" ;; \
        *) echo "unsupported architecture: $arch" >&2; exit 1 ;; \
    esac; \
    url="https://github.com/erebe/wstunnel/releases/download/v${WSTUNNEL_VERSION}/wstunnel_${WSTUNNEL_VERSION}_linux_${arch}.tar.gz"; \
    curl -fsSL --retry 3 "$url" -o /tmp/wstunnel.tar.gz; \
    echo "${sha}  /tmp/wstunnel.tar.gz" | sha256sum -c -; \
    tar -xzf /tmp/wstunnel.tar.gz -C /usr/local/bin wstunnel; \
    rm -f /tmp/wstunnel.tar.gz; \
    chmod 0755 /usr/local/bin/wstunnel; \
    useradd --uid 10001 --gid nogroup --create-home --shell /usr/sbin/nologin ocrlab

COPY entrypoint.sh /entrypoint.sh
RUN chmod 0755 /entrypoint.sh

USER ocrlab
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
