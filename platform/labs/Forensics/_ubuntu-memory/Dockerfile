FROM debian:bookworm-slim@sha256:e67eeead736ff7bbe258ef088bff683635c561b1fcfefad0806c1df4ab49ce0e

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        qemu-system-x86 \
        openssh-client \
        sshpass \
        socat \
        netcat-openbsd \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY ubuntu-memory.qcow2 /vm/ubuntu-memory.qcow2
COPY entrypoint.sh /opt/entrypoint.sh

RUN chmod 0555 /opt/entrypoint.sh \
    && chmod 0444 /vm/ubuntu-memory.qcow2

EXPOSE 22

HEALTHCHECK --interval=20s --timeout=10s --start-period=180s --retries=30 \
    CMD sshpass -p 'Analyst#2026' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PreferredAuthentications=password -o PubkeyAuthentication=no -o ConnectTimeout=5 analyst@127.0.0.1 true || exit 1

ENTRYPOINT ["/opt/entrypoint.sh"]
