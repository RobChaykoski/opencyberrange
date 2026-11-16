"""Build the reviewed RBAC/PBAC matrix from the live RBAC tables.

The matrix is deliberately read-only. It shows the effective role grants (what
an administrator has approved in the database) next to the policy attributes
(scope, sensitivity, read-only, break-glass, tenant boundary) that the
Authorization Service evaluates at request time.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.security.policy_rules import POLICY_RULES
from app.services import rbac


def _counts(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_matrix(db: Session, *, include_timestamp: bool = True) -> dict:
    roles = rbac.role_catalog(db)
    permissions = rbac.permission_catalog(db)
    role_keys = [role["key"] for role in roles]
    grants = {
        role["key"]: set(role.get("permissions") or []) for role in roles
    }

    rows = []
    for permission in permissions:
        key = permission["key"]
        granted_to = [role_key for role_key in role_keys if key in grants[role_key]]
        rows.append(
            {
                **permission,
                "granted_to": granted_to,
                "roles": {role_key: key in grants[role_key] for role_key in role_keys},
            }
        )

    summary = {
        "roles": len(roles),
        "permissions": len(rows),
        "restricted": sum(1 for row in rows if row["sensitivity"] == "restricted"),
        "break_glass": sum(1 for row in rows if row["break_glass"]),
        "read_only": sum(1 for row in rows if row["read_only"]),
        "ungranted": [row["key"] for row in rows if not row["granted_to"]],
        "scopes": _counts([row["scope"] for row in rows]),
        "sensitivities": _counts([row["sensitivity"] for row in rows]),
        "categories": _counts([row["category"] for row in rows]),
        "tenant_scopes": _counts([role["tenant_scope"] for role in roles]),
    }

    result = {
        "roles": roles,
        "permissions": rows,
        "summary": summary,
        "policy_rules": list(POLICY_RULES),
    }
    if include_timestamp:
        result["generated_at"] = datetime.now(timezone.utc).isoformat()
    return result
