# Digital Cyber Transcript

Status: **proposal** (18 November 2026). Extends the existing printable
completion transcript, Open Badges plan, and portfolio.

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

The current PDF answers "what did the learner finish?" The Digital Cyber
Transcript answers "what can the learner show, how was it verified, and what role
does it support?"

It is a **evidence record**, not a second certificate mill.

## 1. Transcript sections

```text
Digital Cyber Transcript
  Identity and credential
  Capability profile
  Completed learning
  Generated artifacts
  Framework coverage
  Career readiness
  Capstones and team scenarios
  Achievements
  Verification
```

### Identity and credential

- display name (learner-controlled);
- programme, cohort, and completion date;
- transcript ID and version;
- issuer and verification URL;
- public key or signature reference;
- consent and sharing state.

### Capability profile

Eight capabilities with score, confidence, and evidence count:

```text
SOC operations        93  High    17 evidence items
Detection engineering 90  High     9 evidence items
Incident response     82  Medium   6 evidence items
Cloud security        71  Medium   4 evidence items
IAM                   44  Low      1 evidence item
GRC                   58  Low      2 evidence items
Automation            66  Medium   3 evidence items
Architecture          40  Low      1 evidence item
```

No capability is shown without confidence and evidence count.

### Completed learning

- labs completed, with track, level, difficulty, and clean-solve marker;
- certificates and levels;
- courses and capstones;
- team scenarios and roles;
- total learning time where the evidence supports it.

### Generated artifacts

This is the section that distinguishes the transcript from a completion list:

| Artifact | Count | Example evidence |
|---|---:|---|
| Incident reports | 15 | Timeline, finding, containment, executive summary |
| Threat hunts | 7 | Hypothesis, query, result, ATT&CK mapping |
| Detection queries | 12 | KQL/SPL/Sigma, test result, tuning note |
| Architecture reviews | 3 | Data-flow diagram, trust boundary, finding |
| Risk assessments | 8 | Risk register, likelihood, impact, treatment |
| SBOMs | 2 | CycloneDX/SPDX plus triage |
| Supply-chain reviews | 2 | Signature and provenance verification |
| Team scenarios | 1 | Role record, decision log, debrief |

Each artifact has:

- title, type, date, and course context;
- the competencies and capabilities it evidences;
- a hash and storage reference;
- a review state: self-assessed, peer-reviewed, instructor-reviewed, or
  externally reviewed;
- a visibility state: private, shareable, or public.

A count alone is not evidence. The transcript links to the artifact or its
verification record.

### Framework coverage

Map the evidence to the frameworks the institution uses:

- MITRE ATT&CK techniques;
- NIST CSF 2.0 functions and categories;
- CIS Controls v8;
- ISO/IEC 27001 Annex A controls;
- NIST AI RMF and ISO/IEC 42001 where AI evidence exists;
- OWASP Top 10 and OWASP LLM Top 10 where application evidence exists.

Show coverage as "evidence mapped", not "certified compliant". A learner who
maps a control is not an auditor.

```text
Framework             Evidence items   Coverage
MITRE ATT&CK          34 techniques    Mapped
NIST CSF 2.0          21 categories    Mapped
CIS Controls v8       18 safeguards    Mapped
ISO/IEC 27001:2022    14 controls      Mapped
```

### Career readiness

Role and job-profile matches with confidence and gates:

```text
SOC Analyst            92%  High
Cloud Security Analyst 84%  Medium
GRC Analyst            95%  High
```

The transcript links to the role evidence packet and states that the percentage
is a curriculum match, not a hiring prediction.

### Verification

- transcript ID and version;
- issuer and issuance date;
- content hash;
- signature or JWT-VC reference;
- public verification URL and QR code;
- revocation status and expiry;
- a human-readable statement of what the credential proves.

## 2. Verification model

Reuse the platform's existing signing pattern:

- Ed25519 signing key with a `kid`;
- public JWKS endpoint;
- signed JSON transcript (JWT-VC or a detached signature);
- content hash over the canonical transcript payload;
- status endpoint for active, expired, or revoked;
- rotation that keeps old public keys for verification.

The PDF includes the transcript ID, QR code, and verification URL. The JSON
transcript is the canonical machine-readable record. The web page is the
human-readable view.

## 3. Data model

