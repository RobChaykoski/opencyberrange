# syntax=docker/dockerfile:1
FROM alpine:3.20

# iproute2 for addressing/routing, openssh for the training shell, python3 for
# the tiny flag/status server. No build toolchain and no shell utilities beyond
# what the node needs.
RUN apk add --no-cache iproute2 openssh python3 nftables tini \
    && ssh-keygen -A \
    && mkdir -p /run/sshd /srv

COPY entrypoint.py /usr/local/bin/topology-node
COPY fwctl /usr/local/bin/fwctl
RUN chmod 0755 /usr/local/bin/topology-node /usr/local/bin/fwctl

EXPOSE 22 8080
ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/topology-node"]
