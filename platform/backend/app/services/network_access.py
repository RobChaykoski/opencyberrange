"""Allow/deny policy for sign-in and self-service registration.

The rules are intentionally simple to audit:

* A matching deny rule always wins.
* Allow rules narrow a dimension (client IP/network or email domain) only when
  at least one allow rule exists for that dimension. With no allow rules the
  dimension stays open, so turning the feature on is opt-in.
* IP and domain dimensions are independent: an institution can require a known
  network *and* an approved email domain by adding allow rules for both.

Rules are stored in ``network_access_rules`` and scoped to ``access`` (sign-in)
or ``registration`` (self-service account creation).
"""

from __future__ import annotations

import ipaddress
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional

from sqlalchemy.orm import Session

from app.models import NetworkAccessRule

logger = logging.getLogger(__name__)

SCOPES = ("access", "registration")
KINDS = ("ip", "network", "domain")
ACTIONS = ("allow", "deny")

IP_KINDS = ("ip", "network")
DOMAIN_KINDS = ("domain",)

_DOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
_MAX_DOMAIN_LENGTH = 253


@dataclass(frozen=True)
class AccessDecision:
    """The outcome of one policy evaluation."""

    allowed: bool
    reason: str = ""
    rule_id: Optional[int] = None
    rule_value: Optional[str] = None


def normalize_scope(value: str) -> str:
    scope = (value or "").strip().lower()
    if scope not in SCOPES:
        raise ValueError("scope must be access or registration")
    return scope


def normalize_action(value: str) -> str:
    action = (value or "").strip().lower()
    if action not in ACTIONS:
        raise ValueError("action must be allow or deny")
    return action


def normalize_kind(value: str) -> str:
    kind = (value or "").strip().lower()
    if kind not in KINDS:
        raise ValueError("kind must be ip, network, or domain")
    return kind


def normalize_value(kind: str, value: str) -> str:
    """Return the canonical form of an IP, CIDR, or domain rule value."""
    kind = normalize_kind(kind)
    raw = (value or "").strip()
    if not raw:
        raise ValueError("A rule value is required")

    if kind == "ip":
        try:
            return str(ipaddress.ip_address(raw))
        except ValueError as exc:
            raise ValueError("Enter a single IPv4 or IPv6 address") from exc

    if kind == "network":
        try:
            return str(ipaddress.ip_network(raw, strict=False))
        except ValueError as exc:
            raise ValueError("Enter a CIDR network such as 203.0.113.0/24") from exc

    domain = raw.lower()
    if domain.startswith("@"):
        domain = domain[1:]
    if domain.startswith("*."):
        domain = domain[2:]
    domain = domain.rstrip(".")
    if not domain:
        raise ValueError("Enter a domain such as example.edu")
    if len(domain) > _MAX_DOMAIN_LENGTH:
        raise ValueError("Domain is too long")
    if not _DOMAIN_RE.fullmatch(domain):
        raise ValueError("Enter a domain using letters, digits, dots, and hyphens")
    return domain


def email_domain(email: Optional[str]) -> str:
    """Return the lowercase domain portion of an email address."""
    if not email or "@" not in email:
        return ""
    return email.rsplit("@", 1)[1].strip().lower().rstrip(".")


def _is_active(rule: NetworkAccessRule, now: datetime) -> bool:
    expires = rule.expires_at
    if expires is None:
        return True
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return expires > now


def _active_rules(db: Session, scope: str) -> list[NetworkAccessRule]:
    rows = db.query(NetworkAccessRule).filter(NetworkAccessRule.scope == scope).all()
    now = datetime.now(timezone.utc)
    return [row for row in rows if _is_active(row, now)]


@lru_cache(maxsize=2048)
def _parse_address(value: str):
    return ipaddress.ip_address(value)


@lru_cache(maxsize=2048)
def _parse_network(value: str):
    return ipaddress.ip_network(value, strict=False)


def _ip_matches(rule: NetworkAccessRule, address: str) -> bool:
    try:
        candidate = _parse_address(address)
        if rule.kind == "ip":
            return candidate == _parse_address(rule.value)
        if rule.kind == "network":
            return candidate in _parse_network(rule.value)
    except ValueError:
        return False
    return False


def _domain_matches(rule: NetworkAccessRule, domain: str) -> bool:
    if not domain:
        return False
    return domain == rule.value or domain.endswith("." + rule.value)


def _decision(rule: NetworkAccessRule, reason: str) -> AccessDecision:
    return AccessDecision(
        allowed=False,
        reason=reason,
        rule_id=rule.id,
        rule_value=rule.value,
    )


def evaluate_ip(db: Session, scope: str, ip_address: Optional[str]) -> AccessDecision:
    """Evaluate IP and network rules for one scope."""
    scope = normalize_scope(scope)
    rules = [rule for rule in _active_rules(db, scope) if rule.kind in IP_KINDS]
    for rule in rules:
        if rule.action == "deny" and _ip_matches(rule, ip_address or ""):
            return _decision(rule, "ip_denied")

    allows = [rule for rule in rules if rule.action == "allow"]
    if allows and not any(_ip_matches(rule, ip_address or "") for rule in allows):
        return AccessDecision(allowed=False, reason="ip_not_allowed")
    return AccessDecision(allowed=True)


def evaluate_domain(db: Session, scope: str, email: Optional[str]) -> AccessDecision:
    """Evaluate email-domain rules for one scope."""
    scope = normalize_scope(scope)
    rules = [rule for rule in _active_rules(db, scope) if rule.kind in DOMAIN_KINDS]
    if not rules:
        return AccessDecision(allowed=True)

    domain = email_domain(email)
    for rule in rules:
        if rule.action == "deny" and _domain_matches(rule, domain):
            return _decision(rule, "domain_denied")

    allows = [rule for rule in rules if rule.action == "allow"]
    if allows and not any(_domain_matches(rule, domain) for rule in allows):
        return AccessDecision(allowed=False, reason="domain_not_allowed")
    return AccessDecision(allowed=True)


def check(
    db: Session,
    scope: str,
    *,
    ip_address: Optional[str] = None,
    email: Optional[str] = None,
) -> AccessDecision:
    """Evaluate both dimensions for a request."""
    ip_decision = evaluate_ip(db, scope, ip_address)
    if not ip_decision.allowed:
        return ip_decision
    return evaluate_domain(db, scope, email)


def has_domain_rules(db: Session, scope: str) -> bool:
    """True when the scope has any active email-domain rule."""
    return any(rule.kind in DOMAIN_KINDS for rule in _active_rules(db, normalize_scope(scope)))


def record_denial(
    scope: str,
    decision: AccessDecision,
    *,
    ip_address: Optional[str] = None,
    email: Optional[str] = None,
    username: Optional[str] = None,
    path: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Write one append-only security event for a denied attempt."""
    try:
        from app.services import security_events

        security_events.record(
            "auth.denied",
            outcome="denied",
            actor_username=username,
            target_type="network_access",
            target_label=email_domain(email) or ip_address or scope,
            path=path,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            detail={
                "scope": scope,
                "reason": decision.reason,
                "rule_id": decision.rule_id,
                "rule_value": decision.rule_value,
                "email_domain": email_domain(email),
            },
        )
        security_events.mark_request_recorded()
    except Exception:
        logger.exception("Could not record the network access denial")
