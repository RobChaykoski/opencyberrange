"""Cyber DNA bounded-context service.

This module reads and writes only ``dna_*`` tables. It accepts
``ActivityCompleted`` events from the exercise platform and never imports the
exercise models or queries exercise tables. Career affinity is deliberately
gated until the learner has enough evidence.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.cyber_dna.events import ActivityCompleted
from app.cyber_dna.models import DnaEvidenceRecord, DnaSnapshot
from app.cyber_dna.taxonomy import (
    competency_index,
    proficiency_scale,
)

logger = logging.getLogger(__name__)

EVIDENCE_FORMULA_VERSION = "evidence-2026.1"
BEHAVIOR_VERSION = "behavior-2026.1"
INTEREST_VERSION = "interest-2026.1"
AFFINITY_VERSION = "affinity-2026.1"
SCHEMA_VERSION = "2026.1"

DIFFICULTY_WEIGHT = {
    "beginner": 1.0,
    "intermediate": 1.5,
    "advanced": 2.0,
    "expert": 2.5,
}
SCORE_SCALE = 4.0
MAX_SCORE = 99
WINDOW_DAYS = 30

AFFINITY_MIN_LABS = 30
AFFINITY_MIN_DOMAINS = 3
AFFINITY_MIN_OBSERVATIONS = 100

BEHAVIOR_CONFIDENCE = ((15, "high"), (8, "medium"), (3, "low"))
BANDS = (
    (0, 24, "awareness"),
    (25, 44, "foundational"),
    (45, 64, "practitioner"),
    (65, 84, "specialist"),
    (85, 99, "lead"),
)

DEFAULT_BEHAVIOR_WEIGHTS = {
    "defensive": {"consistency": 0.40, "investigation": 0.40, "independence": 0.20},
    "offensive": {"persistence": 0.40, "independence": 0.40, "speed": 0.20},
    "investigative": {
        "investigation": 0.50,
        "persistence": 0.30,
        "independence": 0.20,
    },
    "cloud": {"consistency": 0.40, "independence": 0.30, "persistence": 0.30},
    "ot": {"consistency": 0.40, "persistence": 0.30, "investigation": 0.30},
    "ai": {"investigation": 0.40, "persistence": 0.30, "independence": 0.30},
    "identity": {"independence": 0.40, "consistency": 0.30, "investigation": 0.30},
    "intel": {"investigation": 0.50, "consistency": 0.30, "independence": 0.20},
    "leadership": {"consistency": 0.50, "independence": 0.30, "persistence": 0.20},
}

CAREER_FILE = Path(__file__).resolve().parent.parent / "data" / "curriculum-roles.yaml"
_career_cache: dict | None = None

SNAPSHOT_KINDS = ("behavior_profile", "interest_profile", "career_affinity")
VOLATILE_KEYS = {"generated_at", "recorded_at"}


def _naive_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _as_naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=None) if value.tzinfo is not None else value


def _recency(days: int | None) -> float:
    if days is None or days <= 14:
        return 1.0
    if days <= 30:
        return 0.99
    if days <= 60:
        return 0.97
    if days <= 90:
        return 0.94
    return 0.90


def _confidence(sample: int) -> str | None:
    for minimum, label in BEHAVIOR_CONFIDENCE:
        if sample >= minimum:
            return label
    return None


def _iso_week(value: datetime) -> tuple[int, int]:
    year, week, _ = value.isocalendar()
    return (year, week)


def _band(score: int) -> str:
    for lower, upper, label in BANDS:
        if lower <= score <= upper:
            return label
    return "awareness"


def load_career_profiles() -> dict:
    global _career_cache
    if _career_cache is None:
        with CAREER_FILE.open("r", encoding="utf-8") as handle:
            _career_cache = yaml.safe_load(handle) or {}
    return _career_cache


def ingest_activity(db: Session, event: ActivityCompleted) -> int:
    """Append evidence for one event. Idempotent by event and competency."""
    taxonomy = competency_index()
    difficulty = (event.difficulty or "beginner").strip().lower()
    difficulty_weight = DIFFICULTY_WEIGHT.get(difficulty, 1.0)
    attempts = max(1, int(event.attempts or 1))
    hints = max(0, int(event.hints_used or 0))
    independence = 1.0 + (0.35 if hints == 0 else 0.0) + (0.20 if attempts <= 1 else 0.0)
    occurred_at = _as_naive(event.occurred_at) or _naive_utc_now()

    existing = {
        row[0]
        for row in db.query(DnaEvidenceRecord.competency_id)
        .filter(DnaEvidenceRecord.event_id == event.event_id)
        .all()
    }
    created = 0
    for competency_id, weight in event.competency_weights.items():
        if competency_id in existing:
            continue
        competency = taxonomy.get(competency_id)
        if competency is None:
            logger.warning(
                "Cyber DNA event %s references unknown competency %s",
                event.event_id,
                competency_id,
            )
            continue
        db.add(
            DnaEvidenceRecord(
                learner_id=event.learner_id,
                event_id=event.event_id,
                activity_id=event.activity_id,
                activity_category=(event.activity_category or "general").strip().lower(),
                competency_id=competency_id,
                domain_id=competency["domain"],
                mapping_weight=float(weight),
                score_contribution=difficulty_weight * float(weight) * independence,
                difficulty=difficulty,
                attempts=attempts,
                hints_used=hints,
                duration_minutes=(
                    max(1, int(event.duration_minutes))
                    if event.duration_minutes
                    else None
                ),
                prior_failed_attempts=max(0, int(event.prior_failed_attempts or 0)),
                voluntary=bool(event.voluntary),
                source_version=event.source_version,
                occurred_at=occurred_at,
            )
        )
        created += 1
    if not created:
        return 0
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return 0
    return created


def _rows(db: Session, learner_id: int, since: datetime | None = None):
    query = db.query(DnaEvidenceRecord).filter(
        DnaEvidenceRecord.learner_id == learner_id
    )
    if since is not None:
        query = query.filter(DnaEvidenceRecord.occurred_at >= since)
    return query.order_by(DnaEvidenceRecord.occurred_at.desc()).all()


def _events(rows: list[DnaEvidenceRecord]) -> list[DnaEvidenceRecord]:
    """One representative row per event, in occurrence order."""
    seen: dict[str, DnaEvidenceRecord] = {}
    for row in rows:
        if row.event_id not in seen:
            seen[row.event_id] = row
    return sorted(seen.values(), key=lambda item: item.occurred_at, reverse=True)


def competency_scores(db: Session, learner_id: int) -> list[dict]:
    now = _naive_utc_now()
    rows = _rows(db, learner_id)
    buckets: dict[str, dict] = defaultdict(
        lambda: {"weight": 0.0, "count": 0, "latest": None}
    )
    for row in rows:
        occurred = _as_naive(row.occurred_at)
        days = max(0, (now - occurred).days) if occurred else None
        bucket = buckets[row.competency_id]
        bucket["weight"] += float(row.score_contribution or 0.0) * _recency(days)
        bucket["count"] += 1
        if occurred and (bucket["latest"] is None or occurred > bucket["latest"]):
            bucket["latest"] = occurred

    taxonomy = competency_index()
    scores = []
    for competency_id, bucket in buckets.items():
        competency = taxonomy.get(competency_id)
        if competency is None:
            continue
        raw = 100.0 * (1.0 - math.exp(-bucket["weight"] / SCORE_SCALE))
        score = max(0, min(MAX_SCORE, round(raw)))
        scores.append(
            {
                "competency_id": competency_id,
                "competency_name": competency["name"],
                "domain_id": competency["domain"],
                "domain_label": competency["domain_label"],
                "category_id": competency["category"],
                "category_label": competency["category_label"],
                "score": score,
                "band": _band(score),
                "evidence_count": bucket["count"],
                "last_practised_at": (
                    bucket["latest"].isoformat() + "Z" if bucket["latest"] else None
                ),
                "formula_version": EVIDENCE_FORMULA_VERSION,
            }
        )
    return sorted(scores, key=lambda item: (-item["score"], item["competency_id"]))


def evidence_items(
    db: Session,
    learner_id: int,
    competency_id: str | None = None,
    domain_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    query = db.query(DnaEvidenceRecord).filter(
        DnaEvidenceRecord.learner_id == learner_id
    )
    if competency_id:
        query = query.filter(DnaEvidenceRecord.competency_id == competency_id)
    if domain_id:
        query = query.filter(DnaEvidenceRecord.domain_id == domain_id)
    total = query.count()
    rows = (
        query.order_by(DnaEvidenceRecord.occurred_at.desc())
        .offset(max(0, offset))
        .limit(max(1, min(limit, 200)))
        .all()
    )
    taxonomy = competency_index()
    items = []
    for row in rows:
        competency = taxonomy.get(row.competency_id) or {}
        items.append(
            {
                "evidence_id": row.id,
                "event_id": row.event_id,
                "competency_id": row.competency_id,
                "competency_name": competency.get("name", row.competency_id),
                "domain_id": row.domain_id,
                "activity_id": row.activity_id,
                "activity_category": row.activity_category,
                "score_contribution": round(float(row.score_contribution or 0.0), 3),
                "mapping_weight": round(float(row.mapping_weight or 0.0), 4),
                "attempts": row.attempts,
                "hints_used": row.hints_used,
                "duration_minutes": row.duration_minutes,
                "practised_at": (
                    _as_naive(row.occurred_at).isoformat() + "Z"
                    if row.occurred_at
                    else None
                ),
                "source": "live",
            }
        )
    return items, total


def _signal(value: float | None, sample: int) -> dict:
    return {
        "value": None if value is None else round(value, 1),
        "sample_size": sample,
        "confidence": _confidence(sample),
    }


def build_behavior(db: Session, learner_id: int) -> dict:
    now = _naive_utc_now()
    cutoff = now - timedelta(days=WINDOW_DAYS)
    events = _events(_rows(db, learner_id, since=cutoff))
    sample = len(events)
    weights = {
        "persistence": {"attempt_depth": 0.6, "recovery": 0.4},
        "independence": {"hint_free": 0.6, "hint_load": 0.4},
        "speed": {"cap_low": 0.5, "cap_high": 1.5},
        "consistency": {"target_weeks": 4},
        "investigation": {"breadth": 0.6, "attempt_depth": 0.4},
        "note": "Investigation is an exploration proxy, not telemetry.",
    }
    if sample == 0:
        return {
            "version": BEHAVIOR_VERSION,
            "window_days": WINDOW_DAYS,
            "signals": {
                name: _signal(None, 0)
                for name in (
                    "persistence",
                    "independence",
                    "speed",
                    "consistency",
                    "investigation",
                )
            },
            "weights": weights,
        }

    attempts = [max(1, int(row.attempts or 1)) for row in events]
    mean_attempts = sum(attempts) / sample
    attempt_depth = min(1.0, max(0.0, (mean_attempts - 1.0) / 6.0))
    recovery = (
        sum(1 for row in events if int(row.prior_failed_attempts or 0) >= 5) / sample
    )
    persistence = 100.0 * (0.6 * attempt_depth + 0.4 * recovery)

    hints = [max(0, int(row.hints_used or 0)) for row in events]
    hint_free_rate = sum(1 for value in hints if value == 0) / sample
    hints_per_completion = sum(hints) / sample
    hint_load = min(1.0, hints_per_completion / 5.0)
    independence = 100.0 * (0.6 * hint_free_rate + 0.4 * (1.0 - hint_load))

    timed = [
        (row.activity_category, row.difficulty or "beginner", int(row.duration_minutes))
        for row in events
        if row.duration_minutes
    ]
    speed = None
    if len(timed) >= 5:
        groups: dict[tuple[str, str], list[int]] = defaultdict(list)
        for category, difficulty, minutes in timed:
            groups[(category, difficulty)].append(minutes)
        global_medians: dict[str, float] = {}
        for difficulty in {item[1] for item in timed}:
            values = sorted(item[2] for item in timed if item[1] == difficulty)
            global_medians[difficulty] = values[len(values) // 2]
        ratios = []
        for category, difficulty, minutes in timed:
            values = sorted(groups[(category, difficulty)])
            median = values[len(values) // 2]
            if len(values) < 2:
                median = global_medians[difficulty]
            ratios.append(min(1.5, max(0.5, median / minutes)))
        speed = 100.0 * (sum(ratios) / len(ratios) - 0.5)

    weeks = {_iso_week(_as_naive(row.occurred_at)) for row in events}
    active_weeks = len(weeks)
    consistency = 100.0 * min(1.0, active_weeks / 4.0)

    categories = {row.activity_category for row in events}
    breadth = min(1.0, len(categories) / 6.0)
    investigation = 100.0 * (0.6 * breadth + 0.4 * attempt_depth)

    return {
        "version": BEHAVIOR_VERSION,
        "window_days": WINDOW_DAYS,
        "signals": {
            "persistence": _signal(persistence, sample),
            "independence": _signal(independence, sample),
            "speed": _signal(speed, len(timed)),
            "consistency": _signal(consistency, active_weeks),
            "investigation": {
                **_signal(investigation, sample),
                "kind": "proxy",
                "note": (
                    "Exploration breadth from distinct categories and attempt "
                    "depth; not logs, packets, or commands."
                ),
            },
        },
        "weights": weights,
    }


def build_interest(db: Session, learner_id: int) -> dict:
    now = _naive_utc_now()
    events = [row for row in _events(_rows(db, learner_id)) if row.voluntary]
    weighted: dict[str, float] = defaultdict(float)
    for row in events:
        occurred = _as_naive(row.occurred_at)
        days = max(0, (now - occurred).days) if occurred else None
        weighted[row.activity_category] += _recency(days)
    if len(events) < 5 or len(weighted) < 2:
        return {
            "version": INTEREST_VERSION,
            "available": False,
            "voluntary_completions": len(events),
            "vector": {},
            "basis": "voluntary activity categories, recency weighted",
            "note": "Optional answers are not stored in v3.",
        }
    peak = max(weighted.values()) or 1.0
    return {
        "version": INTEREST_VERSION,
        "available": True,
        "voluntary_completions": len(events),
        "vector": {
            category: round(value / peak * 100, 1)
            for category, value in sorted(weighted.items(), key=lambda item: -item[1])
        },
        "basis": "voluntary activity categories, recency weighted",
        "note": "Optional answers are not stored in v3.",
    }


def affinity_gate(db: Session, learner_id: int) -> dict:
    labs = (
        db.query(func.count(func.distinct(DnaEvidenceRecord.activity_id)))
        .filter(DnaEvidenceRecord.learner_id == learner_id)
        .scalar()
        or 0
    )
    domains = (
        db.query(func.count(func.distinct(DnaEvidenceRecord.domain_id)))
        .filter(DnaEvidenceRecord.learner_id == learner_id)
        .scalar()
        or 0
    )
    observations = (
        db.query(func.count(DnaEvidenceRecord.id))
        .filter(DnaEvidenceRecord.learner_id == learner_id)
        .scalar()
        or 0
    )
    return {
        "available": (
            labs >= AFFINITY_MIN_LABS
            and domains >= AFFINITY_MIN_DOMAINS
            and observations >= AFFINITY_MIN_OBSERVATIONS
        ),
        "labs": {"have": int(labs), "need": AFFINITY_MIN_LABS},
        "domains": {"have": int(domains), "need": AFFINITY_MIN_DOMAINS},
        "observations": {"have": int(observations), "need": AFFINITY_MIN_OBSERVATIONS},
    }


def _behavior_weights(pathway: dict) -> dict:
    explicit = pathway.get("behavior_weights")
    if isinstance(explicit, dict) and explicit:
        return {key: float(value) for key, value in explicit.items()}
    family = str(pathway.get("family") or "defensive").lower()
    return dict(DEFAULT_BEHAVIOR_WEIGHTS.get(family, DEFAULT_BEHAVIOR_WEIGHTS["defensive"]))


def _interest_fit(pathway: dict, interest: dict) -> float | None:
    if not interest.get("available"):
        return None
    categories = {
        str(item).strip().lower()
        for item in (pathway.get("categories") or [])
        if item
    }
    if not categories:
        return None
    values = [float(interest["vector"].get(category, 0.0)) for category in categories]
    return sum(values) / len(values) / 100.0


def _affinity_weights(components: dict) -> dict:
    base = {"coverage": 0.50, "depth": 0.20, "behavior": 0.15, "interest": 0.15}
    present = {key: value for key, value in base.items() if components.get(key) is not None}
    total = sum(present.values()) or 1.0
    return {key: value / total for key, value in present.items()}


def build_affinity(
    db: Session,
    learner_id: int,
    pathway_id: str | None = None,
) -> dict:
    gate = affinity_gate(db, learner_id)
    if not gate["available"]:
        return {
            "version": AFFINITY_VERSION,
            "available": False,
            "gate": gate,
            "pathways": [],
            "disclaimer": (
                "Career affinity unlocks at 30 labs, 3 domains, and 100 "
                "competency observations. It is descriptive, not a probability."
            ),
        }

    scores = {item["competency_id"]: item for item in competency_scores(db, learner_id)}
    behavior = build_behavior(db, learner_id)
    interest = build_interest(db, learner_id)
    signals = {
        key: value.get("value")
        for key, value in (behavior.get("signals") or {}).items()
        if value.get("value") is not None
    }
    pathways = load_career_profiles().get("pathways", [])
    if pathway_id:
        pathways = [item for item in pathways if item.get("id") == pathway_id]
        if not pathways:
            raise ValueError(f"unknown pathway: {pathway_id}")

    results = []
    for pathway in pathways:
        critical = list(dict.fromkeys(pathway.get("critical_competencies") or []))
        if not critical:
            continue
        weight = 1.0 / len(critical)
        coverage = 0.0
        depth = 0.0
        evidenced = 0
        for competency_id in critical:
            score = scores.get(competency_id, {}).get("score", 0)
            if score > 0:
                evidenced += 1
            if score >= 60:
                coverage += weight
            depth += weight * min(score / 100.0, 1.0)
        components = {
            "coverage": coverage,
            "depth": depth,
            "behavior": None,
            "interest": _interest_fit(pathway, interest),
        }
        behavior_weights = _behavior_weights(pathway)
        available = {key: value for key, value in behavior_weights.items() if key in signals}
        if available:
            total_weight = sum(available.values()) or 1.0
            components["behavior"] = sum(
                signals[key] / 100.0 * value for key, value in available.items()
            ) / total_weight
        weights = _affinity_weights(components)
        affinity = 100.0 * sum(
            components[key] * value for key, value in weights.items()
        )
        strongest = [
            scores[item]["competency_name"]
            for item in sorted(
                (cid for cid in critical if cid in scores),
                key=lambda cid: -scores[cid]["score"],
            )[:3]
        ]
        gaps = [
            scores.get(cid, {}).get("competency_name", cid)
            for cid in critical
            if scores.get(cid, {}).get("score", 0) < 60
        ][:3]
        why = [
            f"{evidenced} of {len(critical)} critical competencies have evidence.",
            (
                f"{round(coverage * 100)}% of critical competencies are at "
                "practitioner level or above."
            ),
        ]
        if components["behavior"] is not None:
            why.append("Behavior signals are included where the sample allows.")
        if components["interest"] is not None:
            why.append("Voluntary interest is included for this pathway.")
        results.append(
            {
                "pathway_id": pathway.get("id"),
                "title": pathway.get("title"),
                "family": pathway.get("family"),
                "affinity": round(affinity, 1),
                "confidence_band": _confidence(evidenced) or "low",
                "evidence_count": evidenced,
                "components": {
                    key: (None if value is None else round(value, 3))
                    for key, value in components.items()
                },
                "strongest_competencies": strongest,
                "gaps": gaps,
                "why": why,
                "formula_version": AFFINITY_VERSION,
                "weights": weights,
            }
        )
    return {
        "version": AFFINITY_VERSION,
        "available": True,
        "gate": gate,
        "pathways": sorted(
            results,
            key=lambda item: (-item["affinity"], item["title"] or ""),
        ),
        "disclaimer": (
            "Affinity is a descriptive practice signal with an evidence band. "
            "It is not a probability, a rank, or a hiring prediction."
        ),
    }


def build_dna(db: Session, learner_id: int) -> dict:
    scores = competency_scores(db, learner_id)
    return {
        "version": SCHEMA_VERSION,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _naive_utc_now().isoformat() + "Z",
        "evidence_summary": {
            "competencies_with_evidence": len(scores),
            "evidence_items": sum(item["evidence_count"] for item in scores),
        },
        "competencies": scores,
        "behavior": build_behavior(db, learner_id),
        "interest": build_interest(db, learner_id),
        "affinity": build_affinity(db, learner_id),
        "proficiency_scale": proficiency_scale(),
        "disclaimer": (
            "Affinity is a descriptive practice signal with an evidence band. "
            "It is not a probability, a rank, a grade, or a hiring prediction."
        ),
    }


def _canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _stable_content(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if key not in VOLATILE_KEYS}


def _content_hash(payload: dict) -> str:
    return hashlib.sha256(_canonical(_stable_content(payload)).encode("utf-8")).hexdigest()


def record_snapshot(
    db: Session,
    learner_id: int,
    kind: str,
    payload: dict,
) -> tuple[DnaSnapshot, bool]:
    if kind not in SNAPSHOT_KINDS:
        raise ValueError(f"unknown snapshot kind: {kind}")
    body = _canonical(payload)
    digest = _content_hash(payload)
    existing = (
        db.query(DnaSnapshot)
        .filter(
            DnaSnapshot.learner_id == learner_id,
            DnaSnapshot.kind == kind,
            DnaSnapshot.content_sha256 == digest,
        )
        .first()
    )
    if existing is not None:
        return existing, False
    row = DnaSnapshot(
        learner_id=learner_id,
        kind=kind,
        schema_version=SCHEMA_VERSION,
        formula_version=payload.get("version") or payload.get("formula_version"),
        weights=_canonical(payload.get("weights") or {"formula": payload.get("version")}),
        payload=body,
        content_sha256=digest,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(DnaSnapshot)
            .filter(
                DnaSnapshot.learner_id == learner_id,
                DnaSnapshot.kind == kind,
                DnaSnapshot.content_sha256 == digest,
            )
            .first()
        )
        if existing is None:
            raise
        return existing, False
    db.refresh(row)
    return row, True


def list_snapshots(
    db: Session,
    learner_id: int,
    kind: str | None = None,
    limit: int = 20,
) -> list[DnaSnapshot]:
    query = db.query(DnaSnapshot).filter(DnaSnapshot.learner_id == learner_id)
    if kind:
        query = query.filter(DnaSnapshot.kind == kind)
    return (
        query.order_by(DnaSnapshot.created_at.desc(), DnaSnapshot.id.desc())
        .limit(max(1, min(limit, 100)))
        .all()
    )


def get_snapshot(db: Session, learner_id: int, snapshot_id: int) -> DnaSnapshot | None:
    return (
        db.query(DnaSnapshot)
        .filter(DnaSnapshot.id == snapshot_id, DnaSnapshot.learner_id == learner_id)
        .first()
    )


def snapshot_meta(row: DnaSnapshot) -> dict:
    return {
        "snapshot_id": row.id,
        "kind": row.kind,
        "schema_version": row.schema_version,
        "formula_version": row.formula_version,
        "content_sha256": row.content_sha256,
        "created_at": row.created_at.isoformat() + "Z" if row.created_at else None,
        "weights": json.loads(row.weights),
    }


def snapshot_payload(row: DnaSnapshot) -> dict:
    return json.loads(row.payload)


def erase_learner(db: Session, learner_id: int) -> int:
    """Delete every DNA row for a learner. Caller owns the transaction."""
    deleted = (
        db.query(DnaEvidenceRecord)
        .filter(DnaEvidenceRecord.learner_id == learner_id)
        .delete(synchronize_session=False)
    )
    db.query(DnaSnapshot).filter(DnaSnapshot.learner_id == learner_id).delete(
        synchronize_session=False
    )
    return int(deleted or 0)
