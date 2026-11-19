# AI governance and security pathway

Status: **proposal** (18 November 2026). Complements the existing AI track and
[AI security agentic labs](AI-SECURITY-AGENTIC-LABS.md).

The current AI track teaches prompt injection, jailbreak policy bypass, and
indirect prompt injection. Those are necessary but not sufficient. Employers
will also ask who owns the AI system, what data it may touch, how its risk was
assessed, how consent and retention were handled, and how an agent's tools are
constrained.

This pathway treats AI security as **governance plus engineering**. A learner
must be able to write the policy, test the control, and produce the evidence.

## 1. Outcomes

By the end of the pathway a learner can:

- inventory an AI system and assign an accountable owner;
- classify its data and document consent, retention, and residency;
- perform a model-risk assessment using NIST AI RMF and ISO/IEC 42001;
- test for prompt injection, data leakage, poisoning, and unsafe output;
- design an agent permission model with least privilege and human approval;
- produce audit evidence and an incident report for an AI system;
- brief a CIO, a privacy officer, and an engineer at the right level of detail.

## 2. Frameworks and references

| Framework | Use in the pathway |
|---|---|
| **NIST AI RMF 1.0** | Govern, Map, Measure, Manage structure for risk work |
| **NIST AI 600-1** | Generative AI risk profile and suggested actions |
| **ISO/IEC 42001** | AI management system, objectives, roles, continual improvement |
| **ISO/IEC 23894** | AI risk management guidance |
| **NIST CSF 2.0** | Link AI controls to the institution's security programme |
| **MITRE ATLAS** | Adversary tactics and techniques against AI systems |
| **OWASP Top 10 for LLM Applications** | Prompt injection, sensitive disclosure, excessive agency, supply chain |
| **EU AI Act** | High-risk classification, transparency, human oversight, post-market monitoring |
| **Institution policy** | Consent, retention, classification, data residency, procurement |

The pathway is not legal advice. It teaches learners to find the applicable
obligation, document the decision, and escalate to the accountable owner.

## 3. Modules

### Module 1 — AI system inventory and accountability

- Build an AI system register: purpose, owner, users, data, model, vendor,
  deployment location, autonomy level, and affected people.
- Classify each system by risk tier using the institution's criteria.
- Define the accountable owner and the review cadence.
- Evidence: completed register entry, risk tier, owner sign-off.

### Module 2 — Model risk management

- Write a model card and a data card.
- Identify assumptions, limitations, failure modes, and drift indicators.
- Define validation tests and acceptance thresholds.
- Record a review decision: approve, approve with conditions, or reject.
- Evidence: model card, validation plan, risk register entry, decision record.

### Module 3 — Data protection, consent, retention, and residency

- Classify the data used in prompts, retrieval, fine-tuning, and logs.
- Document consent and the withdrawal path.
- Set retention for prompts, outputs, embeddings, and evaluation data.
- Record where data is processed and stored.
- Identify leakage paths: logs, provider retention, vector stores, browser
  caches, and support exports.
- Evidence: data-flow diagram, consent record, retention schedule, residency
  note.

### Module 4 — Prompt injection and output handling

- Test direct and indirect prompt injection against a local mock assistant.
- Treat retrieved content and model output as untrusted input.
- Encode or allowlist output before it reaches HTML, SQL, shell, or a file path.
- Add a regression test for the injection case.
- Evidence: test transcript, fix, regression test, residual risk.

### Module 5 — Model and data poisoning, supply chain

- Trace the model, adapter, dataset, and dependency provenance.
- Verify checksums and signatures where available.
- Detect label flips, backdoor triggers, and poisoned retrieval content.
- Apply an allowlist for model and dataset sources.
- Evidence: provenance record, verification result, detection test.

### Module 6 — Agent security

- Map each tool and data source the agent can reach.
- Apply least-privilege scopes and tenant isolation.
- Require human approval for irreversible, financial, or high-impact actions.
- Sandbox tool execution and log every call.
- Test excessive agency, confused deputy, and cross-tenant retrieval.
- Evidence: tool permission matrix, approval path, audit log, abuse test.

### Module 7 — AI compliance evidence

