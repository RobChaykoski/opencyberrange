"""Run the OpenCyberRange security checklist against the current delta.

The project software-security skill asks five questions of every change:

1. What does the attacker control?
2. Where does it go?
3. What check is missing or wrong?
4. What is the impact?
5. How do you prove it?

This script is the repeatable gate. It scans changed production code for the
high-value patterns from the skill and prints the manual checklist for the
parts a static scan cannot decide (permissions, authorization, data scope).

Usage:
    python scripts/security-delta-review.py
    python scripts/security-delta-review.py --base origin/main
    python scripts/security-delta-review.py --staged

Exit code 1 means a high-confidence finding needs review. Warnings do not fail
the run.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CODE_SUFFIXES = {
    ".py",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".vue",
    ".sh",
    ".yml",
    ".yaml",
    ".sql",
    ".html",
}
TEXT_SUFFIXES = CODE_SUFFIXES | {".md", ".txt", ".json", ".toml", ".ini", ".cfg"}
SKIP_PARTS = {
    ".git",
    "node_modules",
    "dist",
    "_site_manual_lite",
    "_site_highschool",
    "_site_webpt",
    ".venv",
    "__pycache__",
    ".opencode/skills",
}

SECRET_PATTERNS = [
    (
        "private key block",
        re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |PGP )?PRIVATE KEY-----"),
    ),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
]

HIGH_CODE_PATTERNS = [
    ("shell execution", re.compile(r"shell\s*=\s*True")),
    ("os.system", re.compile(r"\bos\.system\s*\(")),
    ("eval", re.compile(r"(?<![\w.])eval\s*\(")),
    ("exec", re.compile(r"(?<![\w.])exec\s*\(")),
    ("pickle deserialization", re.compile(r"\bpickle\.loads?\s*\(")),
    ("unsafe yaml load", re.compile(r"\byaml\.load\s*\((?![^\n]*SafeLoader)")),
    ("Vue v-html", re.compile(r"\bv-html\s*=")),
    ("innerHTML", re.compile(r"\.innerHTML\s*=")),
    ("TLS verification disabled", re.compile(r"\bverify\s*=\s*False\b")),
    ("wildcard CORS", re.compile(r"allow_origins\s*=\s*\[\s*['\"]\*['\"]\s*\]")),
    ("debug enabled", re.compile(r"\bDEBUG\s*=\s*True\b")),
]

WARN_CODE_PATTERNS = [
    ("raw HTML assignment", re.compile(r"dangerouslySetInnerHTML")),
    ("token in localStorage", re.compile(r"localStorage\.setItem\(\s*['\"]token['\"]")),
    ("SQL built with an f-string", re.compile(r"(?i)(?:execute|text)\s*\(\s*f['\"][^'\"]*(?:select|insert|update|delete)[^'\"]*\{")),
    ("SQL string concatenation", re.compile(r"(?i)(?:execute|text)\s*\(\s*['\"][^'\"]*(?:select|insert|update|delete)[^'\"]*['\"]\s*\+")),
    ("subprocess without an argument list", re.compile(r"subprocess\.(?:run|Popen|call|check_output)\([^\n]*shell\s*=\s*True")),
    ("HTTP error text rendered as HTML", re.compile(r"v-html\s*=\s*[\"'][^\"']*error")),
]


def _run(args: list[str]) -> str:
    result = subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def _changed_files(base: str | None, staged: bool) -> list[Path]:
    if staged:
        names = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"])
        names += _run(["git", "ls-files", "--others", "--exclude-standard"])
    elif base:
        names = _run(["git", "diff", "--name-only", "--diff-filter=ACMR", base])
        names += _run(["git", "ls-files", "--others", "--exclude-standard"])
    else:
        names = _run(["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD"])
        names += _run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"])
        names += _run(["git", "ls-files", "--others", "--exclude-standard"])

    files: list[Path] = []
    for name in sorted(set(filter(None, names.splitlines()))):
        normalized = name.replace("\\", "/")
        if normalized.endswith("scripts/security-delta-review.py"):
            continue
        path = ROOT / name
        if not path.is_file():
            continue
        if any(part in normalized for part in SKIP_PARTS):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        files.append(path)
    return files


def _is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(
        marker in lowered
        for marker in (
            "your-",
            "your_",
            "example",
            "changeme",
            "placeholder",
            "xxxx",
            "process.env",
            "os.environ",
            "settings.",
            "<",
            "$",
            "{",
        )
    )


def _scan_secrets(path: Path, lines: list[str]) -> list[tuple[str, int, str]]:
    findings: list[tuple[str, int, str]] = []
    for number, line in enumerate(lines, start=1):
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append((label, number, line.strip()[:160]))
        # Generic assignments are noisy in docs and tests. Keep them to code.
        if path.suffix.lower() in CODE_SUFFIXES:
            match = re.search(
                r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"]([^'\"]{8,})['\"]",
                line,
            )
            if match and not _is_placeholder(match.group(2)):
                findings.append(("credential-like assignment", number, line.strip()[:160]))
    return findings


def _is_suppressed(lines: list[str], number: int, label: str) -> bool:
    """Allow an explicit, auditable inline exception.

    A comment on the finding line or the two lines above can say
    ``security-delta: allow <label>`` (or just ``security-delta: allow``).
    The marker keeps the exception visible in review instead of hiding it in
    the scanner.
    """
    marker = "security-delta: allow"
    for text in lines[max(0, number - 3):number]:
        lowered = text.lower()
        if marker not in lowered:
            continue
        rest = lowered.split(marker, 1)[1].strip()
        if not rest or label.lower() in rest:
            return True
    return False


def _scan_code(path: Path, lines: list[str]) -> tuple[list[tuple[str, int, str]], list[tuple[str, int, str]]]:
    high: list[tuple[str, int, str]] = []
    warn: list[tuple[str, int, str]] = []
    for number, line in enumerate(lines, start=1):
        for label, pattern in HIGH_CODE_PATTERNS:
            if pattern.search(line) and not _is_suppressed(lines, number, label):
                high.append((label, number, line.strip()[:160]))
        for label, pattern in WARN_CODE_PATTERNS:
            if pattern.search(line) and not _is_suppressed(lines, number, label):
                warn.append((label, number, line.strip()[:160]))
    return high, warn


def main() -> int:
    parser = argparse.ArgumentParser(description="Security delta review")
    parser.add_argument("--base", default=None, help="Git base ref or SHA")
    parser.add_argument("--staged", action="store_true", help="Review staged and untracked files")
    args = parser.parse_args()

    files = _changed_files(args.base, args.staged)
    if not files:
        print("Security delta review: no changed text files.")
        return 0

    high_findings: list[tuple[Path, str, int, str]] = []
    warn_findings: list[tuple[Path, str, int, str]] = []
    secret_findings: list[tuple[Path, str, int, str]] = []

    for path in files:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for label, number, text in _scan_secrets(path, lines):
            secret_findings.append((path, label, number, text))
        if path.suffix.lower() in CODE_SUFFIXES:
            high, warn = _scan_code(path, lines)
            high_findings.extend((path, label, number, text) for label, number, text in high)
            warn_findings.extend((path, label, number, text) for label, number, text in warn)

    print("Security delta review")
    print("=" * 72)
    print(f"Changed files: {len(files)}")
    print()
    print("Manual checklist (the skill's five questions):")
    print("  [ ] Permissions: every new read/write is scoped to the signed-in user or an authorised role.")
    print("  [ ] Inputs: no user-controlled value reaches SQL, a shell, a template, eval, or a file path.")
    print("  [ ] Database: queries are parameterised; user_id filters are present; no raw SQL from input.")
    print("  [ ] Output: learner/API text is escaped; no v-html; errors do not leak secrets or PII.")
    print("  [ ] Secrets: no new secret, token, key, password, real hostname, or learner data.")
    print("  [ ] Dependencies: no unreviewed package or image.")
    print("  [ ] Docs: no PII, credentials, real infrastructure details, or private strategy.")
    print()

    def report(
        title: str,
        rows: list[tuple[Path, str, int, str]],
        *,
        redact: bool = False,
    ) -> None:
        if not rows:
            return
        print(title)
        for path, label, number, text in rows:
            print(f"  {path.relative_to(ROOT)}:{number}: {label}")
            print("    [redacted; inspect the file locally]" if redact else f"    {text}")
        print()

    report("HIGH: possible secret", secret_findings, redact=True)
    report("HIGH: review before merge", high_findings)
    report("WARN: verify the context", warn_findings)

    if secret_findings or high_findings:
        print("Security delta review: FAIL (high-confidence finding)")
        return 1
    print("Security delta review: PASS (no high-confidence finding)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
