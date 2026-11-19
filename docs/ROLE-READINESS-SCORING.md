# Role readiness scoring

Status: **proposal** (18 November 2026). Builds on the existing
[career readiness and GPS](CAREER-READINESS-AND-GPS.md) model and
`platform/backend/app/data/curriculum-roles.yaml`.

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

The goal is not to print a percentage and call it hiring. The goal is to make a
role-level readiness claim **explainable, evidence-backed, verifiable, and
honest about its limits**.

## 1. Example output

| Role | Readiness | Confidence | Gate |
|---|---:|---|---|
| SOC Analyst | 94% | High | Capstone passed; all critical domains above floor |
| GRC Analyst | 89% | High | Evidence pack complete; one domain provisional |
| IAM Analyst | 82% | Medium | Capstone passed; cloud evidence thin |
| Cloud Security Analyst | 86% | Medium | Capstone passed; 78% competency coverage |
| Security Consultant | 78% | Low | Communication evidence incomplete |

The percentage is a **curriculum readiness index**, not a probability of
employment. The confidence and gate columns are as important as the number.

## 2. What the score is built from

The existing five components remain the basis:

| Component | Weight | Source |
|---|---:|---|
| Workbook | 30% | Documentation dimension across the role's critical competencies |
| Lab assessment | 20% | Execution dimension |
| Independent | 20% | Troubleshooting and clean-solve evidence |
| Scenario | 10% | Communication and team-scenario evidence |
| Capstone | 20% | Completed role capstone |

Two additional controls prevent a high score from hiding a weak foundation:

- **Coverage** — the share of the role's critical competencies with evidence.
- **Domain floor** — every critical domain must reach the role's minimum.

A missing component is reported as **provisional**, not silently counted as
zero or as complete.

## 3. Score rules

1. Compute the weighted component score exactly as the existing readiness model
   does.
2. Apply the role's `domain_floor`. If any critical domain is below the floor,
   cap the label at **Developing** even when the weighted score is high.
3. Apply the capstone gate. Without capstone evidence, cap the index at 79.
4. Report coverage. Below 60% coverage, cap the index at 69 and mark it
   provisional.
5. Report confidence:
   - **High** — coverage at least 85%, capstone present, no provisional
     components.
   - **Medium** — coverage 60–84%, or one provisional component.
   - **Low** — coverage below 60%, or more than one provisional component.
6. Round to a whole percent. Never show a decimal that implies precision the
   evidence does not support.
7. Version the formula and store the version with every snapshot.

The caps are deliberate. A learner can be strong in two domains and still not be
ready for a role that requires four.

## 4. Bands

| Index | Label | Meaning |
|---:|---|---|
| 0–59 | Not ready yet | Build the foundations and start the pathway |
| 60–69 | Emerging | Early evidence; gaps are still wide |
| 70–79 | Developing | Broad evidence; capstone or a weak domain is the next step |
| 80–89 | Career ready | Strong curriculum evidence; portfolio and interview prep |
| 90–100 | Highly prepared | Deep, repeated, current evidence; external review recommended |

The label is descriptive. It does not certify, rank, or guarantee employment.

## 5. Explainability

Every score must answer:

- Which components contributed, and with what weight?
- Which evidence is missing or provisional?
- Which critical competencies are below the domain floor?
- Which three actions would raise the score the most?
- When was each piece of evidence last practised?
- Which artifacts can an employer inspect?

Example learner view:

```text
SOC Analyst — 94% (High confidence)
  Workbook        96   ██████████
  Lab assessment  92   █████████░
  Independent     90   █████████░
  Scenario        88   ████████░░
  Capstone       100   ██████████

  Coverage        91% of critical competencies
  Domain floor    passed in every domain
  Strongest       network analysis, Windows triage, log correlation
  Next best move  detection engineering artifact; add one cloud log source
  Evidence        12 artifacts, 1 capstone, 1 team scenario
```

The UI must pair every colour with a text label and sample size. A score without
its evidence is not shown.

## 6. Evidence packet

A role score is only a bridge to hiring if the evidence travels with it. The
learner can generate a shareable **role evidence packet**:

