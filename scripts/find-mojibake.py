from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "node_modules", "_site_manual_lite", "wiki.new", "wiki.prev", "dist", "site"}
SUFFIXES = {".md", ".txt", ".yml", ".yaml", ".html", ".css", ".js", ".py"}
PATTERNS = ("\u00e2", "\u00c3", "\u00c2", "\ufffd")
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in SUFFIXES:
        continue
    if any(part in SKIP for part in path.parts):
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    if any(pattern in text for pattern in PATTERNS):
        print(path.relative_to(ROOT))
