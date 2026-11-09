"""Versioned competency model for the eight-axis spider/radar report."""

from __future__ import annotations

import json
from typing import Optional

COMPETENCY_MODEL_VERSION = "2026.1"
COMPETENCY_MAPPING_VERSION = "2026.1"

AXES = (
    {"key": "network_systems", "label": "Network & Systems", "description": "Network foundations, hosts, services, and operating-system security."},
    {"key": "web_api", "label": "Web & API", "description": "Web application, API, and secure-development practice."},
    {"key": "identity_access", "label": "Identity & Access", "description": "Authentication, authorisation, credentials, and directory services."},
    {"key": "incident_forensics", "label": "Incident & Forensics", "description": "Detection, incident analysis, evidence handling, and digital forensics."},
    {"key": "osint", "label": "OSINT", "description": "Open-source research, footprinting, and intelligence analysis."},
    {"key": "malware", "label": "Malware Analysis", "description": "Static and dynamic analysis of malicious code and delivery."},
    {"key": "ot_ics", "label": "OT/ICS", "description": "Industrial control systems, protocols, and critical-infrastructure defence."},
    {"key": "ai_security", "label": "AI Security", "description": "Prompt injection, model misuse, and AI governance."},
)

AXIS_BY_KEY = {axis["key"]: axis for axis in AXES}
AXIS_KEYS = tuple(axis["key"] for axis in AXES)
TARGET_SCORE = 80.0
SCORE_WEIGHTS = {
    "assessment": 0.50,
    "independent": 0.25,
    "retained": 0.15,
    "instructor": 0.10,
}


def _bump(weights: dict[str, float], key: str, value: float) -> None:
    if value > 0:
        weights[key] = round(weights.get(key, 0.0) + value, 4)


def _normalise(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total <= 0:
        return {"network_systems": 1.0}
    return {key: round(value / total, 4) for key, value in weights.items() if value > 0}


def mapping_for_lab(lab) -> dict:
    track = ""
    level = 0
    if getattr(lab, "level", None) is not None:
        level = int(getattr(lab.level, "level_number", 0) or 0)
        if getattr(lab.level, "track", None) is not None:
            track = (lab.level.track.slug or lab.level.track.name or "").lower()
    category = (getattr(lab, "category", "") or "").lower()
    name = (getattr(lab, "name", "") or "").lower()
    weights: dict[str, float] = {}

    if track == "windows":
        if level <= 1:
            _bump(weights, "network_systems", 0.7); _bump(weights, "identity_access", 0.3)
        elif level in (2, 3):
            _bump(weights, "identity_access", 0.55); _bump(weights, "network_systems", 0.45)
        elif level == 6:
            _bump(weights, "identity_access", 0.5); _bump(weights, "web_api", 0.3); _bump(weights, "network_systems", 0.2)
        elif level == 7:
            _bump(weights, "identity_access", 0.8); _bump(weights, "network_systems", 0.2)
        elif level >= 8:
            _bump(weights, "identity_access", 0.6); _bump(weights, "network_systems", 0.4)
        else:
            _bump(weights, "identity_access", 0.5); _bump(weights, "network_systems", 0.5)
    elif track == "linux":
        if level >= 5:
            _bump(weights, "incident_forensics", 0.7); _bump(weights, "network_systems", 0.3)
        elif level >= 3:
            _bump(weights, "identity_access", 0.6); _bump(weights, "network_systems", 0.4)
        else:
            _bump(weights, "network_systems", 0.7); _bump(weights, "identity_access", 0.3)
    elif track == "web":
        _bump(weights, "web_api", 1.0)
    elif track == "software-security":
        _bump(weights, "web_api", 0.7); _bump(weights, "network_systems", 0.3)
    elif track == "forensics":
        _bump(weights, "incident_forensics", 0.8); _bump(weights, "malware", 0.2)
    elif track == "osint":
        _bump(weights, "osint", 1.0)
    elif track == "malware":
        _bump(weights, "malware", 1.0)
    elif track == "ot":
        _bump(weights, "ot_ics", 1.0)
    elif track == "ai":
        _bump(weights, "ai_security", 1.0)
    elif track == "high-school":
        if level >= 12:
            _bump(weights, "web_api", 0.4); _bump(weights, "identity_access", 0.2); _bump(weights, "network_systems", 0.2); _bump(weights, "incident_forensics", 0.2)
        elif level >= 11:
            _bump(weights, "incident_forensics", 0.6); _bump(weights, "network_systems", 0.2); _bump(weights, "identity_access", 0.2)
        else:
            _bump(weights, "network_systems", 0.5); _bump(weights, "identity_access", 0.2); _bump(weights, "web_api", 0.2); _bump(weights, "incident_forensics", 0.1)
    elif "forensic" in category or "incident" in category:
        _bump(weights, "incident_forensics", 0.8); _bump(weights, "network_systems", 0.2)
    elif "web" in category or "api" in category:
        _bump(weights, "web_api", 1.0)
    elif "osint" in category:
        _bump(weights, "osint", 1.0)
    elif "malware" in category:
        _bump(weights, "malware", 1.0)
    elif "ot" in category or "ics" in category:
        _bump(weights, "ot_ics", 1.0)
    elif "ai" in category or "prompt" in name:
        _bump(weights, "ai_security", 1.0)
    elif "identity" in category or "credential" in category:
        _bump(weights, "identity_access", 0.7); _bump(weights, "network_systems", 0.3)
    else:
        _bump(weights, "network_systems", 1.0)

    return {
        "model_version": COMPETENCY_MODEL_VERSION,
        "mapping_version": COMPETENCY_MAPPING_VERSION,
        "difficulty": getattr(lab, "difficulty", None),
        "weights": _normalise(weights),
    }


def parse_mapping(raw: Optional[str], lab) -> dict:
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and parsed.get("weights"):
                return parsed
        except (TypeError, ValueError):
            pass
    return mapping_for_lab(lab)


def backfill_completion_mappings(db, batch_size: int = 500) -> int:
    from sqlalchemy.orm import joinedload
    from app.models import Lab, LabCompletion, Level

    rows = (
        db.query(LabCompletion)
        .options(joinedload(LabCompletion.lab).joinedload(Lab.level).joinedload(Level.track))
        .filter(LabCompletion.competency_mapping.is_(None))
        .limit(batch_size)
        .all()
    )
    for row in rows:
        if row.lab is None:
            continue
        snapshot = mapping_for_lab(row.lab)
        row.competency_model_version = f"{COMPETENCY_MODEL_VERSION}-backfill"
        row.competency_mapping = json.dumps(snapshot, sort_keys=True)
        row.lab_difficulty_snapshot = row.lab.difficulty
    if rows:
        db.commit()
    return len(rows)