- role, score, formula version, date, confidence, and gate states;
- one-page summary of the strongest evidence;
- three to five artifacts: policy diff, detection rule, incident timeline,
  executive summary, capstone report;
- verification hash for each artifact;
- capstone and team-scenario records;
- a statement that the score is a curriculum index, not an employment
  prediction;
- an expiry date, after which the learner must refresh the packet.

The packet is learner-owned. Sharing is opt-in, time-bound, revocable, and
logged. The employer sees the packet, not the learner's private notes, raw quiz
answers, or full activity history.

## 7. What employers see

| Visible | Private |
|---|---|
| Role, score, confidence, gate states | Raw quiz answers and attempts |
| Artifact titles and hashes | Private notes and draft work |
| Capstone and team-scenario summaries | Account activity and sign-in history |
| Learner-written summary | Other role scores the learner did not share |

The employer view is a review aid. It is not an automated hiring decision and
must not be used as one.

## 8. Validity and fairness

- **Standard setting:** employers and faculty agree what "career ready" means
  for each role before the first public score.
- **Calibration:** sample portfolios are reviewed blind by at least two
  reviewers; disagreement is recorded.
- **Bias review:** test score distributions across cohorts for unexplained
  gaps. Do not use protected attributes in the model.
- **No false precision:** show bands and confidence. A 94% with low confidence
  is misleading.
- **Appeal and correction:** a learner can challenge a missing or wrong
  evidence record.
- **Human decision:** employers must review the packet; the platform must not
  send a score to an employer without learner consent.
- **Accessibility:** the score is available as text and table, not colour alone.
- **Privacy:** aggregate reporting uses the existing small-cohort suppression.

## 9. Data model

Proposed additions:

| Table | Purpose |
|---|---|
| `role_readiness_snapshots` | Role, score, formula version, components, coverage, confidence, gates, created_at |
| `role_evidence_packets` | Learner, role, token hash, expiry, revoked_at, created_at |
| `role_evidence_items` | Packet, artifact type, title, hash, storage reference |
| `employer_packet_views` | Packet, viewer label, viewed_at, IP hash, consent record |

Reuse the existing portfolio and snapshot storage where possible. Do not create a
second document store.

## 10. API shape

```json
{
  "role": "soc-analyst",
  "title": "SOC Analyst",
  "score": 94,
  "band": "highly_prepared",
  "confidence": "high",
  "formula_version": "readiness-2027.1",
  "coverage": 91,
  "components": {
    "workbook": 96,
    "lab_assessment": 92,
    "independent": 90,
    "scenario": 88,
    "capstone": 100
  },
  "gates": {
    "capstone": true,
    "domain_floor": true,
    "coverage_floor": true
  },
  "provisional_components": [],
  "next_actions": [
    "Add one cloud log source to the detection portfolio",
    "Refresh the incident timeline artifact"
  ],
  "packet_available": true
}
```

## 11. Implementation phases

1. **Phase 1 — expose the existing model.** Add a multi-role summary card to the
   Portfolio with score, confidence, gates, and next actions. No new formula.
2. **Phase 2 — caps and confidence.** Add the capstone, coverage, and domain-floor
   rules and the formula version.
3. **Phase 3 — evidence packet.** Generate the learner-owned packet, hashes, and
   expiry.
4. **Phase 4 — employer review pilot.** Time-bound share links, consent, view
   logging, and a reviewer rubric.
5. **Phase 5 — calibration.** Blind review with employers and faculty; publish
   the standard-setting record.

## 12. Acceptance criteria

- A learner can see several role scores with confidence and gates.
- Every score links to the evidence that produced it.
- No score is shown without a text label and sample size.
- A missing capstone or weak domain caps the score and says why.
- A learner can revoke an employer share.
- The packet never exposes secrets, PII, raw answers, or private notes.
- The formula and standard-setting record are versioned.
- The platform does not send a score to an employer without explicit consent.

## 13. The bridge to hiring

The differentiator is not the percentage. It is the **verified evidence packet**
behind it: a role-aligned score, the artifacts, the capstone, the team scenario,
and a human-readable summary that an employer can review in ten minutes.

That is more useful than another certificate, and more honest than a single
"employability" number.
