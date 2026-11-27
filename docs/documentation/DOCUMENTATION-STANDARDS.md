# Documentation standard

This standard defines how SWOCTS Cyber Range documentation is grouped, labelled,
scored, reviewed, stored, and retired. It applies to every Markdown file under
`docs/`, the root policy set (`SECURITY.md`, `PRIVACY.md`, `CONTRIBUTING.md`,
`LICENSING.md`), and generated documentation unless an exception is recorded in
the register.

It is an **alignment aid**, not a certification. A control claim needs a named
requirement, a date, and evidence. See [Compliance](../COMPLIANCE.md) for the
project rule on control claims.

## 1. What good looks like

1. **One source of truth.** The repository is authoritative; the published site
   is a build. A signed tag and `versions.yaml` win over any page.
2. **One home per document.** Every document belongs to exactly one group in
   [`documentation-map.yaml`](documentation-map.yaml).
3. **Audience first.** A reader can tell from the first screen whether the page
   is for a learner, instructor, operator, developer, auditor, executive, or the
   public.
4. **Evidence over assertion.** Claims name the release, test, control, or
   artifact that proves them. Planned controls are labelled as planned.
5. **No learner rows, secrets, tokens, or real addresses.** The non-negotiables
   in `.opencode/bootstrap.md` apply to documentation as well as exports.
6. **Generated files stay generated.** Regenerate, do not hand-edit, the data
   dictionary, competency contracts, review queue, lab outcomes, NICE matrix,
   API export, and the group pages in `docs/documentation/groups/`.
7. **Review is scheduled, not remembered.** Every reviewed document carries a
   cadence and a next-review date.

## 2. Grouping model

The groups follow the project's bounded contexts and the NIST Cybersecurity
Framework 2.0 functions. They are intentionally broad: a document should be
findable in one click from the [documentation hub](README.md), and the group
should match the reader's job rather than the author's team.

| Group | Questions it answers | NIST CSF 2.0 | Primary NIST SP 800-53 Rev. 5 controls | Owner |
|---|---|---|---|---|
| [Governance, risk and assurance](groups/governance.md) | What is required, who approved it, what evidence exists, how long is it kept? | GV.OC, GV.RM, GV.RR, GV.PO, GV.OV | PM-1, PM-4, PM-9, CA-2, CA-5, CA-7, RA-3, SI-12 | Platform lead with the privacy officer |
| [Architecture, design and decisions](groups/architecture.md) | How is the platform built, what are its interfaces, and why were decisions made? | ID.AM, PR.PS, PR.DS | CM-2, CM-3, CM-4, SA-5, SA-8, SA-11, SI-12 | Architecture lead |
| [Operations and service management](groups/operations.md) | How do we deploy, operate, back up, restore, upgrade, and recover it? | PR.PS, PR.IR, RC.RP | CM-6, CP-10, IR-4, SI-2, SI-4, AU-2, AU-6 | Platform operator |
| [Security engineering and assurance](groups/security.md) | How is access controlled, tenancy isolated, consent enforced, and risk tested? | PR.AA, PR.DS, DE.CM, RS.AN | AC-3, AC-6, AU-2, CA-7, RA-5, SC-7, SI-4, IR-4 | Security lead |
| [Curriculum, learning and assessment](groups/curriculum.md) | What is taught, how is it assessed, and what evidence does a learner produce? | PR.AT, ID.AM | AT-2, PM-5, SA-11 | Curriculum lead |
| [Integrations and ecosystem](groups/integrations.md) | How do SSO, LMS/LTI, OpenGRC, and reporting boundaries work? | GV.SC, ID.IM | SA-9, SR-3, PM-5 | Integration lead |
| [Product, releases and change](groups/product.md) | What changed, what is supported, what is next, and what is the current count? | GV.RR, GV.OV | CM-3, SA-10, SI-12 | Product lead |
| [Research, pilots and community](groups/research.md) | What are we learning, what is proposed, and what is not yet a commitment? | GV.OV, ID.IM | PM-4, PM-9 | Research lead |
| [Archive](groups/archive.md) | What is retained for provenance but is no longer operating guidance? | GV.OV | SI-12, MP-6 | Records custodian |
| [Documentation system](groups/documentation.md) | How is the documentation set itself governed and reviewed? | GV.PO, GV.OV | PM-1, CM-2, SI-12 | Documentation steward |

### Placement rules

- Put a document in the group of the **reader's decision**, not the author's
  skill. A penetration-test results page belongs in Security; a lab walkthrough
  belongs in Curriculum.
- A document that spans groups belongs in the group that owns its **primary
  outcome**, with links from the other group index.
- A superseded document moves to [Archive](../archive/README.md). Do not leave
  two current pages that disagree.
- Generated pages keep their generated group and are never scored by hand.

## 3. Labels

Each register entry carries the following labels. The allowed values are
enforced by `scripts/documentation_map.py`.

