"""Route authorization audit.

A developer can add a router and forget the authorization dependency. This
audit enumerates the compiled FastAPI routes and reports protected prefixes
that have no recognized authentication or permission dependency.

The default is a startup warning because a public route added by an older
release must not take a running platform down during an upgrade. Set
``OCR_AUTHZ_STRICT=1`` or ``authorization_strict_startup=true`` in an enterprise
deployment to refuse startup instead.
"""

from __future__ import annotations

import os


def _iter_routes(routes):
    """Yield effective routes across FastAPI's lazy included-router wrappers."""
    for route in routes or []:
        candidates = getattr(route, "effective_candidates", None)
        if callable(candidates) and hasattr(route, "original_router"):
            yield from _iter_routes(candidates())
            continue
        if hasattr(route, "path") and hasattr(route, "dependant"):
            yield route

_AUTH_CALLS = {
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "get_current_institution_admin_user",
    "get_current_instructor_user",
    "get_current_reporting_user",
    "require_permission",
    "require_allowed",
}

# Routes under these prefixes must have an authorization dependency.
_PROTECTED_PREFIXES = (
    "/api/admin",
    "/api/consent/admin",
    "/api/instructor",
    "/api/reports",
    "/api/audit",
    "/api/profile",
    "/api/dna",
    "/api/cyber-dna",
    "/api/evidence",
    "/api/competencies",
    "/api/workbook-answers",
    "/api/identity",
    "/api/lti",
    "/api/setup",
    "/api/security",
    "/api/nice",
    "/api/governance",
)

# Authentication routes that are intentionally public. Sensitive auth routes
# (sessions, export, delete-account, change-password, MFA, impersonation) are
# deliberately absent and must keep an auth dependency.
_PUBLIC_PREFIXES = (
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/forgot",
    "/api/auth/reset",
    "/api/auth/sso",
    "/api/auth/verify",
    "/api/reports/verify",
    "/api/exercises/verify",
    "/api/badges/public",
    "/api/public",
    "/api/about",
    "/api/version",
    "/api/setup",
    "/api/lti/jwks",
    "/api/lti/login",
    "/api/lti/launch",
)


def _is_public(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in _PUBLIC_PREFIXES)


def _is_protected_scope(path: str) -> bool:
    if _is_public(path):
        return False
    if path.startswith("/api/auth"):
        if _is_public(path):
            return False
        return any(
            token in path
            for token in (
                "/me",
                "/sessions",
                "/export",
                "/delete-account",
                "/change-password",
                "/mfa",
                "/impersonate",
                "/settings",
                "/profile",
            )
        )
    return any(
        path == prefix or path.startswith(prefix + "/")
        for prefix in _PROTECTED_PREFIXES
    )


def _dependency_calls(dependant, seen: set[int] | None = None) -> set[str]:
    seen = seen or set()
    if id(dependant) in seen:
        return set()
    seen.add(id(dependant))
    names: set[str] = set()
    for dependency in getattr(dependant, "dependencies", []) or []:
        call = getattr(dependency, "call", None)
        if call is not None:
            names.add(getattr(call, "__name__", ""))
            if getattr(call, "__permission__", None):
                names.add("require_permission")
        names.update(_dependency_calls(dependency, seen))
    return names


def audit_routes(app) -> dict:
    protected = 0
    missing: list[dict] = []
    for route in _iter_routes(getattr(app, "routes", [])):
        path = route.path
        if not path.startswith("/api/"):
            continue
        if not _is_protected_scope(path):
            continue
        protected += 1
        names = _dependency_calls(route.dependant)
        if names & _AUTH_CALLS:
            continue
        methods = sorted(
            method for method in (route.methods or set()) if method not in {"HEAD", "OPTIONS"}
        )
        missing.append(
            {
                "path": path,
                "methods": methods,
                "name": route.name,
                "dependencies": sorted(name for name in names if name),
            }
        )
    return {"protected": protected, "missing": missing}


def strict_startup_enabled() -> bool:
    if os.environ.get("OCR_AUTHZ_STRICT", "").lower() in {"1", "true", "yes"}:
        return True
    try:
        from app.database import SessionLocal
        from app.services import settings_service

        db = SessionLocal()
        try:
            value = settings_service.get_setting_fresh(
                db, "authorization_strict_startup", "false"
            )
        finally:
            db.close()
        return (value or "").strip().lower() in {"true", "1", "yes", "on"}
    except Exception:
        return False


def raise_for_missing(report: dict) -> None:
    missing = report.get("missing") or []
    if not missing:
        return
    detail = ", ".join(
        f"{'/'.join(item['methods']) or 'GET'} {item['path']}" for item in missing[:20]
    )
    raise RuntimeError(
        "Authorization startup audit failed: "
        f"{len(missing)} protected route(s) have no auth/permission dependency: {detail}"
    )
