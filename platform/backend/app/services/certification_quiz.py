"""Certification-aligned question banks.

The bank is admin-curated and never sent to learners with answers attached. The
exercise quiz engine samples three questions from the pathway that best matches
the exercise's track and topic, so the check feels like a short certification
drill rather than a generic quiz.

Questions are original practice items written to published objectives. They are
not copied exam questions and are not a certification exam.
"""

from __future__ import annotations

import random
import re
from pathlib import Path
from urllib.parse import urlparse

import yaml

from app.models import Lab

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BANKS_FILE = DATA_DIR / "certification-question-banks.yaml"
CERT_PREFIX = "cert:"
SAMPLE_SIZE = 3

_banks_cache: dict | None = None


def load_banks() -> dict:
    global _banks_cache
    if _banks_cache is None:
        with BANKS_FILE.open("r", encoding="utf-8") as handle:
            _banks_cache = yaml.safe_load(handle) or {}
    return _banks_cache


def reset_cache() -> None:
    global _banks_cache
    _banks_cache = None


def pathways() -> list[dict]:
    return list(load_banks().get("pathways", []))


def pathway_by_id(pathway_id: str) -> dict | None:
    return next((row for row in pathways() if row["id"] == pathway_id), None)


def _question_index() -> dict[str, dict]:
    index = {}
    for pathway in pathways():
        for question in pathway.get("questions", []):
            index[question["id"]] = {**question, "pathway": pathway}
    return index


def _track_slug(lab: Lab | None) -> str:
    level = getattr(lab, "level", None)
    track = getattr(level, "track", None) if level else None
    return str(getattr(track, "slug", "") or "").strip().lower()


def pathway_for_lab(lab: Lab | None) -> dict | None:
    """Pick the most specific pathway that lists the lab's track.

    A single-track pathway (Network+, Linux+) is more specific than a broad
    pathway (Security+), so the smallest matching track list wins.
    """
    slug = _track_slug(lab)
    if not slug:
        return None
    matches = [
        pathway
        for pathway in pathways()
        if slug in {str(track).lower() for track in pathway.get("tracks", [])}
    ]
    if not matches:
        return None
    matches.sort(key=lambda row: (len(row.get("tracks", [])), row["name"]))
    return matches[0]


def _lab_text(lab: Lab) -> str:
    level = getattr(lab, "level", None)
    track = getattr(level, "track", None) if level else None
    return " ".join(
        str(value or "").lower()
        for value in (
            getattr(lab, "name", ""),
            getattr(lab, "slug", ""),
            getattr(lab, "category", ""),
            getattr(lab, "primary_competency", ""),
            getattr(lab, "chapter_name", ""),
            getattr(track, "name", ""),
        )
    )


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= 4
    }


def domain_for_lab(pathway: dict, lab: Lab) -> dict:
    """Choose the pathway domain most relevant to the exercise text."""
    domains = pathway.get("domains", [])
    if not domains:
        return {"id": "", "name": pathway.get("name", "General")}
    text_tokens = _tokens(_lab_text(lab))
    best = domains[0]
    best_score = -1
    for domain in domains:
        score = len(text_tokens & _tokens(domain.get("name", "")))
        if score > best_score:
            best = domain
            best_score = score
    return best


def questions_for_lab(lab: Lab | None) -> list[dict]:
    pathway = pathway_for_lab(lab)
    if pathway is None:
        return []
    return list(pathway.get("questions", []))


def sample_for_lab(
    lab: Lab | None,
    count: int = SAMPLE_SIZE,
    previous_keys: set[str] | None = None,
) -> list[dict]:
    """Return sampled certification questions, or an empty list if unmapped."""
    pathway = pathway_for_lab(lab)
    if pathway is None or not pathway.get("questions"):
        return []
    domain = domain_for_lab(pathway, lab)
    previous = {
        key[len(CERT_PREFIX):] if key.startswith(CERT_PREFIX) else key
        for key in (previous_keys or set())
    }
    relevant = [
        question
        for question in pathway["questions"]
        if question.get("domain") == domain.get("id")
    ]
    pool = relevant if len(relevant) >= count else list(pathway["questions"])
    fresh = [question for question in pool if question["id"] not in previous]
    if len(fresh) < count:
        fresh = pool
    selected = random.sample(fresh, min(count, len(fresh)))
    return [
        {
            **question,
            "key": f"{CERT_PREFIX}{question['id']}",
            "pathway": {
                "id": pathway["id"],
                "name": pathway["name"],
                "code": pathway.get("code"),
                "url": pathway.get("url"),
            },
            "domain_name": domain.get("name"),
        }
        for question in selected
    ]


def resolve_question(key: str) -> dict | None:
    if not key.startswith(CERT_PREFIX):
        return None
    return _question_index().get(key[len(CERT_PREFIX):])


