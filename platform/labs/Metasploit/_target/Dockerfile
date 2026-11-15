# Metasploitable 2 lab target
#
# The qcow2 is not committed to the repository. Build this image on a
# KVM-capable host with scripts/provision-metasploitable2.sh, which prepares
# the disk and passes the build context from a temporary directory.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        qemu-system-x86 \
        qemu-utils \
        openssh-client \
        sshpass \
        netcat-openbsd \
        socat \
        python3 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY metasploitable2.qcow2 /vm/metasploitable2.qcow2
COPY entrypoint.sh /opt/entrypoint.sh

RUN chmod 0555 /opt/entrypoint.sh \
    && chmod 0444 /vm/metasploitable2.qcow2

EXPOSE 22 21 80 139 445 3306 5432 6200 8180

HEALTHCHECK --interval=15s --timeout=8s --start-period=180s --retries=12 \
    CMD sshpass -p msfadmin ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -o PreferredAuthentications=password -o PubkeyAuthentication=no -o ConnectTimeout=5 msfadmin@127.0.0.1 true || exit 1

ENTRYPOINT ["/opt/entrypoint.sh"]
