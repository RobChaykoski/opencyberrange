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


def _request(
    port: int,
    path: str,
    token: str | None = None,
    method: str = "GET",
    payload: dict | None = None,
):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if method == "POST":
        data = json.dumps(payload or {}).encode("utf-8")
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


def _fake_runtime(module):
    class Runtime:
        def status(self, lab_id: str):
            if lab_id == "missing":
                return None
            if lab_id == "unavailable":
                raise module.RuntimeUnavailable("docker is unavailable")
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

        def stop(self, lab_id: str):
            if lab_id == "missing":
                return "not_found"
            if lab_id == "unavailable":
                raise module.RuntimeUnavailable("docker is unavailable")
            return "stopped"

    return Runtime()


def _docker_runtime_checks(module) -> None:
    runtime = module.DockerRuntime(prefix="ocr-lab-")
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
        state = runtime.status("linux-1")
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
        assert runtime.status("missing") is None

    broken = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="Cannot connect to the Docker daemon",
    )
    with mock.patch.object(module.subprocess, "run", return_value=broken):
        try:
            runtime.status("linux-1")
        except module.RuntimeUnavailable:
            pass
        else:
            raise AssertionError("a docker failure must raise RuntimeUnavailable")

    with mock.patch.object(
        module.subprocess, "run", side_effect=subprocess.TimeoutExpired([], 5)
    ):
        try:
            runtime.status("linux-1")
        except module.RuntimeUnavailable:
            pass
        else:
            raise AssertionError("a docker timeout must raise RuntimeUnavailable")


def _docker_stop_checks(module) -> None:
    runtime = module.DockerRuntime(prefix="ocr-lab-", stop_timeout=3)
    success = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="ocr-lab-linux-1\n", stderr=""
    )
    with mock.patch.object(module.subprocess, "run", return_value=success) as run:
        assert runtime.stop("linux-1") == "stopped"
        argv = run.call_args.args[0]
    assert argv == [
        "docker",
        "stop",
        "--time",
        "3",
        "ocr-lab-linux-1",
    ], argv

    missing = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="Error response from daemon: No such container: ocr-lab-missing",
    )
    with mock.patch.object(module.subprocess, "run", return_value=missing):
        assert runtime.stop("missing") == "not_found"

    already = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="Error response from daemon: container is not running",
    )
    with mock.patch.object(module.subprocess, "run", return_value=already):
        assert runtime.stop("linux-1") == "stopped"

    broken = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="Cannot connect to the Docker daemon",
    )
    with mock.patch.object(module.subprocess, "run", return_value=broken):
        try:
            runtime.stop("linux-1")
        except module.RuntimeUnavailable:
            pass
        else:
            raise AssertionError("a docker stop failure must raise RuntimeUnavailable")


def _serve(module, runtime, enabled=None):
    server = module.create_server(
        "127.0.0.1",
        0,
        TOKEN,
        audit_log=None,
        runtime=runtime,
        enabled_mutations=enabled,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _stop(server, thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def main() -> int:
    module = _load()
    _docker_runtime_checks(module)
    _docker_stop_checks(module)
    runtime = _fake_runtime(module)

    server, thread = _serve(module, runtime)
    port = server.server_address[1]
    try:
        status, body = _request(port, "/health")
        assert status == 200 and body["status"] == "ok", (status, body)

        status, _body = _request(port, "/v1/capabilities")
        assert status == 401, status

        status, body = _request(port, "/v1/capabilities", TOKEN)
        assert status == 200, (status, body)
        assert body["implemented"] == ["status"], body
        assert "stop" in body["pending"], body
        assert body["read_only"] is True, body

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

        status, _body = _request(port, "/v1/spawn", TOKEN, "POST", {"lab_id": "linux-1"})
        assert status == 501, status
        status, _body = _request(port, "/v1/spawn", None, "POST", {"lab_id": "linux-1"})
        assert status == 401, status
        status, _body = _request(port, "/v1/unknown", TOKEN)
        assert status == 404, status

        # Stop stays disabled by default.
        status, body = _request(port, "/v1/stop", TOKEN, "POST", {"lab_id": "linux-1"})
        assert status == 501, (status, body)
    finally:
        _stop(server, thread)

    server, thread = _serve(module, runtime, {"stop"})
    port = server.server_address[1]
    try:
        status, body = _request(port, "/v1/capabilities", TOKEN)
        assert status == 200, (status, body)
        assert body["implemented"] == ["status", "stop"], body
        assert body["read_only"] is False, body

        status, body = _request(port, "/v1/stop", TOKEN, "POST", {"lab_id": "linux-1"})
        assert status == 200 and body["stopped"] is True, (status, body)

        status, _body = _request(port, "/v1/stop", TOKEN, "POST", {"lab_id": "missing"})
        assert status == 404, status

        status, _body = _request(
            port, "/v1/stop", TOKEN, "POST", {"lab_id": "unavailable"}
        )
        assert status == 503, status

        status, _body = _request(port, "/v1/stop", TOKEN, "POST", {"lab_id": "Bad_ID"})
        assert status == 400, status

        status, _body = _request(port, "/v1/stop", TOKEN, "POST", {})
        assert status == 400, status

        status, _body = _request(port, "/v1/stop", None, "POST", {"lab_id": "linux-1"})
        assert status == 401, status
    finally:
        _stop(server, thread)

    print("OK: ocr-labd boundary, status, stop, and auth checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
