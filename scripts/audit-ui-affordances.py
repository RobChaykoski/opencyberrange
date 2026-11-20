#!/usr/bin/env python3
"""Report affordance and signifier problems in the Vue frontend.

Heuristic, not a verdict. It flags the shapes that are wrong on their face:

  * a click handler on an element that is not interactive and declares no
    role, tabindex, or key handler;
  * an anchor with no href, or a "#" used as a button;
  * a button without an explicit type, which defaults to submit;
  * an icon-only button with no accessible name;
  * cursor: pointer on a selector that is not a control.

Read the high-severity hits in context before changing anything: a modal
backdrop and a false affordance look the same to a regex.

Usage:
    python scripts/audit-ui-affordances.py
    python scripts/audit-ui-affordances.py --json
    python scripts/audit-ui-affordances.py --fail-on-high
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "platform" / "frontend" / "src"
TAG_RE = re.compile(r"<([a-zA-Z][\w-]*)((?:\s+[^<>]*?)?)/?>", re.S)
NATIVE = {"button", "a", "input", "select", "textarea", "label", "summary", "option"}
CONTROL_HINT = re.compile(
    r"(btn|button|link|tab|clickable|toggle|card|chip|pill|row|option|summary|node|role|axis|label)",
    re.I,
)


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def audit_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")

    for match in TAG_RE.finditer(text):
        tag = match.group(1).lower()
        attrs = match.group(2) or ""
        line = line_of(text, match.start())

        if "@click" in attrs and tag not in NATIVE:
            # A dismiss backdrop (backdrop click plus Escape, or the shared
            # dialog directive) is not a control; flagging it is noise.
            backdrop = ("@click.self" in attrs and "@keydown.esc" in attrs) or (
                "v-modal-dialog" in attrs
            )
            if not backdrop:
                missing = []
                if "role=" not in attrs:
                    missing.append("role")
                if "tabindex" not in attrs:
                    missing.append("tabindex")
                if not any(k in attrs for k in ("@keydown", "@keyup", "@keypress")):
                    missing.append("key handler")
                if missing:
                    findings.append(
                        {
                            "file": rel,
                            "line": line,
                            "severity": "high",
                            "message": f"click on <{tag}> without {', '.join(missing)}",
                        }
                    )

        if tag == "a":
            href = re.search(r'href="([^"]*)"', attrs)
            if not href or href.group(1).strip() in {"", "#"}:
                findings.append(
                    {
                        "file": rel,
                        "line": line,
                        "severity": "high",
                        "message": "<a> without a real href",
                    }
                )

        if tag == "button":
            if "type=" not in attrs:
                findings.append(
                    {
                        "file": rel,
                        "line": line,
                        "severity": "low",
                        "message": "<button> without explicit type",
                    }
                )
            body = text[match.end(): match.end() + 400].split("</button>")[0]
            visible = re.sub(r"<[^>]+>", "", body).strip()
            if (
                not visible
                and "aria-label" not in attrs
                and "title=" not in attrs
                and ("<svg" in body or "<img" in body or "<i " in body)
            ):
                findings.append(
                    {
                        "file": rel,
                        "line": line,
                        "severity": "high",
                        "message": "icon-only <button> without aria-label/title",
                    }
                )

    for style_match in re.finditer(r"<style[^>]*>(.*?)</style>", text, re.S):
        for rule in re.finditer(r"([^{}]+)\{([^}]*)\}", style_match.group(1)):
            selector, body = rule.group(1).strip(), rule.group(2)
            if "cursor: pointer" not in body and "cursor:pointer" not in body:
                continue
            compact = " ".join(selector.split())
            if not CONTROL_HINT.search(compact):
                findings.append(
                    {
                        "file": rel,
                        "line": 0,
                        "severity": "low",
                        "message": f"cursor:pointer on {compact[:60]}",
                    }
                )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument(
        "--fail-on-high",
        action="store_true",
        help="exit 1 when any high-severity finding is present",
    )
    args = parser.parse_args()

    findings = [row for path in sorted(SRC.rglob("*.vue")) for row in audit_file(path)]
    findings.sort(key=lambda row: (row["severity"] != "high", row["file"], row["line"]))

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        high = [row for row in findings if row["severity"] == "high"]
        low = [row for row in findings if row["severity"] == "low"]
        print(f"scanned {SRC}")
        print(f"findings: {len(findings)} ({len(high)} high, {len(low)} low)\n")

        by_file: dict[str, list[dict]] = defaultdict(list)
        for row in high:
            by_file[row["file"]].append(row)
        for name, rows in sorted(by_file.items(), key=lambda item: -len(item[1])):
            print(f"  {len(rows):3d}  {name}")
        print()

        for row in high[:40]:
            where = f"{row['file']}:{row['line']}" if row["line"] else row["file"]
            print(f"  HIGH  {where}  {row['message']}")
        if len(high) > 40:
            print(f"  ... {len(high) - 40} more high-severity findings")

        counts = Counter(row["message"].split(":")[0] for row in findings)
        print("\n  by shape:")
        for label, count in counts.most_common(6):
            print(f"  {count:4d}  {label}")

    if args.fail_on_high and any(row["severity"] == "high" for row in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
