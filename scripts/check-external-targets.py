#!/usr/bin/env python3
"""Check live OSINT targets and their offline mirrors.

Live targets are optional evidence. The offline mirror is the assessed path.
The daily check records drift, missing markers, and mirror changes. It never
collects personal data or scrapes a social-media profile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "platform/backend/app/data/external-targets.yaml"
USER_AGENT = "OpenCyberRange-ExternalTargetCheck/1.0"
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(
    r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
    re.I | re.S,
)
META_RE = re.compile(
    r'<meta[^>]+name=["\']x-swocts-osint["\'][^>]+content=["\'](.*?)["\']',
    re.I | re.S,
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stable_live(body: bytes, status: int, final_url: str) -> tuple[str, str]:
    text = body.decode("utf-8", "replace")
    title = TITLE_RE.search(text)
    description = DESC_RE.search(text)
    marker = META_RE.search(text)
    stable = {
        "status": status,
        "final_url": final_url,
        "title": title.group(1).strip() if title else "",
        "description": description.group(1).strip() if description else "",
        "marker": marker.group(1).strip() if marker else "",
    }
    return (
        _sha256(json.dumps(stable, sort_keys=True).encode("utf-8")),
        stable["marker"],
    )


def _fetch(url: str) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, response.geturl(), response.read()


def _check_offline(target: dict) -> list[str]:
    errors: list[str] = []
    mirror = ROOT / str(target["offline_mirror"])
    if not mirror.is_file():
        return [f"{target['id']}: missing offline mirror {mirror.relative_to(ROOT)}"]
    data = mirror.read_bytes()
    digest = _sha256(data)
    if digest != target.get("offline_mirror_sha256"):
        errors.append(
            f"{target['id']}: offline mirror drift: expected "
            f"{target.get('offline_mirror_sha256')}, got {digest}"
        )
    marker = str(target.get("offline_marker") or target.get("expected_marker") or "")
    if marker and marker not in data.decode("utf-8", "replace"):
        errors.append(f"{target['id']}: offline mirror is missing the expected marker")
    return errors


def _check_live(target: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    observed: dict = {}
    try:
        status, final_url, body = _fetch(str(target["url"]))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return [f"{target['id']}: live check failed: {exc}"], observed
    raw = _sha256(body)
    stable, marker = _stable_live(body, status, final_url)
    text = body.decode("utf-8", "replace")
    expected_marker = str(target.get("expected_marker") or "")
    marker_present = bool(expected_marker and expected_marker in text)
    observed = {
        "status": status,
        "final_url": final_url,
        "raw_sha256": raw,
        "stable_sha256": stable,
        "marker": expected_marker if marker_present else "",
        "marker_status": "present" if marker_present else "absent",
        "checked_at": date.today().isoformat(),
    }
    if status != int(target.get("expected_status", 200)):
        errors.append(f"{target['id']}: status {status}, expected {target.get('expected_status')}")
    if target.get("kind") == "public_repository_file":
        if raw != target.get("raw_sha256"):
            errors.append(
                f"{target['id']}: repository file drift: expected "
                f"{target.get('raw_sha256')}, got {raw}"
            )
    elif stable != target.get("stable_sha256"):
        errors.append(
            f"{target['id']}: stable content drift: expected "
            f"{target.get('stable_sha256')}, got {stable}"
        )
    if marker_present:
        observed["marker"] = expected_marker
    elif target.get("marker_required"):
        errors.append(f"{target['id']}: required marker is absent")
    else:
        print(f"WARN {target['id']}: optional live marker is absent; offline mirror remains authoritative")
    return errors, observed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="check mirrors without network")
    parser.add_argument("--update", action="store_true", help="refresh hashes and checked_at")
    parser.add_argument("--json", action="store_true", help="emit a JSON report")
    parser.add_argument("--strict", action="store_true", help="fail when an optional marker is absent")
    args = parser.parse_args()

    document = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
    targets = document.get("targets") or []
    errors: list[str] = []
    report: list[dict] = []
    for target in targets:
        before = len(errors)
        errors.extend(_check_offline(target))
        observed: dict = {}
        if args.offline or target.get("live_check") is False:
            report.append({"id": target["id"], "mode": "offline", "ok": len(errors) == before})
            continue
        live_errors, observed = _check_live(target)
        if args.strict and not target.get("marker_required") and observed.get("marker_status") == "absent":
            live_errors.append(f"{target['id']}: optional marker is absent")
        errors.extend(live_errors)
        if args.update and observed:
            target.update(observed)
        report.append(
            {
                "id": target["id"],
                "mode": "live",
                "ok": not live_errors,
                "url": target.get("url"),
                **observed,
            }
        )

    if args.update and not args.offline:
        document["targets"] = targets
        INVENTORY.write_text(
            yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps({"ok": not errors, "targets": report}, indent=2))
    else:
        print("External target check")
        print("=" * 40)
        for item in report:
            state = "PASS" if item.get("ok") else "FAIL"
            print(f"{state} {item['id']} ({item['mode']})")
        for error in errors:
            print(f"FAIL: {error}")
        if not errors:
            print("PASS: external targets and offline mirrors match the reviewed evidence")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
