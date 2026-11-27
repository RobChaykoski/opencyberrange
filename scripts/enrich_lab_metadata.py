#!/usr/bin/env python3
"""Add the shared curriculum metadata fields to every lab.yaml.

The review added five optional fields to the canonical schema:

    learning_concepts
    competency_tags
    defensive_skills
    evidence_required
    report_questions

This script fills only the missing fields. It derives a category-aware baseline
from the existing title, outcomes, defensive takeaways, difficulty, and mapped
skills. Existing values are never replaced, so a hand-reviewed lab keeps its
text.

Usage:
    python scripts/enrich_lab_metadata.py --check
    python scripts/enrich_lab_metadata.py --write
    python scripts/enrich_lab_metadata.py --write --lab web-1-1-basic-directory-enumeration
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"
FIELDS = (
    "learning_concepts",
    "competency_tags",
    "defensive_skills",
    "evidence_required",
    "report_questions",
)

CATEGORY_CONCEPTS = {
    "ai": ["AI security", "prompt and tool trust", "agent boundaries"],
    "assessment": ["security assessment", "evidence collection", "reporting"],
    "authentication": ["authentication", "session management", "identity assurance"],
    "credential-attacks": ["credential security", "authentication weaknesses", "detection"],
    "crypto": ["cryptography", "encoding versus encryption", "key management"],
    "enumeration": ["service enumeration", "protocol identification", "attack surface mapping"],
    "exploitation": ["vulnerability exploitation", "impact assessment", "defensive controls"],
    "forensics": ["digital forensics", "evidence handling", "timeline analysis"],
    "general": ["security fundamentals", "safe practice", "evidence-based reasoning"],
    "network": ["network fundamentals", "protocol analysis", "segmentation"],
    "network-analysis": ["packet analysis", "protocol analysis", "detection"],
    "osint": ["open-source intelligence", "identity correlation", "exposure mapping"],
    "ot": ["operational technology", "industrial protocols", "control-network security"],
    "post-exploitation": ["lateral movement", "credential access", "impact assessment"],
    "privilege-escalation": ["local privilege escalation", "misconfiguration analysis", "least privilege"],
    "reconnaissance": ["open-source intelligence", "attack surface mapping", "asset discovery"],
    "web": ["web application security", "HTTP request and response", "attack surface mapping"],
}

CATEGORY_PREFIX = {
    "ai": "ai",
    "assessment": "assessment",
    "authentication": "identity",
    "credential-attacks": "credentials",
    "crypto": "crypto",
    "enumeration": "enumeration",
    "exploitation": "exploitation",
    "forensics": "forensics",
    "general": "foundations",
    "network": "network",
    "network-analysis": "network_analysis",
    "osint": "osint",
    "ot": "ot",
    "post-exploitation": "post_exploitation",
    "privilege-escalation": "privesc",
    "reconnaissance": "recon",
    "web": "web",
}

CATEGORY_EVIDENCE = {
    "ai": ["prompt_or_trace", "control_recommendation", "interpretation"],
    "assessment": ["findings", "evidence_index", "report"],
    "authentication": ["request_and_response", "configuration_review", "interpretation"],
    "credential-attacks": ["command_output", "credential_evidence", "interpretation"],
    "crypto": ["encoded_or_encrypted_sample", "analysis", "interpretation"],
    "enumeration": ["command_output", "service_inventory", "interpretation"],
    "exploitation": ["request_or_command_output", "impact_evidence", "interpretation"],
    "forensics": ["artifact", "timeline", "interpretation"],
    "general": ["short_explanation", "safe_next_step"],
    "network": ["command_output", "packet_or_log_evidence", "interpretation"],
    "network-analysis": ["packet_or_log_evidence", "timeline", "interpretation"],
    "osint": ["source_evidence", "exposure_map", "interpretation"],
    "ot": ["packet_or_register_evidence", "segmentation_plan", "interpretation"],
    "post-exploitation": ["command_output", "impact_evidence", "interpretation"],
    "privilege-escalation": ["command_output", "privilege_evidence", "interpretation"],
    "reconnaissance": ["source_evidence", "asset_inventory", "interpretation"],
    "web": ["request_and_response", "evidence", "interpretation"],
}

CATEGORY_QUESTIONS = {
    "ai": "Which instruction or trust boundary failed?",
    "assessment": "Which finding is best supported by the evidence?",
    "authentication": "Which identity or session control failed?",
    "credential-attacks": "Which credential weakness made the access possible?",
    "crypto": "What does the evidence show about the encoding or key?",
    "enumeration": "Which host, port, or service is involved?",
    "exploitation": "Which request or command shows the impact?",
    "forensics": "Which artifact supports your timeline?",
    "general": "What evidence supports your conclusion?",
    "network": "Which host, port, or protocol is involved?",
    "network-analysis": "Which packet or log entry supports your conclusion?",
    "osint": "Which public source exposed the information?",
    "ot": "Which register, packet, or control action changed?",
    "post-exploitation": "Which action shows the scope of the impact?",
    "privilege-escalation": "Which permission or configuration allowed the escalation?",
    "reconnaissance": "Which public source or asset exposed the information?",
    "web": "Which request or response shows the weakness?",
}

CATEGORY_DEFENSIVE = {
    "ai": ["validate_model_input", "restrict_tool_scope", "log_agent_decisions"],
    "assessment": ["preserve_evidence", "state_confidence", "record_remediation"],
    "authentication": ["use_server_side_sessions", "enforce_mfa", "rotate_credentials"],
    "credential-attacks": ["remove_default_credentials", "rate_limit_logins", "monitor_failures"],
    "crypto": ["use_reviewed_cryptography", "protect_keys", "avoid_custom_crypto"],
    "enumeration": ["reduce_banner_detail", "restrict_unused_services", "monitor_scanning"],
    "exploitation": ["validate_input", "enforce_authorization", "patch_exposed_services"],
    "forensics": ["preserve_original_evidence", "record_timeline", "verify_hashes"],
    "general": ["stay_in_scope", "review_before_publishing", "record_evidence"],
    "network": ["segment_networks", "restrict_management_access", "monitor_traffic"],
    "network-analysis": ["baseline_normal_traffic", "alert_on_anomalies", "retain_packets"],
    "osint": ["minimise_public_identity", "separate_identities", "review_public_sources"],
    "ot": ["segment_control_networks", "restrict_industrial_protocols", "monitor_register_writes"],
    "post-exploitation": ["limit_credentials", "monitor_lateral_movement", "revoke_sessions"],
    "privilege-escalation": ["apply_least_privilege", "remove_unneeded_sudo", "audit_permissions"],
    "reconnaissance": ["reduce_public_exposure", "maintain_asset_inventory", "monitor_discovery"],
    "web": ["validate_input", "enforce_authorization", "monitor_requests"],
}

STOP_VERBS = (
    "explain",
    "use",
    "identify",
    "demonstrate",
    "describe",
    "read",
    "analyse",
    "analyze",
    "configure",
    "exploit",
    "detect",
    "recover",
    "write",
    "perform",
    "compare",
    "recognise",
    "recognize",
    "trace",
    "inspect",
    "review",
    "apply",
    "map",
    "recommend",
    "test",
    "find",
    "run",
    "open",
    "create",
    "build",
    "validate",
    "collect",
    "interpret",
    "prioritise",
    "prioritize",
    "record",
    "name",
    "list",
    "inventory",
    "separate",
    "correlate",
)


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def clean_phrase(text: str) -> str:
    text = re.sub(r"^[\s\-*]+", "", text.strip())
    text = re.sub(r"\s+", " ", text)
    text = text.rstrip(".:;,")
    return text


def concept_from_outcome(outcome: str) -> str:
    text = clean_phrase(outcome)
    lower = text.lower()
    for verb in STOP_VERBS:
        if lower.startswith(verb + " "):
            text = text[len(verb) :].strip()
            break
    # Keep the noun phrase short and readable.
    text = re.sub(r"^(the|a|an)\s+", "", text, flags=re.IGNORECASE)
    words = text.split()
    if len(words) > 7:
        text = " ".join(words[:7])
    return text.lower()


def learning_concepts(lab: dict) -> list[str]:
    category = str(lab.get("category") or "general")
    values = list(CATEGORY_CONCEPTS.get(category, CATEGORY_CONCEPTS["general"]))
    title = clean_phrase(str(lab.get("title") or ""))
    if title:
        values.append(title.lower())
    for outcome in lab.get("learning_outcomes") or []:
        candidate = concept_from_outcome(str(outcome))
        if candidate and len(candidate.split()) >= 2:
            values.append(candidate)
    return dedupe(values)[:5]


def slug_tokens(slug: str) -> list[str]:
    parts = [part for part in slug.split("-") if part and not part.isdigit()]
    # Drop the track prefix when it is the first token.
    if parts:
        parts = parts[1:] if len(parts) > 1 else parts
    return parts


def competency_tags(lab: dict, slug: str) -> list[str]:
    category = str(lab.get("category") or "general")
    prefix = CATEGORY_PREFIX.get(category, "foundations")
    values = []
    tokens = slug_tokens(slug)
    if tokens:
        values.append(prefix + "." + "_".join(tokens))
        if len(tokens) >= 2:
            values.append(prefix + "." + "_".join(tokens[-2:]))
    for skill in lab.get("mapped_skills") or []:
        skill = str(skill).strip().lower()
        if skill:
            values.append(skill.replace("_", "."))
    values.append(prefix + ".fundamentals")
    return dedupe(sanitize_tag(value) for value in values if value)[:5]


def defensive_skills(lab: dict) -> list[str]:
    category = str(lab.get("category") or "general")
    text = str(lab.get("defensive_takeaways") or "")
    values = []
    for chunk in re.split(r"[.;,]| and ", text):
        phrase = clean_phrase(chunk)
        if not phrase:
            continue
        words = phrase.split()
        if len(words) < 2 or len(words) > 12:
            continue
        values.append(snake(phrase))
    if len(values) < 3:
        values.extend(CATEGORY_DEFENSIVE.get(category, CATEGORY_DEFENSIVE["general"]))
    return dedupe(values)[:5]


def evidence_required(lab: dict) -> list[str]:
    category = str(lab.get("category") or "general")
    difficulty = str(lab.get("difficulty") or "beginner")
    values = ["flag"]
    values.extend(CATEGORY_EVIDENCE.get(category, CATEGORY_EVIDENCE["general"]))
    if difficulty in {"advanced", "expert"}:
        values.append("report")
    return dedupe(values)[:5]


def report_questions(lab: dict) -> list[str]:
    category = str(lab.get("category") or "general")
    first = CATEGORY_QUESTIONS.get(category, CATEGORY_QUESTIONS["general"])
    return [
        first,
        "What does the evidence not prove?",
        "Which control would have prevented or detected the issue?",
        "What would you record before escalating?",
    ]


def dedupe(values) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def sanitize_tag(value: str) -> str:
    value = value.lower().replace("-", "_").replace(" ", "_")
    value = re.sub(r"[^a-z0-9_.]", "", value)
    value = re.sub(r"_+", "_", value).strip("._")
    return value


def snake(value: str) -> str:
    value = value.lower().replace("-", "_")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


def render_block(lab: dict, slug: str, missing: list[str]) -> str:
    generated = {
        "learning_concepts": learning_concepts(lab),
        "competency_tags": competency_tags(lab, slug),
        "defensive_skills": defensive_skills(lab),
        "evidence_required": evidence_required(lab),
        "report_questions": report_questions(lab),
    }
    lines = []
    for field in missing:
        lines.append(f"{field}:")
        for value in generated[field]:
            lines.append(f"  - {json.dumps(value, ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def insert_fields(path: Path, lab: dict, slug: str, missing: list[str]) -> bool:
    text = path.read_text(encoding="utf-8")
    block = render_block(lab, slug, missing)
    lines = text.splitlines(keepends=True)
    insert_at = None
    for index, line in enumerate(lines):
        if line.rstrip("\n") == "mitre_attack:":
            insert_at = index
            break
    if insert_at is None:
        for index, line in enumerate(lines):
            if line.rstrip("\n") == "owner:":
                insert_at = index
                break
    if insert_at is None:
        text = text.rstrip("\n") + "\n\n" + block
    else:
        before = "".join(lines[:insert_at])
        after = "".join(lines[insert_at:])
        if before and not before.endswith("\n"):
            before += "\n"
        text = before + block + "\n" + after
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--lab", action="append", default=[])
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("choose --check or --write")

    paths = sorted(LABS.rglob("lab.yaml"))
    if args.lab:
        wanted = set(args.lab)
        paths = [path for path in paths if path.parent.name in wanted]

    changed = []
    complete = 0
    for path in paths:
        lab = load(path)
        slug = path.parent.name
        missing = [field for field in FIELDS if lab.get(field) in (None, "", [])]
        if not missing:
            complete += 1
            continue
        changed.append((slug, missing))
        if args.write:
            insert_fields(path, lab, slug, missing)

    print(f"labs={len(paths)} complete={complete} changed={len(changed)}")
    for slug, missing in changed[:20]:
        print(f"  {slug}: {', '.join(missing)}")
    if len(changed) > 20:
        print(f"  ... {len(changed) - 20} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
