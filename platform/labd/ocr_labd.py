#!/usr/bin/env python3
"""Host-side lab agent spike.

This is the control-plane boundary proposed in ADR 0007. It exposes a narrow,
token-authenticated API for lab lifecycle and network operations. The spike is
read-only: mutating routes return 501 until the implementation is validated.

Security rules:
- bind to loopback by default;
- require a bearer token for everything except /health;
- never expose arbitrary exec, image build, volume, or host filesystem calls;
- write an audit line for every mutating request and every denial.
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

VERSION = "0.1.0"
MAX_BODY = 64 * 1024
AUDIT_LOCK = threading.Lock()
MUTATING_ROUTES = {"/v1/spawn", "/v1/stop", "/v1/isolation", "/v1/mirror"}


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class LabdHandler(BaseHTTPRequestHandler):
    server_version = f"ocr-labd/{VERSION}"
    protocol_version = "HTTP/1.1"
    token = ""
    audit_log: str | None = None

    def log_message(self, fmt: str, *args) -> None:  # keep the systemd journal quiet
        return

    def _authorized(self) -> bool:
        header = self.headers.get("Authorization", "")
        expected = f"Bearer {self.token}"
        return bool(self.token) and hmac.compare_digest(header, expected)

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _audit(self, action: str, outcome: str, detail: str = "") -> None:
        if not self.audit_log:
            return
        record = {
            "ts": _now(),
            "action": action,
            "outcome": outcome,
            "detail": detail[:300],
            "client": self.client_address[0],
        }
        try:
            with AUDIT_LOCK, open(
                self.audit_log, "a", encoding="utf-8"
            ) as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
        except OSError:
            pass

    def _read_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        if length > MAX_BODY:
            raise ValueError("request body is too large")
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("request body must be JSON") from exc
        if not isinstance(payload, dict):
            raise TypeError("request body must be a JSON object")
        return payload

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, {"status": "ok", "version": VERSION})
            return
        if not self._authorized():
            self._audit("auth", "denied", f"GET {path}")
            self._json(401, {"error": "unauthorized"})
            return
        if path == "/v1/capabilities":
            self._json(
                200,
                {
                    "version": VERSION,
                    "mode": "spike",
                    "read_only": True,
                    "operations": [
                        "spawn",
                        "stop",
                        "status",
                        "ensure_isolation",
                        "mirror_gretap",
                        "logs",
                    ],
                },
            )
            return
        if path.startswith("/v1/status/"):
            self._json(
                501,
                {
                    "error": "not_implemented",
                    "message": "status is reserved for the validated agent",
                },
            )
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if not self._authorized():
            self._audit("auth", "denied", f"POST {path}")
            self._json(401, {"error": "unauthorized"})
            return
        if path not in MUTATING_ROUTES:
            self._json(404, {"error": "not_found"})
            return
        try:
            payload = self._read_body()
        except (TypeError, ValueError) as exc:
            self._audit(path, "rejected", str(exc))
            self._json(400, {"error": "invalid_request", "message": str(exc)})
            return
        self._audit(path, "not_implemented", ",".join(sorted(payload)))
        self._json(
            501,
            {
                "error": "not_implemented",
                "message": (
                    "the spike validates the API boundary only; wire this route "
                    "after the host-agent design is accepted"
                ),
            },
        )


def create_server(
    host: str, port: int, token: str, audit_log: str | None = None
) -> ThreadingHTTPServer:
    handler = type(
        "BoundLabdHandler",
        (LabdHandler,),
        {"token": token, "audit_log": audit_log},
    )
    return ThreadingHTTPServer((host, port), handler)


def _load_token(path: str | None) -> str:
    token = (os.environ.get("OCR_LABD_TOKEN") or "").strip()
    if not token and path:
        try:
            token = Path(path).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise SystemExit(f"cannot read token file {path}: {exc}") from exc
    if not token:
        raise SystemExit("OCR_LABD_TOKEN or --token-file is required")
    return token


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8099)
    parser.add_argument("--token-file", default="/etc/ocr-labd/token")
    parser.add_argument("--audit-log", default="/var/log/ocr-labd/audit.jsonl")
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "::1", "localhost"}:
        parser.error("the spike only binds to loopback")
    token = _load_token(args.token_file)
    audit_log = args.audit_log or None
    if audit_log:
        Path(audit_log).parent.mkdir(parents=True, exist_ok=True)
    server = create_server(args.host, args.port, token, audit_log)
    print(f"ocr-labd {VERSION} listening on {args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
