"""Pure integrity helpers for competency contracts and signed reviews.

These functions read the taxonomy, the generated contracts, and the lab tree.
They deliberately do not import the database or the application settings, so an
offline release check can use the same hashing rules as the review service.
"""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TAXONOMY_FILE = DATA_DIR / "competency-taxonomy.yaml"
LABS_DIR = Path(__file__).resolve().parents[3] / "labs"
RELEVANT_SUFFIXES = {".yaml", ".yml", ".md"}


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(payload: dict) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


@lru_cache(maxsize=1)
def taxonomy_entries() -> dict[str, dict]:
    with TAXONOMY_FILE.open(encoding="utf-8") as handle:
        taxonomy = yaml.safe_load(handle) or {}
    entries: dict[str, dict] = {}
    for domain in taxonomy.get("domains", []):
        for category in domain.get("categories", []):
            for competency in category.get("competencies", []):
                entries[str(competency["id"])] = {
                    "id": str(competency["id"]),
                    "name": competency.get("name"),
                    "definition": competency.get("definition"),
                }
    return entries


def taxonomy_hash_for(competency_ids) -> str:
    entries = taxonomy_entries()
    payload = {str(item): entries.get(str(item)) for item in sorted(set(competency_ids))}
    return sha(canonical(payload))


@lru_cache(maxsize=1024)
def lab_hash(slug: str) -> str:
    lab = next(
        (
            path.parent
            for path in LABS_DIR.rglob("lab.yaml")
            if path.parent.name == slug
        ),
        None,
    )
    if lab is None:
        raise FileNotFoundError(f"lab not found: {slug}")
    digest = hashlib.sha256()
    for path in sorted(lab.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in RELEVANT_SUFFIXES:
            continue
        parts = {part.lower() for part in path.parts}
        if "img" in parts or "images" in parts:
            continue
        digest.update(str(path.relative_to(lab)).replace("\\", "/").encode("utf-8"))
        digest.update(path.read_bytes())
    manifest = LABS_DIR.parent / "tester" / "manifests" / f"{slug}.yaml"
    if manifest.is_file():
        digest.update(b"tester-manifest")
        digest.update(manifest.read_bytes())
    return digest.hexdigest()


def contract_snapshot(contract: dict) -> dict:
    """Return the signed fields of a generated contract.

    The order and membership match the review service's snapshot so a hash can
    be compared without loading the database.
    """
    return {
        "competency_ids": contract.get("competency_ids") or [],
        "evidence": contract.get("evidence") or [],
        "assessment_reliability": contract.get("assessment_reliability") or {},
        "assessment_criteria": contract.get("assessment_criteria") or [],
    }


def snapshot_hash(contract: dict) -> str:
    return sha(canonical(contract_snapshot(contract)))
