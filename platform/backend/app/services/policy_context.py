"""Client for the metadata-driven policy context service.

The platform is the enforcement point; OpenMetadata is the authority of record.
This client sends subject, resource, action, and environment context to the
context service, which enriches the resource from its policy view and asks OPA
for a decision. An empty ``POLICY_CONTEXT_URL`` disables the call entirely so
existing deployments keep working until the service is deployed.
"""

from __future__ import annotations

import logging
from typing import Optional

import requests
from fastapi import HTTPException, Request

from app.config import settings
from app.models import User

logger = logging.getLogger(__name__)


def _subject(user: User) -> dict:
    return {
        "id": str(user.id),
        "role": getattr(user, "role", "student") or "student",
        "groups": [],
        "tenant": getattr(user, "institution_id", None),
        "department": getattr(user, "organization", None),
    }


def _environment(request: Optional[Request]) -> dict:
    return {
        "ip": request.client.host if request and request.client else None,
        "network": None,
        "device_managed": None,
        "country": None,
    }


def evaluate(
    user: User,
    *,
    resource_id: str,
    resource_type: str,
    action: str,
    request: Optional[Request] = None,
) -> dict:
    """Return the context service decision, or a local allow when disabled."""
    if not settings.POLICY_CONTEXT_URL:
        return {"decision": "allow", "allow": True, "skipped": True}

    payload = {
        "subject": _subject(user),
        "resource": {"id": resource_id, "type": resource_type},
        "action": action,
        "environment": _environment(request),
    }
    headers = {"Content-Type": "application/json"}
    if settings.POLICY_CONTEXT_TOKEN:
        headers["X-Context-Token"] = settings.POLICY_CONTEXT_TOKEN

    try:
        response = requests.post(
            settings.POLICY_CONTEXT_URL.rstrip("/") + "/decide",
            json=payload,
            headers=headers,
            timeout=settings.POLICY_CONTEXT_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        decision = response.json()
        if not isinstance(decision, dict) or "decision" not in decision:
            raise ValueError("policy context returned an invalid decision")
        logger.info(
            "policy_context decision=%s resource=%s action=%s decision_id=%s",
            decision.get("decision"),
            resource_id,
            action,
            decision.get("decision_id"),
        )
        return decision
    except Exception as exc:
        logger.warning("policy context unavailable: %s", exc)
        if settings.POLICY_CONTEXT_FAIL_CLOSED:
            return {
                "decision": "deny",
                "allow": False,
                "reason": "The data policy service is unavailable. Try again later.",
                "unavailable": True,
            }
        return {
            "decision": "allow",
            "allow": True,
            "reason": "The data policy service is unavailable.",
            "unavailable": True,
        }


def enforce_export(
    user: User,
    *,
    resource_id: str,
    resource_type: str = "report",
    action: str = "export",
    request: Optional[Request] = None,
) -> dict:
    """Block an export when the policy requires denial or human approval."""
    decision = evaluate(
        user,
        resource_id=resource_id,
        resource_type=resource_type,
        action=action,
        request=request,
    )
    outcome = str(decision.get("decision") or "deny")
    if outcome in {"deny", "require_approval"}:
        reason = str(
            decision.get("reason")
            or "The data policy does not permit this export."
        )
        raise HTTPException(
            status_code=403,
            detail=reason,
            headers={
                "X-Policy-Decision": outcome,
                "X-Policy-Decision-Id": str(decision.get("decision_id") or ""),
            },
        )
    return decision
