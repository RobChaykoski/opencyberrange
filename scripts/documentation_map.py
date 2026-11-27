#!/usr/bin/env python3
"""Group, index, and validate the documentation set.

The documentation register assigns every Markdown file under ``docs/`` to one
governance group. Group index pages are generated from the register. The register
is also the review record: relevance, quality score, labels, review dates, and
storage/retention are updated after a review (see
``docs/documentation/DOCUMENT-REVIEW-FORM.md``).

Usage:
    python scripts/documentation_map.py --check
    python scripts/documentation_map.py --check --fail-on-overdue
    python scripts/documentation_map.py --write
    python scripts/documentation_map.py --list-unmatched

``--write`` preserves review fields for documents already in the register and
only infers defaults for new files. Generated group pages are deterministic.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REGISTER = DOCS / "documentation" / "documentation-map.yaml"
GROUPS_DIR = DOCS / "documentation" / "groups"
REVIEW_ANCHOR = date(2026, 11, 26)

GROUP_ORDER = [
    "governance",
    "architecture",
    "operations",
    "security",
    "curriculum",
    "integrations",
    "product",
    "research",
    "archive",
    "documentation",
]

GROUPS: dict[str, dict] = {
    "governance": {
        "title": "Governance, risk and assurance",
        "purpose": (
            "Policy, control mapping, risk, privacy, retention, procurement, "
            "audit, and review records."
        ),
        "csf": ["GV.OC", "GV.RM", "GV.RR", "GV.PO", "GV.OV"],
        "nist": ["PM-1", "PM-4", "PM-9", "CA-2", "CA-5", "CA-7", "RA-3", "SI-12"],
        "owner": "Platform lead with the privacy officer",
    },
    "architecture": {
        "title": "Architecture, design and decisions",
        "purpose": (
            "System and data architecture, interfaces, schemas, and architecture "
            "decision records."
        ),
        "csf": ["ID.AM", "PR.PS", "PR.DS"],
        "nist": ["CM-2", "CM-3", "CM-4", "SA-5", "SA-8", "SA-11", "SI-12"],
        "owner": "Architecture lead",
    },
    "operations": {
        "title": "Operations and service management",
        "purpose": (
            "Deployment, runbooks, backup and restore, availability, monitoring, "
            "database integrity, migrations, and upgrade paths."
        ),
        "csf": ["PR.PS", "PR.IR", "RC.RP"],
        "nist": ["CM-6", "CP-10", "IR-4", "SI-2", "SI-4", "AU-2", "AU-6"],
        "owner": "Platform operator",
    },
    "security": {
        "title": "Security engineering and assurance",
        "purpose": (
            "Authentication, authorization, tenancy, consent enforcement, threat "
            "and vulnerability work, scanning, and security evidence."
        ),
        "csf": ["PR.AA", "PR.DS", "DE.CM", "RS.AN"],
        "nist": ["AC-3", "AC-6", "AU-2", "CA-7", "RA-5", "SC-7", "SI-4", "IR-4"],
        "owner": "Security lead",
    },
    "curriculum": {
        "title": "Curriculum, learning and assessment",
        "purpose": (
            "Learning design, tracks and pathways, labs, competencies, assessment, "
            "analytics, transcripts, achievements, and instructor practice."
        ),
        "csf": ["PR.AT", "ID.AM"],
        "nist": ["AT-2", "PM-5", "SA-11"],
        "owner": "Curriculum lead",
    },
    "integrations": {
        "title": "Integrations and ecosystem",
        "purpose": (
            "SSO and identity providers, LMS/LTI, OpenGRC and the wider ecosystem, "
            "reporting boundaries, and evidence exchange."
        ),
        "csf": ["GV.SC", "ID.IM"],
        "nist": ["SA-9", "SR-3", "PM-5"],
        "owner": "Integration lead",
    },
    "product": {
        "title": "Product, releases and change",
        "purpose": (
            "Scope, releases, deliverables, editions, roadmaps, counts, handoffs, "
            "and the published project overview."
        ),
        "csf": ["GV.RR", "GV.OV"],
        "nist": ["CM-3", "SA-10", "SI-12"],
        "owner": "Product lead",
    },
    "research": {
        "title": "Research, pilots and community",
        "purpose": (
            "Pilots, research notes, community events, UI and experience studies, "
            "and proposals that are not yet product commitments."
        ),
        "csf": ["GV.OV", "ID.IM"],
        "nist": ["PM-4", "PM-9"],
        "owner": "Research lead",
    },
    "archive": {
        "title": "Archive",
        "purpose": (
            "Superseded plans, completed migrations, and historical records kept "
            "for provenance. Not current operating guidance."
        ),
        "csf": ["GV.OV"],
        "nist": ["SI-12", "MP-6"],
        "owner": "Records custodian",
    },
    "documentation": {
        "title": "Documentation system",
        "purpose": (
            "The documentation standard, review form, grouping register, and "
            "generated group indexes."
        ),
        "csf": ["GV.PO", "GV.OV"],
        "nist": ["PM-1", "CM-2", "SI-12"],
        "owner": "Documentation steward",
    },
}

DOC_TYPES = {
    "policy",
    "standard",
    "procedure",
    "runbook",
    "architecture",
    "design",
    "adr",
    "reference",
    "report",
    "assessment",
    "register",
    "form",
    "index",
    "release",
    "generated",
    "archive",
}
AUDIENCES = {
    "public",
    "learner",
    "instructor",
    "operator",
    "developer",
    "auditor",
    "executive",
    "partner",
}
CLASSIFICATIONS = {"public", "internal", "confidential", "restricted"}
LIFECYCLES = {"draft", "active", "deprecated", "archived", "generated"}
REVIEW_STATUSES = {"unreviewed", "in_review", "approved", "needs_revision", "retired"}
CADENCES = {"quarterly": 3, "semiannual": 6, "annual": 12, "biennial": 24}
RETENTION = {"R0", "R1", "R2", "R3", "R4", "R5"}

# Filename/path rules, evaluated in order. The first match wins.
RULES: list[tuple[str, str, str]] = [
    # folder, group, doc_type
    ("docs/archive/", "archive", "archive"),
    ("docs/decisions/", "architecture", "adr"),
    ("docs/architecture/", "architecture", "architecture"),
    ("docs/operations/", "operations", "reference"),    ("docs/curriculum/", "curriculum", "reference"),
    ("docs/security/", "security", "reference"),
    ("docs/compliance/", "governance", "reference"),
    ("docs/integrations/", "integrations", "reference"),
    ("docs/reviews/", "governance", "assessment"),
    ("docs/research/", "research", "report"),
    ("docs/_project_overview/", "product", "reference"),
    ("docs/lite/", "product", "reference"),
    ("docs/documentation/groups/", "documentation", "generated"),
    ("docs/documentation/", "documentation", "form"),
]

# Root filename keywords. Keep more specific rules before broader ones.
KEYWORD_RULES: list[tuple[tuple[str, ...], str, str]] = [
    (("RELEASE-", "DELIVERABLES"), "product", "release"),
    (("CURRICULUM-DRIFT", "CONTENT-GAP", "EMPLOYER-CAPABILITY-GAPS"), "research", "report"),
    (("SECURITY-REVIEW", "CODE-AND-DATABASE-REVIEW", "PILOT-READINESS-REVIEW"), "governance", "assessment"),
    (("OWASP-SECURITY-BASELINE",), "security", "standard"),
    (("OWASP-TOP10-LABS", "API-SECURITY-LABS", "JUICE-SHOP-LABS"), "curriculum", "reference"),
    (("ZAP-SCAN-PLANNER", "INDEPENDENT-SECURITY-TESTING"), "security", "report"),
    (("THREAT-AWARENESS-OPERATIONS",), "security", "procedure"),
    (("MALWARE-", "WINDOWS-ARTIFACT", "OT-SCANNING", "HOST-SCRIPT"), "security", "standard"),
    (
        (
            "SECURITY", "OWASP", "AUTH-LIFECYCLE", "AUTHORIZATION", "RBAC", "TENANT",
            "THREAT", "ZAP", "SCANNING", "ANTI-SCRAPING", "CONSENT-REVOCATION",
            "DATA-LABELS", "SECURITY-DATASETS", "V2-SECURITY", "BACKUP-SECURITY",
        ),
        "security",
        "reference",
    ),
    (
        (
            "PRIVACY", "RETENTION", "DATA-CLASSIFICATION", "COMPLIANCE", "HECVAT",
            "DPA-", "PROCUREMENT", "ACCESSIBILITY", "MINOR-SAFE",
            "EDUCATIONAL-PROVENANCE", "PUBLICATION-METADATA", "REPOSITORY-HYGIENE",
            "MKDOCS-GOVERNANCE", "OPEN-SOURCE-READINESS", "CONTRIBUTORS",
            "EDITIONS", "MICROSOFT-LEGAL", "LIVING-ARCHIVE", "PROFESSIONAL-PRIORITIES",
        ),
        "governance",
        "reference",
    ),
    (("DPA-TEMPLATE",), "governance", "form"),
    (
        (
            "DEPLOYMENT", "RUNBOOK", "OPERATIONS", "BACKUP", "RESTORE", "HA-",
            "MONITORING", "UPGRADE", "OS-SUPPORT", "SUPPORTED-VERSIONS",
            "DATABASE-", "ALEMBIC", "MINIO", "REVERSE-PROXY", "NETWORK-SANDBOX",
            "RANGEBOX", "DEVICE-TOPOLOGY", "HOST-", "STATUS-", "PRODUCTION",
            "GCP-", "UBUNTU", "KASM", "WIKI-ORIGIN", "MANUAL-PUBLISHING",
            "V3-HA-", "RELEASE-5-PRODUCTION-READINESS",
        ),
        "operations",
        "reference",
    ),
    (
        (
            "LTI-", "MOODLE", "SSO", "SAML", "LDAP", "OIDC", "OPENIAM",
            "ECOSYSTEM", "REPORTING-ROADMAP", "OPENGRC",
        ),
        "integrations",
        "reference",
    ),
    (
        (
            "COMMUNITY", "DEVFEST", "PILOT", "UI-AFFORDANCE", "PROFILE-EXPERIENCE",
            "EXERCISE-AND-RANGEBOX-REVIEW", "TWO-TENANT-PILOT", "RESEARCH",
        ),
        "research",
        "report",
    ),
    (
        (
            "ARCHITECTURE", "AUTHORIZATION-SERVICE", "API-ERROR-CODES", "CHARTING",
            "DEVICE-TOPOLOGY", "DATA-DICTIONARY", "ANALYTICS-EVENT-SCHEMA",
            "CYBER-GPS-SCHEMA", "LAB-METADATA-SCHEMA",
        ),
        "architecture",
        "architecture",
    ),
    (
        (
            "CURRICULUM", "LEARNING", "LAB-", "COMPETENCY", "NICE-", "PATHWAY",
            "TRACK", "EXERCISE", "QUESTION", "QUIZ", "CERTIFICATION", "PRACTICE",
            "ACHIEVEMENT", "TRANSCRIPT", "READINESS", "CAREER", "SKILL",
            "EVIDENCE-", "CAPSTONE", "ANALYTICS", "INSTRUCTOR", "STUDENT",
            "PROGRAM", "TRAINING", "BADGE", "OSINT", "FORENSICS", "DFIR",
            "DETECTION-", "ACTIVE-DIRECTORY", "MODERN-APP", "SUPPLY-CHAIN-SECURITY",
            "AUTOMOTIVE", "AI-SECURITY", "IDENTITY-QUESTS", "FOUNDATIONS",
            "SIMULATED-CLOUD", "MULTI-STUDENT", "CYBER-PHYSICAL", "DRONE-",
            "OT01-", "METASPLOIT", "PHONE-OSINT", "LIVE-MEMORY", "VULNHUB",
            "SECURITY-DATASETS",
        ),
        "curriculum",
        "reference",
    ),
    (("AI-MENTOR", "FEDERATION", "LANGUAGE", "COUNTS", "NEXT-STEPS", "HANDOFF", "ABOUT-", "OPEN-BADGES"), "product", "reference"),
]

# Explicit overrides for documents the keyword rules cannot place cleanly.
OVERRIDES: dict[str, tuple[str, str]] = {
    "docs/FOUNDATIONS.md": ("curriculum", "reference"),
    "docs/AI-MENTOR.md": ("product", "design"),
    "docs/FEDERATION.md": ("product", "design"),
    "docs/LANGUAGE-AND-LOCALIZATION.md": ("product", "standard"),
    "docs/OPEN-BADGES-3.0-SCOPE.md": ("curriculum", "standard"),
    "docs/CHARTING.md": ("architecture", "reference"),
    "docs/status-dashboard.md": ("operations", "generated"),
    "docs/status-dashboard.json": ("operations", "generated"),
    "docs/status-hosts.json": ("operations", "generated"),
    "docs/DATA-DICTIONARY.md": ("architecture", "generated"),
    "docs/DATA-LABELS.md": ("security", "reference"),
    "docs/SECURITY-DATASETS.md": ("curriculum", "reference"),
    "docs/OWASP-SECURITY-BASELINE.md": ("security", "standard"),
    "docs/EDUCATIONAL-PROVENANCE.md": ("governance", "standard"),
    "docs/PUBLICATION-METADATA-POLICY.md": ("governance", "policy"),
    "docs/REPOSITORY-HYGIENE.md": ("governance", "standard"),
    "docs/MKDOCS-GOVERNANCE.md": ("governance", "standard"),
    "docs/ACCESSIBILITY.md": ("governance", "standard"),
    "docs/MINOR-SAFE-DEFAULTS.md": ("governance", "standard"),
    "docs/PRIVACY-NOTICE.md": ("governance", "policy"),
    "docs/PRIVACY-AND-DATA-DELETION.md": ("governance", "procedure"),
    "docs/RETENTION-POLICIES.md": ("governance", "standard"),
    "docs/DATA-CLASSIFICATION.md": ("governance", "standard"),
    "docs/COMPLIANCE.md": ("governance", "standard"),
    "docs/EDITIONS.md": ("product", "standard"),
    "docs/COUNTS.md": ("product", "generated"),
    "docs/VALIDATION-REPORT.md": ("product", "report"),
    "docs/PROFESSIONAL-PRIORITIES.md": ("governance", "reference"),
    "docs/LIVING-ARCHIVE.md": ("governance", "reference"),
    "docs/TWO-TENANT-PILOT.md": ("research", "report"),
    "docs/INDEPENDENT-SECURITY-TESTING.md": ("security", "report"),
    "docs/AI-GOVERNANCE-AND-SECURITY-PATHWAY.md": ("curriculum", "reference"),
    "docs/AI-SECURITY-AGENTIC-LABS.md": ("curriculum", "reference"),
    "docs/MODERN-APP-SECURITY-PATHWAY.md": ("curriculum", "reference"),
    "docs/SUPPLY-CHAIN-SECURITY-PATHWAY.md": ("curriculum", "reference"),
    "docs/ATTACK-NAVIGATOR.md": ("curriculum", "reference"),
    "docs/ATTACK-SIMULATION-DASHBOARD.md": ("curriculum", "reference"),
    "docs/AUTOMATED-SCORING.md": ("curriculum", "reference"),
    "docs/CELEBRATION-WALL.md": ("curriculum", "reference"),
    "docs/CYBER-DNA-V3.md": ("curriculum", "reference"),
    "docs/CYBER-WORKFORCE-RISK-SCORE.md": ("curriculum", "reference"),
    "docs/EVENT-CERTIFICATES.md": ("curriculum", "reference"),
    "docs/IMPACT-AND-LEGACY.md": ("curriculum", "reference"),
    "docs/LEARNER-ARCHETYPES.md": ("curriculum", "reference"),
    "docs/LEARNER-DEVELOPMENT-VECTOR.md": ("curriculum", "reference"),
    "docs/LEARNER-VISIBLE-SCORES.md": ("curriculum", "reference"),
    "docs/MULTI-STUDENT-SCENARIOS.md": ("curriculum", "reference"),
    "docs/ROLE-CAPABILITY-MODEL.md": ("curriculum", "reference"),
    "docs/SFIA-9-INGESTION.md": ("curriculum", "reference"),
    "docs/TRAINING-ECOSYSTEM.md": ("curriculum", "reference"),
    "docs/BROWSER-MATRIX.md": ("operations", "reference"),
    "docs/DEPENDENCY-WORKFLOW.md": ("operations", "procedure"),
    "docs/HEALTH-DASHBOARD-PLAN.md": ("operations", "design"),
    "docs/MANUAL-SCREENSHOTS.md": ("operations", "reference"),
    "docs/V2-24.04-BUILD-OUT.md": ("operations", "reference"),
    "docs/EXERCISE-AND-RANGEBOX-REVIEW.md": ("research", "assessment"),
    "docs/INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md": ("architecture", "design"),
    "docs/METADATA-POLICY-CONTEXT.md": ("governance", "reference"),
    "docs/PIA-TRA-FINDINGS.md": ("governance", "assessment"),
    "docs/SUPPLY-CHAIN.md": ("security", "reference"),
    "docs/SOFTWARE-SECURITY-WORKSTREAM.md": ("security", "reference"),
    "docs/V2-PROGRAM-CHARTER.md": ("product", "reference"),
    "docs/README.md": ("documentation", "index"),
    "docs/DPA-TEMPLATE.md": ("governance", "form"),
    "docs/ALEMBIC-BASELINE.md": ("operations", "reference"),
    "docs/ALEMBIC-DRIFT-INVENTORY.md": ("operations", "reference"),
    "docs/DATABASE-INTEGRITY.md": ("operations", "reference"),
    "docs/DATABASE-MIGRATIONS.md": ("operations", "reference"),
    "docs/BACKUP-RESTORE-TEST.md": ("operations", "procedure"),
    "docs/DEPLOYMENT-RUNBOOK.md": ("operations", "runbook"),
    "docs/PILOT-EVENT-RUNBOOK.md": ("operations", "runbook"),
    "docs/MANUAL-PUBLISHING.md": ("operations", "procedure"),
}

TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def title_for(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return path.stem.replace("-", " ").title()
    match = TITLE_RE.search(text)
    if match:
        return re.sub(r"[`*_]", "", match.group(1)).strip()
    return re.sub(r"[-_]+", " ", path.stem).strip().title()


def infer(rel: str) -> tuple[str, str]:
    if rel in OVERRIDES:
        return OVERRIDES[rel]
    lower = rel.lower()
    for prefix, group, doc_type in RULES:
        if lower.startswith(prefix):
            return group, doc_type
    name = Path(rel).name.upper()
    for keywords, group, doc_type in KEYWORD_RULES:
        if any(keyword in name for keyword in keywords):
            return group, doc_type
    return "product", "reference"


def cadence_for(doc_type: str) -> str:
    if doc_type in {"runbook", "procedure"}:
        return "semiannual"
    if doc_type in {"policy", "standard"}:
        return "annual"
    if doc_type in {"assessment", "report", "release"}:
        return "annual"
    if doc_type in {"generated", "archive"}:
        return "annual"
    return "annual"


def retention_for(doc_type: str, group: str) -> str:
    if group == "archive":
        return "R5"
    if doc_type in {"release", "assessment"}:
        return "R0"
    if doc_type == "policy":
        return "R1"
    if doc_type in {"runbook", "procedure"}:
        return "R2"
    if doc_type in {"generated", "index"}:
        return "R3"
    if doc_type == "adr":
        return "R5"
    return "R2"


def default_entry(rel: str, path: Path) -> dict:
    group, doc_type = infer(rel)
    return {
        "path": rel,
        "title": title_for(path),
        "group": group,
        "doc_type": doc_type,
        "audience": ["public"] if group == "documentation" else ["developer"],
        "classification": "public" if rel in {
            "docs/PRIVACY-NOTICE.md",
            "docs/ACCESSIBILITY.md",
            "docs/COMPLIANCE.md",
            "docs/EDITIONS.md",
            "docs/ABOUT-AREA.md",
            "docs/CONTRIBUTORS-AND-BRANCHES.md",
            "docs/OPEN-SOURCE-READINESS.md",
        } else "internal",
        "lifecycle": "active",
        "sensitivity": ["none"],
        "review": {
            "status": "unreviewed",
            "cadence": cadence_for(doc_type),
            "last_reviewed": None,
            "next_review": None,
            "reviewer": None,
            "approver": None,
        },
        "relevance": None,
        "score": None,
        "requirements": [],
        "storage": {
            "source": "git",
            "published": doc_type not in {"generated", "archive"},
            "evidence": doc_type in {"release", "assessment", "policy", "standard"},
            "retention": retention_for(doc_type, group),
        },
    }


def load_register() -> dict:
    if not REGISTER.is_file():
        return {"schema_version": 1, "review_anchor": REVIEW_ANCHOR.isoformat(), "documents": []}
    data = yaml.safe_load(REGISTER.read_text(encoding="utf-8")) or {}
    data.setdefault("schema_version", 1)
    data.setdefault("documents", [])
    return data


def markdown_files() -> list[Path]:
    files = []
    for path in DOCS.rglob("*.md"):
        rel = relative(path)
        if rel.startswith("docs/documentation/groups/"):
            continue
        files.append(path)
    return sorted(files, key=relative)


def sync() -> dict:
    existing = {item["path"]: item for item in load_register().get("documents", [])}
    documents = []
    for path in markdown_files():
        rel = relative(path)
        entry = existing.get(rel)
        if entry is None:
            entry = default_entry(rel, path)
        else:
            # Keep reviewed metadata, refresh the title when the heading changes.
            entry["title"] = title_for(path)
        documents.append(entry)
    documents.sort(key=lambda item: item["path"])
    return {
        "schema_version": 1,
        "review_anchor": REVIEW_ANCHOR.isoformat(),
        "groups": [
            {"id": key, **GROUPS[key]} for key in GROUP_ORDER
        ],
        "documents": documents,
    }


def group_page(group: str, documents: list[dict]) -> str:
    meta = GROUPS[group]
    rows = []
    for item in documents:
        review = item.get("review") or {}
        score = "" if item.get("score") is None else str(item["score"])
        next_review = review.get("next_review") or "unset"
        rows.append(
            "| [{title}]({path}) | `{doc_type}` | {classification} | {status} | {score} | {next_review} |".format(
                title=item["title"].replace("|", "\\|"),
                path="../../" + item["path"].removeprefix("docs/"),
                doc_type=item["doc_type"],
                classification=item["classification"],
                status=review.get("status", "unreviewed"),
                score=score,
                next_review=next_review,
            )
        )
    return "\n".join(
        [
            f"# {meta['title']}",
            "",
            "<!-- Generated by scripts/documentation_map.py. Do not edit. -->",
            "",
            meta["purpose"],
            "",
            f"- **NIST CSF 2.0:** {', '.join(meta['csf'])}",
            f"- **NIST SP 800-53 Rev. 5:** {', '.join(meta['nist'])}",
            f"- **Owner:** {meta['owner']}",
            "",
            f"{len(documents)} document(s) in this group.",
            "",
            "| Document | Type | Classification | Review | Score | Next review |",
            "|---|---|---|---|---:|---|",
            *rows,
            "",
            (
                "Review a document with the "
                "[document review form](../DOCUMENT-REVIEW-FORM.md). Grouping rules "
                "and labels are defined in the "
                "[documentation standard](../DOCUMENTATION-STANDARDS.md)."
            ),            "",
        ]
    )


def write_all(data: dict) -> None:
    REGISTER.parent.mkdir(parents=True, exist_ok=True)
    REGISTER.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )
    GROUPS_DIR.mkdir(parents=True, exist_ok=True)
    for group in GROUP_ORDER:
        documents = [item for item in data["documents"] if item["group"] == group]
        (GROUPS_DIR / f"{group}.md").write_text(
            group_page(group, documents), encoding="utf-8"
        )
    print(f"wrote {relative(REGISTER)} and {len(GROUP_ORDER)} group pages")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(data: dict, fail_on_overdue: bool) -> int:
    errors: list[str] = []
    documents = data.get("documents") or []
    by_path: dict[str, dict] = {}
    for item in documents:
        path = item.get("path", "")
        require(path not in by_path, f"duplicate register entry: {path}", errors)
        by_path[path] = item

    disk = {relative(path) for path in markdown_files()}
    for path in sorted(disk - set(by_path)):
        errors.append(f"document not in register: {path}")
    for path in sorted(set(by_path) - disk):
        errors.append(f"register entry has no file: {path}")

    counts = {group: 0 for group in GROUP_ORDER}
    unreviewed = 0
    overdue: list[str] = []
    today = date.today()
    for item in documents:
        path = item.get("path", "")
        group = item.get("group")
        require(group in GROUPS, f"{path}: unknown group {group!r}", errors)
        if group in counts:
            counts[group] += 1
        require(item.get("doc_type") in DOC_TYPES, f"{path}: unknown doc_type {item.get('doc_type')!r}", errors)
        require(item.get("classification") in CLASSIFICATIONS, f"{path}: unknown classification", errors)
        require(item.get("lifecycle") in LIFECYCLES, f"{path}: unknown lifecycle", errors)
        require(isinstance(item.get("audience"), list) and item["audience"], f"{path}: audience must be a list", errors)
        for audience in item.get("audience") or []:
            require(audience in AUDIENCES, f"{path}: unknown audience {audience!r}", errors)
        for flag in item.get("sensitivity") or []:
            require(flag in {"none", "pii", "security", "credentials", "learner_evidence"}, f"{path}: unknown sensitivity {flag!r}", errors)

        review = item.get("review") or {}
        require(review.get("status") in REVIEW_STATUSES, f"{path}: unknown review status", errors)
        require(review.get("cadence") in CADENCES, f"{path}: unknown cadence", errors)
        if review.get("status") == "unreviewed":
            unreviewed += 1
        if review.get("status") in {"approved", "needs_revision"}:
            require(bool(review.get("last_reviewed")), f"{path}: completed review has no last_reviewed", errors)
            require(bool(review.get("next_review")), f"{path}: completed review has no next_review", errors)
            require(bool(review.get("reviewer")), f"{path}: completed review has no reviewer", errors)
        last = review.get("last_reviewed")
        nxt = review.get("next_review")
        if last and nxt:
            require(str(nxt) >= str(last), f"{path}: next_review is before last_reviewed", errors)
        if nxt and str(nxt) < today.isoformat() and review.get("status") != "retired":
            overdue.append(path)

        score = item.get("score")
        if score is not None:
            require(isinstance(score, int) and 0 <= score <= 100, f"{path}: score must be 0-100", errors)
            require(review.get("status") in {"approved", "needs_revision"}, f"{path}: scored but review is not complete", errors)
            require(bool(review.get("reviewer")), f"{path}: scored without a reviewer", errors)
            require(bool(last), f"{path}: scored without last_reviewed", errors)
        relevance = item.get("relevance")
        if relevance is not None:
            require(isinstance(relevance, int) and 1 <= relevance <= 5, f"{path}: relevance must be 1-5", errors)

        storage = item.get("storage") or {}
        require(storage.get("source") == "git", f"{path}: storage.source must be git", errors)
        require(storage.get("retention") in RETENTION, f"{path}: unknown retention class", errors)

        requirements = item.get("requirements") or []
        require(isinstance(requirements, list), f"{path}: requirements must be a list", errors)
        for requirement in requirements:
            if not isinstance(requirement, dict):
                errors.append(f"{path}: requirement entry must be a mapping")
                continue
            require(bool(requirement.get("source")), f"{path}: requirement has no source", errors)
            require(bool(requirement.get("id")), f"{path}: requirement has no id", errors)
            require(bool(requirement.get("evidence")), f"{path}: requirement has no evidence", errors)

    for group, count in counts.items():
        if count == 0:
            errors.append(f"group {group} has no documents")

    # Generated index pages must match the register.
    for group in GROUP_ORDER:
        page = GROUPS_DIR / f"{group}.md"
        expected = group_page(group, [i for i in documents if i["group"] == group])
        if not page.is_file():
            errors.append(f"missing generated group page: {relative(page)}")
        elif page.read_text(encoding="utf-8") != expected:
            errors.append(f"generated group page is stale: {relative(page)} (run --write)")

    print("Documentation map")
    print("=" * 40)
    for group in GROUP_ORDER:
        print(f"  {group:14} {counts[group]:4}")
    print(f"  {'total':14} {len(documents):4}")
    print(f"  unreviewed: {unreviewed}; overdue: {len(overdue)}")
    if overdue:
        for path in overdue[:20]:
            print(f"  OVERDUE: {path}")
        if len(overdue) > 20:
            print(f"  ... and {len(overdue) - 20} more")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAILED: {len(errors)} error(s)", file=sys.stderr)
        return 1
    if fail_on_overdue and overdue:
        print(f"FAILED: {len(overdue)} overdue review(s)", file=sys.stderr)
        return 1
    print("PASS: every document is grouped, labelled, and indexed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the register and group pages")
    parser.add_argument("--check", action="store_true", help="validate the register and generated pages")
    parser.add_argument("--fail-on-overdue", action="store_true", help="fail when a review date has passed")
    parser.add_argument("--list-unmatched", action="store_true", help="show inferred groups only")
    args = parser.parse_args()

    if not any((args.write, args.check, args.list_unmatched)):
        parser.error("choose --write, --check, or --list-unmatched")

    data = sync()
    if args.list_unmatched:
        for item in data["documents"]:
            print(f"{item['group']:14} {item['doc_type']:12} {item['path']}")
        return 0
    if args.write:
        write_all(data)
        return 0
    return validate(data, args.fail_on_overdue)


if __name__ == "__main__":
    raise SystemExit(main())
