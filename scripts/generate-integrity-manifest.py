#!/usr/bin/env python3
"""Generate the runtime software-integrity manifest.

The supply-chain lock is the build-time source of truth. The backend image
cannot read the repository, so this script copies the lab content hashes and
the release into a small manifest that ships inside the backend package. The
admin "Software integrity" check recomputes the same hashes from the mounted
/labs tree at runtime and compares.

Run after `python scripts/supply_chain.py --update`; CI checks the result.
"""

from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK = ROOT / "supply-chain.lock.json"
OUT = ROOT / "platform" / "backend" / "app" / "data" / "software-integrity.json"


def main() -> int:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    manifest = {
        "schema": 1,
        "release": lock.get("release"),
        "generator": "scripts/generate-integrity-manifest.py",
        "source_lock": "supply-chain.lock.json",
        "labs": {
            slug: entry.get("content_hash", "")
            for slug, entry in sorted((lock.get("labs") or {}).items())
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(manifest['labs'])} labs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
