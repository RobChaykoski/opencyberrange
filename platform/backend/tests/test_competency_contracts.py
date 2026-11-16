"""The per-lab competency contract is complete, weighted, and reviewable."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

from app.services import competency_contract

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "platform/backend/app/data"
SCHEMA = DATA / "competency-contract.schema.json"
OVERRIDES = DATA / "competency-contract-overrides.yaml"
LABS = ROOT / "platform/labs"


def test_contract_bundle_matches_schema():
    document = yaml.safe_load(
        (DATA / "competency-contracts.yaml").read_text(encoding="utf-8")
    )
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(document, schema)


def test_every_lab_has_a_contract():
    document = competency_contract.load_contracts()
    lab_slugs = {
        path.parent.name for path in LABS.rglob("lab.yaml") if path.is_file()
    }
    contracts = document.get("labs") or {}
    assert set(contracts) == lab_slugs


def test_weights_and_evidence_are_valid():
    assert competency_contract.validate_contracts() == []


def test_collection_policy_excludes_surveillance_signals():
    document = competency_contract.load_contracts()
    assert document["prohibited_collection"] == [
        "keystrokes",
        "mouse_movement",
        "exhaustive_terminal_history",
    ]
    for contract in document["labs"].values():
        assert contract["prohibited_collection"] == document["prohibited_collection"]


def test_highest_use_25_are_reviewed_and_ranked():
    overrides = yaml.safe_load(OVERRIDES.read_text(encoding="utf-8"))
    labs = overrides["labs"]
    assert len(labs) == 25
    ranks = sorted(item["usage_rank"] for item in labs.values())
    assert ranks == list(range(1, 26))
    for slug, override in labs.items():
        contract = competency_contract.contract_for_lab(slug)
        assert contract is not None
        assert contract["review_status"] == "reviewed"
        assert contract["reviewed_at"] == "2026-11-16"
        assert contract["usage_rank"] == override["usage_rank"]
        assert contract["usage_completions"] == override["usage_completions"]


def test_baseline_contracts_are_explicit_but_not_claimed_reviewed():
    for contract in competency_contract.load_contracts()["labs"].values():
        if contract["review_status"] == "reviewed":
            continue
        assert contract["review_status"] == "baseline_derived"
        assert contract["reviewed_at"] is None
        assert contract["expected_duration_minutes"] > 0
        assert contract["competency_ids"]
