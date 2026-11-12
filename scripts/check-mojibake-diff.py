import difflib
from pathlib import Path

import ftfy

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "node_modules", "_site_manual_lite", "wiki.new", "wiki.prev", "dist", "site"}
for path in ROOT.rglob("*.md"):
    if any(part in SKIP for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    fixed = ftfy.fix_text(text)
    if fixed == text:
        continue
    print(f"\n=== {path.relative_to(ROOT)} ===")
    old_lines = text.splitlines()
    new_lines = fixed.splitlines()
    for line in difflib.unified_diff(old_lines, new_lines, lineterm="", n=0):
        if line.startswith(("---", "+++", "@@")):
            continue
        print(line[:240])
