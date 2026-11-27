#!/usr/bin/env python3
"""Propose flag-render metadata for Dockerfile-baked labs.

A lab is a candidate when its Dockerfile writes the graded flag to a file with a
simple ``RUN echo/printf`` and ends with a JSON or shell-form ``CMD``. Ambiguous
labs (ENTRYPOINT, multiple paths, no CMD) are reported, not changed.

Usage:
    python scripts/infer_flag_render.py --check
    python scripts/infer_flag_render.py --write
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"
FLAG_WRITE_RE = re.compile(
    r"""RUN\s+(?:echo|printf)\s+['"]?OCR\{[^}]+\}['"]?\s*>\s*([^\s&;]+)""",
    re.IGNORECASE,
)
CHOWN_RE = re.compile(r"chown\s+(?!-R\b)([\w.-]+:[\w.-]+)\s+([^\s&;]+)")
CMD_JSON_RE = re.compile(r"^\s*CMD\s+(\[.*\])\s*$", re.IGNORECASE)
CMD_SHELL_RE = re.compile(r"^\s*CMD\s+(.+)$", re.IGNORECASE)
ENTRYPOINT_RE = re.compile(r"^\s*ENTRYPOINT\s+", re.IGNORECASE)


def _parse_list(value: str) -> list[str] | None:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, list) and parsed and all(isinstance(part, str) for part in parsed):
        return parsed
    return None


def parse_command(text: str) -> list[str] | None:
    """Return the runtime command, combining ENTRYPOINT and CMD where safe."""
    entrypoint = None
    cmd = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("ENTRYPOINT "):
            value = stripped.split(None, 1)[1].strip()
            entrypoint = _parse_list(value) if value.startswith("[") else ["/bin/sh", "-c", value]
        elif stripped.upper().startswith("CMD "):
            value = stripped.split(None, 1)[1].strip()
            if value.startswith("["):
                cmd = _parse_list(value)
            elif "$" not in value:
                cmd = ["/bin/sh", "-c", value]
    if entrypoint and cmd:
        if entrypoint[:2] == ["/bin/sh", "-c"]:
            return entrypoint
        if cmd[:2] == ["/bin/sh", "-c"]:
            return None
        return entrypoint + cmd
    return entrypoint or cmd


def parse_service(lab_dir: Path, dockerfile: Path, compose: dict) -> str | None:
    candidates = []
    for name, service in (compose.get("services") or {}).items():
        if not isinstance(service, dict):
            continue
        build = service.get("build")
        if not isinstance(build, dict):
            continue
        context = (lab_dir / str(build.get("context") or ".")).resolve()
        try:
            dockerfile.resolve().relative_to(context)
        except ValueError:
            continue
        candidates.append(name)
    return candidates[0] if len(candidates) == 1 else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("choose --check or --write")

    confident = []
    skipped = []
    for lab_path in sorted(LABS.rglob("lab.yaml")):
        lab = yaml.safe_load(lab_path.read_text(encoding="utf-8")) or {}
        if lab.get("flag_path"):
            continue
        flag = str(lab.get("flag") or "")
        if not flag:
            continue
        compose_path = lab_path.parent / "docker-compose.yml"
        if not compose_path.is_file():
            continue
        try:
            compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if not isinstance(compose, dict):
            continue
        proposals = []
        for dockerfile in lab_path.parent.rglob("Dockerfile*"):
            if not dockerfile.is_file():
                continue
            text = dockerfile.read_text(encoding="utf-8", errors="ignore")
            writes = sorted(set(FLAG_WRITE_RE.findall(text)))
            if not writes:
                continue
            flag_paths = [item for item in writes if item.endswith("/flag.txt")]
            if len(writes) == 1:
                path = writes[0]
            elif len(flag_paths) == 1:
                path = flag_paths[0]
            else:
                continue
            command = parse_command(text)
            if not command:
                continue
            # A non-root USER can only write its own home or /tmp.
            users = [
                line.split(None, 1)[1].strip()
                for line in text.splitlines()
                if line.strip().upper().startswith("USER ")
            ]
            user = users[-1] if users else "root"
            nonroot = user.lower() not in {"root", "0"}
            if nonroot and not path.startswith((f"/home/{user}/", "/tmp/")):
                continue
            service = parse_service(lab_path.parent, dockerfile, compose)
            if not service:
                continue
            owners = [owner for owner, target in CHOWN_RE.findall(text) if target == path]
            owner = owners[0] if len(owners) == 1 else ""
            if not owner and path.startswith("/home/"):
                parts = path.split("/")
                if len(parts) > 2 and parts[2]:
                    owner = f"{parts[2]}:{parts[2]}"
            proposals.append(
                {
                    "path": path,
                    "service": service,
                    "command": command,
                    "owner": owner,
                }
            )
        if len(proposals) != 1:
            skipped.append((lab_path.parent.name, f"{len(proposals)} proposals"))
            continue
        proposal = proposals[0]
        if not proposal["path"].startswith("/"):
            skipped.append((lab_path.parent.name, "relative path"))
            continue
        confident.append((lab_path, lab, proposal))

    print(f"confident={len(confident)} skipped={len(skipped)}")
    for lab_path, lab, proposal in confident[:40]:
        print(f"  {lab_path.parent.name}: {proposal}")
    for slug, reason in skipped[:20]:
        print(f"  SKIP {slug}: {reason}")

    if args.write:
        for lab_path, lab, proposal in confident:
            text = lab_path.read_text(encoding="utf-8")
            if "flag_path:" in text:
                continue
            lines = text.splitlines()
            insert_at = None
            for index, line in enumerate(lines):
                if line.startswith("flag:"):
                    insert_at = index + 1
                    break
            if insert_at is None:
                continue
            block = [
                f'flag_path: "{proposal["path"]}"',
                f'flag_service: "{proposal["service"]}"',
                f"flag_command: {json.dumps(proposal['command'])}",
            ]
            if proposal["owner"]:
                block.append(f'flag_owner: "{proposal["owner"]}"')
            lines[insert_at:insert_at] = block
            lab_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print("written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
