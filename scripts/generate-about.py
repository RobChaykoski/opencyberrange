#!/usr/bin/env python3
"""Generate the About inventory consumed by the in-app About page.

The output is committed so the About page works in an offline install:

  platform/backend/app/data/about/about.json
  platform/backend/app/data/about/licenses/*
  platform/backend/app/data/about/sbom/manifest.json

Run it after changing requirements, package.json/package-lock.json,
versions.yaml, the branding, or the licence notices. The SBOM JSON files are
generated separately (see the README in the sbom directory).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ABOUT_DIR = ROOT / "platform/backend/app/data/about"
LICENCES_DIR = ABOUT_DIR / "licenses"
SBOM_DIR = ABOUT_DIR / "sbom"

BACKEND_LICENCES = {
    "fastapi": "MIT",
    "uvicorn": "BSD-3-Clause",
    "sqlalchemy": "MIT",
    "psycopg": "LGPL-3.0-only",
    "pyjwt": "MIT",
    "pwdlib": "MIT",
    "bcrypt": "Apache-2.0",
    "python-multipart": "Apache-2.0",
    "pydantic": "MIT",
    "pydantic-settings": "MIT",
    "email-validator": "Unlicense / CC0-1.0",
    "pyyaml": "MIT",
    "docker": "Apache-2.0",
    "apscheduler": "MIT",
    "cryptography": "Apache-2.0 OR BSD-3-Clause",
    "requests": "Apache-2.0",
    "slowapi": "MIT",
    "fpdf2": "LGPL-3.0-only",
    "matplotlib": "PSF-based",
    "aiohttp": "Apache-2.0",
    "websocket-client": "Apache-2.0",
    "pywinrm": "MIT",
    "alembic": "MIT",
    "pyotp": "MIT",
    "redis": "MIT",
    "qrcode": "BSD",
}

IMAGE_LICENCES = [
    ("python:3.11-slim", "PSF plus Debian packages"),
    ("node:22-alpine", "Node.js MIT plus Alpine packages"),
    ("nginx:alpine", "BSD-2-Clause plus Alpine packages"),
    ("postgres:15-alpine", "PostgreSQL Licence plus Alpine packages"),
    ("redis:7.2-alpine", "BSD-3-Clause plus Alpine packages"),
    ("mysql:8.0", "GPL-2.0"),
    ("php:8.1-apache", "PHP Licence 3.01 plus Apache-2.0"),
    ("nginxinc/nginx-unprivileged:alpine", "BSD-2-Clause plus Alpine packages"),
    ("python:3.12-alpine", "PSF plus Alpine packages"),
    ("alpine:3.19", "Alpine package licences"),
    ("ubuntu:22.04", "Ubuntu/Debian package licences"),
    ("kalilinux/kali-rolling", "Kali/Debian package licences"),
    ("remnux/remnux-distro:noble", "REMnux/Debian package licences"),
    (
        "0x4d4c/inetsim@sha256:01fdf65489db7b9a77a33cc336ba1d5ddf23aded35eeb23f2c6455290ca595e8",
        "INetSim GPL-2.0 plus Debian packages",
    ),
    ("axllent/mailpit", "MIT"),
]

LAB_LICENCES = [
    ("Nmap", "GPL-2.0 / Nmap Public Source Licence terms"),
    ("SQLMap", "GPL-2.0"),
    ("Wireshark / tshark", "GPL-2.0"),
    ("Suricata", "GPL-2.0"),
    ("John the Ripper", "GPL-2.0"),
    ("Hydra", "AGPL-3.0"),
    ("Masscan", "AGPL-3.0"),
    ("Metasploit Framework", "BSD-3-Clause"),
    ("Impacket", "Apache-2.0"),
    ("Hashcat", "MIT"),
    ("Volatility 3", "Volatility Software License 1.0"),
    ("INetSim", "GPL-2.0"),
    ("Snap7 / libsnap7", "LGPL-3.0"),
    ("asyncua", "LGPL-3.0-or-later"),
    ("Scapy (build-time generators)", "GPL-2.0-only"),
    ("PyMySQL", "MIT"),
    ("Flask", "BSD-3-Clause"),
    ("pymodbus", "BSD-3-Clause"),
    ("paramiko", "LGPL-2.1"),
    ("PyCryptodome", "Public domain / BSD-2-Clause"),
]


def package_name(requirement: str) -> str:
    name = requirement.split("==", 1)[0].split(">=", 1)[0]
    name = name.split("[", 1)[0].strip()
    return name


def package_version(requirement: str) -> str:
    match = re.search(r"(?:==|>=)([^;]+)", requirement)
    return match.group(1).strip() if match else ""


def backend_components() -> list[dict[str, str]]:
    rows = []
    for line in (ROOT / "platform/backend/requirements.txt").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = package_name(line)
        rows.append(
            {
                "name": name,
                "version": package_version(line),
                "licence": BACKEND_LICENCES.get(name, "See THIRD_PARTY_NOTICES.md"),
                "scope": "backend runtime",
            }
        )
    return rows


def frontend_components() -> list[dict[str, str]]:
    package = json.loads((ROOT / "platform/frontend/package.json").read_text())
    lock = json.loads((ROOT / "platform/frontend/package-lock.json").read_text())
    packages = lock.get("packages") or {}
    rows = []
    for name in (package.get("dependencies") or {}):
        entry = packages.get(f"node_modules/{name}") or {}
        rows.append(
            {
                "name": name,
                "version": entry.get("version") or package["dependencies"][name],
                "licence": entry.get("license") or "See THIRD_PARTY_NOTICES.md",
                "scope": "frontend runtime",
            }
        )
    return rows


def copy_licences() -> list[dict[str, str]]:
    LICENCES_DIR.mkdir(parents=True, exist_ok=True)
    for old in LICENCES_DIR.iterdir():
        if old.is_file():
            old.unlink()
    documents = [
        ("LICENSE", "Project licence (PolyForm Noncommercial 1.0.0)"),
        ("NOTICE", "Copyright and required notice"),
        ("LICENSING.md", "Licensing summary"),
        ("BRANDING.md", "Branding and marks"),
        ("BUILD_NOTICE.md", "Build provenance"),
        ("THIRD_PARTY_NOTICES.md", "Third-party notices"),
    ]
    rows = []
    for name, label in documents:
        shutil.copy2(ROOT / name, LICENCES_DIR / name)
        rows.append({"label": label, "file": name})
    for path in sorted((ROOT / "THIRD_PARTY_LICENSES").glob("*")):
        if path.is_file():
            shutil.copy2(path, LICENCES_DIR / path.name)
            rows.append({"label": path.stem, "file": path.name})
    return rows


def sbom_manifest() -> list[dict[str, object]]:
    SBOM_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(SBOM_DIR.glob("*.json")):
        if path.name == "manifest.json":
            continue
        payload = path.read_bytes()
        label = {
            "backend.cdx.json": "Backend CycloneDX SBOM",
            "frontend.cdx.json": "Frontend CycloneDX SBOM",
        }.get(path.name, path.stem)
        rows.append(
            {
                "name": path.name,
                "label": label,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    (SBOM_DIR / "manifest.json").write_text(
        json.dumps({"files": rows}, indent=2) + "\n", encoding="utf-8"
    )
    return rows


def _git_revision() -> str:
    override = os.environ.get("BUILD_REVISION", "").strip()
    if override and override.lower() != "unknown":
        return override
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def build_metadata(platform: dict, runtime: dict) -> dict:
    """Build-time facts baked beside the inventory.

    Runtime values such as the live Python or PostgreSQL version are resolved
    by the About API. This file records what the release build was created from.
    """
    return {
        "version": platform.get("version", ""),
        "git_sha": _git_revision(),
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "release_date": platform.get("date", ""),
        "status": platform.get("status", ""),
        "python": str((runtime.get("python") or {}).get("current", "")),
        "node": str((runtime.get("node") or {}).get("current", "")),
        "postgres": str((runtime.get("postgres") or {}).get("current", "")),
        "redis": str((runtime.get("redis") or {}).get("current", "")),
    }


def main() -> int:
    versions = yaml.safe_load((ROOT / "versions.yaml").read_text(encoding="utf-8"))
    platform = versions.get("platform") or {}
    runtime = versions.get("runtime") or {}
    edition = (versions.get("editions") or {}).get("community_academic") or {}

    about = {
        "generated_for_release": platform.get("version", ""),
        "release_date": platform.get("date", ""),
        "platform": {
            "name": platform.get("name", "SWOCTS Cyber Range"),
            "version": platform.get("version", ""),
            "status": platform.get("status", ""),
            "edition": edition.get("name", "Community / Academic"),
            "python": str((runtime.get("python") or {}).get("current", "3.11")),
            "node": str((runtime.get("node") or {}).get("current", "22")),
            "postgres": str((runtime.get("postgres") or {}).get("current", "15")),
            "redis": str((runtime.get("redis") or {}).get("current", "7.2")),
        },
        "branding": {
            "product": "SWOCTS Cyber Range",
            "owner": "SWOCTS",
            "logo_designer": "Avery Chaykoski",
            "upstream": "OpenCyberRange",
            "software_licence": "PolyForm Noncommercial 1.0.0",
            "brand_note": (
                "The SWOCTS name and logo are owned by SWOCTS and were created and "
                "designed by Avery Chaykoski. They are brand assets, not software, "
                "and are not licensed under the PolyForm Noncommercial License 1.0.0."
            ),
        },
        "components": {
            "backend": backend_components(),
            "frontend": frontend_components(),
            "images": [
                {"name": name, "version": "", "licence": licence, "scope": "container image"}
                for name, licence in IMAGE_LICENCES
            ],
            "lab_toolchains": [
                {"name": name, "version": "", "licence": licence, "scope": "lab toolchain"}
                for name, licence in LAB_LICENCES
            ],
        },
        "licences": copy_licences(),
        "sbom": sbom_manifest(),
    }
    (ABOUT_DIR / "about.json").write_text(
        json.dumps(about, indent=2) + "\n", encoding="utf-8"
    )
    build = build_metadata(platform, runtime)
    (ABOUT_DIR / "build.json").write_text(
        json.dumps(build, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote {ABOUT_DIR / 'about.json'} "
        f"({len(about['components']['backend'])} backend, "
        f"{len(about['components']['frontend'])} frontend, "
        f"{len(about['licences'])} licence files, {len(about['sbom'])} SBOM files)"
    )
    print(
        f"Wrote {ABOUT_DIR / 'build.json'} "
        f"({build['version']}, {build['git_sha']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
