"""The OWASP validation baseline resolves to real controls, tests, and labs."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from app.config import settings
from app.main import app
from app.security.route_audit import _AUTH_CALLS, _dependency_calls, _iter_routes, audit_routes

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "platform/backend/app/data/owasp-security-baseline.yaml"
LABS = ROOT / "platform/labs"
SLUG_RE = re.compile(r"^[a-z]+(?:-[a-z]+)*-(?:\d+-\d+|midterm-\d+|final-\d+)-[a-z0-9-]+$")
STATUSES = {"covered", "partial", "gap"}
EXPECTED = {
    "owasp-api-top10-2023": [f"API{index}" for index in range(1, 11)],
    "owasp-top10-2025": [f"A{index:02d}" for index in range(1, 11)],
    "owasp-agentic-skills-top10": [f"AST{index:02d}" for index in range(1, 11)],
}
PUBLIC_OBJECT_PREFIXES = (
    "/api/exercises/verify/",
    "/api/competitions/public/",
    "/api/auth/sso/",
    "/api/badges/",
    "/api/public/",
)


def _baseline() -> dict:
    return yaml.safe_load(BASELINE.read_text(encoding="utf-8")) or {}


def test_standards_and_categories_are_complete():
    document = _baseline()
    standards = document.get("standards") or []
    assert [item["id"] for item in standards] == list(EXPECTED)
    for standard in standards:
        assert standard["title"].strip()
        assert standard["licence"].strip()
        assert standard["attribution"].strip()
        categories = standard.get("categories") or []
        assert [item["id"] for item in categories] == EXPECTED[standard["id"]]
        for category in categories:
            assert category["title"].strip()
            assert category["status"] in STATUSES, (standard["id"], category["id"])
            assert category["controls"], (standard["id"], category["id"])
            assert category["checks"], (standard["id"], category["id"])
            assert category.get("note", "").strip(), (standard["id"], category["id"])
            for check in category["checks"]:
                assert (ROOT / check).exists(), (standard["id"], category["id"], check)


def test_every_lab_is_planned_and_evidenced():
    document = _baseline()
    seen: set[str] = set()
    existing = {path.parent.name for path in LABS.rglob("lab.yaml")}
    for standard in document["standards"]:
        categories = {item["id"] for item in standard["categories"]}
        labs = standard.get("labs") or []
        assert len(labs) == 10, standard["id"]
        for lab in labs:
            assert lab["category"] in categories, (standard["id"], lab["id"])
            assert SLUG_RE.match(lab["slug"]), (standard["id"], lab["id"], lab["slug"])
            assert lab["slug"] not in seen, lab["slug"]
            seen.add(lab["slug"])
            assert lab["slug"] not in existing, f"lab already exists: {lab['slug']}"
            assert lab["level"] in {"beginner", "intermediate", "advanced"}
            assert lab["minutes"] > 0
            assert lab["objectives"], lab["id"]
            assert lab["evidence"], lab["id"]
            assert lab["fix"].strip(), lab["id"]


def test_protected_routes_keep_authorization_dependencies():
    report = audit_routes(app)
    assert report["protected"] > 50
    assert report["missing"] == []


def test_object_id_routes_keep_an_auth_or_permission_dependency():
    missing = []
    for route in _iter_routes(app.routes):
        path = getattr(route, "path", "")
        if not path.startswith("/api/"):
            continue
        if any(path.startswith(prefix) for prefix in PUBLIC_OBJECT_PREFIXES):
            continue
        if "_id}" not in path and "_id:" not in path:
            continue
        names = _dependency_calls(route.dependant)
        if not (names & _AUTH_CALLS):
            missing.append((path, sorted(names)))
    assert missing == []


def test_cors_never_combines_wildcard_with_credentials():
    origins = [item.strip() for item in settings.CORS_ORIGINS.split(",") if item.strip()]
    assert origins
    assert "*" not in origins
    main = (ROOT / "platform/backend/app/main.py").read_text(encoding="utf-8")
    assert "allow_credentials=True" in main
    assert "allow_origins=cors_origins" in main


def test_sensitive_routers_keep_rate_limits_and_docs_gating():
    auth = (ROOT / "platform/backend/app/routers/auth.py").read_text(encoding="utf-8")
    admin = (ROOT / "platform/backend/app/routers/admin.py").read_text(encoding="utf-8")
    assert auth.count("@limiter.limit(") >= 8
    assert admin.count("@limiter.limit(") >= 10
    main = (ROOT / "platform/backend/app/main.py").read_text(encoding="utf-8")
    assert "_DOCS_PATHS" in main
    assert "enable_api_docs" in main
    assert "ENABLE_API_DOCS" in main


def test_security_headers_and_supply_chain_evidence_exist():
    snippet = (ROOT / "platform/frontend/security-headers.conf").read_text(encoding="utf-8")
    assert "Content-Security-Policy" in snippet
    assert "frame-src" in snippet
    assert (ROOT / "supply-chain.lock.json").is_file()
    assert (ROOT / "docs/OWASP-SECURITY-BASELINE.md").is_file()
    assert (ROOT / "docs/API-SECURITY-LABS.md").is_file()
    assert (ROOT / "docs/OWASP-TOP10-LABS.md").is_file()
    assert (ROOT / "docs/AI-SECURITY-AGENTIC-LABS.md").is_file()
