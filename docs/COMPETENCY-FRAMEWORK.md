# Competency Framework

Status: **Release 6 foundation, planning.** The taxonomy and lab contracts exist
in Release 5; this page defines what Release 6 must complete before evidence,
capstones, analytics, federation, or AI can be trusted.

The rule is simple: **every object maps to a competency.** A workbook, lab, quiz,
assessment, capstone, and badge that cannot name the competency it develops is
not ready for Release 6.

## Current state

| Piece | Release 5 state |
|---|---|
| Taxonomy | 212 competencies across domains and categories (`app/data/competency-taxonomy.yaml`) |
| Lab contracts | 215 labs mapped; **25 reviewed**, **190 baseline derived** (`app/data/competency-contracts.yaml`) |
| Scoring | Five dimensions: knowledge 20%, execution 30%, troubleshooting 20%, documentation 15%, communication 15% |
| Pathways | 13 curriculum roles with critical competencies and capstone briefs (`app/data/curriculum-roles.yaml`) |
| Mapping | Chapter, track, category, and primary-axis mapping (`app/data/competency-mapping.yaml`) |
| Credentials | Level certificates and Open Badges 3.0 scope |
| Evidence | Completion, attempt, hint, quiz, workbook, and snapshot records |

The 190 baseline-derived contracts are listed, with their competencies and
evidence types, in the [competency-contract review queue](COMPETENCY-REVIEW-QUEUE.md).

The taxonomy is real and the scoring model is defined. The gap is coverage,
hierarchy, versioning, and object mapping.

## Deliverables

### 1. Competency taxonomy

A stable, versioned vocabulary. Every competency has:

| Field | Meaning |
|---|---|
| `id` | Stable identifier such as `NET-031`; never reused |
| `domain` | Group such as Network, Forensics, Incident Response, SOC, Professional |
| `category` | Sub-group such as Protocol Analysis or Host Forensics |
| `name` | Short human label |
| `definition` | What a learner must be able to do |
| `observable_verbs` | Verifiable actions (identify, extract, correlate, document, remediate) |
| `proficiency_levels` | Descriptors for each level |
| `crosswalks` | NICE work role, CS2023 knowledge area, CAE-CD outcome, and SFIA 9 skill/level where applicable |
| `version` | Semantic version of the definition |

### 2. Skill hierarchy

The taxonomy becomes a hierarchy rather than a flat list:

```text
Domain
  Category
    Competency
      Skill / observable
        Evidence type
```

Example:

```text
Windows Event Analysis
├─ Log Analysis
│  ├─ Parse Security, System, and PowerShell logs
│  ├─ Correlate 4624, 4625, 4688, and 4104 events
│  └─ Explain normal versus abnormal log volume
├─ Detection Engineering
│  ├─ Write a Sigma rule from an observed behaviour
│  ├─ Test the rule against benign and malicious samples
│  └─ Document false positives and tuning
├─ Incident Response
│  ├─ Build a host timeline from event and file artifacts
│  ├─ Identify persistence and lateral movement
│  └─ Recommend containment and eradication
└─ Evidence Collection
   ├─ Preserve logs with a hash and chain of custody
   ├─ Record the tool, command, and timestamp
   └─ Attach the artifact to the finding
```

### 3. Competency scoring model

Keep the five dimensions and make the rules explicit:

| Dimension | Weight | Evidence |
|---|---:|---|
| Knowledge | 20% | Quiz attempts, best score per lab |
| Execution | 30% | Hands-on completions, clean solves, advanced labs |
| Troubleshooting | 20% | Clean-solve share plus advanced-lab bonus |
| Documentation | 15% | Workbook answers mapped to a chapter |
| Communication | 15% | Capstone or repeated written evidence |

Rules:

- A score is **provisional** when any dimension has no evidence.
- The weighted score is renormalised over the dimensions with evidence, and the
  API reports coverage.