| Table | Purpose |
|---|---|
| `transcripts` | Learner, version, status, issued_at, expires_at, revoked_at |
| `transcript_sections` | Transcript, section type, payload, order |
| `transcript_artifacts` | Transcript, artifact type, title, hash, storage ref, review state, visibility |
| `transcript_framework_map` | Transcript, framework, item, evidence count, mapping version |
| `transcript_signatures` | Transcript, key id, algorithm, signature, signed_at |
| `transcript_shares` | Transcript, token hash, expiry, revoked_at, consent record |

Reuse existing completion, certificate, portfolio, and readiness data. Do not
copy evidence into a second storage system; store references and hashes.

## 4. Artifact taxonomy

Start with artifact types the platform can already produce or can produce with a
small template:

| Type | Source | Minimum evidence |
|---|---|---|
| Incident report | Capstone or IR lab | Timeline, finding, containment, summary |
| Threat hunt | Hunt lab | Hypothesis, query, result, ATT&CK map |
| Detection query | Quiz/detection lab | Query, test, false-positive note |
| Architecture review | Architecture lab | Diagram, trust boundary, finding |
| Risk assessment | GRC lab | Asset, threat, likelihood, impact, treatment |
| SBOM | Supply-chain lab | SBOM file, scan, triage |
| Team decision record | Team scenario | Role, decision, rationale, time |
| Capstone report | Capstone | Deliverables and review |

If an artifact is missing, show **not generated**, not zero. Do not pad the
transcript.

## 5. Privacy and consent

- The learner controls whether a transcript is shareable.
- The default is private.
- Public transcripts use a pseudonymous subject and the learner's chosen display
  name.
- Never include raw quiz answers, private notes, secrets, flags, VPN keys, PII,
  or another learner's data.
- Under-18 learners follow the existing analytics and sharing restrictions.
- Revocation removes the public view and keeps an audit reference.
- Account deletion revokes the transcript and removes the subject mapping.
- The employer view is time-bound and revocable.

## 6. Output formats

| Format | Use |
|---|---|
| Web page | Learner and employer view, accessible and responsive |
| PDF | Print, advising, portfolio attachment |
| Signed JSON | Machine verification and LMS import |
| Open Badges 3.0 | Portable credentials for achievements and certificates |
| CSV | Programme reporting, with small-cohort suppression |

The PDF must be print-ready: no navigation, no buttons, correct page breaks, and
a clear verification block.

## 7. UI

Profile page:

```text
Digital Cyber Transcript
  [Preview] [Download PDF] [Copy verification link]
  Visibility: Private ▾
  Last updated: 18 Nov 2026

  Capability profile
  Completed learning
  Generated artifacts (15 reports, 7 hunts, 12 queries, ...)
  Framework coverage
  Career readiness
  Verification
```

The artifact list is expandable. Each row shows the type, title, date, review
state, and a link to the evidence. The learner can hide an artifact from the
shareable view without deleting it from their record.

## 8. Relationship to other features

- **Role readiness** supplies the career readiness section.
- **Competency matrix** supplies the capability profile.
- **Portfolio** supplies artifact links and narrative.
- **Open Badges** supplies portable credentials.
- **Workforce readiness** supplies job-profile matches.
- **Multi-student scenarios** supply team decision records.

The transcript is the **read view** over those records, not another scoring
engine.

## 9. Implementation phases

1. **Phase 1 — structured data.** Define the transcript payload and artifact
   taxonomy; generate it from existing completions, certificates, and portfolio.
2. **Phase 2 — artifacts.** Add reviewed artifacts and hashes for the first four
   types: incident report, threat hunt, detection query, risk assessment.
3. **Phase 3 — capability and readiness.** Add the capability profile and role
   matches with confidence and gates.
4. **Phase 4 — verification.** Add signing, public verification, QR, revocation,
   and expiry.
5. **Phase 5 — employer view.** Add time-bound sharing and a review aid, with
   consent and audit.

## 10. Acceptance criteria

- The transcript shows completed learning, artifacts, framework mapping,
  capability profile, and career readiness.
- Every artifact links to evidence and a review state.
- A count is never shown without the artifact type and date.
- The PDF and signed JSON agree.
- A public transcript verifies and can be revoked.
- No secret, flag, PII, raw answer, or private note is exposed.
- Under-18 and small-cohort rules are enforced.
- The learner controls visibility and sharing.

## 11. Anti-patterns

- Counting artifacts that were never reviewed.
- Padding the transcript with every quiz attempt.
- Showing a readiness percentage without confidence and evidence.
- Claiming framework certification from a mapping.
- A public URL that cannot be revoked.
- A PDF that disagrees with the signed JSON.
- Sharing a transcript without the learner's consent.
