#!/usr/bin/env python3
"""Reject Windows media and embedded activation material.

The repository ships deployment code, not operating-system images or product
keys. This audit fails on:

* Windows media files by extension or magic bytes (ISO, VHD/VHDX, VMDK, QCOW2,
  OVA/OVF, WIM/ESD, VDI);
* Windows product keys in source, config, or unattend files;
* `slmgr /ipk`, `ospp /inpkey`, `changepk /ProductKey`, or DISM product-key
  injection;
* non-empty `product_key` assignments.

Institution-owned media and license details belong in a private artifact store
or secret manager, never in git.

Usage:
    python scripts/check-windows-artifacts.py
    python scripts/check-windows-artifacts.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_SUFFIXES = {
    ".iso",
    ".vhd",
    ".vhdx",
    ".vmdk",
    ".qcow2",
    ".ova",
    ".ovf",
    ".wim",
    ".esd",
    ".vdi",
}

MAGIC_CHECKS = (
    ("iso9660", b"CD001", 0x8001),
    ("vhd", b"conectix", -512),
    ("vhdx", b"vhdxfile", 0),
    ("vmdk", b"KDMV", 0),
    ("qcow2", b"QFI\xfb", 0),
    ("wim", b"MSWIM\x00\x00\x00", 0),
)

KEY_RE = re.compile(r"\b(?:[A-Z0-9]{5}-){4}[A-Z0-9]{5}\b")
PLACEHOLDER_RE = re.compile(
    r"(?i)(?:X{5}|0{5}|1{5}|EXAMPLE|PLACEHOLDER|REDACTED|CHANGE|REPLACE|"
    r"YOUR|SET_ME|\.\.\.|[<>]|\$\{)"
)

ACTIVATION_PATTERNS = (
    (
        "slmgr_ipk",
        re.compile(
            r"(?i)\b(?:slmgr(?:\.vbs)?|cscript(?:\.exe)?[^\n]*?slmgr(?:\.vbs)?)"
            r"\b[^\n]*?/ipk\b"
        ),
    ),
    ("ospp_inpkey", re.compile(r"(?i)\bospp(?:\.vbs)?\b[^\n]*?/inpkey\b")),
    (
        "changepk",
        re.compile(r"(?i)\bchangepk(?:\.exe)?\b[^\n]*?/ProductKey\b"),
    ),
    (
        "dism_productkey",
        re.compile(r"(?i)\bdism(?:\.exe)?\b[^\n]*?/Set-ProductKey\b"),
    ),
    (
        "unattend_productkey",
        re.compile(r"(?i)<ProductKey>\s*[^<\s][^<]*</ProductKey>"),
    ),
    (
        "product_key_assignment",
        re.compile(
            r"(?i)\b(?:product_key|windows_product_key|windows_license_key)\b"
            r"\s*[:=]\s*[\"']?([A-Z0-9-]{20,})"
        ),
    ),
)

SKIP_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "_site",
    "wiki",
}
SKIP_NAMES = {
    "package-lock.json",
    "package-lock.json.asc",
}
TEXT_SUFFIXES = {
    ".md",
    ".yaml",
    ".yml",
    ".py",
    ".ps1",
    ".sh",
    ".json",
    ".xml",
    ".txt",
    ".example",
    ".env",
    ".conf",
    ".ini",
    ".toml",
    ".cfg",
    ".hcl",
    ".tf",
    ".pkr",
}
ALLOW_ACTIVATION_PATHS = {
    "docs/WINDOWS-ARTIFACT-POLICY.md",
    "scripts/check-windows-artifacts.py",
}


@dataclass
class Finding:
    category: str
    path: str
    detail: str


def _files() -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        output = "\n".join(
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file()
        )
    files = []
    for name in output.splitlines():
        path = ROOT / name
        if not path.is_file():
            continue
        if any(part.lower() in SKIP_PARTS for part in path.parts):
            continue
        if path.name in SKIP_NAMES:
            continue
        files.append(path)
    return files


def _relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _magic_findings(path: Path) -> list[Finding]:
    findings = []
    try:
        size = path.stat().st_size
    except OSError:
        return findings
    if size < 1024:
        return findings
    try:
        with path.open("rb") as handle:
            head = handle.read(16)
            for category, magic, offset in MAGIC_CHECKS:
                if offset >= 0:
                    if offset + len(magic) > size:
                        continue
                    handle.seek(offset)
                    if handle.read(len(magic)) == magic:
                        findings.append(
                            Finding(category, _relative(path), "Windows media magic bytes")
                        )
                        break
                else:
                    handle.seek(max(0, size + offset))
                    if handle.read(len(magic)) == magic:
                        findings.append(
                            Finding(category, _relative(path), "Windows media footer")
                        )
                        break
    except OSError:
        pass
    return findings


def _text_findings(path: Path, text: str) -> list[Finding]:
    findings = []
    relative = _relative(path)
    allow_activation = relative in ALLOW_ACTIVATION_PATHS

    for match in KEY_RE.finditer(text):
        value = match.group(0)
        if PLACEHOLDER_RE.search(value):
            continue
        findings.append(
            Finding("product_key", relative, "Windows product key in source")
        )

    if allow_activation:
        return findings

    for category, pattern in ACTIVATION_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(1) if match.lastindex else match.group(0)
            if PLACEHOLDER_RE.search(value):
                continue
            findings.append(Finding(category, relative, "Activation key injection"))
            break
    return findings


def audit() -> list[Finding]:
    findings = []
    for path in _files():
        relative = _relative(path)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(
                Finding("media", relative, f"forbidden extension {path.suffix.lower()}")
            )
            continue
        findings.extend(_magic_findings(path))
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".env.example":
            continue
        try:
            if path.stat().st_size > 4_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        findings.extend(_text_findings(path, text))
    findings.sort(key=lambda item: (item.category, item.path))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    findings = audit()
    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], indent=2))
    else:
        print(f"Windows artifact audit: {len(findings)} finding(s)")
        for finding in findings:
            print(f"  {finding.path}: {finding.category} ({finding.detail})")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
