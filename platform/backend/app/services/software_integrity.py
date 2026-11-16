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
# Runtime output written under a lab's container directories is ignored by
# .gitignore and is not part of the reviewed release. Excluding it keeps the
# runtime hash aligned with the build-time lock on a host that has built labs.
LAB_RUNTIME_PARENTS = {"containers"}
LAB_RUNTIME_DIRS = {"app", "data", "logs"}


def _excluded_dir(lab_dir: Path, dirpath: str, name: str) -> bool:
    if name in LAB_EXCLUDE_DIRS:
        return True
    relative = (Path(dirpath) / name).relative_to(lab_dir).parts
    if (
        len(relative) >= 3
        and relative[0] in LAB_RUNTIME_PARENTS
        and relative[2] in LAB_RUNTIME_DIRS
    ):
        return True
    return False

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
        dirnames[:] = sorted(
            d for d in dirnames if not _excluded_dir(lab_dir, dirpath, d)
        )
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
    unreadable: list[dict[str, str]] = []
    if root.is_dir():
        for marker in root.rglob("lab.yaml"):
            lab_dir = marker.parent
            if lab_dir.name in LAB_EXCLUDE_DIRS or lab_dir.name.startswith("_"):
                continue
            if not (lab_dir / "docker-compose.yml").is_file():
                continue
            try:
                actual[lab_dir.name] = content_hash(lab_dir)
            except OSError as exc:
                unreadable.append(
                    {"slug": lab_dir.name, "reason": str(exc)}
                )

    mismatched = [
        {
            "slug": slug,
            "expected": digest,
            "actual": actual.get(slug, ""),
        }
        for slug, digest in sorted(expected.items())
        if slug in actual and actual[slug] != digest
    ]
    missing = sorted(set(expected) - set(actual) - {row["slug"] for row in unreadable})
    extra = sorted(set(actual) - set(expected))
    ok = not mismatched and not missing and not extra and not unreadable

    return {
        "ok": ok,
        "release": manifest.get("release"),
        "checked": len(actual),
        "expected": len(expected),
        "mismatched": mismatched,
        "missing": missing,
        "extra": extra,
        "unreadable": unreadable,
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
