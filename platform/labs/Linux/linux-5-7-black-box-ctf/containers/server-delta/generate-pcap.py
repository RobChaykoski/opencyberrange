#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
# This build-time generator imports Scapy (GPL-2.0-only), so it is
# distributed under GPL-2.0-only. Its generated PCAP output is data and is
# not a derivative work of Scapy.
"""Generate evidence PCAP for server-delta with HTTP POST containing token."""

from scapy.all import IP, TCP, Raw, wrpcap

# Create raw TCP packets with HTTP payload
pkt = (
    IP(src="10.30.1.105", dst="10.30.1.50")
    / TCP(sport=54321, dport=80, flags="PA")
    / Raw(
        load=(
            "POST /upload HTTP/1.1\r\n"
            "Host: 10.30.1.50\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n"
            "\r\n"
            "token=pwn&data=classified"
        )
    )
)

wrpcap("/home/analyst/evidence/traffic.pcap", [pkt])
print("PCAP generated successfully.")