def pathway_summary(pathway: dict) -> dict:
    return {
        "id": pathway["id"],
        "name": pathway["name"],
        "code": pathway.get("code"),
        "url": pathway.get("url"),
        "objectives_url": pathway.get("objectives_url"),
        "tracks": pathway.get("tracks", []),
        "domains": pathway.get("domains", []),
        "careers": pathway.get("careers", []),
        "question_count": len(pathway.get("questions", [])),
    }


def public_pathway_for_lab(lab: Lab | None) -> dict | None:
    pathway = pathway_for_lab(lab)
    if pathway is None:
        return None
    domain = domain_for_lab(pathway, lab)
    return {
        "id": pathway["id"],
        "name": pathway["name"],
        "code": pathway.get("code"),
        "url": pathway.get("url"),
        "domain": {"id": domain.get("id"), "name": domain.get("name")},
        "careers": pathway.get("careers", []),
        "sample_size": SAMPLE_SIZE,
        "question_count": len(pathway.get("questions", [])),
        "notice": (
            "Original practice written to public certification objectives. "
            "Not an exam item and not a certification exam."
        ),
    }


def _is_self_reference(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host:
        return True
    if host in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
        return True
    return any(
        marker in host
        for marker in ("opencyberrange", "swocts", "example.com", "example.org")
    )


def validate_banks() -> dict:
    """Static reliability checks for the admin question bank."""
    issues: list[dict] = []
    seen_ids: set[str] = set()
    seen_prompts: set[str] = set()
    question_count = 0

    if not load_banks().get("reviewed_at"):
        issues.append({"level": "error", "where": "file", "message": "reviewed_at is missing"})

    for pathway in pathways():
        pathway_id = pathway.get("id", "?")
        for field in ("name", "code", "url", "objectives_url", "tracks", "domains", "careers"):
            if not pathway.get(field):
                issues.append(
                    {
                        "level": "error",
                        "where": pathway_id,
                        "message": f"pathway field '{field}' is missing",
                    }
                )
        domains = {str(domain.get("id")) for domain in pathway.get("domains", [])}
        for question in pathway.get("questions", []):
            question_count += 1
            where = f"{pathway_id}/{question.get('id', '?')}"
            if question.get("id") in seen_ids:
                issues.append({"level": "error", "where": where, "message": "duplicate question id"})
            seen_ids.add(question.get("id"))
            prompt = str(question.get("prompt") or "").strip()
            if len(prompt) < 20:
                issues.append({"level": "error", "where": where, "message": "prompt is too short"})
            if prompt.lower() in seen_prompts:
                issues.append({"level": "warning", "where": where, "message": "duplicate prompt"})
            seen_prompts.add(prompt.lower())
            options = question.get("options") or []
            if len(options) < 2:
                issues.append({"level": "error", "where": where, "message": "needs at least two options"})
            correct = question.get("correct")
            if not isinstance(correct, int) or not 0 <= correct < len(options):
                issues.append({"level": "error", "where": where, "message": "invalid correct index"})
            explanation = str(question.get("explanation") or "").strip()
            if len(explanation) < 40:
                issues.append({"level": "error", "where": where, "message": "explanation is too short"})
            if str(question.get("domain")) not in domains:
                issues.append({"level": "error", "where": where, "message": "domain is not declared"})
            if not str(question.get("objective") or "").strip():
                issues.append({"level": "error", "where": where, "message": "objective is missing"})
            if not str(question.get("career") or "").strip():
                issues.append({"level": "error", "where": where, "message": "career is missing"})
            reference = question.get("reference") or {}
            url = str(reference.get("url") or "").strip()
            if not url.startswith("https://"):
                issues.append({"level": "error", "where": where, "message": "reference must be an https URL"})
            elif _is_self_reference(url):
                issues.append({"level": "error", "where": where, "message": "reference is self-referencing or local"})
            if not str(reference.get("label") or "").strip():
                issues.append({"level": "warning", "where": where, "message": "reference label is missing"})

    errors = sum(1 for issue in issues if issue["level"] == "error")
    return {
        "ok": errors == 0,
        "reviewed_at": load_banks().get("reviewed_at"),
        "pathways": len(pathways()),
        "questions": question_count,
        "errors": errors,
        "warnings": sum(1 for issue in issues if issue["level"] == "warning"),
        "issues": issues,
    }


def admin_payload() -> dict:
    """Full bank for administrators, including answers and explanations."""
    return {
        "version": load_banks().get("version"),
        "reviewed_at": load_banks().get("reviewed_at"),
        "status": load_banks().get("status"),
        "notes": load_banks().get("notes"),
        "pathways": [
            {
                **pathway_summary(pathway),
                "questions": pathway.get("questions", []),
            }
            for pathway in pathways()
        ],
        "validation": validate_banks(),
    }
