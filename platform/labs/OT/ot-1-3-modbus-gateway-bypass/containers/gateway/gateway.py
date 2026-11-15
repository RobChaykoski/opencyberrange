#!/usr/bin/env python3
"""Modbus TCP gateway that filters single-register writes.

The gateway is the only reachable service on the lab network. It forwards
reads to the PLC, allows single-register writes to the "batch counters"
(holding registers 20-29), and rejects single-register writes elsewhere with
an illegal-data-address exception.

The allow-list only inspects function code 0x06. Multi-register writes
(function code 0x10) are forwarded without an address check. That is the flaw
students are meant to find: a gateway that filters one write code is not a
write filter.
"""
import os
import socket
import struct
import threading

PLC_HOST = os.environ.get("PLC_HOST", "plc")
PLC_PORT = int(os.environ.get("PLC_PORT", "502"))
LISTEN_PORT = int(os.environ.get("GATEWAY_PORT", "502"))

ALLOWED_WRITE_START = 20
ALLOWED_WRITE_END = 29


def recv_exact(conn, count):
    data = b""
    while len(data) < count:
        chunk = conn.recv(count - len(data))
        if not chunk:
            raise ConnectionError("connection closed")
        data += chunk
    return data


def exception_response(header, function_code, exception_code):
    transaction, protocol, _length, unit = struct.unpack(">HHHB", header)
    pdu = bytes([function_code | 0x80, exception_code])
    return struct.pack(">HHHB", transaction, protocol, len(pdu) + 1, unit) + pdu


def blocked_write(pdu):
    """Return True when a single-register write falls outside the allow-list."""
    if pdu[0] != 0x06 or len(pdu) < 5:
        return False
    address = struct.unpack(">H", pdu[1:3])[0]
    return not (ALLOWED_WRITE_START <= address <= ALLOWED_WRITE_END)


def handle(client):
    upstream = socket.create_connection((PLC_HOST, PLC_PORT), timeout=10)
    client.settimeout(30)
    upstream.settimeout(30)
    try:
        while True:
            try:
                header = recv_exact(client, 7)
            except (TimeoutError, ConnectionError):
                break
            length = struct.unpack(">H", header[4:6])[0]
            pdu = recv_exact(client, max(length - 1, 1))

            if blocked_write(pdu):
                address = struct.unpack(">H", pdu[1:3])[0]
                print(
                    f"blocked single write to holding register {address}",
                    flush=True,
                )
                client.sendall(exception_response(header, pdu[0], 0x02))
                continue

            upstream.sendall(header + pdu)
            response_header = recv_exact(upstream, 7)
            response_length = struct.unpack(">H", response_header[4:6])[0]
            response_pdu = recv_exact(upstream, max(response_length - 1, 1))
            client.sendall(response_header + response_pdu)
    finally:
        client.close()
        upstream.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", LISTEN_PORT))
    server.listen(16)
    print(
        f"Halcyon Modbus gateway listening on 0.0.0.0:{LISTEN_PORT}, "
        f"upstream {PLC_HOST}:{PLC_PORT}",
        flush=True,
    )
    while True:
        client, _addr = server.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()


if __name__ == "__main__":
    main()
