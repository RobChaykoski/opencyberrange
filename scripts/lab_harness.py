#!/usr/bin/env python3
"""Manifest-driven lab harness for OpenCyberRange.

Each production lab has a contract in ``platform/tester/manifests/<slug>.yaml``.
The harness executes the same sequence for every lab and every run:

    build -> start -> health -> network isolation -> expected ports ->
    flag existence -> flag validation -> repeat solve -> resource usage ->
    teardown

A reset is a full ``docker compose down -v`` and a fresh ``up``. ``--runs``
defaults to three so a lab must survive three clean runs.

Examples:
    python scripts/lab_harness.py --validate-all
    python scripts/lab_harness.py --lab linux-1-1-ssh-service-detection --runs 3
    python scripts/lab_harness.py --all --runs 3 --rebuild --json harness.json

The live mode needs Docker, the lab images, and (for KVM labs) /dev/kvm. The
static ``--validate-all`` mode runs anywhere and is part of CI.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_ROOT = ROOT / "platform" / "tester" / "manifests"
LABS_ROOT = ROOT / "platform" / "labs"
TESTER_DIR = ROOT / "platform" / "tester"
FLAG_RE = re.compile(r"OCR\{[^}\n]+\}")
REQUIRED_KEYS = {
    "lab_id",
    "track",
    "difficulty",
    "source",
    "expected_services",
    "health_timeout_seconds",
    "solver",
    "expected_flag_count",
    "expected_flag",
    "forbidden_networks",
    "max_memory_mb",
    "max_cpu",
}


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class LabResult:
    lab_id: str
    checks: list[Check] = field(default_factory=list)
    runs: list[dict] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.runs or (
            all(run.get("passed") for run in self.runs)
            and all(check.passed for check in self.checks)
        )


def _run(cmd: list[str], *, timeout: int = 120, check: bool = False) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(shlex.quote(c) for c in cmd)}\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return result


def load_manifest(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_lab(lab_dir: Path) -> dict:
    return yaml.safe_load((lab_dir / "lab.yaml").read_text(encoding="utf-8")) or {}


def validate_manifest(manifest: dict, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_KEYS - set(manifest)
    if missing:
        return [f"{manifest_path.name}: missing keys {sorted(missing)}"]

    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", str(manifest["lab_id"])):
        errors.append(f"{manifest_path.name}: invalid lab_id")

    source = ROOT / str(manifest["source"])
    lab_dir = source.parent
    if not source.is_file():
        errors.append(f"{manifest_path.name}: source lab.yaml not found")
        return errors
    lab = load_lab(lab_dir)
    if str(lab.get("flag") or "") != str(manifest.get("expected_flag") or ""):
        errors.append(f"{manifest_path.name}: expected_flag differs from lab.yaml")

    services = manifest.get("expected_services")
    if not isinstance(services, list):
        errors.append(f"{manifest_path.name}: expected_services must be a list")
    else:
        for service in services:
            port = service.get("port") if isinstance(service, dict) else None
            protocol = service.get("protocol") if isinstance(service, dict) else None
            if not isinstance(port, int) or not (1 <= port <= 65535):
                errors.append(f"{manifest_path.name}: invalid service port {port!r}")
            if protocol not in {"tcp", "udp"}:
                errors.append(f"{manifest_path.name}: invalid protocol {protocol!r}")

    solver = manifest.get("solver") or {}
    steps = solver.get("steps") if isinstance(solver, dict) else None
    if not isinstance(steps, list):
        errors.append(f"{manifest_path.name}: solver.steps must be a list")
    elif int(manifest.get("expected_flag_count") or 0) > 0 and not steps:
        errors.append(f"{manifest_path.name}: a flag lab needs solver steps")
    for step in steps or []:
        if not isinstance(step, dict) or not step.get("command"):
            errors.append(f"{manifest_path.name}: solver step has no command")

    for key in ("health_timeout_seconds",):
        if not isinstance(manifest.get(key), int) or manifest[key] <= 0:
            errors.append(f"{manifest_path.name}: {key} must be a positive integer")
    for key in ("max_memory_mb", "max_cpu"):
        value = manifest.get(key)
        if not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"{manifest_path.name}: {key} must be positive")
    forbidden = manifest.get("forbidden_networks")
    if not isinstance(forbidden, list) or not forbidden:
        errors.append(f"{manifest_path.name}: forbidden_networks must be a non-empty list")
    return errors


def resolve_command(
    command: str,
    targets: dict[str, str],
    credentials: dict[str, dict[str, str]],
    flag: str,
) -> tuple[str, list[str]]:
    """Resolve the platform tester placeholders. Return (command, problems)."""
    problems: list[str] = []

    def target(match: re.Match) -> str:
        name = match.group(1)
        if name not in targets:
            problems.append(f"unknown target placeholder: {name}")
            return match.group(0)
        return targets[name]

    def cred(match: re.Match) -> str:
        role, field_name = match.group(1), match.group(2)
        entry = credentials.get(role)
        if not entry or field_name not in entry:
            problems.append(f"unknown credential placeholder: {role}.{field_name}")
            return match.group(0)
        return entry[field_name]

    resolved = re.sub(r"\{target\.([^}]+)\}", target, command)
    resolved = re.sub(r"\{cred\.([^.}]+)\.(user|pass)\}", cred, resolved)
    resolved = resolved.replace("{flag}", flag)
    return resolved, problems


def _credentials(lab: dict) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for entry in lab.get("credentials") or []:
        if not isinstance(entry, dict):
            continue
        role = str(entry.get("role") or entry.get("username") or "").strip()
        if not role:
            continue
        mapping[role] = {
            "user": str(entry.get("username") or ""),
            "pass": str(entry.get("password") or ""),
        }
    return mapping


def _compose(project: str, compose_file: Path, args: list[str]) -> list[str]:
    return [
        "docker",
        "compose",
        "-p",
        project,
        "-f",
        str(compose_file),
        *args,
    ]


def _inspect(container_id: str) -> dict:
    result = _run(["docker", "inspect", container_id], timeout=30)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    data = json.loads(result.stdout)
    return data[0] if data else {}


def _project_containers(project: str, compose_file: Path) -> list[dict]:
    result = _run(_compose(project, compose_file, ["ps", "-q"]), timeout=60)
    ids = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [_inspect(container_id) for container_id in ids]


def _targets(containers: list[dict], network: str) -> dict[str, str]:
    targets: dict[str, str] = {}
    for container in containers:
        labels = (container.get("Config") or {}).get("Labels") or {}
        service = labels.get("com.docker.compose.service") or ""
        hostname = (container.get("Config") or {}).get("Hostname") or ""
        name = str(container.get("Name") or "").lstrip("/")
        networks = (container.get("NetworkSettings") or {}).get("Networks") or {}
        addresses = [
            (info or {}).get("IPAddress")
            for info in networks.values()
            if (info or {}).get("IPAddress")
        ]
        if not addresses:
            continue
        ip = addresses[0]
        if network in networks and (networks[network] or {}).get("IPAddress"):
            ip = networks[network]["IPAddress"]
        for key in (service, hostname, name):
            if key:
                targets.setdefault(key, ip)
    return targets


def _lab_network(containers: list[dict], project: str) -> str | None:
    for container in containers:
        networks = (container.get("NetworkSettings") or {}).get("Networks") or {}
        for name in networks:
            if name.startswith(f"{project}_") or name == project:
                return name
    return None


def _start_solver(
    image: str,
    network: str,
    temp_dir: Path,
    name: str,
    *,
    build: bool,
) -> str:
    inspect_result = _run(["docker", "image", "inspect", image], timeout=30)
    if inspect_result.returncode != 0:
        if not build:
            raise RuntimeError(f"solver image {image} is missing and --no-solver-build was set")
        _run(
            ["docker", "build", "-t", image, str(TESTER_DIR)],
            timeout=1800,
            check=True,
        )
    _run(["docker", "rm", "-f", name], timeout=30)
    _run(
        [
            "docker",
            "run",
            "-d",
            "--rm",
            "--name",
            name,
            "--network",
            network,
            "--memory",
            "256m",
            "--cpus",
            "0.5",
            "-v",
            f"{temp_dir}:/tests:ro",
            image,
            "tail",
            "-f",
            "/dev/null",
        ],
        timeout=120,
        check=True,
    )
    return name


def _exec_solver(name: str, command: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return _run(
        ["docker", "exec", name, "sh", "-lc", command],
        timeout=timeout,
    )


def _check_health(
    solver: str,
    services: list[dict],
    targets: dict[str, str],
    timeout: int,
) -> Check:
    if not services:
        return Check("health", True, "no TCP/UDP services declared; container checks only")
    deadline = time.time() + timeout
    missing: list[str] = []
    while time.time() < deadline:
        missing = []
        for service in services:
            port = int(service["port"])
            protocol = service.get("protocol") or "tcp"
            flag = "-u " if protocol == "udp" else ""
            reachable = False
            for ip in sorted(set(targets.values())):
                result = _exec_solver(
                    solver,
                    f"nc -z {flag}-w 2 {shlex.quote(ip)} {port}",
                    timeout=10,
                )
                if result.returncode == 0:
                    reachable = True
                    break
            if not reachable:
                missing.append(f"{protocol}/{port}")
        if not missing:
            return Check("health", True, "all declared services reachable")
        time.sleep(2)
    return Check("health", False, f"unreachable after {timeout}s: {', '.join(missing)}")


def _check_isolation(
    containers: list[dict],
    project: str,
    forbidden: list[str],
) -> Check:
    problems: list[str] = []
    forbidden_lower = [item.lower() for item in forbidden]
    for container in containers:
        labels = (container.get("Config") or {}).get("Labels") or {}
        short = labels.get("com.docker.compose.service") or str(container.get("Name") or "").lstrip("/")
        host_config = container.get("HostConfig") or {}
        if host_config.get("NetworkMode") == "host":
            problems.append(f"{short}: network_mode=host")
        networks = (container.get("NetworkSettings") or {}).get("Networks") or {}
        for network_name in networks:
            lowered = network_name.lower()
            if any(item in lowered for item in forbidden_lower):
                problems.append(f"{short}: attached to forbidden network {network_name}")
            if not (network_name.startswith(f"{project}_") or network_name == project):
                problems.append(f"{short}: attached to non-project network {network_name}")
        bindings = (host_config.get("PortBindings") or {})
        for container_port, hosts in bindings.items():
            for host in hosts or []:
                host_ip = str((host or {}).get("HostIp") or "")
                if host_ip in {"", "0.0.0.0", "::"}:
                    problems.append(f"{short}: publishes {container_port} on all interfaces")
    if problems:
        return Check("network isolation", False, "; ".join(problems))
    return Check("network isolation", True, f"{len(containers)} container(s) on project network only")


def _static_flag_check(lab_dir: Path, flag: str) -> Check:
    if not flag:
        return Check("flag existence", True, "no flag declared")
    for path in lab_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {"__pycache__", ".git", "node_modules"} for part in path.parts):
            continue
        try:
            if flag in path.read_text(encoding="utf-8", errors="ignore"):
                return Check("flag existence", True, f"flag present in {path.name}")
        except OSError:
            continue
    return Check("flag existence", False, "flag is not present in the lab source tree")


def _run_steps(
    solver: str,
    steps: list[dict],
    targets: dict[str, str],
    credentials: dict[str, dict[str, str]],
    flag: str,
) -> tuple[list[Check], str]:
    checks: list[Check] = []
    output = ""
    for index, step in enumerate(steps, start=1):
        name = str(step.get("name") or f"step {index}")
        resolved, problems = resolve_command(
            str(step.get("command") or ""), targets, credentials, flag
        )
        if problems:
            checks.append(Check(name, False, "; ".join(problems)))
            continue
        try:
            result = _exec_solver(solver, resolved, timeout=90)
        except subprocess.TimeoutExpired:
            checks.append(Check(name, False, "timed out after 90s"))
            continue
        output += result.stdout + "\n" + result.stderr + "\n"
        expected = str(step.get("expect") or "")
        passed = result.returncode == 0 and (not expected or expected in output)
        detail = "" if passed else (
            f"exit={result.returncode}; expected {expected!r}; "
            f"output={result.stdout[-300:]!r}"
        )
        checks.append(Check(name, passed, detail))
    return checks, output


def _flag_validation(output: str, expected_flag: str, expected_count: int) -> Check:
    found = set(FLAG_RE.findall(output))
    if expected_flag and expected_flag not in found:
        return Check("flag validation", False, f"{expected_flag} not found in solver output")
    if expected_count and len(found) != expected_count:
        return Check(
            "flag validation",
            False,
            f"expected {expected_count} distinct flag(s), found {len(found)}: {sorted(found)}",
        )
    return Check("flag validation", True, f"found {len(found)} flag(s)")


def _resource_check(containers: list[dict], max_memory_mb: float, max_cpu: float) -> Check:
    ids = [str(c.get("Id") or "") for c in containers if c.get("Id")]
    if not ids:
        return Check("resource usage", False, "no lab containers")
    result = _run(
        ["docker", "stats", "--no-stream", "--format", "{{json .}}", *ids],
        timeout=60,
    )
    if result.returncode != 0:
        return Check("resource usage", False, result.stderr.strip())
    problems: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        memory_text = str(row.get("MemUsage") or "0MiB").split("/")[0].strip()
        match = re.match(r"([0-9.]+)\s*([KMG]i?B)", memory_text, re.IGNORECASE)
        memory_mb = 0.0
        if match:
            value = float(match.group(1))
            unit = match.group(2).lower()
            memory_mb = value / 1024 if unit.startswith("k") else value
            if unit.startswith("g"):
                memory_mb = value * 1024
        cpu_percent = float(str(row.get("CPUPerc") or "0").rstrip("%") or 0)
        if memory_mb > max_memory_mb:
            problems.append(f"{row.get('Name')}: {memory_mb:.0f}MiB > {max_memory_mb:.0f}MiB")
        if cpu_percent / 100 > max_cpu + 0.05:
            problems.append(f"{row.get('Name')}: {cpu_percent / 100:.2f} cores > {max_cpu:.2f}")
    if problems:
        return Check("resource usage", False, "; ".join(problems))
    return Check("resource usage", True, f"within {max_memory_mb:.0f}MiB / {max_cpu:.2f} CPU")


def run_one(lab: dict, manifest: dict, args: argparse.Namespace, run_index: int) -> dict:
    lab_dir = ROOT / manifest["source"]
    lab_dir = lab_dir.parent
    compose_file = lab_dir / "docker-compose.yml"
    project = f"ocr-harness-{manifest['lab_id']}-{run_index}-{int(time.time())}"[:63]
    solver_name = f"{project}-solver"[:63]
    checks: list[Check] = []
    temp_dir = Path(tempfile.mkdtemp(prefix="ocr-lab-harness-"))
    solver_started = False

    def compose(args_list: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
        return _run(_compose(project, compose_file, args_list), timeout=timeout)

    try:
        if not args.no_build and (run_index == 1 or args.rebuild):
            built = compose(["build"], timeout=3600)
            checks.append(
                Check(
                    "build",
                    built.returncode == 0,
                    "" if built.returncode == 0 else built.stderr[-500:],
                )
            )
            if built.returncode != 0:
                raise RuntimeError("build failed")
        else:
            checks.append(Check("build", True, "skipped (--no-build or reuse image)"))

        started = compose(["up", "-d", "--remove-orphans"], timeout=600)
        checks.append(
            Check(
                "start",
                started.returncode == 0,
                "" if started.returncode == 0 else started.stderr[-500:],
            )
        )
        if started.returncode != 0:
            raise RuntimeError("start failed")

        containers = _project_containers(project, compose_file)
        running = [c for c in containers if (c.get("State") or {}).get("Status") == "running"]
        checks.append(
            Check(
                "containers",
                len(running) == len(containers) and bool(containers),
                f"{len(running)}/{len(containers)} running",
            )
        )
        network = _lab_network(containers, project)
        if not network:
            raise RuntimeError("could not find the lab compose network")
        targets = _targets(containers, network)

        _start_solver(
            manifest["solver"]["image"],
            network,
            temp_dir,
            solver_name,
            build=not args.no_solver_build,
        )
        solver_started = True

        checks.append(
            _check_health(
                solver_name,
                manifest.get("expected_services") or [],
                targets,
                int(manifest["health_timeout_seconds"]),
            )
        )
        checks.append(
            _check_isolation(
                containers, project, list(manifest["forbidden_networks"])
            )
        )
        checks.append(_static_flag_check(lab_dir, manifest.get("expected_flag") or ""))

        credentials = _credentials(lab)
        steps = (manifest.get("solver") or {}).get("steps") or []
        for solve_index in (1, 2):
            step_checks, output = _run_steps(
                solver_name,
                steps,
                targets,
                credentials,
                manifest.get("expected_flag") or "",
            )
            checks.extend(step_checks)
            checks.append(
                _flag_validation(
                    output,
                    manifest.get("expected_flag") or "",
                    int(manifest.get("expected_flag_count") or 0),
                )
            )
            if solve_index == 1 and not all(check.passed for check in step_checks):
                break
        checks.append(
            _resource_check(
                containers,
                float(manifest["max_memory_mb"]),
                float(manifest["max_cpu"]),
            )
        )
    except Exception as exc:  # noqa: BLE001 - the harness reports the failing check
        checks.append(Check("harness", False, str(exc)))
    finally:
        if solver_started:
            _run(["docker", "rm", "-f", solver_name], timeout=60)
        if not args.keep:
            compose(["down", "-v", "--remove-orphans"], timeout=300)
        else:
            print(f"kept project {project} for inspection")

    passed = all(check.passed for check in checks)
    result = {
        "project": project,
        "passed": passed,
        "checks": [check.__dict__ for check in checks],
    }
    if solver_started:
        result["solver"] = solver_name
    return result


def manifests_for(selection: list[str], include_all: bool) -> list[Path]:
    if include_all:
        return sorted(MANIFEST_ROOT.glob("*.yaml"))
    paths = []
    for slug in selection:
        path = MANIFEST_ROOT / f"{slug}.yaml"
        if not path.is_file():
            raise SystemExit(f"no manifest for {slug}")
        paths.append(path)
    return paths


def validate_all() -> int:
    paths = sorted(MANIFEST_ROOT.glob("*.yaml"))
    if not paths:
        print("no manifests found", file=sys.stderr)
        return 1
    errors: list[str] = []
    for path in paths:
        errors.extend(validate_manifest(load_manifest(path), path))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"{len(errors)} manifest error(s) across {len(paths)} labs", file=sys.stderr)
        return 1
    print(f"validated {len(paths)} lab manifests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", action="append", default=[], help="lab slug")
    parser.add_argument("--all", action="store_true", help="run every manifest")
    parser.add_argument("--validate-all", action="store_true", help="static validation only")
    parser.add_argument("--runs", type=int, default=3, help="clean runs per lab (default 3)")
    parser.add_argument("--no-build", action="store_true", help="use existing lab images")
    parser.add_argument("--rebuild", action="store_true", help="rebuild images on every run")
    parser.add_argument("--keep", action="store_true", help="leave the last project up")
    parser.add_argument("--no-solver-build", action="store_true")
    parser.add_argument("--json", dest="json_path", help="write the result JSON here")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    if args.validate_all:
        return validate_all()
    if not args.lab and not args.all:
        parser.error("choose --lab SLUG, --all, or --validate-all")
    if args.runs < 1:
        parser.error("--runs must be at least 1")

    results: list[LabResult] = []
    for path in manifests_for(args.lab, args.all):
        manifest = load_manifest(path)
        errors = validate_manifest(manifest, path)
        if errors:
            results.append(
                LabResult(
                    lab_id=str(manifest.get("lab_id") or path.stem),
                    checks=[Check("manifest", False, "; ".join(errors))],
                )
            )
            if args.fail_fast:
                break
            continue

        lab = load_lab((ROOT / manifest["source"]).parent)
        result = LabResult(lab_id=manifest["lab_id"])
        for run_index in range(1, args.runs + 1):
            print(f"[{manifest['lab_id']}] run {run_index}/{args.runs}", flush=True)
            run = run_one(lab, manifest, args, run_index)
            result.runs.append(run)
            for check in run["checks"]:
                print(
                    f"  {'PASS' if check['passed'] else 'FAIL'} {check['name']}"
                    + (f" -- {check['detail']}" if check.get("detail") else ""),
                    flush=True,
                )
            if not run["passed"] and args.fail_fast:
                break
        results.append(result)
        print(
            f"[{manifest['lab_id']}] {'PASS' if result.passed else 'FAIL'}",
            flush=True,
        )
        if not result.passed and args.fail_fast:
            break

    payload = {
        "runs_per_lab": args.runs,
        "labs": [
            {
                "lab_id": result.lab_id,
                "passed": result.passed,
                "runs": result.runs,
                "checks": [check.__dict__ for check in result.checks],
            }
            for result in results
        ],
    }
    if args.json_path:
        Path(args.json_path).write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {args.json_path}")

    failures = [result for result in results if not result.passed]
    print(
        f"{len(results) - len(failures)}/{len(results)} labs passed "
        f"({args.runs} run(s) each)"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
