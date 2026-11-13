#!/usr/bin/env python3
"""Fail when reviewed URL bindings stop using safeHttpUrl.

The security review named three components whose records can carry an
administrator- or content-supplied URL: the tool panel, the question-bank admin
view, and the community-events calendar. This guard keeps that decision from
silently regressing in a later template edit.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "platform/frontend/src/components/ToolPanel.vue": [
        "safeHttpUrl(activeTool.value?.url)",
        ':href="toolUrl"',
        ':src="toolUrl"',
    ],
    "platform/frontend/src/components/QuestionBankAdmin.vue": [
        "safeHttpUrl(detail.objectives_url)",
        "safeHttpUrl(question.reference.url)",
    ],
    "platform/frontend/src/components/CommunityEventsCalendar.vue": [
        "safeHttpUrl(event.url)",
        "safeHttpUrl(source.url)",
        "safeHttpUrl(source.calendarUrl)",
    ],
}

FORBIDDEN = {
    "platform/frontend/src/components/ToolPanel.vue": [
        ':href="activeTool.url"',
        ':src="activeTool.url"',
    ],
    "platform/frontend/src/components/QuestionBankAdmin.vue": [
        ':href="detail.objectives_url"',
        ':href="question.reference.url"',
    ],
    "platform/frontend/src/components/CommunityEventsCalendar.vue": [
        ':href="event.url"',
        ':href="source.url"',
        ':href="source.calendarUrl"',
    ],
}


def main() -> int:
    failures: list[str] = []
    for name, required in CHECKS.items():
        path = ROOT / name
        if not path.is_file():
            failures.append(f"missing: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        if "import { safeHttpUrl }" not in text:
            failures.append(f"{name}: safeHttpUrl is not imported")
        for needle in required:
            if needle not in text:
                failures.append(f"{name}: missing {needle}")
        for needle in FORBIDDEN.get(name, []):
            if needle in text:
                failures.append(f"{name}: unsafe binding {needle}")
    if failures:
        print("safe URL guard: FAIL")
        for line in failures:
            print(f"  - {line}")
        return 1
    print("safe URL guard: OK (tool panel, question banks, community events)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
