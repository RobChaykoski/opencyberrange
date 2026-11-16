"""Object-identifier route inventory.

Every `/api` route with an object id must at least authenticate and establish
capability at the route boundary. Resource ownership, course scope, and tenant
scope are then enforced by the route policy (covered by the runtime IDOR
matrix).
"""

from __future__ import annotations

from app.main import app
from app.security.route_audit import _AUTH_CALLS, _dependency_calls, _iter_routes

_OBJECT_PARAM_NAMES = (
    "_id}",
    "_id:",
)


_PUBLIC_OBJECT_PREFIXES = (
    "/api/exercises/verify/",
    "/api/competitions/public/",
    "/api/auth/sso/",
    "/api/badges/",
    "/api/public/",
)


def _object_id_routes():
    for route in _iter_routes(app.routes):
        path = getattr(route, "path", "")
        if not path.startswith("/api/"):
            continue
        if any(path.startswith(prefix) for prefix in _PUBLIC_OBJECT_PREFIXES):
            continue
        if any(marker in path for marker in _OBJECT_PARAM_NAMES):
            yield route


def test_every_object_id_route_has_an_auth_or_permission_dependency():
    missing = []
    for route in _object_id_routes():
        names = _dependency_calls(route.dependant)
        if not (names & _AUTH_CALLS):
            missing.append((route.path, sorted(names)))
    assert missing == []


def test_high_risk_object_families_are_inventoried():
    prefixes = {
        "/api/rangebox/",
        "/api/labs/vpn-config",
        "/api/profile/",
        "/api/consent/",
        "/api/courses/",
        "/api/analytics/",
        "/api/competitions/",
        "/api/auth/export",
    }
    seen = {getattr(route, "path", "") for route in _iter_routes(app.routes)}
    for prefix in prefixes:
        assert any(
            path == prefix or path.startswith(prefix) for path in seen
        ), f"no route found for high-risk family {prefix}"
