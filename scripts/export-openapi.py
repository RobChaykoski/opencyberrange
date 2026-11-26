#!/usr/bin/env python3
"""Export the live FastAPI OpenAPI schema and a readable capability index.

The output is written to ``docs/_project_overview/`` so the architecture pack
has a machine-readable API contract and a human-readable inventory. The script
uses placeholder settings and never needs a live database or operator secrets.

Usage:
    python scripts/export-openapi.py
    python scripts/export-openapi.py --check
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "platform" / "backend"
OUT_DIR = ROOT / "docs" / "_project_overview"
SCHEMA_OUT = OUT_DIR / "openapi.json"
CAPABILITIES_OUT = OUT_DIR / "API-CAPABILITIES.md"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

os.environ.setdefault("DATABASE_URL", "postgresql://ocr:ocr@127.0.0.1:5432/ocr")
os.environ.setdefault("JWT_SECRET", "openapi-export-" + "x" * 60)
os.environ.setdefault("SETUP_TOKEN", "openapi-export-" + "y" * 60)
os.environ.setdefault("REPORT_SIGNING_KEY", "openapi-export-" + "z" * 60)
os.environ.setdefault("LABS_HOST_PATH", str(ROOT / "platform" / "labs"))
os.environ.setdefault("CORS_ORIGINS", "https://localhost")
os.environ.setdefault(
    "WG_ENCRYPTION_KEY",
    "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
)

from app.main import app  # noqa: E402
from app.version import APP_VERSION, RELEASE_NAME  # noqa: E402

METHODS = ("get", "post", "put", "patch", "delete", "head", "options")
WEBSOCKET_SURFACES = [
    ("WS", "/api/rangebox/{session_id}/vnc", "Student RangeBox VNC proxy; short-lived WebSocket ticket in the query string."),
    ("WS", "/api/rangebox/standalone/vnc", "Standalone RangeBox VNC proxy; short-lived WebSocket ticket in the query string."),
    ("WS", "/api/rangebox/admin/{user_id}/{session_id}/vnc", "Admin View-As RangeBox VNC proxy; read-only."),
]


def _safe_summary(operation: dict) -> str:
    text = str(operation.get("summary") or operation.get("operationId") or "").strip()
    return text.replace("|", "\\|") or "-"


def _security_label(operation: dict, global_security: list[dict]) -> str:
    security = operation.get("security")
    if security is None:
        security = global_security
    if not security:
        return "public / none"
    labels = []
    for requirement in security:
        if not isinstance(requirement, dict):
            continue
        labels.extend(str(key) for key in requirement)
    return ", ".join(labels) if labels else "declared"


def build_markdown(schema: dict) -> str:
    paths = schema.get("paths") or {}
    components = schema.get("components") or {}
    security_schemes = components.get("securitySchemes") or {}
    global_security = schema.get("security") or []
    rows_by_tag: dict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
    method_counts = Counter()
    total = 0

    for path, methods in sorted(paths.items()):
        for method, operation in sorted(methods.items()):
            if method.lower() not in METHODS:
                continue
            if not isinstance(operation, dict):
                continue
            total += 1
            method_counts[method.upper()] += 1
            tags = operation.get("tags") or ["General"]
            tag = str(tags[0])
            rows_by_tag[tag].append(
                (
                    method.upper(),
                    path,
                    _safe_summary(operation),
                    _security_label(operation, global_security),
                )
            )

    endpoint_rows = "\n".join(
        f"| {method} | {path} | {summary} | {security} |"
        for method, path, summary, security in sorted(
            (row for rows in rows_by_tag.values() for row in rows),
            key=lambda row: (row[1], row[0]),
        )
    )

    security_rows = "\n".join(
        f"| `{name}` | {scheme.get('type', '-')} | {scheme.get('scheme', scheme.get('bearerFormat', '-'))} |"
        for name, scheme in sorted(security_schemes.items())
    ) or "| - | - | - |"

    tag_sections = []
    for tag in sorted(rows_by_tag):
        tag_sections.append(f"### {tag}")
        tag_sections.append("")
        tag_sections.append("| Method | Path | Summary | Security |")
        tag_sections.append("|---|---|---|---|")
        for method, path, summary, security in sorted(
            rows_by_tag[tag], key=lambda row: (row[1], row[0])
        ):
            tag_sections.append(f"| {method} | `{path}` | {summary} | {security} |")
        tag_sections.append("")

    ws_rows = "\n".join(
        f"| {method} | `{path}` | {note} |" for method, path, note in WEBSOCKET_SURFACES
    )

    tag_block = "\n".join(tag_sections)

    return f"""# API capabilities

Generated from the live FastAPI application on {datetime.now(UTC).isoformat(timespec="seconds")}.

