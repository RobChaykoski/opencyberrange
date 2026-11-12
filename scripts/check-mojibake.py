from pathlib import Path

import ftfy

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "node_modules", "_site_manual_lite", "wiki.new", "wiki.prev", "dist", "site"}
changed = []
for path in ROOT.rglob("*.md"):
    if any(part in SKIP for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    fixed = ftfy.fix_text(text)
    if fixed != text:
        changed.append((path, text, fixed))

print(f"files needing fixes: {len(changed)}")
for path, text, fixed in changed:
    print(path.relative_to(ROOT))
