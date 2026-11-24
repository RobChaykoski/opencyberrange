#!/usr/bin/env python3
"""Export signed competency-contract reviews and check the release gate.

The dashboard records a signed review in ``competency_contract_reviews``. This
script turns the approved rows into a deterministic, pseudonymous manifest that
can be committed, and an optional full administrator export that is not
committed. It can also write the approved snapshot into
``competency-contract-overrides.yaml``.

The manifest binds a reviewed lab to the contract, lab-content, and taxonomy
hashes. The offline ``--check`` mode refuses a YAML override that claims
``review_status: reviewed`` without a matching signed review.

Usage:
    # Write the manifest and a private administrator export
    python scripts/export-contract-reviews.py --export \
        --database-url "$DATABASE_URL" \
        --admin-export /secure/ocr-contract-reviews.json

    # Merge approved reviews into the overrides file, then regenerate
    python scripts/export-contract-reviews.py --write-overrides \
        --database-url "$DATABASE_URL"

    # Offline release gate
    python scripts/export-contract-reviews.py --check
    python scripts/export-contract-reviews.py --check --require-all
    python scripts/export-contract-reviews.py --check \
        --signature docs/competency-reviews.lock.json.asc \
        --gpg-public-key docs/release-signing-key.asc \
        --gpg-fingerprint 68A817762C831475F00DB54E775050A4C4921814

The manifest is pseudonymous: it records a stable reviewer reference and a hash
of the rationale, not the reviewer name or the review notes. The administrator
export keeps the full record and must be stored outside the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "platform" / "backend"
SCRIPTS = ROOT / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import yaml
from app.services.competency_contract_integrity import (
    canonical,
    lab_hash,
    sha,
    snapshot_hash,
    taxonomy_hash_for,
)
from sqlalchemy import create_engine, text
from supply_chain import verify_signature

DATA = BACKEND / "app" / "data"
CONTRACTS = DATA / "competency-contracts.yaml"
OVERRIDES = DATA / "competency-contract-overrides.yaml"
DEFAULT_MANIFEST = ROOT / "docs" / "competency-reviews.lock.json"
SCHEMA = 1
KIND = "competency-contract-review-manifest"
SIGN_ROLES = {"admin", "institution_admin", "instructor"}
CYCLE_MONTHS = (6, 12, 24)
DUE_SOON_DAYS = 60


class ExportError(Exception):
    pass


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def iso(value: datetime | None) -> str | None:
    return value.isoformat() + "Z" if value else None


def parse_iso(value) -> datetime | None:
    if not value:
        return None
    raw = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(UTC).replace(tzinfo=None)
    return parsed


def reviewer_ref(row: dict) -> str:
    material = "\0".join(
        [
            str(row.get("institution_id") or ""),
            str(row.get("reviewer_id") or ""),
            str(row.get("reviewer_name") or ""),
        ]
    )
    return "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def rationale_hash(value: str | None) -> str:
    return "sha256:" + hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def manifest_digest(document: dict) -> str:
    payload = {
        "schema": document["schema"],
        "kind": document["kind"],
        "institution_id": document["institution_id"],
        "reviews": document["reviews"],
    }
    return "sha256:" + sha(canonical(payload))


def canonical_json(document: dict) -> str:
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def database_url_for_sqlalchemy(value: str) -> str:
    """Use the installed psycopg 3 driver for a plain PostgreSQL URL."""
    if value.startswith("postgres://"):
        return "postgresql+psycopg://" + value[len("postgres://") :]
    if value.startswith("postgresql://"):
        return "postgresql+psycopg://" + value[len("postgresql://") :]
    return value


def fetch_reviews(database_url: str, institution_id: str) -> list[dict]:
    engine = create_engine(database_url_for_sqlalchemy(database_url), future=True)
    query = text(
        """
        SELECT id, institution_id, lab_slug, decision, reviewer_id, reviewer_name,
               reviewer_role, signed_at, next_review_at, review_cycle_months,
               contract_snapshot, contract_hash, baseline_hash, lab_hash,
               taxonomy_hash, rationale, attestation, exported_at
        FROM competency_contract_reviews
        WHERE status = 'signed'
          AND decision = 'approved'
          AND institution_id = :institution_id
        ORDER BY lab_slug ASC, signed_at DESC, id DESC
        """
    )
    with engine.connect() as connection:
        rows = connection.execute(
            query, {"institution_id": institution_id}
        ).mappings().all()
    engine.dispose()

    latest: dict[str, dict] = {}
    for row in rows:
        item = dict(row)
        snapshot = item.get("contract_snapshot")
        if isinstance(snapshot, str):
            snapshot = json.loads(snapshot)
        if not isinstance(snapshot, dict):
            raise ExportError(
                f"review {item['id']} has no contract snapshot"
            )
        item["contract_snapshot"] = snapshot
        latest.setdefault(str(item["lab_slug"]), item)
    return [latest[slug] for slug in sorted(latest)]


def manifest_entry(row: dict) -> dict:
    return {
        "lab_slug": str(row["lab_slug"]),
        "review_id": int(row["id"]),
        "institution_id": str(row["institution_id"]),
        "decision": str(row["decision"]),
        "reviewer_ref": reviewer_ref(row),
        "reviewer_role": str(row["reviewer_role"]),
        "signed_at": iso(row.get("signed_at")),
        "next_review_at": iso(row.get("next_review_at")),
        "review_cycle_months": int(row.get("review_cycle_months") or 12),
        "contract_hash": str(row.get("contract_hash") or ""),
        "baseline_hash": str(row.get("baseline_hash") or ""),
        "lab_hash": str(row.get("lab_hash") or ""),
        "taxonomy_hash": str(row.get("taxonomy_hash") or ""),
        "rationale_hash": rationale_hash(row.get("rationale")),
    }


def build_manifest(rows: list[dict], institution_id: str) -> dict:
    reviews = [manifest_entry(row) for row in rows]
    document = {
        "schema": SCHEMA,
        "kind": KIND,
        "institution_id": institution_id,
        "reviews": reviews,
    }
    document["manifest_hash"] = manifest_digest(document)
    return document


def admin_export(rows: list[dict], institution_id: str) -> dict:
    return {
        "schema": SCHEMA,
        "kind": "competency-contract-review-admin-export",
        "institution_id": institution_id,
        "generated_at": iso(utc_now()),
        "reviews": [
            {
                "lab_slug": row["lab_slug"],
                "review_id": row["id"],
                "reviewer_id": row.get("reviewer_id"),
                "reviewer_name": row.get("reviewer_name"),
                "reviewer_role": row.get("reviewer_role"),
                "decision": row.get("decision"),
                "attestation": bool(row.get("attestation")),
                "rationale": row.get("rationale"),
                "signed_at": iso(row.get("signed_at")),
                "next_review_at": iso(row.get("next_review_at")),
                "review_cycle_months": row.get("review_cycle_months"),
                "contract_hash": row.get("contract_hash"),
                "baseline_hash": row.get("baseline_hash"),
                "lab_hash": row.get("lab_hash"),
                "taxonomy_hash": row.get("taxonomy_hash"),
                "exported_at": iso(row.get("exported_at")),
                "contract_snapshot": row.get("contract_snapshot"),
            }
            for row in rows
        ],
    }


def write_manifest(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(document), encoding="utf-8", newline="\n")


def merge_overrides(rows: list[dict], path: Path = OVERRIDES) -> dict:
    document = load_yaml(path)
    labs = document.setdefault("labs", {})
    for row in rows:
        slug = str(row["lab_slug"])
        snapshot = row["contract_snapshot"]
        entry = dict(labs.get(slug) or {})
        entry["competency_ids"] = snapshot.get("competency_ids") or []
        entry["evidence"] = snapshot.get("evidence") or []
        entry["assessment_reliability"] = snapshot.get("assessment_reliability") or {}
        entry["assessment_criteria"] = snapshot.get("assessment_criteria") or []
        entry["review_status"] = "reviewed"
        signed_at = parse_iso(row.get("signed_at"))
        entry["reviewed_at"] = signed_at.date().isoformat() if signed_at else None
        entry["review_id"] = int(row["id"])
        entry["review_hash"] = str(row.get("contract_hash") or "")
        entry["reviewer_ref"] = reviewer_ref(row)
        entry["reviewer_role"] = str(row.get("reviewer_role") or "")
        entry.pop("evidence_weights", None)
        labs[slug] = entry
    document["labs"] = labs
    return document


def write_overrides(document: dict, path: Path = OVERRIDES) -> None:
    rendered = yaml.safe_dump(
        document, sort_keys=False, default_flow_style=False, width=1000
    )
    path.write_text(rendered, encoding="utf-8", newline="\n")


def check_manifest(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        return [f"missing manifest: {manifest_path} (run --export)"]

    if args.signature:
        errors.extend(
            verify_signature(
                manifest_path,
                Path(args.signature),
                args.public_key,
                gpg_public_key=args.gpg_public_key,
                gpg_fingerprint=args.gpg_fingerprint,
            )
        )

    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return errors + [f"manifest is not valid JSON: {exc}"]

    if document.get("schema") != SCHEMA or document.get("kind") != KIND:
        errors.append("manifest schema or kind is not recognised")
    reviews = document.get("reviews")
    if not isinstance(reviews, list):
        return errors + ["manifest has no reviews list"]
    if document.get("manifest_hash") != manifest_digest(document):
        errors.append("manifest hash does not match its reviews")

    contracts = (load_yaml(Path(args.contracts)).get("labs") or {})
    overrides = (load_yaml(Path(args.overrides)).get("labs") or {})
    by_slug: dict[str, dict] = {}
    for entry in reviews:
        slug = str(entry.get("lab_slug") or "")
        if not slug:
            errors.append("manifest entry has no lab_slug")
            continue
        if slug in by_slug:
            errors.append(f"{slug}: duplicate manifest entry")
        by_slug[slug] = entry

    now = utc_now()
    checked = 0
    for slug, contract in sorted(contracts.items()):
        if not isinstance(contract, dict):
            continue
        override = overrides.get(slug) or {}
        reviewed = str(override.get("review_status") or "") == "reviewed"
        entry = by_slug.get(slug)
        if reviewed and entry is None:
            errors.append(f"{slug}: reviewed override has no signed review")
            continue
        if entry is not None and not reviewed:
            errors.append(f"{slug}: signed review has no reviewed override")
            continue
        if not reviewed:
            if args.require_all:
                errors.append(f"{slug}: contract is not reviewed")
            continue

        checked += 1
        if entry.get("decision") != "approved":
            errors.append(f"{slug}: manifest decision is not approved")
        if entry.get("reviewer_role") not in SIGN_ROLES:
            errors.append(f"{slug}: reviewer role cannot sign")
        if not str(entry.get("reviewer_ref") or "").startswith("sha256:"):
            errors.append(f"{slug}: reviewer reference is missing")
        if not str(entry.get("rationale_hash") or "").startswith("sha256:"):
            errors.append(f"{slug}: rationale hash is missing")
        if int(entry.get("review_cycle_months") or 0) not in CYCLE_MONTHS:
            errors.append(f"{slug}: review cycle is not 6, 12, or 24 months")
        if entry.get("contract_hash") != snapshot_hash(contract):
            errors.append(f"{slug}: signed contract hash no longer matches the generated contract")
        if entry.get("lab_hash") != lab_hash(slug):
            errors.append(f"{slug}: lab content changed after the signature")
        ids = [
            str(link.get("id"))
            for link in contract.get("competency_ids") or []
            if isinstance(link, dict) and link.get("id")
        ]
        if entry.get("taxonomy_hash") != taxonomy_hash_for(ids):
            errors.append(f"{slug}: taxonomy changed after the signature")
        signed_at = parse_iso(entry.get("signed_at"))
        if signed_at is None:
            errors.append(f"{slug}: signed_at is missing")
        if override.get("review_id") != entry.get("review_id"):
            errors.append(f"{slug}: override review_id does not match the manifest")
        if override.get("review_hash") != entry.get("contract_hash"):
            errors.append(f"{slug}: override review_hash does not match the manifest")
        reviewed_at = str(override.get("reviewed_at") or "")
        if signed_at and reviewed_at != signed_at.date().isoformat():
            errors.append(f"{slug}: override reviewed_at does not match the signature date")
        next_review = parse_iso(entry.get("next_review_at"))
        if next_review is None:
            errors.append(f"{slug}: next_review_at is missing")
        elif next_review < now and not args.allow_overdue:
            errors.append(f"{slug}: review is overdue (next review {next_review.date()})")

    for slug in sorted(set(by_slug) - set(contracts)):
        errors.append(f"{slug}: manifest entry has no generated contract")

    if args.require_all:
        missing = [
            slug
            for slug, contract in contracts.items()
            if isinstance(contract, dict)
            and str((overrides.get(slug) or {}).get("review_status") or "") != "reviewed"
        ]
        if missing:
            errors.append(
                f"{len(missing)} contract(s) are not reviewed; first: {', '.join(sorted(missing)[:5])}"
            )
    print(
        f"checked {checked} signed review(s); "
        f"{sum(1 for s in contracts if str((overrides.get(s) or {}).get('review_status') or '') == 'reviewed')} reviewed override(s); "
        f"{len(contracts)} contract(s)"
    )
    return errors


def print_summary(rows: list[dict], contracts_path: Path = CONTRACTS, overrides_path: Path = OVERRIDES) -> None:
    contracts = load_yaml(contracts_path).get("labs") or {}
    overrides = load_yaml(overrides_path).get("labs") or {}
    reviewed = [
        slug
        for slug, entry in overrides.items()
        if str((entry or {}).get("review_status") or "") == "reviewed"
    ]
    signed = {str(row["lab_slug"]) for row in rows}
    print(f"contracts: {len(contracts)}")
    print(f"reviewed overrides: {len(reviewed)}")
    print(f"signed approvals in the export scope: {len(signed)}")
    print(f"reviewed overrides without a signed approval: {len(set(reviewed) - signed)}")
    print(f"signed approvals without a reviewed override: {len(signed - set(reviewed))}")
    print(f"contracts still pending: {len(set(contracts) - set(reviewed))}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("OCR_REVIEW_DATABASE_URL") or os.environ.get("DATABASE_URL"))
    parser.add_argument("--institution-id", default="default")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--contracts", default=str(CONTRACTS))
    parser.add_argument("--overrides", default=str(OVERRIDES))
    parser.add_argument("--admin-export", type=Path)
    parser.add_argument("--export", action="store_true", help="Write the signed-review manifest")
    parser.add_argument("--write-overrides", action="store_true", help="Merge approved reviews into the overrides file")
    parser.add_argument("--check", action="store_true", help="Check the manifest and YAML overrides offline")
    parser.add_argument("--require-all", action="store_true", help="Fail while any contract is unreviewed")
    parser.add_argument("--allow-overdue", action="store_true", help="Allow an overdue next-review date")
    parser.add_argument("--summary", action="store_true", help="Print review coverage without failing")
    parser.add_argument("--signature", help="Detached signature over the manifest")
    parser.add_argument("--public-key", help="minisign public key")
    parser.add_argument("--gpg-public-key", help="GnuPG public key file")
    parser.add_argument("--gpg-fingerprint", help="Require this GnuPG fingerprint")
    args = parser.parse_args()

    modes = [args.export, args.write_overrides, args.check, args.summary]
    if not any(modes):
        args.check = True
    needs_database = args.export or args.write_overrides or args.admin_export or args.summary
    if needs_database and not args.database_url:
        parser.error("--database-url (or OCR_REVIEW_DATABASE_URL / DATABASE_URL) is required")

    rows: list[dict] = []
    if needs_database:
        try:
            rows = fetch_reviews(args.database_url, args.institution_id)
        except Exception as exc:  # noqa: BLE001 - the CLI must report any DB failure
            print(f"ERROR: could not read signed reviews: {exc}", file=sys.stderr)
            return 1

    if args.export:
        document = build_manifest(rows, args.institution_id)
        write_manifest(Path(args.manifest), document)
        print(f"wrote {Path(args.manifest)} ({len(rows)} signed review(s))")
    if args.admin_export:
        args.admin_export.parent.mkdir(parents=True, exist_ok=True)
        args.admin_export.write_text(
            json.dumps(admin_export(rows, args.institution_id), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote administrator export {args.admin_export} (not for publication)")
    if args.write_overrides:
        overrides_path = Path(args.overrides)
        document = merge_overrides(rows, overrides_path)
        write_overrides(document, overrides_path)
        print(f"wrote {overrides_path} ({len(rows)} approved review(s))")
        print("next: python scripts/generate-competency-contracts.py")
        print("next: python scripts/generate-competency-review-queue.py")
        print("next: python scripts/validate-competency-contracts.py")
        print("next: python scripts/supply_chain.py --update")
    if args.summary:
        print_summary(rows, Path(args.contracts), Path(args.overrides))
    if args.check:
        errors = check_manifest(args)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            print(f"FAILED: {len(errors)} review-gate problem(s)", file=sys.stderr)
            return 1
        print("PASS: every reviewed contract has a matching signed review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
