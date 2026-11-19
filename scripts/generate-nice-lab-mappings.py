#!/usr/bin/env python3
"""Generate provisional NICE v2.2.0 mappings for every repository lab.

The mapping is deliberately conservative and clearly labelled provisional:
- Work roles come from the lab's competency keys and category.
- Tasks, knowledge, and skills are selected only from components linked to
  those work roles, with keyword overlap against the lab text.
- A reviewer must confirm or replace the mapping before it is treated as
  curriculum evidence.

The output is read by the backend seeder. It only fills labs that have no
mapping yet; reviewed mappings are never overwritten.

Usage:
    python scripts/generate-nice-lab-mappings.py
    python scripts/generate-nice-lab-mappings.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "platform" / "backend"
sys.path.insert(0, str(BACKEND))

from app.services import nice_framework

LABS = ROOT / "platform" / "labs"
OUTPUT = BACKEND / "app" / "data" / "nice" / "lab-mappings.yaml"

COMPETENCY_ROLES = {
    "network_systems": ["PD-WRL-001", "PD-WRL-007", "IO-WRL-004"],
    "identity_access": ["PD-WRL-001", "IO-WRL-005", "IO-WRL-006"],
    "incident_forensics": ["PD-WRL-003", "PD-WRL-002", "IN-WRL-001"],
    "web_api": ["DD-WRL-005", "PD-WRL-007", "DD-WRL-003"],
    "osint": ["PD-WRL-006", "IN-WRL-001", "PD-WRL-003"],
    "malware": ["PD-WRL-006", "PD-WRL-002", "PD-WRL-001"],
    "ot_ics": ["DD-WRL-009", "PD-WRL-004", "PD-WRL-001"],
    "ai_security": ["DD-WRL-003", "DD-WRL-005", "PD-WRL-006"],
}

CATEGORY_ROLES = {
    "web": ["DD-WRL-005", "PD-WRL-007"],
    "forensics": ["PD-WRL-002", "PD-WRL-003"],
    "ot": ["DD-WRL-009"],
    "ai": ["DD-WRL-003", "DD-WRL-005"],
    "osint": ["PD-WRL-006"],
    "reconnaissance": ["PD-WRL-007", "IO-WRL-004"],
    "enumeration": ["PD-WRL-007", "IO-WRL-004"],
    "network": ["IO-WRL-004", "PD-WRL-004"],
    "network-analysis": ["PD-WRL-001", "IO-WRL-004"],
    "credential-attacks": ["PD-WRL-001", "IO-WRL-005"],
    "authentication": ["PD-WRL-001", "IO-WRL-005"],
    "privilege-escalation": ["PD-WRL-001", "PD-WRL-007"],
    "post-exploitation": ["PD-WRL-001", "PD-WRL-003"],
    "exploitation": ["PD-WRL-007", "DD-WRL-005"],
    "crypto": ["PD-WRL-001", "DD-WRL-003"],
    "assessment": ["PD-WRL-001", "PD-WRL-007"],
}

STOP = {
    "the", "and", "for", "with", "from", "this", "that", "into", "your",
    "you", "using", "use", "lab", "exercise", "identify", "explain",
    "describe", "perform", "analyze", "analyse", "demonstrate", "submit",
    "correct", "flag", "step", "test", "automated", "basic", "introduction",
}


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]{4,}", (text or "").lower())
        if token not in STOP
    }


def _lab_text(data: dict) -> str:
    parts = [
        str(data.get("title") or ""),
        str(data.get("category") or ""),
        str(data.get("description") or ""),
        " ".join(str(item) for item in data.get("learning_outcomes") or []),
        " ".join(str(item) for item in data.get("mapped_skills") or []),
        " ".join(str(item) for item in data.get("tools") or []),
    ]
    return " ".join(parts)


def _prepare_nice() -> dict:
    prepared = nice_framework._prepare(nice_framework._load_snapshot())
    components = {
        (item["component_type"], item["code"]): item
        for item in prepared["components"]
    }
    links: dict[str, dict[str, list[str]]] = {}
    for link in prepared["links"]:
        role = link["source_code"]
        bucket = links.setdefault(
            role, {"task": [], "knowledge": [], "skill": []}
        )
        bucket[link["target_type"]].append(link["target_code"])
    return {"components": components, "links": links}


def _pick_linked(
    codes: list[str],
    components: dict,
    lab_tokens: set[str],
    limit: int = 3,
) -> list[str]:
    scored = []
    for code in dict.fromkeys(codes):
        item = components.get(("task", code)) or components.get(("knowledge", code)) or components.get(("skill", code))
        if not item:
            continue
        text = f"{item.get('name') or ''} {item.get('statement') or ''}"
        score = len(lab_tokens & _tokens(text))
        scored.append((score, code))
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    selected = [code for score, code in scored if score > 0][:limit]
    if not selected:
        selected = [code for _, code in scored[: min(2, len(scored))]]
    return selected


def build_mapping(data: dict, nice: dict) -> dict:
    components = nice["components"]
    links = nice["links"]
    roles = []
    for skill in data.get("mapped_skills") or []:
        roles.extend(COMPETENCY_ROLES.get(str(skill), []))
    roles.extend(CATEGORY_ROLES.get(str(data.get("category") or ""), []))
    roles = list(dict.fromkeys(role for role in roles if role in links))[:3]
    if not roles:
        roles = ["PD-WRL-001"]

    lab_tokens = _tokens(_lab_text(data))
    tasks, knowledge, skills = [], [], []
    for role in roles:
        bucket = links.get(role, {})
        tasks.extend(bucket.get("task", []))
        knowledge.extend(bucket.get("knowledge", []))
        skills.extend(bucket.get("skill", []))

    selected_tasks = _pick_linked(tasks, components, lab_tokens)
    selected_knowledge = _pick_linked(knowledge, components, lab_tokens)
    selected_skills = _pick_linked(skills, components, lab_tokens)
    overlap = len(lab_tokens & _tokens(
        " ".join(
            f"{components.get(('task', code), {}).get('statement', '')} "
            f"{components.get(('knowledge', code), {}).get('statement', '')} "
            f"{components.get(('skill', code), {}).get('statement', '')}"
            for code in selected_tasks + selected_knowledge + selected_skills
        )
    ))
    confidence = "medium" if overlap >= 3 else "low"

    return {
        "review_status": "provisional",
        "source": "derived_from_competency_and_category",
        "reviewed_at": None,
        "reviewed_by": None,
        "confidence": confidence,
        "work_roles": roles,
        "tasks": selected_tasks,
        "knowledge": selected_knowledge,
        "skills": selected_skills,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    nice = _prepare_nice()
    mappings = {}
    for path in sorted(LABS.rglob("lab.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        slug = path.parent.name
        mappings[slug] = build_mapping(data, nice)

    payload = {
        "framework": "NICE",
        "version": nice_framework.NICE_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "policy_version": 1,
        "mappings": mappings,
    }
    text = yaml.safe_dump(payload, sort_keys=True, allow_unicode=True)

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        # Generated timestamp changes every run; compare the mapping body only.
        current_body = current.split("generated_at:", 1)[-1].split("\n", 1)[-1]
        new_body = text.split("generated_at:", 1)[-1].split("\n", 1)[-1]
        if current_body != new_body:
            print("error: lab-mappings.yaml is out of date; regenerate it.")
            return 1
        print(f"OK: {len(mappings)} lab mappings are current.")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8")
    provisional = sum(1 for item in mappings.values() if item["review_status"] == "provisional")
    print(f"wrote {OUTPUT} ({len(mappings)} labs, {provisional} provisional)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
