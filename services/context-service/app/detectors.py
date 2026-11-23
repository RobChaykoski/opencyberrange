"""Detectors for publication-sensitive content.

The same rules are used by the production context service (`POST /scan`) and
by the repository publication audit. They deliberately return a redacted value
in every serialized result: a DLP response must not become the next leak.
"""

from __future__ import annotations

import ipaddress
import re
from collections.abc import Iterable
from dataclasses import dataclass, field

DOCUMENTATION_RANGES = tuple(
    ipaddress.ip_network(value)
    for value in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")
)
PUBLIC_ALLOWLIST = {
    "0.0.0.0",
    "1.1.1.1",
    "8.8.4.4",
    "8.8.8.8",
    "9.9.9.9",
    "255.255.255.255",
}

IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
FLAG_RE = re.compile(r"\b(?:OCR|TRAILLINE)\{[A-Za-z0-9_]+\}")
INTERNAL_HOST_RE = re.compile(
    r"\b(?:[a-z0-9-]+\.)+(?:internal|corp|lan|local)\b", re.IGNORECASE
)
PLACEHOLDER_RE = re.compile(
    r"(?i)(?:replace|change|example|your|sample|placeholder|todo|xxx|\.\.\.|[<>])"
)

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("provider_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    (
        "assigned_secret",
        re.compile(
            r"(?i)\b(?:client_secret|api[_-]?key|access[_-]?token|bootstrap[_-]?token|"
            r"password|secret)\b\s*[:=]\s*[\"']?([A-Za-z0-9_./+=-]{16,})"
        ),
    ),
)


@dataclass
class Finding:
    category: str
    severity: str
    raw: str
    start: int
    end: int
    note: str = ""

    @property
    def redacted(self) -> str:
        if self.category == "flag":
            prefix = self.raw.split("{", 1)[0]
            return f"{prefix}{{<redacted>}}"
        if self.category.endswith("_ip"):
            return "<redacted-ip>"
        if self.category == "internal_hostname":
            return "<redacted-host>"
        return "<redacted>"

    def as_dict(self) -> dict:
        return {
            "category": self.category,
            "severity": self.severity,
            "value": self.redacted,
            "note": self.note,
        }


@dataclass
class ScanResult:
    findings: list[Finding] = field(default_factory=list)
    redacted_text: str = ""

    @property
    def categories(self) -> set[str]:
        return {finding.category for finding in self.findings}

    @property
    def classification(self) -> str:
        if self.categories & {"flag", "secret"}:
            return "restricted"
        if self.categories & {"private_ip", "public_ip", "internal_hostname"}:
            return "confidential"
        return "internal"

    @property
    def publication_safe(self) -> bool:
        return not self.findings

    @property
    def contains_infrastructure_metadata(self) -> bool:
        return bool(
            self.categories & {"private_ip", "public_ip", "internal_hostname"}
        )

    @property
    def contains_assessment_answer_key(self) -> bool:
        return "flag" in self.categories

    @property
    def contains_secrets(self) -> bool:
        return "secret" in self.categories

    def as_dict(self) -> dict:
        return {
            "classification": self.classification,
            "publication_safe": self.publication_safe,
            "contains_infrastructure_metadata": self.contains_infrastructure_metadata,
            "contains_assessment_answer_key": self.contains_assessment_answer_key,
            "contains_secrets": self.contains_secrets,
            "findings": [finding.as_dict() for finding in self.findings],
            "redacted_text": self.redacted_text,
        }


def _is_documentation_ip(value: ipaddress.IPv4Address) -> bool:
    return any(value in network for network in DOCUMENTATION_RANGES)


def _scan_ip(value: str, start: int, findings: list[Finding]) -> None:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return
    if not isinstance(address, ipaddress.IPv4Address):
        return
    if address.is_loopback or address.is_unspecified or address.is_multicast:
        return
    if address.is_link_local or _is_documentation_ip(address):
        return
    if str(address) in PUBLIC_ALLOWLIST:
        return
    if address.is_private:
        findings.append(
            Finding(
                "private_ip",
                "high",
                value,
                start,
                start + len(value),
                "Private address can disclose the deployment topology.",
            )
        )
        return
    findings.append(
        Finding(
            "public_ip",
            "medium",
            value,
            start,
            start + len(value),
            "Public address should be reviewed before publication.",
        )
    )


def _scan_secrets(text: str, findings: list[Finding]) -> None:
    for name, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(1) if match.lastindex else match.group(0)
            if PLACEHOLDER_RE.search(value):
                continue
            findings.append(
                Finding(
                    "secret",
                    "critical",
                    value,
                    match.start(1) if match.lastindex else match.start(),
                    match.end(1) if match.lastindex else match.end(),
                    f"Possible {name}; rotate and remove before publication.",
                )
            )


def scan_text(text: str, extra_hosts: Iterable[str] = ()) -> ScanResult:
    findings: list[Finding] = []
    for match in IPV4_RE.finditer(text):
        _scan_ip(match.group(0), match.start(), findings)
    for match in FLAG_RE.finditer(text):
        if not PLACEHOLDER_RE.search(match.group(0)):
            findings.append(
                Finding(
                    "flag",
                    "high",
                    match.group(0),
                    match.start(),
                    match.end(),
                    "Assessment answer key.",
                )
            )
    for match in INTERNAL_HOST_RE.finditer(text):
        findings.append(
            Finding(
                "internal_hostname",
                "medium",
                match.group(0),
                match.start(),
                match.end(),
                "Internal hostname can disclose the deployment topology.",
            )
        )
    for host in extra_hosts:
        host = host.strip().lower()
        if not host:
            continue
        for match in re.finditer(re.escape(host), text, re.IGNORECASE):
            findings.append(
                Finding(
                    "internal_hostname",
                    "medium",
                    match.group(0),
                    match.start(),
                    match.end(),
                    "Configured sensitive hostname.",
                )
            )
    _scan_secrets(text, findings)
    findings.sort(key=lambda finding: (finding.start, finding.end))

    redacted = text
    for finding in sorted(findings, key=lambda item: item.start, reverse=True):
        redacted = (
            redacted[: finding.start]
            + f"[REDACTED:{finding.category}]"
            + redacted[finding.end :]
        )
    return ScanResult(findings=findings, redacted_text=redacted)
