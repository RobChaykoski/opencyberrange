#!/usr/bin/env python3
"""Sample and report lab session telemetry from Docker and PostgreSQL.

This is the read-only MVP for lab telemetry. It does not write to the platform
database and does not change lab settings. Run it on the range host:

    python3 scripts/lab-telemetry.py sample --once
    python3 scripts/lab-telemetry.py sample --interval 15
    python3 scripts/lab-telemetry.py report --days 7
    python3 scripts/lab-telemetry.py report --days 7 --json

The sampler writes one JSON line per active session per sample:

    session_id, user_id, lab_slug, status, started_at, ts,
    ready, boot_seconds, containers_total, containers_ready,
    cpu_percent, mem_mb, declared_mem_mb, declared_cpus,
    container_names

It records no learner prompts, flags, hostnames, or PII. Reports aggregate by
lab and suppress labs with fewer than --min-sessions sessions.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

DEFAULT_OUTPUT = Path.home() / "opencyberrange" / "telemetry" / "lab-telemetry.jsonl"


def _run(command: list[str], timeout: int = 60) -> str:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"{result.stderr.strip()[:500]}"
        )
    return result.stdout


def _db_sessions(
    db_container: str, db_user: str, db_name: str
) -> list[dict]:
    sql = (
        "SELECT s.id, s.user_id, s.status, "
        "to_char(s.started_at, 'YYYY-MM-DD\"T\"HH24:MI:SS'), l.slug "
        "FROM lab_sessions s JOIN labs l ON l.id = s.lab_id "
        "WHERE s.status IN ('starting','running') "
        "   OR s.started_at > now() - interval '2 days' "
        "ORDER BY s.started_at DESC"
    )
    output = _run(
        [
            "docker",
            "exec",
            db_container,
            "psql",
            "-U",
            db_user,
            "-d",
            db_name,
            "-tA",
            "-F",
            "|",
            "-c",
            sql,
        ]
    )
    rows = []
    for line in output.splitlines():
        parts = line.split("|")
        if len(parts) != 5:
            continue
        rows.append(
            {
                "session_id": int(parts[0]),
                "user_id": int(parts[1]),
                "status": parts[2],
                "started_at": parts[3],
                "lab_slug": parts[4],
            }
        )
    return rows


def _docker_containers() -> list[dict]:
    output = _run(
        [
            "docker",
            "ps",
            "--format",
            '{{.Names}}|{{.Label "com.docker.compose.project"}}',
        ]
    )
    containers = []
    for line in output.splitlines():
        if "|" not in line:
            continue
        name, project = line.split("|", 1)
        containers.append({"name": name, "project": project.strip().lower()})
    return containers


def _docker_stats() -> dict[str, dict]:
    output = _run(
        [
            "docker",
            "stats",
            "--no-stream",
            "--format",
            "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}",
        ],
        timeout=120,
    )
    stats = {}
    for line in output.splitlines():
        parts = line.split("|")
        if len(parts) != 3:
            continue
        name, cpu, memory = parts
        try:
            cpu_percent = float(cpu.strip().rstrip("%"))
        except ValueError:
            cpu_percent = 0.0
        used = memory.split("/")[0].strip()
        stats[name] = {
            "cpu_percent": cpu_percent,
            "mem_mb": _parse_memory_mb(used),
        }
    return stats


def _parse_memory_mb(value: str) -> float:
    value = value.strip()
    units = (
        ("GiB", 1024.0),
        ("MiB", 1.0),
        ("KiB", 1.0 / 1024.0),
        ("GB", 1000.0),
        ("MB", 1.0),
        ("kB", 1.0 / 1000.0),
    )
    for suffix, factor in units:
        if value.endswith(suffix):
            try:
                return float(value[: -len(suffix)]) * factor
            except ValueError:
                return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def _inspect(name: str) -> dict:
    output = _run(["docker", "inspect", name], timeout=30)
    data = json.loads(output)
    if not isinstance(data, list) or not data:
        return {}
    return data[0]


def _session_payload(
    session: dict,
    containers: list[dict],
    stats: dict[str, dict],
) -> dict | None:
    project = f"lab_{session['user_id']}_{session['lab_slug']}".lower()
    names = [
        item["name"]
        for item in containers
        if item["project"] == project or item["name"].startswith(project)
    ]
    if not names:
        return None

    started_at = datetime.fromisoformat(session["started_at"]).replace(
        tzinfo=UTC
    )
    now = datetime.now(UTC)
    elapsed = max(0.0, (now - started_at).total_seconds())

    total = len(names)
    ready = 0
    cpu = 0.0
    mem_mb = 0.0
    declared_mem_mb = 0.0
    declared_cpus = 0.0
    inspect_errors = 0
    for name in names:
        try:
            info = _inspect(name)
        except Exception:  # noqa: BLE001 - one bad container must not abort the sample
            inspect_errors += 1
            continue
        state = info.get("State") or {}
        health = (state.get("Health") or {}).get("Status")
        if state.get("Running") and health in (None, "healthy"):
            ready += 1
        host_config = info.get("HostConfig") or {}
        declared_mem_mb += float(host_config.get("Memory") or 0) / (1024 * 1024)
        nano = float(host_config.get("NanoCpus") or 0)
        if nano:
            declared_cpus += nano / 1_000_000_000
        else:
            quota = float(host_config.get("CpuQuota") or 0)
            period = float(host_config.get("CpuPeriod") or 0)
            if quota and period:
                declared_cpus += quota / period
        stat = stats.get(name) or {}
        cpu += float(stat.get("cpu_percent") or 0)
        mem_mb += float(stat.get("mem_mb") or 0)

    return {
        "ts": now.isoformat(),
        "session_id": session["session_id"],
        "user_id": session["user_id"],
        "lab_slug": session["lab_slug"],
        "status": session["status"],
        "started_at": started_at.isoformat(),
        "elapsed_seconds": round(elapsed, 1),
        "ready": total > 0 and ready == total and inspect_errors == 0,
        "boot_seconds": round(elapsed, 1) if total > 0 and ready == total else None,
        "containers_total": total,
        "containers_ready": ready,
        "container_names": names,
        "cpu_percent": round(cpu, 2),
        "mem_mb": round(mem_mb, 1),
        "declared_mem_mb": round(declared_mem_mb, 1),
        "declared_cpus": round(declared_cpus, 2),
    }


def sample_once(args: argparse.Namespace) -> list[dict]:
    sessions = _db_sessions(args.db_container, args.db_user, args.db_name)
    containers = _docker_containers()
    stats = _docker_stats()
    payloads = []
    for session in sessions:
        if session["status"] not in ("starting", "running"):
            continue
        payload = _session_payload(session, containers, stats)
        if payload is not None:
            payloads.append(payload)
    return payloads


def _append(path: Path, payloads: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for payload in payloads:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def _load(path: Path, days: int) -> list[dict]:
    cutoff = datetime.now(UTC) - timedelta(days=days)
    rows = []
    if not path.is_file():
        return rows
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                timestamp = datetime.fromisoformat(row["ts"])
            except (ValueError, KeyError):
                continue
            if timestamp >= cutoff:
                rows.append(row)
    return rows


def report(path: Path, days: int, min_sessions: int) -> list[dict]:
    rows = _load(path, days)
    by_lab: dict[str, list[dict]] = {}
    for row in rows:
        by_lab.setdefault(row["lab_slug"], []).append(row)

    report_rows = []
    for lab_slug, samples in sorted(by_lab.items()):
        session_ids = {sample["session_id"] for sample in samples}
        if len(session_ids) < min_sessions:
            continue
        boots_by_session: dict[int, float] = {}
        for sample in samples:
            if sample.get("boot_seconds") is None:
                continue
            current = boots_by_session.get(sample["session_id"])
            if current is None or sample["boot_seconds"] < current:
                boots_by_session[sample["session_id"]] = sample["boot_seconds"]
        boots = list(boots_by_session.values())
        mem = [float(sample["mem_mb"]) for sample in samples if sample["mem_mb"] > 0]
        cpu = [
            float(sample["cpu_percent"])
            for sample in samples
            if sample["cpu_percent"] > 0
        ]
        declared_mem = max(
            (float(sample["declared_mem_mb"]) for sample in samples), default=0.0
        )
        declared_cpu = max(
            (float(sample["declared_cpus"]) for sample in samples), default=0.0
        )
        ready_sessions = len(boots_by_session)
        boot_p95 = _percentile(boots, 0.95)
        mem_p95 = _percentile(mem, 0.95)
        cpu_p95 = _percentile(cpu, 0.95)
        recommendations = []

        if declared_mem <= 0:
            recommendations.append("set an explicit memory limit")
        elif mem_p95 is not None and mem_p95 > declared_mem * 0.85:
            target = max(128, int((mem_p95 * 1.25 + 31) // 32 * 32))
            recommendations.append(f"increase memory to {target} MB")
        elif (
            declared_mem > 256
            and mem_p95 is not None
            and declared_mem > mem_p95 * 2.0
        ):
            target = max(128, int((mem_p95 * 1.5 + 31) // 32 * 32))
            recommendations.append(f"reduce memory to {target} MB")

        if declared_cpu <= 0:
            recommendations.append("set an explicit CPU limit")
        elif cpu_p95 is not None and cpu_p95 > declared_cpu * 100 * 0.85:
            target = max(0.1, round(cpu_p95 / 100 * 1.25, 1))
            recommendations.append(f"increase CPU to {target} cores")
        elif (
            declared_cpu > 0.25
            and cpu_p95 is not None
            and declared_cpu > (cpu_p95 / 100) * 2.0
        ):
            target = max(0.1, round(cpu_p95 / 100 * 1.5, 1))
            recommendations.append(f"reduce CPU to {target} cores")

        if boot_p95 is not None and boot_p95 > 60:
            recommendations.append("prebuild image and review start order/healthcheck")
        if ready_sessions < len(session_ids):
            recommendations.append("investigate failed or slow starts")
        if not recommendations:
            recommendations.append("settings look proportionate")

        sample_count = len(session_ids)
        confidence = (
            "low" if sample_count < 5 else "medium" if sample_count < 20 else "high"
        )

        report_rows.append(
            {
                "lab_slug": lab_slug,
                "samples": len(samples),
                "sessions": sample_count,
                "confidence": confidence,
                "ready_sessions": ready_sessions,
                "ready_rate": round(ready_sessions / sample_count, 3),
                "boot_p50_seconds": round(_percentile(boots, 0.5) or 0, 1),
                "boot_p95_seconds": round(boot_p95 or 0, 1),
                "mem_p95_mb": round(mem_p95 or 0, 1),
                "declared_mem_mb": round(declared_mem, 1),
                "cpu_p95_percent": round(cpu_p95 or 0, 2),
                "declared_cpus": round(declared_cpu, 2),
                "recommendations": recommendations,
            }
        )
    return report_rows


def _print_report(rows: list[dict]) -> None:
    if not rows:
        print("no lab telemetry samples in the window")
        return
    print(
        "| Lab | Sessions | Confidence | Ready | Boot p50 | Boot p95 | Mem p95 | Mem limit | CPU p95 | CPU limit | Recommendation |"
    )
    print("|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for row in rows:
        print(
            f"| {row['lab_slug']} | {row['sessions']} | {row['confidence']} | "
            f"{row['ready_rate']:.0%} | "
            f"{row['boot_p50_seconds']:.1f}s | {row['boot_p95_seconds']:.1f}s | "
            f"{row['mem_p95_mb']:.0f} MB | {row['declared_mem_mb']:.0f} MB | "
            f"{row['cpu_p95_percent']:.1f}% | {row['declared_cpus']:.2f} | "
            f"{'; '.join(row['recommendations'])} |"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-container", default="ocr-db")
    parser.add_argument("--db-user", default="labuser")
    parser.add_argument("--db-name", default="labdb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sample_parser = subparsers.add_parser("sample", help="Append live samples.")
    sample_parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    sample_parser.add_argument("--once", action="store_true")
    sample_parser.add_argument("--interval", type=int, default=15)
    sample_parser.add_argument("--duration", type=int, default=0)

    report_parser = subparsers.add_parser("report", help="Aggregate samples.")
    report_parser.add_argument("--input", type=Path, default=DEFAULT_OUTPUT)
    report_parser.add_argument("--days", type=int, default=7)
    report_parser.add_argument("--min-sessions", type=int, default=1)
    report_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "sample":
        started = time.monotonic()
        while True:
            try:
                payloads = sample_once(args)
                _append(args.output, payloads)
                print(
                    f"sampled {len(payloads)} session(s) at "
                    f"{datetime.now(UTC).isoformat()}",
                    flush=True,
                )
            except Exception as exc:  # noqa: BLE001 - keep the sampler alive
                print(f"sample failed: {exc}", file=sys.stderr, flush=True)
            if args.once:
                return 0
            if args.duration and time.monotonic() - started >= args.duration:
                return 0
            time.sleep(max(1, args.interval))
    rows = report(args.input, args.days, args.min_sessions)
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        _print_report(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
