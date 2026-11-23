"""Metadata-driven policy context gate for exports."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.config import settings
from app.services import policy_context


def _user(role="instructor"):
    return SimpleNamespace(
        id=42,
        role=role,
        institution_id="swocts",
        organization="Trailline",
    )


class _Response:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def raise_for_status(self):
        if self.status >= 400:
            raise RuntimeError(f"HTTP {self.status}")

    def json(self):
        return self.payload


def test_context_disabled_is_a_noop(monkeypatch):
    monkeypatch.setattr(settings, "POLICY_CONTEXT_URL", "")
    decision = policy_context.enforce_export(
        _user(), resource_id="reports:instructor:all"
    )
    assert decision["decision"] == "allow"
    assert decision["skipped"] is True


def test_deny_blocks_the_export(monkeypatch):
    monkeypatch.setattr(settings, "POLICY_CONTEXT_URL", "http://context")
    monkeypatch.setattr(
        policy_context.requests,
        "post",
        lambda *args, **kwargs: _Response(
            {"decision": "deny", "reason": "Restricted", "allow": False}
        ),
    )
    with pytest.raises(HTTPException) as error:
        policy_context.enforce_export(_user(), resource_id="reports:instructor:all")
    assert error.value.status_code == 403
    assert error.value.headers["X-Policy-Decision"] == "deny"


def test_require_approval_blocks_the_export(monkeypatch):
    monkeypatch.setattr(settings, "POLICY_CONTEXT_URL", "http://context")
    monkeypatch.setattr(
        policy_context.requests,
        "post",
        lambda *args, **kwargs: _Response(
            {
                "decision": "require_approval",
                "reason": "PIPEDA approval required",
                "allow": False,
            }
        ),
    )
    with pytest.raises(HTTPException) as error:
        policy_context.enforce_export(_user(), resource_id="reports:instructor:all")
    assert error.value.status_code == 403
    assert error.value.headers["X-Policy-Decision"] == "require_approval"


def test_allow_passes(monkeypatch):
    monkeypatch.setattr(settings, "POLICY_CONTEXT_URL", "http://context")
    monkeypatch.setattr(
        policy_context.requests,
        "post",
        lambda *args, **kwargs: _Response({"decision": "allow", "allow": True}),
    )
    decision = policy_context.enforce_export(
        _user(), resource_id="reports:instructor:all"
    )
    assert decision["decision"] == "allow"


def test_unavailable_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "POLICY_CONTEXT_URL", "http://context")
    monkeypatch.setattr(settings, "POLICY_CONTEXT_FAIL_CLOSED", True)

    def fail(*args, **kwargs):
        raise RuntimeError("connection refused")

    monkeypatch.setattr(policy_context.requests, "post", fail)
    with pytest.raises(HTTPException) as error:
        policy_context.enforce_export(_user(), resource_id="reports:instructor:all")
    assert error.value.status_code == 403


def test_unavailable_can_fail_open(monkeypatch):
    monkeypatch.setattr(settings, "POLICY_CONTEXT_URL", "http://context")
    monkeypatch.setattr(settings, "POLICY_CONTEXT_FAIL_CLOSED", False)

    def fail(*args, **kwargs):
        raise RuntimeError("connection refused")

    monkeypatch.setattr(policy_context.requests, "post", fail)
    decision = policy_context.enforce_export(
        _user(), resource_id="reports:instructor:all"
    )
    assert decision["decision"] == "allow"
    assert decision["unavailable"] is True
