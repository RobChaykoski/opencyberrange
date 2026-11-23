#!/usr/bin/env python3
"""Synthetic Windows service surface for the Multiple Port Discovery lab.

The lab teaches port discovery, not SMB or RDP exploitation. Three listeners
make the target deterministic and fast to build:

    80/tcp    HTTP index and /flag.txt
    445/tcp   SMB-like banner
    3389/tcp  RDP-like banner
"""

from __future__ import annotations

import os
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FLAG = os.environ.get("FLAG", "OCR{mult1pl3_p0rts}")

INDEX = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>FinanceCorp Windows Server</title></head>
<body>
  <h1>FinanceCorp Windows Server</h1>
  <p>Status: reachable.</p>
  <p>The flag is available at <a href="/flag.txt">/flag.txt</a>.</p>
  <p>This host also exposes file sharing and remote desktop ports.</p>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "FinanceCorp/1.0"
    sys_version = ""

    def do_GET(self) -> None:
        if self.path.rstrip("/") == "/flag.txt":
            body = FLAG + "\n"
        elif self.path in ("/", "/index.html"):
            body = INDEX
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


def banner_server(port: int, banner: bytes) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("0.0.0.0", port))
        listener.listen(32)
        print(f"listening on {port}", flush=True)
        while True:
            connection, _ = listener.accept()
            with connection:
                connection.sendall(banner)


def main() -> None:
    for port, banner in (
        (445, b"SMB simulated service\r\n"),
        (3389, b"RDP simulated service\r\n"),
    ):
        threading.Thread(
            target=banner_server, args=(port, banner), daemon=True
        ).start()
    print("listening on 80", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 80), Handler).serve_forever()


if __name__ == "__main__":
    main()
