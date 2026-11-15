#!/usr/bin/env python3
"""Validate built MkDocs output before it is published.

The source checks (check-links, check-doc-assets) run before a build. This
script inspects the built tree for problems a source check cannot see:

* a missing ``index.html`` for a site;
* root-absolute ``href="/..."`` or ``src="/..."`` references, which break the
  site when it is served under a prefix;
* a ``course/`` directory, which is runtime learner content and must never be
  published from a repository build;
* a site that still contains an absolute ``http(s)://`` link to a platform API.

Usage:
    python scripts/check-built-docs.py --root _site_manual_lite
    python scripts/check-built-docs.py --root "$RUNNER_TEMP/sites" --require reference/manual
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT_ABSOLUTE = re.compile(r'(?:href|src)="/[^"]*"', re.IGNORECASE)
COURSE_DIR = "course"


def site_roots(root: Path) -> list[Path]:
    """Return the directory for each site under ``root``.

    A site is either ``root`` itself (when it has index.html) or a directory
    that has index.html, including the namespaced reference/manual layout.
    """
    if (root / "index.html").is_file():
        return [root]
    found: list[Path] = []
    for path in sorted(root.rglob("index.html")):
        parent = path.parent
        # Skip nested page indexes; only the top of each site has search/.
        if (parent / "search" / "search_index.json").is_file():
            found.append(parent)
    return found


def check_site(site: Path, root: Path, skip_root_absolute: bool = False) -> list[str]:
    problems: list[str] = []
    rel = site.relative_to(root)
    if not (site / "index.html").is_file():
        problems.append(f"{rel}: missing index.html")
        return problems
    if not (site / "search" / "search_index.json").is_file():
        problems.append(f"{rel}: missing search/search_index.json")
    if skip_root_absolute:
        return problems
    for path in site.rglob("*.html"):
        # Material's 404 template uses absolute asset paths when site_url is
        # empty. A static host usually supplies its own 404 page; do not let
        # that optional file block an otherwise portable site.
        if path.name == "404.html":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = ROOT_ABSOLUTE.search(text)
        if match:
            problems.append(
                f"{path.relative_to(root)}: root-absolute reference {match.group(0)}"
            )
            break
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Built output directory.")
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        help="Relative site path that must exist (repeatable).",
    )
    parser.add_argument(
        "--allow-course",
        action="store_true",
        help="Permit a course/ directory (off by default; runtime content).",
    )
    parser.add_argument(
        "--skip-root-absolute",
        action="store_true",
        help="Do not fail on root-absolute asset references (inspection builds).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"FAIL: build root does not exist: {root}", file=sys.stderr)
        return 1

    problems: list[str] = []
    sites = site_roots(root)
    if not sites:
        problems.append(f"{root}: no MkDocs site (index.html + search/) found")

    for relative in args.require:
        if not (root / relative / "index.html").is_file():
            problems.append(f"{relative}: required site is missing")

    if not args.allow_course:
        for course in root.rglob(COURSE_DIR):
            if course.is_dir() and any(course.iterdir()):
                problems.append(
                    f"{course.relative_to(root)}: runtime course content must "
                    "not be published from a repository build"
                )
                break

    for site in sites:
        problems.extend(
            check_site(site, root, skip_root_absolute=args.skip_root_absolute)
        )

    if problems:
        print("FAIL: built documentation has publish blockers:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    total_files = sum(1 for path in root.rglob("*") if path.is_file())
    total_bytes = sum(path.stat().st_size for path in root.rglob("*") if path.is_file())
    print(
        f"PASS: {len(sites)} site(s), {total_files} files, "
        f"{total_bytes / (1024 * 1024):.1f} MiB"
    )
    for site in sites:
        print(f"  - {site.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
