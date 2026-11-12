#!/usr/bin/env python3
"""Reject external image references in learner-facing content.

The platform serves workbook and manual images from the local docs tree. An
external image would make every learner's browser fetch a third-party URL:
tracking, mixed content, and an image decoder parsing bytes the platform never
validated. The runtime image pipeline only accepts uploaded raster data that it
re-encodes; content images must follow the same rule by being hosted locally.

Scans Workbook/, Manual-Lite/, and the SPA source. README badges and docs that
intentionally show external screenshots are out of scope.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCAN_DIRS = [ROOT / "Workbook", ROOT / "Manual-Lite", ROOT / "platform" / "frontend" / "src"]
SUFFIXES = {".md", ".vue", ".html"}

MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(\s*(https?:)?//", re.IGNORECASE)
HTML_IMAGE = re.compile(r"<img\b[^>]*\bsrc\s*=\s*[\"'](https?:)?//", re.IGNORECASE)
CSS_IMAGE = re.compile(r"url\(\s*[\"']?(https?:)?//", re.IGNORECASE)

failures: list[str] = []


def main() -> int:
    for base in SCAN_DIRS:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                if MARKDOWN_IMAGE.search(line) or HTML_IMAGE.search(line) or CSS_IMAGE.search(line):
                    failures.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()[:160]}")

    if failures:
        print("FAIL: external image reference found in learner-facing content.")
        print("Host the image under the docs tree and reference it with a relative path.")
        for item in failures:
            print(f"  {item}")
        return 1

    print("PASS: learner-facing content references no external images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
