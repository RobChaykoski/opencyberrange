#!/usr/bin/env python3
"""Fetch a reviewed external dataset into a local, gitignored cache.

The registry is the authority. This script only downloads entries whose source
explicitly allows fetching and whose files have a pinned URL and SHA-256. It
refuses reference-only and no-licence sources, so a public repository never
turns a reading reference into a redistributed sample.

Examples:
    python scripts/fetch-external-datasets.py --list
    python scripts/fetch-external-datasets.py --dataset SDLIN-201110074812
    python scripts/fetch-external-datasets.py --source security-datasets --all
    python scripts/fetch-external-datasets.py --verify

The cache defaults to `platform/backend/app/data/external-datasets/cache/` and
is excluded by `.gitignore`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "platform/backend/app/data/external-datasets.yaml"
FETCHABLE = {"security-datasets", "splunk-attack-data"}
CONTAINER = {"juice-shop"}
USER_AGENT = "OpenCyberRange-dataset-fetch/1.0"


def _load() -> dict:
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}


def _url(source: dict, item: dict) -> str:
    base = str(source.get("fetch_base") or "").rstrip("/")
    pin = str(source.get("pin") or "")
    path = str(item.get("path") or "").lstrip("/")
    return f"{base}/{pin}/{path}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _target(cache: Path, dataset: dict, item: dict) -> Path:
    return cache / str(dataset["id"]) / Path(str(item["path"])).name


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with (
        urllib.request.urlopen(request, timeout=120) as response,
        tempfile.NamedTemporaryFile(
            dir=destination.parent, delete=False, suffix=".part"
        ) as handle,
    ):
        temp_path = Path(handle.name)
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    temp_path.replace(destination)


def _report(rows: list[dict], as_json: bool) -> None:
    if as_json:
        print(json.dumps(rows, indent=2))
        return
    for row in rows:
        status = row.get("status", "")
        size = row.get("bytes")
        print(f"{status:8} {row['dataset']:32} {row.get('file', ''):60} {size or ''}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list registry entries")
    parser.add_argument("--source", help="filter by source id")
    parser.add_argument("--dataset", help="fetch one dataset id")
    parser.add_argument("--all", action="store_true", help="fetch every fetchable entry")
    parser.add_argument("--verify", action="store_true", help="verify the local cache only")
    parser.add_argument("--force", action="store_true", help="replace an existing file")
    parser.add_argument("--dest", help="override the cache directory")
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    args = parser.parse_args()

    document = _load()
    sources = {str(item["id"]): item for item in document.get("sources") or []}
    datasets = document.get("datasets") or []
    cache = Path(args.dest) if args.dest else ROOT / str(document["policy"]["cache_root"])

    if args.list:
        rows = []
        for dataset in datasets:
            source = sources.get(str(dataset.get("source"))) or {}
            rows.append(
                {
                    "dataset": dataset.get("id"),
                    "source": dataset.get("source"),
                    "access": dataset.get("access") or source.get("access"),
                    "redistribution": dataset.get("redistribution")
                    or source.get("redistribution"),
                    "files": len(dataset.get("files") or []),
                    "licence": source.get("licence") or "",
                }
            )
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            for row in rows:
                print(
                    f"{row['dataset']:38} {row['source']:22} "
                    f"{row['access']:16} {row['redistribution']:24} files={row['files']}"
                )
        return 0

    if args.dataset:
        selected = [item for item in datasets if item.get("id") == args.dataset]
        if not selected:
            print(f"FAIL: unknown dataset {args.dataset}", file=sys.stderr)
            return 2
    elif args.source or args.all:
        selected = [
            item
            for item in datasets
            if (args.all or item.get("source") == args.source)
        ]
    else:
        parser.print_help()
        return 2

    rows: list[dict] = []
    errors = 0
    for dataset in selected:
        dataset_id = str(dataset.get("id"))
        source_id = str(dataset.get("source"))
        source = sources.get(source_id) or {}
        access = dataset.get("access") or source.get("access")
        redistribution = dataset.get("redistribution") or source.get("redistribution")
        if source_id == "unb-cic":
            rows.append(
                {
                    "dataset": dataset_id,
                    "status": "MANUAL",
                    "file": dataset.get("page"),
                }
            )
            continue
        if source_id in CONTAINER:
            rows.append(
                {
                    "dataset": dataset_id,
                    "status": "CONTAINER",
                    "file": f"{dataset.get('image')}@{dataset.get('image_digest')}",
                }
            )
            continue
        if source_id not in FETCHABLE or access != "public":
            if access == "reference":
                message = (
                    f"{dataset_id}: reference-only ({source.get('licence')}); "
                    "use the source page, not this cache"
                )
            else:
                message = (
                    f"{dataset_id}: fetch refused; source access is "
                    f"{access!r} and redistribution is {redistribution!r}"
                )
            rows.append({"dataset": dataset_id, "status": "SKIP", "file": message})
            continue
        for item in dataset.get("files") or []:
            target = _target(cache, dataset, item)
            expected_hash = str(item.get("sha256"))
            expected_size = int(item.get("bytes"))
            if target.is_file() and not args.force:
                actual_hash = _sha256(target)
                actual_size = target.stat().st_size
                if actual_hash == expected_hash and actual_size == expected_size:
                    rows.append(
                        {
                            "dataset": dataset_id,
                            "file": _display(target),
                            "status": "OK",
                            "bytes": actual_size,
                        }
                    )
                    continue
                if args.verify:
                    rows.append(
                        {
                            "dataset": dataset_id,
                            "file": _display(target),
                            "status": "MISMATCH",
                            "bytes": actual_size,
                        }
                    )
                    errors += 1
                    continue
            if args.verify:
                rows.append(
                    {
                        "dataset": dataset_id,
                        "file": _display(target),
                        "status": "MISSING",
                    }
                )
                errors += 1
                continue
            url = _url(source, item)
            try:
                _download(url, target)
            except (urllib.error.URLError, OSError) as exc:
                rows.append(
                    {
                        "dataset": dataset_id,
                        "file": url,
                        "status": "ERROR",
                        "error": str(exc),
                    }
                )
                errors += 1
                continue
            actual_hash = _sha256(target)
            actual_size = target.stat().st_size
            if actual_hash != expected_hash or actual_size != expected_size:
                rows.append(
                    {
                        "dataset": dataset_id,
                        "file": _display(target),
                        "status": "MISMATCH",
                        "bytes": actual_size,
                    }
                )
                errors += 1
                if not args.force:
                    target.unlink(missing_ok=True)
                continue
            rows.append(
                {
                    "dataset": dataset_id,
                    "file": _display(target),
                    "status": "FETCHED",
                    "bytes": actual_size,
                }
            )

    _report(rows, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

