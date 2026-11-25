#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build the synthetic packet capture for the Arkime session-triage lab.

The capture is generated at container start with by-scapy and contains only
documentation ranges. It is intentionally small: DNS answers, one benign HTTP
session, one suspicious HTTP session and a second outbound POST.
"""

from __future__ import annotations

import sys
import time

from scapy.all import DNS, DNSQR, DNSRR, Ether, IP, Raw, TCP, UDP, wrpcap

CLIENT_IP = "10.20.1.105"
CLIENT_MAC = "02:42:0a:14:01:69"
GATEWAY_MAC = "02:42:0a:14:00:01"
DNS_IP = "10.20.0.53"
DNS_MAC = "02:42:0a:14:00:35"
C2_IP = "198.51.100.47"
NORMAL_IP = "192.0.2.10"

# The validator requires the exact flag to appear in a container file. The
# capture only carries the token; the learner wraps it as OCR{<token>}.
FLAG = "OCR{arkime_s3ss10n_tr1ag3}"
TOKEN = FLAG[4:-1]

PACKETS: list = []


def add(packet, timestamp: float) -> None:
    packet.time = timestamp
    PACKETS.append(packet)


def dns_answer(qname: str, answer: str, start: float, txt: bool = False) -> None:
    query = (
        Ether(src=CLIENT_MAC, dst=DNS_MAC)
        / IP(src=CLIENT_IP, dst=DNS_IP)
        / UDP(sport=53000, dport=53)
        / DNS(rd=1, qd=DNSQR(qname=qname))
    )
    response = (
        Ether(src=DNS_MAC, dst=CLIENT_MAC)
        / IP(src=DNS_IP, dst=CLIENT_IP)
        / UDP(sport=53, dport=53000)
        / DNS(
            id=query[DNS].id,
            qr=1,
            aa=1,
            qd=query[DNS].qd,
            an=DNSRR(
                rrname=qname,
                type="TXT" if txt else "A",
                ttl=300,
                rdata=f'"{answer}"' if txt else answer,
            ),
        )
    )
    add(query, start)
    add(response, start + 0.01)


def http_exchange(
    destination: str,
    sport: int,
    host: str,
    path: str,
    request_body: bytes,
    response_body: bytes,
    start: float,
) -> None:
    method = "POST" if request_body else "GET"
    request = (
        f"{method} {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "User-Agent: HeliosFreight-Update/1.0\r\n"
        "Accept: */*\r\n"
        f"Content-Length: {len(request_body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("ascii") + request_body
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(response_body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("ascii") + response_body

    cseq = 100000 + sport
    sseq = 200000 + sport

    def outbound(flags: str, seq: int, ack: int, payload: bytes = b""):
        packet = (
            Ether(src=CLIENT_MAC, dst=GATEWAY_MAC)
            / IP(src=CLIENT_IP, dst=destination)
            / TCP(sport=sport, dport=80, flags=flags, seq=seq, ack=ack)
        )
        return packet / Raw(payload) if payload else packet

    def inbound(flags: str, seq: int, ack: int, payload: bytes = b""):
        packet = (
            Ether(src=GATEWAY_MAC, dst=CLIENT_MAC)
            / IP(src=destination, dst=CLIENT_IP)
            / TCP(sport=80, dport=sport, flags=flags, seq=seq, ack=ack)
        )
        return packet / Raw(payload) if payload else packet

    add(outbound("S", cseq, 0), start)
    add(inbound("SA", sseq, cseq + 1), start + 0.01)
    add(outbound("A", cseq + 1, sseq + 1), start + 0.02)
    add(outbound("PA", cseq + 1, sseq + 1, request), start + 0.03)
    add(inbound("A", sseq + 1, cseq + 1 + len(request)), start + 0.04)
    add(inbound("PA", sseq + 1, cseq + 1 + len(request), response), start + 0.05)
    add(outbound("FA", cseq + 1 + len(request), sseq + 1 + len(response)), start + 0.06)
    add(inbound("FA", sseq + 1 + len(response), cseq + 2 + len(request)), start + 0.07)
    add(outbound("A", cseq + 2 + len(request), sseq + 2 + len(response)), start + 0.08)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: seed_pcap.py <output.pcap>", file=sys.stderr)
        return 2

    start = time.time() - 30

    dns_answer("c2.ocrlab.example", C2_IP, start)
    dns_answer("intranet.ocrlab.example", NORMAL_IP, start + 0.2)
    dns_answer("exfil.ocrlab.example", "helios-dmz", start + 0.4, txt=True)

    http_exchange(
        NORMAL_IP,
        49152,
        "intranet.ocrlab.example",
        "/index.html",
        b"",
        b'{"page":"helios-intranet"}',
        start + 0.5,
    )

    http_exchange(
        C2_IP,
        49153,
        "c2.ocrlab.example",
        f"/collect/{TOKEN}?src=helios-dmz",
        b"",
        b'{"status":"ok"}',
        start + 1.0,
    )

    http_exchange(
        C2_IP,
        49154,
        "c2.ocrlab.example",
        "/upload",
        b"synthetic-exfil-only",
        b'{"status":"received"}',
        start + 1.6,
    )

    wrpcap(sys.argv[1], PACKETS)
    print(f"wrote {len(PACKETS)} packets to {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
