# Workforce readiness and job matching

Status: **proposal** (18 November 2026). Extends
[role readiness scoring](ROLE-READINESS-SCORING.md) and the
[Cyber Workforce Readiness Framework](CYBER-WORKFORCE-READINESS-FRAMEWORK.md).

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

This is the bridge between the curriculum and a hiring conversation. It maps
evidence to a **job profile**, shows the learner how ready they are for that
profile, and lets an authorised instructor find learners who meet a stated
threshold. It does not make a hiring decision.

## 1. Job profile

A job profile is a versioned, reviewable definition, not a scraped job advert.

```yaml
id: soc-analyst
version: "2027.1"
title: SOC Analyst
family: defensive
level: entry
reviewed_by: "Industry advisory board"
reviewed_at: "2026-11-18"
requirements:
  - capability: soc-operations
    weight: 0.25
    minimum: 75
  - capability: kql
    weight: 0.15
    minimum: 70
  - capability: incident-response
    weight: 0.20
    minimum: 70
  - capability: threat-hunting
    weight: 0.15
    minimum: 65
  - capability: reporting
    weight: 0.15
    minimum: 70
  - capability: mitre-attack
    weight: 0.10
    minimum: 65
gates:
  capstone: true
  team_scenario: true
  evidence_packet: true
```

Every requirement has:

- a capability or competency ID from the existing taxonomy;
- a weight that sums to 1.0;
- a minimum score, so a strong average cannot hide a failed critical skill;
- a gate for capstone, team scenario, or a verified artifact.

## 2. Learner score

Example:

```text
SOC Analyst — 86% ready
  KQL                 92   █████████░
  Incident response   82   ████████░░
  Threat hunting      78   ███████░░░
  Reporting           80   ████████░░
  MITRE ATT&CK        85   ████████░░

  Gates: capstone passed · team scenario passed · packet ready
  Confidence: high
  Top gap: threat hunting evidence is one lab deep
```

The score is a **weighted match** to the profile, with three controls:

1. **Minimum per requirement.** A component below its minimum caps the overall
   result and appears as a blocker.
2. **Coverage.** A requirement with no evidence is reported as unmeasured, not
   as zero.
3. **Confidence.** High, medium, or low based on evidence count, recency, and
   the number of provisional components.

The exact formula uses the existing capability scores; this layer only applies
the profile weights and gates. Store the profile and formula versions with every
snapshot.

## 3. Hiring view

The learner can generate a **job-aligned evidence packet** for one profile. It
contains:

- profile title and version;
- overall match and confidence;
- per-requirement score and the evidence behind it;
- capstone and team-scenario summaries;
- three to five artifacts with hashes;
- a learner-written summary;
- a clear statement that the score is a curriculum match, not a prediction of
  job performance;
- an expiry date and a revocation link.

The employer sees the packet, not the learner's private notes, raw quiz answers,
or full activity history. Sharing is opt-in, time-bound, and logged.

## 4. Instructor filter

The instructor can filter a course or cohort by job profile and threshold:

```text
Students ready for: Cloud Security Analyst
Minimum: 80%     Confidence: medium or high
Include: capstone passed, packet ready

Name      Readiness  Confidence  Top gap                 Packet
Ana       91%        High        Architecture evidence   Ready
Sam       86%        High        GRC evidence            Ready
Lee       82%        Medium      IAM depth               Draft
```

Rules:

- The filter is for support and programme review, not a public ranking.
- The instructor sees only learners they are entitled to see.
- Under-18 learners follow the existing analytics exclusion.
- Small cohorts use the existing suppression rules.
- The filter result is not an automated shortlist. A human reviews the packet.
- The learner can see that their record matched a filter, unless the institution
  has a lawful reason to hide a support review.

## 5. Job profile catalogue

Start with a curated set, reviewed by employers and faculty:

