# Employer capability gaps

Status: **planning** (18 November 2026). This page connects employer feedback to
the curriculum. It is not a release commitment.

The consistent complaint is not a lack of theory. It is that graduates cannot
perform operational work on day one. The ten gaps below are the working list.
Existing coverage is acknowledged so the roadmap does not pretend to start from
zero.

## 1. The ten gaps

| Rank | Gap | What employers want | Current coverage | Next move |
|---:|---|---|---|---|
| 1 | Cloud security | Secure Azure/AWS/GCP, review IAM, analyse cloud logs, investigate cloud incidents | Simulated cloud design; Identity track; AppSec cloud labs | Cloud range labs 1–10 |
| 2 | Detection engineering | SIEM detections, KQL/Sigma/SPL, tuning, false positives | Suricata, log analysis, quiz bank, detection pathway notes | Sentinel-like detection labs |
| 3 | Threat hunting | ATT&CK-led hunts using logs, EDR, intelligence | Network tap, log correlation, OSINT, Cyber DNA investigation proxy | Hunt labs with evidence |
| 4 | Incident response | Lead investigations, triage, evidence, reports, containment | Forensics track, IR competencies, multi-student design | IR capstone and team scenario |
| 5 | Identity and access | RBAC/ABAC, PAM, SSO, Conditional Access, MFA | Identity track (3 labs), Keycloak in cloud range | Expand to 8 identity labs |
| 6 | Security automation | Python, PowerShell, APIs, Logic Apps, SOAR | Automation is implicit in some labs | Automation pathway |
| 7 | Vulnerability management | CVSS, EPSS, KEV, business impact, exposure, prioritisation | Scanner labs, AppSec, Wazuh/OpenSearch plan | Prioritisation labs |
| 8 | Security architecture | Threat modelling, reviews, trust boundaries, secure design | Architecture is mostly implicit | STRIDE/PASTA and review labs |
| 9 | GRC and compliance | Map controls to frameworks and collect evidence | Question banks, risk/GRC content, transcript design | Control-to-evidence labs |
| 10 | Communication | Executive summaries, risk reports, audit evidence, incident updates | Workbook answers, reports, portfolio | Communication index and capstones |

## 2. The five hardest-to-hire skills

These should become the core pillars of the 2027 programme:

1. **Microsoft Sentinel + KQL** — or the local equivalent: OpenSearch, Wazuh,
   Sigma, and a query language.
2. **Cloud security** — Azure/AWS identity, storage, logging, and incident
   response.
3. **Identity security** — Entra ID/IAM/PAM concepts, with Keycloak as the local
   identity provider.
4. **Threat detection and hunting** — telemetry, ATT&CK, hypotheses, evidence.
5. **Security automation** — Python/API/SOAR, tested and reviewed.

The platform does not need a real cloud account to teach these. It needs a
credible simulation, a rubric, and evidence.

## 3. Programme shape

```text
Year 1 foundations
  network, Linux, Windows, web, high-school, digital safety
      |
Year 2 pathways
  detection, IR, identity, cloud, automation, GRC, architecture
      |
Year 3 applied
  AI governance, supply chain, capstones, team scenarios
      |
Portfolio
  artifacts, transcript, role readiness, employer packet
```

Every pathway ends with a capstone and at least one artifact a reviewer can
inspect.

## 4. Pathway notes

| Area | Design |
|---|---|
| Simulated cloud | [Simulated cloud range](SIMULATED-CLOUD.md) |
| AI governance and security | [AI governance and security pathway](AI-GOVERNANCE-AND-SECURITY-PATHWAY.md) |
| Supply chain | [Supply chain security pathway](SUPPLY-CHAIN-SECURITY-PATHWAY.md) |
| Multi-student scenarios | [Multi-student incident scenarios](MULTI-STUDENT-SCENARIOS.md) |
| Readiness and hiring | [Workforce readiness and job matching](WORKFORCE-READINESS-JOB-MATCHING.md) |
| Transcript | [Digital Cyber Transcript](DIGITAL-CYBER-TRANSCRIPT.md) |
| Risk and support | [CWRS](CYBER-WORKFORCE-RISK-SCORE.md) |
| Competency view | [Competency matrix and lab health](COMPETENCY-MATRIX-AND-LAB-HEALTH.md) |
| Framework | [Cyber Workforce Readiness Framework](CYBER-WORKFORCE-READINESS-FRAMEWORK.md) |

## 5. What to build first

1. **Detection and IR.** Reuse the network tap, logs, and existing forensics
   labs. Add KQL/Sigma and a hunt capstone.
2. **Simulated cloud.** Reuse LocalStack, Keycloak, MinIO, Vault, OpenSearch,
   and the existing container toolchain. Add IAM, storage, secrets, and IR labs.
3. **Identity.** Expand the three existing labs into RBAC/ABAC, PAM, SSO,
   Conditional Access, and access review.
4. **Automation.** Add Python/API/SOAR labs that replace a repeated manual task.
5. **Vulnerability management and GRC.** Add prioritisation and
   control-to-evidence labs.

Cloud and detection are the highest-demand and reuse the most existing work.

## 6. Evidence per gap

| Gap | Minimum evidence |
|---|---|
| Cloud security | IAM policy diff, storage fix, cloud incident timeline |
| Detection engineering | Query, Sigma rule, test result, ATT&CK map |
| Threat hunting | Hypothesis, query, evidence, decision |
| Incident response | Timeline, containment record, executive summary |
| Identity | Role model, consent flow, access review |
| Automation | Working script/playbook, test, README |
| Vulnerability management | Prioritised list with CVSS/EPSS/KEV and impact |
| Architecture | Data-flow diagram, trust boundary, review finding |
| GRC | Control matrix, evidence pack, audit response |
| Communication | Report, brief, and audience adaptation |

## 7. Metrics

- capstone pass rate and artifact quality;
- employer review of a sample portfolio;
- time to first independent solve;
- clean-solve rate and hint pressure;
- role readiness distribution;
- placement or further-study outcomes where consent allows;
- advisory-board review of the pathway every year.

## 8. Guardrails

- Do not add a lab without a competency and evidence mapping.
- Do not claim a skill from a completion alone.
- Do not use real cloud accounts, patient data, malware, or production systems
  in a shared lab.
- Do not let a tool vendor define the learning outcome.
- Do not confuse a certification objective with operational capability.
- Do not publish learner rankings.

## 9. Open questions

- Which cloud profile ships first: AWS-like (LocalStack) or Azure-like
  (Azurite plus a mock ARM adapter)?
- Which SIEM is the reference: Wazuh + OpenSearch or a hosted Sentinel tenant?
- Which roles does the advisory board consider entry-level in this region?
- What evidence will employers actually review in ten minutes?
