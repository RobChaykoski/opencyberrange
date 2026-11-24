#!/usr/bin/env python3
"""Probe the product API for cross-tenant leakage during a two-tenant pilot.

Provide one bearer token per tenant. The script compares the resources each
tenant can list, then tries to read the other tenant's resources by id. It never
prints tokens or response bodies; failures report only a method, path, and
status.

Example::

    python scripts/check-tenant-pilot-api.py \
      --base-url https://range.example.edu \
      --token-a "$TOKEN_A" --token-b "$TOKEN_B" \
      --admin-token-a "$ADMIN_A" --admin-token-b "$ADMIN_B"

Use ``--plan`` to print the checks without network access.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any

FORBIDDEN = {401, 403, 404}
SHARED_PREFIX = "/api/labs"


def _plan() -> list[str]:
    return [
        "GET /api/auth/me for both tokens",
        "GET /api/courses/ for both tokens; the id sets must be disjoint",
        "GET /api/courses/{foreign_id} for every foreign course; expect 401/403/404",
        "GET /api/evidence for both tokens; the id sets must be disjoint",
        "GET /api/evidence/{foreign_id} for every foreign item; expect 401/403/404",
        "GET /api/labs/ for both tokens; expect 200 and a common shared slug",
        "GET /api/admin/users with each admin token; every row stays in its tenant",
        "GET /api/admin/users/{foreign_id} for a foreign user; expect 401/403/404",
    ]


def _request(
    base: str, path: str, token: str, context: ssl.SSLContext, timeout: float
) -> tuple[int, Any]:
    request = urllib.request.Request(
        f"{base.rstrip('/')}{path}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, context=context, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except ValueError:
            payload = {}
        return exc.code, payload
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SystemExit(f"request failed for {path}: {exc}") from exc


def _items(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("items", "users", "results", "courses", "evidence"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
    return []


def _ids(rows: list[dict]) -> set[int]:
    return {row["id"] for row in rows if isinstance(row.get("id"), int)}


def _course_slugs(rows: list[dict]) -> set[str]:
    slugs = set()
    for row in rows:
        slug = row.get("slug") or row.get("lab_slug")
        if isinstance(slug, str):
            slugs.add(slug)
    return slugs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://localhost")
    parser.add_argument("--token-a")
    parser.add_argument("--token-b")
    parser.add_argument("--admin-token-a")
    parser.add_argument("--admin-token-b")
    parser.add_argument("--label-a", default="A")
    parser.add_argument("--label-b", default="B")
    parser.add_argument("--insecure", action="store_true")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    if args.plan:
        for line in _plan():
            print(line)
        return 0

    if not args.token_a or not args.token_b:
        parser.error("--token-a and --token-b are required unless --plan is used")

    context = ssl._create_unverified_context() if args.insecure else ssl.create_default_context()
    failures: list[str] = []
    report: dict[str, Any] = {"tenants": {"a": args.label_a, "b": args.label_b}}

    def get(path: str, token: str) -> tuple[int, Any]:
        return _request(args.base_url, path, token, context, args.timeout)

    def expect_forbidden(path: str, token: str, label: str) -> None:
        status, _ = get(path, token)
        if status not in FORBIDDEN:
            failures.append(f"{label}: {path} returned {status}, expected 401/403/404")

    tokens = {"a": args.token_a, "b": args.token_b}
    labels = {"a": args.label_a, "b": args.label_b}

    identities: dict[str, dict] = {}
    for key, token in tokens.items():
        status, body = get("/api/auth/me", token)
        if status != 200 or not isinstance(body, dict):
            failures.append(f"{labels[key]}: /api/auth/me returned {status}")
            continue
        identities[key] = {
            "id": body.get("id"),
            "username": body.get("username"),
            "role": body.get("role"),
        }
    report["identities"] = identities

    courses: dict[str, set[int]] = {}
    for key, token in tokens.items():
        status, body = get("/api/courses/", token)
        if status != 200:
            failures.append(f"{labels[key]}: /api/courses/ returned {status}")
            continue
        courses[key] = _ids(_items(body))

    if len(courses) == 2:
        overlap = courses["a"] & courses["b"]
        if overlap:
            failures.append(
                f"courses: {len(overlap)} course id(s) visible to both tenants"
            )
        for foreign_key, other_key in (("a", "b"), ("b", "a")):
            for course_id in courses[other_key]:
                expect_forbidden(
                    f"/api/courses/{course_id}",
                    tokens[foreign_key],
                    labels[foreign_key],
                )

    evidence: dict[str, set[int]] = {}
    for key, token in tokens.items():
        status, body = get("/api/evidence", token)
        if status != 200:
            failures.append(f"{labels[key]}: /api/evidence returned {status}")
            continue
        evidence[key] = _ids(_items(body))

    if len(evidence) == 2:
        overlap = evidence["a"] & evidence["b"]
        if overlap:
            failures.append(
                f"evidence: {len(overlap)} item id(s) visible to both tenants"
            )
        for foreign_key, other_key in (("a", "b"), ("b", "a")):
            for evidence_id in evidence[other_key]:
                expect_forbidden(
                    f"/api/evidence/{evidence_id}",
                    tokens[foreign_key],
                    labels[foreign_key],
                )

    catalogue: dict[str, set[str]] = {}
    for key, token in tokens.items():
        status, body = get(f"{SHARED_PREFIX}/", token)
        if status != 200:
            failures.append(f"{labels[key]}: {SHARED_PREFIX}/ returned {status}")
            continue
        rows = _items(body)
        catalogue[key] = _course_slugs(rows)
    if len(catalogue) == 2 and not (catalogue["a"] & catalogue["b"]):
        failures.append("catalogue: the two tenants share no lab slugs")

    admins = {
        "a": args.admin_token_a,
        "b": args.admin_token_b,
    }
    admin_identities: dict[str, dict] = {}
    admin_visible: dict[str, set[int]] = {}
    for key, token in admins.items():
        if not token:
            continue
        status, body = get("/api/admin/users", token)
        if status != 200:
            failures.append(f"admin {labels[key]}: /api/admin/users returned {status}")
            continue
        rows = _items(body)
        institutions = {
            row.get("institution_id") for row in rows if row.get("institution_id")
        }
        admin_identities[key] = {"institutions": sorted(institutions)}
        admin_visible[key] = _ids(rows)
        if len(institutions) > 1:
            failures.append(
                f"admin {labels[key]}: users span {len(institutions)} institutions"
            )

    if "a" in admin_visible and "b" in admin_visible:
        overlap = admin_visible["a"] & admin_visible["b"]
        if overlap:
            failures.append(
                f"admin users: {len(overlap)} user id(s) visible to both tenants"
            )

    report["courses"] = {key: len(value) for key, value in courses.items()}
    report["evidence"] = {key: len(value) for key, value in evidence.items()}
    report["catalogue"] = {key: len(value) for key, value in catalogue.items()}
    report["admins"] = admin_identities
    report["failures"] = failures
    report["ok"] = not failures

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"tenants: {args.label_a} vs {args.label_b}")
        print("courses: " + ", ".join(f"{k}={v}" for k, v in report["courses"].items()))
        print("evidence: " + ", ".join(f"{k}={v}" for k, v in report["evidence"].items()))
        print("catalogue: " + ", ".join(f"{k}={v}" for k, v in report["catalogue"].items()))
        if failures:
            print("FAILED:")
            for failure in failures:
                print(f"  - {failure}")
        else:
            print("PASSED: no cross-tenant API leakage detected")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
