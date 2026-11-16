"""Compose security invariants for the production profile."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
PROD = REPO / "platform" / "docker-compose.prod.yml"


def _compose():
    return yaml.safe_load(PROD.read_text(encoding="utf-8")) or {}


def test_postgres_is_not_published_to_the_host():
    services = _compose().get("services", {})
    assert "db" in services
    # A database on a host port defeats the private Compose network and is a
    # common internet-exposure finding. Only the backend needs to reach it.
    assert "ports" not in services["db"]
    assert services["db"].get("network_mode") != "host"


def test_production_requires_a_separate_report_signing_key():
    services = _compose().get("services", {})
    backend_env = services["backend"].get("environment", {})
    assert backend_env.get("ENVIRONMENT") == "production"
    assert "REPORT_SIGNING_KEY" in backend_env
