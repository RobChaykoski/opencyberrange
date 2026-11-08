"""Verify that local images and workbook assets referenced by Markdown exist.

The main link checker validates Markdown links. This check covers image
references and the screenshot paths used by the manual, so a moved or missing
PNG fails CI instead of rendering a broken figure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ["Manual-Lite", "Workbook", "docs"]
IMAGE_MD = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
IMAGE_HTML = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)
LINK_MD = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")

failures: list[str] = []
checked = 0


def check_reference(md_path: Path, raw: str) -> None:
    global checked
    target = raw.strip().split()[0].strip("<>")
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https", "data", "mailto"} or target.startswith("#"):
        return
    if not target:
        return
    local = unquote(parsed.path)
    if not local:
        return
    candidate = (md_path.parent / local).resolve()
    if not candidate.exists():
        failures.append(f"{md_path.relative_to(ROOT)} -> {target}")
    checked += 1


for directory in SCAN_DIRS:
    base = ROOT / directory
    if not base.exists():
        continue
    for path in base.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in IMAGE_MD.findall(text):
            check_reference(path, raw)
        for raw in IMAGE_HTML.findall(text):
            check_reference(path, raw)
        # Workbook index links point at chapter sources; check local targets too.
        if path.name == "index.md" and "Workbook" in path.parts:
            for raw in LINK_MD.findall(text):
                check_reference(path, raw)

if failures:
    print(f"FAIL: {len(failures)} missing local asset(s)")
    for item in failures[:40]:
        print(f"  - {item}")
    sys.exit(1)

print(f"PASS: checked {checked} local image/workbook asset reference(s)")
