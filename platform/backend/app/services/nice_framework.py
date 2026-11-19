"""NICE Framework v2.2.0 ingestion and lookup.

The authoritative machine-readable source is published by NIST:

    https://csrc.nist.gov/csrc/media/Projects/cprt/documents/nice/
    v2-2-0_nf_components.json

A compressed snapshot ships with the platform so a fresh install can populate
the authoring dropdown without network access. An administrator can refresh from
the official URL later; component codes are stable, so existing lab mappings
survive a refresh.
"""

from __future__ import annotations

import gzip
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import requests
import yaml
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Lab
from app.models.nice import (
    LabNiceComponent,
    LabNiceMetadata,
    NiceComponent,
    NiceFrameworkMeta,
    NiceLink,
)

logger = logging.getLogger(__name__)

NICE_VERSION = "2.2.0"
OFFICIAL_URL = (
    "https://csrc.nist.gov/csrc/media/Projects/cprt/documents/nice/"
    "v2-2-0_nf_components.json"
)
SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "nice" / "nice-v2.2.0.json.gz"
)
LAB_MAPPINGS_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "nice" / "lab-mappings.yaml"
)
MAX_DOWNLOAD_BYTES = 20 * 1024 * 1024
COMPONENT_TYPES = ("work_role", "task", "knowledge", "skill")
LINK_TYPES = {
    "task": "work_role_task",
    "knowledge": "work_role_knowledge",
    "skill": "work_role_skill",
}


