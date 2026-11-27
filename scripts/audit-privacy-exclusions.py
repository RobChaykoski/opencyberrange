#!/usr/bin/env python3
"""Audit learner-data exclusion in instructor-facing analytics.

Under-18 accounts are excluded from instructor reporting by product decision.
The exclusion is easy to apply in one query and forget in the next: RB-05 was
exactly that, where ``_course_context`` removed minors from ``user_ids`` but
the pulse and reaction helpers were still queried without that set.

This audit is a static guardrail, not a proof. It checks two invariants:

1. A direct query for a privacy-sensitive model inside an instructor-facing
   route must be guarded by ``is_minor``/``minor_ids``/``user_ids`` or scoped
   to ``current_user.id``.
2. A call from an instructor-facing route to a helper that queries such a
   model must pass a filtered ``user_ids`` set, or be self-scoped. If the
   helper has no ``user_ids`` parameter it cannot be filtered, which is a
   finding rather than a pass.

Usage:
    python scripts/audit-privacy-exclusions.py --summary
    python scripts/audit-privacy-exclusions.py --json
    python scripts/audit-privacy-exclusions.py --report docs/PRIVACY-AUDIT.md
    python scripts/audit-privacy-exclusions.py --no-fail
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "platform" / "backend" / "app"
SCAN_DIRS = (APP / "routers", APP / "services")

SENSITIVE_MODELS = {"SurveyResponse", "ExercisePulseSurvey", "ExerciseReaction"}

# Names that show a query was narrowed to non-minor accounts.
GUARD_TOKENS = (
    "is_minor",
    "minor_ids",
    "non_minor_ids",
    "allowed_user_ids",
    "user_ids",
)

INSTRUCTOR_DEPS = {
    "get_current_instructor_user",
    "get_current_reporting_user",
    "get_current_admin_user",
    "get_current_institution_admin",
}

ROUTE_METHODS = {"get", "post", "put", "patch", "delete"}


@dataclass
class Finding:
    file: str
    line: int
    endpoint: str
    target: str
    rule: str
    detail: str


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _depends_names(func: ast.AST) -> set[str]:
    """Return dependency names used in ``Depends(...)`` defaults."""
    names = set()
    if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return names
    for default in list(func.args.defaults) + [
        item for item in func.args.kw_defaults if item is not None
    ]:
        if (
            isinstance(default, ast.Call)
            and isinstance(default.func, ast.Name)
            and default.func.id == "Depends"
            and default.args
        ):
            target = default.args[0]
            if isinstance(target, ast.Name):
                names.add(target.id)
            elif isinstance(target, ast.Attribute):
                names.add(target.attr)
    return names


def _route_info(func: ast.AST) -> tuple[str, str] | None:
    """Return (method, path) when the function is an APIRouter route."""
    if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return None
    for deco in func.decorator_list:
        if not isinstance(deco, ast.Call):
            continue
        if not (
            isinstance(deco.func, ast.Attribute)
            and deco.func.attr in ROUTE_METHODS
        ):
            continue
        path = ""
        if deco.args and isinstance(deco.args[0], ast.Constant):
            path = str(deco.args[0].value)
        return deco.func.attr.upper(), path
    return None


def _is_self_scoped(func: ast.AST) -> bool:
    """True when the function only reads the caller's own rows."""
    for node in ast.walk(func):
        if isinstance(node, ast.Compare):
            text = ast.unparse(node)
            if "current_user.id" in text:
                return True
    return False


def _has_guard(text: str) -> bool:
    return any(token in text for token in GUARD_TOKENS)


def _function_applies_minor_rule(func: ast.AST) -> bool:
    """True when the function computes or applies the under-18 exclusion.

    Some routes query first and filter the rows afterwards (the survey
    responses endpoint does this so a suppressed row cannot leak through a
    cohort count), so the guard is not in the query chain.
    """
    text = ast.unparse(func)
    return any(token in text for token in ("is_minor", "minor_ids", "non_minor_ids"))


def _top_chain(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> ast.AST:
    """Return the outermost call/attribute in the same expression chain."""
    current = node
    while current in parents:
        parent = parents[current]
        if isinstance(parent, ast.Attribute) and parent.value is current:
            current = parent
            continue
        if isinstance(parent, ast.Call) and parent.func is current:
            current = parent
            continue
        break
    return current


def _sensitive_queries(func: ast.AST) -> list[ast.AST]:
    queries = []
    for node in ast.walk(func):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "query"
            and node.args
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id in SENSITIVE_MODELS
        ):
            continue
        queries.append(node)
    return queries


def _function_params(func: ast.AST) -> set[str]:
    if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return set()
    args = func.args
    names = {a.arg for a in list(args.args) + list(args.kwonlyargs)}
    return names


def _call_keywords(call: ast.Call) -> set[str]:
    return {kw.arg for kw in call.keywords if kw.arg}


