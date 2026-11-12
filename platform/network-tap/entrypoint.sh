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
#
# Exclude port 9999 from the capture.  The client's own connection to this
# service is mirrored into the tap like any other lab traffic, so without the
# filter every capture would contain itself (and the student's tcpdump would
# display the pcap stream as noise).
exec socat -u \
    "SYSTEM:tcpdump -i ${IFACE} -U -n -w - 'not port 9999' 2>/dev/null" \
    TCP-LISTEN:9999,reuseaddr,fork
