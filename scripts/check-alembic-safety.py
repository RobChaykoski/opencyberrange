#!/usr/bin/env python3
"""Guard the Alembic revision graph and reject autogenerate usage.

The live schema contains runtime tenant DDL and legacy-restored columns and
indexes that are not represented in the migration graph. Autogenerate would
propose destructive drops. This check keeps that unsafe path out of CI and
scripts until the baseline is reconciled.
"""

from __future__ import annotations

import os
import sys
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "platform" / "backend"
SELF = Path(__file__).resolve()

# Revision modules import the application package and its settings. Set a
# harmless local placeholder before Alembic walks them; this script never opens
# a database connection.
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
os.environ.setdefault("DATABASE_URL", "postgresql://ocr:ocr@localhost/ocr")
os.environ.setdefault("JWT_SECRET", "alembic-safety-check")

from alembic.config import Config
from alembic.script import ScriptDirectory

PATTERNS = (
    "alembic revision --autogenerate",
    "autogenerate=True",
    "--autogenerate",
)
SCAN = (ROOT / ".github" / "workflows", ROOT / "scripts")


def _script() -> ScriptDirectory:
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "alembic"))
    return ScriptDirectory.from_config(cfg)


def main() -> int:
    errors: list[str] = []
    script = _script()
    heads = script.get_heads()
    if len(heads) != 1:
        errors.append(f"expected one Alembic head, found {heads}")

    revisions = list(script.walk_revisions())
    for current, previous in pairwise(revisions):
        if current.down_revision != previous.revision:
            errors.append(
                f"non-linear revision graph: {current.revision} -> "
                f"{current.down_revision}, expected {previous.revision}"
            )

    for directory in SCAN:
        for path in directory.rglob("*"):
            if not path.is_file() or path == SELF:
                continue
            if path.suffix not in {".yml", ".yaml", ".sh", ".py"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in PATTERNS:
                if pattern in text:
                    errors.append(
                        f"{path.relative_to(ROOT)} uses {pattern!r}; "
                        "hand-write the migration after reviewing the drift"
                    )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: single Alembic head {heads[0]}; no autogenerate usage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
