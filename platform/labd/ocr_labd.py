#!/usr/bin/env python3
"""Host-side lab agent spike.

This is the control-plane boundary proposed in ADR 0007. It exposes a narrow,
token-authenticated API for lab lifecycle and network operations.

Implemented read-only:

- ``GET /v1/capabilities``
- ``GET /v1/status/<lab_id>``

``POST /v1/stop`` is implemented but disabled unless the operator passes
``--enable-stop``. Spawn, isolation, and mirror operations still return ``501``.
Do not enable a mutation on a host until the lab harness passes.

Security rules:
- bind to loopback by default;
- require a bearer token for everything except /health;
- never expose arbitrary exec, image build, volume, or host filesystem calls;
- validate the lab id before it reaches the runtime;
- write an audit line for every mutation, denial, and failed read.
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
import re
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

VERSION = "0.3.0"
MAX_BODY = 64 * 1024
AUDIT_LOCK = threading.Lock()
MUTATING_ROUTES = {"/v1/spawn", "/v1/isolation", "/v1/mirror"}
LAB_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
STATUS_PREFIX = "/v1/status/"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class RuntimeUnavailable(Exception):
    """The runtime could not answer a request."""


# Kept for callers that imported the old name during the status-only spike.
StatusUnavailable = RuntimeUnavailable


class DockerRuntime:
    """Read-only status and an optional stop through fixed Docker calls.

    The lab id is validated by the handler and the container name is built from
    a fixed prefix. No shell is used and no user-controlled argument reaches the
    command line.
    """

    def __init__(
        self,
        prefix: str = "ocr-lab-",
        timeout: float = 5.0,
        stop_timeout: int = 10,
    ) -> None:
        self.prefix = prefix
        self.timeout = timeout
        self.stop_timeout = stop_timeout

    def _run(self, argv: list[str], timeout: float):
        try:
            return subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                env=os.environ.copy(),
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise RuntimeUnavailable("docker is unavailable") from exc

    def status(self, lab_id: str) -> dict[str, Any] | None:
        name = f"{self.prefix}{lab_id}"
        result = self._run(
            ["docker", "inspect", "--format", "{{json .State}}", name],
            self.timeout,
        )

        if result.returncode != 0:
            stderr = (result.stderr or "").lower()
            if "no such object" in stderr or "no such container" in stderr:
                return None
            raise RuntimeUnavailable("docker inspect failed")

        try:
            state = json.loads(result.stdout)
        except ValueError as exc:
            raise RuntimeUnavailable("docker returned unreadable state") from exc
        if not isinstance(state, dict):
            raise RuntimeUnavailable("docker returned unreadable state")

        exit_code = state.get("ExitCode")
        started_at = state.get("StartedAt")
        finished_at = state.get("FinishedAt")
        return {
            "state": str(state.get("Status") or "unknown"),
            "running": bool(state.get("Running")),
            "paused": bool(state.get("Paused")),
            "restarting": bool(state.get("Restarting")),
            "oom_killed": bool(state.get("OOMKilled")),
            "exit_code": exit_code if isinstance(exit_code, int) else None,
            "started_at": started_at if isinstance(started_at, str) else None,
            "finished_at": finished_at if isinstance(finished_at, str) else None,
        }

    def stop(self, lab_id: str) -> str:
        """Stop a container. Returns ``stopped`` or ``not_found``."""

        name = f"{self.prefix}{lab_id}"
        result = self._run(
            ["docker", "stop", "--time", str(self.stop_timeout), name],
            self.stop_timeout + 10,
        )
        if result.returncode == 0:
            return "stopped"
        stderr = (result.stderr or "").lower()
        if "no such object" in stderr or "no such container" in stderr:
            return "not_found"
        if "is not running" in stderr or "already stopped" in stderr:
            return "stopped"
        raise RuntimeUnavailable("docker stop failed")


# Backwards-compatible name from the status-only spike.
DockerStatusProvider = DockerRuntime


class LabdHandler(BaseHTTPRequestHandler):
    server_version = f"ocr-labd/{VERSION}"
    protocol_version = "HTTP/1.1"
    token = ""
    audit_log: str | None = None
    runtime: DockerRuntime | None = None
    enabled_mutations: frozenset[str] = frozenset()

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

    def _lab_id(self, value: Any) -> str | None:
        if isinstance(value, str) and LAB_ID.match(value):
            return value
        return None

    def _status(self, path: str) -> None:
        lab_id = path[len(STATUS_PREFIX):].strip("/")
        if not LAB_ID.match(lab_id):
            self._audit("status", "rejected", lab_id)
            self._json(
                400,
                {
                    "error": "invalid_lab_id",
                    "message": "lab id must be lower-case letters, digits, and hyphens",
                },
            )
            return
        runtime = self.runtime or DockerRuntime()
        try:
            state = runtime.status(lab_id)
        except RuntimeUnavailable as exc:
            self._audit(f"status:{lab_id}", "unavailable", str(exc))
            self._json(503, {"error": "runtime_unavailable"})
            return
        if state is None:
            self._audit(f"status:{lab_id}", "not_found")
            self._json(404, {"error": "not_found"})
            return
        self._json(200, {"lab_id": lab_id, **state})

    def _stop(self) -> None:
        if "stop" not in self.enabled_mutations:
            self._audit("stop", "disabled")
            self._json(
                501,
                {
                    "error": "not_implemented",
                    "message": (
                        "stop is implemented but disabled; start the agent with "
                        "--enable-stop after the lab harness passes"
                    ),
                },
            )
            return
        try:
            payload = self._read_body()
        except (TypeError, ValueError) as exc:
            self._audit("stop", "rejected", str(exc))
            self._json(400, {"error": "invalid_request", "message": str(exc)})
            return
        lab_id = self._lab_id(payload.get("lab_id"))
        if lab_id is None:
            self._audit("stop", "rejected", "invalid lab_id")
            self._json(
                400,
                {
                    "error": "invalid_lab_id",
                    "message": "lab id must be lower-case letters, digits, and hyphens",
                },
            )
            return
        runtime = self.runtime or DockerRuntime()
        try:
            outcome = runtime.stop(lab_id)
        except RuntimeUnavailable as exc:
            self._audit(f"stop:{lab_id}", "unavailable", str(exc))
            self._json(503, {"error": "runtime_unavailable"})
            return
        if outcome == "not_found":
            self._audit(f"stop:{lab_id}", "not_found")
            self._json(404, {"error": "not_found"})
            return
        self._audit(f"stop:{lab_id}", "stopped")
        self._json(200, {"lab_id": lab_id, "stopped": True})

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
            implemented = ["status"]
            if "stop" in self.enabled_mutations:
                implemented.append("stop")
            pending = [
                operation
                for operation in (
                    "spawn",
                    "stop",
                    "ensure_isolation",
                    "mirror_gretap",
                    "logs",
                )
                if operation not in implemented
            ]
            self._json(
                200,
                {
                    "version": VERSION,
                    "mode": "spike",
                    "read_only": implemented == ["status"],
                    "implemented": implemented,
                    "pending": pending,
                    "enabled_mutations": sorted(self.enabled_mutations),
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
        if path.startswith(STATUS_PREFIX):
            self._status(path)
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if not self._authorized():
            self._audit("auth", "denied", f"POST {path}")
            self._json(401, {"error": "unauthorized"})
            return
        if path == "/v1/stop":
            self._stop()
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
                    "this mutation is not wired yet; validate it against the lab "
                    "harness before enabling it on a host"
                ),
            },
        )


def create_server(
    host: str,
    port: int,
    token: str,
    audit_log: str | None = None,
    runtime: DockerRuntime | None = None,
    enabled_mutations: frozenset[str] | set[str] | None = None,
) -> ThreadingHTTPServer:
    handler = type(
        "BoundLabdHandler",
        (LabdHandler,),
        {
            "token": token,
            "audit_log": audit_log,
            "runtime": runtime,
            "enabled_mutations": frozenset(enabled_mutations or ()),
        },
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
    parser.add_argument("--container-prefix", default="ocr-lab-")
    parser.add_argument(
        "--enable-stop",
        action="store_true",
        help="Enable POST /v1/stop (only after the lab harness passes)",
    )
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "::1", "localhost"}:
        parser.error("the spike only binds to loopback")
    token = _load_token(args.token_file)
    audit_log = args.audit_log or None
    if audit_log:
        Path(audit_log).parent.mkdir(parents=True, exist_ok=True)
    runtime = DockerRuntime(prefix=args.container_prefix)
    enabled = frozenset({"stop"}) if args.enable_stop else frozenset()
    server = create_server(
        args.host, args.port, token, audit_log, runtime, enabled
    )
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
