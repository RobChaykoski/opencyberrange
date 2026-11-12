"""Keep the data dictionary in step with the ORM.

Fails when a table declared in ``platform/backend/app/models.py`` is not named
in ``docs/DATA-DICTIONARY.md``. It is intentionally simple: the dictionary is a
review document, and this check only guarantees that every table is mentioned
somewhere. A reviewer still confirms the purpose, authority, retention, access,
export, and deletion columns.

Usage:
    python scripts/check-data-dictionary.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "platform" / "backend" / "app" / "models.py"
DICTIONARY = ROOT / "docs" / "DATA-DICTIONARY.md"

TABLE_PATTERN = re.compile(r'__tablename__\s*=\s*"([a-z0-9_]+)"')


def main() -> int:
    if not MODELS.exists() or not DICTIONARY.exists():
        print("Data dictionary check: models or dictionary file is missing.")
        return 1

    tables = sorted(set(TABLE_PATTERN.findall(MODELS.read_text(encoding="utf-8"))))
    text = DICTIONARY.read_text(encoding="utf-8")
    missing = [table for table in tables if table not in text]

    print("Data dictionary check")
    print("=" * 40)
    print(f"Tables in models.py: {len(tables)}")
    print(f"Documented: {len(tables) - len(missing)}")
    if missing:
        print("Missing tables:")
        for table in missing:
            print(f"  - {table}")
        print("FAIL: add each table to docs/DATA-DICTIONARY.md")
        return 1
    print("PASS: every table is named in the data dictionary.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
