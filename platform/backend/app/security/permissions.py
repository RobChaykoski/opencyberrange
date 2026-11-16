"""Permission catalog and role grants, loaded from ``permissions.yaml``.

The YAML file is authoritative so a release review can diff one readable file.
It records each permission's description, category, sensitivity, scope, whether
it is read-only, and whether it is eligible for break-glass access. Role grants
live here too; the database tables in :mod:`app.models.security` are seeded from
this file and can then be adjusted by an administrator.

This remains the PBAC seam for the platform: routers call :func:`authorize` with
a permission and, where relevant, a resource owner, course scope, tenant, or
explicit share.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

_CATALOG_PATH = Path(__file__).with_name("permissions.yaml")
with _CATALOG_PATH.open("r", encoding="utf-8") as handle:
    _DOCUMENT = yaml.safe_load(handle) or {}

_PERMISSIONS: dict[str, dict] = _DOCUMENT.get("permissions") or {}
_ROLES: dict[str, dict] = _DOCUMENT.get("roles") or {}

PERMISSION_CATALOG: dict[str, str] = {
    key: str(meta.get("description") or key) for key, meta in _PERMISSIONS.items()
}
PERMISSION_META: dict[str, dict] = dict(_PERMISSIONS)

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    role: frozenset(str(item) for item in (meta.get("permissions") or []))
    for role, meta in _ROLES.items()
}
ROLE_META: dict[str, dict] = dict(_ROLES)
SEEDED_ROLES = tuple(ROLE_PERMISSIONS)

READ_ONLY_PERMISSIONS = frozenset(
    key for key, meta in _PERMISSIONS.items() if meta.get("read_only")
)
SELF_PERMISSIONS = frozenset(
    key for key, meta in _PERMISSIONS.items() if meta.get("scope") == "self"
)
SHARED_PERMISSIONS = frozenset(
    key for key, meta in _PERMISSIONS.items() if meta.get("scope") == "shared"
)
SCOPED_PERMISSIONS = frozenset(
    key for key, meta in _PERMISSIONS.items() if meta.get("scope") == "course"
)
SENSITIVE_PRIVATE_PERMISSIONS = frozenset(
    key for key, meta in _PERMISSIONS.items() if meta.get("sensitivity") == "restricted"
)
BREAK_GLASS_PERMISSIONS = frozenset(
    key for key, meta in _PERMISSIONS.items() if meta.get("break_glass")
)
HIGH_SENSITIVITY_PERMISSIONS = frozenset(
    key
    for key, meta in _PERMISSIONS.items()
    if meta.get("sensitivity") in {"high", "critical", "restricted"}
)


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    permission: str
    reason: str
    role: str
    scope: dict = field(default_factory=dict)
    source: str = "role"
    break_glass_id: int | None = None
    tenant_id: str | None = None


def permissions_for_role(role: str) -> frozenset[str]:
    return ROLE_PERMISSIONS.get((role or "student").strip().lower(), frozenset())


def permission_meta(permission: str) -> dict:
    return PERMISSION_META.get(permission, {})


def export_permission_for_rank(rank: int) -> str:
    """Map a label rank to the atomic export permission it requires."""
    if rank <= 0:
        return "export.public"
    if rank == 1:
        return "export.internal"
    if rank == 2:
        return "export.confidential"
    return "export.restricted"


def validate_catalog() -> list[str]:
    """Return catalog problems. Startup and tests call this before serving."""
    problems: list[str] = []
    for role, granted in ROLE_PERMISSIONS.items():
        unknown = granted - set(PERMISSION_CATALOG)
        if unknown:
            problems.append(f"role {role} grants unknown permissions: {sorted(unknown)}")
    for role, meta in ROLE_META.items():
        if role not in ROLE_PERMISSIONS:
            problems.append(f"role {role} has metadata but no permission list")
        if not meta.get("label"):
            problems.append(f"role {role} has no label")
    restricted = ROLE_PERMISSIONS.get("admin", frozenset()) & SENSITIVE_PRIVATE_PERMISSIONS
    if restricted:
        problems.append(f"admin must not receive private permissions: {sorted(restricted)}")
    for permission in PERMISSION_CATALOG:
        meta = permission_meta(permission)
        if meta.get("sensitivity") not in {"low", "medium", "high", "critical", "restricted"}:
            problems.append(f"permission {permission} has no valid sensitivity")
        if meta.get("scope") not in {"self", "shared", "course", "global"}:
            problems.append(f"permission {permission} has no valid scope")
        # Private permissions are deliberately ungranted: they require an
        # owner, an explicit share, or a break-glass grant.
        if permission in SENSITIVE_PRIVATE_PERMISSIONS:
            continue
        if not any(permission in granted for granted in ROLE_PERMISSIONS.values()):
            problems.append(f"permission {permission} is granted to no role")
    return problems


# Fail at import time rather than serving a half-reviewed catalog. The message
# names the exact drift so a release review can fix it before deployment.
_PROBLEMS = validate_catalog()
if _PROBLEMS:
    raise RuntimeError("permission catalog invalid: " + "; ".join(_PROBLEMS))
