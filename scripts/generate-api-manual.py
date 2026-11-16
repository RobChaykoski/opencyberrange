#!/usr/bin/env python3
"""Generate the complete API reference page for the user manual.

The page is generated from the live FastAPI OpenAPI schema so it cannot drift
from the routes, request models, or response models. It deliberately contains
no real credentials; every example uses placeholders.

Usage:
    python scripts/generate-api-manual.py
    python scripts/generate-api-manual.py --check
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "platform" / "backend"
OUTPUT = ROOT / "Manual-Lite/11_API_Reference/index.md"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Import the application without requiring a live database or operator secrets.
# The settings are placeholders; this script only reads the OpenAPI schema.
os.environ.setdefault("DATABASE_URL", "postgresql://ocr:ocr@127.0.0.1:5432/ocr")
os.environ.setdefault("JWT_SECRET", "api-manual-" + "x" * 60)
os.environ.setdefault("SETUP_TOKEN", "api-manual-" + "y" * 60)
os.environ.setdefault("REPORT_SIGNING_KEY", "api-manual-" + "z" * 60)
os.environ.setdefault("LABS_HOST_PATH", str(ROOT / "platform" / "labs"))
os.environ.setdefault("CORS_ORIGINS", "https://localhost")
os.environ.setdefault(
    "WG_ENCRYPTION_KEY",
    "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
)

from app.main import app  # noqa: E402


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "general"


def _ref_name(schema: dict[str, Any]) -> str:
    ref = str(schema.get("$ref") or "")
    return ref.rsplit("/", 1)[-1] if ref else ""


def _resolve(schema: dict[str, Any], components: dict[str, Any]) -> dict[str, Any]:
    name = _ref_name(schema)
    if name:
        return components.get(name) or {}
    return schema


def _type_name(schema: dict[str, Any], components: dict[str, Any], depth: int = 0) -> str:
    if not isinstance(schema, dict) or not schema or depth > 4:
        return "any"
    if "$ref" in schema:
        return f"`{_ref_name(schema)}`"
    if "oneOf" in schema:
        return " or ".join(_type_name(item, components, depth + 1) for item in schema["oneOf"])
    if "anyOf" in schema:
        return " or ".join(_type_name(item, components, depth + 1) for item in schema["anyOf"])
    if "allOf" in schema:
        return " + ".join(_type_name(item, components, depth + 1) for item in schema["allOf"])
    if "enum" in schema:
        return " | ".join(f"`{value}`" for value in schema["enum"])
    kind = schema.get("type") or "any"
    if kind == "array":
        return f"array[{_type_name(schema.get('items') or {}, components, depth + 1)}]"
    if kind == "object" and isinstance(schema.get("additionalProperties"), dict):
        return f"map[string, {_type_name(schema['additionalProperties'], components, depth + 1)}]"
    return str(kind)


def _description(value: Any) -> str:
    text = str(value or "").strip().replace("\n", " ")
    return text.replace("|", "\\|")


def _properties_table(schema: dict[str, Any], components: dict[str, Any]) -> list[str]:
    schema = _resolve(schema, components)
    properties = schema.get("properties") or {}
    required = set(schema.get("required") or [])
    if not properties:
        return []
    rows = [
        "| Field | Type | Required | Description |",
        "|---|---|---|---|",
    ]
    for name, item in properties.items():
        rows.append(
            f"| `{name}` | {_type_name(item, components)} | "
            f"{'yes' if name in required else 'no'} | {_description(item.get('description'))} |"
        )
    return rows


def _schema_block(
    label: str,
    schema: dict[str, Any],
    components: dict[str, Any],
) -> list[str]:
    if not schema:
        return []
    lines = [f"**{label}:** {_type_name(schema, components)}", ""]
    table = _properties_table(schema, components)
    if table:
        lines.extend(table)
        lines.append("")
    return lines


def _operation_security(
    operation: dict[str, Any],
    global_security: list[dict[str, Any]],
) -> str:
    security = operation.get("security")
    if security is None:
        security = global_security
    if not security:
        return "Public"
    names: list[str] = []
    for requirement in security:
        names.extend(requirement.keys())
    return ", ".join(sorted(set(names))) or "Public"


def _parameter_rows(operation: dict[str, Any]) -> list[str]:
    parameters = operation.get("parameters") or []
    if not parameters:
        return []
    rows = [
        "| Parameter | In | Type | Required | Description |",
        "|---|---|---|---|---|",
    ]
    for parameter in parameters:
        schema = parameter.get("schema") or {}
        rows.append(
            f"| `{parameter.get('name')}` | {parameter.get('in')} | "
            f"{_type_name(schema, {})} | {'yes' if parameter.get('required') else 'no'} | "
            f"{_description(parameter.get('description'))} |"
        )
    return rows


def _request_block(operation: dict[str, Any], components: dict[str, Any]) -> list[str]:
    body = operation.get("requestBody") or {}
    content = body.get("content") or {}
    if not content:
        return []
    lines: list[str] = []
    for media_type, item in content.items():
        lines.append(f"**Request body** (`{media_type}`)")
        lines.append("")
        lines.extend(_schema_block("Schema", item.get("schema") or {}, components))
    return lines


def _response_lines(operation: dict[str, Any], components: dict[str, Any]) -> list[str]:
    responses = operation.get("responses") or {}
    if not responses:
        return []
    lines = ["**Responses**", ""]
    for status, response in responses.items():
        description = _description(response.get("description"))
        content = response.get("content") or {}
        schema = next(iter(content.values()), {}).get("schema") if content else {}
        schema_text = f" — {_type_name(schema, components)}" if schema else ""
        lines.append(f"- `{status}`: {description}{schema_text}")
    lines.append("")
    return lines


def _operation_lines(
    method: str,
    path: str,
    operation: dict[str, Any],
    components: dict[str, Any],
    global_security: list[dict[str, Any]],
) -> list[str]:
    lines = [
        f"### `{method.upper()} {path}`",
        "",
        f"**{operation.get('summary') or operation.get('operationId') or 'Endpoint'}**",
        "",
    ]
    if operation.get("description"):
        lines.extend([_description(operation["description"]), ""])
    lines.extend(
        [
            f"**Authentication:** {_operation_security(operation, global_security)}",
            "",
        ]
    )
    if operation.get("deprecated"):
        lines.extend(["!!! warning \"Deprecated\"", "    This endpoint is marked deprecated.", ""])
    parameter_rows = _parameter_rows(operation)
    if parameter_rows:
        lines.extend(["**Parameters**", "", *parameter_rows, ""])
    request = _request_block(operation, components)
    if request:
        lines.extend(request)
    response = _response_lines(operation, components)
    if response:
        lines.extend(response)
    return lines


def build_manual() -> str:
    schema = app.openapi()
    components = (schema.get("components") or {}).get("schemas") or {}
    security_schemes = (schema.get("components") or {}).get("securitySchemes") or {}
    global_security = schema.get("security") or []
    paths = schema.get("paths") or {}

    groups: dict[str, list[tuple[str, str, dict[str, Any]]]] = {}
    index_rows = [
        "| Method | Path | Summary | Authentication |",
        "|---|---|---|---|",
    ]
    for path, methods in sorted(paths.items()):
        for method, operation in sorted(methods.items()):
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            tags = operation.get("tags") or ["General"]
            tag = str(tags[0])
            groups.setdefault(tag, []).append((method, path, operation))
            index_rows.append(
                f"| `{method.upper()}` | `{path}` | {_description(operation.get('summary'))} | "
                f"{_operation_security(operation, global_security)} |"
            )

    lines: list[str] = [
        "# API reference",
        "",
        "This page is generated from the running FastAPI OpenAPI schema. It is the",
        "complete route reference for the platform API. Use the interactive",
        "OpenAPI page only when an administrator has enabled API documentation.",
        "",
        "!!! note \"Generated page\"",
        "    Run `python scripts/generate-api-manual.py` after changing a router or",
        "    schema. The CI check regenerates this page and fails on drift.",
        "",
        "## Base URL and versioning",
        "",
        "The API is served under `/api` on the same origin as the web interface.",
        "The current platform version is available at `GET /api/version`. The",
        "health probe is `GET /health` and does not require authentication.",
        "",
        "## Authentication",
        "",
        "1. `POST /api/auth/login` with form fields `username` and `password`.",
        "2. Store the returned access token and refresh token in the client.",
        "3. Send `Authorization: Bearer <access_token>` on protected requests.",
        "4. Rotate the access token with `POST /api/auth/refresh` before it expires.",
        "5. Re-authenticate for sensitive actions with `POST /api/auth/reauth`.",
        "",
        "An expired or revoked token returns `401`. A valid token without the",
        "required permission returns `403`. Never place a token in a URL, a log,",
        "a screenshot, or a report.",
        "",
        "## Request conventions",
        "",
        "- Send JSON with `Content-Type: application/json` unless the endpoint",
        "  documents a form, multipart, or plain-text body.",
        "- Use `Idempotency-Key` only where the endpoint documents it; do not",
        "  assume every write is idempotent.",
        "- Paginated endpoints use `page` and `per_page` when documented. Respect",
        "  the server cap; do not request an unbounded page.",
        "- Tenant and object scope are enforced on the server. A client-supplied",
        "  `institution_id`, role, or owner field is not trusted.",
        "",
        "## Response conventions",
        "",
        "- Success responses use the documented schema and a `2xx` status.",
        "- Validation failures use `422` with a structured `detail` list.",
        "- Authorization failures use `401` (not signed in) or `403` (not allowed).",
        "- Missing objects use `404`; conflict and state errors use `409`.",
        "- Rate limits use `429`; retry after the documented window.",
        "- Unexpected failures use `500` and must not include a stack trace or secret.",
        "",
        "A typical error body is:",
        "",
        "```json",
        '{"detail": "Not enough permissions"}',
        "```",
        "",
        "A validation error body is:",
        "",
        "```json",
        '{"detail": [{"loc": ["body", "field"], "msg": "field required", "type": "missing"}]}',
        "```",
        "",
        "## Rate limits and sensitive actions",
        "",
        "Authentication, registration, password reset, flag submission, exports,",
        "and administrative changes have stricter limits than ordinary reads.",
        "The exact limit is enforced per route and may use a shared counter across",
        "workers. A `429` means the request was refused, not that the credential",
        "was wrong.",
        "",
        "Sensitive actions may also require re-authentication, a written reason,",
        "or an approval. The response can include `X-Reauth-Required`; the SPA",
        "opens the re-authentication dialog instead of silently retrying.",
        "",
        "## Permissions and data scope",
        "",
        "Authorization is deny-by-default. A route may require a role permission,",
        "an object ownership check, a tenant match, a course enrollment, or an",
        "explicit share. The permission catalogue and matrix are documented in",
        "[RBAC and PBAC](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/RBAC-PBAC.md) "
        "and the admin **Security** tab.",
        "",
        "Data labels and export rules are documented in",
        "[Data labels](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/DATA-LABELS.md). "
        "Private DNA, GPS, and AI data are",
        "owner-only unless an explicit share or break-glass grant exists.",
        "",
        "## OpenAPI and interactive docs",
        "",
        "- `GET /openapi.json` returns the schema used to build this page.",
        "- `GET /docs` and `GET /redoc` are disabled by default.",
        "- An administrator can enable them with the `enable_api_docs` setting or",
        "  the `ENABLE_API_DOCS=true` environment override for emergency debugging.",
        "- The API schema and this manual are informational; they do not grant",
        "  access to a route.",
        "",
        "## Security schemes",
        "",
    ]
    if security_schemes:
        for name, scheme in security_schemes.items():
            lines.append(
                f"- **{name}**: {scheme.get('type', 'unknown')}"
                + (f" ({scheme.get('scheme')})" if scheme.get("scheme") else "")
                + (f" — {_description(scheme.get('description'))}" if scheme.get("description") else "")
            )
    else:
        lines.append("- Bearer JWT, declared by the route dependencies.")
    lines.extend(
        [
            "",
            "## Endpoint index",
            "",
            *index_rows,
            "",
            "## Endpoint details",
            "",
        ]
    )

    for tag in sorted(groups):
        lines.extend([f"## {tag}", ""])
        for method, path, operation in groups[tag]:
            lines.extend(
                _operation_lines(method, path, operation, components, global_security)
            )
    lines.extend(
        [
            "## Data handling",
            "",
            "- Do not send real learner, patient, customer, or institutional data to",
            "  a lab endpoint unless the deployment's data policy explicitly allows it.",
            "- Use synthetic identifiers in examples and test scripts.",
            "- Exports are labelled and audited. Do not remove a label or bypass an",
            "  export reason.",
            "- Report a vulnerability privately to `security@swocts.com`; do not test",
            "  it against another user's data.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the page is stale")
    args = parser.parse_args()
    generated = build_manual()
    if args.check:
        if not OUTPUT.is_file():
            print(f"FAIL: missing {OUTPUT}", file=sys.stderr)
            return 1
        current = OUTPUT.read_text(encoding="utf-8")
        if current != generated:
            print(
                f"FAIL: {OUTPUT} is stale; run python scripts/generate-api-manual.py",
                file=sys.stderr,
            )
            return 1
        print("PASS: API manual matches the OpenAPI schema")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(generated, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT} ({generated.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
