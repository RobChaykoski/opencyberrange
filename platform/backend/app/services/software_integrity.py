"""Runtime software-integrity check for the deployed platform.

The supply-chain lock is generated at build time. A small manifest with the
same lab content hashes ships inside the backend package, so an administrator
can verify the mounted lab tree against the reviewed release without the
repository being present on the server.

This detects tampering or drift in the largest mutable input (lab content) and
reports the running image digest and build revision for the audit trail. It
does not replace the build-time supply-chain check for dependencies.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

MANIFEST_PATH = Path(__file__).resolve().parent.parent / "data" / "software-integrity.json"
LAB_EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "dist",
    "wiki",
    "wiki.prev",
}
LAB_EXCLUDE_SUFFIXES = (".pyc", ".pyo")
LAB_EXCLUDE_FILES = {".DS_Store"}

_CACHE_TTL = 60.0
_cache: tuple[float, dict] | None = None


def _file_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if b"\x00" in data:
        return data
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def content_hash(lab_dir: Path) -> str:
    """Match scripts/supply_chain.py: hash every tracked file, LF-normalised."""
    lab_dir = lab_dir.resolve()
    digest = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(lab_dir):
        dirnames[:] = sorted(d for d in dirnames if d not in LAB_EXCLUDE_DIRS)
        for filename in sorted(filenames):
            if filename in LAB_EXCLUDE_FILES or filename.endswith(LAB_EXCLUDE_SUFFIXES):
                continue
            path = Path(dirpath) / filename
            rel = path.relative_to(lab_dir).as_posix()
            digest.update(rel.encode("utf-8", "surrogateescape"))
            digest.update(b"\0")
            digest.update(_file_bytes(path))
            digest.update(b"\0")
    return digest.hexdigest()


def load_manifest() -> dict:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _image_info() -> dict:
    info = {"image_id": "", "digests": [], "revision": os.environ.get("OCR_BUILD_REVISION", "unknown")}
    try:
        from app.services.docker_manager import DockerManager

        manager = DockerManager()
        container = manager.client.containers.get(os.environ.get("HOSTNAME", ""))
        image = manager.client.images.get(container.attrs.get("Image", ""))
        info["image_id"] = image.short_id
        info["digests"] = image.attrs.get("RepoDigests") or []
        labels = (image.attrs.get("Config") or {}).get("Labels") or {}
        info["revision"] = labels.get("org.opencontainers.image.revision", info["revision"])
    except Exception as exc:  # best-effort evidence, never a hard failure
        info["error"] = str(exc)
    return info


def verify(labs_root: str | None = None) -> dict:
    manifest = load_manifest()
    expected: dict[str, str] = manifest.get("labs") or {}
    root = Path(labs_root or os.environ.get("LABS_DIR", "/labs"))

    actual: dict[str, str] = {}
    if root.is_dir():
        for compose in root.rglob("docker-compose.yml"):
            lab_dir = compose.parent
            if lab_dir.name in LAB_EXCLUDE_DIRS or lab_dir.name.startswith("_"):
                continue
            actual[lab_dir.name] = content_hash(lab_dir)

    mismatched = [
        {
            "slug": slug,
            "expected": digest,
            "actual": actual.get(slug, ""),
        }
        for slug, digest in sorted(expected.items())
        if slug in actual and actual[slug] != digest
    ]
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    ok = not mismatched and not missing and not extra

    return {
        "ok": ok,
        "release": manifest.get("release"),
        "checked": len(actual),
        "expected": len(expected),
        "mismatched": mismatched,
        "missing": missing,
        "extra": extra,
        "labs_root": str(root),
        "build": _image_info(),
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def verify_cached() -> dict:
    global _cache
    now = time.monotonic()
    if _cache and now - _cache[0] < _CACHE_TTL:
        return _cache[1]
    result = verify()
    _cache = (now, result)
    return result


def invalidate_cache() -> None:
    global _cache
    _cache = None
