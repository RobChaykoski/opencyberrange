#!/usr/bin/env python3
"""Audit lab containers for host and Docker control-plane exposure.

This is a static release gate. It reads every lab's docker-compose.yml,
Dockerfiles, and lab.yaml and flags configuration that could let a
student-controlled container reach the host, the Docker socket, management
networks, cloud metadata, or another learner's lab.

Exit code 1 when a Critical finding is present. Warnings are reported but do
not fail the gate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
LABS = ROOT / "platform" / "labs"

CRITICAL_CAPS = {"SYS_ADMIN", "SYS_MODULE", "SYS_PTRACE", "DAC_READ_SEARCH"}
HIGH_CAPS = {"NET_ADMIN", "NET_RAW", "SYS_NICE", "SYS_RESOURCE", "MKNOD"}
HOST_NETWORK_KEYS = ("network_mode", "pid", "ipc", "uts", "userns_mode")
SENSITIVE_VOLUME_WORDS = ("flag", "secret", "credential", "cred", "private", "key", "docker.sock")
MANAGEMENT_HINTS = ("172.16.16.", "169.254.169.254", "host.docker.internal", "/var/run/docker.sock")


def _load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    except Exception as exc:
        return {"__parse_error__": str(exc)}


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _volume_parts(volume) -> tuple[str, str, bool]:
    if isinstance(volume, dict):
        source = str(volume.get("source", ""))
        target = str(volume.get("target", ""))
        read_only = bool(volume.get("read_only"))
        return source, target, read_only
    text = str(volume)
    parts = text.split(":")
    if len(parts) >= 2:
        source, target = parts[0], parts[1]
        read_only = len(parts) >= 3 and "ro" in parts[2].split(",")
        return source, target, read_only
    return "", text, False


def _is_host_path(source: str) -> bool:
    if not source or source.startswith(("./", "../")):
        return False
    return source.startswith(("/", "~")) or bool(re.match(r"^[A-Za-z]:[\\/]", source))


def audit_lab(lab_dir: Path) -> list[dict]:
    findings: list[dict] = []
    compose_path = lab_dir / "docker-compose.yml"
    if not compose_path.is_file():
        return findings
    compose = _load_yaml(compose_path)
    if "__parse_error__" in compose:
        findings.append({
            "severity": "critical",
            "service": "-",
            "check": "compose-parse",
            "detail": compose["__parse_error__"],
            "file": str(compose_path.relative_to(ROOT)),
        })
        return findings

    for service_name, service in (compose.get("services") or {}).items():
        if not isinstance(service, dict):
            continue
        prefix = f"{compose_path.relative_to(ROOT)}::{service_name}"

        if service.get("privileged") is True:
            findings.append({
                "severity": "critical",
                "service": service_name,
                "check": "privileged",
                "detail": "privileged: true grants the container host-level capabilities.",
                "file": str(compose_path.relative_to(ROOT)),
            })

        for key in HOST_NETWORK_KEYS:
            if str(service.get(key, "")).lower() == "host":
                findings.append({
                    "severity": "critical",
                    "service": service_name,
                    "check": f"{key}-host",
                    "detail": f"{key}: host shares the host namespace.",
                    "file": str(compose_path.relative_to(ROOT)),
                })

        for volume in _as_list(service.get("volumes")):
            source, target, read_only = _volume_parts(volume)
            lowered = f"{source}:{target}".lower()
            if "docker.sock" in lowered or "/var/run/docker" in lowered:
                findings.append({
                    "severity": "critical",
                    "service": service_name,
                    "check": "docker-socket",
                    "detail": f"Mounts the Docker control socket: {source}:{target}",
                    "file": str(compose_path.relative_to(ROOT)),
                })
            elif _is_host_path(source):
                findings.append({
                    "severity": "warning" if read_only else "high",
                    "service": service_name,
                    "check": "host-bind-mount",
                    "detail": (
                        f"{'Read-only' if read_only else 'Writable'} host path "
                        f"{source} mounted at {target}."
                    ),
                    "file": str(compose_path.relative_to(ROOT)),
                })
            elif any(word in lowered for word in SENSITIVE_VOLUME_WORDS):
                findings.append({
                    "severity": "high",
                    "service": service_name,
                    "check": "sensitive-volume-name",
                    "detail": f"Volume name suggests flags or credentials: {source}:{target}",
                    "file": str(compose_path.relative_to(ROOT)),
                })

        for cap in _as_list(service.get("cap_add")):
            cap = str(cap).upper()
            if cap in CRITICAL_CAPS:
                findings.append({
                    "severity": "critical",
                    "service": service_name,
                    "check": f"cap-{cap.lower()}",
                    "detail": f"cap_add: {cap} can reach host resources.",
                    "file": str(compose_path.relative_to(ROOT)),
                })
            elif cap in HIGH_CAPS:
                findings.append({
                    "severity": "high",
                    "service": service_name,
                    "check": f"cap-{cap.lower()}",
                    "detail": f"cap_add: {cap} is powerful; confirm the lab needs it.",
                    "file": str(compose_path.relative_to(ROOT)),
                })

        if service.get("devices"):
            findings.append({
                "severity": "high",
                "service": service_name,
                "check": "devices",
                "detail": "Passes host devices into the container.",
                "file": str(compose_path.relative_to(ROOT)),
            })

        for opt in _as_list(service.get("security_opt")):
            if "unconfined" in str(opt).lower():
                findings.append({
                    "severity": "high",
                    "service": service_name,
                    "check": "security-opt-unconfined",
                    "detail": f"security_opt: {opt}",
                    "file": str(compose_path.relative_to(ROOT)),
                })

        user = str(service.get("user", "") or "").strip()
        if not user:
            findings.append({
                "severity": "warning",
                "service": service_name,
                "check": "root-user",
                "detail": "No user: set; the service runs as root unless the image drops privileges.",
                "file": str(compose_path.relative_to(ROOT)),
            })
        elif user in {"0", "root", "0:0"}:
            findings.append({
                "severity": "warning",
                "service": service_name,
                "check": "root-user",
                "detail": f"user: {user} runs as root.",
                "file": str(compose_path.relative_to(ROOT)),
            })

        for host in _as_list(service.get("extra_hosts")):
            if any(hint in str(host) for hint in MANAGEMENT_HINTS):
                findings.append({
                    "severity": "critical",
                    "service": service_name,
                    "check": "extra-host",
                    "detail": f"extra_hosts points at a management or metadata endpoint: {host}",
                    "file": str(compose_path.relative_to(ROOT)),
                })

        for env in _as_list(service.get("environment")):
            text = str(env)
            if any(hint in text for hint in MANAGEMENT_HINTS):
                findings.append({
                    "severity": "high",
                    "service": service_name,
                    "check": "environment-management-endpoint",
                    "detail": f"Environment value references a management endpoint: {text}",
                    "file": str(compose_path.relative_to(ROOT)),
                })

    # Dockerfiles: a privileged flag or socket reference is just as dangerous.
    for dockerfile in lab_dir.rglob("Dockerfile*"):
        try:
            text = dockerfile.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lowered = text.lower()
        if "docker.sock" in lowered or "--privileged" in lowered:
            findings.append({
                "severity": "critical",
                "service": "-",
                "check": "dockerfile-control-plane",
                "detail": "Dockerfile references the Docker socket or privileged mode.",
                "file": str(dockerfile.relative_to(ROOT)),
            })
        if re.search(r"(?im)^\s*user\s+root\s*$", text):
            findings.append({
                "severity": "warning",
                "service": "-",
                "check": "dockerfile-root-user",
                "detail": "Dockerfile explicitly sets USER root.",
                "file": str(dockerfile.relative_to(ROOT)),
            })

    # lab.yaml should never point a student target at the management plane.
    lab_yaml = lab_dir / "lab.yaml"
    if lab_yaml.is_file():
        text = lab_yaml.read_text(encoding="utf-8-sig", errors="replace")
        for hint in MANAGEMENT_HINTS:
            if hint in text:
                findings.append({
                    "severity": "critical" if "169.254.169.254" in hint or "docker.sock" in hint else "high",
                    "service": "-",
                    "check": "lab-target-management-endpoint",
                    "detail": f"lab.yaml references {hint}.",
                    "file": str(lab_yaml.relative_to(ROOT)),
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--labs", default=str(LABS))
    args = parser.parse_args()

    labs_root = Path(args.labs)
    all_findings: list[dict] = []
    lab_dirs = sorted({path.parent for path in labs_root.rglob("docker-compose.yml")})
    for lab_dir in lab_dirs:
        all_findings.extend(audit_lab(lab_dir))

    critical = [f for f in all_findings if f["severity"] == "critical"]
    high = [f for f in all_findings if f["severity"] == "high"]
    warnings = [f for f in all_findings if f["severity"] == "warning"]

    if args.json:
        print(json.dumps({
            "labs": len(lab_dirs),
            "critical": critical,
            "high": high,
            "warnings": warnings,
        }, indent=2))
    else:
        print(f"Audited {len(lab_dirs)} lab compose files")
        for label, rows in (("CRITICAL", critical), ("HIGH", high), ("WARNING", warnings)):
            print(f"\n{label}: {len(rows)}")
            for row in rows:
                print(f"  {row['file']}::{row['service']} [{row['check']}] {row['detail']}")

    return 1 if critical else 0


if __name__ == "__main__":
    sys.exit(main())
