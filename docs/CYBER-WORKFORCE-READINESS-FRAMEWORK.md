# Cyber Workforce Readiness Framework

Status: **proposal** (18 November 2026).

This is the umbrella framework for the curriculum changes discussed in
[employer capability gaps](EMPLOYER-CAPABILITY-GAPS.md), the
[simulated cloud range](SIMULATED-CLOUD.md),
[AI governance and security](AI-GOVERNANCE-AND-SECURITY-PATHWAY.md),
[supply chain security](SUPPLY-CHAIN-SECURITY-PATHWAY.md), and
[multi-student scenarios](MULTI-STUDENT-SCENARIOS.md).

## 1. Definition of readiness

A learner is workforce-ready when they can produce **defensible evidence** that
they can perform the work expected of an entry-level practitioner, explain the
limits of that evidence, and communicate the result to a technical and a
non-technical audience.

Readiness is not:

- a completion percentage;
- a certification count;
- a quiz score in isolation;
- attendance in a course;
- a single capstone with no review.

Readiness is a profile of evidence, not one number. A learner may be strong in
detection and weak in GRC; the profile must show that, not hide it.

## 2. Readiness dimensions

| Dimension | Question | Example evidence |
|---|---|---|
| **Technical execution** | Can the learner perform the task safely? | Lab completion, clean solve, configuration diff, test result |
| **Investigation** | Can the learner find and explain what happened? | Timeline, query, detection rule, root-cause note |
| **Cloud and identity** | Can the learner reason about modern infrastructure? | IAM policy, storage fix, OIDC flow, agent permission matrix |
| **Governance and risk** | Can the learner map a control to evidence and decide? | Control matrix, risk register, impact assessment, audit response |
| **Communication and collaboration** | Can the learner explain and coordinate? | Executive summary, incident update, team scenario, debrief |

Cross-cutting themes:

- **AI security and governance** — every role will touch an AI system.
- **Supply chain** — every build and dependency is an attack surface.
- **Automation** — repetitive work should be scripted and reviewed.
- **Safety and ethics** — no real patient data, malware, or cloud cost.

## 3. Proficiency ladder

Use the existing competency language:

| Level | Meaning | Evidence threshold |
|---|---|---|
| **Awareness** | Can explain the concept | Quiz or short written answer |
| **Guided** | Can perform with instructions | Workbook walkthrough completed |
| **Independent** | Can perform without hints | Clean lab solve, no hints |
| **Applied** | Can solve an unfamiliar variant | New scenario, artifact, review |
| **Professional** | Can lead, defend, and improve the work | Capstone, team scenario, external review |

A course should not claim a learner is "professional" because they completed a
single lab. The evidence hierarchy must be explicit.

## 4. Evidence hierarchy

From weakest to strongest:

1. attendance or video view;
2. quiz score;
3. lab completion with hints;
4. clean lab solve;
5. artifact produced in the lab;
6. capstone with a written report;
7. team scenario with a role-specific decision record;
8. external reviewer or employer sign-off.

A readiness claim needs at least one artifact from level 5 or above, and a
capstone or team scenario for the role the learner is targeting.

## 5. Role profiles

| Target role | Core pathways | Required evidence |
|---|---|---|
| SOC Analyst | Network, Linux, Windows, detection, IR | Triage report, detection rule, clean labs |
| Detection Engineer | Detection, network, cloud, automation | Sigma/KQL rule, test results, ATT&CK map |
| Cloud Security Engineer | Simulated cloud, identity, supply chain | IAM policy, storage fix, incident timeline |
| Incident Responder | Forensics, IR, multi-student scenario | Timeline, containment record, executive brief |
| IAM Engineer | Identity, cloud, GRC | Role model, consent flow, access review |
| GRC Analyst | GRC, AI governance, cloud | Control matrix, evidence pack, risk register |
| Security Architect | Architecture, cloud, supply chain | Threat model, architecture review, design fix |
| DevSecOps Engineer | Supply chain, automation, cloud | SBOM, signature verification, pipeline fix |

These are starting points, not job guarantees. The learner's portfolio should
show the evidence, not only the pathway name.

## 6. Curriculum architecture

```text
Foundations
  network, Linux, Windows, web, high-school
      |
Pathways
  detection, IR, identity, cloud, AI governance, supply chain, GRC, architecture
      |
Capstones
  individual technical capstone + written report
      |
Team scenarios
  role-based incident with information asymmetry
      |
Portfolio and external review
  artifacts, timeline, executive brief, employer or faculty review
```

The platform already has tracks, levels, competency contracts, achievements,
Cyber DNA, and portfolio exports. This framework adds the **evidence contract**
and the **team layer**.

## 7. Assessment rules

- Use a rubric with named dimensions and observable criteria.
- Require more than one evidence type for a readiness claim.
- Separate technical accuracy from communication quality.
- Allow resubmission; record the revision, not only the final score.
- Publish the rubric before the task.
- Use cohort-size suppression in analytics.
- Do not make a single automated score a high-stakes decision.
- Record how AI assistance was used and require the learner to verify it.
- Sample and moderate grading across instructors.
- Keep an appeal and correction path.

## 8. Governance

| Group | Responsibility |
|---|---|
| Programme director | Framework, mapping, quality, employer relationships |
| Faculty | Delivery, rubric, moderation, learner support |
| Industry advisory board | Role profiles, scenario review, portfolio calibration |
| Lab maintainers | Lab health, safety, supply chain, reset |
| Privacy and compliance | Consent, retention, data residency, AI review |
| Security team | Platform security, incident response, access review |

Review the framework annually and after a major employer or technology change.
Version the framework so historical transcripts remain reproducible.

## 9. Metrics

Track:

- capstone pass rate and rubric distribution;
- artifact quality by dimension;
- clean-solve rate and hint pressure;
- team-scenario participation and role coverage;
- employer or advisory review of a sample portfolio;
- employment or further-study outcomes where consent allows;
- learner feedback on relevance and workload;
- lab health and abandonment.

Do not rank learners publicly. Report aggregates with confidence and sample
size.

## 10. Implementation roadmap

1. **Publish the framework and role profiles.** This document, the employer gap
   analysis, and the pathway notes.
2. **Map existing labs to the dimensions.** Reuse competency contracts; mark
   gaps.
3. **Build the first two pathways.** Simulated cloud and detection/IR are the
   highest-demand and reuse the most existing tooling.
4. **Add the first team scenario.** Instructor-led, one role set, manual
   scoring.
5. **Add portfolio evidence.** Require an artifact per pathway and a capstone.
6. **Pilot with an employer or advisory board.** Review a sample of portfolios.
7. **Automate only after the rubric is stable.** Do not automate a rubric that
   faculty have not calibrated.

## 11. Anti-patterns

- Claiming readiness from completion alone.
- A single "readiness score" with no evidence.
- Teaching tools without the underlying concept.
- Real cloud accounts, real patient data, or real malware in a shared lab.
- A team scenario with one shared login.
- A capstone that is graded only on the flag.
- AI-generated reports accepted without verification.
- A framework that is never reviewed by employers.

## 12. Acceptance criteria

- Every readiness claim maps to named evidence.
- Every target role has a pathway and a capstone or team scenario.
- The rubric is public and moderated.
- At least one artifact per pathway is stored in the portfolio.
- The framework is versioned and reviewed annually.
- The platform can export the evidence without exposing secrets or PII.