- A competency is **validated** only when the score is at least 60 **and** a
  workbook, capstone, or instructor-reviewed evidence record exists.
- A single completion cannot validate a competency.
- Every score reports the formula version, evidence count, and confidence.
- Rating labels (Not Ready, Emerging, Developing, Career Ready, Highly Prepared)
  are curriculum labels, not grades or employment predictions.

### 4. Learning outcome mappings

Every object carries a mapping:

| Object | Required mapping | Weighting | Evidence produced |
|---|---|---|---|
| Workbook chapter | Competencies and skills | Documentation dimension | Analyst answers, reflections |
| Lab | Reviewed competency contract | Execution and troubleshooting | Flag, validation step, artifact |
| Quiz | Knowledge competencies | Knowledge dimension | Attempt and best score |
| Assessment | Rubric criteria and competencies | Configurable | Rubric-scored artifact |
| Capstone | Critical competencies and deliverables | Capstone component (20% of readiness) | Timeline, findings, remediation, brief |
| Badge | Competency threshold and evidence rule | None | Credential metadata |

A CI check must fail when a lab, quiz, assessment, capstone, or badge has no
mapping, or when a mapping points at an unknown competency.

### 5. Assessment weightings

Weightings are configuration, not code:

- Dimensions: the five weights above.
- Object types: workbook 30%, lab assessment 20%, independent work 20%, scenario
  10%, capstone 20% (the existing readiness model).
- Role profiles: level targets such as Gold 75, Silver 60, Bronze 45.
- Capstones: integration weight set per role and validated against the critical
  competency list.

Changing a weight creates a new formula version. Old snapshots keep the version
they were computed with.

## Review queue

The 190 baseline contracts already carry competency IDs, weights, evidence
weights, prerequisites, duration, and reliability. Release 6 completes the
subject-matter review:

1. Prioritize by recorded completions and pathway exposure.
2. Review the contract against the lab, workbook, and harness.
3. Run the live harness three times.
4. Set `review_status: reviewed`, `reviewed_at`, and the reliability rationale.
5. Regenerate the contracts and record the change.

`docs/COMPETENCY-CONTRACTS.md` is the working queue.

## Versioning and governance

- **Version format:** `YYYY.N` for the taxonomy and `1.0` for a bundle. A
  breaking change is a major bundle version.
- **Change log:** every added, renamed, merged, split, or deprecated competency.
- **Deprecation:** keep the old ID as an alias for at least one release so
  historical evidence still resolves.
- **Calibration:** two reviewers score a sample of evidence; report agreement
  and refine descriptors.
- **Signed bundles:** the taxonomy, contracts, and mappings export as a signed
  bundle for federation.

## Acceptance criteria

- 215 of 215 labs have a reviewed contract, or a documented exception with an
  owner and a date.
- 100% of workbooks, quizzes, assessments, capstones, and badges have a mapping.
- A read API exposes the taxonomy and mappings with a version and a change log.
- Crosswalks exist for NICE work roles, CS2023 knowledge areas, CAE-CD
  outcomes, and SFIA 9 skills and responsibility levels where a credible mapping
  exists; gaps are explicit.
- SFIA 9 content follows the licensing and review gates in
  [SFIA 9 ingestion](SFIA-9-INGESTION.md); no skill definitions or mappings are
  added before a commercial or academic product licence permits embedding SFIA
  content and publishing the mapping. The personal licence is not sufficient.
- No competency score can be produced without evidence, and no validated score
  can be produced from one completion.
- CI fails on an unmapped object, an unknown competency, or a stale contract.

## Why this comes first

Capstones, analytics, federation, and the AI mentor all consume the same
vocabulary. If the vocabulary is incomplete, the capstone omits a competency,
the dashboard reports a domain nobody mapped, the federation bundle disagrees
with its peer, and the AI mentor explains a score that was never grounded. The
competency model is the contract the rest of Release 6 depends on.
