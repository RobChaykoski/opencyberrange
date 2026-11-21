"""Unit tests for the sign-in and registration allow/deny policy."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services import network_access


class _Query:
    def __init__(self, rows):
        self._rows = rows

    def filter(self, *_args, **_kwargs):
        return self

    def all(self):
        return self._rows


class _Session:
    def __init__(self, rows):
        self._rows = rows

    def query(self, _model):
        return _Query(self._rows)


def _rule(action, kind, value, rule_id=1):
    return SimpleNamespace(
        id=rule_id,
        action=action,
        kind=kind,
        value=value,
        expires_at=None,
    )


def test_normalize_ip_and_network():
    assert network_access.normalize_value("ip", " 203.0.113.5 ") == "203.0.113.5"
    assert network_access.normalize_value("network", "203.0.113.7/24") == "203.0.113.0/24"


def test_normalize_domain_strips_at_and_wildcard():
    assert network_access.normalize_value("domain", "@Example.EDU.") == "example.edu"
    assert network_access.normalize_value("domain", "*.lab.example.edu") == "lab.example.edu"


def test_normalize_rejects_bad_values():
    with pytest.raises(ValueError):
        network_access.normalize_value("ip", "203.0.113.0/24")
    with pytest.raises(ValueError):
        network_access.normalize_value("network", "not-a-network")
    with pytest.raises(ValueError):
        network_access.normalize_value("domain", "https://example.edu")


def test_deny_rule_wins():
    session = _Session([_rule("deny", "network", "10.0.0.0/8")])
    decision = network_access.evaluate_ip(session, "access", "10.1.2.3")
    assert decision.allowed is False
    assert decision.reason == "ip_denied"


def test_allow_rule_narrows_only_when_present():
    open_session = _Session([])
    assert network_access.evaluate_ip(open_session, "access", "198.51.100.4").allowed

    session = _Session([_rule("allow", "network", "203.0.113.0/24")])
    assert network_access.evaluate_ip(session, "access", "203.0.113.9").allowed
    denied = network_access.evaluate_ip(session, "access", "198.51.100.4")
    assert denied.allowed is False
    assert denied.reason == "ip_not_allowed"


def test_domain_allow_matches_subdomains():
    session = _Session([_rule("allow", "domain", "example.edu")])
    assert network_access.evaluate_domain(session, "registration", "a@example.edu").allowed
    assert network_access.evaluate_domain(session, "registration", "a@lab.example.edu").allowed
    assert not network_access.evaluate_domain(session, "registration", "a@example.com").allowed


def test_domain_deny_wins_over_allow():
    session = _Session(
        [
            _rule("allow", "domain", "example.edu", 1),
            _rule("deny", "domain", "blocked.example.edu", 2),
        ]
    )
    decision = network_access.evaluate_domain(session, "access", "student@blocked.example.edu")
    assert decision.allowed is False
    assert decision.reason == "domain_denied"
    assert decision.rule_id == 2


def test_ip_then_domain_are_independent_dimensions():
    session = _Session(
        [
            _rule("allow", "network", "203.0.113.0/24", 1),
            _rule("allow", "domain", "example.edu", 2),
        ]
    )
    assert network_access.check(session, "access", ip_address="203.0.113.9", email="a@example.edu").allowed
    assert not network_access.check(session, "access", ip_address="203.0.113.9", email="a@example.com").allowed
    assert not network_access.check(session, "access", ip_address="198.51.100.4", email="a@example.edu").allowed


def test_email_domain_helper():
    assert network_access.email_domain("Student@Example.EDU") == "example.edu"
    assert network_access.email_domain("not-an-email") == ""
    assert network_access.email_domain(None) == ""
