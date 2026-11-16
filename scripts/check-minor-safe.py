#!/usr/bin/env python3
"""Validate minor-safe defaults for the Grades 9-12 stream.

The repository cannot infer a learner's age. It can, however, keep the
minor-facing content offline, fictional, and free of live targets, and fail the
build if an adult OSINT lab or an unlabelled external target leaks into the
High School tree.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HS_LABS = ROOT / "platform/labs/High School"
OSINT_LABS = ROOT / "platform/labs/OSINT"
HS_WIKI = ROOT / "platform/frontend/wiki/range/high-school"
MKDOCS = ROOT / "mkdocs-highschool.yml"

REQUIRED_HS = {
    "audience": "grades_9_12",
    "offline_only": True,
    "personal_data": "none",
    "free_text": False,
    "public_profiles": False,
    "phone_required": False,
    "analytics": "aggregate_only",
    "minor_safe_defaults": True,
}
FORBIDDEN_URL = re.compile(r"https?://[^\s\"'<>]+", re.I)
URL_ALLOWED_SUFFIXES = (".example", ".lab", ".invalid", ".test")
REAL_GPS = re.compile(r"42\.31|-83\.02|42°18'53|83°2'11|Windsor, Ontario")
FORBIDDEN_WIKI_TEXT = ("instructor-owned", "linkedin.com/in/", "profile-qr.png", "swocts.com")


def _allowed_url(url: str) -> bool:
    from urllib.parse import urlparse

    parsed = urlparse(url.rstrip(".,);"))
    host = (parsed.hostname or "").lower()
    if not host or host.startswith("{target."):
        return True
    if host in {"localhost", "127.0.0.1"}:
        return True
    if host.endswith(URL_ALLOWED_SUFFIXES):
        return True
    return False


def _lab_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> int:
    errors: list[str] = []
    hs_paths = sorted(HS_LABS.glob("*/lab.yaml"))
    if len(hs_paths) < 6:
        errors.append("expected at least six High School labs")
    for path in hs_paths:
        lab = _lab_yaml(path)
        slug = path.parent.name
        for key, expected in REQUIRED_HS.items():
            if lab.get(key) != expected:
                errors.append(f"{slug}: {key}={lab.get(key)!r}; expected {expected!r}")
        if lab.get("external_targets"):
            errors.append(f"{slug}: minor-facing lab declares external targets")
        if lab.get("category") == "osint":
            errors.append(f"{slug}: minor-facing lab must not be categorised as osint")
        target_blob = "\n".join(
            str(lab.get(key) or "")
            for key in ("description", "scenario", "troubleshooting")
        ) + yaml.safe_dump(
            {"hints": lab.get("hints"), "test": lab.get("test")},
            sort_keys=False,
        )
        if any(not _allowed_url(url) for url in FORBIDDEN_URL.findall(target_blob)):
            errors.append(f"{slug}: non-local URL in minor-facing lab scenario or hints")
        if REAL_GPS.search(yaml.safe_dump(lab, sort_keys=False)):
            errors.append(f"{slug}: real location data in minor-facing lab metadata")

    for path in sorted(OSINT_LABS.glob("osint-2-*/lab.yaml")):
        lab = _lab_yaml(path)
        slug = path.parent.name
        if lab.get("audience") != "adult":
            errors.append(f"{slug}: advanced OSINT lab must be audience: adult")
        if lab.get("visibility") != "course":
            errors.append(f"{slug}: advanced OSINT lab must be visibility: course")
        if lab.get("public_profiles") is True:
            errors.append(f"{slug}: public profiles are not allowed in this track")

    if not MKDOCS.is_file():
        errors.append("mkdocs-highschool.yml is missing")
    else:
        text = MKDOCS.read_text(encoding="utf-8")
        if "exclude_docs:" not in text:
            errors.append("High School wiki must use exclude_docs")
        for required in ("CH_OSINT01_OSINT_Foundations/**", "CH_OSINT02_Mobile_OSINT/**", "CH_MAL01_Malware_Fundamentals/**"):
            if required not in text:
                errors.append(f"High School wiki must exclude {required}")

    if HS_WIKI.is_dir():
        for path in HS_WIKI.rglob("*"):
            if path.is_dir() and path.name.startswith("CH_OSINT"):
                errors.append(f"stale OSINT directory in High School wiki: {path.relative_to(ROOT)}")
            if path.name == "profile-qr.png":
                errors.append(f"stale profile QR in High School wiki: {path.relative_to(ROOT)}")
            if path.suffix in {".html", ".json", ".md"}:
                try:
                    text = path.read_text(encoding="utf-8", errors="replace").lower()
                except OSError:
                    continue
                for term in FORBIDDEN_WIKI_TEXT:
                    if term in text:
                        errors.append(
                            f"forbidden term {term!r} in High School wiki: {path.relative_to(ROOT)}"
                        )
                        break

    # The instructor-profile workflow must not survive in any built wiki, even
    # a stale copy in another track. The real-site reference is allowed only in
    # the OSINT live-target inventory and its adult pages.
    wiki_root = ROOT / "platform/frontend/wiki"
    if wiki_root.is_dir():
        for path in wiki_root.rglob("*"):
            if path.name == "profile-qr.png":
                errors.append(f"stale profile QR in a built wiki: {path.relative_to(ROOT)}")
            if path.suffix in {".html", ".json"}:
                try:
                    text = path.read_text(encoding="utf-8", errors="replace").lower()
                except OSError:
                    continue
                for term in ("instructor-owned", "linkedin.com/in/"):
                    if term in text:
                        errors.append(
                            f"forbidden term {term!r} in a built wiki: {path.relative_to(ROOT)}"
                        )
                        break

    print("Minor-safe lab check")
    print("=" * 40)
    print(f"High School labs: {len(hs_paths)}")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: offline, fictional, no live targets, and High School wiki scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
