#!/bin/bash
# Network Tap: streams live PCAP data over TCP port 9999.
# Students connect from their own machine:
#   nc <tap-ip> 9999 | tcpdump -r - -A 'port 80'
#   nc <tap-ip> 9999 | wireshark -k -i -
#   nc <tap-ip> 9999 > capture.pcap

# The tap container is started on the default bridge and then attached to the
# lab network, so the lab interface is not always eth0. Pick the interface that
# carries the lab subnet (10.x) and fall back to eth0 if there is only one.
LAB_IFACE="$(ip -o -4 addr show | awk '$4 ~ /^10\./ {print $2; exit}')"
if [ -z "$LAB_IFACE" ]; then
    LAB_IFACE="eth0"
fi

# Enable promiscuous mode so we see ALL bridge traffic, not just ours
ip link set "$LAB_IFACE" promisc on 2>/dev/null

# BPF filter: exclude our own management traffic (port 9999)
FILTER="not port 9999"

# socat listens on TCP 9999 and forks a tcpdump for each connection.
# -U = packet-buffered output (flush after each packet for real-time streaming)
# -w - = write pcap to stdout (binary pcap format)
exec socat TCP-LISTEN:9999,reuseaddr,fork \
    EXEC:"tcpdump -i ${LAB_IFACE} -U -w - ${FILTER}",nofork
