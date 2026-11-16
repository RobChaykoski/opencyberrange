#!/usr/bin/env python3
"""Validate the external open dataset registry and its attributions.

The registry is deliberately a register, not a data dump. This check enforces
the rules that keep lab building reproducible and legally attributable:

* every source has a name, homepage, licence, attribution, and access policy;
* every fetchable file is pinned to a commit and has a SHA-256;
* every pathway reference resolves to a real module and is reciprocal;
* a source with no declared licence stays reference-only;
* live-malware sources never carry a redistributable file entry;
* the notices and documentation name every source.

Usage:
    python scripts/check-external-datasets.py
    python scripts/check-external-datasets.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "platform/backend/app/data/external-datasets.yaml"
DETECTION = ROOT / "platform/backend/app/data/detection-pathway.yaml"
DFIR = ROOT / "platform/backend/app/data/dfir-pathway.yaml"
NOTICES = ROOT / "THIRD_PARTY_NOTICES.md"
DOCS = ROOT / "docs/SECURITY-DATASETS.md"
MALWARE_DOCS = ROOT / "docs/MALWARE-SAMPLE-SOURCES.md"
CACHE = ROOT / "platform/backend/app/data/external-datasets/cache"

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ATTACK_RE = re.compile(r"^(T\d{4}(?:\.\d{3})?|G\d{4})$")
REFERENCE_ONLY_SOURCES = {"thezoo", "vx-underground", "pcap-attack"}
FETCHABLE_SOURCES = {"security-datasets", "splunk-attack-data"}
CITATION_SOURCES = {"unb-cic"}
CONTAINER_SOURCES = {"juice-shop"}
STANDARD_SOURCES = {
    "owasp-api-security",
    "owasp-top10-2025",
    "owasp-agentic-skills",
    "opencre",
}


def _read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _module_ids() -> set[str]:
    ids: set[str] = set()
    for path in (DETECTION, DFIR):
        for module in _read_yaml(path).get("modules") or []:
            ids.add(str(module.get("id")))
    return ids


def _module_external() -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for path in (DETECTION, DFIR):
        for module in _read_yaml(path).get("modules") or []:
            mapping[str(module.get("id"))] = [
                str(item) for item in (module.get("external_datasets") or [])
            ]
    return mapping


def _tracked_cache_files() -> list[str]:
    try:
        output = subprocess.run(
            ["git", "ls-files", "-z", str(CACHE.relative_to(ROOT))],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return [item for item in output.decode("utf-8", "surrogateescape").split("\0") if item]


def _check_source(source: dict, errors: list[str]) -> None:
    label = source.get("id") or "source"
    for field in (
        "id",
        "name",
        "homepage",
        "licence",
        "attribution",
        "redistribution",
        "access",
        "fetch",
    ):
        if not str(source.get(field) or "").strip():
            errors.append(f"{label}: missing {field}")
    if not str(source.get("homepage") or "").startswith("https://"):
        errors.append(f"{label}: homepage must be https")
    if source.get("fetch") in {"github_raw", "github_lfs"}:
        if not source.get("pin"):
            errors.append(f"{label}: a fetchable source needs a commit pin")
        if not str(source.get("fetch_base") or "").startswith("https://"):
            errors.append(f"{label}: a fetchable source needs an https fetch_base")
    if source.get("fetch") == "container":
        if not source.get("pin"):
            errors.append(f"{label}: a container source needs a pinned tag and digest")
        if not str(source.get("fetch_base") or "").strip():
            errors.append(f"{label}: a container source needs an image reference")
    if source.get("redistribution") == "forbidden" and source.get("access") != "reference_only":
        errors.append(f"{label}: forbidden redistribution must be reference_only")


def _check_file(source_id: str, dataset: dict, item: dict, errors: list[str]) -> None:
    label = f"{dataset.get('id')}: file"
    if not str(item.get("path") or "").strip():
        errors.append(f"{label}: missing path")
    if not isinstance(item.get("bytes"), int) or item.get("bytes", 0) <= 0:
        errors.append(f"{label}: bytes must be a positive integer")
    if not SHA256_RE.match(str(item.get("sha256") or "")):
        errors.append(f"{label}: sha256 must be 64 lowercase hex characters")
    if not str(item.get("media_type") or "").strip():
        errors.append(f"{label}: missing media_type")
    if source_id == "splunk-attack-data" and item.get("lfs") is not True:
        errors.append(f"{label}: Splunk attack_data logs must declare lfs: true")


def _check_dataset(
    dataset: dict,
    source: dict,
    module_ids: set[str],
    module_external: dict[str, list[str]],
    errors: list[str],
) -> None:
    source_id = str(dataset.get("source") or "")
    label = str(dataset.get("id") or "dataset")
    for field in ("source", "id", "title", "kind", "platform", "attack", "use", "files"):
        if field not in dataset:
            errors.append(f"{label}: missing {field}")
    if not str(dataset.get("title") or "").strip():
        errors.append(f"{label}: title is required")
    if not str(dataset.get("use") or "").strip():
        errors.append(f"{label}: use is required")
    if not isinstance(dataset.get("platform"), list) or not dataset.get("platform"):
        errors.append(f"{label}: platform must be a non-empty list")
    if not isinstance(dataset.get("attack"), list):
        errors.append(f"{label}: attack must be a list")
    else:
        for technique in dataset.get("attack") or []:
            if not ATTACK_RE.match(str(technique)):
                errors.append(f"{label}: invalid ATT&CK id {technique!r}")
    if dataset.get("attack_group") and not ATTACK_RE.match(str(dataset.get("attack_group"))):
        errors.append(f"{label}: invalid ATT&CK group id {dataset.get('attack_group')!r}")

    lab_modules = dataset.get("lab_modules")
    if not isinstance(lab_modules, list):
        errors.append(f"{label}: lab_modules must be a list")
        lab_modules = []
    for module in lab_modules:
        if module not in module_ids:
            errors.append(f"{label}: unknown pathway module {module!r}")
        elif label not in module_external.get(module, []):
            errors.append(f"{label}: {module} does not list it in external_datasets")

    if source_id in REFERENCE_ONLY_SOURCES:
        if dataset.get("access") != "reference_only":
            errors.append(f"{label}: {source_id} entries must declare access: reference_only")
        if dataset.get("redistribution") != "forbidden":
            errors.append(f"{label}: {source_id} entries must declare redistribution: forbidden")
        if dataset.get("files"):
            errors.append(f"{label}: {source_id} must not carry a file entry")
    elif source_id in FETCHABLE_SOURCES:
        files = dataset.get("files") or []
        if not files:
            errors.append(f"{label}: a fetchable dataset must list at least one file")
        for item in files:
            _check_file(source_id, dataset, item, errors)
    elif source_id in CITATION_SOURCES:
        if dataset.get("files"):
            errors.append(f"{label}: CIC entries stay as a download page, not a vendored file")
        for field in ("citation", "page", "download"):
            if not str(dataset.get(field) or "").strip():
                errors.append(f"{label}: CIC entry needs {field}")
        if not str(dataset.get("page") or "").startswith("https://"):
            errors.append(f"{label}: CIC page must be https")
    elif source_id in STANDARD_SOURCES:
        if dataset.get("files"):
            errors.append(f"{label}: a standards baseline is a reference, not a data file")
        for field in ("citation", "licence"):
            if not str(dataset.get(field) or "").strip():
                errors.append(f"{label}: standards baseline needs {field}")
        if dataset.get("access") != "reference":
            errors.append(f"{label}: standards baseline access must be reference")
    elif source_id in CONTAINER_SOURCES:
        if dataset.get("files"):
            errors.append(f"{label}: a container lab application is not a fetched data file")
        if not str(dataset.get("image") or "").strip():
            errors.append(f"{label}: a container lab needs an image reference")
        if not re.match(r"^sha256:[0-9a-f]{64}$", str(dataset.get("image_digest") or "")):
            errors.append(f"{label}: image_digest must be a sha256 digest")
        if dataset.get("access") != "container_image":
            errors.append(f"{label}: container lab access must be container_image")
    elif source_id == "aman-hardikar-forensics":
        if dataset.get("files"):
            errors.append(f"{label}: the mind map is an index, not a data file")
        if not str(dataset.get("citation") or "").strip():
            errors.append(f"{label}: the mind map needs a citation")
    else:
        errors.append(f"{label}: unknown source {source_id!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    args = parser.parse_args()

    errors: list[str] = []
    document = _read_yaml(REGISTRY)
    policy = document.get("policy") or {}
    if policy.get("raw_data_committed") is not False:
        errors.append("policy.raw_data_committed must be false")
    if policy.get("live_malware_committed") is not False:
        errors.append("policy.live_malware_committed must be false")
    if policy.get("require_sha256_when_fetchable") is not True:
        errors.append("policy.require_sha256_when_fetchable must be true")
    cache_root = str(policy.get("cache_root") or "")
    if not cache_root:
        errors.append("policy.cache_root is required")
    elif CACHE.resolve() != (ROOT / cache_root).resolve():
        errors.append("policy.cache_root must match the documented cache path")

    sources = document.get("sources") or []
    datasets = document.get("datasets") or []
    if not sources:
        errors.append("no sources declared")
    if not datasets:
        errors.append("no datasets declared")

    source_map: dict[str, dict] = {}
    for source in sources:
        source_id = str(source.get("id") or "")
        if source_id in source_map:
            errors.append(f"duplicate source id: {source_id}")
        source_map[source_id] = source
        _check_source(source, errors)

    module_ids = _module_ids()
    module_external = _module_external()
    dataset_ids: set[str] = set()
    for dataset in datasets:
        dataset_id = str(dataset.get("id") or "")
        if dataset_id in dataset_ids:
            errors.append(f"duplicate dataset id: {dataset_id}")
        dataset_ids.add(dataset_id)
        source = source_map.get(str(dataset.get("source") or ""))
        if source is None:
            errors.append(f"{dataset_id}: source does not exist")
            continue
        _check_dataset(dataset, source, module_ids, module_external, errors)

    for module, entries in module_external.items():
        for entry in entries:
            if entry not in dataset_ids:
                errors.append(f"{module}: unknown external dataset {entry!r}")

    notices = NOTICES.read_text(encoding="utf-8") if NOTICES.is_file() else ""
    docs = DOCS.read_text(encoding="utf-8") if DOCS.is_file() else ""
    malware_docs = MALWARE_DOCS.read_text(encoding="utf-8") if MALWARE_DOCS.is_file() else ""
    for source_id, source in source_map.items():
        name = str(source.get("name") or source_id)
        if not DOCS.is_file():
            errors.append("docs/SECURITY-DATASETS.md is missing")
            break
        if name not in docs and source_id not in docs:
            errors.append(f"{source_id}: not named in docs/SECURITY-DATASETS.md")
        if name not in notices and source_id not in notices:
            errors.append(f"{source_id}: not named in THIRD_PARTY_NOTICES.md")
        if source_id in REFERENCE_ONLY_SOURCES and not MALWARE_DOCS.is_file():
            errors.append("docs/MALWARE-SAMPLE-SOURCES.md is missing")
            break
        if source_id in {"thezoo", "vx-underground"} and name not in malware_docs:
            errors.append(f"{source_id}: not named in docs/MALWARE-SAMPLE-SOURCES.md")

    if CACHE.exists():
        tracked = _tracked_cache_files()
        if tracked:
            errors.append("external dataset cache files are tracked: " + ", ".join(tracked[:3]))

    report = {
        "sources": len(sources),
        "datasets": len(datasets),
        "fetchable": sum(1 for item in datasets if item.get("source") in FETCHABLE_SOURCES),
        "citation_required": sum(1 for item in datasets if item.get("source") in CITATION_SOURCES),
        "reference_only": sum(1 for item in datasets if item.get("source") in REFERENCE_ONLY_SOURCES),
        "container_images": sum(1 for item in datasets if item.get("source") in CONTAINER_SOURCES),
        "standards": sum(1 for item in datasets if item.get("source") in STANDARD_SOURCES),
        "modules_with_external_data": sum(1 for items in module_external.values() if items),
        "errors": errors,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("External dataset registry")
        print("=" * 40)
        print(f"sources: {report['sources']}")
        print(f"datasets: {report['datasets']}")
        print(f"fetchable: {report['fetchable']}")
        print(f"citation required: {report['citation_required']}")
        print(f"reference only: {report['reference_only']}")
        print(f"container lab images: {report['container_images']}")
        print(f"standards: {report['standards']}")
        print(f"pathway modules with external data: {report['modules_with_external_data']}")
        if errors:
            for error in errors:
                print(f"FAIL: {error}")
        else:
            print("PASS: sources, attribution, pins, hashes, and pathway references")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