- Map controls to NIST AI RMF and ISO/IEC 42001.
- Collect evidence that the control operated: logs, approvals, test results,
  review records.
- Run an AI impact assessment for a high-risk use case.
- Prepare an audit response and a corrective action plan.
- Evidence: control matrix, evidence pack, impact assessment, audit response.

### Module 8 — AI incident response and capstone

Scenario: a patient-facing assistant begins disclosing another patient's
information after a retrieval index is misconfigured.

The learner must:

1. triage the disclosure and preserve evidence;
2. contain the assistant and revoke the affected credentials;
3. identify the data, consent, and retention impact;
4. decide whether notification is required with the privacy officer;
5. fix the retrieval isolation and add a regression test;
6. write the technical report and the executive summary;
7. update the risk register and the model card.

Evidence: timeline, containment record, impact assessment, fix, regression
test, reports, and updated register.

## 4. Lab map

| Lab | Primary skill | Evidence |
|---|---|---|
| AI system register | Governance | Register entry and owner |
| Model card and risk tier | Model risk | Model card, risk tier |
| Consent and retention review | Privacy | Data-flow, consent, retention |
| Prompt injection regression | AI security | Test, fix, regression |
| Poisoned retrieval | Supply chain | Provenance, detection |
| Agent permission matrix | Agent security | Scope matrix, approval path |
| AI impact assessment | Compliance | Assessment and evidence pack |
| Patient AI disclosure capstone | IR and communication | Timeline, reports, register update |

The first four are low-cost and can reuse the existing AI mock services. The
agent and capstone labs need a retrieval mock and a tool sandbox, which can run
locally without a real model provider.

## 5. Mapping to employer gaps

| Gap | Modules |
|---|---|
| Cloud and AI security operations | 4, 5, 6 |
| Detection engineering | 4, 5, capstone |
| Threat hunting | 5, capstone |
| Incident response | 8 |
| Identity and access management | 6 |
| Security automation | 4, 6 |
| Vulnerability management | 2, 5 |
| Security architecture | 1, 2, 6 |
| GRC and compliance | 1, 3, 7 |
| Communication | 7, 8 |

## 6. Achievements

- **AI System Steward** — inventory, owner, risk tier, and model card.
- **Prompt Injection Defender** — injection test, fix, and regression.
- **Agent Security Architect** — permission matrix and abuse test.
- **AI Compliance Analyst** — control matrix and evidence pack.
- **AI Incident Responder** — capstone timeline and reports.

These follow the existing achievement catalogue metadata and should use the
`tracks` group with gold or platinum tiers.

## 7. Safety and ethics

- Use synthetic patient records and clearly fake identifiers.
- Do not use a real model provider or real API keys in the labs.
- Do not train on real personal data.
- Do not present the output as a clinical, hiring, admissions, or disciplinary
  decision. The scenario is about the control, not the model's opinion.
- Make the limitation visible in the UI and the report.
- Provide a consent and erasure path for any learner-generated content.
- Keep human review in the loop for every high-impact action.

## 8. Implementation phases

1. **Phase 1 — governance labs.** Register, model card, risk tier, consent and
   retention review. No new runtime.
2. **Phase 2 — AI security labs.** Reuse the existing prompt-injection mock;
   add output-handling and poisoning cases.
3. **Phase 3 — agent lab.** Add a retrieval mock and a tool sandbox with
   explicit scopes and approval.
4. **Phase 4 — capstone.** Add the patient disclosure scenario, evidence pack,
   and achievement metadata.

## 9. Acceptance criteria

- A learner can complete the governance modules without a real AI vendor.
- Every security lab has a failing test, a fix, and a regression test.
- Every governance lab produces an artifact an auditor could inspect.
- The capstone requires a technical report and an executive summary.
- No real patient data, model credential, or provider account is used.
- The pathway maps every lab to NIST AI RMF and at least one other framework.

## 10. Open decisions

- Which institution policy will the labs use for consent and retention?
- Is the agent lab local-only, or does it use a small self-hosted model?
- Which high-risk use case anchors the capstone: patient support, student
  advising, or hiring assistance?
- Who reviews the AI impact assessment in the teaching scenario?
