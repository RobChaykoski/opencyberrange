#!/usr/bin/env python3
"""Smoke-check the host-agent spike boundary without a host installation."""

from __future__ import annotations

import importlib.util
import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "platform" / "labd" / "ocr_labd.py"
TOKEN = "labd-spike-test-token"  # test-only credential; security-delta: allow


def _load():
    spec = importlib.util.spec_from_file_location("ocr_labd", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _request(port: int, path: str, token: str | None = None, method: str = "GET"):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = b"{}" if method == "POST" else None
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        headers=headers,
        data=data,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def main() -> int:
    module = _load()
    server = module.create_server("127.0.0.1", 0, TOKEN, audit_log=None)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _request(port, "/health")
        assert status == 200 and body["status"] == "ok", (status, body)

        status, _body = _request(port, "/v1/capabilities")
        assert status == 401, status

        status, body = _request(port, "/v1/capabilities", TOKEN)
        assert status == 200, (status, body)
        assert "spawn" in body["operations"]
        assert body["read_only"] is True

        status, _body = _request(port, "/v1/spawn", TOKEN, "POST")
        assert status == 501, status
        status, _body = _request(port, "/v1/spawn", None, "POST")
        assert status == 401, status
        status, _body = _request(port, "/v1/unknown", TOKEN)
        assert status == 404, status
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print("OK: ocr-labd spike boundary and auth checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