| Profile | Core requirements |
|---|---|
| SOC Analyst | SOC operations, KQL, IR, threat hunting, reporting, ATT&CK |
| GRC Analyst | Control mapping, risk register, audit evidence, communication |
| IAM Analyst | Authentication, RBAC/ABAC, PAM, SSO, access review |
| Cloud Security Analyst | Cloud identity, storage, logging, posture, IR |
| Security Consultant | Architecture, threat modeling, reporting, client communication |
| Detection Engineer | Detection-as-code, Sigma/KQL, telemetry, ATT&CK, testing |
| Incident Responder | Forensics, IR, evidence handling, team scenario, reporting |
| DevSecOps Engineer | Supply chain, CI/CD, containers, automation, SBOM |

The catalogue is versioned. Add a profile only after an employer or advisory
review confirms the requirements and the minimums.

## 6. Labor-market input

Do not scrape job boards into a score without permission and review. Use:

- the industry advisory board;
- a curated sample of public role descriptions with source and date;
- O*NET and NICE work-role mappings where they add useful structure;
- employer interviews and hiring-manager feedback;
- the institution's own graduate outcome data, with consent.

A job profile should record its source, review date, and next review date. A
profile older than 12 months is marked stale and cannot be used for a new
hiring packet until reviewed.

## 7. Data model

| Table | Purpose |
|---|---|
| `job_profiles` | Profile, version, title, family, level, status, review dates |
| `job_profile_requirements` | Profile, capability, weight, minimum, position |
| `job_profile_gates` | Profile, gate type, required, description |
| `job_readiness_snapshots` | Learner, profile, score, confidence, components, gates, formula version |
| `job_evidence_packets` | Learner, profile, token hash, expiry, revoked_at |
| `job_packet_views` | Packet, viewer label, consent record, viewed_at |

Reuse the existing capability scores and evidence packet storage.

## 8. API shape

```json
{
  "profile": "soc-analyst",
  "profile_version": "2027.1",
  "title": "SOC Analyst",
  "score": 86,
  "confidence": "high",
  "requirements": [
    {"capability": "kql", "score": 92, "minimum": 70, "weight": 0.15, "met": true},
    {"capability": "incident-response", "score": 82, "minimum": 70, "weight": 0.20, "met": true},
    {"capability": "threat-hunting", "score": 78, "minimum": 65, "weight": 0.15, "met": true},
    {"capability": "reporting", "score": 80, "minimum": 70, "weight": 0.15, "met": true},
    {"capability": "mitre-attack", "score": 85, "minimum": 65, "weight": 0.10, "met": true}
  ],
  "gates": {"capstone": true, "team_scenario": true, "evidence_packet": true},
  "top_gaps": ["threat hunting depth", "cloud log source"],
  "packet_available": true
}
```

## 9. Fairness and governance

- Do not use protected attributes or proxies for them.
- Do not infer a disability, health condition, immigration status, or financial
  need.
- Do not present the match as a probability of being hired.
- Publish the profile and minimums.
- Calibrate with employers before a live hiring pilot.
- Review false positives and false negatives.
- Keep the learner's packet under their control.
- Provide an appeal and correction path.
- Expire the packet and require a refresh.
- Never send a score to an employer without explicit consent.

## 10. Implementation phases

1. **Phase 1 — curated profiles.** Publish five profiles with requirements,
   weights, minimums, and gates.
2. **Phase 2 — learner score.** Show the profile match, components, confidence,
   and gaps in the portfolio.
3. **Phase 3 — instructor filter.** Add the readiness filter with the privacy and
   suppression rules.
4. **Phase 4 — evidence packet.** Generate the job-aligned packet and the
   revocation path.
5. **Phase 5 — employer pilot.** Time-bound review with a small number of
   employers and a calibration report.

## 11. Acceptance criteria

- A learner can see readiness for several job profiles with confidence and gaps.
- A low critical requirement blocks the overall result and explains why.
- An instructor can filter by profile and threshold without exposing a public
  ranking.
- An employer sees only a consenting learner's packet.
- The profile, formula, and packet are versioned.
- No profile is used after its review date without re-approval.
- The platform never claims the match is a hiring prediction.

## 12. Why this matters

Most programmes can show a transcript. Very few can show a **verified,
role-aligned evidence packet** that an employer can review in ten minutes.

That is the differentiator: not another dashboard, but a defensible bridge
between what the learner can do and what the job requires.
