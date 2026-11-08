#!/usr/bin/env python3
"""Per-lab release proof for the nine curriculum criteria.

This is a static evidence gate, not a substitute for a student walkthrough. It
checks what can be proven from lab.yaml, the compose file, the workbook, and
repository metadata, and marks the rest as REVIEW so a human can sign it off.

Usage:
    python scripts/lab-release-proof.py
    python scripts/lab-release-proof.py --json
    python scripts/lab-release-proof.py --write docs/reviews/LAB-RELEASE-PROOF.md
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
LABS = ROOT / "platform" / "labs"
WORKBOOK = ROOT / "Workbook"

ACTION_VERBS = {
    "analyze", "analyse", "assemble", "capture", "collect", "configure",
    "confirm", "create", "demonstrate", "detect", "differentiate", "discover",
    "document", "enumerate", "explain", "exploit", "extract", "fetch",
    "identify", "inspect", "interact", "investigate", "map", "recover",
    "record", "review", "scan", "search", "submit", "test", "trace", "treat",
    "validate", "verify",
}
DEFENSIVE_WORDS = (
    "defensive", "defence", "defense", "detection", "mitigat", "harden",
    "prevent", "remediat", "what just happened", "takeaway",
)
TROUBLESHOOT_WORDS = (
    "troubleshoot", "if you get stuck", "common mistake", "technical failure",
    "connection refused", "target unreachable",
)
DIFFICULTIES = {"beginner", "intermediate", "advanced", "expert"}
FLAG_RE = re.compile(r"^OCR\{.+\}$")


def _load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    except Exception:
        return {}


def _workbook_text(lab: dict) -> str:
    workbook = str(lab.get("workbook") or "").strip("/")
    if not workbook:
        return ""
    parts = workbook.split("/")
    if len(parts) < 4:
        return ""
    chapter, exercise = parts[-2], parts[-1]
    for candidate in (
        WORKBOOK / chapter / f"{exercise}.md",
        WORKBOOK / chapter / exercise / "index.md",
        WORKBOOK / chapter / exercise / "00_Introduction.md",
    ):
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8", errors="replace")
    return ""


def _objectives_measurable(lab: dict) -> tuple[bool, str]:
    objectives = lab.get("objectives") or []
    if not isinstance(objectives, list) or not objectives:
        return False, "no objectives list"
    measurable = 0
    for objective in objectives:
        text = str(objective).strip().lower()
        first = text.split()[0] if text.split() else ""
        if first in ACTION_VERBS:
            measurable += 1
    if measurable == 0:
        return False, "no objective begins with an action verb"
    if measurable < len(objectives):
        return True, f"{measurable}/{len(objectives)} objectives begin with an action verb"
    return True, "all objectives begin with an action verb"


def _flag_demonstrates(lab: dict) -> tuple[bool, str]:
    flag = str(lab.get("flag") or "")
    if not FLAG_RE.match(flag):
        return False, "flag is missing or not OCR{...}"
    objectives = " ".join(str(o) for o in (lab.get("objectives") or [])).lower()
    test_steps = (lab.get("test") or {}).get("steps") or []
    flag_step = any("OCR{" in str(step.get("expect", "")) for step in test_steps)
    objective_flag = "flag" in objectives
    if not flag_step:
        return False, "no test step expects OCR{"
    if not objective_flag:
        return True, "test retrieves the flag but no objective names it"
    return True, "test retrieves the flag and an objective names it"


def _workbook_matches(lab: dict, workbook: str) -> tuple[str, str]:
    if not workbook:
        if str(lab.get("category") or "").lower() == "assessment":
            return "review", "no workbook; confirm this is an instructor-led assessment"
        return "gap", "no workbook linked"
    declared_hosts = {
        str(item.get("hostname", "")).lower()
        for item in (lab.get("hostnames") or [])
        if isinstance(item, dict) and item.get("hostname")
    }
    if declared_hosts:
        lower = workbook.lower()
        if not any(host in lower for host in declared_hosts):
            # Placeholder-based workbooks are acceptable if they tell the
            # student to use the target shown in the exercise.
            if "<target>" not in lower and "{target" not in lower:
                return "gap", "declared hostnames do not appear in the workbook"
    return "pass", "workbook exists and hostnames or target placeholders agree"


def _duration_realistic(lab: dict, track_medians: dict[str, float]) -> tuple[bool, str]:
    try:
        duration = int(lab.get("duration_minutes") or 0)
    except (TypeError, ValueError):
        return False, "duration_minutes is not an integer"
    if duration < 10 or duration > 300:
        return False, f"duration {duration} is outside 10-300 minutes"
    track = lab.get("__track__", "")
    median = track_medians.get(track)
    if median and (duration > median * 2.5 or duration < median / 3):
        return True, f"{duration} min is an outlier against the track median {median:.0f}"
    return True, f"{duration} min is within the track range"


def _difficulty_evidence(lab: dict) -> tuple[str, str]:
    difficulty = str(lab.get("difficulty") or "").lower()
    if difficulty not in DIFFICULTIES:
        return "gap", f"difficulty '{difficulty}' is not a known value"
    if not lab.get("difficulty_evidence"):
        return "review", "difficulty is declared but learner evidence is not recorded"
    return "pass", "difficulty has a written evidence note"


def _hints_scaffold(lab: dict) -> tuple[str, str]:
    hints = lab.get("hints") or []
    is_assessment = str(lab.get("category") or "").lower() == "assessment"
    if not isinstance(hints, list) or len(hints) < 3:
        count = len(hints) if isinstance(hints, list) else 0
        if is_assessment:
            return "review", f"{count} hints; confirm the assessment needs no more"
        return "gap", f"{count} hints; need at least 3"
    flag = str(lab.get("flag") or "")
    unlocks = []
    for hint in hints:
        text = str(hint.get("text", ""))
        if flag and flag in text:
            return "gap", "a hint contains the flag"
        try:
            unlocks.append(int(hint.get("unlock_after_minutes", 0)))
        except (TypeError, ValueError):
            return "gap", "hint unlock_after_minutes is not an integer"
    if unlocks != sorted(unlocks):
        return "gap", "hint unlock times are not increasing"
    if len(set(unlocks)) < 2:
        return "gap", "hints do not unlock progressively"
    return "pass", f"{len(hints)} hints unlock progressively"


def _technical_failures(lab: dict, workbook: str) -> tuple[str, str]:
    if str(lab.get("troubleshooting") or "").strip():
        return "pass", "lab.yaml has troubleshooting guidance"
    haystack = (json.dumps(lab, ensure_ascii=False) + "\n" + workbook).lower()
    if any(word in haystack for word in TROUBLESHOOT_WORDS):
        return "pass", "troubleshooting guidance distinguishes technical failure"
    steps = (lab.get("test") or {}).get("steps") or []
    if steps and all(step.get("expect") for step in steps):
        return "review", "test steps have expected outputs; add a troubleshooting note"
    return "gap", "no troubleshooting guidance"


def _defensive_interpretation(lab: dict, workbook: str) -> tuple[str, str]:
    if str(lab.get("defensive_takeaways") or "").strip():
        return "pass", "lab.yaml has a defensive takeaway"
    haystack = (json.dumps(lab, ensure_ascii=False) + "\n" + workbook).lower()
    if any(word in haystack for word in DEFENSIVE_WORDS):
        return "pass", "defensive or detection interpretation present"
    return "gap", "no defensive takeaway found"


def _metadata(lab: dict) -> tuple[bool, str]:
    missing = [
        field for field in ("owner", "content_version", "reviewed_at")
        if not str(lab.get(field) or "").strip()
    ]
    if missing:
        return False, f"missing {', '.join(missing)}"
    return True, f"owner={lab['owner']}, version={lab['content_version']}, reviewed={lab['reviewed_at']}"


def audit_lab(lab_dir: Path, track_medians: dict[str, float]) -> dict:
    lab = _load_yaml(lab_dir / "lab.yaml")
    lab["__track__"] = lab_dir.relative_to(LABS).parts[0]
    workbook = _workbook_text(lab)
    checks = {}

    for key, result in (
        ("objective_measurable", _objectives_measurable(lab)),
        ("flag_demonstrates_objective", _flag_demonstrates(lab)),
        ("workbook_matches_environment", _workbook_matches(lab, workbook)),
        ("duration_realistic", _duration_realistic(lab, track_medians)),
        ("hints_scaffold", _hints_scaffold(lab)),
        ("technical_failures_distinguishable", _technical_failures(lab, workbook)),
        ("defensive_interpretation", _defensive_interpretation(lab, workbook)),
        ("owner_version_review", _metadata(lab)),
    ):
        status, detail = result
        if isinstance(status, bool):
            status = "pass" if status else "gap"
        checks[key] = {"status": status, "detail": detail}

    status, detail = _difficulty_evidence(lab)
    checks["difficulty_evidence"] = {"status": status, "detail": detail}

    # A lab passes only when every check is pass. Any gap fails the release gate.
    verdict = "pass"
    if any(item["status"] == "gap" for item in checks.values()):
        verdict = "fail"
    elif any(item["status"] == "review" for item in checks.values()):
        verdict = "review"

    return {
        "slug": lab_dir.name,
        "name": lab.get("name", lab_dir.name),
        "track": lab["__track__"],
        "difficulty": lab.get("difficulty"),
        "duration_minutes": lab.get("duration_minutes"),
        "workbook": lab.get("workbook"),
        "owner": lab.get("owner"),
        "content_version": lab.get("content_version"),
        "reviewed_at": lab.get("reviewed_at"),
        "verdict": verdict,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", default="")
    args = parser.parse_args()

    lab_dirs = sorted({path.parent for path in LABS.rglob("lab.yaml")})
    durations: dict[str, list[int]] = {}
    for lab_dir in lab_dirs:
        lab = _load_yaml(lab_dir / "lab.yaml")
        track = lab_dir.relative_to(LABS).parts[0]
        try:
            durations.setdefault(track, []).append(int(lab.get("duration_minutes") or 0))
        except (TypeError, ValueError):
            pass
    medians = {
        track: statistics.median([value for value in values if value > 0] or [0])
        for track, values in durations.items()
    }

    results = [audit_lab(lab_dir, medians) for lab_dir in lab_dirs]
    summary = {
        "labs": len(results),
        "pass": sum(1 for row in results if row["verdict"] == "pass"),
        "review": sum(1 for row in results if row["verdict"] == "review"),
        "fail": sum(1 for row in results if row["verdict"] == "fail"),
        "checks": {
            key: {
                "pass": sum(1 for row in results if row["checks"][key]["status"] == "pass"),
                "review": sum(1 for row in results if row["checks"][key]["status"] == "review"),
                "gap": sum(1 for row in results if row["checks"][key]["status"] == "gap"),
            }
            for key in results[0]["checks"] if results
        },
    }

    if args.json:
        print(json.dumps({"summary": summary, "labs": results}, indent=2))
    else:
        print(f"Labs: {summary['labs']}  pass: {summary['pass']}  review: {summary['review']}  fail: {summary['fail']}")
        for key, counts in summary["checks"].items():
            print(f"  {key}: pass={counts['pass']} review={counts['review']} gap={counts['gap']}")

    if args.write:
        write_markdown(Path(args.write), summary, results)
    return 1 if summary["fail"] else 0


def write_markdown(path: Path, summary: dict, results: list[dict]) -> None:
    lines = [
        "# Lab release proof",
        "",
        "Status: **automated evidence pass; live student walkthrough still required**",
        "Generated by `scripts/lab-release-proof.py`.",
        "",
        "This report checks the nine v2.5.2 release criteria for every lab. "
        "`pass` means the static evidence is present. `review` means the check "
        "needs a human or learner-evidence decision. `fail` means a required "
        "artefact is missing.",
        "",
        "## Summary",
        "",
        f"- Labs: **{summary['labs']}**",
        f"- Pass: **{summary['pass']}**",
        f"- Review: **{summary['review']}**",
        f"- Fail: **{summary['fail']}**",
        "",
        "| Criterion | Pass | Review | Gap |",
        "|---|---:|---:|---:|",
    ]
    for key, counts in summary["checks"].items():
        lines.append(f"| `{key}` | {counts['pass']} | {counts['review']} | {counts['gap']} |")

    lines += [
        "",
        "## Gaps and reviews",
        "",
        "| Lab | Track | Verdict | Gaps / reviews |",
        "|---|---|---|---|",
    ]
    for row in results:
        issues = [
            f"{key}: {item['detail']}"
            for key, item in row["checks"].items()
            if item["status"] in {"gap", "review"}
        ]
        if issues:
            lines.append(
                f"| `{row['slug']}` | {row['track']} | {row['verdict']} | "
                + "<br>".join(issues).replace("|", "\\|")
                + " |"
            )

    lines += [
        "",
        "## How to use this report",
        "",
        "1. Fix every `gap` before release.",
        "2. Review every `review` with the student-tester skill and record the",
        "   walkthrough evidence.",
        "3. Re-run the script after changes.",
        "4. Do not mark a lab `pass` from this script alone; it proves artefacts,",
        "   not that a learner can complete the lab.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
