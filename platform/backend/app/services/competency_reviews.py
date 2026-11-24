"""Review-cycle service for competency contracts.

A review is an append-only, tenant-scoped decision. It does not mutate the
running contract. Approved reviews are exported into the overrides file by an
administrator, then the contracts are regenerated and the release lock is signed.

The effective status comes from the latest signed decision, never from a newer
draft. A draft is shown separately so it cannot hide a valid approval.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

import yaml
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import CompetencyContractReview, User
from app.services.audit import log_admin_action
from app.services.competency_contract import load_contracts, taxonomy_ids
from app.services.evidence import REVIEW_ROLES, _tenant_of

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TAXONOMY_FILE = DATA_DIR / "competency-taxonomy.yaml"
LABS_DIR = Path(__file__).resolve().parents[3] / "labs"
EVIDENCE_TYPES = {"flag", "validation_step", "analyst_answer", "artifact"}
SIGN_ROLES = {"admin", "institution_admin", "instructor"}
CYCLE_MONTHS = (6, 12, 24)
DUE_SOON_DAYS = 60
RELEVANT_SUFFIXES = {".yaml", ".yml", ".md"}
PRIORITY = {
    "overdue": 0,
    "stale": 1,
    "changes_requested": 2,
    "pending": 3,
    "due_soon": 4,
    "draft": 5,
    "current": 6,
}


class ReviewError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical(payload: dict) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


@lru_cache(maxsize=1)
def _taxonomy_entries() -> dict[str, dict]:
    with TAXONOMY_FILE.open(encoding="utf-8") as handle:
        taxonomy = yaml.safe_load(handle) or {}
    entries: dict[str, dict] = {}
    for domain in taxonomy.get("domains", []):
        for category in domain.get("categories", []):
            for competency in category.get("competencies", []):
                entries[str(competency["id"])] = {
                    "id": str(competency["id"]),
                    "name": competency.get("name"),
                    "definition": competency.get("definition"),
                }
    return entries


def taxonomy_hash_for(competency_ids) -> str:
    entries = _taxonomy_entries()
    payload = {str(item): entries.get(str(item)) for item in sorted(set(competency_ids))}
    return _sha(_canonical(payload))


def lab_hash(slug: str) -> str:
    lab = next(
        (path.parent for path in LABS_DIR.rglob("lab.yaml") if path.parent.name == slug),
        None,
    )
    if lab is None:
        raise ReviewError("contract_review_lab_not_found", "The lab does not exist.", 404)
    digest = hashlib.sha256()
    for path in sorted(lab.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in RELEVANT_SUFFIXES:
            continue
        parts = {part.lower() for part in path.parts}
        if "img" in parts or "images" in parts:
            continue
        digest.update(str(path.relative_to(lab)).replace("\\", "/").encode("utf-8"))
        digest.update(path.read_bytes())
    manifest = LABS_DIR.parent / "tester" / "manifests" / f"{slug}.yaml"
    if manifest.is_file():
        digest.update(b"tester-manifest")
        digest.update(manifest.read_bytes())
    return digest.hexdigest()


def _require_reviewer(user: User) -> None:
    if user.role not in REVIEW_ROLES:
        raise ReviewError(
            "contract_review_forbidden",
            "Contract review is available to instructors and administrators.",
            403,
        )


def _require_signer(user: User) -> None:
    if user.role not in SIGN_ROLES:
        raise ReviewError(
            "contract_review_forbidden",
            "Only an instructor or administrator can sign a contract review.",
            403,
        )


def _tenant_scope(user: User) -> str | None:
    return None if user.role == "admin" else _tenant_of(user)


def _contract(slug: str) -> dict:
    contract = (load_contracts().get("labs") or {}).get(slug)
    if not isinstance(contract, dict):
        raise ReviewError(
            "contract_review_lab_not_found",
            "The lab contract does not exist.",
            404,
        )
    return contract


def _review_query(db: Session, slug: str, tenant: str | None):
    query = db.query(CompetencyContractReview).filter(
        CompetencyContractReview.lab_slug == slug
    )
    if tenant:
        query = query.filter(CompetencyContractReview.institution_id == tenant)
    return query


def _latest_decision(
    db: Session, slug: str, tenant: str | None
) -> CompetencyContractReview | None:
    return (
        _review_query(db, slug, tenant)
        .filter(CompetencyContractReview.status.in_(("signed", "changes_requested")))
        .order_by(
            CompetencyContractReview.signed_at.desc(),
            CompetencyContractReview.id.desc(),
        )
        .first()
    )


def _latest_draft(
    db: Session, slug: str, tenant: str | None
) -> CompetencyContractReview | None:
    return (
        _review_query(db, slug, tenant)
        .filter(CompetencyContractReview.status == "draft")
        .order_by(
            CompetencyContractReview.updated_at.desc(),
            CompetencyContractReview.id.desc(),
        )
        .first()
    )


def _competency_ids(contract: dict) -> list[str]:
    return [
        str(link.get("id"))
        for link in contract.get("competency_ids") or []
        if isinstance(link, dict) and link.get("id")
    ]


def review_status(
    contract: dict,
    review: CompetencyContractReview | None,
    now: datetime | None = None,
) -> str:
    if review is None:
        return "pending"
    if review.status == "changes_requested":
        return "changes_requested"
    if review.status != "signed":
        return "pending"
    current = now or _now()
    try:
        if review.lab_hash != lab_hash(review.lab_slug):
            return "stale"
    except ReviewError:
        return "stale"
    ids = _competency_ids(contract)
    if review.taxonomy_hash != taxonomy_hash_for(ids):
        return "stale"
    if review.next_review_at is None or review.next_review_at < current:
        return "overdue"
    if review.next_review_at <= current + timedelta(days=DUE_SOON_DAYS):
        return "due_soon"
    return "current"


def serialize(review: CompetencyContractReview) -> dict:
    return {
        "id": review.id,
        "lab_slug": review.lab_slug,
        "status": review.status,
        "decision": review.decision,
        "rationale": review.rationale,
        "attestation": review.attestation,
        "reviewer_id": review.reviewer_id,
        "reviewer_name": review.reviewer_name,
        "reviewer_role": review.reviewer_role,
        "review_cycle_months": review.review_cycle_months,
        "next_review_at": (
            review.next_review_at.isoformat() + "Z" if review.next_review_at else None
        ),
        "signed_at": review.signed_at.isoformat() + "Z" if review.signed_at else None,
        "exported_at": (
            review.exported_at.isoformat() + "Z" if review.exported_at else None
        ),
        "contract_hash": review.contract_hash,
        "baseline_hash": review.baseline_hash,
        "deviation": review.deviation,
        "lab_hash": review.lab_hash,
        "taxonomy_hash": review.taxonomy_hash,
        "contract_snapshot": review.contract_snapshot,
        "created_at": (
            review.created_at.isoformat() + "Z" if review.created_at else None
        ),
        "updated_at": (
            review.updated_at.isoformat() + "Z" if review.updated_at else None
        ),
    }


def queue(db: Session, user: User) -> dict:
    _require_reviewer(user)
    contracts = load_contracts().get("labs") or {}
    now = _now()
    tenant = _tenant_scope(user)
    query = db.query(CompetencyContractReview).order_by(
        CompetencyContractReview.signed_at.desc(),
        CompetencyContractReview.updated_at.desc(),
        CompetencyContractReview.id.desc(),
    )
    if tenant:
        query = query.filter(CompetencyContractReview.institution_id == tenant)
    decisions: dict[str, CompetencyContractReview] = {}
    drafts: dict[str, CompetencyContractReview] = {}
    for review in query.all():
        if review.status in {"signed", "changes_requested"}:
            decisions.setdefault(review.lab_slug, review)
        elif review.status == "draft":
            drafts.setdefault(review.lab_slug, review)
    rows = []
    counts: dict[str, int] = {}
    for slug, contract in sorted(contracts.items()):
        if not isinstance(contract, dict):
            continue
        review = decisions.get(slug)
        draft = drafts.get(slug)
        status = review_status(contract, review, now)
        if review is None and draft is not None:
            status = "draft"
        counts[status] = counts.get(status, 0) + 1
        rows.append(
            {
                "lab_slug": slug,
                "track": contract.get("track"),
                "difficulty": contract.get("difficulty"),
                "contract_status": contract.get("review_status"),
                "status": status,
                "review_id": review.id if review else None,
                "draft_id": draft.id if draft else None,
                "next_review_at": (
                    review.next_review_at.isoformat() + "Z"
                    if review and review.next_review_at
                    else None
                ),
                "signed_at": (
                    review.signed_at.isoformat() + "Z"
                    if review and review.signed_at
                    else None
                ),
                "reviewer_id": review.reviewer_id if review else None,
                "reviewer_name": review.reviewer_name if review else None,
            }
        )
    rows.sort(
        key=lambda row: (
            PRIORITY.get(row["status"], 99),
            row["track"] or "",
            row["lab_slug"],
        )
    )
    return {"contracts": rows, "counts": counts, "total": len(rows)}


def detail(db: Session, user: User, slug: str) -> dict:
    _require_reviewer(user)
    contract = _contract(slug)
    tenant = _tenant_scope(user)
    review = _latest_decision(db, slug, tenant)
    draft = _latest_draft(db, slug, tenant)
    history = (
        _review_query(db, slug, tenant)
        .order_by(CompetencyContractReview.id.desc())
        .limit(50)
        .all()
    )
    return {
        "lab_slug": slug,
        "contract": contract,
        "status": review_status(contract, review),
        "latest": serialize(review) if review else None,
        "draft": serialize(draft) if draft else None,
        "history": [serialize(row) for row in history],
        "lab_hash": lab_hash(slug),
        "taxonomy_hash": taxonomy_hash_for(_competency_ids(contract)),
    }


def _finite_weight(value, label: str) -> float:
    try:
        weight = float(value)
    except (TypeError, ValueError):
        raise ReviewError("contract_review_invalid", f"{label} weights must be numbers.") from None
    if not math.isfinite(weight) or weight <= 0 or weight > 1:
        raise ReviewError(
            "contract_review_invalid",
            f"{label} weights must be finite and greater than 0 and at most 1.",
        )
    return weight


def _validate_payload(payload: dict) -> dict:
    competencies = payload.get("competency_ids") or []
    if len(competencies) > 20:
        raise ReviewError("contract_review_invalid", "At most 20 competencies are allowed.")
    known = taxonomy_ids()
    normalized = []
    seen: set[str] = set()
    for link in competencies:
        if not isinstance(link, dict) or not link.get("id"):
            raise ReviewError("contract_review_invalid", "Each competency needs an id and a weight.")
        competency_id = str(link["id"])
        if competency_id not in known:
            raise ReviewError("contract_review_invalid", f"Unknown competency {competency_id}.")
        if competency_id in seen:
            raise ReviewError("contract_review_invalid", f"Competency {competency_id} is repeated.")
        seen.add(competency_id)
        normalized.append(
            {"id": competency_id, "weight": _finite_weight(link.get("weight"), "Competency")}
        )
    if not normalized:
        raise ReviewError("contract_review_invalid", "At least one competency is required.")
    if abs(sum(item["weight"] for item in normalized) - 1.0) > 0.001:
        raise ReviewError("contract_review_invalid", "Competency weights must sum to 1.0.")

    evidence = payload.get("evidence") or []
    if len(evidence) > 10:
        raise ReviewError("contract_review_invalid", "At most 10 evidence items are allowed.")
    normalized_evidence = []
    for item in evidence:
        if not isinstance(item, dict) or item.get("type") not in EVIDENCE_TYPES:
            raise ReviewError(
                "contract_review_invalid",
                "Each evidence item must be flag, validation_step, analyst_answer, or artifact.",
            )
        normalized_evidence.append(
            {
                "type": item["type"],
                "weight": _finite_weight(item.get("weight"), "Evidence"),
                "source": str(item.get("source") or "")[:300] or None,
                "validation": str(item.get("validation") or "")[:80] or None,
            }
        )
    if not normalized_evidence or abs(
        sum(item["weight"] for item in normalized_evidence) - 1.0
    ) > 0.001:
        raise ReviewError("contract_review_invalid", "Evidence weights must sum to 1.0.")

    try:
        cycle = int(payload.get("review_cycle_months") or 12)
    except (TypeError, ValueError):
        raise ReviewError("contract_review_invalid", "Review cycle must be 6, 12, or 24 months.") from None
    if cycle not in CYCLE_MONTHS:
        raise ReviewError("contract_review_invalid", "Review cycle must be 6, 12, or 24 months.")
    rationale = str(payload.get("rationale") or "").strip()
    if len(rationale) < 20:
        raise ReviewError(
            "contract_review_rationale_required",
            "A review rationale of at least 20 characters is required.",
        )
    reliability = payload.get("assessment_reliability") or {}
    if not isinstance(reliability, dict):
        raise ReviewError("contract_review_invalid", "Reliability must be an object.")
    allowed_reliability = {
        "level",
        "score",
        "evidence_completeness",
        "determinism",
        "independent_validation",
        "rationale",
    }
    reliability = {
        key: str(value)[:2000]
        for key, value in reliability.items()
        if key in allowed_reliability
    }
    criteria = [
        str(item)[:500]
        for item in (payload.get("assessment_criteria") or [])
        if str(item).strip()
    ][:20]
    return {
        "competency_ids": normalized,
        "evidence": normalized_evidence,
        "assessment_reliability": reliability,
        "assessment_criteria": criteria,
        "review_cycle_months": cycle,
        "rationale": rationale,
    }


def _baseline(contract: dict) -> dict:
    return {
        "competency_ids": contract.get("competency_ids") or [],
        "evidence": contract.get("evidence") or [],
        "assessment_reliability": contract.get("assessment_reliability") or {},
        "assessment_criteria": contract.get("assessment_criteria") or [],
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
            {str(item.get("type")) for item in snapshot.get("evidence") or [] if isinstance(item, dict)}
        ),
    }


def _owned_draft(
    db: Session, user: User, slug: str, tenant: str | None
) -> CompetencyContractReview | None:
    draft = _latest_draft(db, slug, tenant)
    if draft is None:
        return None
    if user.role != "admin" and draft.reviewer_id not in (None, user.id):
        raise ReviewError(
            "contract_review_draft_owned",
            "Another reviewer owns this draft. An administrator must reassign it.",
            409,
        )
    return draft


def save_draft(db: Session, user: User, slug: str, payload: dict) -> dict:
    _require_signer(user)
    contract = _contract(slug)
    normalized = _validate_payload(payload)
    tenant = _tenant_scope(user)
    review = _owned_draft(db, user, slug, tenant)
    if review is None:
        review = CompetencyContractReview(
            institution_id=_tenant_of(user),
            lab_slug=slug,
            status="draft",
            contract_snapshot={},
            contract_hash="",
            lab_hash="",
            taxonomy_hash="",
            rationale=normalized["rationale"],
            reviewer_id=user.id,
            reviewer_name=user.username,
            reviewer_role=user.role,
            review_cycle_months=normalized["review_cycle_months"],
        )
        db.add(review)
    review.contract_snapshot = {
        "competency_ids": normalized["competency_ids"],
        "evidence": normalized["evidence"],
        "assessment_reliability": normalized["assessment_reliability"],
        "assessment_criteria": normalized["assessment_criteria"],
    }
    review.contract_hash = _sha(_canonical(review.contract_snapshot))
    review.baseline_hash = _sha(_canonical(_baseline(contract)))
    review.deviation = _deviation(contract, review.contract_snapshot)
    review.lab_hash = lab_hash(slug)
    review.taxonomy_hash = taxonomy_hash_for(
        [item["id"] for item in normalized["competency_ids"]]
    )
    review.rationale = normalized["rationale"]
    review.review_cycle_months = normalized["review_cycle_months"]
    review.status = "draft"
    review.decision = None
    review.attestation = False
    review.signed_at = None
    review.next_review_at = None
    db.commit()
    db.refresh(review)
    return serialize(review)


def _add_months(value: datetime, months: int) -> datetime:
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    day = min(value.day, 28)
    return value.replace(year=year, month=month, day=day)


def sign(db: Session, user: User, slug: str, payload: dict) -> dict:
    _require_signer(user)
    contract = _contract(slug)
    normalized = _validate_payload(payload)
    if not payload.get("attestation"):
        raise ReviewError(
            "contract_review_attestation_required",
            "The reviewer must attest that they inspected the exercise, workbook, and evidence.",
        )
    decision = str(payload.get("decision") or "").strip()
    if decision not in {"approved", "changes_requested"}:
        raise ReviewError(
            "contract_review_invalid",
            "Decision must be approved or changes_requested.",
        )
    tenant = _tenant_scope(user)
    review = _owned_draft(db, user, slug, tenant)
    if review is None:
        review = CompetencyContractReview(
            institution_id=_tenant_of(user),
            lab_slug=slug,
            status="draft",
            contract_snapshot={},
            contract_hash="",
            lab_hash="",
            taxonomy_hash="",
            rationale=normalized["rationale"],
            reviewer_id=user.id,
            reviewer_name=user.username,
            reviewer_role=user.role,
            review_cycle_months=normalized["review_cycle_months"],
        )
        db.add(review)
    review.contract_snapshot = {
        "competency_ids": normalized["competency_ids"],
        "evidence": normalized["evidence"],
        "assessment_reliability": normalized["assessment_reliability"],
        "assessment_criteria": normalized["assessment_criteria"],
    }
    review.contract_hash = _sha(_canonical(review.contract_snapshot))
    review.baseline_hash = _sha(_canonical(_baseline(contract)))
    review.deviation = _deviation(contract, review.contract_snapshot)
    review.lab_hash = lab_hash(slug)
    review.taxonomy_hash = taxonomy_hash_for(
        [item["id"] for item in normalized["competency_ids"]]
    )
    review.rationale = normalized["rationale"]
    review.review_cycle_months = normalized["review_cycle_months"]
    review.attestation = True
    review.reviewer_id = user.id
    review.reviewer_name = user.username
    review.reviewer_role = user.role
    review.signed_at = _now()
    review.decision = decision
    review.exported_at = None
    review.exported_by_id = None
    if decision == "approved":
        review.status = "signed"
        review.next_review_at = _add_months(
            review.signed_at, normalized["review_cycle_months"]
        )
        superseded = (
            _review_query(db, slug, tenant)
            .filter(
                CompetencyContractReview.id != review.id,
                CompetencyContractReview.status == "signed",
            )
            .update({"status": "superseded"}, synchronize_session=False)
        )
    else:
        review.status = "changes_requested"
        review.next_review_at = None
        superseded = 0
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ReviewError(
            "contract_review_conflict",
            "Another reviewer signed this contract. Reload and try again.",
            409,
        ) from exc
    db.refresh(review)
    log_admin_action(
        action="CONTRACT_REVIEW_SIGNED",
        admin_user_id=user.id,
        admin_username=user.username,
        target_type="competency_contract_review",
        target_id=review.id,
        target_identifier=slug,
        details={
            "decision": decision,
            "cycle_months": review.review_cycle_months,
            "contract_hash": review.contract_hash,
            "lab_hash": review.lab_hash,
            "taxonomy_hash": review.taxonomy_hash,
            "superseded": int(superseded or 0),
        },
    )
    return serialize(review)


def export_ready(db: Session, user: User) -> dict:
    _require_reviewer(user)
    tenant = _tenant_scope(user)
    query = db.query(CompetencyContractReview).filter(
        CompetencyContractReview.status == "signed",
        CompetencyContractReview.decision == "approved",
        CompetencyContractReview.exported_at.is_(None),
    )
    if tenant:
        query = query.filter(CompetencyContractReview.institution_id == tenant)
    reviews = []
    blocked = []
    for row in query.order_by(
        CompetencyContractReview.signed_at.asc(), CompetencyContractReview.id.asc()
    ).all():
        contract = (load_contracts().get("labs") or {}).get(row.lab_slug) or {}
        status = review_status(contract, row)
        item = {
            **serialize(row),
            "cycle_status": status,
        }
        if status in {"current", "due_soon"}:
            reviews.append(item)
        else:
            blocked.append(item)
    return {"reviews": reviews, "blocked": blocked}


def mark_exported(db: Session, user: User, review_id: int) -> dict:
    if user.role not in {"admin", "institution_admin"}:
        raise ReviewError(
            "contract_review_forbidden",
            "Only an administrator can mark a review exported.",
            403,
        )
    tenant = _tenant_scope(user)
    review = db.get(CompetencyContractReview, review_id)
    if review is None or (tenant and review.institution_id != tenant):
        raise ReviewError("contract_review_not_found", "Review not found.", 404)
    if review.status != "signed" or review.decision != "approved":
        raise ReviewError(
            "contract_review_invalid",
            "Only an approved signed review can be exported.",
            409,
        )
    if review.exported_at is not None:
        raise ReviewError(
            "contract_review_already_exported",
            "This review was already exported.",
            409,
        )
    contract = (load_contracts().get("labs") or {}).get(review.lab_slug) or {}
    status = review_status(contract, review)
    if status not in {"current", "due_soon"}:
        raise ReviewError(
            "contract_review_stale",
            "The review is stale or overdue. Re-review the contract before exporting.",
            409,
        )
    now = _now()
    updated = (
        db.query(CompetencyContractReview)
        .filter(
            CompetencyContractReview.id == review.id,
            CompetencyContractReview.exported_at.is_(None),
            CompetencyContractReview.status == "signed",
        )
        .update(
            {"exported_at": now, "exported_by_id": user.id},
            synchronize_session=False,
        )
    )
    if not updated:
        db.rollback()
        raise ReviewError(
            "contract_review_already_exported",
            "This review was already exported.",
            409,
        )
    db.commit()
    db.refresh(review)
    log_admin_action(
        action="CONTRACT_REVIEW_EXPORTED",
        admin_user_id=user.id,
        admin_username=user.username,
        target_type="competency_contract_review",
        target_id=review.id,
        target_identifier=review.lab_slug,
        details={"contract_hash": review.contract_hash},
    )
    return serialize(review)
