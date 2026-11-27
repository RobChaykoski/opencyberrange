#!/usr/bin/env python3
"""Pin the dominant upstream lab base images by manifest digest.

Only Dockerfile ``FROM`` lines are rewritten. Compose ``image:`` lines are left
for a separate pass because a service may combine ``build:`` with a local tag.

Usage:
    python scripts/pin_lab_base_images.py --check
    python scripts/pin_lab_base_images.py --write
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"

DIGESTS = {
    "ubuntu:22.04": "sha256:b000e69a50ff940390233025e7a337fb8469b509e2334fa4d018ac30f3e18cdb",
    "ubuntu:24.04": "sha256:562111b88caa79c71391c0c4d3c2114a7d5c35915c20561fd893cb1e07929e6b",
    "python:3.11-slim": "sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c",
    "python:3.12-slim": "sha256:191083cdf6c7bda8c76158983163ead5d5cf7b77cf3033e805bb0f5296f51b4b",
    "python:3.12-alpine": "sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89",
    "alpine:3.19": "sha256:6baf43584bcb78f2e5847d1de515f23499913ac9f12bdf834811a3145eb11ca1",
    "alpine:3.18": "sha256:de0eb0b3f2a47ba1eb89389859a9bd88b28e82f5826b6969ad604979713c2d4f",
    "alpine:3.20": "sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc",
    "debian:bookworm-slim": "sha256:e67eeead736ff7bbe258ef088bff683635c561b1fcfefad0806c1df4ab49ce0e",
    "kalilinux/kali-rolling": "sha256:69a9a33d98a584a537bd0f7144d20c3b6d23f3bafa9ffcf0cadf4c5f186d02ff",
    "osixia/openldap:1.5.0": "sha256:18742e9c449c9c1afe129d3f2f3ee15fb34cc43e5f940a20f3399728f41d7c28",
    "mysql:8.0": "sha256:7dcddc01f13bab2f15cde676d44d01f61fc9f99fe7785e86196dfc07d358ae2b",
    "php:8.1-apache": "sha256:72f0c0134922985022d55a39b0390d35dc7a10e961aa6c44fa35b4c3102f4268",
    "nginx:alpine": "sha256:7fc0fb4af7bf006aeb31aea88069976060f8f0a0a86b667126742cc17f4e31ae",
    "nginxinc/nginx-unprivileged:alpine": "sha256:b5047b9b76845eac124358373c6852377c52e4b05834a47647e955dd91cb8f1e",
}
FROM_RE = re.compile(r"^(\s*FROM\s+)([^\s]+)(.*)$", re.IGNORECASE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("choose --check or --write")

    changed = 0
    files = 0
    for path in sorted(LABS.rglob("Dockerfile*")):
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        updated = []
        touched = False
        for line in lines:
            match = FROM_RE.match(line)
            if not match:
                updated.append(line)
                continue
            image = match.group(2)
            digest = DIGESTS.get(image)
            if not digest:
                updated.append(line)
                continue
            updated.append(f"{match.group(1)}{image}@{digest}{match.group(3)}")
            touched = True
            changed += 1
        if touched:
            files += 1
            if args.write:
                path.write_text("\n".join(updated) + "\n", encoding="utf-8", newline="\n")

    print(f"pinned_refs={changed} files={files} written={args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
