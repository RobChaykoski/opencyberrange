"""Every protected API route must declare an auth/permission dependency."""

from __future__ import annotations

from app.main import app
from app.security.route_audit import audit_routes


def test_protected_routes_all_have_an_authorization_dependency():
    report = audit_routes(app)
    assert report["protected"] > 50
    assert report["missing"] == []