| Item | Value |
|---|---|
| Product | {RELEASE_NAME} |
| Platform version | `{APP_VERSION}` |
| OpenAPI version | `{schema.get('openapi', 'unknown')}` |
| API title | {schema.get('info', {}).get('title', 'unknown')} |
| API version | `{schema.get('info', {}).get('version', 'unknown')}` |
| Paths | {len(paths)} |
| Operations | {total} |
| Methods | {', '.join(f'{key} {value}' for key, value in sorted(method_counts.items()))} |

The machine-readable contract is [`openapi.json`](openapi.json). It follows the
OpenAPI specification and can be imported into Swagger UI, Redoc, Postman,
Insomnia, or an API gateway. The application serves the same schema at
`/openapi.json` when the API is running.

## Authentication and exposure

The API is same-origin behind nginx at `/api`. Browser calls use the SPA's
Bearer token; the wiki subrequests use the HttpOnly `wiki_session` cookie
validated by nginx against `/api/auth/me`. Do not publish a live token or a
real hostname in an exported schema.

| Scheme | Type | Details |
|---|---|---|
{security_rows}

## Serving and exposure

The API is private by default. The machine-readable schema in this folder is the
reviewed offline export; it does not make the live documentation public.

| Surface | Default | Control |
|---|---|---|
| REST API `/api/*` | Available to authenticated callers through nginx | JWT / role and consent checks |
| `/openapi.json` | Hidden | `enable_api_docs` setting; `ENABLE_API_DOCS=true` is an emergency override |
| `/docs` (Swagger UI) | Hidden | Same setting |
| `/redoc` | Hidden | Same setting |
| `/api/health`, `/health`, `/api/version` | Available | Health and release probes |

When enabling the live docs for a review, restrict them at the edge and turn
them off again afterwards. The exported `openapi.json` is the safer artifact to
share with an integrator.

## Capability summary

| Capability | Endpoint families |
|---|---|
| Identity and session | `/api/auth/*`, `/api/identity/*`, `/api/sso/*`, `/api/profile/security/*` |
| Learning catalogue | `/api/exercises/*`, `/api/labs/*`, `/api/curriculum/*`, `/api/courses/*` |
| Lab runtime | `/api/labs/*`, `/api/rangebox/*`, `/api/workbook/*` |
| Assessment and evidence | `/api/quiz/*`, `/api/evidence/*`, `/api/reviews/*`, `/api/competency-reviews/*`, `/api/capstones/*` |
| Learner portfolio | `/api/profile/*`, `/api/portfolio/*`, `/api/journeys/*`, `/api/impact/*`, `/api/recognition/*` |
| Analytics and reporting | `/api/analytics/*`, `/api/reports/*`, `/api/usage/*`, `/api/dashboard/*` |
| Administration | `/api/admin/*`, `/api/settings/*`, `/api/modules/*`, `/api/security-admin/*`, `/api/governance/*` |
| Integrations | `/api/lti/*`, `/api/open-badges/*`, `/api/nice/*` |
| Public/health | `/api/setup/*`, `/api/config/public`, `/api/version`, `/health` |

## Operations by tag

{tag_block}

## WebSocket and streaming surfaces

OpenAPI does not describe WebSocket handshakes. These surfaces are exposed by
the application and are documented here for completeness.

| Method | Path | Purpose |
|---|---|---|
{ws_rows}

## Full operation index

| Method | Path | Summary | Security |
|---|---|---|---|
{endpoint_rows}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if the checked-in export differs")
    args = parser.parse_args()

    schema = app.openapi()
    schema_text = json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    markdown_text = build_markdown(schema)

    if args.check:
        current_schema = SCHEMA_OUT.read_text(encoding="utf-8") if SCHEMA_OUT.exists() else ""
        current_markdown = (
            CAPABILITIES_OUT.read_text(encoding="utf-8") if CAPABILITIES_OUT.exists() else ""
        )
        if current_schema != schema_text:
            print("FAIL: openapi.json is stale; run scripts/export-openapi.py")
            return 1
        # Generated timestamp changes on every run; compare the body after it.
        current_body = current_markdown.split("Generated from the live FastAPI application on", 1)[-1].split("\n", 1)[-1]
        new_body = markdown_text.split("Generated from the live FastAPI application on", 1)[-1].split("\n", 1)[-1]
        if current_body != new_body:
            print("FAIL: API-CAPABILITIES.md is stale; run scripts/export-openapi.py")
            return 1
        print("OK: OpenAPI export and capability index are current.")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCHEMA_OUT.write_text(schema_text, encoding="utf-8")
    CAPABILITIES_OUT.write_text(markdown_text, encoding="utf-8")
    print(f"wrote {SCHEMA_OUT.relative_to(ROOT)}")
    print(f"wrote {CAPABILITIES_OUT.relative_to(ROOT)}")
    print(f"paths={len(schema.get('paths') or {})} operations={sum(1 for methods in (schema.get('paths') or {}).values() for method in methods if method in METHODS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
