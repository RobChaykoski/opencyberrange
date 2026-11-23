# The Trailline Universe

Release 6 uses one fictional employer for its agentic-AI, identity, and GRC
exercises: **Trailline Security & GRC**. Reusing one organisation makes the
scenarios cumulative. A learner who meets Priya Patel in an intake exercise
recognises her again when a service token leaks, and the same audit data has the
same sensitivity in every lab.

All names, domains, records, and credentials in this universe are synthetic.
Nothing here refers to a real company, client, or person.

## Company Profile

| Item | Value |
|---|---|
| Name | Trailline Security & GRC |
| Industry | Cybersecurity advisory, AI governance, cloud compliance |
| Headquarters | Toronto / Windsor-Essex Corridor, Ontario |
| Internal domain | `trailline.internal` |
| Public mock domain | `trailline-grc.test` |
| Identity provider | Keycloak at `auth.trailline.internal` |
| Collaboration | Mattermost at `chat.trailline.internal` |
| Source control | Gitea at `git.trailline.internal` |
| Flagship service | **TrailGuard AI**, a RAG compliance assistant |

TrailGuard reviews vendor SOC 2 reports and client intake questionnaires, drafts
audit summaries, and calls internal tools. It runs as the non-human identity
`svc-trailguard-bot`. That identity has read/write access to the client audit
bucket, which is the architectural weakness the labs explore.

## Personas

| Person | Role | Why they appear |
|---|---|---|
| **Elena Vance** — `e.vance@trailline.internal` | VP of Risk & Compliance | High-privilege approver for vendor onboarding and audit exports |
| **Marcus Chen** — `m.chen@trailline.internal` | Lead AI Governance Architect | Maintains TrailGuard orchestration, tool scopes, and API tokens |
| **Priya Patel** — `p.patel@trailline.internal` | Senior GRC Auditor | Uploads third-party reports into the RAG ingestion folder |
| **svc-trailguard-bot** — `svc-trailguard@trailline.internal` | Non-human service identity | Over-privileged agent account with read/write access to audit buckets |

External counterparties are also fictional. **LumenPay** is the recurring vendor
in the SOC 2 exercises; its operations contact is
`vendor-ops@lumenpay.example`.

## Data Classes

| Class | Examples | Handling |
|---|---|---|
| Client audit records | SOC 2 evidence, control test results, remediation notes | Confidential; export requires Elena's approval |
| Vendor reports | Readiness assessments, questionnaires, PDFs | Confidential; may be uploaded by Priya |
| Agent configuration | System prompts, tool scopes, destination allow-lists | Internal; owned by Marcus |
| Service credentials | `svc-trailguard-bot` tokens, Keycloak clients | Secret; rotate on exposure |

## Lab Conventions

- Lab hostnames use the platform's `.lab` suffix, for example
  `trailguard.lab`, `auth.lab`, and `git.lab`. The narrative domains above are
  used in documents, logs, and email samples.
- The flag is always the internal marker returned by the vulnerable action. It
  is never placed in a visible system prompt, a hint, or a client document.
- Documents are data. No exercise asks the learner to treat retrieved content as
  an instruction.
- Real cloud services, real client data, and real credentials never appear in a
  lab. The services are deterministic mocks or local open-source components.

## Release 6 Story Arc

1. **Foundations** — prompt injection, jailbreak policy, indirect injection
   (`AI01`).
2. **Agentic AI** — a poisoned vendor report drives TrailGuard to export audit
   records (`AI02`).
3. **Non-human identity** — a leaked `svc-trailguard-bot` token allows
   privilege escalation across internal APIs.
4. **Supply chain** — a poisoned model or dependency reaches the TrailGuard
   pipeline.
5. **Detection and response** — automated swarms meet detection-as-code.
6. **Post-quantum migration** — Trailline inventories and upgrades a legacy
   service.

Use this page as the cast list and continuity reference. When a new exercise
needs a person, domain, or service, add it here first so later labs can reuse it.
