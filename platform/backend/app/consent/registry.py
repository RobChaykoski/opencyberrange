"""Consent types and the cleanup targets each revocation must run.

Adding a privacy-sensitive table means adding a target here and a purge/verify
hook in :mod:`app.consent.hooks`. ``PRIVACY_TABLES`` is asserted in tests so a
new derived table cannot ship without a destruction path.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TargetSpec:
    service: str
    action: str


@dataclass(frozen=True)
class ConsentSpec:
    id: str
    label: str
    description: str
    default_granted: bool
    targets: tuple[TargetSpec, ...]
    removed: tuple[str, ...]
    kept: tuple[str, ...]


CONSENT_TYPES: dict[str, ConsentSpec] = {
    "cyber_dna": ConsentSpec(
        id="cyber_dna",
        label="Cyber DNA",
        description=(
            "Competency evidence, behavior and interest profiles, affinity "
            "signals, and stored DNA snapshots."
        ),
        default_granted=False,
        targets=(
            TargetSpec("cyber_dna", "evidence"),
            TargetSpec("cyber_dna", "snapshots"),
            TargetSpec("reports", "learner_snapshots"),
        ),
        removed=(
            "Competency rollups and evidence",
            "Behavior, interest, and career-affinity models",
            "DNA snapshots and derived career reports",
        ),
        kept=(
            "Exercise completions and attempts",
            "Transcript and assessment results",
            "Certificates and achievements",
        ),
    ),
    "cyber_gps": ConsentSpec(
        id="cyber_gps",
        label="Cyber GPS",
        description=(
            "Direction finding from evidence: gap analysis, target roles, "
            "learning routes, forecasts, and readiness scores."
        ),
        default_granted=False,
        targets=(TargetSpec("cyber_gps", "cache"),),
        removed=(
            "Learning routes and target-role views",
            "Gap analysis and readiness forecasts",
        ),
        kept=("Current course progress", "Completed exercise history"),
    ),
    "portfolio": ConsentSpec(
        id="portfolio",
        label="Professional portfolio",
        description=(
            "The learner-generated portfolio and stored career/report snapshots."
        ),
        default_granted=False,
        targets=(TargetSpec("reports", "learner_snapshots"),),
        removed=("Stored portfolio and career snapshots",),
        kept=("Certificates", "Transcript and completed exercises"),
    ),
    "portfolio_sharing": ConsentSpec(
        id="portfolio_sharing",
        label="Portfolio sharing",
        description=(
            "External share links and public portfolio profiles for employers "
            "or other third parties."
        ),
        default_granted=False,
        targets=(
            TargetSpec("portfolio", "share_tokens"),
            TargetSpec("portfolio", "public_profiles"),
        ),
        removed=("Share tokens", "Public portfolio profiles"),
        kept=("The learner's private portfolio",),
    ),
    "ai_coach": ConsentSpec(
        id="ai_coach",
        label="AI coach",
        description=(
            "Conversation history, prompt context, embeddings, and AI memory."
        ),
        default_granted=False,
        targets=(
            TargetSpec("ai", "conversations"),
            TargetSpec("ai", "embeddings"),
            TargetSpec("ai", "memory"),
        ),
        removed=("Conversation history", "Embeddings and vector memory"),
        kept=("Learning records", "Certificates"),
    ),
    "research": ConsentSpec(
        id="research",
        label="Research and learner analytics",
        description=(
            "Learner-level analytics profiles, segmentation, and research "
            "datasets derived from platform activity."
        ),
        default_granted=False,
        targets=(
            TargetSpec("analytics", "learner_profiles"),
            TargetSpec("analytics", "segmentation"),
            TargetSpec("analytics", "research_datasets"),
        ),
        removed=("Learner analytics profiles", "Segmentation and research rows"),
        kept=("Aggregate counts that cannot identify a learner",),
    ),
}

# Fixed, auditable table registry. A privacy-sensitive table that appears here
# must have a purge target and a verification target in hooks.py.
PRIVACY_TABLES: dict[str, tuple[str, str]] = {
    "dna_evidence_records": ("cyber_dna", "evidence"),
    "dna_snapshots": ("cyber_dna", "snapshots"),
    "learner_snapshots": ("reports", "learner_snapshots"),
    "portfolio_share_tokens": ("portfolio", "share_tokens"),
    "public_profiles": ("portfolio", "public_profiles"),
    "ai_conversations": ("ai", "conversations"),
    "ai_embeddings": ("ai", "embeddings"),
    "ai_memory": ("ai", "memory"),
    "learner_analytics_profiles": ("analytics", "learner_profiles"),
    "learner_segmentations": ("analytics", "segmentation"),
    "research_dataset_rows": ("analytics", "research_datasets"),
}

VERIFY_SLOTS: tuple[tuple[str, int], ...] = (
    ("immediate", 0),
    ("24h", 24 * 60 * 60),
    ("7d", 7 * 24 * 60 * 60),
)

REVOCATION_SLA_SECONDS = 60 * 60
MAX_JOB_ATTEMPTS = 3


def spec_for(consent_type: str) -> ConsentSpec:
    try:
        return CONSENT_TYPES[consent_type]
    except KeyError as exc:
        raise ValueError(f"unknown consent type: {consent_type}") from exc


def target_for(service: str, action: str) -> TargetSpec:
    for spec in CONSENT_TYPES.values():
        for target in spec.targets:
            if target.service == service and target.action == action:
                return target
    raise ValueError(f"unknown consent target: {service}:{action}")
