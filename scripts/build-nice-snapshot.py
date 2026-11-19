#!/usr/bin/env python3
"""Build the bundled NICE Framework v2.2.0 component snapshot.

The platform ships a compressed snapshot so a fresh install can populate the
authoring dropdown without outbound network access. Administrators can refresh
from the official NIST URL later.

Usage:
    python scripts/build-nice-snapshot.py
    python scripts/build-nice-snapshot.py --source nice.json
"""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = (
    "https://csrc.nist.gov/csrc/media/Projects/cprt/documents/nice/"
    "v2-2-0_nf_components.json"
)
TARGET = ROOT / "platform/backend/app/data/nice/nice-v2.2.0.json.gz"
ALLOWED_TYPES = {"category", "work_role", "task", "knowledge", "skill"}


def compact(payload: dict) -> dict:
    elements = [
        item for item in payload.get("elements", [])
        if item.get("element_type") in ALLOWED_TYPES
    ]
    identifiers = {item["element_identifier"] for item in elements}
    relationships = [
        item for item in payload.get("relationships", [])
        if item.get("source_element_identifier") in identifiers
        and item.get("dest_element_identifier") in identifiers
    ]
    return {
        "documents": payload.get("documents", []),
        "relationship_types": payload.get("relationship_types", []),
        "elements": elements,
        "relationships": relationships,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Read a local JSON file instead of the official URL")
    parser.add_argument("--target", default=str(TARGET))
    args = parser.parse_args()

    if args.source:
        payload = json.loads(Path(args.source).read_text(encoding="utf-8"))
    else:
        with urlopen(OFFICIAL, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))

    version = (payload.get("documents") or [{}])[0].get("version", "unknown")
    if not str(version).startswith("2.2"):
        raise SystemExit(f"unexpected NICE version: {version}")

    data = compact(payload)
    target = Path(args.target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(target, "wt", encoding="utf-8", compresslevel=9) as handle:
        json.dump(data, handle, separators=(",", ":"))

    print(
        f"wrote {target} ({target.stat().st_size} bytes, "
        f"{len(data['elements'])} elements, {len(data['relationships'])} links)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
