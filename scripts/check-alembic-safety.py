#!/usr/bin/env python3
"""Guard the Alembic revision graph and reject autogenerate usage.

The live schema contains runtime tenant DDL and legacy-restored columns and
indexes that are not represented in the migration graph. Autogenerate would
propose destructive drops. This check keeps that unsafe path out of CI and
scripts until the baseline is reconciled.

It parses the revision files with ``ast`` so the docs/quality job does not need
Alembic, the application package, or a database connection.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSIONS = ROOT / "platform" / "backend" / "alembic" / "versions"
SELF = Path(__file__).resolve()

PATTERNS = (
    "alembic revision --autogenerate",
    "autogenerate=True",
    "--autogenerate",
)
SCAN = (ROOT / ".github" / "workflows", ROOT / "scripts")


def _literal(node):
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        return None


def _metadata(path: Path) -> tuple[str | None, list[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    revision = None
    down: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            value = _literal(node.value)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            target = node.target
            value = _literal(node.value)
        else:
            continue
        if not isinstance(target, ast.Name):
            continue
        if target.id == "revision" and isinstance(value, str):
            revision = value
        elif target.id == "down_revision":
            if isinstance(value, str):
                down = [value]
            elif isinstance(value, (tuple, list)):
                down = [item for item in value if isinstance(item, str)]
            elif value is None:
                down = []
    return revision, down


def main() -> int:
    errors: list[str] = []
    graph: dict[str, list[str]] = {}
    for path in VERSIONS.glob("*.py"):
        revision, down = _metadata(path)
        if not revision:
            errors.append(f"{path.name}: no revision id")
            continue
        if revision in graph:
            errors.append(f"duplicate revision id {revision}")
        graph[revision] = down

    if not graph:
        errors.append("no Alembic revisions found")

    down_refs = {item for values in graph.values() for item in values}
    heads = sorted(set(graph) - down_refs)
    if len(heads) != 1:
        errors.append(f"expected one Alembic head, found {heads}")

    missing = sorted(down_refs - set(graph))
    for item in missing:
        errors.append(f"down_revision {item} does not exist")

    for revision, down in graph.items():
        if len(down) > 1:
            errors.append(f"{revision}: merge revisions are not allowed")
        for item in down:
            if item not in graph:
                errors.append(f"{revision}: unknown down_revision {item}")

    if len(heads) == 1:
        visited: list[str] = []
        current: str | None = heads[0]
        while current and current in graph and current not in visited:
            visited.append(current)
            downs = graph[current]
            current = downs[0] if len(downs) == 1 else None
        if len(visited) != len(graph):
            errors.append(
                f"revision graph is disconnected: {len(visited)} of "
                f"{len(graph)} revisions reachable from {heads[0]}"
            )

    for directory in SCAN:
        for path in directory.rglob("*"):
            if not path.is_file() or path == SELF:
                continue
            if path.suffix not in {".yml", ".yaml", ".sh", ".py"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in PATTERNS:
                if pattern in text:
                    errors.append(
                        f"{path.relative_to(ROOT)} uses {pattern!r}; "
                        "hand-write the migration after reviewing the drift"
                    )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: single Alembic head {heads[0]}; no autogenerate usage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
