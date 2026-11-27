#!/usr/bin/env python3
"""One lab-quality pass over manifests, workbooks, and compose files.

This is the normalizer gate: it checks the shared metadata contract, the
workbook's concept coverage, and the container safety defaults. It does not
rewrite prose; it reports drift so a reviewer can fix it deliberately.

Usage:
    python scripts/lint_labs.py --check
    python scripts/lint_labs.py --check --strict
    python scripts/lint_labs.py --json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"
WORKBOOK = ROOT / "Workbook"
FIELDS = (
    "learning_concepts",
    "competency_tags",
    "defensive_skills",
    "evidence_required",
    "report_questions",
)
CONCEPT_GROUPS = {
    "scenario": ("scenario", "background", "what just happened"),
    "objectives": ("objective", "your objectives", "goal", "what you will practise"),
    "tasks": ("walkthrough", "guided steps", "work through the exercise", "tasks"),
    "flag": ("flag", "submit", "what success looks like"),
    "remediation": (
        "defensive takeaway",
        "defensive takeaways",
        "the fixes",
        "key takeaways",
        "defensive controls",
    ),
}
IP_RE = re.compile(r"(?<![\d.])(?:10\.)\d{1,3}\.\d{1,3}\.\d{1,3}(?![\d.])")
FINDINGS: list[dict] = []


def add(level: str, check: str, lab: str, detail: str) -> None:
    FINDINGS.append({"level": level, "check": check, "lab": lab, "detail": detail})


def load_yaml(path: Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        add("error", "yaml", path.parent.name, f"cannot parse: {exc}")
        return {}


def workbook_page(lab: dict) -> Path | None:
    value = str(lab.get("workbook") or "").strip()
    if not value:
        return None
    parts = [part for part in value.replace("\\", "/").split("/") if part]
    chapter = next((part for part in parts if part.startswith("CH_")), "")
    page = parts[-1] if parts else ""
    candidates = []
    if chapter and page:
        candidates.append(WORKBOOK / chapter / f"{page}.md")
    if page:
        candidates.extend(WORKBOOK.rglob(f"{page}.md"))
    return next((path for path in candidates if path.is_file()), None)


def check_manifest(path: Path) -> None:
    lab = load_yaml(path)
    slug = path.parent.name
    for field in FIELDS:
        if lab.get(field) in (None, "", []):
            add("error", "metadata", slug, f"missing {field}")
    flag = str(lab.get("flag") or "")
    if not flag.startswith("OCR{") or flag.endswith("OCR{}"):
        add("error", "flag", slug, "missing or malformed flag")
    if not str(lab.get("defensive_takeaways") or "").strip():
        add("warning", "defensive", slug, "no defensive takeaway")
    if not str(lab.get("workbook") or "").strip():
        if not lab.get("assessment_workbook_exemption"):
            add("warning", "workbook", slug, "no workbook path")
        return
    page = workbook_page(lab)
    if page is None:
        if not lab.get("assessment_workbook_exemption"):
            add("warning", "workbook", slug, "workbook page does not resolve")
        return

    text = page.read_text(encoding="utf-8", errors="ignore")
    headings = " ".join(
        line[3:].strip().lower()
        for line in text.splitlines()
        if line.startswith("## ")
    )
    for concept, needles in CONCEPT_GROUPS.items():
        if not any(needle in headings for needle in needles):
            add("info", "workbook-concept", slug, f"missing {concept} section")

    ips = sorted(set(IP_RE.findall(text)))
    if ips:
        add(
            "info",
            "workbook-ip",
            slug,
            f"hard-coded lab IPs (consider a session token): {', '.join(ips[:4])}",
        )


def check_compose(path: Path) -> None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        add("error", "compose", path.parent.name, f"cannot parse: {exc}")
        return
    services = data.get("services") or {}
    for name, service in services.items():
        if not isinstance(service, dict):
            continue
        slug = f"{path.parent.name}/{name}"
        if service.get("privileged") is True:
            add("error", "compose", slug, "privileged: true is not allowed")
        deploy_limits = (
            (service.get("deploy") or {}).get("resources", {}).get("limits", {})
        )
        if not service.get("mem_limit") and not deploy_limits.get("memory"):
            add("info", "compose", slug, "no memory limit (runtime default applies)")
        if not service.get("pids_limit") and not deploy_limits.get("pids"):
            add("info", "compose", slug, "no pids limit (runtime default applies)")
        image = str(service.get("image") or "")
        if (
            image
            and not service.get("build")
            and "@sha256:" not in image
            and not image.startswith(("ocr-", "ocr/", "localhost/"))
        ):
            add("warning", "compose", slug, f"unpinned upstream image: {image}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    if not args.check and not args.json:
        parser.error("choose --check or --json")

    for path in sorted(LABS.rglob("lab.yaml")):
        check_manifest(path)
    for path in sorted(LABS.rglob("docker-compose*.yml")):
        check_compose(path)

    counts = {
        level: sum(1 for item in FINDINGS if item["level"] == level)
        for level in ("error", "warning", "info")
    }
    if args.json:
        print(json.dumps({"counts": counts, "findings": FINDINGS}, indent=2))
    else:
        print("Lab lint")
        print("=" * 40)
        print(
            f"  errors: {counts['error']}  warnings: {counts['warning']}  "
            f"info: {counts['info']}"
        )
        shown = 0
        for item in FINDINGS:
            if item["level"] == "info":
                continue
            if not args.verbose and shown >= 30:
                remaining = counts["error"] + counts["warning"] - shown
                print(f"  ... {remaining} more")
                break
            print(f"  [{item['level'].upper():7}] {item['lab']}: {item['check']}: {item['detail']}")
            shown += 1
        groups = {}
        for item in FINDINGS:
            if item["level"] == "info":
                groups[item["check"]] = groups.get(item["check"], 0) + 1
        if groups:
            summary = ", ".join(f"{key}={value}" for key, value in sorted(groups.items()))
            print(f"  info: {summary}")
    if counts["error"]:
        return 1
    if args.strict and counts["warning"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
