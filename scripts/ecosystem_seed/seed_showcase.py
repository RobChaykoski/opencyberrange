#!/usr/bin/env python3
"""Seed the full local Moodle LTI 1.3 showcase in one command.

This script assumes the dev-only training stack and the OpenCyberRange backend
are already running. It is idempotent: rerunning it refreshes the same users,
courses, course tool, demo activity, and LTI platform.

Typical local Docker Desktop use:

    python scripts/ecosystem_seed/seed_showcase.py

For the standard dev host with TLS, set the public/internal URLs explicitly:

    MOODLE_ISSUER=https://moodle.example.test:9443 \
    OCR_PUBLIC_URL=https://172.16.16.44 \
    python scripts/ecosystem_seed/seed_showcase.py

Environment overrides:
    MOODLE_CONTAINER, OCR_CONTAINER
    MOODLE_ISSUER, MOODLE_INTERNAL_URL
    OCR_PUBLIC_URL, OCR_INTERNAL_URL
    MOODLE_LTI_CLIENT_ID, MOODLE_LTI_COURSE, MOODLE_LTI_LAB_SLUG
    MOODLE_LTI_ACTIVITY_NAME, MOODLE_LTI_COURSE_TOOL_NAME
    TRAINING_PASSWORD
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

ROOT = Path(__file__).resolve().parents[2]
DEPLOY = ROOT / "deploy" / "ecosystem-test"
SEED = ROOT / "scripts" / "ecosystem_seed"


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    path = DEPLOY / ".env"
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(
    cmd: list[str],
    *,
    input_text: str | None = None,
    capture: bool = False,
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=capture,
        check=False,
    )
    if result.returncode != 0:
        if capture:
            if result.stdout:
                print(result.stdout, file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        fail(f"command failed ({result.returncode}): {' '.join(cmd[:4])} ...")
    return result


def docker_running(name: str) -> bool:
    result = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Running}}", name],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def container_env(name: str, key: str) -> str:
    result = subprocess.run(
        ["docker", "exec", name, "printenv", key],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def docker_env_args(values: dict[str, str]) -> list[str]:
    args: list[str] = []
    for key, value in values.items():
        args.extend(["-e", f"{key}={value}"])
    return args


def internal_alias(url: str) -> str:
    """Map host-loopback names to the Docker host alias for server-to-server calls."""
    parts = urlsplit(url)
    if parts.hostname not in ("localhost", "127.0.0.1"):
        return url
    host = "host.docker.internal"
    if parts.port:
        host = f"{host}:{parts.port}"
    return urlunsplit((parts.scheme, host, parts.path, parts.query, parts.fragment))


def check_ocr_to_moodle(ocr_container: str, url: str) -> None:
    code = (
        "import sys, urllib.request; "
        "urllib.request.urlopen(sys.argv[1], timeout=8).read(1)"
    )
    result = subprocess.run(
        ["docker", "exec", ocr_container, "python", "-c", code, url],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(
            f"the OCR container cannot reach Moodle at {url}.\n"
            "  For local Docker Desktop, set MOODLE_BIND=0.0.0.0 (or the host IP)\n"
            "  in deploy/ecosystem-test/.env, recreate Moodle, and rerun.\n"
            "  Or set MOODLE_ISSUER / MOODLE_INTERNAL_URL to an address both\n"
            "  the browser and the OCR container can reach."
        )


def check_moodle_to_ocr(moodle_container: str, url: str) -> None:
    php = (
        "$u=" + json.dumps(url) + ";"
        "$p=parse_url($u);"
        "$scheme=$p['scheme'] ?? 'http';"
        "$host=$p['host'] ?? '';"
        "$port=$p['port'] ?? ($scheme === 'https' ? 443 : 80);"
        "$s=@fsockopen($host,$port,$e,$m,8);"
        "if(!$s){fwrite(STDERR,$m ?: 'connection failed'); exit(1);}"
        "fclose($s);"
    )
    result = subprocess.run(
        ["docker", "exec", moodle_container, "php", "-r", php],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(
            f"Moodle cannot reach the OCR endpoint at {url}.\n"
            "  Publish the frontend on an interface Moodle can reach, or set\n"
            "  OCR_PUBLIC_URL / OCR_INTERNAL_URL to a reachable address."
        )


def parse_output(output: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in output.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            parsed[key.strip()] = value.strip()
    return parsed


def main() -> int:
    file_env = load_env()
    if os.environ.get("OCR_ENV") in ("production", "prod") or file_env.get(
        "OCR_ENV"
    ) in ("production", "prod"):
        fail("refusing to seed the showcase against production")

    moodle_container = os.environ.get("MOODLE_CONTAINER", "ecosystem-test-moodle-1")
    if not docker_running(moodle_container):
        fail(
            f"Moodle container {moodle_container!r} is not running.\n"
            "  Start it with: cd deploy/ecosystem-test && docker compose up -d"
        )

    ocr_container = os.environ.get("OCR_CONTAINER", "")
    if not ocr_container:
        for candidate in ("ocr-backend", "ocr-r5-backend"):
            if docker_running(candidate):
                ocr_container = candidate
                break
    if not ocr_container or not docker_running(ocr_container):
        fail(
            "could not find the OCR backend container.\n"
            "  Set OCR_CONTAINER=... (for the local test stack it is ocr-r5-backend)."
        )

    if container_env(ocr_container, "OCR_ENV") in ("production", "prod"):
        fail(f"{ocr_container} reports a production environment")

    training_password = (
        os.environ.get("TRAINING_PASSWORD") or "TrainLab!2026#Student"
    )
    moodle_port = os.environ.get("MOODLE_PORT") or file_env.get("MOODLE_PORT") or "8091"
    moodle_issuer = (
        os.environ.get("MOODLE_ISSUER")
        or f"http://host.docker.internal:{moodle_port}"
    ).rstrip("/")
    ocr_public = (
        os.environ.get("OCR_PUBLIC_URL")
        or container_env(ocr_container, "PUBLIC_BASE_URL")
        or "http://host.docker.internal:18081"
    ).rstrip("/")
    moodle_internal = (
        os.environ.get("MOODLE_INTERNAL_URL") or internal_alias(moodle_issuer)
    ).rstrip("/")
    ocr_internal = (
        os.environ.get("OCR_INTERNAL_URL") or internal_alias(ocr_public)
    ).rstrip("/")

    moodle_host = urlsplit(moodle_issuer).hostname
    ocr_host = urlsplit(ocr_public).hostname
    loopback = {"localhost", "127.0.0.1"}
    if (
        urlsplit(moodle_issuer).scheme == "http"
        and urlsplit(ocr_public).scheme == "http"
        and moodle_host != ocr_host
        and not (moodle_host in loopback and ocr_host in loopback)
    ):
        print(
            "WARNING: browser-facing Moodle and OCR hosts differ "
            f"({moodle_host} vs {ocr_host}). The local HTTP CSP allows "
            "loopback framing only, so use the same host for both."
        )

    client_id = os.environ.get("MOODLE_LTI_CLIENT_ID", "ocr-training-client")
    course = os.environ.get("MOODLE_LTI_COURSE", "OCR-CAP-COHORT")
    course_tool = os.environ.get(
        "MOODLE_LTI_COURSE_TOOL_NAME", "OpenCyberRange Showcase"
    )
    activity = os.environ.get(
        "MOODLE_LTI_ACTIVITY_NAME", "Avalon Biotech - Suspicious Traffic Analysis"
    )
    lab_slug = os.environ.get(
        "MOODLE_LTI_LAB_SLUG", "network-1-1-packet-capture-analysis"
    )
    platform_name = os.environ.get(
        "MOODLE_PLATFORM_NAME", "Training Moodle (Showcase)"
    )

    print("== Connectivity ==")
    check_ocr_to_moodle(ocr_container, moodle_internal)
    check_moodle_to_ocr(moodle_container, ocr_internal)
    print(f"  OCR container -> Moodle: {moodle_internal}")
    print(f"  Moodle -> OCR:           {ocr_internal}")

    print("== Moodle users and courses ==")
    run(
        [
            "docker",
            "exec",
            "-u",
            os.environ.get("MOODLE_SEED_USER", "daemon"),
            "-e",
            f"TRAINING_PASSWORD={training_password}",
            moodle_container,
            "php",
            "/seed/seed_moodle.php",
        ]
    )

    print("== OpenCyberRange users and course ==")
    run(
        [
            "docker",
            "exec",
            "-i",
            "-w",
            "/app",
            "-e",
            f"TRAINING_PASSWORD={training_password}",
            ocr_container,
            "python",
            "-",
        ],
        input_text=(SEED / "seed_ocr.py").read_text(encoding="utf-8"),
    )

    print("== Moodle 5 course tool and demo activity ==")
    php_result = run(
        [
            "docker",
            "exec",
            "-u",
            os.environ.get("MOODLE_SEED_USER", "daemon"),
            *docker_env_args(
                {
                    "OCR_PUBLIC_URL": ocr_public,
                    "OCR_INTERNAL_URL": ocr_internal,
                    "MOODLE_LTI_CLIENT_ID": client_id,
                    "MOODLE_LTI_COURSE": course,
                    "MOODLE_LTI_COURSE_TOOL_NAME": course_tool,
                    "MOODLE_LTI_ACTIVITY_NAME": activity,
                    "MOODLE_LTI_LAB_SLUG": lab_slug,
                    "MOODLE_ALLOW_PRIVATE_LTI_URLS": "1",
                }
            ),
            moodle_container,
            "php",
            "/seed/seed_moodle_lti.php",
        ],
        capture=True,
    )
    print(php_result.stdout.strip())
    details = parse_output(php_result.stdout)
    if not details.get("client_id") or not details.get("deployment_id"):
        fail("the Moodle LTI seed did not return a client id and deployment id")

    print("== OpenCyberRange LTI platform ==")
    run(
        [
            "docker",
            "exec",
            "-i",
            "-w",
            "/app",
            *docker_env_args(
                {
                    "MOODLE_ISSUER": moodle_issuer,
                    "MOODLE_INTERNAL_URL": moodle_internal,
                    "MOODLE_LTI_CLIENT_ID": details["client_id"],
                    "MOODLE_LTI_DEPLOYMENT_ID": details["deployment_id"],
                    "MOODLE_PLATFORM_NAME": platform_name,
                }
            ),
            ocr_container,
            "python",
            "-",
        ],
        input_text=(SEED / "seed_lti.py").read_text(encoding="utf-8"),
    )

    cmid = details.get("cmid", "")
    print("\nShowcase ready.")
    print(f"  Moodle:          {moodle_issuer}")
    print(f"  OpenCyberRange:  {ocr_public}")
    print(f"  Course:          {course}")
    print(f"  Activity:        {activity}")
    if cmid and cmid != "0":
        print(f"  Activity URL:    {moodle_issuer}/mod/lti/view.php?id={cmid}")
    print(f"  LTI deployment:  {details.get('deployment_id')} (client {details.get('client_id')})")
    print("  Accounts:        instructor01 / student01 / mentor01 / ta01")
    print(
        "  Password:        TRAINING_PASSWORD "
        f"(default {training_password})"
    )
    print("  Admin reviews:   OpenCyberRange -> Admin -> Settings -> LTI platforms")
    print(
        "\n  Dev-only note: Moodle's cURL SSRF allow-list was relaxed for the\n"
        "  private Docker host. Do not run this seed on a production Moodle."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
