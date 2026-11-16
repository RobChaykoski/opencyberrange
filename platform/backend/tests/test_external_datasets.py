"""The external dataset registry stays attributable and reference-safe."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "platform/backend/app/data"
REGISTRY = DATA / "external-datasets.yaml"
DETECTION = DATA / "detection-pathway.yaml"
DFIR = DATA / "dfir-pathway.yaml"
REFERENCE_ONLY = {"thezoo", "vx-underground", "pcap-attack"}
CONTAINER = {"juice-shop"}


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _modules() -> dict[str, dict]:
    modules: dict[str, dict] = {}
    for path in (DETECTION, DFIR):
        for module in _load(path).get("modules") or []:
            modules[str(module["id"])] = module
    return modules


def test_registry_and_attribution_are_valid():
    result = subprocess.run(
        [sys.executable, "scripts/check-external-datasets.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_every_external_reference_is_reciprocal():
    registry = _load(REGISTRY)
    sources = {item["id"]: item for item in registry["sources"]}
    datasets = {item["id"]: item for item in registry["datasets"]}
    modules = _modules()

    for dataset in datasets.values():
        source = sources[dataset["source"]]
        for module_id in dataset.get("lab_modules") or []:
            assert module_id in modules, (dataset["id"], module_id)
            assert dataset["id"] in (modules[module_id].get("external_datasets") or []), (
                dataset["id"],
                module_id,
            )
        if source["id"] in REFERENCE_ONLY:
            assert dataset.get("access") == "reference_only", dataset["id"]
            assert dataset.get("redistribution") == "forbidden", dataset["id"]
            assert not dataset.get("files"), dataset["id"]
        if source["id"] in CONTAINER:
            assert dataset.get("access") == "container_image", dataset["id"]
            assert dataset.get("image"), dataset["id"]
            assert str(dataset.get("image_digest", "")).startswith("sha256:"), dataset["id"]
            assert not dataset.get("files"), dataset["id"]

    for module_id, module in modules.items():
        for dataset_id in module.get("external_datasets") or []:
            assert dataset_id in datasets, (module_id, dataset_id)
            assert module_id in (datasets[dataset_id].get("lab_modules") or []), (
                module_id,
                dataset_id,
            )


def test_fetchable_entries_are_hashed_and_pinned():
    registry = _load(REGISTRY)
    sources = {item["id"]: item for item in registry["sources"]}
    for dataset in registry["datasets"]:
        source = sources[dataset["source"]]
        if source["id"] in {"security-datasets", "splunk-attack-data"}:
            assert source.get("pin"), source["id"]
            assert dataset.get("files"), dataset["id"]
            for item in dataset["files"]:
                assert len(item["sha256"]) == 64, (dataset["id"], item["path"])
                assert item["bytes"] > 0, (dataset["id"], item["path"])
        if source["id"] in {"thezoo", "vx-underground", "pcap-attack", "juice-shop"}:
            assert not dataset.get("files"), dataset["id"]
        if source["id"] == "juice-shop":
            assert source.get("pin"), source["id"]
            assert dataset.get("image", "").startswith("bkimminich/juice-shop:"), dataset["id"]
