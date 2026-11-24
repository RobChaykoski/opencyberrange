#!/usr/bin/env python3
"""Smoke-check the host-agent spike boundary without a host installation."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

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


def _fake_provider(module):
    class Provider:
        def status(self, lab_id: str):
            if lab_id == "missing":
                return None
            if lab_id == "unavailable":
                raise module.StatusUnavailable("docker is unavailable")
            return {
                "state": "running",
                "running": True,
                "paused": False,
                "restarting": False,
                "oom_killed": False,
                "exit_code": 0,
                "started_at": "2026-11-24T00:00:00Z",
                "finished_at": None,
            }

    return Provider()


def _docker_provider_checks(module) -> None:
    provider = module.DockerStatusProvider(prefix="ocr-lab-")
    running = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=json.dumps(
            {
                "Status": "running",
                "Running": True,
                "Paused": False,
                "Restarting": False,
                "OOMKilled": False,
                "ExitCode": 0,
                "StartedAt": "2026-11-24T00:00:00Z",
                "FinishedAt": "0001-01-01T00:00:00Z",
            }
        ),
        stderr="",
    )
    with mock.patch.object(module.subprocess, "run", return_value=running) as run:
        state = provider.status("linux-1")
        argv = run.call_args.args[0]
    assert state["state"] == "running" and state["running"] is True, state
    assert argv[:2] == ["docker", "inspect"], argv
    assert argv[-1] == "ocr-lab-linux-1", argv

    missing = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="Error: No such object: ocr-lab-missing",
    )
    with mock.patch.object(module.subprocess, "run", return_value=missing):
        assert provider.status("missing") is None

    broken = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="Cannot connect to the Docker daemon",
    )
    with mock.patch.object(module.subprocess, "run", return_value=broken):
        try:
            provider.status("linux-1")
        except module.StatusUnavailable:
            pass
        else:
            raise AssertionError("a docker failure must raise StatusUnavailable")

    with mock.patch.object(
        module.subprocess, "run", side_effect=subprocess.TimeoutExpired([], 5)
    ):
        try:
            provider.status("linux-1")
        except module.StatusUnavailable:
            pass
        else:
            raise AssertionError("a docker timeout must raise StatusUnavailable")


def main() -> int:
    module = _load()
    _docker_provider_checks(module)

    server = module.create_server(
        "127.0.0.1",
        0,
        TOKEN,
        audit_log=None,
        status_provider=_fake_provider(module),
    )
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
        assert "status" in body["implemented"], body
        assert "spawn" in body["pending"], body
        assert body["read_only"] is True

        status, body = _request(port, "/v1/status/linux-1", TOKEN)
        assert status == 200 and body["state"] == "running", (status, body)
        assert body["lab_id"] == "linux-1", body

        status, _body = _request(port, "/v1/status/missing", TOKEN)
        assert status == 404, status

        status, _body = _request(port, "/v1/status/unavailable", TOKEN)
        assert status == 503, status

        status, _body = _request(port, "/v1/status/..%2fetc", TOKEN)
        assert status == 400, status

        status, _body = _request(port, "/v1/status/Linux-1", TOKEN)
        assert status == 400, status

        status, _body = _request(port, "/v1/status/linux-1")
        assert status == 401, status

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
    print("OK: ocr-labd boundary, status, and auth checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
