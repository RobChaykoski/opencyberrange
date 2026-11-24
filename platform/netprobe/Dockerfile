# Pinned helper image for host-network and lab-network setup.
#
# The backend creates short-lived privileged or host-network containers to read
# host routes, install isolation rules, and configure GRETAP/TC mirrors. Those
# helpers must not run `apk add` at runtime, so the tools are baked in and the
# base is digest-pinned.
FROM alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc

RUN apk add --no-cache \
    iproute2 \
    iptables \
    bridge-utils

CMD ["sleep", "infinity"]
