#!/usr/bin/env python3
"""Seed unsigned drafts for the pre-cycle reviewed contracts.

The 25 contracts marked ``review_status: reviewed`` before the signed review
cycle have no database review. This script creates one unassigned draft per lab
from the current contract so an instructor can open, inspect, and sign it.

Run inside the backend container:

    python /tmp/seed-legacy-contract-drafts.py --dry-run
    python /tmp/seed-legacy-contract-drafts.py --apply

It never creates a signed review and never edits the generated contract file.
"""

from __future__ import annotations

import argparse

import yaml
from app.database import SessionLocal
from app.models import CompetencyContractReview
from app.services.competency_contract import load_contracts
from app.services.competency_contract_integrity import (
    DATA_DIR,
    lab_hash,
    snapshot_hash,
    taxonomy_hash_for,
)

OVERRIDES = DATA_DIR / "competency-contract-overrides.yaml"
INSTITUTION = "default"
DRAFT_RATIONALE = (
    "Draft seeded from the pre-cycle reviewed YAML contract. Confirm the "
    "competencies, evidence, reliability, and criteria, then sign the review."
)


def _reviewed_overrides() -> dict[str, dict]:
    with OVERRIDES.open(encoding="utf-8") as handle:
        document = yaml.safe_load(handle) or {}
    return {
        slug: entry
        for slug, entry in (document.get("labs") or {}).items()
        if isinstance(entry, dict) and entry.get("review_status") == "reviewed"
    }


def _deviation(contract: dict, snapshot: dict) -> dict:
    baseline = {
        str(link.get("id")): float(link.get("weight") or 0)
        for link in contract.get("competency_ids") or []
        if isinstance(link, dict)
    }
    proposed = {
        str(link.get("id")): float(link.get("weight") or 0)
        for link in snapshot.get("competency_ids") or []
        if isinstance(link, dict)
    }
    return {
        "competencies_added": sorted(set(proposed) - set(baseline)),
        "competencies_removed": sorted(set(baseline) - set(proposed)),
        "weights_changed": sorted(
            key
            for key in set(baseline) & set(proposed)
            if abs(baseline[key] - proposed[key]) > 0.001
        ),
        "evidence_types": sorted(
            {
                str(item.get("type"))
                for item in snapshot.get("evidence") or []
                if isinstance(item, dict)
            }
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write the drafts")
    parser.add_argument("--dry-run", action="store_true", help="Only report")
    parser.add_argument("--institution-id", default=INSTITUTION)
    args = parser.parse_args()
    if not args.apply:
        args.dry_run = True

    contracts = load_contracts().get("labs") or {}
    overrides = _reviewed_overrides()
    db = SessionLocal()
    created = []
    skipped_signed = []
    skipped_draft = []
    missing = []
    try:
        for slug in sorted(overrides):
            contract = contracts.get(slug)
            if not isinstance(contract, dict):
                missing.append(slug)
                continue
            signed = (
                db.query(CompetencyContractReview)
                .filter(
                    CompetencyContractReview.lab_slug == slug,
                    CompetencyContractReview.institution_id
                    == args.institution_id,
                    CompetencyContractReview.status.in_(
                        ("signed", "changes_requested")
                    ),
                )
                .first()
            )
            if signed is not None:
                skipped_signed.append(slug)
                continue
            draft = (
                db.query(CompetencyContractReview)
                .filter(
                    CompetencyContractReview.lab_slug == slug,
                    CompetencyContractReview.institution_id
                    == args.institution_id,
                    CompetencyContractReview.status == "draft",
                )
                .first()
            )
            if draft is not None:
                skipped_draft.append(slug)
                continue
            snapshot = {
                "competency_ids": contract.get("competency_ids") or [],
                "evidence": contract.get("evidence") or [],
                "assessment_reliability": contract.get(
                    "assessment_reliability"
                )
                or {},
                "assessment_criteria": contract.get("assessment_criteria")
                or [],
            }
            ids = [
                str(link.get("id"))
                for link in snapshot["competency_ids"]
                if isinstance(link, dict) and link.get("id")
            ]
            created.append(slug)
            if args.dry_run:
                continue
            db.add(
                CompetencyContractReview(
                    institution_id=args.institution_id,
                    lab_slug=slug,
                    status="draft",
                    contract_snapshot=snapshot,
                    contract_hash=snapshot_hash(contract),
                    baseline_hash=snapshot_hash(contract),
                    deviation=_deviation(contract, snapshot),
                    lab_hash=lab_hash(slug),
                    taxonomy_hash=taxonomy_hash_for(ids),
                    rationale=DRAFT_RATIONALE,
                    attestation=False,
                    reviewer_id=None,
                    reviewer_name="Unassigned",
                    reviewer_role="instructor",
                    review_cycle_months=12,
                )
            )
        if args.apply:
            db.commit()
    finally:
        db.close()

    print(f"reviewed overrides: {len(overrides)}")
    print(f"drafts to create: {len(created)}")
    print(f"already signed: {len(skipped_signed)}")
    print(f"already drafted: {len(skipped_draft)}")
    print(f"missing contracts: {len(missing)}")
    if missing:
        print("missing:", ", ".join(missing))
    if created:
        print("labs:", ", ".join(created))
    if args.dry_run:
        print("dry run: no rows written")
    else:
        print("applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
