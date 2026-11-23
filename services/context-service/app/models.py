from __future__ import annotations

from pydantic import BaseModel, Field


class Subject(BaseModel):
    id: str
    role: str
    groups: list[str] = Field(default_factory=list)
    tenant: str | None = None
    department: str | None = None
    clearance: str | None = None


class ResourceRef(BaseModel):
    id: str
    type: str = "resource"


class Environment(BaseModel):
    ip: str | None = None
    network: str | None = None
    device_managed: bool | None = None
    country: str | None = None


class DecisionRequest(BaseModel):
    subject: Subject
    resource: ResourceRef
    action: str = "read"
    environment: Environment = Field(default_factory=Environment)


class ResourceMetadata(BaseModel):
    id: str
    classification: str = "internal"
    owner: str = "unknown"
    steward: str | None = None
    contains_pii: bool = False
    contains_phi: bool = False
    contains_pci: bool = False
    contains_infrastructure_metadata: bool = False
    contains_assessment_answer_key: bool = False
    contains_secrets: bool = False
    publication_safe: bool = True
    jurisdiction: str | None = None
    retention: str | None = None
    frameworks: list[str] = Field(default_factory=list)
    controls: list[str] = Field(default_factory=list)
    training_data: bool = False


class ContextResponse(BaseModel):
    resource: ResourceMetadata
    metadata_hash: str


class DecisionResponse(BaseModel):
    decision_id: str
    decision: str
    allow: bool
    reason: str
    obligations: list[str] = Field(default_factory=list)
    policy_version: str
    metadata_hash: str
    resource: ResourceMetadata


class ScanRequest(BaseModel):
    source: str = "document"
    text: str


class ScanResponse(BaseModel):
    source: str
    classification: str
    publication_safe: bool
    contains_infrastructure_metadata: bool
    contains_assessment_answer_key: bool
    contains_secrets: bool
    findings: list[dict]
    redacted_text: str


class ScanDecisionRequest(ScanRequest):
    subject: Subject
    action: str = "publish"
    environment: Environment = Field(default_factory=Environment)


class ScanDecisionResponse(DecisionResponse):
    scan: ScanResponse
