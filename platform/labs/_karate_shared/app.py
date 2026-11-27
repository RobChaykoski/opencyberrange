#!/usr/bin/env python3
"""Deterministic JSON target for the Karate API-testing labs.

One image, four modes selected by ``LAB_MODE``:

  first_test   A small jobs API. The flag is in /api/v1/jobs.
  assertions   An echo endpoint used for match and Scenario Outline practice.
               The flag is returned only for the exact value ``karate``.
  auth         A token login and a /me endpoint. The flag is behind a valid
               Bearer token, so the learner must log in once and reuse it.
  negative     A deliberately broken account endpoint (BOLA). The flag is in
               another user's account, which a correct negative test exposes.

Nothing here is real. There is no external network access, no database, and no
randomness: the same request always returns the same response.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

MODE = os.environ.get("LAB_MODE", "first_test")
FLAG = os.environ.get("FLAG", "OCR{karate_flag_not_set}")
COMPANY = os.environ.get("COMPANY", "Northwind Training API")
PORT = int(os.environ.get("PORT", "8080"))
DEMO_USER = os.environ.get("DEMO_USER", "analyst")
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "karate-demo-2026")
DEMO_TOKEN = os.environ.get("DEMO_TOKEN", "northwind-karate-demo-token")

JOBS = [
    {
        "id": 1,
        "title": "Junior API Tester",
        "location": "Remote",
        "team": "Quality Engineering",
    },
    {
        "id": 2,
        "title": "Application Security Analyst",
        "location": "Hybrid",
        "team": "Product Security",
    },
]

PRODUCTS = [
    {"id": "P-100", "name": "Kettle", "price": 24.50, "in_stock": True},
    {"id": "P-200", "name": "Karate Gi", "price": 65.00, "in_stock": True},
    {"id": "P-300", "name": "Focus Mitts", "price": 39.95, "in_stock": False},
]


def json_bytes(payload: dict | list) -> bytes:
    return (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")


def home() -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{COMPANY}</title></head>
<body style="font:16px/1.5 system-ui,sans-serif;max-width:720px;margin:2rem auto">
<h1>{COMPANY}</h1>
<p>Safe training API. Every record is fictional.</p>
<h2>Endpoints</h2>
<ul>
<li><code>GET /api/v1/health</code></li>
<li><code>GET /api/v1/jobs</code></li>
<li><code>GET /api/v1/jobs/{{id}}</code></li>
<li><code>GET /api/v1/products</code></li>
<li><code>GET /api/v1/echo?value=karate</code></li>
<li><code>POST /api/v1/login</code> with JSON username and password</li>
<li><code>GET /api/v1/me</code> with <code>Authorization: Bearer &lt;token&gt;</code></li>
<li><code>GET /api/v1/accounts/{{id}}</code></li>
</ul>
<p>Current lab mode: <code>{MODE}</code></p>
</body></html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "NorthwindTrainingAPI/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        # Keep the container log quiet and deterministic.
        return

    def _send(self, status: int, payload: dict | list | str, content_type: str = "application/json") -> None:
        body = payload.encode("utf-8") if isinstance(payload, str) else json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: int, code: str, detail: str) -> None:
        self._send(status, {"error": code, "detail": detail})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        if path == "/":
            self._send(200, home(), "text/html; charset=utf-8")
            return
        if path == "/api/v1/health":
            self._send(200, {"status": "ok", "service": COMPANY, "mode": MODE})
            return
        if path == "/api/v1/jobs":
            payload: dict = {"jobs": JOBS}
            if MODE == "first_test":
                payload["flag"] = FLAG
                payload["lesson"] = (
                    "Your Karate feature sets the base URL, path, method, and "
                    "status, then matches the first job title."
                )
            self._send(200, payload)
            return
        if path.startswith("/api/v1/jobs/"):
            job_id = path.rsplit("/", 1)[-1]
            job = next((item for item in JOBS if str(item["id"]) == job_id), None)
            if job is None:
                self._error(404, "not_found", "No job with that id.")
            else:
                self._send(200, job)
            return
        if path == "/api/v1/products":
            self._send(200, {"products": PRODUCTS})
            return
        if path == "/api/v1/echo":
            value = (query.get("value") or [""])[0]
            payload = {"value": value, "length": len(value)}
            if MODE == "assertions" and value == "karate":
                payload["flag"] = FLAG
                payload["match"] = "The exact value you sent is the lesson."
            self._send(200, payload)
            return
        if path == "/api/v1/me":
            auth = self.headers.get("Authorization", "")
            if auth != f"Bearer {DEMO_TOKEN}":
                self._error(401, "unauthorized", "A valid Bearer token is required.")
                return
            payload = {
                "username": DEMO_USER,
                "role": "analyst",
                "display_name": "Avery Analyst",
            }
            if MODE == "auth":
                payload["flag"] = FLAG
            self._send(200, payload)
            return
        if path.startswith("/api/v1/accounts/"):
            account_id = path.rsplit("/", 1)[-1]
            if account_id == "1001":
                self._send(
                    200,
                    {"id": 1001, "owner": DEMO_USER, "balance": 1250.00, "currency": "CAD"},
                )
            elif account_id == "1002":
                payload = {
                    "id": 1002,
                    "owner": "manager",
                    "balance": 9800.00,
                    "currency": "CAD",
                }
                if MODE == "negative":
                    payload["flag"] = FLAG
                    payload["lesson"] = (
                        "A correct test expects 403 for another user's account. "
                        "This response proves the check is missing."
                    )
                self._send(200, payload)
            else:
                self._error(404, "not_found", "No account with that id.")
            return

        self._error(404, "not_found", "Unknown path.")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/api/v1/login":
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._error(400, "invalid_json", "Send a JSON object.")
                return
            if (
                str(body.get("username", "")) == DEMO_USER
                and str(body.get("password", "")) == DEMO_PASSWORD
            ):
                self._send(
                    200,
                    {"token": DEMO_TOKEN, "token_type": "bearer", "expires_in": 3600},
                )
            else:
                self._error(401, "invalid_credentials", "Incorrect username or password.")
            return

        self._error(404, "not_found", "Unknown path.")


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()
