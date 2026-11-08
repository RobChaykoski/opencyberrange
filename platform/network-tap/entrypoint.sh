#!/bin/sh
set -eu

# The lab network is attached after the container starts, so eth1 can take a
# moment to appear.  Wait for it before opening the capture stream.
IFACE="${CAPTURE_IFACE:-eth1}"
i=0
while [ ! -e "/sys/class/net/${IFACE}" ] && [ "$i" -lt 60 ]; do
    i=$((i + 1))
    sleep 1
done

if [ ! -e "/sys/class/net/${IFACE}" ]; then
    echo "network-tap: interface ${IFACE} did not appear" >&2
    exit 1
fi

# One tcpdump per client so multiple students can capture concurrently.
# -u keeps the stream unidirectional: a client that half-closes its write
# side (busybox nc does) would otherwise make socat exit and kill tcpdump
# after the 24-byte pcap header.
exec socat -u \
    "SYSTEM:tcpdump -i ${IFACE} -U -n -w - 2>/dev/null" \
    TCP-LISTEN:9999,reuseaddr,fork
