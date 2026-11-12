#!/usr/bin/env python3
"""Network topology node: router, host, or flag service.

The platform injects the node role, its point-to-point links, and an optional
default gateway or static routes. The engine owns addresses; this process only
applies them and starts the services the role needs.

Roles:
  router  - enables IPv4 forwarding; connected routes come from the interfaces
  host    - optional default route via the peer router
  service - host behaviour plus an HTTP flag endpoint and a status endpoint

All roles expose ``GET /status`` on port 8080 with their role and links, and
``sshd`` on 22 for the training user.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

NODE_ID = os.environ.get("OCR_NODE_ID", "node")
ROLE = os.environ.get("OCR_ROLE", "host")
LINKS = json.loads(os.environ.get("OCR_LINKS", "[]"))
GATEWAY = os.environ.get("OCR_GATEWAY", "").strip()
ROUTES = json.loads(os.environ.get("OCR_ROUTES", "[]"))
FLAG = os.environ.get("OCR_FLAG", "").strip()
HTTP_PORT = int(os.environ.get("OCR_HTTP_PORT", "80"))
SSH_USER = os.environ.get("OCR_SSH_USER", "analyst")
SSH_PASSWORD = os.environ.get("OCR_SSH_PASSWORD", "")


def run(*args: str) -> int:
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(
            f"[topology] {' '.join(args)} failed: {result.stderr.strip()}",
            file=sys.stderr,
            flush=True,
        )
    return result.returncode


def configure_ssh() -> None:
    if not SSH_PASSWORD:
        return
    subprocess.run(
        ["id", "-u", SSH_USER],
        capture_output=True,
        check=False,
    )
    if subprocess.run(["id", "-u", SSH_USER], capture_output=True, check=False).returncode != 0:
        run("adduser", "-D", "-s", "/bin/sh", SSH_USER)
    proc = subprocess.run(
        ["chpasswd"],
        input=f"{SSH_USER}:{SSH_PASSWORD}\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        print(f"[topology] chpasswd failed: {proc.stderr.strip()}", file=sys.stderr, flush=True)
    with open("/etc/ssh/sshd_config.d/99-topology.conf", "w", encoding="utf-8") as handle:
        handle.write(
            "PasswordAuthentication yes\n"
            "PermitRootLogin no\n"
            "UsePAM no\n"
            "AllowUsers {user}\n".format(user=SSH_USER)
        )
    run("/usr/sbin/sshd")


def configure_network() -> None:
    if ROLE == "router":
        run("sysctl", "-w", "net.ipv4.ip_forward=1")
    for route in ROUTES:
        to = str(route.get("to") or "").strip()
        via = str(route.get("via") or "").strip()
        if to and via:
            run("ip", "route", "replace", to, "via", via)
    if GATEWAY and ROLE in {"host", "service"}:
        run("ip", "route", "replace", "default", "via", GATEWAY)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args) -> None:  # keep container logs quiet
        return

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib API
        if self.path in {"/status", "/health"}:
            self._send(
                200,
                json.dumps(
                    {
                        "node": NODE_ID,
                        "role": ROLE,
                        "links": LINKS,
                        "routes": ROUTES,
                        "gateway": GATEWAY or None,
                    },
                    sort_keys=True,
                ).encode("utf-8"),
                "application/json",
            )
            return
        if self.path == "/flag" and ROLE == "service" and FLAG:
            self._send(200, (FLAG + "\n").encode("utf-8"), "text/plain; charset=utf-8")
            return
        self._send(404, b"not found\n", "text/plain; charset=utf-8")


def start_servers() -> None:
    status = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    Thread(target=status.serve_forever, daemon=True).start()
    if ROLE == "service":
        flag_server = ThreadingHTTPServer(("0.0.0.0", HTTP_PORT), Handler)
        Thread(target=flag_server.serve_forever, daemon=True).start()


def main() -> int:
    print(
        f"[topology] node={NODE_ID} role={ROLE} links={len(LINKS)}",
        flush=True,
    )
    configure_ssh()
    configure_network()
    start_servers()
    # Keep PID 1 alive; tini forwards signals to this process.
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    raise SystemExit(main())
