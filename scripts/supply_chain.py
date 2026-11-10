#!/usr/bin/env python3
"""Verify the OpenCyberRange supply-chain lock.

The lock records SHA-256 hashes for the platform dependency, build, compose,
deployment, and workflow inputs, plus a content hash for every lab. It detects drift between the reviewed release tree and the tree that is
about to be built, tested, or deployed.

What it proves
--------------
* The files and lab directories match the committed lock.
* A changed dependency, Dockerfile, compose file, workflow, or lab fails closed.

What it does not prove
----------------------
* It does not prove the repository or the build host is trustworthy. The lock
  itself is part of the repository, so the trust anchor is the reviewed commit
  or release tag. Sign the lock for release artefacts and verify the signature
  with ``--signature`` / ``--public-key``.
* It does not replace ``pip-audit``, ``npm audit``, CodeQL, Trivy, or an SBOM.
  Those find known vulnerabilities; this detects input drift.

Usage
-----
    python scripts/supply_chain.py --check
    python scripts/supply_chain.py --check --json
    python scripts/supply_chain.py --check --labs-only
    python scripts/supply_chain.py --check --signature supply-chain.lock.json.asc
    python scripts/supply_chain.py --check-pins
    python scripts/supply_chain.py --update

Update the lock only when the change is intentional and reviewed:

    python scripts/supply_chain.py --update
    git diff supply-chain.lock.json

For a release, sign the lock with the release key:

    gpg --detach-sign --armor supply-chain.lock.json
    python scripts/supply_chain.py --check --signature supply-chain.lock.json.asc
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lab_build_hash import build_hash  # noqa: E402

LOCK_NAME = "supply-chain.lock.json"
SCHEMA = 1

# Inputs that decide what the platform and its deploy path will do. Keep this
# list small enough to review and broad enough to catch a compromised build.
COVERED_FILES = [
    "versions.yaml",
    "platform/backend/app/version.py",
    "platform/backend/requirements.txt",
    "platform/backend/requirements-dev.txt",
    "platform/backend/pyproject.toml",
    "platform/backend/Dockerfile",
    "platform/frontend/package.json",
    "platform/frontend/package-lock.json",
    "platform/frontend/Dockerfile",
    "platform/frontend/docker-entrypoint.sh",
    "platform/frontend/nginx.conf",
    "platform/frontend/nginx-ssl.conf",
    "platform/frontend/security-headers.conf",
    "platform/frontend/index.html",
    "platform/frontend/binaries/wstunnel_10.5.2_linux_amd64.tar.gz",
    "platform/frontend/binaries/wstunnel_10.5.2_linux_arm64.tar.gz",
    "platform/docker-compose.prod.yml",
    "docker-compose.override.yml",
    "docker-compose.prod.yml",
    "scripts/install-platform.sh",
    "scripts/deploy-updates.sh",
    "scripts/GDG-Deploy.sh",
    "scripts/prebuild-labs.sh",
    "scripts/lab_build_hash.py",
    "scripts/supply_chain.py",
    "scripts/database_integrity.py",
    "scripts/check-licences.py",
    "scripts/generate-about.py",
    "scripts/verify-lab-builds.sh",
    "scripts/ui-smoke.mjs",
    "scripts/status-dashboard.py",
    ".github/workflows/ci.yml",
    ".github/workflows/quality.yml",
    ".github/workflows/codeql.yml",
    ".github/workflows/dependency-audit.yml",
    ".github/workflows/trivy.yml",
    ".github/workflows/ui-smoke.yml",
]

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

IMAGE_SOURCES = [
    "platform/backend/Dockerfile",
    "platform/frontend/Dockerfile",
    "platform/docker-compose.prod.yml",
    "docker-compose.prod.yml",
    "docker-compose.override.yml",
]

FROM_RE = re.compile(r"^\s*FROM\s+([^\s#]+)", re.IGNORECASE)
IMAGE_RE = re.compile(r"^\s*image:\s*[\"']?([^\"'\s#]+)", re.IGNORECASE)


def sha256_file(path: Path) -> str:
    """Hash a source file with text line endings normalised to LF."""
    return hashlib.sha256(file_bytes(path)).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_hash(lab_dir: Path) -> str:
    """Hash every tracked file in a lab, including lab.yaml and README.md.

    Text line endings are normalised to LF so a Windows checkout and a Linux
    checkout of the same commit produce the same hash. Binary files are hashed
    as-is.
    """
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
            digest.update(file_bytes(path))
            digest.update(b"\0")
    return digest.hexdigest()


def file_bytes(path: Path) -> bytes:
    """Return file content with text line endings normalised to LF."""
    data = path.read_bytes()
    if b"\x00" in data:
        return data
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def lab_dirs(labs_root: Path) -> list[Path]:
    if not labs_root.is_dir():
        return []
    found = sorted(
        path.parent for path in labs_root.rglob("docker-compose.yml")
        if path.parent.name not in LAB_EXCLUDE_DIRS
    )
    return found


def lab_entries(labs_root: Path) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    for lab_dir in lab_dirs(labs_root):
        slug = lab_dir.name
        if slug in entries:
            raise ValueError(f"duplicate lab slug: {slug}")
        built = build_hash(str(lab_dir))
        entries[slug] = {
            "content_hash": content_hash(lab_dir),
            "services": built["services"],
        }
    return entries


def read_release(root: Path) -> str:
    version_file = root / "platform/backend/app/version.py"
    if not version_file.is_file():
        return ""
    for line in version_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("APP_VERSION") and "=" in line:
            return line.split("=", 1)[1].strip().strip("\"'")
    return ""


def build_lock(root: Path, labs_root: Path | None = None, include_images: bool = False) -> dict:
    labs_root = labs_root or (root / "platform/labs")
    files: dict[str, dict] = {}
    for rel in COVERED_FILES:
        path = root / rel
        if path.is_file():
            files[rel] = {"sha256": sha256_file(path)}

    lock = {
        "schema": SCHEMA,
        "generator": "scripts/supply_chain.py",
        "release": read_release(root),
        "files": dict(sorted(files.items())),
        "labs": dict(sorted(lab_entries(labs_root).items())),
    }
    if include_images:
        lock["images"] = {ref: image_record(ref) for ref in image_refs(root)}
    return lock


def image_refs(root: Path) -> list[str]:
    refs: set[str] = set()
    for rel in IMAGE_SOURCES:
        path = root / rel
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = FROM_RE.match(line)
            if match:
                ref = match.group(1)
                if ref.upper() != "SCRATCH":
                    refs.add(ref)
                continue
            match = IMAGE_RE.match(line)
            if match:
                refs.add(match.group(1))
    return sorted(ref for ref in refs if not is_local_image(ref))


def is_local_image(ref: str) -> bool:
    lowered = ref.lower()
    return (
        lowered.startswith("ocr-")
        or lowered.startswith("opencyberrange/")
        or lowered.startswith(".")
        or lowered.startswith("docker.io/opencyberrange/")
    )


def image_record(ref: str) -> dict:
    if not shutil.which("docker"):
        return {"present": False, "error": "docker not available"}
    inspect = subprocess.run(
        ["docker", "image", "inspect", "--format", "{{.Id}}", ref],
        capture_output=True,
        text=True,
    )
    if inspect.returncode != 0:
        return {"present": False, "error": "image not present locally"}
    digests = subprocess.run(
        ["docker", "image", "inspect", "--format", "{{json .RepoDigests}}", ref],
        capture_output=True,
        text=True,
    )
    repo_digests = []
    if digests.returncode == 0 and digests.stdout.strip():
        try:
            repo_digests = json.loads(digests.stdout)
        except json.JSONDecodeError:
            repo_digests = []
    return {"present": True, "image_id": inspect.stdout.strip(), "repo_digests": repo_digests}


def image_pin_warnings(root: Path) -> list[str]:
    warnings = []
    for ref in image_refs(root):
        if "@sha256:" not in ref:
            warnings.append(
                f"UNPINNED image: {ref} (add @sha256:<digest> to pin the base image)"
            )
    return warnings


def verify_data(
    lock: dict,
    root: Path,
    labs_root: Path | None = None,
    files_only: bool = False,
    labs_only: bool = False,
    require_images: bool = False,
) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    labs_root = labs_root or (root / "platform/labs")
    summary = {"files": 0, "labs": 0, "images": 0}

    if lock.get("schema") != SCHEMA:
        errors.append(f"SCHEMA mismatch: lock={lock.get('schema')} expected={SCHEMA}")

    expected_release = lock.get("release")
    current_release = read_release(root)
    if expected_release and current_release and expected_release != current_release:
        errors.append(
            f"RELEASE mismatch: lock={expected_release} code={current_release} "
            "(run --update after the version bump)"
        )

    if not labs_only:
        for rel, entry in sorted((lock.get("files") or {}).items()):
            path = root / rel
            summary["files"] += 1
            if not path.is_file():
                errors.append(f"MISSING file: {rel}")
                continue
            current = sha256_file(path)
            if current != entry.get("sha256"):
                errors.append(
                    f"MISMATCH file: {rel} (locked {entry.get('sha256')[:12]}, current {current[:12]})"
                )

        if lock.get("images"):
            for ref, entry in sorted(lock["images"].items()):
                summary["images"] += 1
                current = image_record(ref)
                if not current.get("present"):
                    message = f"MISSING image: {ref} ({current.get('error', 'not present')})"
                    if require_images:
                        errors.append(message)
                    else:
                        warnings.append(message)
                    continue
                if entry.get("image_id") and entry["image_id"] != current.get("image_id"):
                    errors.append(
                        f"MISMATCH image: {ref} (locked {entry['image_id'][:19]}, current {current['image_id'][:19]})"
                    )

    if not files_only:
        current_labs = lab_entries(labs_root)
        locked_labs = lock.get("labs") or {}
        summary["labs"] = len(current_labs)
        for slug, entry in sorted(locked_labs.items()):
            current = current_labs.get(slug)
            if current is None:
                errors.append(f"REMOVED lab: {slug} (in lock but not on disk)")
                continue
            if entry.get("content_hash") != current["content_hash"]:
                errors.append(f"MISMATCH lab content: {slug}")
            if (entry.get("services") or []) != current["services"]:
                errors.append(
                    f"MISMATCH lab services: {slug} (locked {entry.get('services')}, current {current['services']})"
                )
        for slug in sorted(set(current_labs) - set(locked_labs)):
            errors.append(f"NEW lab: {slug} (not in lock; run --update)")

    return errors, warnings, summary


def verify_signature(lock_path: Path, signature: Path, public_key: str | None) -> list[str]:
    if not signature.is_file():
        return [f"MISSING signature: {signature}"]
    if shutil.which("minisign") and public_key:
        result = subprocess.run(
            ["minisign", "-Vm", str(lock_path), "-x", str(signature), "-P", public_key],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return [f"BAD signature: {result.stderr.strip() or result.stdout.strip()}"]
        return []
    if shutil.which("gpg"):
        result = subprocess.run(
            ["gpg", "--verify", str(signature), str(lock_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return [f"BAD signature: {result.stderr.strip() or result.stdout.strip()}"]
        return []
    return ["NO verifier: install minisign or gpg to verify the lock signature"]


def write_lock(path: Path, lock: dict) -> None:
    path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="verify the lock (default)")
    parser.add_argument("--update", action="store_true", help="write the lock from the current tree")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="repository root")
    parser.add_argument("--labs-dir", help="override the labs directory")
    parser.add_argument("--lock", help="lock file path")
    parser.add_argument("--files-only", action="store_true")
    parser.add_argument("--labs-only", action="store_true")
    parser.add_argument("--images", action="store_true", help="include local image IDs in the lock")
    parser.add_argument("--require-images", action="store_true", help="fail when a locked image is absent")
    parser.add_argument("--check-pins", action="store_true", help="report base images without a digest")
    parser.add_argument("--strict-pins", action="store_true", help="fail on unpinned base images")
    parser.add_argument("--signature", help="detached signature over the lock")
    parser.add_argument("--public-key", help="minisign public key")
    parser.add_argument("--json", action="store_true", help="machine-readable result")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    labs_root = Path(args.labs_dir).resolve() if args.labs_dir else (root / "platform/labs")
    lock_path = Path(args.lock).resolve() if args.lock else (root / LOCK_NAME)

    if args.check_pins:
        warnings = image_pin_warnings(root)
        if args.json:
            print(json.dumps({"ok": not (args.strict_pins and warnings), "unpinned": warnings}, indent=2))
        else:
            for warning in warnings:
                print(warning)
            print(f"{len(warnings)} unpinned image reference(s)")
        if args.strict_pins and warnings:
            return 1
        if not args.update and not args.check_pins:
            return 0

    if args.update:
        lock = build_lock(root, labs_root, include_images=args.images)
        write_lock(lock_path, lock)
        counts = {"files": len(lock["files"]), "labs": len(lock["labs"])}
        if args.json:
            print(json.dumps({"ok": True, "updated": str(lock_path), **counts}, indent=2))
        else:
            print(f"Wrote {lock_path} ({counts['files']} files, {counts['labs']} labs)")
        return 0

    if args.check_pins:
        return 0

    if not lock_path.is_file():
        message = f"missing lock: {lock_path} (run --update)"
        if args.json:
            print(json.dumps({"ok": False, "errors": [message], "warnings": []}, indent=2))
        else:
            print(f"ERROR: {message}")
        return 1

    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid lock JSON: {exc}")
        return 1

    signature_errors: list[str] = []
    if args.signature:
        signature_errors = verify_signature(lock_path, Path(args.signature).resolve(), args.public_key)

    errors, warnings, summary = verify_data(
        lock,
        root,
        labs_root,
        files_only=args.files_only,
        labs_only=args.labs_only,
        require_images=args.require_images,
    )
    errors = signature_errors + errors

    if args.json:
        print(json.dumps({
            "ok": not errors,
            "release": lock.get("release"),
            "summary": summary,
            "errors": errors,
            "warnings": warnings,
        }, indent=2))
    else:
        for warning in warnings:
            print(f"WARN: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        if errors:
            print(f"\nFAILED: {len(errors)} supply-chain mismatch(es) across {summary['files']} files and {summary['labs']} labs")
        else:
            print(f"OK: {summary['files']} files and {summary['labs']} lab hashes match {lock_path.name} (release {lock.get('release') or 'unknown'})")
            if warnings:
                print(f"WARN: {len(warnings)} non-blocking warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
