# ADR 0005: Release 6 is evidence-first

Status: **Proposed (planning)**
Date: 2026-11-17
Related: [Release 6 scope](../RELEASE-6-SCOPE.md),
[Competency Framework](../COMPETENCY-FRAMEWORK.md),
[Evidence Engine](../EVIDENCE-ENGINE.md)

## Context

Release 5 shipped a competency taxonomy, a contract for every lab, deterministic
flag scoring, Cyber DNA v3, instructor analytics, and signed single-host
operations. Institutions now ask for five things that appear independent:

- high availability and Kubernetes deployments;
- capstone generation from competencies;
- cohort analytics;
- federation with peer institutions;
- an AI mentor.

They are not independent. Every one of them consumes the same competency
vocabulary and the same evidence. Building the visible features first would
produce a capstone that omits competencies, dashboards that report domains
nobody mapped, federation bundles that disagree, and an AI mentor that explains
scores with no evidence behind them.

Cyber DNA is the clearest example. It is defensible only if every competency
observation comes from a reviewed contract and a recorded piece of evidence. A
completion count is not evidence.

## Decision

Release 6 is ordered **competency first, evidence second, intelligence last**:

1. Complete the competency framework: taxonomy, hierarchy, scoring, mappings,
   weightings, review.
2. Build the Evidence Engine: evidence records, rubrics, automated collection,
   instructor review.
3. Build capstones and cohort analytics on that evidence.
4. Add HA and Kubernetes as a deployment profile, not a data-model change.
5. Federate signed definitions, content, rubrics, and capstones. Never learner
   data.
6. Add the AI Mentor only after 1, 2, and 4 are operating with real evidence.

The single-host Compose profile remains the reference deployment. The AI Mentor
does not grade, does not make high-impact decisions, and does not see raw
learner artifacts or PII.

## Consequences

Positive:

- Every downstream feature shares one competency vocabulary and one evidence
  record.
- Cyber DNA, analytics, capstones, and the mentor can cite the same source.
- Federation is a bounded exchange of signed definitions, not a data-sharing
  project.
- Academic review can inspect the rubric and the evidence, not just a score.
- The platform can explain a competency change without a model.

Negative and mitigated:

- **Upfront review work.** The 185 baseline contracts need subject-matter review.
  Mitigation: prioritize by use, publish the queue, and allow documented
  exceptions with an owner and a date.
- **Instructor effort.** Evidence review adds work. Mitigation: automate
  deterministic evidence, reserve human review for artifacts and rubrics, and
  make the queue and calibration visible.
- **Slower visible roadmap.** HA and AI arrive later. Mitigation: the dependency
  order prevents rework; the single-host profile and existing analytics keep
  shipping in the meantime.
- **Governance overhead.** Competency, evidence, federation, and AI boards are
  required. Mitigation: one decision log, one versioning policy, and one release
  gate.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| AI mentor first, evidence later | It would explain scores that are not grounded; it would be a chatbot with a security theme |
| Completion-only analytics | It measures activity, not capability; it cannot support accreditation or competency transcripts |
| Central shared database for federation | Violates privacy-first and data sovereignty; creates a high-value target and a cross-institution data controller problem |
| AI grading | Conflicts with the deterministic scoring contract, Article 22-style human oversight, and the bias evidence we cannot yet produce |
| Kubernetes-first rewrite | Would consume the release without improving the teaching loop; the data model must be stable first |

## Review

This ADR is reviewed with the Release 6 scope. A change to the order requires a
new ADR that names the dependency it breaks and the evidence that replaces it.
