"""Validate optional exercise knowledge-check banks.

Every bank lives beside a lab at ``<lab>/quiz.yaml``. This checker keeps the
content honest: unique question ids, at least two options, a valid correct
index, an explanation, and a reference. It reports coverage so the team can see
which exercises still need a bank.

Usage:
    python scripts/check-quiz-banks.py
    python scripts/check-quiz-banks.py --check   # non-zero on invalid banks
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return [f"cannot parse: {exc}"]
    if not isinstance(data, dict):
        return ["top level must be a mapping"]
    cert = data.get("certification") or {}
    if not isinstance(cert, dict):
        errors.append("certification must be a mapping")
        cert = {}
    questions = data.get("questions") or []
    if not isinstance(questions, list) or len(questions) < 2:
        return errors + ["needs at least two questions"]
    if cert.get("code") and len(questions) < 5:
        errors.append("certification banks should have at least five questions")
    if not cert.get("code") and len(questions) < 2:
        errors.append("general banks need at least two questions")

    seen = set()
    for index, question in enumerate(questions, 1):
        if not isinstance(question, dict):
            errors.append(f"question {index}: must be a mapping")
            continue
        qid = str(question.get("id") or "").strip()
        if not qid:
            errors.append(f"question {index}: missing id")
        elif qid in seen:
            errors.append(f"question {index}: duplicate id {qid}")
        seen.add(qid)
        prompt = str(question.get("prompt") or "").strip()
        if not prompt:
            errors.append(f"question {index}: missing prompt")
        options = question.get("options") or []
        if not isinstance(options, list) or len(options) < 2:
            errors.append(f"question {index}: needs at least two options")
        correct = question.get("correct")
        if not isinstance(correct, int) or not 0 <= correct < len(options):
            errors.append(f"question {index}: correct index is invalid")
        if not str(question.get("explanation") or "").strip():
            errors.append(f"question {index}: missing explanation")
        reference = question.get("reference") or {}
        if not isinstance(reference, dict) or not str(reference.get("url") or "").strip():
            errors.append(f"question {index}: missing reference url")
    return errors


def main() -> int:
    check = "--check" in sys.argv
    labs = sorted(LABS.rglob("lab.yaml")) if LABS.exists() else []
    lab_banks = sorted(LABS.rglob("quiz.yaml")) if LABS.exists() else []
    track_banks = sorted(LABS.rglob("_track_quiz.yaml")) if LABS.exists() else []
    banks = lab_banks + track_banks
    failures = 0
    certified = 0
    general = 0
    for bank in banks:
        errors = validate(bank)
        rel = bank.relative_to(ROOT)
        data = yaml.safe_load(bank.read_text(encoding="utf-8")) or {}
        if (data.get("certification") or {}).get("code"):
            certified += 1
        else:
            general += 1
        if errors:
            failures += 1
            print(f"FAIL {rel}")
            for error in errors:
                print(f"  - {error}")
        elif "--verbose" in sys.argv:
            print(f"OK   {rel}")
    print(
        f"\nChecked {len(banks)} quiz bank(s) across {len(labs)} lab(s): "
        f"{len(banks) - failures} valid, {failures} invalid "
        f"({certified} certification, {general} general)."
    )
    print(
        f"Coverage: {len(lab_banks)} lab-specific bank(s) + "
        f"{len(track_banks)} track fallback bank(s)."
    )
    if len(labs) and len(lab_banks) < len(labs):
        print(
            f"Lab-specific coverage: {len(lab_banks)}/{len(labs)} labs. "
            "Every track with a fallback bank still offers a check."
        )
    if failures and check:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