def audit_file(path: Path) -> list[Finding]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    except (OSError, SyntaxError) as exc:  # pragma: no cover - broken input
        return [
            Finding(_rel(path), 0, "-", "parse", "parse-error", str(exc))
        ]

    functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    by_name = {func.name: func for func in functions}
    queries_sensitive = {
        func.name for func in functions if _sensitive_queries(func)
    }

    parents: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    findings: list[Finding] = []

    for func in functions:
        route = _route_info(func)
        if route is None:
            continue
        method, route_path = route
        deps = _depends_names(func)
        if not deps & INSTRUCTOR_DEPS:
            continue
        endpoint = f"{method} {route_path or func.name}"
        self_scoped = _is_self_scoped(func)
        applies_minor_rule = _function_applies_minor_rule(func)

        # Rule 1: direct sensitive query must carry an exclusion guard.
        for query in _sensitive_queries(func):
            text = ast.unparse(_top_chain(query, parents))
            if _has_guard(text) or self_scoped or applies_minor_rule:
                continue
            findings.append(
                Finding(
                    _rel(path),
                    query.lineno,
                    endpoint,
                    next(
                        arg.id
                        for arg in query.args
                        if isinstance(arg, ast.Name)
                    ),
                    "unguarded-query",
                    "Instructor-facing query is not narrowed to non-minor accounts.",
                )
            )

        # Rule 2: helper calls must pass a filtered user set (or be self-scoped).
        for node in ast.walk(func):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            callee_name = node.func.id
            if callee_name not in queries_sensitive or self_scoped:
                continue
            kwargs = _call_keywords(node)
            callee = by_name.get(callee_name)
            params = _function_params(callee) if callee else set()
            if "user_id" in kwargs or "user_ids" in kwargs:
                continue
            if "user_id" in params and "current_user.id" in ast.unparse(node):
                continue
            if "user_ids" not in params:
                detail = (
                    f"{callee_name}() has no user_ids parameter, so the caller "
                    "cannot exclude minors; add one and pass the filtered set."
                )
            else:
                detail = (
                    f"{callee_name}() accepts user_ids but the call does not pass "
                    "the minor-filtered set."
                )
            findings.append(
                Finding(
                    _rel(path),
                    node.lineno,
                    endpoint,
                    callee_name,
                    "unfiltered-helper",
                    detail,
                )
            )

    return findings


def collect() -> list[Finding]:
    findings: list[Finding] = []
    for directory in SCAN_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            findings.extend(audit_file(path))
    return findings


def render_report(findings: list[Finding]) -> str:
    lines = [
        "# Privacy exclusion audit",
        "",
        ("Generated by `python scripts/audit-privacy-exclusions.py --report "
        "docs/PRIVACY-AUDIT.md`."),
        "Do not edit by hand. Regenerate after changing an analytics query.",
        "",
        "## Scope",
        "",
        "Learner-data models: "
        + ", ".join(f"`{name}`" for name in sorted(SENSITIVE_MODELS))
        + ".",
        "",
        ("An instructor-facing route passes when its query is narrowed by "
        "`is_minor`/`minor_ids`/`user_ids`, or is scoped to `current_user.id`. "
        "A call to a helper passes when it passes a filtered `user_ids` set, or "
        "when the helper has no such parameter and the route is self-scoped."),
        "",
        "## Result",
        "",
    ]
    if not findings:
        lines += [
            ("No findings. Every instructor-facing analytics query for a "
            "learner-data model is narrowed to non-minor accounts."),
            "",
        ]
    else:
        lines += [
            f"**{len(findings)} finding(s).**",
            "",
            "| File | Line | Endpoint | Target | Rule | Detail |",
            "|---|---|---|---|---|---|",
        ]
        for item in findings:
            lines.append(
                f"| `{item.file}` | {item.line} | `{item.endpoint}` | "
                f"`{item.target}` | {item.rule} | {item.detail} |"
            )
        lines.append("")
    lines += [
        "## Limits",
        "",
        ("This is a static invariant check, not a proof. It recognises the "
        "helpers and guard names this codebase uses. A new query path, a new "
        "guard name, or a query built through metaprogramming will not be "
        "seen, so a clean report is evidence for review, not a certificate."),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON findings")
    parser.add_argument("--summary", action="store_true", help="one-line summary")
    parser.add_argument("--report", metavar="PATH", help="write Markdown report")
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="exit 0 even when findings exist",
    )
    args = parser.parse_args()

    findings = collect()

    if args.json:
        print(json.dumps([asdict(item) for item in findings], indent=2))
    elif args.summary:
        print(
            f"privacy audit: {len(findings)} finding(s) across "
            f"{len(list(SCAN_DIRS[0].rglob('*.py')))} router/service files"
        )
    else:
        print(render_report(findings))

    if args.report:
        target = ROOT / args.report if not Path(args.report).is_absolute() else Path(args.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_report(findings), encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT)}")

    if findings and not args.no_fail:
        print("FAILED: instructor-facing analytics can include under-18 learner data")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
