from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field

import httpx

from .models import DecisionRequest, DecisionResponse, ResourceMetadata

POLICY_VERSION = "dlp-2026.1"
logger = logging.getLogger("context.audit")


@dataclass
class Decision:
    decision: str
    reason: str
    obligations: list[str] = field(default_factory=list)

    @property
    def allow(self) -> bool:
        return self.decision in {"allow", "mask", "warn", "audit"}


def _subject_hash(subject_id: str) -> str:
    return hashlib.sha256(subject_id.encode()).hexdigest()[:16]


def _metadata_hash(metadata: ResourceMetadata) -> str:
    payload = json.dumps(metadata.model_dump(), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def _opa_input(request: DecisionRequest, metadata: ResourceMetadata) -> dict:
    return {
        "subject": request.subject.model_dump(),
        "resource": metadata.model_dump(),
        "action": request.action,
        "environment": request.environment.model_dump(),
    }


def fixture_decision(payload: dict) -> Decision:
    """Python mirror of the MVP Rego policy, for tests and local development."""
    subject = payload.get("subject") or {}
    resource = payload.get("resource") or {}
    action = payload.get("action")
    role = subject.get("role")
    classification = resource.get("classification")

    if resource.get("contains_secrets") and action in {
        "publish",
        "export",
        "external_share",
    }:
        return Decision(
            "deny",
            "Secret material cannot leave the controlled environment.",
            ["block:secrets"],
        )
    if resource.get("contains_assessment_answer_key") and action in {
        "publish",
        "external_share",
    }:
        return Decision(
            "deny",
            "Assessment answer keys cannot be published or externally shared.",
            ["block:assessment-answer-key"],
        )
    if resource.get("publication_safe") is False and action == "publish":
        return Decision(
            "deny",
            "Resource is not approved for publication.",
            ["block:publication"],
        )
    if resource.get("contains_infrastructure_metadata") and action in {
        "export",
        "external_share",
    }:
        return Decision(
            "require_approval",
            "Infrastructure metadata requires review and redaction before export.",
            ["approval:infrastructure-metadata", "redact:infrastructure-metadata"],
        )
    if resource.get("contains_assessment_answer_key") and action == "export":
        return Decision(
            "require_approval",
            "Assessment answer keys require approval and redaction before export.",
            ["approval:assessment-answer-key", "redact:assessment-answer-key"],
        )
    if classification == "restricted" and role == "student":
        return Decision("deny", "Students cannot export restricted resources.")
    if (
        action in {"export", "external_share"}
        and resource.get("contains_pii")
        and resource.get("jurisdiction") == "canada"
    ):
        return Decision(
            "require_approval",
            "PII shared outside the organisation requires approval under PIPEDA.",
            ["approval:pipeda-pii"],
        )
    if resource.get("training_data") and resource.get("contains_pii") and role == "student":
        return Decision(
            "mask",
            "Synthetic training PII is masked for students.",
            ["mask:pii"],
        )
    if classification == "public":
        return Decision("allow", "Public resource.")
    if classification == "restricted" and role in {"security-analyst", "admin"}:
        return Decision("allow", "Role may read restricted resources.")
    if classification in {"internal", "confidential"}:
        return Decision("allow", "No blocking policy matched.")
    return Decision("deny", "No policy permits this action.")


class OpaPolicy:
    def __init__(self, url: str, timeout: float = 2.0):
        self.url = url.rstrip("/")
        self.timeout = timeout

    def decide(self, payload: dict) -> Decision:
        response = httpx.post(
            f"{self.url}/v1/data/opencyberrange/dlp/result",
            json={"input": payload},
            timeout=self.timeout,
        )
        response.raise_for_status()
        result = (response.json() or {}).get("result") or {}
        decision = str(result.get("decision") or "deny")
        reason = str(result.get("reason") or "No policy reason returned.")
        obligations = [str(item) for item in (result.get("obligations") or [])]
        return Decision(decision, reason, obligations)


def decide(
    request: DecisionRequest,
    metadata: ResourceMetadata,
    *,
    opa_url: str | None,
    fail_closed: bool = True,
) -> DecisionResponse:
    payload = _opa_input(request, metadata)
    metadata_hash = _metadata_hash(metadata)
    if opa_url:
        try:
            decision = OpaPolicy(opa_url).decide(payload)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            if fail_closed:
                decision = Decision("deny", "Policy engine unavailable.")
            else:
                decision = fixture_decision(payload)
            logger.warning("policy_engine_error %s", exc)
    else:
        decision = fixture_decision(payload)

    decision_id = str(uuid.uuid4())
    logger.info(
        json.dumps(
            {
                "decision_id": decision_id,
                "policy_version": POLICY_VERSION,
                "metadata_hash": metadata_hash,
                "subject_hash": _subject_hash(request.subject.id),
                "resource_id": metadata.id,
                "action": request.action,
                "decision": decision.decision,
                "obligations": decision.obligations,
            }
        )
    )
    return DecisionResponse(
        decision_id=decision_id,
        decision=decision.decision,
        allow=decision.allow,
        reason=decision.reason,
        obligations=decision.obligations,
        policy_version=POLICY_VERSION,
        metadata_hash=metadata_hash,
        resource=metadata,
    )
