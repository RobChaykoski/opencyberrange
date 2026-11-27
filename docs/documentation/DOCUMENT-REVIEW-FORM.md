# Document review form

Use this form for a scheduled review, a release-gate review, or an ad-hoc review
of a document in [`documentation-map.yaml`](documentation-map.yaml). Copy the
form into the review issue or record, or open the GitHub issue form
`.github/ISSUE_TEMPLATE/documentation-review.yml`. The standard that defines the
labels, weights, cadence, and storage is
[Documentation standard](DOCUMENTATION-STANDARDS.md).

Do not paste learner rows, credentials, tokens, private keys, or live addresses
into a review record. Record the location and handling instead.

---

## 1. Document identity

| Field | Value |
|---|---|
| Title | |
| Repository path | `docs/` |
| Register path (exact) | `docs/...` |
| Group | |
| Document type | |
| Version or release reviewed against | |
| Commit or signed tag | |
| Owner | |
| Review date | `YYYY-MM-DD` |
| Reviewer | |
| Approver | |

## 2. Requirement acknowledgment

State the requirement this document serves. Name the source and the exact
identifier. One primary requirement is enough; add secondary ones only when the
document genuinely provides evidence for them.

| Requirement source | Identifier | How the document satisfies it | Evidence reference |
|---|---|---|---|
| NIST CSF 2.0 | e.g. `GV.PO-01` | | |
| NIST SP 800-53 Rev. 5 | e.g. `PM-1`, `SI-12` | | |
| NIST SP 800-171 Rev. 3 | e.g. `03.12.04` | | |
| NIST SP 800-218 (SSDF) | e.g. `PW.1` | | |
| ISO/IEC 27001:2022 A.7.5 | | | |
| Internal (Release 6, ADR, policy) | | | |

**Acknowledgment.** I have read the document and confirm that the requirement
statement above is accurate for the review date. I understand that a control
claim without evidence is not an approval.

- [ ] Acknowledged by the reviewer.
- [ ] The evidence reference is reachable and points to the reviewed commit or
  signed tag.
- [ ] Any planned or partial control is labelled as planned or partial.

## 3. Subjective relevance

**Project relevance statement (2-4 sentences).** Explain why this document
matters to the project now. Name the audience and the outcome or decision it
supports. If it supports a Release 6 pillar, name the pillar.

> 

