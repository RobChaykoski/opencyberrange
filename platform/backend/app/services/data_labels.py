"""Enforceable data-label policy for reports and exports.

The export-label service decides what a file says. This service decides whether
the file may leave the platform. The institution can use the built-in four-level
scheme or supply custom levels, set a region, cap exports by role, block
Restricted material, and mark a level non-exportable.

The policy is advisory unless ``data_label_enforcement_enabled`` is on. Missing
or invalid tokens are left to the route's normal authentication dependency.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.auth import _decode_token, get_user_by_username
from app.models import User
from app.security.permissions import export_permission_for_rank
from app.security.policy import authorize
from app.services import export_labels, settings_service

logger = logging.getLogger(__name__)

TRUTHY = {"true", "1", "yes", "on", "enabled"}
BUILTIN_RANK = {
    key: level["rank"] for key, level in export_labels.BUILTIN_LEVELS.items()
}


@dataclass(frozen=True)
class DataLabelDecision:
    allowed: bool
    enforced: bool
    classification_key: str
    classification: str
    rank: int
    reason: str
    policy: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "enforced": self.enforced,
            "classification": self.classification,
            "classification_key": self.classification_key,
            "rank": self.rank,
            "reason": self.reason,
            "policy": self.policy,
        }


@dataclass(frozen=True)
class DataLabelPolicy:
    levels: dict[str, dict[str, Any]]
    configured_key: str
    labels_enabled: bool
    enforcement: bool
    region: str
    max_export_rank: int
    block_restricted: bool
    region_rules: dict[str, dict[str, Any]]
    role_max_rank: dict[str, int]
    warnings: list[str]


def _setting(db: Session, key: str, default: str = "") -> str:
    return (
        settings_service.get_setting_fresh(db, key, default) or default
    ).strip()


def _truthy(value: str, default: bool = False) -> bool:
    text = (value or "").strip().lower()
    if not text:
        return default
    return text in TRUTHY


def _int_value(value: str, default: int, minimum: int = 0, maximum: int = 100) -> int:
    try:
        return max(minimum, min(maximum, int(value)))
    except (TypeError, ValueError):
        return default


def _json_object(raw: str, label: str, warnings: list[str]) -> dict:
    if not raw:
        return {}
    import json

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        warnings.append(f"{label} is not valid JSON: {exc}")
        return {}
    if not isinstance(parsed, dict):
        warnings.append(f"{label} must be a JSON object.")
        return {}
    return parsed


def _resolve_level(
    levels: dict[str, dict[str, Any]], key: str
) -> dict[str, Any]:
    """Map a built-in or configured key to an effective level.

    A custom scheme may rename or merge levels. If the exact key is absent,
    choose the lowest custom level whose rank covers the built-in rank. This
    prevents a removed/renamed level from silently downgrading an export.
    """
    if key in levels:
        return levels[key]
    wanted = BUILTIN_RANK.get(key)
    ordered = sorted(levels.values(), key=lambda level: level["rank"])
    if wanted is None:
        return ordered[0]
    for level in ordered:
        if level["rank"] >= wanted:
            return level
    return ordered[-1]


def load_policy(db: Session) -> DataLabelPolicy:
    levels, warnings = export_labels.load_levels(db)
    configured = _setting(db, "export_classification", "internal").lower()
    configured_level = _resolve_level(levels, configured)

    region_rules = _json_object(
        _setting(db, "data_label_region_rules"), "Region rules", warnings
    )
    cleaned_regions: dict[str, dict[str, Any]] = {}
    for region, rule in region_rules.items():
        if not isinstance(rule, dict):
            warnings.append(f"Region rule '{region}' must be an object.")
            continue
        cleaned: dict[str, Any] = {}
        if "max_export_rank" in rule:
            cleaned["max_export_rank"] = _int_value(
                str(rule.get("max_export_rank")), 3
            )
        if "block_restricted" in rule:
            cleaned["block_restricted"] = bool(rule.get("block_restricted"))
        cleaned_regions[str(region).strip().upper()] = cleaned

    role_limits = _json_object(
        _setting(db, "data_label_role_max_rank"), "Role limits", warnings
    )
    cleaned_roles: dict[str, int] = {}
    for role, value in role_limits.items():
        cleaned_roles[str(role).strip().lower()] = _int_value(str(value), 3)

    return DataLabelPolicy(
        levels=levels,
        configured_key=configured_level["key"],
        labels_enabled=_truthy(_setting(db, "export_label_enabled", "true"), True),
        enforcement=_truthy(
            _setting(db, "data_label_enforcement_enabled", "false"), False
        ),
        region=_setting(db, "data_label_region").upper(),
        max_export_rank=_int_value(
            _setting(db, "data_label_max_export_rank", "3"), 3
        ),
        block_restricted=_truthy(
            _setting(db, "data_label_block_restricted_exports", "true"), True
        ),
        region_rules=cleaned_regions,
        role_max_rank=cleaned_roles,
        warnings=warnings,
    )


def effective_level(policy: DataLabelPolicy, path: str | None) -> dict[str, Any]:
    configured = _resolve_level(policy.levels, policy.configured_key)
    path_key = export_labels.classification_for_path(path)
    if not path_key:
        return configured
    forced = _resolve_level(policy.levels, path_key)
    return forced if forced["rank"] >= configured["rank"] else configured


def evaluate_export(
    db: Session, user: User | None, path: str
) -> DataLabelDecision:
    policy = load_policy(db)
    level = effective_level(policy, path)
    enforced = policy.enforcement and policy.labels_enabled
    if not enforced:
        return DataLabelDecision(
            allowed=True,
            enforced=False,
            classification_key=level["key"],
            classification=level["label"],
            rank=level["rank"],
            reason=(
                "Data-label enforcement is off."
                if not policy.enforcement
                else "Export labels are disabled; enforcement is inactive."
            ),
            policy="advisory",
        )

    if not level.get("exportable", True):
        return DataLabelDecision(
            allowed=False,
            enforced=True,
            classification_key=level["key"],
            classification=level["label"],
            rank=level["rank"],
            reason="This label is marked non-exportable by the institution.",
            policy="denied",
        )

    if user is None:
        # Let the route's authentication dependency return the correct 401.
        return DataLabelDecision(
            allowed=True,
            enforced=True,
            classification_key=level["key"],
            classification=level["label"],
            rank=level["rank"],
            reason="No authenticated subject; route authentication applies.",
            policy="unauthenticated",
        )

    base_grant = authorize(db, user, "export.data")
    if not base_grant.allowed:
        return DataLabelDecision(
            allowed=False,
            enforced=True,
            classification_key=level["key"],
            classification=level["label"],
            rank=level["rank"],
            reason=base_grant.reason,
            policy="denied",
        )

    label_permission = export_permission_for_rank(level["rank"])
    label_grant = authorize(db, user, label_permission)
    if not label_grant.allowed:
        return DataLabelDecision(
            allowed=False,
            enforced=True,
            classification_key=level["key"],
            classification=level["label"],
            rank=level["rank"],
            reason=label_grant.reason,
            policy="denied",
        )

    role = (getattr(user, "role", "") or "student").strip().lower()
    ceiling = policy.max_export_rank
    if role in policy.role_max_rank:
        ceiling = min(ceiling, policy.role_max_rank[role])

    region_rule = policy.region_rules.get(policy.region, {}) if policy.region else {}
    if "max_export_rank" in region_rule:
        ceiling = min(ceiling, region_rule["max_export_rank"])
    block_restricted = policy.block_restricted or bool(
        region_rule.get("block_restricted", False)
    )

    if level["rank"] > ceiling:
        return DataLabelDecision(
            allowed=False,
            enforced=True,
            classification_key=level["key"],
            classification=level["label"],
            rank=level["rank"],
            reason=(
                f"{level['label']} exports exceed the ceiling for role "
                f"'{role}' in region '{policy.region or 'unspecified'}'."
            ),
            policy="denied",
        )
    if level["key"] == "restricted" and block_restricted:
        return DataLabelDecision(
            allowed=False,
            enforced=True,
            classification_key=level["key"],
            classification=level["label"],
            rank=level["rank"],
            reason="Restricted exports are blocked by policy.",
            policy="denied",
        )

    return DataLabelDecision(
        allowed=True,
        enforced=True,
        classification_key=level["key"],
        classification=level["label"],
        rank=level["rank"],
        reason="Within the institution's export policy.",
        policy="enforced",
    )


def resolve_request_user(request: Request, db: Session) -> User | None:
    header = request.headers.get("authorization") or ""
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    token = token.strip()
    try:
        if token.startswith("ocr_svc_"):
            from app.services.service_identities import resolve_token

            return resolve_token(db, token)
        payload = _decode_token(token, db)
    except HTTPException:
        return None
    user = get_user_by_username(db, username=payload.get("sub"))
    if user is not None:
        from app.services import auth_sessions

        auth_sessions.bind_user(db, user, payload)
    return user


def response_headers(
    decision: DataLabelDecision, path: str
) -> dict[str, str]:
    headers = export_labels.export_response_headers(path)
    if not headers:
        return {}
    headers["X-Data-Policy"] = decision.policy
    if decision.enforced:
        headers["X-Data-Enforcement"] = "enabled"
    return headers


def policy_summary(
    db: Session,
    *,
    role: str | None = None,
    path: str | None = None,
) -> dict[str, Any]:
    policy = load_policy(db)
    levels = [
        {
            "key": level["key"],
            "label": level["label"],
            "rank": level["rank"],
            "exportable": bool(level.get("exportable", True)),
            "handling": level.get("handling"),
        }
        for level in sorted(policy.levels.values(), key=lambda item: item["rank"])
    ]
    path_map = {}
    for prefix, key in export_labels.EXPORT_CLASSIFICATION_PREFIXES:
        path_map[prefix] = _resolve_level(policy.levels, key)["key"]

    sample = None
    if role or path:
        sample = evaluate_export(
            db,
            SimpleNamespace(id=0, role=role or "student"),
            path or "/api/auth/export",
        ).as_dict()

    return {
        "labels_enabled": policy.labels_enabled,
        "enforcement": policy.enforcement,
        "region": policy.region or None,
        "max_export_rank": policy.max_export_rank,
        "block_restricted_exports": policy.block_restricted,
        "role_max_rank": policy.role_max_rank,
        "region_rules": policy.region_rules,
        "default_classification": policy.configured_key,
        "levels": levels,
        "label_permissions": {
            level["key"]: export_permission_for_rank(level["rank"])
            for level in levels
        },
        "path_map": path_map,
        "warnings": policy.warnings,
        "sample_decision": sample,
    }