def _load_snapshot() -> dict:
    with gzip.open(SNAPSHOT_PATH, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _download_official() -> dict:
    with requests.get(
        OFFICIAL_URL,
        timeout=45,
        headers={"User-Agent": "OpenCyberRange NICE ingestion/1.0"},
        stream=True,
    ) as response:
        response.raise_for_status()
        size = 0
        chunks = []
        for chunk in response.iter_content(chunk_size=65536):
            size += len(chunk)
            if size > MAX_DOWNLOAD_BYTES:
                raise ValueError("NICE Framework download is too large")
            chunks.append(chunk)
    return json.loads(b"".join(chunks).decode("utf-8"))


def _prepare(payload: dict) -> dict:
    documents = payload.get("documents") or []
    version = str((documents[0] if documents else {}).get("version") or "")
    if not version.startswith("2.2"):
        raise ValueError(f"Unexpected NICE Framework version: {version or 'missing'}")

    elements = {
        item["element_identifier"]: item
        for item in payload.get("elements", [])
        if item.get("element_type") in {"category", *COMPONENT_TYPES}
    }
    categories = {
        item["element_identifier"]: item
        for item in elements.values()
        if item.get("element_type") == "category"
    }

    components = []
    for item in elements.values():
        element_type = item.get("element_type")
        if element_type not in COMPONENT_TYPES:
            continue
        identifier = str(item["element_identifier"])
        category_code = None
        category_name = None
        if element_type == "work_role":
            category_code = identifier.split("-", 1)[0]
            category = categories.get(category_code) or {}
            category_name = category.get("title")
        components.append(
            {
                "component_type": element_type,
                "code": identifier,
                "name": str(item.get("title") or identifier),
                "statement": str(item.get("text") or ""),
                "category_code": category_code,
                "category_name": category_name,
            }
        )

    links = []
    for relation in payload.get("relationships", []):
        source = elements.get(relation.get("source_element_identifier"))
        target = elements.get(relation.get("dest_element_identifier"))
        if not source or not target:
            continue
        if source.get("element_type") != "work_role":
            continue
        target_type = target.get("element_type")
        if target_type not in LINK_TYPES:
            continue
        links.append(
            {
                "source_code": source["element_identifier"],
                "target_code": target["element_identifier"],
                "target_type": target_type,
                "link_type": LINK_TYPES[target_type],
            }
        )

    return {
        "version": version,
        "components": components,
        "links": links,
    }


def ingest_payload(
    db: Session,
    payload: dict,
    *,
    source: str,
    source_url: Optional[str] = None,
) -> dict:
    prepared = _prepare(payload)
    existing = {
        (row.component_type, row.code): row
        for row in db.query(NiceComponent).all()
    }
    seen = set()
    for item in prepared["components"]:
        key = (item["component_type"], item["code"])
        seen.add(key)
        row = existing.get(key)
        if row is None:
            row = NiceComponent(version=prepared["version"], is_active=True, **item)
            db.add(row)
        else:
            row.name = item["name"]
            row.statement = item["statement"]
            row.category_code = item["category_code"]
            row.category_name = item["category_name"]
            row.version = prepared["version"]
            row.is_active = True
    for key, row in existing.items():
        if key not in seen:
            row.is_active = False
    db.flush()

    id_by = {
        (row.component_type, row.code): row.id
        for row in db.query(NiceComponent).all()
    }
    db.query(NiceLink).delete(synchronize_session=False)
    db.flush()
    for link in prepared["links"]:
        source_id = id_by.get(("work_role", link["source_code"]))
        target_id = id_by.get((link["target_type"], link["target_code"]))
        if source_id is None or target_id is None:
            continue
        db.add(
            NiceLink(
                source_id=source_id,
                target_id=target_id,
                link_type=link["link_type"],
            )
        )

    counts = {
        "work_roles": sum(
            1 for item in prepared["components"] if item["component_type"] == "work_role"
        ),
        "tasks": sum(
            1 for item in prepared["components"] if item["component_type"] == "task"
        ),
        "knowledge": sum(
            1 for item in prepared["components"] if item["component_type"] == "knowledge"
        ),
        "skills": sum(
            1 for item in prepared["components"] if item["component_type"] == "skill"
        ),
        "links": len(prepared["links"]),
    }
    meta = db.query(NiceFrameworkMeta).filter(NiceFrameworkMeta.id == 1).first()
    if meta is None:
        meta = NiceFrameworkMeta(id=1)
        db.add(meta)
    meta.version = prepared["version"]
    meta.source = source
    meta.source_url = source_url
    meta.fetched_at = datetime.now(timezone.utc)
    meta.counts = json.dumps(counts)
    db.commit()
    return {"version": prepared["version"], "source": source, "counts": counts}


def seed_if_empty(db: Session) -> Optional[dict]:
    if db.query(NiceComponent).count() > 0:
        return None
    try:
        return ingest_payload(
            db,
            _load_snapshot(),
            source="bundled",
            source_url=OFFICIAL_URL,
        )
    except IntegrityError:
        db.rollback()
        logger.info("NICE Framework seed already completed by another worker.")
        return None
    except Exception as exc:  # noqa: BLE001 - never block startup
        db.rollback()
        logger.warning("NICE Framework seed failed: %s", exc)
        return None


def refresh(db: Session, *, source: str = "official") -> dict:
    if source == "snapshot":
        return ingest_payload(
            db,
            _load_snapshot(),
            source="bundled",
            source_url=OFFICIAL_URL,
        )
    return ingest_payload(
        db,
        _download_official(),
        source="official",
        source_url=OFFICIAL_URL,
    )


def load_lab_mappings() -> dict:
    if not LAB_MAPPINGS_PATH.is_file():
        return {}
    try:
        return yaml.safe_load(LAB_MAPPINGS_PATH.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001 - a bad seed must not break startup
        logger.warning("Could not load NICE lab mappings: %s", exc)
        return {}


def _component_ids(db: Session, item: dict) -> list[int]:
    wanted = []
    for component_type, key in (
        ("work_role", "work_roles"),
        ("task", "tasks"),
        ("knowledge", "knowledge"),
        ("skill", "skills"),
    ):
        for code in item.get(key) or []:
            wanted.append((component_type, str(code)))
    if not wanted:
        return []
    rows = (
        db.query(NiceComponent)
        .filter(
            NiceComponent.is_active.is_(True),
            NiceComponent.component_type.in_([kind for kind, _ in wanted]),
            NiceComponent.code.in_([code for _, code in wanted]),
        )
        .all()
    )
    by_key = {(row.component_type, row.code): row.id for row in rows}
    return [
        by_key[key]
        for key in wanted
        if key in by_key
    ]


def seed_lab_mappings(db: Session, *, overwrite: bool = False) -> dict:
    """Load provisional repository mappings into labs that have none.

    Reviewed mappings are never replaced unless ``overwrite`` is set and the
    current status is still provisional.
    """
    payload = load_lab_mappings()
    mappings = payload.get("mappings") or {}
    labs = {lab.slug: lab for lab in db.query(Lab).all()}
    seeded = skipped = missing = components = 0
    for slug, item in mappings.items():
        lab = labs.get(slug)
        if lab is None:
            missing += 1
            continue
        meta = (
            db.query(LabNiceMetadata)
            .filter(LabNiceMetadata.lab_id == lab.id)
            .first()
        )
        existing = (
            db.query(func.count(LabNiceComponent.id))
            .filter(LabNiceComponent.lab_id == lab.id)
            .scalar()
            or 0
        )
        if existing and not overwrite:
            skipped += 1
            continue
        if existing and meta and meta.review_status == "reviewed":
            skipped += 1
            continue
        if existing and overwrite:
            db.query(LabNiceComponent).filter(
                LabNiceComponent.lab_id == lab.id
            ).delete(synchronize_session=False)
            db.flush()
        ids = _component_ids(db, item)
        if not ids:
            missing += 1
            continue
        for component_id in ids:
            db.add(
                LabNiceComponent(
                    lab_id=lab.id,
                    component_id=component_id,
                    created_by_id=None,
                )
            )
            components += 1
        if meta is None:
            meta = LabNiceMetadata(lab_id=lab.id, source=item.get("source") or "derived")
            db.add(meta)
        meta.review_status = item.get("review_status") or "provisional"
        meta.source = item.get("source") or "derived"
        meta.confidence = item.get("confidence")
        meta.policy_version = int(payload.get("policy_version") or 1)
        meta.reviewed_at = None
        meta.reviewed_by_id = None
        seeded += 1
    db.commit()
    return {
        "seeded": seeded,
        "skipped": skipped,
        "missing": missing,
        "components": components,
        "total_mappings": len(mappings),
    }


def coverage(db: Session, *, limit: int = 50) -> dict:
    total = int(db.query(func.count(Lab.id)).scalar() or 0)
    mapped = int(
        db.query(func.count(func.distinct(LabNiceComponent.lab_id))).scalar() or 0
    )
    status_rows = (
        db.query(LabNiceMetadata.review_status, func.count(LabNiceMetadata.lab_id))
        .group_by(LabNiceMetadata.review_status)
        .all()
    )
    status_counts = {status: int(count) for status, count in status_rows}
    queue_rows = (
        db.query(Lab, LabNiceMetadata)
        .outerjoin(LabNiceMetadata, LabNiceMetadata.lab_id == Lab.id)
        .filter(
            or_(
                LabNiceMetadata.lab_id.is_(None),
                LabNiceMetadata.review_status == "provisional",
            )
        )
        .order_by(Lab.name)
        .limit(max(1, min(limit, 200)))
        .all()
    )
    return {
        "framework": "NICE",
        "version": status(db).get("version"),
        "total_labs": total,
        "mapped_labs": mapped,
        "unmapped_labs": max(0, total - mapped),
        "coverage_percent": round((mapped / total) * 100, 1) if total else 0.0,
        "provisional": status_counts.get("provisional", 0),
        "reviewed": status_counts.get("reviewed", 0),
        "status_counts": status_counts,
        "review_queue": [
            {
                "lab_id": lab.id,
                "slug": lab.slug,
                "name": lab.name,
                "category": lab.category,
                "review_status": meta.review_status if meta else "unmapped",
                "source": meta.source if meta else None,
                "confidence": meta.confidence if meta else None,
            }
            for lab, meta in queue_rows
        ],
    }


def status(db: Session) -> dict:
    meta = db.query(NiceFrameworkMeta).filter(NiceFrameworkMeta.id == 1).first()
    counts = {}
    if meta and meta.counts:
        try:
            counts = json.loads(meta.counts)
        except ValueError:
            counts = {}
    return {
        "installed": meta is not None,
        "version": meta.version if meta else None,
        "source": meta.source if meta else None,
        "source_url": meta.source_url if meta else OFFICIAL_URL,
        "fetched_at": meta.fetched_at.isoformat() if meta and meta.fetched_at else None,
        "counts": counts,
        "expected_version": NICE_VERSION,
    }


def list_components(
    db: Session,
    *,
    component_type: str,
    query: str = "",
    work_role_code: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    if component_type not in COMPONENT_TYPES:
        raise ValueError(f"Unknown component type: {component_type}")
    rows = db.query(NiceComponent).filter(
        NiceComponent.component_type == component_type,
        NiceComponent.is_active.is_(True),
    )
    text = (query or "").strip()
    if text:
        pattern = f"%{text}%"
        rows = rows.filter(
            or_(
                NiceComponent.code.ilike(pattern),
                NiceComponent.name.ilike(pattern),
                NiceComponent.statement.ilike(pattern),
            )
        )
    if work_role_code and component_type != "work_role":
        role = (
            db.query(NiceComponent)
            .filter(
                NiceComponent.component_type == "work_role",
                NiceComponent.code == work_role_code,
                NiceComponent.is_active.is_(True),
            )
            .first()
        )
        if role is None:
            return {"total": 0, "items": []}
        rows = rows.join(
            NiceLink,
            NiceLink.target_id == NiceComponent.id,
        ).filter(
            NiceLink.source_id == role.id,
            NiceLink.link_type == LINK_TYPES[component_type],
        )
    total = rows.count()
    items = (
        rows.order_by(NiceComponent.code)
        .offset(max(0, offset))
        .limit(max(1, min(limit, 200)))
        .all()
    )
    return {
        "total": total,
        "items": [
            {
                "id": row.id,
                "type": row.component_type,
                "code": row.code,
                "name": row.name,
                "statement": row.statement,
                "category_code": row.category_code,
                "category_name": row.category_name,
                "version": row.version,
            }
            for row in items
        ],
    }


def lab_mappings(db: Session, lab_id: int) -> dict:
    rows = (
        db.query(NiceComponent)
        .join(LabNiceComponent, LabNiceComponent.component_id == NiceComponent.id)
        .filter(LabNiceComponent.lab_id == lab_id)
        .order_by(NiceComponent.component_type, NiceComponent.code)
        .all()
    )
    grouped = {component_type: [] for component_type in COMPONENT_TYPES}
    for row in rows:
        grouped[row.component_type].append(
            {
                "id": row.id,
                "code": row.code,
                "name": row.name,
                "statement": row.statement,
                "category_code": row.category_code,
                "category_name": row.category_name,
            }
        )
    return grouped


def _normalize_selections(selections: dict[str, Iterable[str]]) -> dict[str, list[str]]:
    normalized = {}
    for component_type in COMPONENT_TYPES:
        codes = [str(code).strip() for code in selections.get(component_type, []) if code]
        normalized[component_type] = list(dict.fromkeys(codes))
    return normalized


def validate_selections(db: Session, selections: dict[str, Iterable[str]]) -> list[str]:
    normalized = _normalize_selections(selections)
    all_codes = [code for codes in normalized.values() for code in codes]
    if not all_codes:
        return []
    rows = (
        db.query(NiceComponent)
        .filter(
            NiceComponent.code.in_(all_codes),
            NiceComponent.is_active.is_(True),
        )
        .all()
    )
    by_key = {(row.component_type, row.code) for row in rows}
    return [
        f"{component_type}:{code}"
        for component_type, codes in normalized.items()
        for code in codes
        if (component_type, code) not in by_key
    ]


def set_lab_mappings(
    db: Session,
    *,
    lab_id: int,
    selections: dict[str, Iterable[str]],
    created_by_id: Optional[int] = None,
    replace: bool = True,
) -> dict:
    normalized = _normalize_selections(selections)
    missing = validate_selections(db, normalized)
    if missing:
        raise ValueError("Unknown or inactive NICE components: " + ", ".join(missing))

    all_codes = [code for codes in normalized.values() for code in codes]
    rows = (
        db.query(NiceComponent)
        .filter(
            NiceComponent.code.in_(all_codes),
            NiceComponent.is_active.is_(True),
        )
        .all()
    ) if all_codes else []
    by_key = {(row.component_type, row.code): row for row in rows}

    if replace:
        db.query(LabNiceComponent).filter(LabNiceComponent.lab_id == lab_id).delete(
            synchronize_session=False
        )
        db.flush()
        existing = set()
    else:
        existing = {
            row.component_id
            for row in db.query(LabNiceComponent).filter(
                LabNiceComponent.lab_id == lab_id
            )
        }
    for component_type, codes in normalized.items():
        for code in codes:
            component = by_key[(component_type, code)]
            if component.id in existing:
                continue
            db.add(
                LabNiceComponent(
                    lab_id=lab_id,
                    component_id=component.id,
                    created_by_id=created_by_id,
                )
            )
    meta = (
        db.query(LabNiceMetadata)
        .filter(LabNiceMetadata.lab_id == lab_id)
        .first()
    )
    if meta is None:
        meta = LabNiceMetadata(lab_id=lab_id, source="manual")
        db.add(meta)
    meta.review_status = "reviewed"
    meta.source = "manual"
    meta.confidence = "reviewed"
    meta.policy_version = 1
    meta.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    meta.reviewed_by_id = created_by_id
    db.commit()
    return lab_mappings(db, lab_id)


def mark_lab_reviewed(
    db: Session,
    *,
    lab_id: int,
    reviewed_by_id: Optional[int] = None,
) -> dict:
    """Mark an existing provisional mapping as reviewed without changing it."""
    mapped = (
        db.query(LabNiceComponent)
        .filter(LabNiceComponent.lab_id == lab_id)
        .first()
    )
    if mapped is None:
        raise ValueError("Lab has no NICE mapping to review")
    meta = (
        db.query(LabNiceMetadata)
        .filter(LabNiceMetadata.lab_id == lab_id)
        .first()
    )
    if meta is None:
        meta = LabNiceMetadata(lab_id=lab_id, source="provisional")
        db.add(meta)
    meta.review_status = "reviewed"
    meta.confidence = "reviewed"
    meta.policy_version = meta.policy_version or 1
    meta.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    meta.reviewed_by_id = reviewed_by_id
    db.commit()
    return lab_mappings(db, lab_id)
