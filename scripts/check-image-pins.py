#!/usr/bin/env python3
"""Report unpinned upstream base images in lab Dockerfiles and compose files.

Locally built images (``ocr-*``, ``localhost/*``, ``stage-*``) and images pinned
by ``@sha256:`` are ignored. A bare tag such as ``ubuntu:22.04`` or
``python:3.11-slim`` is reported because the tag can move.

Usage:
    python scripts/check-image-pins.py
    python scripts/check-image-pins.py --strict
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"
FROM_RE = re.compile(r"^\s*FROM\s+([^\s]+)", re.IGNORECASE)


def is_local(image: str) -> bool:
    name = image.split("@", 1)[0]
    return (
        name.startswith(("ocr-", "ocr/", "localhost/", "stage-"))
        or name == "scratch"
    )


def is_pinned(image: str) -> bool:
    return "@sha256:" in image


def scan() -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for path in LABS.rglob("Dockerfile*"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            match = FROM_RE.match(line)
            if not match:
                continue
            image = match.group(1)
            if not is_local(image) and not is_pinned(image):
                findings.append((str(path.relative_to(ROOT)), image))
    for path in LABS.rglob("docker-compose*.yml"):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        for service in (data.get("services") or {}).values():
            if not isinstance(service, dict):
                continue
            image = service.get("image")
            if not image or service.get("build"):
                continue
            image = str(image)
            if not is_local(image) and not is_pinned(image):
                findings.append((str(path.relative_to(ROOT)), image))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    findings = scan()
    print(f"unpinned upstream image references: {len(findings)}")
    for path, image in findings:
        print(f"  {path}: {image}")
    return 1 if args.strict and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