| Label | Values | Meaning |
|---|---|---|
| `doc_type` | `policy`, `standard`, `procedure`, `runbook`, `architecture`, `design`, `adr`, `reference`, `report`, `assessment`, `register`, `form`, `index`, `release`, `generated`, `archive` | What kind of document it is. |
| `audience` | `public`, `learner`, `instructor`, `operator`, `developer`, `auditor`, `executive`, `partner` | Who the document is written for. A document may have more than one. |
| `classification` | `public`, `internal`, `confidential`, `restricted` | Handling class, aligned with [Data classification](../DATA-CLASSIFICATION.md). |
| `lifecycle` | `draft`, `active`, `deprecated`, `archived`, `generated` | Where the document is in its life. |
| `sensitivity` | `none`, `pii`, `security`, `credentials`, `learner_evidence` | Extra warning beyond the classification. |
| `review.status` | `unreviewed`, `in_review`, `approved`, `needs_revision`, `retired` | The review decision. |
| `storage.retention` | `R0`..`R5` | Retention class (see section 7). |

Classification does not grant access. Repository permissions, tenant scope,
RBAC, and consent still decide who may read a document or an export.

## 4. Relevance and quality scoring

The form records two different judgements.

### 4.1 Subjective relevance (1-5)

Relevance is the reviewer's judgement of how much the document matters to the
project **now**. It is deliberately subjective and must be explained in one or
two sentences.

| Score | Meaning |
|---:|---|
| 5 | Essential. A current release, control, safety rule, or learner outcome depends on it. |
| 4 | High. Widely used and should stay current; a stale copy causes rework. |
| 3 | Useful. Supports a specific team or decision but is not on the critical path. |
| 2 | Marginal. Historical context or a narrow audience; keep only if cheap. |
| 1 | Obsolete. Supersede, archive, or retire. |

### 4.2 Quality score (0-100)

The quality score is evidence-based and uses fixed weights. A document is not
"approved" without a score and a named reviewer.

| Criterion | Weight | What earns full marks |
|---|---:|---|
| Requirement fit | 25 | Names the requirement or control it serves and links the evidence. |
| Accuracy and currency | 20 | Matches the signed release, `versions.yaml`, current code, and current counts. |
| Completeness | 15 | Purpose, audience, prerequisites, procedure, failure modes, and references are present. |
| Usability and accessibility | 15 | Clear structure, plain language, working links, accessible formats, no dead ends. |
| Traceability | 15 | Links to code, tests, ADRs, labs, controls, and release evidence. |
| Maintenance | 10 | Has an owner, a cadence, a next-review date, and a clear change trigger. |

| Band | Decision |
|---:|---|
| 90-100 | Authoritative. Approve; cite as current evidence. |
| 75-89 | Current. Approve with minor corrections. |
| 60-74 | Needs revision. Keep in use only with the gaps recorded. |
| 40-59 | At risk. Do not cite as evidence until revised. |
| 0-39 | Retire or rewrite. Move to Archive or replace. |

## 5. Review timeline

Review cadence is set by document type and criticality. A shorter cadence wins
when a document is both, for example a deployment runbook that is also a
control evidence source.

| Document type | Default cadence | Next review |
|---|---|---|
| Policy, standard | Annual | 12 months after approval |
| Procedure, runbook | Semiannual | 6 months after approval |
| Architecture, design | Annual | 12 months, or when the design changes |
| ADR | On decision | Never edited after acceptance; superseded ADRs stay in place |
| Reference, register, index | Annual | 12 months, or when the source changes |
| Report, assessment, release | Annual confirm | Immutable after 90 days; confirm or archive |
| Generated | Each release | Regenerated, not reviewed |
| Archive | Biennial | Confirm retention only; no content edits |

**Trigger-based reviews** happen regardless of the calendar:

- a signed release changes behaviour, counts, or the version;
- a security incident, breach, or failed restore drill;
- a control, law, institution policy, or consent model changes;
- a broken-link or publication audit fails;
- 90 days before an accreditation, audit, or procurement submission;
- a reviewer or owner leaves the role.

**Review window.** The reviewer has 10 working days to complete a scheduled
review. If the review cannot be completed, set `review.status: in_review`, keep
the due date, and record the reason. Do not silently move the date.

## 6. NIST-aligned review method

Use the NIST SP 800-53A Rev. 5 assessment methods. They keep the review
evidence-based and repeatable.

| Method | Use it for | Evidence to record |
|---|---|---|
| **Examine** | Documents, records, configurations, logs, and artifacts | File path, commit or tag, hash, screenshot or excerpt |
| **Interview** | Owners, operators, instructors, and reviewers | Role, date, question set, summary, follow-up |
| **Test** | Executing a procedure, link check, restore drill, or control test | Command, environment, result, pass/fail, log |

Record the method and the evidence reference in the form. A finding that cannot
be closed becomes a POA&M item under CA-5 and is tracked in
[Compliance](../COMPLIANCE.md). Continuous monitoring under CA-7 uses the
review register, the link check, the validation report, and the release
evidence.

### Requirement sources to acknowledge

