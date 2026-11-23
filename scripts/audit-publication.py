#!/usr/bin/env python3
"""Audit public documentation for infrastructure metadata and answer keys.

Two classes of material are treated as publication-sensitive:

* infrastructure metadata: real public/private addresses, internal hostnames,
  deployment usernames, and the private subnet;
* assessment answer keys: lab flags outside the lab definition and runtime.

The audit is intentionally path-aware. A flag is allowed in
``platform/labs/**/lab.yaml``, the compose file, and the container code that
serves it; it is not allowed in a workbook, lab README, manifest, or test.

Usage:
    python scripts/audit-publication.py --summary
    python scripts/audit-publication.py --json
    python scripts/audit-publication.py --index .local/publication-index.json
    python scripts/audit-publication.py --report docs/PUBLICATION-AUDIT.md
    python scripts/audit-publication.py --no-fail
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - CI installs PyYAML
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"

TEXT_SUFFIXES = {
    ".md",
    ".yaml",
    ".yml",
    ".py",
    ".sh",
    ".ps1",
    ".json",
    ".php",
    ".txt",
    ".example",
    ".env",
    ".conf",
    ".ini",
    ".toml",
    ".cfg",
    ".sql",
}
TEXT_NAMES = {".env.example", "Dockerfile"}

SKIP_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "wiki",
    "_site",
    "_site_ai",
    "_site_forensics",
    "_site_identity",
    "_site_linpt",
    "_site_malware",
    "_site_msfpt",
    "_site_netfor",
    "_site_osint",
    "_site_ot",
    "_site_swsec",
}

FLAG_RE = re.compile(r"\b(?:OCR|TRAILLINE)\{[A-Za-z0-9_]+\}")
PLACEHOLDER_RE = re.compile(
    r"(?i)(?:replace|change|example|your|sample|placeholder|todo|flag_here|"
    r"here|abc|xxx|\.\.\.|[<>])"
)

INFRASTRUCTURE_PATTERNS = (
    ("public_ip", re.compile(r"\b70\.54\.16\.7\b")),
    ("private_subnet", re.compile(r"\b172\.16\.16\.\d{1,3}(?:/\d{1,2})?\b")),
    ("platform_host", re.compile(r"\bctfd\.swocts\.com\b", re.IGNORECASE)),
    ("moodle_host", re.compile(r"\bmoodle\.swocts\.com\b", re.IGNORECASE)),
    ("auth_host", re.compile(r"\bauth\.swocts\.com\b", re.IGNORECASE)),
    ("legacy_platform_host", re.compile(r"\bocr\.swocts\.com\b", re.IGNORECASE)),
    ("deployment_alias", re.compile(r"\bocr-(?:prod|dev)\b", re.IGNORECASE)),
    ("deployment_user", re.compile(r"\bocrv2\b", re.IGNORECASE)),
    ("admin_email", re.compile(r"\badmin@swocts\.com\b", re.IGNORECASE)),
)

SECRET_PATTERNS = (
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "assigned_secret",
        re.compile(
            r"(?i)\b(?:client_secret|api[_-]?key|access[_-]?token|"
            r"bootstrap[_-]?token|password|secret)\b\s*[:=]\s*[\"']?"
            r"([A-Za-z0-9_./+=-]{16,})"
        ),
    ),
)

PUBLIC_ALLOWLIST = {
    "0.0.0.0",
    "1.1.1.1",
    "2.1.4.0",  # release version, not an address
    "8.8.4.4",
    "8.8.8.8",
    "9.9.9.9",
    "255.255.255.255",
}
DOCUMENTATION_NETWORKS = tuple(
    ipaddress.ip_network(value)
    for value in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")
)
PUBLICATION_DOC_PREFIXES = (
    "docs/",
    "deploy/",
    ".opencode/skills/documentation/",
)
PUBLICATION_ROOT_FILES = {"README.md", "SECURITY.md", "CHANGELOG.md"}


@dataclass
class Finding:
    category: str
    path: str
    line: int
    detail: str


def _tracked_files() -> list[Path]:
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
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
        except OSError:
            continue
        files.append(path)
    return files


def _lab_flags() -> dict[str, str]:
    flags: dict[str, str] = {}
    for path in LABS.rglob("lab.yaml"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        value = ""
        if yaml is not None:
            try:
                data = yaml.safe_load(text) or {}
                value = str(data.get("flag") or "").strip()
            except Exception:  # noqa: BLE001 - malformed YAML is a skipped lab
                value = ""
        if not value:
            match = re.search(r"(?m)^flag:\s*[\"']?([^\"'\n]+)", text)
            value = match.group(1).strip() if match else ""
        if value:
            flags[value] = path.parent.name
    return flags


def _relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _allowed_flag_path(name: str) -> bool:
    # The OSINT external-target registry is runtime lab data: the marker is
    # served to the lab, not printed in a workbook.
    if name == "platform/backend/app/data/external-targets.yaml":
        return True
    if not name.startswith("platform/labs/"):
        return False
    return name.endswith(
        (
            "/lab.yaml",
            "/docker-compose.yml",
            ".py",
            ".sh",
            ".ps1",
            ".json",
            ".php",
            ".sql",
            ".env",
        )
    ) or "/containers/" in name or "/_shared/" in name


def _publication_doc(name: str) -> bool:
    """Paths where a flag or answer key must never appear."""
    return (
        name.startswith(PUBLICATION_DOC_PREFIXES)
        or name in PUBLICATION_ROOT_FILES
        or name.endswith("/README.md")
        or "/ctf/" in name
    )


def _infrastructure_doc(name: str) -> bool:
    """Paths where a real address or secret should not appear."""
    return name.startswith(PUBLICATION_DOC_PREFIXES) or name in PUBLICATION_ROOT_FILES


def _line_for(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _scan_public_ipv4(path: Path, text: str, findings: list[Finding]) -> None:
    name = _relative(path)
    if not _infrastructure_doc(name):
        return
    for match in re.finditer(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text):
        value = match.group(0)
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            continue
        if not isinstance(address, ipaddress.IPv4Address):
            continue
        if address.is_private or address.is_loopback or address.is_link_local:
            continue
        if address.is_multicast or address.is_reserved or address.is_unspecified:
            continue
        if str(address) in PUBLIC_ALLOWLIST:
            continue
        if any(address in network for network in DOCUMENTATION_NETWORKS):
            continue
        findings.append(
            Finding(
                "public_ip",
                name,
                _line_for(text, match.start()),
                "Public address outside the documentation ranges.",
            )
        )


def audit() -> tuple[list[Finding], dict[str, str]]:
    flags = _lab_flags()
    findings: list[Finding] = []

    for path in _tracked_files():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        relative = _relative(path)

        for flag in flags:
            if flag not in text:
                continue
            if _allowed_flag_path(relative):
                continue
            for match in re.finditer(re.escape(flag), text):
                findings.append(
                    Finding(
                        "flag",
                        relative,
                        _line_for(text, match.start()),
                        f"Lab flag for {flags[flag]} outside the lab definition/runtime.",
                    )
                )

        if _publication_doc(relative):
            for match in FLAG_RE.finditer(text):
                value = match.group(0)
                if value in flags or PLACEHOLDER_RE.search(value):
                    continue
                findings.append(
                    Finding(
                        "flag",
                        relative,
                        _line_for(text, match.start()),
                        "Actual-looking assessment flag in documentation.",
                    )
                )

        for category, pattern in INFRASTRUCTURE_PATTERNS:
            for match in pattern.finditer(text):
                findings.append(
                    Finding(
                        category,
                        relative,
                        _line_for(text, match.start()),
                        "Real infrastructure value in a tracked file.",
                    )
                )

        _scan_public_ipv4(path, text, findings)

        if _infrastructure_doc(relative):
            for category, pattern in SECRET_PATTERNS:
                for match in pattern.finditer(text):
                    value = match.group(1) if match.lastindex else match.group(0)
                    if PLACEHOLDER_RE.search(value):
                        continue
                    # Assignment-shaped code is not a leaked credential.
                    if any(token in value for token in ("(", ")", "$", "hash_", "getenv")):
                        continue
                    findings.append(
                        Finding(
                            "secret",
                            relative,
                            _line_for(text, match.start()),
                            f"Possible {category} in documentation.",
                        )
                    )

    findings.sort(key=lambda item: (item.category, item.path, item.line))
    return findings, flags


def _write_index(path: Path, findings: list[Finding], flags: dict[str, str]) -> None:
    index = {
        "generated_at": datetime.now(UTC).isoformat(),
        "lab_flags": {slug: flag for flag, slug in sorted(flags.items(), key=lambda item: item[1])},
        "flag_documentation_leaks": sorted(
            {finding.path for finding in findings if finding.category == "flag"}
        ),
        "findings": [
            {
                "category": finding.category,
                "path": finding.path,
                "line": finding.line,
                "detail": finding.detail,
            }
            for finding in findings
        ],
    }
    # The index is local-only and may contain real flag values. Keep the
    # findings list redacted; the lab_flags map is the operator key.
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(path: Path, findings: list[Finding], flags: dict[str, str]) -> None:
    by_category = Counter(finding.category for finding in findings)
    by_file = Counter(finding.path for finding in findings)
    lines = [
        "# Publication audit",
        "",
        "Generated from the tracked working tree. This report contains no flag",
        "values and no raw addresses.",
        "",
        "| Category | Findings |",
        "|---|---:|",
    ]
    for category, count in sorted(by_category.items()):
        lines.append(f"| `{category}` | {count} |")
    lines += [
        "",
        f"Lab flags indexed: **{len(flags)}**",
        "",
        "## Files with findings",
        "",
        "| File | Findings |",
        "|---|---:|",
    ]
    for name, count in by_file.most_common(50):
        lines.append(f"| `{name}` | {count} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print findings as JSON.")
    parser.add_argument("--summary", action="store_true", help="Print a short summary.")
    parser.add_argument("--index", type=Path, help="Write a local flag/location index.")
    parser.add_argument("--report", type=Path, help="Write a Markdown report.")
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Return 0 even when findings exist (reporting mode).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include every finding in the text output (default: first 80).",
    )
    args = parser.parse_args()

    findings, flags = audit()

    if args.index:
        _write_index(args.index, findings, flags)
    if args.report:
        _write_report(args.report, findings, flags)

    if args.json:
        print(
            json.dumps(
                {
                    "generated_at": datetime.now(UTC).isoformat(),
                    "lab_flags": len(flags),
                    "findings": [
                        {
                            **asdict(finding),
                            "value": "<redacted>",
                        }
                        for finding in findings
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        by_category = Counter(finding.category for finding in findings)
        print(
            f"publication audit: {len(findings)} finding(s) "
            f"across {len({finding.path for finding in findings})} file(s); "
            f"{len(flags)} lab flag(s) indexed"
        )
        for category, count in sorted(by_category.items()):
            print(f"  {category}: {count}")
        visible = findings if args.all else findings[:80]
        for finding in visible:
            print(f"  {finding.path}:{finding.line}: {finding.category} ({finding.detail})")
        if not args.all and len(findings) > len(visible):
            print(f"  ... {len(findings) - len(visible)} more; use --all or --json")

    if findings and not args.no_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
