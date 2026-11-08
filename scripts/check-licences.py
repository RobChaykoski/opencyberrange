#!/usr/bin/env python3
"""Licence-compliance guard for the core platform and repository inventory.

This is a regression check, not legal advice. It fails on the specific
conditions the project has decided are not acceptable:

- the required notice files are missing;
- a licence text referenced by THIRD_PARTY_NOTICES.md is missing;
- the core backend requirements add AGPL/GPL libraries that are not part of
  the documented mixed-licence lab generators;
- Redis is not pinned to the BSD-3-Clause 7.2 line;
- the INetSim image floats on ``latest``;
- a Scapy-importing lab generator lacks its GPL-2.0 SPDX header;
- a production frontend dependency declares GPL/AGPL/SSPL/RSAL;
- the Microsoft symbol artifact or the RockYou wordlist is re-vendored.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def warn(message: str) -> None:
    WARNINGS.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# 1. Required project notice files.
for name in (
    "LICENSE",
    "NOTICE",
    "LICENSING.md",
    "BRANDING.md",
    "BUILD_NOTICE.md",
    "THIRD_PARTY_NOTICES.md",
    "THIRD_PARTY_LICENSES",
):
    if not (ROOT / name).exists():
        fail(f"missing required notice path: {name}")

# 1b. The About inventory and its generated files must be present.
about_path = ROOT / "platform/backend/app/data/about/about.json"
licences_dir = ROOT / "platform/backend/app/data/about/licenses"
sbom_dir = ROOT / "platform/backend/app/data/about/sbom"
if not about_path.is_file():
    fail("About inventory is missing: platform/backend/app/data/about/about.json")
else:
    about = json.loads(read(about_path))
    branding = about.get("branding") or {}
    if branding.get("owner") != "SWOCTS":
        fail("About inventory does not record SWOCTS as the brand owner")
    if branding.get("logo_designer") != "Avery Chaykoski":
        fail("About inventory does not credit Avery Chaykoski for the logo")
    if (about.get("privacy") or {}).get("admin_default") is not True:
        fail("About inventory does not record the admin privacy default")
    if not about.get("sbom"):
        fail("About inventory has no SBOM entries")
    for doc in about.get("licences") or []:
        if not (licences_dir / doc.get("file", "")).is_file():
            fail(f"About licence document is missing: {doc.get('file')}")
    for row in about.get("sbom") or []:
        if not (sbom_dir / row.get("name", "")).is_file():
            fail(f"About SBOM file is missing: {row.get('name')}")
if not (ROOT / "platform/backend/app/routers/about.py").is_file():
    fail("About API router is missing: platform/backend/app/routers/about.py")

# 2. Every licence text referenced by the inventory exists.
notices = read(ROOT / "THIRD_PARTY_NOTICES.md")
for match in re.finditer(r"THIRD_PARTY_LICENSES/([A-Za-z0-9._-]+)", notices):
    name = match.group(1)
    if not (ROOT / "THIRD_PARTY_LICENSES" / name).is_file():
        fail(f"THIRD_PARTY_NOTICES.md references missing text: {name}")

# 3. The core backend must not add AGPL/GPL libraries.
requirements = read(ROOT / "platform/backend/requirements.txt")
for package in ("pymupdf", "mysqlclient", "scapy"):
    if re.search(rf"^\s*{package}\b", requirements, re.IGNORECASE | re.MULTILINE):
        fail(
            f"forbidden core backend dependency: {package} "
            "(AGPL/GPL; use a permissive alternative or document a mixed-licence component)"
        )

# 4. Redis must stay on the BSD-3-Clause 7.2 line.
redis_files = (
    "platform/docker-compose.prod.yml",
    "scripts/install-platform.sh",
    "scripts/deploy-updates.sh",
)
for rel in redis_files:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing Redis pin file: {rel}")
        continue
    text = read(path)
    if "redis:7.2-alpine" not in text:
        fail(f"{rel} does not pin redis:7.2-alpine")
    if re.search(r"redis:7(?!\.2\b)", text):
        fail(f"{rel} contains a non-7.2 Redis image reference")
versions = read(ROOT / "versions.yaml")
if not re.search(r"redis:\s*\n\s+current:\s*[\"']?7\.2", versions):
    fail("versions.yaml does not record Redis 7.2")

# 5. The third-party INetSim image must be digest-pinned.
for path in ROOT.glob("platform/labs/**/Dockerfile*"):
    text = read(path)
    if "0x4d4c/inetsim:latest" in text:
        fail(f"{path.relative_to(ROOT)} uses the floating 0x4d4c/inetsim:latest tag")

# 6. Scapy-importing lab generators must carry the GPL-2.0 SPDX header.
for path in ROOT.glob("platform/labs/**/*.py"):
    text = read(path)
    if re.search(r"^\s*(?:from|import)\s+scapy\b", text, re.IGNORECASE | re.MULTILINE):
        if "SPDX-License-Identifier: GPL-2.0-only" not in text:
            fail(f"{path.relative_to(ROOT)} imports Scapy without the GPL-2.0 SPDX header")

# 7. Production frontend dependencies must not declare strong copyleft.
lock_path = ROOT / "platform/frontend/package-lock.json"
if lock_path.is_file():
    lock = json.loads(read(lock_path))
    for package_path, meta in (lock.get("packages") or {}).items():
        if not package_path:
            continue
        licence = meta.get("license") or ""
        if re.search(r"\b(?:AGPL|GPL|SSPL|RSAL)\b", licence):
            fail(f"frontend dependency {package_path} declares {licence}")

# 8. Do not re-vendor the Microsoft symbol table or the RockYou wordlist.
for path in ROOT.glob("platform/labs/**/symbols/**/*.json.xz"):
    fail(f"Microsoft symbol artifact is vendored again: {path.relative_to(ROOT)}")
rangebox = read(ROOT / "RangeBox/Dockerfile")
if "rockyou-75.txt" in rangebox:
    fail("RangeBox Dockerfile downloads the breach-derived RockYou wordlist")

# 9. The mixed-licence section must list the GPL generator scripts.
licensing = read(ROOT / "LICENSING.md")
if "GPL-2.0-only" not in licensing or "Scapy" not in licensing:
    fail("LICENSING.md does not document the GPL-2.0-only Scapy generators")

if WARNINGS:
    print("Licence warnings:")
    for message in WARNINGS:
        print(f"  WARN: {message}")

if ERRORS:
    print("Licence compliance: FAILED")
    for message in ERRORS:
        print(f"  ERROR: {message}")
    sys.exit(1)

print("Licence compliance: OK")