Name at least one source. Use the identifier the source actually publishes.

- **NIST CSF 2.0** (NIST CSWP 29): the function and subcategory, for example
  `GV.PO-01`, `ID.AM-01`, `PR.PS-01`, `DE.CM-01`.
- **NIST SP 800-53 Rev. 5**: the control, for example `PM-1`, `CM-2`, `CM-3`,
  `SA-5`, `SI-12`, `CA-2`, `CA-5`, `CA-7`.
- **NIST SP 800-53A Rev. 5**: the assessment method and procedure used.
- **NIST SP 800-171 Rev. 3**: `03.12.01` assessment, `03.12.02` POA&M,
  `03.12.03` continuous monitoring, `03.12.04` system security plan
  documentation.
- **NIST SP 800-218 (SSDF)**: `PO.1`, `PS.1`, `PW.1` where the document records
  requirements, design, or verification.
- **NIST SP 800-128**: configuration baseline, change control, and documentation
  maintenance.
- **NIST SP 800-37 Rev. 2**: the RMF step the document supports.
- **ISO/IEC 27001:2022 Annex A 7.5**: documented information and control of
  documented information, where the institution uses ISO.
- **Internal**: a Release 6 pillar, an ADR, the competency review guide, the
  retention policy, or a signed release deliverable.

## 7. Storage, publication, and retention

| Store | Role | Rule |
|---|---|---|
| Git repository (`docs/`) | Authoritative source | Branch protection, signed releases, review through pull request. |
| MkDocs site | Published view | Built from the repository; the manual and workbook origins stay separate. See [MkDocs governance](../MKDOCS-GOVERNANCE.md). |
| Release evidence bundle | Proof for a signed tag | Hash recorded in the supply-chain lock and integrity manifest; immutable. |
| OpenGRC | Governance evidence | Stable identifiers, hashes, periods, and aggregate counts only. No learner rows, PCAP, or payloads. |
| `docs/archive/` | Superseded documents | Read-only. Linked from the archive index with the superseding page. |
| Institution archive | Legal hold and disposition | The institution's schedule wins. A legal hold always overrides the defaults. |

### Retention classes

These classes translate the documentation set into the existing
[Retention policies](../RETENTION-POLICIES.md). They do not replace the data
retention rules for learner records.

| Class | Use | Default |
|---|---|---|
| `R0` | Release evidence, signed deliverables, assessment records | Permanent audit evidence |
| `R1` | Policy, standard, control mapping | Current plus 7 years, institution schedule |
| `R2` | Runbook, procedure, operational reference | Current plus 2 years after supersession |
| `R3` | Generated reference, index, working register | Current plus 1 year |
| `R4` | Draft and working notes | 90 days after supersession |
| `R5` | Archive and accepted ADR | Permanent, read-only |

### Handling rules

- `public` documents may be published to the public site.
- `internal` documents stay on the authenticated documentation surface.
- `confidential` documents stay in the repository and are shared only with the
  named audience; never attach them to a public issue.
- `restricted` documents require an explicit owner decision and must not contain
  the secret itself, only its location and handling instructions.
- No document may contain a real learner row, password, token, private key, live
  address, or unredacted screenshot. Use synthetic data.

## 8. Roles

| Role | Responsibility |
|---|---|
| Documentation steward | Keeps the register, group pages, and link checks current; runs the quarterly sample. |
| Group owner | Nominates reviewers, resolves conflicting pages, approves archive moves. |
| Reviewer | Scores the document, records evidence, sets the next review date. |
| Approver | Confirms the decision and accepts any residual gap; cannot be the only reviewer for a restricted document. |
| Records custodian | Applies retention, legal hold, and disposition. |
| All authors | Keep the page in the right group, label it, and update it in the same change as the code or release it describes. |

## 9. Operating the standard

```bash
# Validate the register and generated group pages
python scripts/documentation_map.py --check

# Fail CI when a scheduled review is overdue
python scripts/documentation_map.py --check --fail-on-overdue

# Add new documents with default labels, or refresh generated pages
python scripts/documentation_map.py --write

# Check links before merging a documentation change
python scripts/check-links.py --mkdocs
```

A pull request that adds, moves, renames, or retires a document must update
`documentation-map.yaml` and the relevant group page in the same change. The
Quality workflow runs the register check on every pull request.

## 10. Measures

The steward reports these each quarter:

- group coverage: percentage of documents with an assigned group;
- review coverage: percentage reviewed in the last cadence window;
- overdue reviews, and the oldest overdue item;
- average quality score by group;
- documents scoring below 60, with an owner and a plan;
- broken links and failed publication checks;
- archived documents with no superseding link.

Targets for the first year: 100% grouped, 80% reviewed, zero overdue critical
documents, and every Release 6 evidence page above 75.

## 11. Exceptions

Record an exception in the register rather than leaving a document unlabelled.
An exception names the document, the reason, the compensating control, the
owner, and the expiry date. Generated files and accepted ADRs are the only
standing exceptions to content review.
