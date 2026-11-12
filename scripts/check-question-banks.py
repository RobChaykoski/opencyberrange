"""Validate the admin-curated certification question banks.

Checks every item for the things a reviewer can verify statically:

* required fields and unique ids;
* a valid correct-answer index and at least two options;
* a substantive explanation and a declared domain and objective;
* an https reference that is not self-referencing or local;
* duplicate prompts.

Optionally check that each reference URL responds. Network checks are off by
default because CI and air-gapped hosts may not have outbound access.

Usage:
    python scripts/check-question-banks.py
    python scripts/check-question-banks.py --check-links
    python scripts/check-question-banks.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
BANKS = ROOT / "platform" / "backend" / "app" / "data" / "certification-question-banks.yaml"


def _self_reference(url: str) -> bool:
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


def validate(check_links: bool = False) -> dict:
    issues: list[dict] = []
    seen_ids: set[str] = set()
    seen_prompts: set[str] = set()
    references: dict[str, str] = {}
    question_count = 0

    if not BANKS.exists():
        return {
            "ok": False,
            "errors": 1,
            "warnings": 0,
            "questions": 0,
            "pathways": 0,
            "issues": [
                {"level": "error", "where": str(BANKS), "message": "bank file is missing"}
            ],
        }

    data = yaml.safe_load(BANKS.read_text(encoding="utf-8")) or {}
    if not data.get("reviewed_at"):
        issues.append(
            {"level": "error", "where": "file", "message": "reviewed_at is missing"}
        )
    pathways = data.get("pathways") or []
    if not pathways:
        issues.append(
            {"level": "error", "where": "file", "message": "no pathways are defined"}
        )

    for pathway in pathways:
        pathway_id = pathway.get("id", "?")
        for field in ("name", "code", "url", "objectives_url", "tracks", "domains"):
            if not pathway.get(field):
                issues.append(
                    {
                        "level": "error",
                        "where": pathway_id,
                        "message": f"pathway field '{field}' is missing",
                    }
                )
        domains = {str(domain.get("id")) for domain in pathway.get("domains", [])}
        questions = pathway.get("questions") or []
        if not questions:
            issues.append(
                {
                    "level": "error",
                    "where": pathway_id,
                    "message": "pathway has no questions",
                }
            )
        for question in questions:
            question_count += 1
            where = f"{pathway_id}/{question.get('id', '?')}"
            question_id = question.get("id")
            if not question_id:
                issues.append({"level": "error", "where": where, "message": "id is missing"})
            elif question_id in seen_ids:
                issues.append(
                    {"level": "error", "where": where, "message": "duplicate question id"}
                )
            seen_ids.add(question_id)

            prompt = str(question.get("prompt") or "").strip()
            if len(prompt) < 20:
                issues.append(
                    {"level": "error", "where": where, "message": "prompt is too short"}
                )
            if prompt.lower() in seen_prompts:
                issues.append(
                    {"level": "warning", "where": where, "message": "duplicate prompt"}
                )
            seen_prompts.add(prompt.lower())

            options = question.get("options") or []
            if len(options) < 2:
                issues.append(
                    {
                        "level": "error",
                        "where": where,
                        "message": "needs at least two options",
                    }
                )
            if len({str(option).strip().lower() for option in options}) != len(options):
                issues.append(
                    {"level": "error", "where": where, "message": "options are not unique"}
                )
            correct = question.get("correct")
            if not isinstance(correct, int) or not 0 <= correct < len(options):
                issues.append(
                    {"level": "error", "where": where, "message": "invalid correct index"}
                )

            explanation = str(question.get("explanation") or "").strip()
            if len(explanation) < 40:
                issues.append(
                    {"level": "error", "where": where, "message": "explanation is too short"}
                )
            if str(question.get("domain")) not in domains:
                issues.append(
                    {"level": "error", "where": where, "message": "domain is not declared"}
                )
            if not str(question.get("objective") or "").strip():
                issues.append(
                    {"level": "error", "where": where, "message": "objective is missing"}
                )

            reference = question.get("reference") or {}
            url = str(reference.get("url") or "").strip()
            label = str(reference.get("label") or "").strip()
            if not url.startswith("https://"):
                issues.append(
                    {
                        "level": "error",
                        "where": where,
                        "message": "reference must be an https URL",
                    }
                )
            elif _self_reference(url):
                issues.append(
                    {
                        "level": "error",
                        "where": where,
                        "message": "reference is self-referencing or local",
                    }
                )
            else:
                references[url] = label
            if not label:
                issues.append(
                    {"level": "warning", "where": where, "message": "reference label is missing"}
                )

    if check_links:
        for url, label in sorted(references.items()):
            try:
                request = urllib.request.Request(
                    url,
                    method="HEAD",
                    headers={"User-Agent": "OpenCyberRange-question-bank-check/1.0"},
                )
                with urllib.request.urlopen(request, timeout=10) as response:
                    status = getattr(response, "status", 200)
                if status >= 400:
                    issues.append(
                        {
                            "level": "warning",
                            "where": url,
                            "message": f"reference returned HTTP {status} ({label})",
                        }
                    )
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                issues.append(
                    {
                        "level": "warning",
                        "where": url,
                        "message": f"reference could not be reached: {exc}",
                    }
                )

    errors = sum(1 for issue in issues if issue["level"] == "error")
    return {
        "ok": errors == 0,
        "errors": errors,
        "warnings": sum(1 for issue in issues if issue["level"] == "warning"),
        "questions": question_count,
        "pathways": len(pathways),
        "reviewed_at": data.get("reviewed_at"),
        "references": len(references),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate certification question banks")
    parser.add_argument("--check-links", action="store_true", help="Check reference URLs")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args()

    result = validate(check_links=args.check_links)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Question bank check")
        print("=" * 40)
        print(
            f"Pathways: {result['pathways']}  Questions: {result['questions']}  "
            f"References: {result.get('references', 0)}  Reviewed: {result.get('reviewed_at')}"
        )
        for issue in result["issues"]:
            print(f"{issue['level'].upper()}: {issue['where']}: {issue['message']}")
        print(
            "PASS" if result["ok"] else f"FAIL ({result['errors']} error(s))"
        )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
