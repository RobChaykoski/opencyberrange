"""Keep the inline-script CSP hash in step with index.html.

The SPA's only inline script is the theme bootstrap. nginx pins it by sha256 in
three CSP headers. If index.html changes without updating the hash, the script
is silently blocked and the page flashes the wrong theme. CI runs this on every
pull request and push to main, and fails on both missing and stale hashes.

Usage:
    python scripts/check-csp-hash.py
"""

from __future__ import annotations

import base64
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "platform" / "frontend" / "index.html"
CSP_FILES = (
    ROOT / "platform" / "frontend" / "nginx.conf",
    ROOT / "platform" / "frontend" / "nginx-ssl.conf",
    ROOT / "platform" / "frontend" / "security-headers.conf",
)


def _inline_hashes(html: str) -> set[str]:
    return {
        base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
        for script in re.findall(r"<script>(.*?)</script>", html, re.DOTALL)
    }


def main() -> int:
    if not INDEX.is_file():
        print(f"Missing {INDEX}")
        return 1
    expected = _inline_hashes(INDEX.read_text(encoding="utf-8"))
    if not expected:
        print("No inline script found in index.html; nothing to pin.")
        return 0

    problems = []
    for path in CSP_FILES:
        if not path.is_file():
            problems.append(f"missing CSP file: {path}")
            continue
        pinned = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            if "Content-Security-Policy" in line and "script-src" in line:
                pinned.update(re.findall(r"'sha256-([^']+)'", line))
        missing = expected - pinned
        extra = pinned - expected
        if missing:
            problems.append(
                f"{path.name}: CSP is missing the inline-script hash(es) "
                + ", ".join(f"sha256-{value}" for value in sorted(missing))
            )
        if extra:
            problems.append(
                f"{path.name}: CSP has stale inline-script hash(es) that are not "
                "in index.html: "
                + ", ".join(f"sha256-{value}" for value in sorted(extra))
            )

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        print("Recompute with:")
        print(
            "  python -c \"import base64,hashlib,re; "
            "s=re.search(r'<script>(.*?)</script>', "
            "open('platform/frontend/index.html').read(), re.S).group(1); "
            "print('sha256-'+base64.b64encode(hashlib.sha256(s.encode()).digest()).decode())\""
        )
        return 1
    print("CSP inline-script hash matches index.html in all nginx configs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