**Relevance score (1-5).** Circle one and justify it in one sentence. The rubric
is in [Documentation standard](DOCUMENTATION-STANDARDS.md#41-subjective-relevance-1-5).

| 1 Obsolete | 2 Marginal | 3 Useful | 4 High | 5 Essential |
|---|---|---|---|---|
| | | | | |

**Justification.**

> 

## 4. Quality score (0-100)

Score each criterion, then add the weighted points. Do not award a score without
naming the evidence you examined.

| Criterion | Weight | Score (0-1) | Weighted points | Evidence examined |
|---|---:|---:|---:|---|
| Requirement fit | 25 | | | |
| Accuracy and currency | 20 | | | |
| Completeness | 15 | | | |
| Usability and accessibility | 15 | | | |
| Traceability | 15 | | | |
| Maintenance | 10 | | | |
| **Total** | **100** | | | |

**Band.** Select one: `90-100 authoritative` / `75-89 current` / `60-74 needs
revision` / `40-59 at risk` / `0-39 retire or rewrite`.

**Findings.** List each gap as `[severity] finding → evidence → action → owner →
due date`. Severity is `critical`, `major`, `minor`, or `observation`.

| # | Severity | Finding | Evidence | Action | Owner | Due |
|---:|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |

## 5. Review timeline

| Field | Value |
|---|---|
| Cadence (`quarterly`, `semiannual`, `annual`, `biennial`) | |
| Last reviewed | `YYYY-MM-DD` |
| Next review due | `YYYY-MM-DD` |
| Review window (working days) | 10 |
| Trigger reviewed (release, incident, control change, audit, other) | |
| Supersedes / superseded by | |
| Archive date (if retiring) | `YYYY-MM-DD` or `n/a` |

**Calendar triggers to check.**

- [ ] A signed release changed behaviour, counts, or the version.
- [ ] A security incident, privacy event, or failed restore drill occurred.
- [ ] A control, law, institution policy, or consent model changed.
- [ ] A link, publication, or accessibility check failed.
- [ ] An audit, accreditation, or procurement submission is within 90 days.
- [ ] The owner or reviewer changed role.

## 6. Labels

| Label | Value | Notes |
|---|---|---|
| `doc_type` | | |
| `audience` | | |
| `classification` | `public` / `internal` / `confidential` / `restricted` | Align with [Data classification](../DATA-CLASSIFICATION.md). |
| `lifecycle` | `draft` / `active` / `deprecated` / `archived` / `generated` | |
| `sensitivity` | `none` / `pii` / `security` / `credentials` / `learner_evidence` | |
| `review.status` | `approved` / `needs_revision` / `retired` | |
| `storage.retention` | `R0`-`R5` | See [Documentation standard](DOCUMENTATION-STANDARDS.md#7-storage-publication-and-retention). |

**Handling check.**

- [ ] The classification matches the most sensitive content in the document.
- [ ] The document contains no learner row, credential, token, private key, or
  live address.
- [ ] Screenshots and examples use synthetic data.
- [ ] A `restricted` document names the owner and the handling instruction but
  does not contain the secret itself.

## 7. Storage and publication

| Field | Value |
|---|---|
| Authoritative source | `git` |
| Repository path | `docs/...` |
| Published location | MkDocs page / URL, or `not published` |
| Release evidence bundle | Path or hash, or `n/a` |
| OpenGRC evidence reference | Stable ID or hash, or `n/a` |
| Archive location | `docs/archive/...`, or `n/a` |
| Retention class and period | |
| Legal hold | `yes` / `no` |
| Access restriction | Public / authenticated / named group |

**Publication check.**

- [ ] The source of truth is the repository, not the published site.
- [ ] `python scripts/check-links.py --mkdocs` passes for the changed pages.
- [ ] The page is in the correct group index.
- [ ] If published, the page follows the [MkDocs governance](../MKDOCS-GOVERNANCE.md)
  rules and the correct origin (manual or workbook).
- [ ] If retired, the archive page links to the superseding document.

## 8. NIST review method and evidence

Record what the review actually did. Do not mark a method as used if it was not.

| Method | Used | Evidence |
|---|---|---|
| **Examine** (documents, records, configurations, logs) | `yes/no` | |
| **Interview** (owner, operator, instructor, reviewer) | `yes/no` | |
| **Test** (procedure run, link check, restore drill, control test) | `yes/no` | |

**Assessment notes.** Summarise the examine/interview/test results and link the
supporting evidence. If a finding cannot be closed, open a POA&M item under
CA-5 and record the reference.

> 

## 9. Decision and sign-off

| Decision | Select |
|---|---|
| Approve as authoritative | |
| Approve with minor corrections | |
| Revise and re-review | |
| Retire and archive | |
| Escalate to the group owner | |

**Conditions or residual risk.**

> 

**Reviewer sign-off.** Name, role, date.

> 

**Approver sign-off.** Name, role, date. The approver must not be the only
reviewer for a `restricted` document.

> 

---

## 10. Register update

Paste the completed values into the matching entry in
[`documentation-map.yaml`](documentation-map.yaml), then run:

```bash
python scripts/documentation_map.py --check
```

```yaml
# Replace the matching path entry in documentation-map.yaml.
- path: docs/EXAMPLE.md
  group: governance
  doc_type: standard
  audience: [developer, auditor]
  classification: internal
  lifecycle: active
  sensitivity: [none]
  review:
    status: approved
    cadence: annual
    last_reviewed: "2026-11-26"
    next_review: "2027-11-26"
    reviewer: "Reviewer name"
    approver: "Approver name"
  relevance: 4
  score: 86
  requirements:
    - source: NIST SP 800-53 Rev. 5
      id: PM-1
      evidence: docs/documentation/DOCUMENTATION-STANDARDS.md
  storage:
    source: git
    published: true
    evidence: true
    retention: R1
```
